# from flask import Flask, request, jsonify
# from pymongo import MongoClient
# import bcrypt

# # MongoDB setup
# client = MongoClient('mongodb://localhost:27017/')
# db = client["Smart_Doc"]

# app = Flask(__name__)

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.json.get('username')
#     password = request.json.get('password').encode('utf-8')  # Ensure password is in bytes

#     # Find user in the database
#     user = db.users.find_one({"username": username})

#     if user:
#         # Check if the password matches
#         if bcrypt.checkpw(password, user['password']):
#             return jsonify({"message": "Authentication approved"}), 200
#         else:
#             return jsonify({"error": "Enter valid username and password"}), 401
#     else:
#         return jsonify({"error": "Enter a valid username"}), 404

# if __name__ == '__main__':
#     app.run(debug=True)

# this will be easier to test

from pymongo import MongoClient
import bcrypt
import json
import re

def get_db(client=None):
    if client is None:
        client = MongoClient('mongodb://localhost:27017/')
    return client["Smart_Doc"]

def validate_username(username):
    """ Ensure the username contains only alphanumeric characters. """
    return re.match('^[a-zA-Z0-9]+$', username) is not None

def validate_password(password):
    """ Ensure the password is at least 7 characters long. """
    return len(password) >= 7

def login(username, password, db=None):
    if db is None:
        db = get_db()

    if not validate_username(username):
        return json.dumps({"error": "Username must contain only alphanumeric characters"}), 400
    if not validate_password(password):
        return json.dumps({"error": "Password must be at least 7 characters long"}), 400

    password = password.encode('utf-8') 

    user = db.users.find_one({"username": username})

    if user:
        if bcrypt.checkpw(password, user['password']):
            return json.dumps({"message": "Authentication approved"}), 200
        else:
            return json.dumps({"error": "Enter valid username and password"}), 401
    else:
        return json.dumps({"error": "Enter a valid username"}), 404
    
def create_account(username, password, db=None):
    if db is None:
        db = get_db()

    # Validate username and password
    if not validate_username(username):
        return json.dumps({"error": "Invalid username. Use alphanumeric characters only."}), 400
    if not validate_password(password):
        return json.dumps({"error": "Invalid password. Must be at least 7 characters long."}), 400

    # Check if username already exists
    if db.users.find_one({"username": username}):
        return json.dumps({"error": "Username already taken"}), 409

    # Encrypt the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert new user
    db.users.insert_one({"username": username, "password": hashed_password})

    return json.dumps({"message": "User created successfully"}), 201

# if __name__ == '__main__':
#     username = input("Enter username: ")
#     password = input("Enter password: ")
#     message, status_code = login(username, password)
#     print(f"Status Code: {status_code}, Response: {message}")
