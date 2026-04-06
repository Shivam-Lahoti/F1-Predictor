import sys
from pathlib import Path
import fastf1
import pandas as pd
from datetime import date
from sqlalchemy import func

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import (
    get_session, Circuit, Driver, Team, Race,
    QualifyingResult, RaceResult, LapTime, PitStop, Weather
)

cache_dir = backend_dir / 'fastf1_cache'
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
    circuit_key = (
        str(event['EventName'])
        .lower()
        .replace(' ', '_')
        .replace("'", '')
        .replace('-', '_')
    )
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
        print(f"  Created circuit: {circuit.name}")
    return circuit


def get_or_create_driver(session_obj, driver_abbr, driver_info=None):
    """Get or create driver. Always looks up by code — never by driver number,
    as numbers are reused across seasons (e.g. Vettel and Button both used #22)."""
    if pd.isna(driver_abbr) or not driver_abbr:
        return None

    driver_abbr = str(driver_abbr).strip()
    driver = session_obj.query(Driver).filter_by(code=driver_abbr).first()
    if driver:
        return driver

    if driver_info is None:
        print(f"  WARNING - driver {driver_abbr} not in DB and no info provided, skipping")
        return None

    first  = str(driver_info.get('FirstName', '')).strip()
    last   = str(driver_info.get('LastName', '')).strip()
    bcast  = str(driver_info.get('BroadcastName', '')).strip()
    nation = str(driver_info.get('CountryCode', '')).strip()

    driver = Driver(
        driver_number=None,
        code=driver_abbr,
        first_name=first,
        last_name=last,
        broadcast_name=bcast if bcast else driver_abbr,
        nationality=nation if nation else 'Unknown'
    )
    session_obj.add(driver)
    session_obj.commit()
    print(f"  Created driver: {driver.first_name} {driver.last_name} ({driver_abbr})")
    return driver


def get_or_create_team(session_obj, team_name):
    if pd.isna(team_name) or not team_name:
        return None
    team_name = str(team_name).strip()
    key = team_name.lower().replace(' ', '_').replace('-', '_')
    team = session_obj.query(Team).filter_by(team_key=key).first()
    if not team:
        team = Team(team_key=key, name=team_name)
        session_obj.add(team)
        session_obj.commit()
        print(f"  Created team: {team_name}")
    return team


def load_qualifying_results(session_obj, race_entry, quali_session):
    try:
        count = 0
        for _, row in quali_session.results.iterrows():
            driver = get_or_create_driver(session_obj, row['Abbreviation'], row)
            if not driver:
                continue
            session_obj.add(QualifyingResult(
                race_id=race_entry.id,
                driver_id=driver.id,
                position=int(row['Position']) if pd.notna(row['Position']) else None,
                q1_time=convert_timedelta_to_seconds(row.get('Q1')),
                q2_time=convert_timedelta_to_seconds(row.get('Q2')),
                q3_time=convert_timedelta_to_seconds(row.get('Q3'))
            ))
            count += 1
        session_obj.commit()
        print(f"  Qualifying: {count} results loaded")
    except Exception as e:
        print(f"  ERROR - qualifying: {e}")
        session_obj.rollback()


def load_race_results(session_obj, race_entry, race_session):
    try:
        count = 0
        for _, row in race_session.results.iterrows():
            driver = get_or_create_driver(session_obj, row['Abbreviation'], row)
            if not driver:
                print(f"  WARNING - skipping result for unresolvable driver: {row['Abbreviation']}")
                continue
            team = get_or_create_team(session_obj, row.get('TeamName'))
            session_obj.add(RaceResult(
                race_id=race_entry.id,
                driver_id=driver.id,
                team_id=team.id if team else None,
                grid_position=int(row['GridPosition']) if pd.notna(row['GridPosition']) else None,
                final_position=int(row['Position']) if pd.notna(row['Position']) else None,
                points=float(row['Points']) if pd.notna(row['Points']) else 0.0,
                status=str(row.get('Status', 'Unknown'))
            ))
            count += 1
        session_obj.commit()
        print(f"  Race results: {count} results loaded")
    except Exception as e:
        print(f"  ERROR - race results: {e}")
        session_obj.rollback()


def load_lap_times_sample(session_obj, race_entry, race_session):
    try:
        count = 0
        for _, row in race_session.results.iterrows():
            abbr = row['Abbreviation']
            driver = get_or_create_driver(session_obj, abbr, row)
            if not driver:
                continue
            for _, lap in race_session.laps.pick_driver(abbr).iterrows():
                session_obj.add(LapTime(
                    race_id=race_entry.id,
                    driver_id=driver.id,
                    lap_number=int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
                    lap_time=convert_timedelta_to_seconds(lap.get('LapTime')),
                    compound=str(lap.get('Compound')) if pd.notna(lap.get('Compound')) else None,
                    tyre_life=int(lap['TyreLife']) if pd.notna(lap.get('TyreLife')) else None
                ))
                count += 1
        session_obj.commit()
        print(f"  Lap times: {count} laps loaded")
    except Exception as e:
        print(f"  ERROR - lap times: {e}")
        session_obj.rollback()


def load_pit_stops(session_obj, race_entry, race_session):
    try:
        pit_laps = race_session.laps[race_session.laps['PitOutTime'].notna()]
        count = 0
        for _, lap in pit_laps.iterrows():
            driver = session_obj.query(Driver).filter_by(code=lap['Driver']).first()
            if not driver:
                continue
            session_obj.add(PitStop(
                race_id=race_entry.id,
                driver_id=driver.id,
                lap_number=int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
                compound_after=str(lap.get('Compound')) if pd.notna(lap.get('Compound')) else None
            ))
            count += 1
        session_obj.commit()
        print(f"  Pit stops: {count} loaded")
    except Exception as e:
        print(f"  ERROR - pit stops: {e}")
        session_obj.rollback()


def load_weather_data(session_obj, race_entry, race_session):
    try:
        if not hasattr(race_session, 'weather') or race_session.weather is None:
            print("  No weather data available")
            return
        count = 0
        for _, row in race_session.weather.iloc[::10].iterrows():
            session_obj.add(Weather(
                race_id=race_entry.id,
                air_temp=float(row['AirTemp']) if pd.notna(row.get('AirTemp')) else None,
                track_temp=float(row['TrackTemp']) if pd.notna(row.get('TrackTemp')) else None,
                humidity=float(row['Humidity']) if pd.notna(row.get('Humidity')) else None,
                pressure=float(row['Pressure']) if pd.notna(row.get('Pressure')) else None,
                rainfall=bool(row.get('Rainfall', False)) if pd.notna(row.get('Rainfall')) else False
            ))
            count += 1
        session_obj.commit()
        print(f"  Weather: {count} entries loaded")
    except Exception as e:
        print(f"  ERROR - weather: {e}")
        session_obj.rollback()


def load_race_weekend(year, race_name, session_obj):
    print(f"\n{'='*70}")
    print(f"Loading: {year} {race_name}")
    print(f"{'='*70}")

    try:
        schedule = fastf1.get_event_schedule(year)
        event = schedule[schedule['EventName'] == race_name].iloc[0]

        circuit = get_or_create_circuit(session_obj, event)

        existing_race = session_obj.query(Race).filter_by(
            year=year, race_name=race_name
        ).first()

        if existing_race:
            result_count = session_obj.query(func.count(RaceResult.id)).filter_by(
                race_id=existing_race.id
            ).scalar()
            if result_count >= 15:
                print(f"  Race already complete ({result_count} results). Skipping.")
                return
            else:
                print(f"  Race exists but incomplete ({result_count} results). Reloading data.")
                race_entry = existing_race
        else:
            race_entry = Race(
                year=year,
                round_number=int(event['RoundNumber']),
                race_name=race_name,
                circuit_id=circuit.id,
                race_date=event['EventDate'].date() if pd.notna(event['EventDate']) else None
            )
            session_obj.add(race_entry)
            session_obj.commit()
            print(f"  Created race entry: {race_name}")

        print("  Loading qualifying session...")
        quali = fastf1.get_session(year, race_name, 'Q')
        quali.load()

        print("  Loading race session...")
        race = fastf1.get_session(year, race_name, 'R')
        race.load()

        load_qualifying_results(session_obj, race_entry, quali)
        load_race_results(session_obj, race_entry, race)
        load_lap_times_sample(session_obj, race_entry, race)
        load_pit_stops(session_obj, race_entry, race)
        load_weather_data(session_obj, race_entry, race)

        print(f"  DONE: {year} {race_name}")

    except Exception as e:
        print(f"  FAILED: {year} {race_name} -- {e}")
        session_obj.rollback()


def load_season(year, session_obj, only_completed=False):
    """
    Load all races for a given season.
    If only_completed=True, skips future races (useful for current season).
    """
    print(f"\n{'#'*70}")
    print(f"# LOADING {year} SEASON")
    print(f"{'#'*70}")

    try:
        schedule = fastf1.get_event_schedule(year)
        races = schedule[schedule['RoundNumber'] > 0]

        if only_completed:
            today = date.today()
            races = races[races['EventDate'].dt.date < today]
            print(f"\nFound {len(races)} completed races in {year} (as of {today})")
        else:
            print(f"\nFound {len(races)} races in {year}")

        for i, (_, event) in enumerate(races.iterrows(), 1):
            race_name = event['EventName']
            print(f"\n[{i}/{len(races)}] {race_name}")
            try:
                load_race_weekend(year, race_name, session_obj)
            except Exception as e:
                print(f"  FAILED: {race_name} -- {e}")
                continue

        print(f"\nCompleted {year} season load.")

    except Exception as e:
        print(f"ERROR loading {year} season: {e}")


def update_current_season(session_obj):
    """
    Load only new completed races for the current season.
    Safe to run repeatedly — skips already complete races.
    """
    current_year = date.today().year
    print(f"\n{'#'*70}")
    print(f"# UPDATING {current_year} SEASON (new races only)")
    print(f"{'#'*70}")

    try:
        schedule = fastf1.get_event_schedule(current_year)
        today = date.today()
        completed = schedule[
            (schedule['RoundNumber'] > 0) &
            (schedule['EventDate'].dt.date < today)
        ]
        print(f"\nCompleted races this season: {len(completed)}")

        new_loaded = 0
        for _, event in completed.iterrows():
            race_name = event['EventName']
            existing = session_obj.query(Race).filter_by(
                year=current_year, race_name=race_name
            ).first()

            if existing:
                count = session_obj.query(func.count(RaceResult.id)).filter_by(
                    race_id=existing.id
                ).scalar()
                if count >= 15:
                    print(f"  Skipping {race_name} (already complete)")
                    continue

            print(f"\n  Loading {race_name}...")
            load_race_weekend(current_year, race_name, session_obj)
            new_loaded += 1

        if new_loaded == 0:
            print("\n  All races up to date. Nothing new to load.")
        else:
            print(f"\n  Loaded {new_loaded} new race(s).")

    except Exception as e:
        print(f"ERROR updating current season: {e}")


def print_summary(session_obj):
    from sqlalchemy import text
    from models.database import create_database_engine
    engine = create_database_engine()
    print("\n" + "="*70)
    print("DATABASE SUMMARY")
    print("="*70)
    with engine.connect() as conn:
        for table in ['circuits', 'drivers', 'teams', 'races',
                      'qualifying_results', 'race_results', 'lap_times', 'pit_stops', 'weather']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
            print(f"  {table:<25} {count:>8,} rows")

        # Races per year
        print("\n  Races per year:")
        rows = conn.execute(text(
            "SELECT year, COUNT(*) as races FROM races GROUP BY year ORDER BY year"
        )).fetchall()
        for r in rows:
            print(f"    {r[0]}: {r[1]} races")
    print("="*70 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='F1 ETL Pipeline')
    parser.add_argument(
        '--mode',
        choices=['historical', 'current', 'update'],
        default='update',
        help=(
            'historical: load 2015-2025 | '
            'current: load current season only | '
            'update: load new races in current season (default)'
        )
    )
    parser.add_argument('--year', type=int, help='Specific year to load (historical mode only)')
    args = parser.parse_args()

    session_obj = get_session()

    if args.mode == 'historical':
        print("\n" + "="*70)
        print(" F1 HISTORICAL DATA ETL -- 2015 to 2025")
        print("="*70)
        years = [args.year] if args.year else range(2015, 2026)
        for year in years:
            try:
                load_season(year, session_obj, only_completed=(year == date.today().year))
            except Exception as e:
                print(f"ERROR loading year {year}: {e}")

    elif args.mode == 'current':
        current_year = date.today().year
        print("\n" + "="*70)
        print(f" F1 ETL -- {current_year} SEASON (completed races only)")
        print("="*70)
        load_season(current_year, session_obj, only_completed=True)

    elif args.mode == 'update':
        print("\n" + "="*70)
        print(" F1 ETL -- UPDATE CURRENT SEASON")
        print("="*70)
        update_current_season(session_obj)

    print_summary(session_obj)
    session_obj.close()


if __name__ == "__main__":
    main()