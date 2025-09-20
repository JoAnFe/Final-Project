import os

class Settings:
    DB_URL: str = os.getenv("DB_URL", "mysql://smart:smartpass@mysql:3306/smartagri")
    MQTT_HOST: str = os.getenv("MQTT_HOST", "mosquitto")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "8883"))
    MQTT_CA: str = os.getenv("MQTT_CA", "/app/pki/ca/ca.crt")
    MQTT_CERT: str = os.getenv("MQTT_CERT", "/app/pki/gateway/gateway.crt")
    MQTT_KEY: str = os.getenv("MQTT_KEY", "/app/pki/gateway/gateway.key")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_ALGO: str = "HS256"
    TOPIC_BASE: str = "agri"
    ALERT_WEBHOOK: str = os.getenv("ALERT_WEBHOOK", "")
    POLICY_MIN_PH: float = 5.5
    POLICY_MAX_PH: float = 8.0
    DASHBOARD_USER: str = os.getenv("DASHBOARD_USER", "admin")
    DASHBOARD_PASSWORD: str = os.getenv("DASHBOARD_PASSWORD", "changeme")
    ALLOWED_ORIGINS: list[str] = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

settings = Settings()
