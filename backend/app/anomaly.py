from sklearn.ensemble import IsolationForest
import numpy as np

# For demo: fixed model on [t, h, sm]
model = IsolationForest(contamination=0.02, random_state=42)
_fitted = False

def _ensure_fit():
    global _fitted
    if _fitted: return
    # bootstrap with benign ranges
    X = np.random.normal([22, 55, 0.35], [2.0, 10, 0.05], size=(500,3))
    model.fit(X)
    _fitted = True

def anomaly_flag(r) -> bool:
    _ensure_fit()
    x = np.array([[
        r.temperature if r.temperature is not None else 22.0,
        r.humidity if r.humidity is not None else 50.0,
        r.soil_moisture if r.soil_moisture is not None else 0.3,
    ]])
    return model.predict(x)[0] == -1
