import importlib
from fastapi.testclient import TestClient


def _load_app(monkeypatch, db_url: str):
    """Reload app modules with test configuration and return TestClient + db/models."""
    monkeypatch.setenv("DB_URL", db_url)
    monkeypatch.setenv("DASHBOARD_USER", "tester")
    monkeypatch.setenv("DASHBOARD_PASSWORD", "secret")
    monkeypatch.setenv("JWT_SECRET", "unit-test-secret")
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://localhost")

    from backend.app import config, db, models, alerts, main

    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(models)
    importlib.reload(alerts)
    importlib.reload(main)

    db.Base.metadata.drop_all(bind=db.engine)
    db.Base.metadata.create_all(bind=db.engine)

    main.run_mqtt_loop = lambda: None  # avoid network dial-out during tests

    client = TestClient(main.app)
    return client, db, models


def _get_token(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/token",
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_token_auth_flow(monkeypatch, tmp_path):
    db_path = tmp_path / "test_auth.db"
    client, _, _ = _load_app(monkeypatch, f"sqlite+pysqlite:///{db_path}")

    token = _get_token(client, "tester", "secret")
    assert isinstance(token, str) and token

    bad_resp = client.post(
        "/token",
        data={"username": "tester", "password": "wrong", "grant_type": "password"},
    )
    assert bad_resp.status_code == 401

    unauth = client.get("/devices")
    assert unauth.status_code == 401

    client.close()


def test_protected_endpoints(monkeypatch, tmp_path):
    db_path = tmp_path / "test_data.db"
    client, db, models = _load_app(monkeypatch, f"sqlite+pysqlite:///{db_path}")

    with db.SessionLocal() as session:
        device = models.Device(device_id="dev-1", common_name="Soil Sensor")
        session.add(device)
        session.add(
            models.Reading(
                device_id="dev-1",
                temperature=21.5,
                humidity=48.0,
                soil_moisture=0.31,
                ph=6.9,
            )
        )
        session.add(
            models.Alert(
                device_id="dev-1",
                severity="medium",
                message="pH out of range",
                rule="ph_window",
            )
        )
        session.commit()

    token = _get_token(client, "tester", "secret")
    headers = {"Authorization": f"Bearer {token}"}

    devices = client.get("/devices", headers=headers)
    assert devices.status_code == 200
    payload = devices.json()
    assert payload and payload[0]["device_id"] == "dev-1"

    alerts = client.get("/alerts", headers=headers)
    assert alerts.status_code == 200
    alert_payload = alerts.json()
    assert alert_payload and alert_payload[0]["message"] == "pH out of range"

    readings = client.get("/readings/dev-1", headers=headers)
    assert readings.status_code == 200
    reading_payload = readings.json()
    assert reading_payload and reading_payload[-1]["temperature"] == 21.5

    client.close()
