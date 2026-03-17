"""
poem.py - Weather Poem Generation Module
Generates bilingual poems comparing weather conditions using Groq API
"""

import sqlite3
from datetime import datetime
from groq import Groq
from config import (
    DATABASE_NAME,
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_MAX_TOKENS,
    POEM_OUTPUT_FILE,
    WEATHER_CODE_DESCRIPTIONS
)

def get_weather_description(weather_code):
    """Convert weather code to human-readable description"""
    return WEATHER_CODE_DESCRIPTIONS.get(int(weather_code), "unknown weather")

def fetch_latest_weather_from_db():
    """Fetch the latest weather data from the database"""
    print("\n📊 Reading weather data from database...")
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get the latest forecast date
    cursor.execute('''
        SELECT location_name, forecast_date, weather_code, 
               temperature_max, temperature_min, precipitation_sum, 
               wind_speed_max
        FROM weather_data
        WHERE forecast_date = (SELECT MAX(forecast_date) FROM weather_data)
        ORDER BY location_name
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("❌ No weather data found in database. Run fetch.py first!")
        return None
    
    weather_data = []
    for row in rows:
        weather_data.append({
            'location': row[0],
            'date': row[1],
            'weather_code': row[2],
            'temp_max': row[3],
            'temp_min': row[4],
            'precipitation': row[5],
            'wind_speed': row[6]
        })
    
    print(f"✓ Found weather data for {len(weather_data)} locations")
    return weather_data

def generate_poem(weather_data):
    """Generate a bilingual poem comparing weather conditions using Groq API"""
    print("\n✍️  Generating weather poem with Groq...")
    
    # Check for Groq API key
    if not GROQ_API_KEY:
        print("❌ Error: GROQ_API_KEY not found in environment variables")
        print("   Please set it with: export GROQ_API_KEY='your-api-key'")
        print("   Or create a .env file with your API key")
        return None
    
    # Prepare weather summary for the prompt
    weather_summary = []
    for data in weather_data:
        weather_desc = get_weather_description(data['weather_code'])
        summary = (f"{data['location']}: {weather_desc}, "
                  f"{data['temp_min']:.1f}°C to {data['temp_max']:.1f}°C, "
                  f"{data['precipitation']:.1f}mm rain, "
                  f"wind {data['wind_speed']:.1f} km/h")
        weather_summary.append(summary)
    
    weather_text = "\n".join(weather_summary)
    
    # Create Groq client
    client = Groq(api_key=GROQ_API_KEY)
    
    # Create the prompt
    prompt = f"""Based on tomorrow's weather forecast for these three locations:

{weather_text}

Write a short, creative poem (8-12 lines) that:
1. Compares the weather in all three locations
2. Describes the differences poetically
3. Suggests which location would be the nicest to visit tomorrow
4. Write it in TWO languages: English first, then Danish

Make it lyrical and fun!"""
    
    try:
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=GROQ_MODEL,
            temperature=GROQ_TEMPERATURE,
            max_tokens=GROQ_MAX_TOKENS,
        )
        
        poem = chat_completion.choices[0].message.content
        
        print("\n" + "="*60)
        print("🌍 WEATHER POEM OF THE DAY 🌍")
        print("="*60)
        print(poem)
        print("="*60 + "\n")
        
        # Save poem to file
        with open(POEM_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(f"Generated at: {datetime.now()}\n")
            f.write(f"Forecast date: {weather_data[0]['date']}\n\n")
            f.write(poem)
        
        print(f"✓ Poem saved to {POEM_OUTPUT_FILE}")
        return poem
        
    except Exception as e:
        print(f"❌ Error generating poem: {e}")
        return None

def run_poem_pipeline():
    """Main function to run the poem generation pipeline"""
    print("="*60)
    print("✍️  WEATHER POEM GENERATION PIPELINE")
    print("="*60)
    
    # Step 1: Fetch data from database
    weather_data = fetch_latest_weather_from_db()
    
    if weather_data is None:
        return
    
    # Step 2: Generate poem
    poem = generate_poem(weather_data)
    
    if poem:
        print("\n✅ Poem generation completed!")
        print(f"📝 Poem saved to: {POEM_OUTPUT_FILE}\n")

if __name__ == "__main__":
    run_poem_pipeline()