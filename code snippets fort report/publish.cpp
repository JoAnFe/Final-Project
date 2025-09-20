StaticJsonDocument<200> doc;
doc["device_id"] = deviceId;
doc["metric"] = "soil_moisture";
doc["value"] = readSensor();
doc["timestamp"] = getTimestamp();
serializeJson(doc, payload);
mqttClient.publish(topic, payload);