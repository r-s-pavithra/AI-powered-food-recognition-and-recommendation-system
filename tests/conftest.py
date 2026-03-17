from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base, get_db
from backend.models.alert import Alert  # noqa: F401
from backend.models.chat_history import ChatHistory  # noqa: F401
from backend.models.notification import Notification  # noqa: F401
from backend.models.pantry_item import PantryItem  # noqa: F401
from backend.models.professional_tip import ProfessionalTip  # noqa: F401
from backend.models.recipe import Recipe  # noqa: F401
from backend.models.user import User  # noqa: F401
from backend.models.waste_log import ItemSaved, WasteLog  # noqa: F401
from backend.routers import alerts, auth, notifications, pantry, profile, recipes, waste


@pytest.fixture(scope="session")
def engine(tmp_path_factory):
    test_dir = tmp_path_factory.mktemp("db")
    db_path = Path(test_dir) / "test_food_tracker.db"
    test_engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=test_engine)
    yield test_engine
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="session")
def SessionLocal(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session(SessionLocal):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def app(SessionLocal):
    application = FastAPI()
    application.include_router(auth.router)
    application.include_router(pantry.router)
    application.include_router(recipes.router)
    application.include_router(alerts.router)
    application.include_router(notifications.router)
    application.include_router(profile.router)
    application.include_router(waste.router)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture()
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client):
    email = "pytest_user@example.com"
    password = "testpass123"

    register_payload = {
        "name": "Pytest User",
        "email": email,
        "password": password,
    }
    register_resp = client.post("/api/auth/register", json=register_payload)
    assert register_resp.status_code in (201, 400)

    login_resp = client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_item_payload():
    return {
        "product_name": "Milk",
        "category": "dairy",
        "expiry_date": (date.today() + timedelta(days=5)).isoformat(),
        "purchase_date": date.today().isoformat(),
        "quantity": 2,
        "unit": "liters",
        "storage_location": "fridge",
        "source": "manual",
    }
