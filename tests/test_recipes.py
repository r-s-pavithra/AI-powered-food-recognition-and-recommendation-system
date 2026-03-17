from backend.models.recipe import Recipe
from backend.models.user import User


def test_toggle_favorite_add_and_remove(client, auth_headers, db_session):
    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    user_id = me.json()["id"]

    recipe = Recipe(
        name="Test Recipe",
        description="Simple recipe for tests",
        category="main_course",
        cuisine="indian",
        prep_time=10,
        cook_time=15,
        servings=2,
        difficulty="easy",
        ingredients='["rice", "dal"]',
        instructions='["Boil", "Serve"]',
        calories=250,
        protein=10,
        carbs=35,
        fat=6,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    add_fav = client.post(f"/api/recipes/{recipe.id}/favorite", headers=auth_headers)
    assert add_fav.status_code == 200
    assert add_fav.json()["is_favorite"] is True

    favorites = client.get("/api/recipes/favorites/list", headers=auth_headers)
    assert favorites.status_code == 200
    assert any(r["id"] == recipe.id for r in favorites.json())

    remove_fav = client.post(f"/api/recipes/{recipe.id}/favorite", headers=auth_headers)
    assert remove_fav.status_code == 200
    assert remove_fav.json()["is_favorite"] is False


def test_recipe_favorite_is_user_scoped(client, db_session):
    # user A
    client.post("/api/auth/register", json={"name": "User A", "email": "ra@example.com", "password": "pass1234"})
    la = client.post("/api/auth/login", data={"username": "ra@example.com", "password": "pass1234"})
    ha = {"Authorization": f"Bearer {la.json()['access_token']}"}
    ua = client.get("/api/auth/me", headers=ha).json()

    # user B
    client.post("/api/auth/register", json={"name": "User B", "email": "rb@example.com", "password": "pass1234"})
    lb = client.post("/api/auth/login", data={"username": "rb@example.com", "password": "pass1234"})
    hb = {"Authorization": f"Bearer {lb.json()['access_token']}"}

    recipe = Recipe(
        name="Scoped Favorite Recipe",
        description="Scoped",
        category="main_course",
        cuisine="indian",
        prep_time=5,
        cook_time=10,
        servings=1,
        difficulty="easy",
        ingredients='["tomato"]',
        instructions='["Cook"]',
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)

    # user A favorites it
    add_fav = client.post(f"/api/recipes/{recipe.id}/favorite", headers=ha)
    assert add_fav.status_code == 200

    # user B should not see it in favorites
    b_favs = client.get("/api/recipes/favorites/list", headers=hb)
    assert b_favs.status_code == 200
    assert all(r["id"] != recipe.id for r in b_favs.json())
