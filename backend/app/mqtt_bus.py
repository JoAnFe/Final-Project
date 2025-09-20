import ssl, json, time
from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.orm import Session
from .config import settings
from .db import SessionLocal
from .models import Reading, Device
from .rules import evaluate_policies
from .anomaly import anomaly_flag

TOPIC_DATA = f"{settings.TOPIC_BASE}/+/data"       # agri/<device_id>/data
TOPIC_CMD  = f"{settings.TOPIC_BASE}/+/cmd"        # downstream cmd (gw publishes)

def _client():
    c = Client(client_id="gateway")
    c.tls_set(
        ca_certs=settings.MQTT_CA,
        certfile=settings.MQTT_CERT,
        keyfile=settings.MQTT_KEY,
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )
    c.username_pw_set("gateway")  # identity is cert CN; mosquitto can map it
    return c

def on_message(client: Client, userdata, msg: MQTTMessage):
    try:
        topic_parts = msg.topic.split("/")
        device_id = topic_parts[1]
        payload = json.loads(msg.payload.decode())
        with SessionLocal() as db:
            if not db.query(Device).filter_by(device_id=device_id, enabled=True).first():
                return  # unknown/disabled device
            r = Reading(
                device_id=device_id,
                temperature=payload.get("t"),
                humidity=payload.get("h"),
                soil_moisture=payload.get("sm"),
                ph=payload.get("ph"),
                n=payload.get("n"), p=payload.get("p"), k=payload.get("k"),
                voltage=payload.get("v"), current=payload.get("c"),
                extra=payload.get("extra", {})
            )
            db.add(r)
            # update last_seen
            dev = db.query(Device).filter_by(device_id=device_id).first()
            if dev: 
                from datetime import datetime
                dev.last_seen = datetime.utcnow()
            db.commit()
            # Policy checks & anomaly detection
            evaluate_policies(db, r)
            if anomaly_flag(r):
                from .alerts import raise_alert
                raise_alert(db, device_id, "high", "Anomalous sensor pattern", "anomaly")
    except Exception as e:
        print("on_message error:", e)

def run_mqtt_loop():
    c = _client()
    c.on_message = on_message
    c.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
    c.subscribe(TOPIC_DATA, qos=1)
    c.loop_start()