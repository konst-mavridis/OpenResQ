# app/risk/services/weather_service.py
import os
import requests
from datetime import datetime, timedelta
from app.models.weather import (
    WeatherData, CurrentWeather,
    MinuteForecast, HourlyForecast,
    DailyForecast, WeatherAlert, AirQuality
)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = os.getenv("WEATHER_BASE_URL", "https://api.openweathermap.org/data/3.0/onecall")
OWM_KEY = WEATHER_API_KEY

# -----------------------------
# 1) MAIN WEATHER (ONE CALL 3.0)
# -----------------------------
def fetch_weather(lat: float, lng: float) -> WeatherData:
    url = (
        f"{WEATHER_BASE_URL}?lat={lat}&lon={lng}"
        f"&appid={OWM_KEY}&units=metric"
    )

    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    # -----------------------------
    # CURRENT WEATHER
    # -----------------------------
    current = CurrentWeather(
        temp=data["current"]["temp"],
        feels_like=data["current"]["feels_like"],
        humidity=data["current"]["humidity"],
        wind_speed=data["current"]["wind_speed"],
        wind_gust=data["current"].get("wind_gust"),
        pressure=data["current"]["pressure"],
        condition=data["current"]["weather"][0]["main"],
        condition_code=str(data["current"]["weather"][0]["id"]),
        icon=data["current"]["weather"][0]["icon"],
        visibility=data["current"].get("visibility"),
        uv_index=data["current"].get("uvi"),
        timestamp=datetime.fromtimestamp(data["current"]["dt"])
    )

    # -----------------------------
    # MINUTE FORECAST
    # -----------------------------
    minute_forecast = [
        MinuteForecast(
            timestamp=datetime.fromtimestamp(m["dt"]),
            precipitation_mm=m["precipitation"]
        )
        for m in data.get("minutely", [])
    ]

    # -----------------------------
    # HOURLY FORECAST
    # -----------------------------
    hourly_forecast = [
        HourlyForecast(
            timestamp=datetime.fromtimestamp(h["dt"]),
            temp=h["temp"],
            feels_like=h["feels_like"],
            humidity=h["humidity"],
            wind_speed=h["wind_speed"],
            precipitation_mm=h.get("rain", {}).get("1h", 0.0),
            condition=h["weather"][0]["main"]
        )
        for h in data.get("hourly", [])
    ]

    # -----------------------------
    # DAILY FORECAST
    # -----------------------------
    daily_forecast = [
        DailyForecast(
            date=datetime.fromtimestamp(d["dt"]),
            temp_min=d["temp"]["min"],
            temp_max=d["temp"]["max"],
            humidity=d["humidity"],
            wind_speed=d["wind_speed"],
            condition=d["weather"][0]["main"],
            rain_mm=d.get("rain", 0.0),
            snow_mm=d.get("snow", 0.0),
        )
        for d in data.get("daily", [])
    ]

    # -----------------------------
    # WEATHER ALERTS
    # -----------------------------
    alerts = [
        WeatherAlert(
            title=a.get("event", "Alert"),
            description=a.get("description", ""),
            severity=a.get("severity", "unknown"),
            start=datetime.fromtimestamp(a["start"]),
            end=datetime.fromtimestamp(a["end"]),
            source=a.get("sender_name", "unknown")
        )
        for a in data.get("alerts", [])
    ]

    # -----------------------------
    # AIR QUALITY API
    # -----------------------------
    air_quality = fetch_air_quality(lat, lng)

    # -----------------------------
    # HISTORICAL WEATHER (15 YEARS)
    # -----------------------------
    historical = fetch_historical_weather(lat, lng, years=15)

    # -----------------------------
    # CLIMATE NORMALS (MONTHLY)
    # -----------------------------
    climate = fetch_climate_normals(lat, lng)

    # -----------------------------
    # RETURN FULL WEATHER DATA
    # -----------------------------
    return WeatherData(
        current=current,
        minute_forecast=minute_forecast,
        hourly_forecast=hourly_forecast,
        daily_forecast=daily_forecast,
        alerts=alerts,
        air_quality=air_quality,
        historical=historical,
        climate=climate
    )


# -----------------------------
# 2) AIR QUALITY
# -----------------------------
def fetch_air_quality(lat: float, lng: float) -> AirQuality:
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lng}&appid={OWM_KEY}"
    )
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()["list"][0]

    return AirQuality(
        aqi=data["main"]["aqi"],
        pm25=data["components"]["pm2_5"],
        pm10=data["components"]["pm10"],
        o3=data["components"]["o3"],
        no2=data["components"]["no2"],
        so2=data["components"]["so2"],
        co=data["components"]["co"]
    )


# -----------------------------
# 3) HISTORICAL WEATHER (15 YEARS)
# -----------------------------
def fetch_historical_weather(lat: float, lng: float, years: int = 15):
    results = []

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365 * years)

    url = (
        "https://history.openweathermap.org/data/2.5/history/city?"
        f"lat={lat}&lon={lng}&type=hour"
        f"&start={int(start_date.timestamp())}"
        f"&end={int(end_date.timestamp())}"
        f"&appid={OWM_KEY}&units=metric"
    )

    r = requests.get(url)
    if r.status_code != 200:
        return []

    data = r.json()

    for entry in data.get("list", []):
        results.append({
            "date": datetime.fromtimestamp(entry["dt"]),
            "temp": entry["main"]["temp"],
            "humidity": entry["main"]["humidity"],
            "wind_speed": entry["wind"]["speed"],
            "rain_mm": entry.get("rain", {}).get("1h", 0.0),
            "snow_mm": entry.get("snow", {}).get("1h", 0.0),
            "condition": entry["weather"][0]["main"]
        })

    return results


# -----------------------------
# 4) CLIMATE NORMALS (MONTHLY)
# -----------------------------
def fetch_climate_normals(lat: float, lng: float):
    url = (
        f"https://history.openweathermap.org/data/2.5/climate/month?"
        f"lat={lat}&lon={lng}&appid={OWM_KEY}"
    )

    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()

    # Παίρνουμε τον πρώτο μήνα ως reference
    m = data["list"][0]

    return {
        "avg_temp": m["temp"]["average"],
        "avg_humidity": m["humidity"]["average"],
        "avg_wind": m["wind"]["average"],
        "avg_rain_mm": m["precipitation"]["average"]
    }
