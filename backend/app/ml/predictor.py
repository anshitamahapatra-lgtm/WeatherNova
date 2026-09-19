import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "weather_event_model.joblib",
)

model = joblib.load(MODEL_PATH)


def predict_weather_event(
    temperature: float,
    humidity: float,
    wind_speed: float,
    precipitation: float,
) -> dict:

    features = pd.DataFrame(
        [[
            temperature,
            humidity,
            wind_speed,
            precipitation,
        ]],
        columns=[
            "temperature",
            "humidity",
            "wind_speed",
            "precipitation",
        ],
    )

    prediction = model.predict(features)[0]

    probabilities = model.predict_proba(features)[0]
    confidence = float(max(probabilities))

    return {
        "event_type": prediction,
        "confidence": round(confidence, 2),
    }