from unittest.mock import patch, MagicMock, mock_open
import pytest
from API.Authorization_Authenication_api import login
import bcrypt
import mongomock
from API.Secure_File_Uploader_api import upload_file_to_db

# Use the patch decorator to mock the get_db function for each test
@patch('API.Authorization_Authenication_api.get_db')
def test_valid_login(mock_get_db):
    """ Test login with valid credentials """
    # Setup a mongomock.MongoClient and replace the db client in the login function
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.db
    mock_get_db.return_value = mock_db

    # Insert a mock user into the mocked 'users' collection
    mock_users = mock_db.users
    mock_users.insert_one({'username': 'celine', 'password': bcrypt.hashpw('testing'.encode('utf-8'), bcrypt.gensalt())})

    # Call the function under test
    username = 'celine'
    password = 'testing'
    message, status_code = login(username, password)

    # Assertions to verify expected outcome
    assert status_code == 200
    assert 'Authentication approved' in message

@patch('API.Authorization_Authenication_api.get_db')
def test_invalid_login(mock_get_db):
    """ Test login with invalid credentials """
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.db
    mock_get_db.return_value = mock_db

    mock_users = mock_db.users
    mock_users.insert_one({'username': 'celine', 'password': bcrypt.hashpw('testing'.encode('utf-8'), bcrypt.gensalt())})

    username = 'celine'
    password = 'hello123'
    message, status_code = login(username, password)

    assert status_code == 401
    assert 'Enter valid username and password' in message


