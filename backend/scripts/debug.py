"""
Debug script - test inserting one race to find the exact DB error
"""
import sys
import traceback
from pathlib import Path
import fastf1
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

fastf1.Cache.enable_cache(str(backend_dir / 'fastf1_cache'))

from models.database import get_session, Driver, Team, Race, RaceResult, QualifyingResult

session_obj = get_session()

# -- Step 1: check race entry exists ----------------------------------
race_entry = session_obj.query(Race).filter_by(
    year=2019, race_name='Australian Grand Prix'
).first()
print(f"Race entry: {'found (id=' + str(race_entry.id) + ')' if race_entry else 'NOT FOUND'}")

if not race_entry:
    print("Cannot continue - race entry missing from DB")
    sys.exit(1)

# -- Step 2: load FastF1 session --------------------------------------
print("\nLoading FastF1 race session...")
race_session = fastf1.get_session(2019, 'Australian Grand Prix', 'R')
race_session.load()
print(f"FastF1 loaded: {len(race_session.results)} drivers")

# -- Step 3: check drivers and teams exist in DB ----------------------
print("\nChecking drivers and teams in DB:")
for _, row in race_session.results.iterrows():
    abbr = row['Abbreviation']
    team_name = row.get('TeamName')
    driver = session_obj.query(Driver).filter_by(code=abbr).first()
    team = session_obj.query(Team).filter_by(name=team_name).first()
    d_status = "OK" if driver else "MISSING"
    t_status = "OK" if team else "MISSING"
    print(f"  {abbr:<6} driver={d_status:<8} team={str(team_name):<30} team_status={t_status}")

# -- Step 4: attempt insert one by one --------------------------------
print("\nAttempting inserts one by one:")
for _, row in race_session.results.iterrows():
    abbr = row['Abbreviation']
    try:
        driver = session_obj.query(Driver).filter_by(code=abbr).first()
        team = session_obj.query(Team).filter_by(name=row.get('TeamName')).first()

        r = RaceResult(
            race_id=race_entry.id,
            driver_id=driver.id if driver else None,
            team_id=team.id if team else None,
            grid_position=int(row['GridPosition']) if pd.notna(row['GridPosition']) else None,
            final_position=int(row['Position']) if pd.notna(row['Position']) else None,
            points=float(row['Points']) if pd.notna(row['Points']) else 0.0,
            status=str(row.get('Status', 'Unknown'))
        )
        session_obj.add(r)
        session_obj.flush()  # flush each row so we see exactly which one fails
        print(f"  {abbr}: OK")
    except Exception as e:
        print(f"  {abbr}: FAILED")
        traceback.print_exc()
        session_obj.rollback()
        break

session_obj.rollback()  # don't actually save - this is just a test
print("\nDebug complete.")