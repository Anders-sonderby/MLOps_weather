"""
fetch.py - Weather Data Collection Module
Fetches weather forecast data from Open-Meteo API and stores it in SQLite database
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import sqlite3
from datetime import datetime
from config import (
    DATABASE_NAME,
    LOCATIONS,
    OPENMETEO_API_URL,
    WEATHER_VARIABLES,
    FORECAST_DAYS,
    CACHE_EXPIRE_AFTER,
    RETRY_ATTEMPTS,
    RETRY_BACKOFF_FACTOR
)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=CACHE_EXPIRE_AFTER)
retry_session = retry(cache_session, retries=RETRY_ATTEMPTS, backoff_factor=RETRY_BACKOFF_FACTOR)
openmeteo = openmeteo_requests.Client(session=retry_session)

def create_database():
    """Create SQLite database and table if it doesn't exist"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_name TEXT NOT NULL,
            forecast_date DATE NOT NULL,
            weather_code INTEGER,
            temperature_max REAL,
            temperature_min REAL,
            precipitation_sum REAL,
            wind_speed_max REAL,
            wind_direction REAL,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(location_name, forecast_date)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def fetch_weather_data():
    """Fetch weather data from Open-Meteo API for all locations"""
    print("\n🌤️  Fetching weather data...")
    
    # Extract coordinates
    latitudes = [loc["lat"] for loc in LOCATIONS]
    longitudes = [loc["lon"] for loc in LOCATIONS]
    
    # API parameters
    url = OPENMETEO_API_URL
    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "daily": WEATHER_VARIABLES,
        "timezone": "auto",
        "forecast_days": FORECAST_DAYS,
    }
    
    responses = openmeteo.weather_api(url, params=params)
    
    all_data = []
    
    # Process each location
    for i, response in enumerate(responses):
        location_name = LOCATIONS[i]["name"]
        
        print(f"\n📍 {location_name}")
        print(f"   Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"   Timezone: {response.Timezone()}")
        
        # Process daily data
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_precipitation_sum = daily.Variables(3).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
        daily_wind_direction_10m_dominant = daily.Variables(5).ValuesAsNumpy()
        
        # Get the full date range
        date_range = pd.date_range(
            start=pd.to_datetime(daily.Time() + response.UtcOffsetSeconds(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd() + response.UtcOffsetSeconds(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
        
        # Extract ONLY tomorrow's data (index 1)
        # Index 0 = today, Index 1 = tomorrow
        tomorrow_index = 1
        
        daily_data = {
            "date": [date_range[tomorrow_index]],
            "location_name": [location_name],
            "weather_code": [daily_weather_code[tomorrow_index]],
            "temperature_2m_max": [daily_temperature_2m_max[tomorrow_index]],
            "temperature_2m_min": [daily_temperature_2m_min[tomorrow_index]],
            "precipitation_sum": [daily_precipitation_sum[tomorrow_index]],
            "wind_speed_10m_max": [daily_wind_speed_10m_max[tomorrow_index]],
            "wind_direction_10m_dominant": [daily_wind_direction_10m_dominant[tomorrow_index]]
        }
        
        daily_dataframe = pd.DataFrame(data=daily_data)
        all_data.append(daily_dataframe)
        
        print(f"   Tomorrow's Temperature: {daily_temperature_2m_min[tomorrow_index]:.1f}°C - {daily_temperature_2m_max[tomorrow_index]:.1f}°C")
        print(f"   Tomorrow's Precipitation: {daily_precipitation_sum[tomorrow_index]:.1f} mm")
        print(f"   Tomorrow's Wind: {daily_wind_speed_10m_max[tomorrow_index]:.1f} km/h")
    
    # Combine all locations
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Fetched data for {len(all_data)} locations")
    return combined_df

def store_in_database(df):
    """Store weather data in SQLite database"""
    print("\n💾 Storing data in database...")
    
    conn = sqlite3.connect(DATABASE_NAME)
    
    rows_inserted = 0
    for _, row in df.iterrows():
        try:
            conn.execute('''
                INSERT OR REPLACE INTO weather_data 
                (location_name, forecast_date, weather_code, temperature_max, 
                 temperature_min, precipitation_sum, wind_speed_max, wind_direction)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['location_name'],
                row['date'].date(),
                int(row['weather_code']),
                float(row['temperature_2m_max']),
                float(row['temperature_2m_min']),
                float(row['precipitation_sum']),
                float(row['wind_speed_10m_max']),
                float(row['wind_direction_10m_dominant'])
            ))
            rows_inserted += 1
        except Exception as e:
            print(f"❌ Error inserting row: {e}")
    
    conn.commit()
    conn.close()
    print(f"✓ Stored {rows_inserted} records in database")

def run_fetch_pipeline():
    """Main function to run the fetch and store pipeline"""
    print("="*60)
    print("📥 WEATHER DATA FETCH & STORE PIPELINE")
    print("="*60)
    
    # Step 1: Create database
    create_database()
    
    # Step 2: Fetch weather data
    weather_df = fetch_weather_data()
    
    # Step 3: Store in database
    store_in_database(weather_df)
    
    print("\n✅ Fetch pipeline completed!")
    print(f"📊 Database: {DATABASE_NAME}\n")
    
    return weather_df

if __name__ == "__main__":
    run_fetch_pipeline()