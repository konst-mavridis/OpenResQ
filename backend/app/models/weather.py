# app/risk/models/weather.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CurrentWeather(BaseModel):
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    wind_gust: Optional[float] = None
    pressure: int
    condition: str
    condition_code: str
    icon: Optional[str] = None
    visibility: Optional[int] = None
    uv_index: Optional[float] = None
    timestamp: datetime

class MinuteForecast(BaseModel):
    timestamp: datetime
    precipitation_mm: float

class HourlyForecast(BaseModel):
    timestamp: datetime
    temp: float
    feels_like: float
    humidity: int
    wind_speed: float
    precipitation_mm: float
    condition: str

class DailyForecast(BaseModel):
    date: datetime
    temp_min: float
    temp_max: float
    humidity: int
    wind_speed: float
    condition: str
    rain_mm: float
    snow_mm: float

class WeatherAlert(BaseModel):
    title: str
    description: str
    severity: str
    start: datetime
    end: datetime
    source: str

class AirQuality(BaseModel):
    aqi: int
    pm25: float
    pm10: float
    o3: float
    no2: float
    so2: float
    co: float

class WeatherData(BaseModel):
    current: CurrentWeather
    minute_forecast: List[MinuteForecast] = []
    hourly_forecast: List[HourlyForecast] = []
    daily_forecast: List[DailyForecast] = []
    alerts: List[WeatherAlert] = []
    air_quality: Optional[AirQuality] = None
