def test_register_login_and_get_me(client):
    payload = {
        "name": "Auth Test User",
        "email": "auth_test@example.com",
        "password": "pass1234",
    }
    register = client.post("/api/auth/register", json=payload)
    assert register.status_code == 201
    assert register.json()["email"] == payload["email"]

    login = client.post(
        "/api/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == payload["email"]


def test_register_duplicate_email_returns_400(client):
    payload = {
        "name": "Dup User",
        "email": "dup_user@example.com",
        "password": "pass1234",
    }
    first = client.post("/api/auth/register", json=payload)
    second = client.post("/api/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 400
    assert "already" in second.json()["detail"].lower()


def test_login_with_wrong_password_returns_401(client):
    payload = {
        "name": "Wrong Pass User",
        "email": "wrong_pass@example.com",
        "password": "pass1234",
    }
    client.post("/api/auth/register", json=payload)

    login = client.post(
        "/api/auth/login",
        data={"username": payload["email"], "password": "incorrect"},
    )
    assert login.status_code == 401


def test_get_me_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
