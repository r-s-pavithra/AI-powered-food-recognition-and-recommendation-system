from datetime import date, timedelta


def test_add_list_update_delete_pantry_item(client, auth_headers, sample_item_payload):
    add = client.post("/api/pantry/add", json=sample_item_payload, headers=auth_headers)
    assert add.status_code == 201
    item_id = add.json()["id"]

    list_resp = client.get("/api/pantry/items", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(item["id"] == item_id for item in list_resp.json())

    updated_payload = {
        **sample_item_payload,
        "product_name": "Milk Updated",
        "quantity": 3,
        "expiry_date": (date.today() + timedelta(days=7)).isoformat(),
    }
    update = client.put(
        f"/api/pantry/items/{item_id}",
        json=updated_payload,
        headers=auth_headers,
    )
    assert update.status_code == 200
    assert update.json()["product_name"] == "Milk Updated"
    assert update.json()["quantity"] == 3

    delete = client.delete(f"/api/pantry/items/{item_id}", headers=auth_headers)
    assert delete.status_code == 200
    assert delete.json()["success"] is True

    not_found = client.get(f"/api/pantry/items/{item_id}", headers=auth_headers)
    assert not_found.status_code == 404


def test_pantry_items_are_user_scoped(client, sample_item_payload):
    # user 1
    client.post(
        "/api/auth/register",
        json={"name": "User One", "email": "u1@example.com", "password": "pass1234"},
    )
    login1 = client.post("/api/auth/login", data={"username": "u1@example.com", "password": "pass1234"})
    h1 = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    # user 2
    client.post(
        "/api/auth/register",
        json={"name": "User Two", "email": "u2@example.com", "password": "pass1234"},
    )
    login2 = client.post("/api/auth/login", data={"username": "u2@example.com", "password": "pass1234"})
    h2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    add = client.post("/api/pantry/add", json=sample_item_payload, headers=h1)
    item_id = add.json()["id"]

    list_user_2 = client.get("/api/pantry/items", headers=h2)
    assert list_user_2.status_code == 200
    assert all(item["id"] != item_id for item in list_user_2.json())

    get_user_2 = client.get(f"/api/pantry/items/{item_id}", headers=h2)
    assert get_user_2.status_code == 404
