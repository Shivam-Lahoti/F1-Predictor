from fastapi import APIRouter, HTTPException
import sys
from pathlib import Path
import pandas as pd
from datetime import date
import glob

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from models.database import get_session

router = APIRouter(prefix="/api/predict", tags=["predictions"])


def get_latest_prediction_file() -> Path | None:
    """Return the most recently saved predictions CSV."""
    pattern = str(backend_dir / 'ml' / 'predictions_2026_rd*.csv')
    files = sorted(glob.glob(pattern))
    return Path(files[-1]) if files else None


@router.get("/next")
def get_next_race_predictions():
    """Get ML predictions for the next upcoming race."""
    pred_file = get_latest_prediction_file()
    if not pred_file:
        raise HTTPException(status_code=404, detail="No predictions available yet")

    preds = pd.read_csv(pred_file)

    # Extract round number from filename e.g. predictions_2026_rd04.csv
    round_number = int(pred_file.stem.split('_rd')[-1])

    session = get_session()
    try:
        # Get race info
        race = session.execute(text("""
            SELECT r.id, r.race_name, r.race_date, r.round_number,
                   c.name AS circuit_name, c.country, c.location
            FROM races r
            JOIN circuits c ON r.circuit_id = c.id
            WHERE r.year = 2026 AND r.round_number = :rnd
            LIMIT 1
        """), {'rnd': round_number}).fetchone()

        # Get qualifying grid for this race if available
        quali = {}
        if race:
            quali_rows = session.execute(text("""
                SELECT d.code, qr.position
                FROM qualifying_results qr
                JOIN drivers d ON qr.driver_id = d.id
                WHERE qr.race_id = :race_id
            """), {'race_id': race[0]}).fetchall()
            quali = {row[0]: row[1] for row in quali_rows}

        # Get driver full names
        driver_info = session.execute(text("""
            SELECT code, first_name, last_name, nationality,
                   broadcast_name
            FROM drivers
        """)).fetchall()
        drivers = {
            row[0]: {
                'first_name':     row[1] or '',
                'last_name':      row[2] or '',
                'nationality':    row[3] or '',
                'broadcast_name': row[4] or row[0],
                'full_name':      f"{row[1] or ''} {row[2] or ''}".strip() or row[0]
            }
            for row in driver_info
        }

        # Get team for each driver from latest 2026 race
        team_rows = session.execute(text("""
            SELECT DISTINCT ON (d.code) d.code, t.name AS team
            FROM race_results rr
            JOIN races r    ON rr.race_id   = r.id
            JOIN drivers d  ON rr.driver_id = d.id
            JOIN teams t    ON rr.team_id   = t.id
            WHERE r.year = 2026
            ORDER BY d.code, r.round_number DESC
        """)).fetchall()
        teams = {row[0]: row[1] for row in team_rows}

        predictions = []
        for _, row in preds.iterrows():
            code = row['driver_code']
            info = drivers.get(code, {})
            predictions.append({
                'predicted_position': int(row['predicted_rank']),
                'predicted_score':    round(float(row['predicted_score']), 3),
                'driver_code':        code,
                'driver_name':        info.get('full_name', code),
                'broadcast_name':     info.get('broadcast_name', code),
                'nationality':        info.get('nationality', ''),
                'team':               teams.get(code, 'Unknown'),
                'qualifying_position': quali.get(code),
            })

        return {
            'race': {
                'round_number':  round_number,
                'race_name':     race[1] if race else f'2026 Round {round_number}',
                'race_date':     str(race[2]) if race else None,
                'circuit_name':  race[4] if race else None,
                'country':       race[5] if race else None,
                'location':      race[6] if race else None,
            },
            'predictions':      predictions,
            'model_info': {
                'trained_on':   '2015-2026',
                'races_used':   244,
                'generated_at': str(date.today()),
            }
        }

    finally:
        session.close()


@router.get("/history")
def get_prediction_history():
    """List all available prediction files."""
    pattern = str(backend_dir / 'ml' / 'predictions_2026_rd*.csv')
    files = sorted(glob.glob(pattern))
    result = []
    for f in files:
        p = Path(f)
        rnd = int(p.stem.split('_rd')[-1])
        df  = pd.read_csv(f)
        result.append({
            'round':      rnd,
            'file':       p.name,
            'drivers':    len(df),
            'top3':       df.head(3)['driver_code'].tolist()
        })
    return result