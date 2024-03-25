import pymongo
import bcrypt
from getpass import getpass
import os

# Correct import paths for the functions
from API.Authorization_Authenication_api import login as auth_login
from API.Secure_File_Uploader_api import create_folder, upload_file

# MongoDB setup
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]

session = {"user": None}  # Simulates user session

def login():
    username = input("Username: ")
    password = getpass("Password: ")
    
    user = db.users.find_one({"username": username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session["user"] = username
        print("Login successful.")
        
        # Fetch and print folders and files
        print("\nYour folders and files:")
        if 'folders' in user:
            for folder in user['folders']:
                print(f"- Folder: {folder['folder_name']}")
                if 'files' in folder and folder['files']:
                    for file in folder['files']:
                        print(f"  - File: {file['file_name']} ({file['file_path']})")
                else:
                    print("  - No files in this folder")
        else:
            print("You have no folders.")
        
        return True
    else:
        print("Invalid username or password.")
        return False


def make_account():
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if db.users.find_one({"username": username}):
        print("User already exists.")
        return False
    
    db.users.insert_one({"username": username, "password": hashed_password, "folders": []})
    session["user"] = username
    print("Account created successfully.")
    return True

def main():
    while True:
        print("\n1. Login")
        print("2. Make an account")
        if session["user"]:
            print("3. Create a folder")
            print("4. Upload a file")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            login()
        elif choice == '2':
            make_account()
        elif choice == '3' and session["user"]:
            folder_name = input("Folder name: ")
            create_folder(session["user"], folder_name)  # Here, you should ensure the API function does the DB update
        elif choice == '4' and session["user"]:
            folder_name = input("Folder name: ")
            file_path = input("Path to the file: ")
            filename = os.path.basename(file_path)  # Extracts the file name from the full path

            # Now call save_file_to_folder with all required arguments
            status, code = upload_file(session["user"], folder_name, file_path, filename)
            print(status)
        elif choice == '5':
            print("Exiting.")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()
