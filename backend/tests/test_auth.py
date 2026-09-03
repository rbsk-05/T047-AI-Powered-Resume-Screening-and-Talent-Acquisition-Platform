import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10]}@example.com"


def test_register_recruiter_returns_token_and_profile() -> None:
    email = _unique_email("recruiter")

    response = client.post("/api/v1/auth/register", json={
        "email": email, "password": "supersecret1", "full_name": "Rita Recruiter", "role": "recruiter",
    })

    assert response.status_code == 201
    body = response.json()
    assert body["user"]["role"] == "recruiter"
    assert body["user"]["email"] == email
    assert "access_token" in body and body["access_token"]


def test_register_rejects_duplicate_email() -> None:
    email = _unique_email("dup")
    payload = {"email": email, "password": "supersecret1", "full_name": "Dup User", "role": "candidate"}
    client.post("/api/v1/auth/register", json=payload)

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409


def test_login_with_correct_password_succeeds() -> None:
    email = _unique_email("login")
    client.post("/api/v1/auth/register", json={"email": email, "password": "correct-horse", "full_name": "Login User", "role": "candidate"})

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "correct-horse"})

    assert response.status_code == 200
    assert response.json()["user"]["email"] == email


def test_login_with_wrong_password_is_rejected() -> None:
    email = _unique_email("wrongpw")
    client.post("/api/v1/auth/register", json={"email": email, "password": "correct-horse", "full_name": "Wrong PW", "role": "candidate"})

    response = client.post("/api/v1/auth/login", json={"email": email, "password": "not-the-password"})

    assert response.status_code == 401


def test_me_endpoint_requires_a_token() -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_endpoint_returns_the_authenticated_user() -> None:
    email = _unique_email("me")
    register_response = client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret1", "full_name": "Me User", "role": "recruiter"})
    token = register_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_creating_a_job_requires_a_recruiter_token() -> None:
    payload = {"job_title": "Backend Developer", "job_description": "Develop REST API services using Python and AWS for at least 2 years."}

    response = client.post("/api/v1/jobs", json=payload)

    assert response.status_code == 401


def test_candidate_cannot_create_a_job() -> None:
    email = _unique_email("candidate-jobtry")
    register_response = client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret1", "full_name": "Candidate Try", "role": "candidate"})
    token = register_response.json()["access_token"]
    payload = {"job_title": "Backend Developer", "job_description": "Develop REST API services using Python and AWS for at least 2 years."}

    response = client.post("/api/v1/jobs", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403


def test_recruiter_can_create_a_job() -> None:
    email = _unique_email("recruiter-jobok")
    register_response = client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret1", "full_name": "Recruiter OK", "role": "recruiter"})
    token = register_response.json()["access_token"]
    payload = {"job_title": "Backend Developer", "job_description": "Develop REST API services using Python and AWS for at least 2 years."}

    response = client.post("/api/v1/jobs", json=payload, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201
