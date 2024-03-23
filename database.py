from pymongo import MongoClient
import bcrypt

# Connect to MongoDB (Adjust the connection string as necessary)
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"] 

def create_user(username, password):
    users_collection = db.users
    
    # Check if the user already exists
    if users_collection.find_one({"username": username}):
        return "User already exists"
    
    # Hash and salt the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create the user document
    user_document = {
        "username": username,
        "password": hashed_password,
        "folders": []
    }
    
    # Insert the user into the database
    users_collection.insert_one(user_document)
    return "User created successfully"

def add_folder_to_user(username, folder_name):
    users_collection = db.users
    folder = {"folder_name": folder_name, "files": []}
    users_collection.update_one({"username": username}, {"$push": {"folders": folder}})
    return "Folder added successfully"

def add_file_to_folder(username, folder_name, file_name, analysis):
    users_collection = db.users
    file = {"file_name": file_name, "analysis": analysis}
    users_collection.update_one(
        {"username": username, "folders.folder_name": folder_name},
        {"$push": {"folders.$.files": file}}
    )
    return "File added successfully"


if __name__ == "__main__":
    print(create_user("testing", "12345"))
    print(add_folder_to_user("testing", "MyDocuments"))
    print(add_file_to_folder("testing", "MyDocuments", "example.pdf", "PDF analysis"))
