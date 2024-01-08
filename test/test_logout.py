from login_db.models import Token, TokenStatus
from api.main import app
from fastapi.testclient import TestClient


client = TestClient(app)

class ValidateToken:
    def __init__(self, token: str):
        self.token = token

def create_mock_token(status):
    return Token(token="mock_token",
                 status=status)

def test_logout_valid_token(mocker):
    mock_session = mocker.MagicMock()
    mocker.patch('api.main.Session', autospec=True, return_value=mock_session)

    mock_token = create_mock_token(TokenStatus.ACTIVE)
    mock_session.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_token

    data = {"token": "mock_token"}
    response = client.post("/logout/", json=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully."

def test_logout_invalid_token(mocker):
    mock_session = mocker.MagicMock()
    mocker.patch('api.main.Session', autospec=True, return_value=mock_session)

    mock_token = None
    mock_session.__enter__.return_value.query.return_value.filter.return_value.first.return_value = mock_token

    data = {"token": "mock_token"}
    response = client.post("/logout/", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid token."
