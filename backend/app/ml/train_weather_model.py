import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier


# Training data
data = [
    # temperature, humidity, wind_speed, precipitation, event_type
    [22, 60, 5, 0.0, "Clear/Cloudy"],
    [25, 55, 8, 0.0, "Clear/Cloudy"],
    [28, 50, 10, 0.0, "Clear/Cloudy"],
    [20, 70, 6, 0.0, "Clear/Cloudy"],

    [24, 85, 12, 2.0, "Rain"],
    [22, 90, 15, 5.0, "Rain"],
    [20, 95, 18, 10.0, "Rain"],
    [27, 88, 20, 8.0, "Rain"],

    [26, 80, 25, 15.0, "Thunderstorm"],
    [29, 85, 30, 20.0, "Thunderstorm"],
    [24, 90, 35, 25.0, "Thunderstorm"],

    [38, 30, 10, 0.0, "Heatwave"],
    [40, 25, 12, 0.0, "Heatwave"],
    [42, 20, 15, 0.0, "Heatwave"],

    [10, 90, 5, 0.0, "Fog"],
    [8, 95, 3, 0.0, "Fog"],
    [12, 92, 4, 0.0, "Fog"],

    [18, 75, 45, 0.0, "Strong Winds"],
    [20, 70, 50, 0.0, "Strong Winds"],
    [22, 65, 55, 0.0, "Strong Winds"],
]

columns = [
    "temperature",
    "humidity",
    "wind_speed",
    "precipitation",
    "event_type",
]

df = pd.DataFrame(data, columns=columns)

X = df[
    [
        "temperature",
        "humidity",
        "wind_speed",
        "precipitation",
    ]
]

y = df["event_type"]


# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
)

model.fit(X, y)


# Save model
model_dir = os.path.join(
    os.path.dirname(__file__),
    "models",
)

os.makedirs(model_dir, exist_ok=True)

model_path = os.path.join(
    model_dir,
    "weather_event_model.joblib",
)

joblib.dump(model, model_path)

print("Model trained successfully.")
print(f"Saved to: {model_path}")
print(f"Classes: {list(model.classes_)}")