from login_db.enums import UserStatus
from login_db.models import User
from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def create_mock_user(status):
    return User(username="test_user",
                email="test@test.com",
                password="pw_test",
                status=status)


def test_login_ok(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=True)
    
    mock_user = create_mock_user(UserStatus.ACTIVE)
    mocker.patch('api.main.retrieve_user', return_value=mock_user)
    
    mocker.patch('api.main.create_jwt_token', return_value="mock_token")

    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 200
    assert response.json()["token"] is not None


def test_login_pending_user(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=True)
    
    mock_user = create_mock_user(UserStatus.PENDING)
    mocker.patch('api.main.retrieve_user', return_value=mock_user)
    
    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Pending user."


def test_login_banned_user(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=True)
    
    mock_user = create_mock_user(UserStatus.BANNED)
    mocker.patch('api.main.retrieve_user', return_value=mock_user)

    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Banned user."


def test_login_deleted_user(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=True)
    
    mock_user = create_mock_user(UserStatus.DELETED)
    mocker.patch('api.main.retrieve_user', return_value=mock_user)

    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Deleted user."


def test_login_inactive_user(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=True)
    
    mock_user = create_mock_user(UserStatus.INACTIVE)
    mocker.patch('api.main.retrieve_user', return_value=mock_user)


    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive user."


def test_login_invalid_credentials(mocker):
    mocker.patch("api.main.is_username_password_valid", return_value=False)

    data = {"username": "test", "password": "pw_test"}
    response = client.post("/login/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username and password combination"
