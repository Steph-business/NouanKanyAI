from pathlib import Path
from typing import List

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = BASE_DIR / "ml" / "data" / "sensor_data.csv"


def load_demo_machine_state() -> List[dict]:
    if not DATASET_PATH.exists():
        return [
            {"machine_id": "CLIM-001", "nom": "Climatisation centrale", "power_kw": 8.5, "temperature_c": 28.0, "vibration_hz": 6.0, "pressure_bar": 2.2, "status": "actif", "priority": "haute"},
            {"machine_id": "FRIG-002", "nom": "Réfrigération", "power_kw": 3.2, "temperature_c": 24.0, "vibration_hz": 5.0, "pressure_bar": 2.0, "status": "actif", "priority": "moyenne"},
            {"machine_id": "POMP-003", "nom": "Pompe hydraulique", "power_kw": 11.8, "temperature_c": 40.0, "vibration_hz": 18.0, "pressure_bar": 3.4, "status": "eco", "priority": "haute"},
            {"machine_id": "ELEC-004", "nom": "Éclairage bureau", "power_kw": 2.1, "temperature_c": 23.0, "vibration_hz": 4.3, "pressure_bar": 1.2, "status": "actif", "priority": "basse"},
        ]

    try:
        df = pd.read_csv(DATASET_PATH)
        latest = df.sort_values("timestamp").groupby("machine_id", as_index=False).tail(1)
        machine_specs = {
            "CLIM-001": {"nom": "Climatisation centrale", "status": "actif", "priority": "haute"},
            "FRIG-002": {"nom": "Réfrigération", "status": "actif", "priority": "moyenne"},
            "POMP-003": {"nom": "Pompe hydraulique", "status": "eco", "priority": "haute"},
            "ELEC-004": {"nom": "Éclairage bureau", "status": "actif", "priority": "basse"},
        }
        result = []
        for _, row in latest.iterrows():
            spec = machine_specs.get(row["machine_id"], {"nom": row["machine_id"], "status": "actif", "priority": "moyenne"})
            result.append({
                "machine_id": row["machine_id"],
                "nom": spec["nom"],
                "power_kw": round(float(row["power_kw"]), 2),
                "temperature_c": round(float(row["temperature_c"]), 1),
                "vibration_hz": round(float(row["vibration_hz"]), 1),
                "pressure_bar": round(float(row["pressure_bar"]), 2),
                "status": spec["status"],
                "priority": spec["priority"],
            })
        return result
    except Exception:
        return []
