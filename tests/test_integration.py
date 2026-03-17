from datetime import date, timedelta

from backend.models.notification import Notification


def test_profile_update_and_alerts_flow(client, auth_headers):
    profile_update = client.put(
        "/api/profile/",
        headers=auth_headers,
        json={
            "height_cm": 170,
            "weight_kg": 80,
            "health_goal": "weight_loss",
            "phone": "+911234567890",
        },
    )
    assert profile_update.status_code == 200
    payload = profile_update.json()
    assert payload["user"]["bmi"] is not None
    assert payload["user"]["health_goal"] == "weight_loss"

    expiring_item = {
        "product_name": "Paneer",
        "category": "dairy",
        "expiry_date": (date.today() + timedelta(days=2)).isoformat(),
        "quantity": 1,
        "unit": "pack",
        "source": "manual",
    }
    add = client.post("/api/pantry/add", headers=auth_headers, json=expiring_item)
    assert add.status_code == 201

    expiring = client.get("/api/alerts/expiring", headers=auth_headers, params={"days": 7})
    assert expiring.status_code == 200
    assert any(item["product_name"] == "Paneer" for item in expiring.json())

    stats = client.get("/api/alerts/stats", headers=auth_headers)
    assert stats.status_code == 200
    assert "critical" in stats.json()


def test_notifications_mark_all_read_and_delete_read(client, auth_headers, db_session):
    me = client.get("/api/auth/me", headers=auth_headers).json()
    user_id = me["id"]

    db_session.add_all(
        [
            Notification(user_id=user_id, title="N1", message="m1", type="critical", is_read=False),
            Notification(user_id=user_id, title="N2", message="m2", type="warning", is_read=False),
        ]
    )
    db_session.commit()

    before = client.get("/api/notifications/stats", headers=auth_headers)
    assert before.status_code == 200
    assert before.json()["unread"] >= 2

    mark_all = client.post("/api/notifications/mark-all-read", headers=auth_headers)
    assert mark_all.status_code == 200
    assert mark_all.json()["success"] is True

    after_mark = client.get("/api/notifications/stats", headers=auth_headers)
    assert after_mark.status_code == 200
    assert after_mark.json()["unread"] == 0

    delete_read = client.post("/api/notifications/delete-all-read", headers=auth_headers)
    assert delete_read.status_code == 200
    assert delete_read.json()["success"] is True
