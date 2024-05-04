from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_from_directory
import os
import sys
from pymongo import MongoClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from API.Authorization_Authenication_api import login, create_account
from API.Secure_File_Uploader_api import create_folder, delete_folder, get_file_from_db, upload_file_to_db, allowed_file
from werkzeug.utils import secure_filename
import gridfs
from API.Text_NLP_Analysis_api import summarize_text_with_chatgpt, nlp_analysis
from bson import ObjectId
import pdfplumber
import logging
logging.basicConfig(level=logging.DEBUG)
from API.Feed_Ingester_api import extract_keywords_with_chatgpt, google_search


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to keep sessions

client = MongoClient('mongodb://localhost:27017/')  # Adjust the URI as needed
db = client['Smart_Doc'] 
fs = gridfs.GridFS(db)

# @app.route('/')
# def home():
#     if 'username' in session:
#         return render_template('documents.html', username=session['username'])
#     return render_template('index.html')

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        user = db.users.find_one({"username": username}, {"folders": 1, "_id": 0})
        if user and 'folders' in user:
            folders = user['folders']
        else:
            folders = []
        return render_template('documents.html', username=username, folders=folders)
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def handle_login():
    username = request.json.get('username')
    password = request.json.get('password')
    message, status_code = login(username, password)
    if status_code == 200:
        session['username'] = username  # Set session for logged in user
    return jsonify(message), status_code
    
    

@app.route('/register', methods=['POST'])
def handle_register():
    username = request.json.get('username')
    password = request.json.get('password')
    message, status_code = create_account(username, password)
    return jsonify(message), status_code

@app.route('/create_folder', methods=['POST'])
def handle_create_folder():
    folder_name = request.json.get('folder_name')
    username = session.get('username')
    if not username:
        return jsonify({"error": "User not authenticated"}), 401
    result = create_folder(username, folder_name)
    return jsonify(result)

@app.route('/download/<file_id>')
def download_file(file_id):
    download_path = '/path/to/download'  # Set the local download path
    file_path, message = get_file_from_db(file_id, download_path)
    if file_path:
        return send_from_directory(directory=os.path.dirname(file_path), filename=os.path.basename(file_path), as_attachment=True)
    else:
        return jsonify({"error": message}), 404


@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)  # Clear session
    return redirect(url_for('home'))



# Allowed extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

@app.route('/files/<folder_name>')
def show_files(folder_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    user = db.users.find_one({"username": session['username']}, {"folders": 1})
    folder = next((f for f in user['folders'] if f['folder_name'] == folder_name), None)
    
    if folder:
        files = folder.get('files', [])
        return render_template('folder_files.html', folder_name=folder_name, files=files)
    else:
        return "Folder not found", 404

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if user not logged in

    folder_name = request.form['folder_name']
    file = request.files['file']
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        temp_storage_path = os.path.join(os.path.expanduser('~'), 'temp_storage')
        if not os.path.exists(temp_storage_path):
            os.makedirs(temp_storage_path)

        temp_path = os.path.join(temp_storage_path, filename)
        file.save(temp_path)  # Temporarily save the file

        # Save file to GridFS with explicit PDF content type
        with open(temp_path, 'rb') as f:
            file_id = fs.put(f, filename=filename, content_type='application/pdf')

        # Update user's folder with file reference
        db.users.update_one(
            {"username": session['username'], "folders.folder_name": folder_name},
            {"$push": {"folders.$.files": {"file_name": filename, "file_id": file_id}}}
        )

        # Remove the temporary file after uploading to GridFS
        os.remove(temp_path)
        # logging.debug(f"Uploading file with detected content type: {file.content_type}")
        return redirect(url_for('show_files', folder_name=folder_name))
    else:
        return "File not allowed", 400


@app.route('/check_content_type/<file_id>')
def check_content_type(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        content_type = file.content_type if file.content_type else "None found"
        return f"File Content Type: {content_type}", 200
    except Exception as e:
        return str(e), 500


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


@app.route('/folder/<folder_name>')
def folder(folder_name):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = db.users.find_one({"username": session['username']}, {"folders": 1})
    folder = next((f for f in user['folders'] if f['folder_name'] == folder_name), None)
    
    if folder:
        files = folder.get('files', [])
        return render_template('folder_files.html', folder_name=folder_name, files=files)
    else:
        return "Folder not found", 404


@app.route('/analyze/<file_id>')
def analyze_file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        print("Content Type:", file.content_type)  # Debug statement

        if file.content_type == 'application/pdf':
            with pdfplumber.open(file) as pdf:
                text = ' '.join(page.extract_text() or '' for page in pdf.pages)
            summary = summarize_text_with_chatgpt(text)
            keywords = extract_keywords_with_chatgpt(text)
            keywords_links = {}
            nlp = nlp_analysis(text)
            for keyword in keywords:
                if isinstance(keyword, str):  # Ensure keyword is a string
                    keywords_links[keyword] = google_search(keyword)
                else:
                    print(f"Invalid keyword type: {type(keyword)}")

            return render_template('analyze.html', file_name=file.filename, summary=summary, keywords_links=keywords_links, nlp = nlp)
        return f"Unsupported file type: {file.content_type}", 400
    except gridfs.NoFile:
        return "File not found", 404
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
