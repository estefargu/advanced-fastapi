import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.database.engine import get_db
from main import app

# Base de datos en memoria para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestAuthentication:
    def test_register_success(self):
        response = client.post(
            "/auth/register",
            json={"username": "testuser1", "password": "password123"}
        )
        assert response.status_code == 201
        assert response.json()["username"] == "testuser1"
        assert "id" in response.json()
    
    def test_register_duplicate_user(self):
        client.post(
            "/auth/register",
            json={"username": "duplicate1", "password": "password123"}
        )
        response = client.post(
            "/auth/register",
            json={"username": "duplicate1", "password": "password123"}
        )
        assert response.status_code == 400
    
    def test_register_short_password(self):
        response = client.post(
            "/auth/register",
            json={"username": "shortpass1", "password": "123"}
        )
        assert response.status_code == 422 or response.status_code == 400
    
    def test_login_success(self):
        client.post(
            "/auth/register",
            json={"username": "logintest1", "password": "password123"}
        )
        response = client.post(
            "/auth/login",
            json={"username": "logintest1", "password": "password123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_wrong_password(self):
        client.post(
            "/auth/register",
            json={"username": "wrongpass1", "password": "password123"}
        )
        response = client.post(
            "/auth/login",
            json={"username": "wrongpass1", "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self):
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent999", "password": "password123"}
        )
        assert response.status_code == 401