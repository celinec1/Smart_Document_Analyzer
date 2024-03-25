# from flask import Flask, request, jsonify
# from werkzeug.utils import secure_filename
# from pymongo import MongoClient
# import os
# import bcrypt

# client = MongoClient('mongodb://localhost:27017/')
# db = client["Smart_Doc"]

# # Flask app configuration
# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploads'
# ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpeg'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route('/create_folder', methods=['POST'])
# def create_folder():
#     username = request.form.get('username')
#     folder_name = request.form.get('folder')
#     if not username or not folder_name:
#         return jsonify({"status": "Username and folder name are required"}), 400

#     result = db.users.update_one(
#         {"username": username},
#         {"$addToSet": {"folders": {"folder_name": folder_name, "files": []}}}
#     )
#     if result.modified_count:
#         return jsonify({"status": "Folder created successfully"})
#     else:
#         return jsonify({"status": "Failed to create folder or folder already exists"}), 400

# @app.route('/upload_file', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"status": "No file part"}), 400
#     file = request.files['file']
#     username = request.form.get('username')
#     folder_name = request.form.get('folder')
#     if not file or not allowed_file(file.filename):
#         return jsonify({"status": "Invalid file"}), 400
#     filename = secure_filename(file.filename)
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     file.save(file_path)

#     db.users.update_one(
#         {"username": username, "folders.folder_name": folder_name},
#         {"$push": {"folders.$.files": {"file_name": filename, "file_path": file_path}}}
#     )
#     return jsonify({"status": "File successfully uploaded"})

# @app.route('/delete_file', methods=['POST'])
# def delete_file():
#     username = request.form.get('username')
#     folder_name = request.form.get('folder')
#     file_name = request.form.get('file')
#     result = db.users.update_one(
#         {"username": username, "folders.folder_name": folder_name},
#         {"$pull": {"folders.$.files": {"file_name": file_name}}}
#     )
#     if result.modified_count:
#         return jsonify({"status": "File successfully deleted"})
#     else:
#         return jsonify({"status": "Failed to delete file"}), 400

# if __name__ == '__main__':
#     app.run(debug=True)




from pymongo import MongoClient
import os

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]
UPLOAD_FOLDER = 'uploads'

def create_folder(username, folder_name):
    if not username or not folder_name:
        return {"status": "Username and folder name are required"}, 400

    result = db.users.update_one(
        {"username": username},
        {"$addToSet": {"folders": {"folder_name": folder_name, "files": []}}}
    )
    if result.modified_count:
        return {"status": "Folder created successfully"}, 200
    else:
        return {"status": "Failed to create folder or folder already exists"}, 400

def upload_file(username, folder_name, file_path, filename):
    if not username or not folder_name or not os.path.exists(file_path):
        return {"status": "Invalid request"}, 400

    db.users.update_one(
        {"username": username, "folders.folder_name": folder_name},
        {"$push": {"folders.$.files": {"file_name": filename, "file_path": file_path}}}
    )
    return {"status": "File successfully uploaded"}, 200
