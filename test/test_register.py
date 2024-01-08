from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from login_db.exceptions import DatabaseInsertionError
from api.main import app

client = TestClient(app)

def create_mock_user_data():
    return {"username": "new_user",
            "email": "newuser@test.com",
            "password": "new_password"}

def test_register_successful(mocker):
    user_data = create_mock_user_data()
    mocker.patch('api.main.insert_user', return_value=None)  # Replace 'your_module' with the actual module where `insert_user` is located
    
    response = client.post("/register/", json=user_data)
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully."

def test_register_existing_username(mocker):
    user_data = create_mock_user_data()
    mocker.patch('api.main.insert_user', side_effect=IntegrityError(None, None, None))  # Replace 'your_module'
    
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_existing_email(mocker):
    user_data = create_mock_user_data()
    user_data["username"] = "another_user"
    mocker.patch('api.main.insert_user', side_effect=IntegrityError(None, None, None))  # Replace 'your_module'
    
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_invalid_data(mocker):
    user_data = create_mock_user_data()
    user_data["email"] = "invalid_email"
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422

def test_register_database_error(mocker):
    user_data = create_mock_user_data()
    mocker.patch('api.main.insert_user', side_effect=DatabaseInsertionError("mock database error"))  # Replace 'your_module'
    
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "mock database error" in response.json()["detail"]

def test_register_unexpected_error(mocker):
    user_data = create_mock_user_data()
    mocker.patch('api.main.insert_user', side_effect=Exception("unexpected error"))  # Replace 'your_module'
    
    response = client.post("/register/", json=user_data)
    assert response.status_code == 500
    assert "Internal Server Error" in response.json()["detail"]
