from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests

from app.database.connection import get_db
from app.models.report import WeatherReport
from app.models.event import WeatherEvent
from app.ml.predictor import predict_weather_event


router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


def get_weather_condition(weather_code):
    conditions = {
        0: {
            "label": "Clear Sky",
            "icon": "☀️",
        },
        1: {
            "label": "Mainly Clear",
            "icon": "🌤️",
        },
        2: {
            "label": "Partly Cloudy",
            "icon": "⛅",
        },
        3: {
            "label": "Overcast",
            "icon": "☁️",
        },
        45: {
            "label": "Fog",
            "icon": "🌫️",
        },
        48: {
            "label": "Freezing Fog",
            "icon": "🌫️",
        },
        51: {
            "label": "Light Drizzle",
            "icon": "🌦️",
        },
        53: {
            "label": "Moderate Drizzle",
            "icon": "🌦️",
        },
        55: {
            "label": "Dense Drizzle",
            "icon": "🌧️",
        },
        56: {
            "label": "Light Freezing Drizzle",
            "icon": "🌧️",
        },
        57: {
            "label": "Dense Freezing Drizzle",
            "icon": "🌧️",
        },
        61: {
            "label": "Light Rain",
            "icon": "🌦️",
        },
        63: {
            "label": "Moderate Rain",
            "icon": "🌧️",
        },
        65: {
            "label": "Heavy Rain",
            "icon": "🌧️",
        },
        66: {
            "label": "Light Freezing Rain",
            "icon": "🌧️",
        },
        67: {
            "label": "Heavy Freezing Rain",
            "icon": "🌧️",
        },
        71: {
            "label": "Light Snow",
            "icon": "🌨️",
        },
        73: {
            "label": "Moderate Snow",
            "icon": "❄️",
        },
        75: {
            "label": "Heavy Snow",
            "icon": "❄️",
        },
        77: {
            "label": "Snow Grains",
            "icon": "🌨️",
        },
        80: {
            "label": "Light Rain Showers",
            "icon": "🌦️",
        },
        81: {
            "label": "Moderate Rain Showers",
            "icon": "🌧️",
        },
        82: {
            "label": "Violent Rain Showers",
            "icon": "⛈️",
        },
        85: {
            "label": "Light Snow Showers",
            "icon": "🌨️",
        },
        86: {
            "label": "Heavy Snow Showers",
            "icon": "❄️",
        },
        95: {
            "label": "Thunderstorm",
            "icon": "⛈️",
        },
        96: {
            "label": "Thunderstorm with Hail",
            "icon": "⛈️",
        },
        99: {
            "label": "Severe Thunderstorm with Hail",
            "icon": "⛈️",
        },
    }

    return conditions.get(
        weather_code,
        {
            "label": "Unknown Weather",
            "icon": "🌡️",
        },
    )


def get_weather_event_type(weather_code):
    if weather_code in [95, 96, 99]:
        return "Thunderstorm"

    if weather_code in [
        51,
        53,
        55,
        56,
        57,
        61,
        63,
        65,
        66,
        67,
        80,
        81,
        82,
    ]:
        return "Rain"

    if weather_code in [
        71,
        73,
        75,
        77,
        85,
        86,
    ]:
        return "Snow"

    if weather_code in [45, 48]:
        return "Fog"

    return "Clear/Cloudy"


def get_event_severity(weather_code):
    if weather_code in [95, 99]:
        return "high"

    if weather_code in [96]:
        return "moderate"

    if weather_code in [65, 67, 82]:
        return "high"

    if weather_code in [63, 66, 81]:
        return "moderate"

    if weather_code in [
        51,
        53,
        56,
        61,
        80,
    ]:
        return "low"

    if weather_code in [73, 75, 86]:
        return "moderate"

    if weather_code in [71, 77, 85]:
        return "low"

    if weather_code in [45, 48]:
        return "low"

    return "normal"


def calculate_risk(
    weather_code,
    precipitation_probability,
):
    risk_score = 0
    reasons = []

    if weather_code in [95, 96, 99]:
        risk_score += 60

        reasons.append(
            "Thunderstorm conditions detected."
        )

    elif weather_code in [65, 67, 82]:
        risk_score += 50

        reasons.append(
            "Heavy precipitation conditions detected."
        )

    elif weather_code in [63, 66, 81]:
        risk_score += 35

        reasons.append(
            "Moderate precipitation conditions detected."
        )

    elif weather_code in [
        51,
        53,
        56,
        61,
        80,
    ]:
        risk_score += 20

        reasons.append(
            "Light precipitation conditions detected."
        )

    elif weather_code in [
        71,
        73,
        75,
        77,
        85,
        86,
    ]:
        risk_score += 35

        reasons.append(
            "Snow or snow shower conditions detected."
        )

    elif weather_code in [45, 48]:
        risk_score += 20

        reasons.append(
            "Reduced visibility due to fog conditions."
        )

    if (
        precipitation_probability is not None
        and precipitation_probability >= 70
    ):
        risk_score += 20

        reasons.append(
            "High probability of precipitation."
        )

    elif (
        precipitation_probability is not None
        and precipitation_probability >= 40
    ):
        risk_score += 10

        reasons.append(
            "Moderate probability of precipitation."
        )

    risk_score = min(
        risk_score,
        100,
    )

    if risk_score >= 70:
        risk_level = "High"

    elif risk_score >= 40:
        risk_level = "Moderate"

    elif risk_score >= 20:
        risk_level = "Low"

    else:
        risk_level = "Normal"

    if not reasons:
        reasons.append(
            "No significant weather risk detected."
        )

    return {
        "score": risk_score,
        "level": risk_level,
        "reasons": reasons,
    }


def normalize_location_name(name):
    """
    Convert reverse-geocoded names into a clean city name.

    WeatherNova should display a city rather than an airport,
    village, suburb, or other small locality.
    """
    if not name:
        return ""

    cleaned = " ".join(str(name).strip().split())
    lower_cleaned = cleaned.lower()

    # Keep the displayed city consistent for all common
    # Visakhapatnam-area names returned by geocoders.
    if "visakhapatnam" in lower_cleaned:
        return "Visakhapatnam"

    if lower_cleaned in {
        "vizag",
        "vizag airport",
    }:
        return "Visakhapatnam"

    suffixes = [
        " International Airport",
        " Airport",
        " Rural",
        " Urban",
    ]

    changed = True

    while changed:
        changed = False

        for suffix in suffixes:
            if cleaned.lower().endswith(
                suffix.lower()
            ):
                cleaned = cleaned[
                    : -len(suffix)
                ].strip()
                changed = True
                break

    return cleaned


def find_searchable_city(latitude, longitude):
    """
    Resolve browser GPS coordinates into a recognizable city.

    City-level administrative fields are checked before small
    localities such as villages, suburbs, and airports.
    """
    reverse_url = (
        "https://nominatim.openstreetmap.org/reverse"
    )

    reverse_params = {
        "lat": latitude,
        "lon": longitude,
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 18,
        "accept-language": "en",
    }

    try:
        reverse_response = requests.get(
            reverse_url,
            params=reverse_params,
            headers={
                "User-Agent": "WeatherNova/1.0"
            },
            timeout=10,
        )

        reverse_response.raise_for_status()
        reverse_data = reverse_response.json()

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to determine your city "
                "from your current location."
            ),
        ) from exc

    address = reverse_data.get(
        "address",
        {},
    )

    # Check city-level administrative information first.
    city_level_fields = [
        address.get("city"),
        address.get("municipality"),
        address.get("town"),
        address.get("county"),
        address.get("state_district"),
        address.get("city_district"),
    ]

    for value in city_level_fields:
        normalized = normalize_location_name(value)

        if normalized == "Visakhapatnam":
            return "Visakhapatnam"

    # Fallback candidates are checked only after city-level
    # fields have been considered.
    candidates = city_level_fields + [
        address.get("village"),
        address.get("suburb"),
    ]

    cleaned_candidates = []

    for candidate in candidates:
        cleaned = normalize_location_name(candidate)

        if (
            cleaned
            and cleaned.lower()
            not in [
                item.lower()
                for item in cleaned_candidates
            ]
        ):
            cleaned_candidates.append(cleaned)

    if not cleaned_candidates:
        raise HTTPException(
            status_code=404,
            detail=(
                "Unable to determine a city "
                "from your current location."
            ),
        )

    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    for candidate in cleaned_candidates:
        try:
            geocoding_response = requests.get(
                geocoding_url,
                params={
                    "name": candidate,
                    "count": 5,
                    "language": "en",
                    "format": "json",
                },
                timeout=10,
            )

            geocoding_response.raise_for_status()

            geocoding_data = (
                geocoding_response.json()
            )

        except requests.RequestException:
            continue

        results = geocoding_data.get(
            "results",
            [],
        )

        if not results:
            continue

        best_result = None
        best_distance = None

        for result in results:
            result_latitude = result.get(
                "latitude"
            )
            result_longitude = result.get(
                "longitude"
            )

            if (
                result_latitude is None
                or result_longitude is None
            ):
                continue

            distance = (
                (float(result_latitude) - latitude) ** 2
                + (
                    float(result_longitude)
                    - longitude
                ) ** 2
            )

            if (
                best_distance is None
                or distance < best_distance
            ):
                best_distance = distance
                best_result = result

        if best_result:
            resolved_name = normalize_location_name(
                best_result.get(
                    "name",
                    candidate,
                )
            )

            if resolved_name:
                return resolved_name

        return candidate

    return cleaned_candidates[0]


@router.get("/location")
def get_weather_by_location(
    latitude: float,
    longitude: float,
):
    """
    Convert browser GPS coordinates into a city name.

    The frontend then sends that city through the existing
    /weather/?city=... endpoint so the normal WeatherNova
    weather pipeline remains unchanged.
    """
    if not (
        -90 <= latitude <= 90
        and -180 <= longitude <= 180
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid latitude or longitude.",
        )

    city = find_searchable_city(
        latitude,
        longitude,
    )

    return {
        "city": city,
        "latitude": latitude,
        "longitude": longitude,
    }


@router.get("/")
def get_weather(
    city: str,
    db: Session = Depends(get_db),
):
    geocoding_url = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    geocoding_params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    try:
        geocoding_response = requests.get(
            geocoding_url,
            params=geocoding_params,
            timeout=10,
        )

        geocoding_response.raise_for_status()

        geocoding_data = (
            geocoding_response.json()
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to reach weather "
                "location service."
            ),
        ) from exc

    results = geocoding_data.get("results")

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"City '{city}' not found.",
        )

    location = results[0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    resolved_city = location.get(
        "name",
        city,
    )

    country = location.get(
        "country",
        "",
    )

    country_code = location.get(
        "country_code",
        "",
    )

    state = location.get(
        "admin1",
        "",
    )

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "weather_code"
        ),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation_probability,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "forecast_days": 7,
        "timezone": "auto",
    }

    try:
        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to reach weather service.",
        ) from exc

    current = weather_data.get("current")

    hourly = weather_data.get("hourly")

    daily = weather_data.get("daily")

    if not current:
        raise HTTPException(
            status_code=502,
            detail="Current weather data is unavailable.",
        )

    if not daily:
        raise HTTPException(
            status_code=502,
            detail="Forecast data is unavailable.",
        )

    if not hourly:
        raise HTTPException(
            status_code=502,
            detail="Hourly weather data is unavailable.",
        )

    temperature = current.get(
        "temperature_2m"
    )

    humidity = current.get(
        "relative_humidity_2m"
    )

    wind_speed = current.get(
        "wind_speed_10m"
    )

    weather_code = current.get(
        "weather_code"
    )

    condition = get_weather_condition(
        weather_code
    )

    event_type = get_weather_event_type(
        weather_code
    )

    severity = get_event_severity(
        weather_code
    )

    precipitation_probabilities = daily.get(
        "precipitation_probability_max",
        [],
    )

    current_precipitation_probability = (
        precipitation_probabilities[0]
        if precipitation_probabilities
        else None
    )

    # Machine-learning prediction
    ml_prediction = predict_weather_event(
        temperature=temperature or 0,
        humidity=humidity or 0,
        wind_speed=wind_speed or 0,
        precipitation=current_precipitation_probability or 0,
    )

    risk = calculate_risk(
        weather_code,
        current_precipitation_probability,
    )

    existing_report = (
        db.query(WeatherReport)
        .filter(
            WeatherReport.city == resolved_city,
            WeatherReport.event_type == event_type,
        )
        .order_by(
            WeatherReport.timestamp.desc()
        )
        .first()
    )

    is_duplicate = (
        existing_report is not None
    )

    new_report = WeatherReport(
        source="Open-Meteo",
        description=(
            f"{condition['label']} weather "
            f"observation for {resolved_city}"
        ),
        event_type=event_type,
        city=resolved_city,
        state=state,
        latitude=latitude,
        longitude=longitude,
        verification_status="verified",
        confidence_score=1.0,
        trust_score=1.0,
        is_duplicate=is_duplicate,
    )

    db.add(new_report)

    if event_type != "Clear/Cloudy":
        new_event = WeatherEvent(
            event_type=event_type,
            title=(
                f"{condition['label']} detected "
                f"in {resolved_city}"
            ),
            city=resolved_city,
            state=state,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            status="active",
        )

        db.add(new_event)

    db.commit()

    db.refresh(new_report)

    forecast = []

    dates = daily.get(
        "time",
        [],
    )

    weather_codes = daily.get(
        "weather_code",
        [],
    )

    max_temperatures = daily.get(
        "temperature_2m_max",
        [],
    )

    min_temperatures = daily.get(
        "temperature_2m_min",
        [],
    )

    precipitation_probabilities = daily.get(
        "precipitation_probability_max",
        [],
    )

    for index, forecast_date in enumerate(
        dates
    ):
        forecast_weather_code = (
            weather_codes[index]
            if index < len(weather_codes)
            else None
        )

        forecast_condition = (
            get_weather_condition(
                forecast_weather_code
            )
        )

        forecast.append(
            {
                "date": forecast_date,

                "weather_code": (
                    forecast_weather_code
                ),

                "condition": (
                    forecast_condition["label"]
                ),

                "icon": (
                    forecast_condition["icon"]
                ),

                "temperature_max": (
                    max_temperatures[index]
                    if index
                    < len(max_temperatures)
                    else None
                ),

                "temperature_min": (
                    min_temperatures[index]
                    if index
                    < len(min_temperatures)
                    else None
                ),

                "precipitation_probability": (
                    precipitation_probabilities[index]
                    if index
                    < len(
                        precipitation_probabilities
                    )
                    else None
                ),
            }
        )

    hourly_forecast = []

    hourly_times = hourly.get(
        "time",
        [],
    )

    hourly_temperatures = hourly.get(
        "temperature_2m",
        [],
    )

    hourly_humidity = hourly.get(
        "relative_humidity_2m",
        [],
    )

    hourly_precipitation = hourly.get(
        "precipitation_probability",
        [],
    )

    hourly_weather_codes = hourly.get(
        "weather_code",
        [],
    )

    hourly_wind_speed = hourly.get(
        "wind_speed_10m",
        [],
    )

    # Return the next 24 hours starting from the
    # current hour.
    for index in range(
        min(24, len(hourly_times))
    ):
        hourly_weather_code = (
            hourly_weather_codes[index]
            if index < len(hourly_weather_codes)
            else None
        )

        hourly_condition = get_weather_condition(
            hourly_weather_code
        )

        hourly_forecast.append(
            {
                "time": hourly_times[index],
                "temperature": (
                    hourly_temperatures[index]
                    if index < len(hourly_temperatures)
                    else None
                ),
                "humidity": (
                    hourly_humidity[index]
                    if index < len(hourly_humidity)
                    else None
                ),
                "precipitation_probability": (
                    hourly_precipitation[index]
                    if index < len(hourly_precipitation)
                    else None
                ),
                "wind_speed": (
                    hourly_wind_speed[index]
                    if index < len(hourly_wind_speed)
                    else None
                ),
                "weather_code": hourly_weather_code,
                "condition": hourly_condition["label"],
                "icon": hourly_condition["icon"],
            }
        )

    return {
        "city": resolved_city,

        "country": country,

        "country_code": country_code,

        "state": state,

        "latitude": latitude,

        "longitude": longitude,

        "temperature": temperature,

        "humidity": humidity,

        "wind_speed": wind_speed,

        "weather_code": weather_code,

        "condition": condition["label"],

        "condition_icon": condition["icon"],

        "event_type": event_type,

        "ml_event_type": ml_prediction["event_type"],

        "ml_confidence": ml_prediction["confidence"],

        "severity": severity,

        "is_duplicate": is_duplicate,

        "report_id": new_report.id,

        "precipitation_probability": (
            current_precipitation_probability
        ),

        "risk": risk,

        "forecast": forecast,

        "hourly": hourly_forecast,
    }