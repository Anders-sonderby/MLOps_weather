"""
config.py - Configuration Module
Centralized configuration for the weather forecast pipeline
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
# This will be ignored on GitHub Actions (which uses secrets directly)
load_dotenv()

# Database Configuration
DATABASE_NAME = 'data/weather_forecast.db'

# Locations to track
LOCATIONS = [
    {"name": "Aalborg", "lat": 57.048, "lon": 9.9187},
    {"name": "Silkeborg", "lat": 56.1697, "lon": 9.5451},
    {"name": "Nice", "lat": 43.7031, "lon": 7.2661}
]

# Open-Meteo API Configuration
OPENMETEO_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_VARIABLES = [
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
    "wind_direction_10m_dominant"
]
FORECAST_DAYS = 2  # Get today + tomorrow (we'll use tomorrow's forecast)
CACHE_EXPIRE_AFTER = 3600  # seconds
RETRY_ATTEMPTS = 5
RETRY_BACKOFF_FACTOR = 0.2

# Groq API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = "llama-3.3-70b-versatile"  # or "mixtral-8x7b-32768"
GROQ_TEMPERATURE = 0.8
GROQ_MAX_TOKENS = 500

# Output Configuration
POEM_OUTPUT_FILE = 'output/poems/latest.txt'
POEM_ARCHIVE_DIR = 'output/poems/'

# Weather code descriptions (WMO codes)
WEATHER_CODE_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "foggy",
    51: "light drizzle",
    53: "drizzle",
    55: "heavy drizzle",
    61: "light rain",
    63: "rain",
    65: "heavy rain",
    71: "light snow",
    73: "snow",
    75: "heavy snow",
    77: "snow grains",
    80: "rain showers",
    81: "rain showers",
    82: "heavy rain showers",
    85: "snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "thunderstorm with heavy hail"
}