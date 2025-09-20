from fastapi import BackgroundTasks
import httpx
from threading import Thread

from .models import Alert
from .config import settings


def raise_alert(db, device_id: str, severity: str, message: str, rule: str,
                background: BackgroundTasks | None = None):
    """Persist alert and optionally post to webhook in the background."""
    alert = Alert(device_id=device_id, severity=severity,
                  message=message, rule=rule)
    db.add(alert)
    db.commit()
    if not settings.ALERT_WEBHOOK:
        return

    def _send_webhook():
        try:
            httpx.post(
                settings.ALERT_WEBHOOK,
                json={
                    "device_id": device_id,
                    "severity": severity,
                    "message": message,
                    "rule": rule,
                },
                timeout=3,
            )
        except Exception:
            pass

    if background:
        background.add_task(_send_webhook)
    else:
        Thread(target=_send_webhook, daemon=True).start()
