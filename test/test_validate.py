from login_db.models import Token, TokenType, TokenStatus
from api.main import app
from fastapi.testclient import TestClient
from datetime import datetime, timedelta


client = TestClient(app)

def create_mock_token(status, expiration_time):
    return Token(token="mock_token",
                 status=status,
                 expiration_time=expiration_time,
                 user_id=1,
                 type=TokenType.RESET_PASSWORD)

def test_reset_password_valid_token(mocker):
    mock_session = mocker.MagicMock()
    mocker.patch('api.main.Session', autospec=True, return_value=mock_session)

    mocker.patch("api.main.modify_user_password", return_value=None)

    mock_token = create_mock_token(TokenStatus.ACTIVE, datetime.utcnow() + timedelta(days=1))
    mock_session.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_token

    data = {"token": "mock_token", "password": "new_password"}
    response = client.post("/reset-password/", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset successfully."


def test_reset_password_invalid_token(mocker):
    mock_session = mocker.MagicMock()
    mocker.patch('api.main.Session', autospec=True, return_value=mock_session)

    mock_token = create_mock_token(TokenStatus.EXPIRED, datetime.utcnow() - timedelta(days=1))
    mock_session.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_token

    data = {"token": "mock_token", "password": "new_password"}
    response = client.post("/reset-password/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"

def test_reset_password_used_token(mocker):
    mock_session = mocker.MagicMock()
    mocker.patch('api.main.Session', autospec=True, return_value=mock_session)

    mock_token = create_mock_token(TokenStatus.USED, datetime.utcnow() + timedelta(days=1))
    mock_session.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_token

    data = {"token": "mock_token", "password": "new_password"}
    response = client.post("/reset-password/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"
