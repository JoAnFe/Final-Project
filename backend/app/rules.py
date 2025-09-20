from .models import Alert, Reading
from .config import settings
from .alerts import raise_alert

def evaluate_policies(db, r: Reading):
    if r.ph is not None:
        if r.ph < settings.POLICY_MIN_PH or r.ph > settings.POLICY_MAX_PH:
            raise_alert(db, r.device_id, "medium",
                        f"pH {r.ph:.2f} out of bounds [{settings.POLICY_MIN_PH}, {settings.POLICY_MAX_PH}]",
                        "ph_window")
    if r.soil_moisture is not None and r.soil_moisture < 0.15:
        raise_alert(db, r.device_id, "low", "Soil moisture low; consider irrigation", "moisture_low")