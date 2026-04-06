"""
F1 Data Scheduler
Automatically loads new race results after each race weekend.
Runs as a background service alongside the FastAPI backend.
"""
import sys
import subprocess
from pathlib import Path
import fastf1
import pandas as pd
from datetime import date, timedelta
import time
import logging

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

fastf1.Cache.enable_cache(str(backend_dir / 'fastf1_cache'))

from sqlalchemy import func
from models.database import get_session, Race, RaceResult

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s  %(levelname)s  %(message)s',
    handlers=[
        logging.FileHandler(backend_dir / 'scheduler.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Import ETL functions from etl_historical ──────────────────
from scripts.etl_historical import (
    get_or_create_circuit,
    get_or_create_driver,
    get_or_create_team,
    load_qualifying_results,
    load_race_results,
    load_lap_times_sample,
    load_pit_stops,
    load_weather_data,
)

CHECK_INTERVAL_HOURS = 6   # check every 6 hours
RACE_DAY = 6               # Sunday (0=Monday ... 6=Sunday)
RESULTS_DELAY_HOURS = 4    # wait 4 hours after race start before fetching


def get_completed_races_missing_results(session_obj, year: int) -> list:
    """Return races that have happened but have no results in DB yet."""
    today = date.today()
    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as e:
        log.warning(f"Could not fetch {year} schedule: {e}")
        return []

    missing = []
    races = schedule[
        (schedule['RoundNumber'] > 0) &
        (schedule['EventDate'].dt.date <= today)
    ]

    for _, event in races.iterrows():
        race_name = event['EventName']
        existing  = session_obj.query(Race).filter_by(
            year=year, race_name=race_name
        ).first()

        if existing:
            count = session_obj.query(RaceResult).filter_by(
                race_id=existing.id
            ).count()
            if count >= 15:
                continue  # already complete
        missing.append(event)

    return missing


def load_single_race(session_obj, year: int, event) -> bool:
    """Load a single race weekend into the DB."""
    race_name    = event['EventName']
    round_number = int(event['RoundNumber'])

    log.info(f"Loading {year} {race_name}...")

    existing = session_obj.query(Race).filter_by(
        year=year, race_name=race_name
    ).first()

    if existing:
        race_entry = existing
    else:
        circuit    = get_or_create_circuit(session_obj, event)
        race_entry = Race(
            year=year,
            round_number=round_number,
            race_name=race_name,
            circuit_id=circuit.id,
            race_date=event['EventDate'].date() if pd.notna(event['EventDate']) else None
        )
        session_obj.add(race_entry)
        session_obj.commit()

    try:
        quali = fastf1.get_session(year, race_name, 'Q')
        quali.load()

        race_session = fastf1.get_session(year, race_name, 'R')
        race_session.load()

        # Ensure drivers/teams exist
        for _, dr in race_session.results.iterrows():
            get_or_create_driver(session_obj, dr['Abbreviation'], dr)
            get_or_create_team(session_obj, dr.get('TeamName'))

        load_qualifying_results(session_obj, race_entry, quali)
        load_race_results(session_obj, race_entry, race_session)
        load_lap_times_sample(session_obj, race_entry, race_session)
        load_pit_stops(session_obj, race_entry, race_session)
        load_weather_data(session_obj, race_entry, race_session)

        log.info(f"Successfully loaded {year} {race_name}")
        return True

    except Exception as e:
        log.error(f"Failed to load {year} {race_name}: {e}")
        session_obj.rollback()
        return False


def retrain_model():
    """Retrain the ML model after new race data is loaded."""
    log.info("Retraining ML model...")
    try:
        result = subprocess.run(
            [sys.executable, str(backend_dir / 'models' / 'train_model.py')],
            capture_output=True, text=True, cwd=str(backend_dir)
        )
        if result.returncode == 0:
            log.info("Model retrained successfully")
            for line in result.stdout.strip().split('\n')[-5:]:
                if line.strip():
                    log.info(f"  {line}")
        else:
            log.error(f"Model retraining failed:\n{result.stderr[-500:]}")
    except Exception as e:
        log.error(f"Model retraining error: {e}")


def run_check():
    """Single check cycle — finds and loads any missing race results."""
    log.info("Running scheduled check...")
    session_obj = get_session()

    try:
        current_year = date.today().year
        years_to_check = [current_year]

        # Also check previous year if we're in Jan/Feb
        if date.today().month <= 2:
            years_to_check.append(current_year - 1)

        total_loaded = 0
        for year in years_to_check:
            missing = get_completed_races_missing_results(session_obj, year)
            if missing:
                log.info(f"Found {len(missing)} races needing data for {year}")
                for event in missing:
                    success = load_single_race(session_obj, year, event)
                    if success:
                        total_loaded += 1
                    # Rate limit between races
                    time.sleep(10)
            else:
                log.info(f"{year}: all races up to date")

        if total_loaded > 0:
            log.info(f"Loaded {total_loaded} new race(s) -- retraining model...")
            retrain_model()
        else:
            log.info("No new races to load")

    except Exception as e:
        log.error(f"Check failed: {e}")
    finally:
        session_obj.close()


def main():
    log.info("F1 Data Scheduler started")
    log.info(f"Check interval: every {CHECK_INTERVAL_HOURS} hours")
    log.info("Press Ctrl+C to stop\n")

    # Run once immediately on startup
    run_check()

    # Then run on schedule
    while True:
        sleep_seconds = CHECK_INTERVAL_HOURS * 3600
        log.info(f"Next check in {CHECK_INTERVAL_HOURS} hours...")
        time.sleep(sleep_seconds)
        run_check()


if __name__ == "__main__":
    main()