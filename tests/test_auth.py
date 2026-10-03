import io
from PIL import Image
from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app

settings.OPENAI_API_KEY = "test-key-123"
client = TestClient(app)

def create_dummy_jpeg(width=300, height=300, color="red"):
    img = Image.new("RGB", (width, height), color=color)
    out = io.BytesIO()
    img.save(out, format="JPEG")
    return out.getvalue()

import uuid

def test_auth_registration_and_login():
    unique_id = str(uuid.uuid4())[:8]
    email = f"user_{unique_id}@example.com"
    password = "secretpassword123"

    # 1. Register User 1
    reg_response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg_response.status_code == 201
    user_data = reg_response.json()
    assert user_data["email"] == email

    # 2. Duplicate registration fails
    dup_response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert dup_response.status_code == 400

    # 3. Login User 1 -> Token
    login_response = client.post("/api/v1/auth/token", data={"username": email, "password": password})
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Get profile /me
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email

def test_unauthenticated_me():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

def test_ownership_authorization():
    u_a = f"usera_{str(uuid.uuid4())[:8]}@example.com"
    u_b = f"userb_{str(uuid.uuid4())[:8]}@example.com"

    # Register User A and User B
    client.post("/api/v1/auth/register", json={"email": u_a, "password": "pass"})
    token_a = client.post("/api/v1/auth/token", data={"username": u_a, "password": "pass"}).json()["access_token"]
    
    client.post("/api/v1/auth/register", json={"email": u_b, "password": "pass"})
    token_b = client.post("/api/v1/auth/token", data={"username": u_b, "password": "pass"}).json()["access_token"]


    target_bytes = create_dummy_jpeg(300, 300, "pink")
    ref_bytes = create_dummy_jpeg(300, 300, "blue")
    files = {"target_image": ("target.jpg", target_bytes, "image/jpeg"), "reference_image": ("ref.jpg", ref_bytes, "image/jpeg")}
    data = {"category": "Makeup", "consent_version": settings.PHOTO_CONSENT_VERSION}

    # User A creates a generation
    headers_a = {"Authorization": f"Bearer {token_a}"}
    create_res = client.post("/api/v1/generations", files=files, data=data, headers=headers_a)
    assert create_res.status_code == 202
    req_id = create_res.json()["request_id"]

    # User A can fetch history and poll status
    history_res = client.get("/api/v1/generations", headers=headers_a)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 1

    status_a = client.get(f"/api/v1/generations/{req_id}", headers=headers_a)
    assert status_a.status_code == 200

    # User B attempting to access User A's generation -> 403 Forbidden
    headers_b = {"Authorization": f"Bearer {token_b}"}
    status_b = client.get(f"/api/v1/generations/{req_id}", headers=headers_b)
    assert status_b.status_code == 403

    del_b = client.delete(f"/api/v1/generations/{req_id}", headers=headers_b)
    assert del_b.status_code == 403

    # User A deleting User A's generation -> 204 No Content
    del_a = client.delete(f"/api/v1/generations/{req_id}", headers=headers_a)
    assert del_a.status_code == 204
