@app.post("/ingest")
async def ingest(data: Telemetry):
    for rule in rules:
        if evaluate(data, rule):
            trigger_alert(rule, data.device_id)
            if "command" in rule["action"]:
                send_command(data.device_id, rule["action"]["command"])
    db.save(data)