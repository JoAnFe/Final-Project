from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import Device, Reading, Alert
from .auth import encode_jwt, require_user
from .mqtt_bus import run_mqtt_loop
from .config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup() -> None:
    run_mqtt_loop()

@app.post("/token")
def issue_token(form: OAuth2PasswordRequestForm = Depends()):
    if not (
        form.username == settings.DASHBOARD_USER
        and form.password == settings.DASHBOARD_PASSWORD
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return {"access_token": encode_jwt(form.username), "token_type": "bearer"}

def _device_to_dict(device: Device) -> dict:
    return {
        "id": device.id,
        "device_id": device.device_id,
        "common_name": device.common_name,
        "enabled": device.enabled,
        "last_seen": device.last_seen,
    }


def _alert_to_dict(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "device_id": alert.device_id,
        "ts": alert.ts,
        "severity": alert.severity,
        "message": alert.message,
        "rule": alert.rule,
    }


def _reading_to_dict(reading: Reading) -> dict:
    return {
        "id": reading.id,
        "device_id": reading.device_id,
        "ts": reading.ts,
        "temperature": reading.temperature,
        "humidity": reading.humidity,
        "soil_moisture": reading.soil_moisture,
        "ph": reading.ph,
        "n": reading.n,
        "p": reading.p,
        "k": reading.k,
        "voltage": reading.voltage,
        "current": reading.current,
        "extra": reading.extra,
    }


@app.get("/devices")
def list_devices(db: Session = Depends(get_db), _: str = Depends(require_user)):
    devices = db.query(Device).all()
    return [_device_to_dict(d) for d in devices]

@app.get("/alerts")
def list_alerts(db: Session = Depends(get_db), _: str = Depends(require_user)):
    alerts = (db.query(Alert)
                .order_by(Alert.ts.desc())
                .limit(200)
                .all())
    return [_alert_to_dict(a) for a in alerts]

@app.get("/readings/{device_id}")
def get_readings(device_id: str, limit: int = 200,
                 db: Session = Depends(get_db),
                 _: str = Depends(require_user)):
    readings = (db.query(Reading)
                  .filter(Reading.device_id == device_id)
                  .order_by(Reading.ts.desc())
                  .limit(limit)
                  .all())
    return [_reading_to_dict(r) for r in reversed(readings)]
