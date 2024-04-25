from pymongo import MongoClient
import gridfs
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]
fs = gridfs.GridFS(db)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'png', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_db(username, folder_name, file_path, custom_filename=None):
    if not allowed_file(file_path):
        return {"status": "Invalid file", "file_id": None}

    extension = file_path.rsplit('.', 1)[1].lower()
    if extension == 'pdf':
        content_type = 'application/pdf'
    elif extension == 'txt':
        content_type = 'text/plain'
    elif extension in {'png', 'jpeg'}:
        content_type = f'image/{extension}'
    else:
        return {"status": "Unsupported file type", "file_id": None}

    filename = secure_filename(custom_filename or file_path)
    with open(file_path, 'rb') as file_to_upload:
        file_id = fs.put(file_to_upload, filename=filename, content_type=content_type)

        db.users.update_one(
            {"username": username, "folders.folder_name": folder_name},
            {"$push": {"folders.$.files": {"file_name": filename, "file_id": file_id}}}
        )

    return {"status": "File successfully uploaded", "file_id": str(file_id)}


def get_file_from_db(file_id, download_path):
    try:
        file_id = ObjectId(file_id)
        file = fs.get(file_id)
        output_path = os.path.join(download_path, file.filename)
        
        # Ensure directory exists
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        
        # Save the file locally
        with open(output_path, 'wb') as file_to_save:
            file_to_save.write(file.read())
        return output_path, "File retrieved successfully"
    except gridfs.NoFile:
        return None, "File not found"
    except Exception as e:
        return None, f"An error occurred: {str(e)}"

def delete_file_from_db(username, folder_name, file_id):
    try:
        file_id = ObjectId(file_id)
        
        fs.delete(file_id)
        
        db.users.update_one(
            {"username": username, "folders.folder_name": folder_name},
            {"$pull": {"folders.$.files": {"file_id": file_id}}}
        )
        
        return "File successfully deleted"
    except gridfs.NoFile:
        return "File not found or already deleted"
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    # Upload a file
    username = input("Enter your username: ")
    folder_name = input("Enter folder name to upload to: ")
    file_path = input("Enter the full path of the file you want to upload: ")
    custom_filename = input("Enter the name you want to save the file as (or press Enter to keep the original name): ")
    
    upload_result = upload_file_to_db(username, folder_name, file_path, custom_filename)
    print(upload_result)
    
    # Retrieve a file
    # file_id = input("Enter the file_id of the file you want to retrieve: ")
    # download_path = input("Enter the directory where you want to save the downloaded file: ")
    # saved_file_path, message = get_file_from_db(file_id, download_path)
    
    
    # if saved_file_path:
    #     print(f"Retrieved and wrote file to {saved_file_path}")
    # else:
    #     print(message)

    # delete_file = input("Do you want to delete a file? (yes/no): ")
    # if delete_file.lower() == 'yes':
    #     username = input("Username: ")
    #     folder_name = input("Folder name: ")
    #     file_id_to_delete = input("Enter the file_id of the file you want to delete: ")
    #     deletion_result = delete_file_from_db(username, folder_name, file_id_to_delete)
    #     print(deletion_result)

if __name__ == '__main__':
    main()
