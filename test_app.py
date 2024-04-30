import pytest
from API.Authorization_Authenication_api import login 

def test_valid_login():
    """ Test login with valid credentials """
    username = 'celine'
    password = 'testing'
    message, status_code = login(username, password)
    assert status_code == 200
    assert 'Authentication approved' in message

def test_invalid_login():
    """ Test login with invalid password """
    username = 'celine'
    password = 'hello'
    message, status_code = login(username, password)
    assert status_code == 401
    assert 'Enter valid username and password' in message

