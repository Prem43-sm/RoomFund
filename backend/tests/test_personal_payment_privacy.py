"""Regression test for the personal-payment ownership boundary (IDOR protection)."""
import os
import tempfile

db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
db_file.close()
os.environ["DATABASE_URL"] = f"sqlite:///{db_file.name}"

from fastapi.testclient import TestClient  # noqa: E402
from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.audit_log import AuditLog  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402


def token(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_personal_payments_are_never_exposed_cross_user():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    try:
        for name, email in [("Prem", "prem@example.com"), ("Rahul", "rahul@example.com")]:
            response = client.post("/api/auth/register", json={"name": name, "email": email, "password": "safe-password"})
            assert response.status_code == 200
        prem_headers = {"Authorization": f"Bearer {token(client, 'prem@example.com', 'safe-password')}"}
        rahul_headers = {"Authorization": f"Bearer {token(client, 'rahul@example.com', 'safe-password')}"}
        created = client.post("/api/personal-payments", headers=prem_headers, json={"title": "Headphones", "amount_minor": 50000, "currency": "INR", "expense_date": "2026-11-16", "description": "Private"})
        assert created.status_code == 200
        payment_id = created.json()["id"]
        assert client.get("/api/personal-payments", headers=rahul_headers).json() == []
        assert client.delete(f"/api/personal-payments/{payment_id}", headers=rahul_headers).status_code == 404
        assert len(client.get("/api/personal-payments", headers=prem_headers).json()) == 1
        db = SessionLocal()
        try:
            event = db.query(AuditLog).filter(AuditLog.entity_id == payment_id).one()
            assert event.action == "PERSONAL_PAYMENT_CREATED"
            assert event.record_hash and event.previous_hash is None
        finally:
            db.close()
    finally:
        client.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        os.unlink(db_file.name)
