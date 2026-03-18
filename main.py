"""
main.py - Weather Forecast ML Ops Pipeline Orchestrator
Coordinates the entire weather forecast data pipeline
"""

from fetch import run_fetch_pipeline
from poem import run_poem_pipeline
from config import DATABASE_NAME, POEM_OUTPUT_FILE
import sys

def main():
    """Main orchestrator for the weather forecast pipeline"""
    print("\n" + "="*60)
    print("🌦️  WEATHER FORECAST ML OPS PIPELINE")
    print("="*60)
    print("\nThis pipeline will:")
    print("  1. Fetch weather data from Open-Meteo API")
    print("  2. Store data in SQLite database")
    print("  3. Generate a bilingual weather poem using Groq AI")
    print("="*60 + "\n")
    
    try:
        # Step 1: Fetch and store weather data
        print("STEP 1: Fetching and storing weather data...")
        weather_df = run_fetch_pipeline()
        
        # Step 2: Generate poem
        print("\nSTEP 2: Generating weather poem...")
        run_poem_pipeline()
        
        # Success summary
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📁 Output files:")
        print(f"   • {DATABASE_NAME} - SQLite database with weather data")
        print(f"   • {POEM_OUTPUT_FILE} - Latest bilingual poem")
        print(f"   • output/poems/poem_YYYY-MM-DD.txt - Dated poem archives")
        print("\n💡 Next steps:")
        print(f"   • View database: sqlite3 {DATABASE_NAME}")
        print(f"   • Read latest poem: cat {POEM_OUTPUT_FILE}")
        print("   • View all poems: ls output/poems/")
        print("   • Re-run: python main.py")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()