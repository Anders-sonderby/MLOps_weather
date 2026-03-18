"""
generate_page.py - GitHub Pages Generator
Reads weather data from database and updates docs/index.html
"""

import sqlite3
import shutil
from datetime import datetime
from config import DATABASE_NAME, WEATHER_CODE_DESCRIPTIONS, POEM_OUTPUT_FILE

def get_weather_description(weather_code):
    """Convert weather code to description"""
    return WEATHER_CODE_DESCRIPTIONS.get(int(weather_code), "unknown weather")

def get_latest_weather_data():
    """Fetch the latest weather forecast from database"""
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
        return None
    
    weather_data = {}
    for row in rows:
        location_key = row[0].lower().replace('å', 'a')  # Normalize for JavaScript IDs
        weather_data[location_key] = {
            'location': row[0],
            'date': row[1],
            'weather_code': row[2],
            'temp_max': row[3],
            'temp_min': row[4],
            'precipitation': row[5],
            'wind_speed': row[6],
            'weather_desc': get_weather_description(row[2])
        }
    
    return weather_data

def generate_weather_cards_html(weather_data):
    """Generate HTML for weather cards with actual data"""
    if not weather_data:
        return '<div class="error">No weather data available</div>'
    
    html = ""
    
    for location_key, data in weather_data.items():
        html += f'''
                    <div class="weather-card">
                        <h3>📍 {data['location']}</h3>
                        <div class="weather-info">
                            <p><strong>Temperature:</strong> <span>{data['temp_min']:.1f}°C - {data['temp_max']:.1f}°C</span></p>
                            <p><strong>Conditions:</strong> <span>{data['weather_desc'].title()}</span></p>
                            <p><strong>Precipitation:</strong> <span>{data['precipitation']:.1f} mm</span></p>
                            <p><strong>Wind:</strong> <span>{data['wind_speed']:.1f} km/h</span></p>
                        </div>
                    </div>'''
    
    return html

def update_index_html():
    """Update docs/index.html with latest weather data"""
    print("\n🌐 Generating GitHub Pages...")
    
    # Get weather data
    weather_data = get_latest_weather_data()
    
    if not weather_data:
        print("⚠️  No weather data found in database")
        return
    
    # Copy poem to docs folder for GitHub Pages access
    try:
        shutil.copy(POEM_OUTPUT_FILE, 'docs/latest_poem.txt')
        print(f"✓ Copied poem to docs/latest_poem.txt")
    except Exception as e:
        print(f"⚠️  Warning: Could not copy poem: {e}")
    
    # Read the template
    with open('docs/index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Generate weather cards HTML
    weather_cards_html = generate_weather_cards_html(weather_data)
    
    # Replace the placeholder weather data section
    # Find the weather-data div and replace its content
    start_marker = '<div id="weather-data" class="weather-cards">'
    end_marker = '</div>\n            </div>\n            \n            <!-- Poem Section -->'
    
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker)
    
    if start_idx != -1 and end_idx != -1:
        # Replace the content between markers
        new_html = (
            html_content[:start_idx + len(start_marker)] + 
            weather_cards_html +
            html_content[end_idx:]
        )
        
        # Write updated HTML
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"✓ Updated docs/index.html with data for {len(weather_data)} locations")
        
        # Get forecast date for display
        first_location = list(weather_data.values())[0]
        print(f"  Forecast date: {first_location['date']}")
        print(f"  Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Error: Could not find weather data section in HTML")

if __name__ == "__main__":
    update_index_html()
    print("\n✅ GitHub Pages generation completed!")