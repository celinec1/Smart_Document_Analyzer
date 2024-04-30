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

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client["Smart_Doc"]

def login(username, password):
    password = password.encode('utf-8')  # Ensure password is in bytes

    # Find user in the database
    user = db.users.find_one({"username": username})

    if user:
        # Check if the password matches
        if bcrypt.checkpw(password, user['password']):
            return json.dumps({"message": "Authentication approved"}), 200
        else:
            return json.dumps({"error": "Enter valid username and password"}), 401
    else:
        return json.dumps({"error": "Enter a valid username"}), 404

# if __name__ == '__main__':
#     username = input("Enter username: ")
#     password = input("Enter password: ")
#     message, status_code = login(username, password)
#     print(f"Status Code: {status_code}, Response: {message}")
