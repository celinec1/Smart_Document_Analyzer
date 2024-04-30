from API import create_app
import pytest


@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'MONGO_URI': 'mongodb://your_test_db_url'})
    with app.test_client() as client:
        yield client

def test_valid_login(client):
    """ Test login with valid credentials """
    response = client.post('/login', json={'username': 'celine', 'password': 'testing'})
    assert response.status_code == 200
    assert response.json['message'] == 'Authentication approved'

def test_invalid_login(client):
    """ Test login with invalid password """
    response = client.post('/login', json={'username': 'celine', 'password': 'hello'})
    assert response.status_code == 401
    assert response.json['error'] == 'Enter valid username and password'

