from unittest.mock import patch, MagicMock
import pytest
from API.Authorization_Authenication_api import login 

@patch('API.Authorization_Authenication_api.db.users.find_one')
def test_valid_login(mock_find_one):
    """ Test login with valid credentials """
    # Setup the mock
    mock_find_one.return_value = {'username': 'celine', 'password': bcrypt.hashpw('testing'.encode('utf-8'), bcrypt.gensalt())}
    username = 'celine'
    password = 'testing'
    message, status_code = login(username, password)
    assert status_code == 200
    assert 'Authentication approved' in message

@patch('API.Authorization_Authenication_api.db.users.find_one')
def test_invalid_login(mock_find_one):
    """ Test login with invalid password """
    # Setup the mock
    mock_find_one.return_value = {'username': 'celine', 'password': bcrypt.hashpw('testing'.encode('utf-8'), bcrypt.gensalt())}
    username = 'celine'
    password = 'hello'
    message, status_code = login(username, password)
    assert status_code == 401
    assert 'Enter valid username and password' in message
