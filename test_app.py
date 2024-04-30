from unittest.mock import patch, MagicMock
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
    password = 'hello'
    message, status_code = login(username, password)

    assert status_code == 401
    assert 'Enter valid username and password' in message

# Mock the gridfs and MongoDB interactions
@patch('API.Secure_File_Uploader_api.gridfs.GridFS')
@patch('API.Secure_File_Uploader_api.MongoClient')
def test_upload_pdf_success(mock_mongo_client, mock_grid_fs):
    # Setting up the mock database
    mock_db = MagicMock()
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo_client.return_value = mock_client
    mock_fs = MagicMock()
    mock_grid_fs.return_value = mock_fs
    mock_fs.put.return_value = 'mock_file_id'

    # Perform the test
    result = upload_file_to_db('celine', 'documents', '/path/to/document.pdf', 'document.pdf')

    # Check that the function returns a success message and file_id
    assert result == {'status': 'File successfully uploaded', 'file_id': 'mock_file_id'}
    mock_fs.put.assert_called_once()

@patch('API.Secure_File_Uploader_api.gridfs.GridFS')
@patch('API.Secure_File_Uploader_api.MongoClient')
def test_upload_mp4_unsupported(mock_mongo_client, mock_grid_fs):
    # Setting up the mock database
    mock_db = MagicMock()
    mock_client = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_mongo_client.return_value = mock_client
    mock_fs = MagicMock()
    mock_grid_fs.return_value = mock_fs

    # Perform the test
    result = upload_file_to_db('celine', 'videos', '/path/to/video.mp4', 'video.mp4')

    # Check that the function returns an error for unsupported file type
    assert result == {'status': 'Unsupported file type', 'file_id': None}
    mock_fs.put.assert_not_called()
