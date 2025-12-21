"""
FastF1 Data Exploration Script
Run this to understand available F1 data structure
"""

import fastf1
import pandas as pd
from pathlib import Path
import sys

# Enable cache for faster subsequent loads
cache_dir = Path("../fastf1_cache")
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

print("\n" + "="*70)
print("🏎️  F1 DATA EXPLORATION TOOL")
print("="*70 + "\n")

def explore_race_data(year=2024, race='Monaco'):
    """Explore what data is available for a specific race"""
    
    print(f"\n{'='*70}")
    print(f"📍 Exploring {year} {race} Grand Prix - Race Session")
    print(f"{'='*70}\n")
    
    try:
        # Load race session
        print("⏳ Loading session data... (this may take 1-2 minutes on first run)")
        session = fastf1.get_session(year, race, 'R')
        session.load()
        print("✅ Session loaded successfully!\n")
        
        print("1️⃣  RACE RESULTS (Top 10)")
        print("-" * 70)
        results_cols = ['DriverNumber', 'BroadcastName', 'Position', 'GridPosition', 'Points']
        print(session.results[results_cols].head(10).to_string(index=False))
        
        print("\n\n2️⃣  AVAILABLE DATA COLUMNS")
        print("-" * 70)
        print("Lap data columns:")
        lap_columns = list(session.laps.columns)
        for i in range(0, len(lap_columns), 4):
            print("  ", ", ".join(lap_columns[i:i+4]))
        
        print("\n\n3️⃣  SAMPLE LAP TIMES (Winner's First 10 Laps)")
        print("-" * 70)
        winner_number = session.results.iloc[0]['DriverNumber']
        winner_laps = session.laps.pick_driver(winner_number)
        lap_cols = ['Driver', 'LapNumber', 'LapTime', 'Compound', 'TyreLife']
        print(winner_laps[lap_cols].head(10).to_string(index=False))
        
        print("\n\n4️⃣  WEATHER DATA")
        print("-" * 70)
        if hasattr(session, 'weather') and session.weather is not None and len(session.weather) > 0:
            weather_cols = ['Time', 'AirTemp', 'TrackTemp', 'Humidity', 'Pressure', 'Rainfall']
            available_weather_cols = [col for col in weather_cols if col in session.weather.columns]
            print(session.weather[available_weather_cols].head(10).to_string(index=False))
        else:
            print("  ⚠️  Weather data not available for this session")
        
        print("\n\n5️⃣  PIT STOPS SUMMARY")
        print("-" * 70)
        pit_stops = session.laps[session.laps['PitOutTime'].notna()]
        print(f"  Total pit stops in race: {len(pit_stops)}")
        if len(pit_stops) > 0:
            print("\n  First 10 pit stops:")
            pit_cols = ['Driver', 'LapNumber', 'Compound', 'TyreLife']
            print(pit_stops[pit_cols].head(10).to_string(index=False))
        
        print("\n\n6️⃣  FASTEST LAP")
        print("-" * 70)
        fastest = session.laps.pick_fastest()
        print(f"  Driver: {fastest['Driver']}")
        print(f"  Lap Time: {fastest['LapTime']}")
        print(f"  Lap Number: {fastest['LapNumber']}")
        print(f"  Compound: {fastest['Compound']}")
        
        print("\n\n7️⃣  TIRE STRATEGY SUMMARY")
        print("-" * 70)
        compounds_used = session.laps.groupby('Driver')['Compound'].unique()
        print("  Tire compounds used by each driver:")
        for driver, compounds in compounds_used.head(10).items():
            compounds_str = ", ".join([str(c) for c in compounds if pd.notna(c)])
            print(f"    {driver}: {compounds_str}")
        
        return session
        
    except Exception as e:
        print(f"\n❌ Error loading race data: {e}")
        print("\nPossible reasons:")
        print("  - Network connection issues")
        print("  - Race data not yet available")
        print("  - Invalid race name or year")
        return None


def explore_qualifying_data(year=2024, race='Monaco'):
    """Explore qualifying session data"""
    
    print(f"\n\n{'='*70}")
    print(f"📍 Exploring {year} {race} Qualifying Session")
    print(f"{'='*70}\n")
    
    try:
        print("⏳ Loading qualifying data...")
        quali = fastf1.get_session(year, race, 'Q')
        quali.load()
        print("✅ Qualifying loaded successfully!\n")
        
        print("📊 QUALIFYING RESULTS (Top 10)")
        print("-" * 70)
        quali_cols = ['DriverNumber', 'BroadcastName', 'Q1', 'Q2', 'Q3', 'Position']
        print(quali.results[quali_cols].head(10).to_string(index=False))
        
        return quali
        
    except Exception as e:
        print(f"\n❌ Error loading qualifying data: {e}")
        return None


def list_available_races(year=2024):
    """List all races in a season"""
    
    print(f"\n\n{'='*70}")
    print(f"📅 Available Races in {year} Season")
    print(f"{'='*70}\n")
    
    try:
        schedule = fastf1.get_event_schedule(year)
        schedule_cols = ['RoundNumber', 'EventName', 'EventDate', 'Country', 'Location']
        available_cols = [col for col in schedule_cols if col in schedule.columns]
        print(schedule[available_cols].to_string(index=False))
        
        print(f"\n  Total races in {year}: {len(schedule)}")
        
        return schedule
        
    except Exception as e:
        print(f"\n❌ Error loading schedule: {e}")
        return None


def main():
    """Main exploration function"""
    
    # Explore 2024 Monaco GP
    race_session = explore_race_data(2024, 'Monaco')
    
    if race_session is not None:
        # Explore qualifying
        quali_session = explore_qualifying_data(2024, 'Monaco')
        
        # List all 2024 races
        schedule = list_available_races(2024)
        
        # Summary
        print("\n\n" + "="*70)
        print("✅ EXPLORATION COMPLETE!")
        print("="*70)
        print("\n📋 KEY TAKEAWAYS:")
        print("  ✓ Lap-by-lap timing data available")
        print("  ✓ Tire compound and life tracking")
        print("  ✓ Weather conditions per lap")
        print("  ✓ Qualifying times (Q1, Q2, Q3)")
        print("  ✓ Pit stop information")
        print("  ✓ Grid positions vs final positions")
        print("  ✓ Complete data for 2018-2024 seasons")
        
        print("\n🎯 NEXT STEPS:")
        print("  1. Design database schema for this data")
        print("  2. Build ETL pipeline to load historical races")
        print("  3. Extract features for ML prediction models")
        print("  4. Build prediction API endpoints")
        
        print("\n🏎️  Ready to build the F1 Predictor!\n")
        
    else:
        print("\n⚠️  Exploration incomplete due to errors")
        print("Try running again or check your internet connection\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Exploration interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)