# app/services/prediction.py

from pathlib import Path
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from fastapi import HTTPException

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.h5"
CSV_PATH   = BASE_DIR.parent / "training_data" / "cybersecurity_attacks.csv"

# ─── Lazy-load Keras model with pre-flight checks ───────────────────────────────
_model = None
def _get_model():
    global _model
    if _model is None:
        # 1) does the file exist?
        if not MODEL_PATH.is_file():
            raise RuntimeError(f"Model file not found at {MODEL_PATH!r}. Have you called ann.save(...) in your training script?")
        # 2) is it non-zero bytes?
        if MODEL_PATH.stat().st_size == 0:
            raise RuntimeError(f"Model file at {MODEL_PATH!r} is empty. You need to overwrite it with a real HDF5 via ann.save(...).")
        # 3) try loading, catching the HDF5 signature error
        try:
            _model = load_model(MODEL_PATH)
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {MODEL_PATH!r}: {e}")
    return _model

# ─── Rebuild your LabelEncoders from the original CSV ──────────────────────────
_df               = pd.read_csv(CSV_PATH)
le_protocol       = LabelEncoder().fit(_df["Protocol"])
le_packet_type    = LabelEncoder().fit(_df["Packet Type"])
le_traffic_type   = LabelEncoder().fit(_df["Traffic Type"])
le_attack_type    = LabelEncoder().fit(_df["Attack Type"])

# ─── Feature order & class names ───────────────────────────────────────────────
FEATURES    = [
    "Source Port",
    "Destination Port",
    "Protocol",
    "Packet Length",
    "Packet Type",
    "Traffic Type",
]
CLASS_NAMES = list(le_attack_type.classes_)

# ─── Prediction function ───────────────────────────────────────────────────────
def predict(input_data: dict) -> str:
    """
    input_data must include keys:
      - Source Port (int)
      - Destination Port (int)
      - Protocol (str)
      - Packet Length (int)
      - Packet Type (str)
      - Traffic Type (str)
    Returns the predicted Attack Type string.
    """
    df = pd.DataFrame([input_data])

    # 1) encode categories (reject unseen)
    try:
        df["Protocol"]     = le_protocol.transform(df["Protocol"])
        df["Packet Type"]  = le_packet_type.transform(df["Packet Type"])
        df["Traffic Type"] = le_traffic_type.transform(df["Traffic Type"])
    except ValueError as e:
        # e.g. unseen label 'SYN'
        unseen = str(e).split(":")[-1].strip().strip("[] '\"")
        raise HTTPException(status_code=400, detail=f"Unrecognized category: {unseen}")

    # 2) build feature matrix
    try:
        X = df[FEATURES].values.astype(float)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input data: {e}")

    # 3) inference
    model = _get_model()
    try:
        probs = model.predict(X)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction error: {e}")

    idx = int(np.argmax(probs, axis=1)[0])

    # 4) map back to string
    return CLASS_NAMES[idx]
