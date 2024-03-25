from pymongo import MongoClient
import os
from celery import current_app as celery_app

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]
UPLOAD_FOLDER = 'uploads'

@celery_app.task
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

@celery_app.task
def upload_file(username, folder_name, file_path, filename):
    if not username or not folder_name or not os.path.exists(file_path):
        return {"status": "Invalid request"}, 400

    db.users.update_one(
        {"username": username, "folders.folder_name": folder_name},
        {"$push": {"folders.$.files": {"file_name": filename, "file_path": file_path}}}
    )
    return {"status": "File successfully uploaded"}, 200
