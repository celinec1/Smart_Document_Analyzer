from unittest.mock import patch
import pytest
from API.Authorization_Authenication_api import login, get_db
import bcrypt
import mongomock

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

def test_invalid_login(mock_get_db):
    """ Test login with valid credentials """
    mock_client = mongomock.MongoClient()
    mock_db = mock_client.db
    mock_get_db.return_value = mock_db

    mock_users = mock_db.users
    mock_users.insert_one({'username': 'celine', 'password': bcrypt.hashpw('testing'.encode('utf-8'), bcrypt.gensalt())})

    username = 'celine'
    password = 'hello'
    message, status_code = login(username, password)

    assert status_code == 401
    assert 'Authentication not approved' in message


