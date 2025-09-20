#include <WiFiClientSecure.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#define DEVICE_ID "device-001"

const char* WIFI_SSID = "";     // Provisioned to NVS
const char* WIFI_PASS = "";     // Provisioned to NVS

// TLS broker
const char* MQTT_HOST = "192.168.1.10"; // or broker.local
const int   MQTT_PORT = 8883;

// Embed certs or store in SPIFFS; for demo, minimal strings:
const char* CA_CERT = R"EOF(
-----BEGIN CERTIFICATE-----
... paste ca.crt ...
-----END CERTIFICATE-----
)EOF";

const char* CLIENT_CERT = R"EOF(
-----BEGIN CERTIFICATE-----
... paste device-001.crt ...
-----END CERTIFICATE-----
)EOF";

const char* CLIENT_KEY = R"EOF(
-----BEGIN EC PRIVATE KEY-----
... paste device-001.key ...
-----END EC PRIVATE KEY-----
)EOF";

WiFiClientSecure tlsClient;
PubSubClient mqtt(tlsClient);

unsigned long lastPub = 0;

void onCmd(char* topic, byte* payload, unsigned int len) {
  // handle actuator commands e.g., {"irrigate": true, "seconds": 10}
  DynamicJsonDocument doc(256);
  DeserializationError err = deserializeJson(doc, payload, len);
  if (!err) {
    if (doc["irrigate"] == true) {
      // TODO: drive relay GPIO safely with watchdog + failsafe
      // digitalWrite(RELAY_PIN, HIGH); delay(doc["seconds"].as<int>()*1000); digitalWrite(RELAY_PIN, LOW);
    }
  }
}

void ensureMqtt() {
  if (mqtt.connected()) return;
  while (!mqtt.connected()) {
    if (mqtt.connect(DEVICE_ID)) {
      String cmdTopic = String("agri/") + DEVICE_ID + "/cmd";
      mqtt.subscribe(cmdTopic.c_str(), 1);
    } else {
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  // TODO: BLE provisioning path to write WiFi and broker info to NVS

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }

  tlsClient.setCACert(CA_CERT);
  tlsClient.setCertificate(CLIENT_CERT);
  tlsClient.setPrivateKey(CLIENT_KEY);

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onCmd);
}

void loop() {
  ensureMqtt();
  mqtt.loop();

  unsigned long now = millis();
  if (now - lastPub > 5000) { // every 5s
    lastPub = now;
    // Simulated sensors; replace with real reads
    float t = 22.0 + (rand() % 1000) / 100.0f - 5.0f;
    float h = 50.0 + (rand() % 1000) / 10.0f - 50.0f;
    float sm = 0.30 + (rand() % 100) / 1000.0f; // 0..1
    float ph = 6.8 + (rand() % 40) / 100.0f - 0.2f;

    DynamicJsonDocument doc(256);
    doc["t"] = t; doc["h"] = h; doc["sm"] = sm; doc["ph"] = ph;
    char buf[256]; size_t n = serializeJson(doc, buf);

    String topic = String("agri/") + DEVICE_ID + "/data";
    mqtt.publish(topic.c_str(), buf, n, false);
  }
}