import json, time, ssl
from paho.mqtt.client import Client

BROKER="mosquitto"; PORT=8883; BASE="agri"

def on_connect(c, u, f, rc, props=None):
    c.subscribe(f"{BASE}/+/data", qos=1)

def on_message(c, u, msg):
    try:
        parts = msg.topic.split("/")
        dev = parts[1]
        payload = json.loads(msg.payload.decode("utf-8"))
        if payload.get("sm", 1.0) < 0.12:
            cmd = json.dumps({"irrigate": True, "seconds": 10})
            c.publish(f"{BASE}/{dev}/cmd", cmd, qos=1, retain=False)
    except Exception as e:
        print("edge_agent:", e)

if __name__ == "__main__":
    c = Client("edge-agent")
    c.tls_set(ca_certs="/app/pki/ca/ca.crt",
              certfile="/app/pki/gateway/gateway.crt",
              keyfile="/app/pki/gateway/gateway.key",
              tls_version=ssl.PROTOCOL_TLS_CLIENT)
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(BROKER, PORT, 60)
    c.loop_forever()