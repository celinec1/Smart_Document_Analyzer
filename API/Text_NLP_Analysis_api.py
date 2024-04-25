import os
import requests
from pymongo import MongoClient
import gridfs
from bson import ObjectId
import pdfplumber

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]
fs = gridfs.GridFS(db)
api_key = ''


def get_file_content_from_db(file_id):
    """Retrieve file content from GridFS by file ID, decode based on file type, and return metadata."""
    try:
        file_id = ObjectId(file_id)
        file = fs.get(file_id)
        print(f"Found file with ID {file_id}. Content type: {file.content_type}")  # Diagnostic information
        if file.content_type == 'text/plain':
            content = file.read().decode('utf-8')
            return content, file.filename, file.metadata
        elif file.content_type == 'application/pdf':
            with pdfplumber.open(file) as pdf:
                pages = [page.extract_text() for page in pdf.pages]
                content = ' '.join(filter(None, pages))  # Join non-None content
            return content, file.filename, file.metadata
        else:
            return "Unsupported file type for summarization: {}".format(file.content_type), None, None
    except gridfs.NoFile:
        return "File not found.", None, None
    except UnicodeDecodeError as e:
        return f"Unicode decoding error: {str(e)}", None, None
    except Exception as e:
        return f"Error processing file: {str(e)}", None, None

def summarize_text_with_chatgpt(text, api_key):
    """Uses ChatGPT to generate a summary for the provided text."""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',  # Ensure this model is available and appropriate for your usage
        'messages': [{'role': 'system', 'content': 'Summarize this text:'},
                     {'role': 'user', 'content': text}],
        'max_tokens': 150
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f"Failed to generate summary, status code {response.status_code}, response: {response.text}"


def store_summary_in_db(username, folder_name, original_filename, summary):
    """Store the generated summary in MongoDB within a specific user's folder based on username."""
    client = MongoClient('mongodb://localhost:27017/')
    db = client["Smart_Doc"]
    fs = gridfs.GridFS(db)

    new_filename = f"{os.path.splitext(original_filename)[0]}_analyzed.txt"
    summary_bytes = summary.encode('utf-8')  # Convert summary string to bytes
    file_id = fs.put(summary_bytes, filename=new_filename, content_type='text/plain')

    # Now update the user document with this new file reference
    db.users.update_one(
        {'username': username, 'folders.folder_name': folder_name},
        {'$push': {'folders.$.files': {'file_name': new_filename, 'file_id': file_id}}}
    )
    return file_id


def main():
    username = input("Enter username: ")
    folder_name = input("Enter folder name: ")
    file_id_input = input("Enter the file_id of the text file you want to summarize: ")
    content, original_filename, _ = get_file_content_from_db(file_id_input)
    
    if original_filename is None:
        print("Failed to retrieve the file or unsupported file type.")
        return
    
    if content.startswith("File not found") or content.startswith("Error"):
        print(content)
    else:
        print("Processing summary...")
        summary = summarize_text_with_chatgpt(content, api_key)
        if "Failed to generate summary" in summary:
            print(summary)
        else:
            print("Summary of the document:")
            print(summary)
            summary_file_id = store_summary_in_db(username, folder_name, original_filename, summary)
            print(f"Summary stored in database with file ID: {summary_file_id}")

if __name__ == '__main__':
    main()
