from login_db.models import User
from api.main import app
from fastapi.testclient import TestClient


client = TestClient(app)


def create_mock_user():
    return User(id=1, username="test_user", email="test@test.com", password="pw_test")

def test_forgot_password_success(mocker):
    mocker.patch("api.main.Session", return_value=mocker.MagicMock())
    mocker.patch("api.main.send_reset_email", return_value=None)
    mocker.patch("api.main.insert_token", return_value=None)
    mocker.patch("secrets.token_urlsafe", return_value="mock_token")

    mock_user = create_mock_user()
    mocker.patch('api.main.Session.query().filter().first', return_value=mock_user)

    data = {"email": "test@test.com"}
    response = client.post("/forgotten-password/", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "If your email is registered, you will receive a password reset link."

def test_forgot_password_user_not_found(mocker):
    mocker.patch("api.main.Session", return_value=mocker.MagicMock())
    mocker.patch("api.main.send_reset_email", return_value=None)
    mocker.patch("api.main.insert_token", return_value=None)
    mocker.patch("secrets.token_urlsafe", return_value="mock_token")

    mocker.patch('api.main.Session.query().filter().first', return_value=None)

    data = {"email": "nonexistent@test.com"}
    response = client.post("/forgotten-password/", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "If your email is registered, you will receive a password reset link."

def test_forgot_password_internal_error(mocker):
    mocker.patch("api.main.Session", return_value=mocker.MagicMock())
    mocker.patch("api.main.send_reset_email", side_effect=Exception("Mocked Exception"))
    mocker.patch("secrets.token_urlsafe", return_value="mock_token")

    mock_user = create_mock_user()
    mocker.patch('api.main.Session.query().filter().first', return_value=mock_user)

    data = {"email": "test@test.com"}
    response = client.post("/forgotten-password/", json=data)
    assert response.status_code == 500
    assert response.json()["detail"] == "Internal Server Error"
