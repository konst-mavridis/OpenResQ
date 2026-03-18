# app/risk/services/weather_risk.py
from app.models.weather import WeatherData

def calculate_weather_risk(weather: WeatherData) -> int:
    score = 0

    # Θερμοκρασία (π.χ. υψηλή θερμοκρασία → κίνδυνος φωτιάς)
    temp = weather.current.temp
    if temp >= 38:
        score += 30
    elif temp >= 32:
        score += 20
    elif temp >= 28:
        score += 10

    # Υγρασία (χαμηλή → υψηλός κίνδυνος φωτιάς)
    hum = weather.current.humidity
    if hum <= 15:
        score += 30
    elif hum <= 25:
        score += 20
    elif hum <= 35:
        score += 10

    # Άνεμος
    wind = weather.current.wind_speed
    if wind >= 10:
        score += 25
    elif wind >= 6:
        score += 15
    elif wind >= 3:
        score += 5

    # Alerts
    if weather.alerts:
        score += 15

    # Clamp 0–100
    return max(0, min(100, score))
