"""
Fill Missing Race Results
Finds races that have 0 results and loads only the missing data.
Does NOT touch races that already have complete data.
"""
import sys
from pathlib import Path
import fastf1
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

from sqlalchemy import text
from models.database import (
    get_session, Driver, Team, Race,
    QualifyingResult, RaceResult, LapTime, PitStop, Weather
)

# -- FastF1 cache -----------------------------------------------------
cache_dir = backend_dir / 'fastf1_cache'
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))

# -- Helpers (same as original ETL) -----------------------------------
def td_to_sec(td):
    if pd.isna(td):
        return None
    try:
        return td.total_seconds()
    except (AttributeError, TypeError):
        return None

def get_or_create_driver(session_obj, abbr, info=None):
    if pd.isna(abbr) or not abbr:
        return None
    abbr = str(abbr).strip()
    driver = session_obj.query(Driver).filter_by(code=abbr).first()
    if not driver and info is not None:
        try:
            num = int(info.get('DriverNumber', 0)) if pd.notna(info.get('DriverNumber')) else None
        except (ValueError, TypeError):
            num = None
        driver = Driver(
            driver_number=num,
            code=abbr,
            first_name=str(info.get('FirstName', '')),
            last_name=str(info.get('LastName', '')),
            broadcast_name=str(info.get('BroadcastName', abbr)),
            nationality=str(info.get('CountryCode', 'Unknown'))
        )
        session_obj.add(driver)
        session_obj.commit()
        print(f"  Created driver: {driver.broadcast_name} ({abbr})")
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

# -- Loaders ----------------------------------------------------------
def load_qualifying(session_obj, race_entry, quali_session):
    session_obj.query(QualifyingResult).filter_by(race_id=race_entry.id).delete()
    session_obj.commit()
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
                q1_time=td_to_sec(row.get('Q1')),
                q2_time=td_to_sec(row.get('Q2')),
                q3_time=td_to_sec(row.get('Q3'))
            ))
            count += 1
        session_obj.commit()
        print(f"  Qualifying: {count} results loaded")
    except Exception as e:
        print(f"  ERROR - Qualifying: {e}")
        session_obj.rollback()

def load_results(session_obj, race_entry, race_session):
    session_obj.query(RaceResult).filter_by(race_id=race_entry.id).delete()
    session_obj.commit()
    try:
        count = 0
        for _, row in race_session.results.iterrows():
            # Always try to create driver if missing - never skip silently
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
        print(f"  ERROR - Race results: {e}")
        session_obj.rollback()

def load_laps(session_obj, race_entry, race_session):
    session_obj.query(LapTime).filter_by(race_id=race_entry.id).delete()
    session_obj.commit()
    try:
        count = 0
        for abbr in race_session.results['Abbreviation'].tolist():
            driver = get_or_create_driver(session_obj, abbr, 
                race_session.results[race_session.results['Abbreviation'] == abbr].iloc[0] 
                if not race_session.results[race_session.results['Abbreviation'] == abbr].empty else None)
            if not driver:
                continue
            for _, lap in race_session.laps.pick_driver(abbr).iterrows():
                session_obj.add(LapTime(
                    race_id=race_entry.id,
                    driver_id=driver.id,
                    lap_number=int(lap['LapNumber']) if pd.notna(lap['LapNumber']) else None,
                    lap_time=td_to_sec(lap.get('LapTime')),
                    compound=str(lap.get('Compound')) if pd.notna(lap.get('Compound')) else None,
                    tyre_life=int(lap['TyreLife']) if pd.notna(lap.get('TyreLife')) else None
                ))
                count += 1
        session_obj.commit()
        print(f"  Lap times: {count} laps loaded")
    except Exception as e:
        print(f"  ERROR - Lap times: {e}")
        session_obj.rollback()

def load_pits(session_obj, race_entry, race_session):
    session_obj.query(PitStop).filter_by(race_id=race_entry.id).delete()
    session_obj.commit()
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
        print(f"  ERROR - Pit stops: {e}")
        session_obj.rollback()

# -- Main -------------------------------------------------------------
def main():
    session_obj = get_session()

    print("\nFinding races with missing results...\n")
    rows = session_obj.execute(text("""
        SELECT r.id, r.year, r.round_number, r.race_name
        FROM races r
        LEFT JOIN race_results rr ON rr.race_id = r.id
        WHERE r.round_number > 0
        GROUP BY r.id, r.year, r.round_number, r.race_name
        HAVING COUNT(rr.id) < 15
        ORDER BY r.year, r.round_number
    """)).fetchall()

    print(f"Found {len(rows)} races needing data\n")
    for row in rows:
        print(f"  {row[1]} Rd{row[2]:>2} -- {row[3]}")

    print(f"\n{'-'*60}")
    print(f"Starting fill... ({len(rows)} races)")
    print(f"{'-'*60}")

    success, failed = 0, []

    for i, row in enumerate(rows, 1):
        race_id, year, rnd, name = row
        print(f"\n[{i}/{len(rows)}] {year} -- {name}")

        race_entry = session_obj.query(Race).filter_by(id=race_id).first()

        try:
            print("  Loading qualifying session...")
            quali = fastf1.get_session(year, name, 'Q')
            quali.load()
            load_qualifying(session_obj, race_entry, quali)

            print("  Loading race session...")
            race_session = fastf1.get_session(year, name, 'R')
            race_session.load()

            for _, dr in race_session.results.iterrows():
                get_or_create_driver(session_obj, dr['Abbreviation'], dr)
                get_or_create_team(session_obj, dr.get('TeamName'))

            load_results(session_obj, race_entry, race_session)
            load_laps(session_obj, race_entry, race_session)
            load_pits(session_obj, race_entry, race_session)

            success += 1
            print(f"  DONE: {year} {name}")

        except Exception as e:
            print(f"  FAILED: {year} {name} -- {e}")
            failed.append(f"{year} {name}")
            session_obj.rollback()
            continue

    print(f"\n{'-'*60}")
    print(f"FILL COMPLETE")
    print(f"  Success: {success}")
    print(f"  Failed:  {len(failed)}")
    if failed:
        print("\nFailed races:")
        for f in failed:
            print(f"  - {f}")
    print(f"{'-'*60}\n")
    session_obj.close()

if __name__ == "__main__":
    main()