import sys
from pathlib import Path
import fastf1
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import IntegrityError

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import (
    get_session, Circuit, Driver, Team, Race, QualifyingResult, RaceResult, LapTime, PitStop, Weather
)

cache_dir = backend_dir/ 'fastf1_cache'
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))


def convert_timedelta_to_seconds(td):
    if pd.isna(td):
        return None
    try:
        return td.total_seconds()
    except (AttributeError, TypeError):
        return None

def get_or_create_circuit(session_obj, event):
    """Get or create circuit entry"""
    circuit_key = str(event['EventName']).lower().replace(' ', '_').replace("'", "").replace('-', '_')
    
    # Check if circuit exists
    circuit = session_obj.query(Circuit).filter_by(circuit_key=circuit_key).first()
    
    if not circuit:
        circuit = Circuit(
            circuit_key=circuit_key,
            name=str(event['EventName']),
            location=str(event.get('Location', 'Unknown')),
            country=str(event.get('Country', 'Unknown'))
        )
        session_obj.add(circuit)
        session_obj.commit()
        print(f"Created circuit: {circuit.name}")
    
    return circuit

def get_or_create_driver(session_obj, driver_abbr, driver_info=None):
    """Get or create driver entry"""
    if pd.isna(driver_abbr) or not driver_abbr:
        return None
    
    driver_abbr = str(driver_abbr).strip()
    
    # Check if driver exists by code
    driver = session_obj.query(Driver).filter_by(code=driver_abbr).first()
    
    if not driver and driver_info is not None:
        try:
            driver_number = int(driver_info.get('DriverNumber', 0)) if pd.notna(driver_info.get('DriverNumber')) else None
        except (ValueError, TypeError):
            driver_number = None
            
        driver = Driver(
            driver_number=driver_number,
            code=driver_abbr,
            first_name=str(driver_info.get('FirstName', '')),
            last_name=str(driver_info.get('LastName', '')),
            broadcast_name=str(driver_info.get('BroadcastName', driver_abbr)),
            nationality=str(driver_info.get('CountryCode', 'Unknown'))
        )
        session_obj.add(driver)
        session_obj.commit()
        print(f"Created driver: {driver.broadcast_name} ({driver.code})")
    
    return driver


def get_or_create_team(session_obj, team_name):
    """Get or create team entry"""
    if pd.isna(team_name) or not team_name:
        return None
    
    team_name = str(team_name).strip()
    team_key = team_name.lower().replace(' ', '_').replace('-', '_')
    
    # Check if team exists
    team = session_obj.query(Team).filter_by(team_key=team_key).first()
    
    if not team:
        team = Team(
            team_key=team_key,
            name=team_name
        )
        session_obj.add(team)
        session_obj.commit()
        print(f"Created team: {team.name}")
    
    return team



def load_race_weekend(year, race_name, session_obj):
    """Load complete race weekend data"""
    
    print(f"\n{'='*70}")
    print(f"Loading: {year} {race_name}")
    print(f"{'='*70}")
    
    try:
        # Get event info
        schedule = fastf1.get_event_schedule(year)
        event = schedule[schedule['EventName'] == race_name].iloc[0]
        
        # Get or create circuit
        circuit = get_or_create_circuit(session_obj, event)
        
        # Check if race already exists
        existing_race = session_obj.query(Race).filter_by(
            year=year,
            race_name=race_name
        ).first()
        
        if existing_race:
            print(f"Race already exists in database. Skipping.")
            return
        
        # Load qualifying session
        print("Loading qualifying data...")
        quali = fastf1.get_session(year, race_name, 'Q')
        quali.load()
        
        # Load race session
        print("Loading race data...")
        race = fastf1.get_session(year, race_name, 'R')
        race.load()
        
        # Create race entry
        race_entry = Race(
            year=year,
            round_number=int(event['RoundNumber']),
            race_name=race_name,
            circuit_id=circuit.id,
            race_date=event['EventDate'].date() if pd.notna(event['EventDate']) else None
        )
        session_obj.add(race_entry)
        session_obj.commit()
        print(f"Created race entry: {race_name}")
        
        # Load drivers and teams from race results
        print(" Loading drivers and teams...")
        for idx, row in race.results.iterrows():
            driver = get_or_create_driver(session_obj, row['Abbreviation'], row)
            team = get_or_create_team(session_obj, row.get('TeamName'))
        
        # Load qualifying results
        print("Loading qualifying results...")
        load_qualifying_results(session_obj, race_entry, quali)
        
        # Load race results
        print("Loading race results...")
        load_race_results(session_obj, race_entry, race)
        
        # Load lap times (all drivers)
        print("Loading lap times (all drivers)...")
        load_lap_times_sample(session_obj, race_entry, race)
        
        # Load pit stops
        print("Loading pit stops...")
        load_pit_stops(session_obj, race_entry, race)
        
        # Load weather data (sample)
        print("Loading weather data...")
        load_weather_data(session_obj, race_entry, race)
        
        print(f"Successfully loaded {year} {race_name}!")
        
    except Exception as e:
        print(f"Error loading {year} {race_name}: {e}")
        session_obj.rollback()


def load_qualifying_results(session_obj, race_entry, quali_session):
    """Load qualifying results"""
    try:
        for idx, row in quali_session.results.iterrows():
            driver = session_obj.query(Driver).filter_by(code=row['Abbreviation']).first()
            if not driver:
                continue
            
            quali_result = QualifyingResult(
                race_id=race_entry.id,
                driver_id=driver.id,
                position=int(row['Position']) if pd.notna(row['Position']) else None,
                q1_time=convert_timedelta_to_seconds(row.get('Q1')),
                q2_time=convert_timedelta_to_seconds(row.get('Q2')),
                q3_time=convert_timedelta_to_seconds(row.get('Q3'))
            )
            session_obj.add(quali_result)
        
        session_obj.commit()
        print(f"Loaded {len(quali_session.results)} qualifying results")
    except Exception as e:
        print(f"Error loading qualifying: {e}")
        session_obj.rollback()


def load_race_results(session_obj, race_entry, race_session):
    """Load race results"""
    try:
        for idx, row in race_session.results.iterrows():
            driver = session_obj.query(Driver).filter_by(code=row['Abbreviation']).first()
            if not driver:
                continue
            
            team = session_obj.query(Team).filter_by(name=row.get('TeamName')).first()
            
            race_result = RaceResult(
                race_id=race_entry.id,
                driver_id=driver.id,
                team_id=team.id if team else None,
                grid_position=int(row['GridPosition']) if pd.notna(row['GridPosition']) else None,
                final_position=int(row['Position']) if pd.notna(row['Position']) else None,
                points=float(row['Points']) if pd.notna(row['Points']) else 0.0,
                status=str(row.get('Status', 'Unknown'))
            )
            session_obj.add(race_result)
        
        session_obj.commit()
        print(f"Loaded {len(race_session.results)} race results")
    except Exception as e:
        print(f"Error loading race results: {e}")
        session_obj.rollback()


def load_lap_times_sample(session_obj, race_entry, race_session):
    """Load lap times for all drivers"""
    try:
        all_drivers = race_session.results['Abbreviation'].tolist()
        lap_count = 0
        
        for driver_abbr in all_drivers:
            driver = session_obj.query(Driver).filter_by(code=driver_abbr).first()
            if not driver:
                continue
            
            driver_laps = race_session.laps.pick_driver(driver_abbr)
            
            for idx, lap in driver_laps.iterrows():
                lap_time_entry = LapTime(
                    race_id=race_entry.id,
                    driver_id=driver.id,
                    lap_number=int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
                    lap_time=convert_timedelta_to_seconds(lap.get('LapTime')),
                    compound=str(lap.get('Compound')) if pd.notna(lap.get('Compound')) else None,
                    tyre_life=int(lap['TyreLife']) if pd.notna(lap.get('TyreLife')) else None
                )
                session_obj.add(lap_time_entry)
                lap_count += 1
        
        session_obj.commit()
        print(f"Loaded {lap_count} lap times (all drivers)")
    except Exception as e:
        print(f"Error loading lap times: {e}")
        session_obj.rollback()


def load_pit_stops(session_obj, race_entry, race_session):
    """Load pit stop data"""
    try:
        pit_stops = race_session.laps[race_session.laps['PitOutTime'].notna()]
        pit_count = 0
        
        for idx, lap in pit_stops.iterrows():
            driver = session_obj.query(Driver).filter_by(code=lap['Driver']).first()
            if not driver:
                continue
            
            pit_stop = PitStop(
                race_id=race_entry.id,
                driver_id=driver.id,
                lap_number=int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
                compound_after=str(lap.get('Compound')) if pd.notna(lap.get('Compound')) else None
            )
            session_obj.add(pit_stop)
            pit_count += 1
        
        session_obj.commit()
        print(f"Loaded {pit_count} pit stops")
    except Exception as e:
        print(f"Error loading pit stops: {e}")
        session_obj.rollback()


def load_weather_data(session_obj, race_entry, race_session):
    """Load weather data (sample every 10 laps)"""
    try:
        if not hasattr(race_session, 'weather') or race_session.weather is None:
            print("No weather data available")
            return
        
        weather_data = race_session.weather
        weather_count = 0
        
        # Sample every 10th weather entry to avoid too much data
        for idx, row in weather_data.iloc[::10].iterrows():
            weather_entry = Weather(
                race_id=race_entry.id,
                air_temp=float(row['AirTemp']) if pd.notna(row.get('AirTemp')) else None,
                track_temp=float(row['TrackTemp']) if pd.notna(row.get('TrackTemp')) else None,
                humidity=float(row['Humidity']) if pd.notna(row.get('Humidity')) else None,
                pressure=float(row['Pressure']) if pd.notna(row.get('Pressure')) else None,
                rainfall=bool(row.get('Rainfall', False)) if pd.notna(row.get('Rainfall')) else False
            )
            session_obj.add(weather_entry)
            weather_count += 1
        
        session_obj.commit()
        print(f"Loaded {weather_count} weather entries")
    except Exception as e:
        print(f"Error loading weather: {e}")
        session_obj.rollback()



def load_season(year, session_obj):
    """Load all races for a given season"""
    print(f"\n{'#'*70}")
    print(f"# LOADING {year} SEASON")
    print(f"{'#'*70}")
    
    try:
        schedule = fastf1.get_event_schedule(year)
        race_names = schedule['EventName'].tolist()
        
        print(f"\nFound {len(race_names)} races in {year}")
        
        for i, race_name in enumerate(race_names, 1):
            print(f"\n[{i}/{len(race_names)}] Processing: {race_name}")
            try:
                load_race_weekend(year, race_name, session_obj)
            except Exception as e:
                print(f"Failed to load {race_name}: {e}")
                continue
        
        print(f"Completed {year} season!")
        
    except Exception as e:
        print(f"Error loading {year} season: {e}")


def main():
    """Main ETL execution"""
    print("\n" + "="*70)
    print(" F1 HISTORICAL DATA ETL PIPELINE")
    print("="*70)
    print("Loading data from 2015 to 2025")
    print("Note: 2025 data may be incomplete (season in progress)")
    print("\n" + "="*70)
    
    session_obj = get_session()
    
    # Load data year by year
    years = range(2015, 2026)  # 2015 to 2025
    
    for year in years:
        try:
            load_season(year, session_obj)
        except Exception as e:
            print(f"Error loading year {year}: {e}")
            continue
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL DATABASE SUMMARY")
    print("="*70)
    
    from sqlalchemy import text
    from models.database import create_database_engine
    
    engine = create_database_engine()
    with engine.connect() as conn:
        tables = ['circuits', 'drivers', 'teams', 'races', 'qualifying_results', 
                  'race_results', 'lap_times', 'pit_stops', 'weather']
        
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            print(f"  {table:25} {count:>6} rows")
    
    print("ETL Pipeline Complete!")
    print("="*70 + "\n")
    
    session_obj.close()


if __name__ == "__main__":
    main()

    
