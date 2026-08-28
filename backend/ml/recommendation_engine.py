"""
backend/ml/recommendation_engine.py — Moteur de recommandation hybride (IA + Règles métier).

Ce module combine les prédictions du modèle XGBoost et les scores d'anomalie d'Isolation Forest
pour générer des actions correctives concrètes (optimisation de charge, délestage préventif, alertes critiques).
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd

# Tarif moyen d'électricité CIE en Côte d'Ivoire (FCFA / kWh)
TARIF_KWH: float = 65.0


def load_models(
    xgb_path: str = "backend/ml/models/xgboost_model.pkl",
    iso_path: str = "backend/ml/models/isolation_forest.pkl",
) -> Tuple[Any, Any]:
    """
    Charge les modèles legacy depuis le disque pour le moteur de recommandation.

    :param xgb_path: Chemin vers le modèle XGBoost sérialisé.
    :param iso_path: Chemin vers le modèle Isolation Forest sérialisé.
    :return: Tuple contenant (xgb_data, iso_data).
    """
    xgb_data = joblib.load(xgb_path)
    iso_data = joblib.load(iso_path)
    return xgb_data, iso_data


def predict_next_hours(
    xgb_data: Dict[str, Any],
    machine_id: str,
    current_temp: float,
    current_vibration: float,
    current_pressure: float,
    hours_ahead: int = 24,
) -> List[Dict[str, Any]]:
    """
    Prédit la consommation électrique heure par heure sur un horizon temporel donné.

    :param xgb_data: Dictionnaire contenant le modèle, l'encodeur et les noms de variables.
    :param machine_id: Code de l'équipement (ex: 'CLIM-001').
    :param current_temp: Température actuelle (°C).
    :param current_vibration: Vibrations actuelles (Hz).
    :param current_pressure: Pression actuelle (bar).
    :param hours_ahead: Nombre d'heures à projeter dans le futur.
    :return: Liste de prévisions contenant l'heure, la puissance estimée (kW) et le coût en FCFA.
    """
    model = xgb_data["model"]
    le = xgb_data["label_encoder"]
    features = xgb_data["features"]

    # 1. Encodage catégoriel de l'identifiant machine
    try:
        machine_encoded = le.transform([machine_id])[0]
    except (ValueError, KeyError):
        machine_encoded = 0

    predictions = []
    now = datetime.now()

    # 2. Projection itérative pour chaque heure de l'horizon
    for h in range(hours_ahead):
        hour = (now.hour + h) % 24
        day = (now.weekday() + (now.hour + h) // 24) % 7
        month = now.month

        input_data = pd.DataFrame(
            [
                {
                    "temperature_c": current_temp,
                    "vibration_hz": current_vibration,
                    "pressure_bar": current_pressure,
                    "hour_of_day": hour,
                    "day_of_week": day,
                    "month": month,
                    "machine_encoded": machine_encoded,
                }
            ]
        )

        pred_kw = model.predict(input_data)[0]
        predictions.append(
            {
                "hour": hour,
                "predicted_kw": round(float(pred_kw), 2),
                "cost_fcfa": round(float(pred_kw) * TARIF_KWH, 0),
            }
        )

    return predictions


def detect_anomalies(
    iso_data: Dict[str, Any], sensor_readings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Vérifie si les relevés capteurs d'une machine présentent une anomalie selon Isolation Forest.

    :param iso_data: Dictionnaire contenant le modèle Isolation Forest et son encodeur.
    :param sensor_readings: Relevés télémétriques (puissance, température, vibrations, pression).
    :return: Dictionnaire avec `is_anomaly`, `anomaly_score` et niveau de `severity`.
    """
    model = iso_data["model"]
    le = iso_data["label_encoder"]

    try:
        machine_encoded = le.transform([sensor_readings["machine_id"]])[0]
    except (ValueError, KeyError):
        machine_encoded = 0

    input_data = pd.DataFrame(
        [
            {
                "power_kw": sensor_readings["power_kw"],
                "temperature_c": sensor_readings["temperature_c"],
                "vibration_hz": sensor_readings["vibration_hz"],
                "pressure_bar": sensor_readings["pressure_bar"],
                "machine_encoded": machine_encoded,
            }
        ]
    )

    # Inférence : -1 = anomalie, 1 = normal
    prediction = model.predict(input_data)[0]
    score = model.decision_function(input_data)[0]

    # Classification de sévérité basée sur la distance à la frontière de décision
    if score < -0.3:
        severity = "critique"
    elif score < -0.1:
        severity = "modérée"
    else:
        severity = "faible"

    return {
        "is_anomaly": bool(prediction == -1),
        "anomaly_score": round(float(score), 4),
        "severity": severity,
    }


def generate_recommendations(
    xgb_data: Dict[str, Any],
    iso_data: Dict[str, Any],
    machines_state: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Génère des recommandations actionnables en croisant les détections d'anomalies,
    les prévisions de consommation et des règles métier d'optimisation énergétique.

    :param xgb_data: Modèle XGBoost chargé.
    :param iso_data: Modèle Isolation Forest chargé.
    :param machines_state: Liste des états capteurs actuels de toutes les machines.
    :return: Liste de recommandations triées par ordre de sévérité décroissante.
    """
    recommendations = []

    for machine in machines_state:
        mid = machine["machine_id"]

        # Étape 1 : Diagnostic d'anomalies de comportement
        anomaly = detect_anomalies(iso_data, machine)
        if anomaly["is_anomaly"]:
            recommendations.append(
                {
                    "machine_id": mid,
                    "type": "alerte",
                    "severity": anomaly["severity"],
                    "title": f"Anomalie détectée sur {mid}",
                    "description": (
                        f"Les capteurs de {mid} montrent un comportement anormal "
                        f"(score: {anomaly['anomaly_score']}). "
                        f"Température: {machine['temperature_c']}°C, "
                        f"Vibration: {machine['vibration_hz']}Hz."
                    ),
                    "action": "Lancer un diagnostic d'urgence",
                    "gain_fcfa": 0,
                }
            )

        # Étape 2 : Prévision de la consommation future à court terme (6h)
        preds = predict_next_hours(
            xgb_data,
            mid,
            machine["temperature_c"],
            machine["vibration_hz"],
            machine["pressure_bar"],
            hours_ahead=6,
        )

        avg_predicted_kw = float(np.mean([p["predicted_kw"] for p in preds]))

        # Étape 3 : Application des règles expertes d'efficacité énergétique

        # Règle 1 : Détection de surconsommation (> 120% de la moyenne attendue)
        if machine["power_kw"] > avg_predicted_kw * 1.2:
            excess_kw = machine["power_kw"] - avg_predicted_kw
            gain = round(excess_kw * 6 * TARIF_KWH)  # Économie potentielle sur 6 heures
            recommendations.append(
                {
                    "machine_id": mid,
                    "type": "optimisation",
                    "severity": "modérée",
                    "title": f"Surconsommation sur {mid}",
                    "description": (
                        f"{mid} consomme {machine['power_kw']}kW alors que la prédiction "
                        f"normale est de {avg_predicted_kw:.1f}kW. "
                        f"Réduire la charge permettrait d'économiser."
                    ),
                    "action": f"Réduire la puissance de {excess_kw:.1f}kW",
                    "gain_fcfa": gain,
                }
            )

        # Règle 2 : Délestage préventif pendant les heures de pointe (10h-16h) pour machines non critiques
        current_hour = datetime.now().hour
        if 10 <= current_hour <= 16 and machine.get("priority") == "basse":
            gain = round(machine["power_kw"] * 2 * TARIF_KWH)  # Économie pour 2h de délestage
            recommendations.append(
                {
                    "machine_id": mid,
                    "type": "délestage",
                    "severity": "faible",
                    "title": f"Délestage préventif possible sur {mid}",
                    "description": (
                        f"Nous sommes en heure de pointe (10h-16h). {mid} est de priorité "
                        f"basse et peut être mise en veille pendant 2h sans impact."
                    ),
                    "action": f"Programmer un délestage de 2h sur {mid}",
                    "gain_fcfa": gain,
                }
            )

        # Règle 3 : Seuil critique de surchauffe thermique (> 60°C)
        if machine["temperature_c"] > 60:
            recommendations.append(
                {
                    "machine_id": mid,
                    "type": "alerte",
                    "severity": "critique",
                    "title": f"Surchauffe détectée sur {mid}",
                    "description": (
                        f"La température de {mid} est de {machine['temperature_c']}°C "
                        f"(seuil critique: 60°C). Risque de dommage matériel."
                    ),
                    "action": "Inspection immédiate requise",
                    "gain_fcfa": 0,
                }
            )

    # Tri des recommandations par ordre de criticité
    severity_order = {"critique": 0, "modérée": 1, "faible": 2}
    recommendations.sort(key=lambda x: severity_order.get(x["severity"], 3))

    return recommendations


if __name__ == "__main__":
    print("[TEST] Exécution du test autonome du moteur de recommandation...\n")
    try:
        xgb_mod, iso_mod = load_models()
        test_machines = [
            {"machine_id": "CLIM-001", "power_kw": 14.0, "temperature_c": 45.0, "vibration_hz": 8.0, "pressure_bar": 3.2, "priority": "haute"},
            {"machine_id": "POMP-003", "power_kw": 25.0, "temperature_c": 72.0, "vibration_hz": 55.0, "pressure_bar": 6.5, "priority": "haute"},
            {"machine_id": "ELEC-004", "power_kw": 3.5, "temperature_c": 30.0, "vibration_hz": 5.0, "pressure_bar": 2.1, "priority": "basse"},
        ]
        test_recs = generate_recommendations(xgb_mod, iso_mod, test_machines)
        print(f"[TEST] {len(test_recs)} recommandation(s) produite(s) avec succès.")
    except Exception as e:
        print(f"[TEST] Modèles legacy non présents : {e}")
