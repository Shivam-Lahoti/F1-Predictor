"""
Verify ML model accuracy against completed 2026 races.
Runs predictions for each completed 2026 race using only
data available BEFORE that race, then compares to actual results.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from sqlalchemy import text

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

from models.database import get_session

session = get_session()

SEP = "=" * 65

# -- Load model and features --------------------------------------
model_path    = backend_dir / 'ml' / 'race_predictor.pkl'
features_path = backend_dir / 'ml' / 'features.pkl'

if not model_path.exists() or not features_path.exists():
    print("ERROR: Model or features not found. Run train_model.py first.")
    sys.exit(1)

model    = joblib.load(model_path)
FEATURES = joblib.load(features_path)
print(f"Loaded model with {len(FEATURES)} features: {FEATURES}")

# -- Load full historical data ------------------------------------
print("\nLoading historical data...")
hist = pd.read_sql(text("""
    SELECT rr.id, r.year, r.round_number, r.circuit_id,
           d.code AS driver_code, d.id AS driver_id,
           t.id AS team_id, t.name AS team_name,
           rr.grid_position, rr.final_position, rr.points, rr.status,
           qr.position AS quali_position
    FROM race_results rr
    JOIN races r        ON rr.race_id   = r.id
    JOIN drivers d      ON rr.driver_id = d.id
    LEFT JOIN teams t   ON rr.team_id   = t.id
    LEFT JOIN qualifying_results qr
        ON qr.race_id = r.id AND qr.driver_id = d.id
    ORDER BY r.year, r.round_number
"""), session.bind)

# -- Get completed 2026 races -------------------------------------
races_2026 = pd.read_sql(text("""
    SELECT r.id, r.year, r.round_number, r.race_name, r.circuit_id
    FROM races r
    WHERE r.year = 2026
    ORDER BY r.round_number
"""), session.bind)

print(f"Verifying against {len(races_2026)} completed 2026 races\n")

def exp_avg(vals, alpha=0.7):
    if len(vals) == 0:
        return np.nan
    w = np.array([alpha ** (len(vals) - i - 1) for i in range(len(vals))])
    return float(np.average(vals, weights=w / w.sum()))

def build_features(code, prior, circuit_id, qpos):
    dh     = prior[prior['driver_code'] == code]
    recent = dh.tail(5)

    avg_pts5  = exp_avg(recent['points'].tolist()) or 0
    avg_pos5  = exp_avg(recent['final_position'].dropna().tolist()) or 12
    avg_pts3  = dh['points'].tail(3).mean() if len(dh) > 0 else 0
    avg_pos3  = dh['final_position'].tail(3).mean() if len(dh) > 0 else 12
    dnf_rate  = dh['status'].str.contains(
        'Retired|Accident|Mechanical|Engine|Gearbox|Hydraulics|Power|Brake|Wheel|Crash',
        case=False, na=False).mean() if len(dh) > 0 else 0.1
    quali_std = dh['quali_position'].tail(5).std() if len(dh) >= 2 else 3.0

    ch    = dh[dh['circuit_id'] == circuit_id]
    n_ch  = len(ch)
    if n_ch > 0:
        w = np.array([0.7 ** (n_ch - i - 1) for i in range(n_ch)])
        w /= w.sum()
        circ_avg_pos  = float(np.average(ch['final_position'].fillna(12), weights=w))
        circ_avg_pts  = float(np.average(ch['points'].fillna(0), weights=w))
        circ_win_rate = float((ch['final_position'] == 1).mean())
        circ_dnf_rate = float(ch['status'].str.contains(
            'Retired|Accident|Mechanical', case=False, na=False).mean())
    else:
        circ_avg_pos, circ_avg_pts, circ_win_rate, circ_dnf_rate = 12, 0, 0, 0.1

    latest_year  = dh['year'].max() if len(dh) > 0 else 0
    th           = dh[dh['year'] == latest_year]
    team_avg_pts  = th['points'].mean() if len(th) > 0 else 0
    team_avg_pos  = th['final_position'].mean() if len(th) > 0 else 12
    team_win_rate = (th['final_position'] == 1).mean() if len(th) > 0 else 0

    return {
        'quali_pos':            float(qpos),
        'driver_avg_pts_last5': float(avg_pts5 or 0),
        'driver_avg_pos_last5': float(avg_pos5 or 12),
        'driver_avg_pts_last3': float(avg_pts3 or 0),
        'driver_avg_pos_last3': float(avg_pos3 or 12),
        'driver_dnf_rate':      float(dnf_rate),
        'quali_consistency':    float(quali_std or 3.0),
        'circuit_win_rate':     float(circ_win_rate),
        'circuit_avg_pos':      float(circ_avg_pos),
        'circuit_avg_pts':      float(circ_avg_pts),
        'circuit_dnf_rate':     float(circ_dnf_rate),
        'circuit_races':        float(n_ch),
        'team_avg_pts':         float(team_avg_pts or 0),
        'team_avg_pos':         float(team_avg_pos or 12),
        'team_win_rate':        float(team_win_rate),
        'career_races':         float(len(dh)),
        'grid_quali_delta':     0.0,
    }

all_errors = []

for _, race in races_2026.iterrows():
    race_id    = race['id']
    race_name  = race['race_name']
    round_num  = race['round_number']
    circuit_id = race['circuit_id']

    actuals = pd.read_sql(text("""
        SELECT d.code AS driver_code, rr.final_position, rr.status
        FROM race_results rr
        JOIN drivers d ON rr.driver_id = d.id
        WHERE rr.race_id = :race_id
        ORDER BY rr.final_position
    """), session.bind, params={'race_id': int(race_id)})

    if len(actuals) == 0:
        print(f"  {race_name}: no results in DB, skipping")
        continue

    quali = pd.read_sql(text("""
        SELECT d.code AS driver_code, qr.position AS quali_position
        FROM qualifying_results qr
        JOIN drivers d ON qr.driver_id = d.id
        WHERE qr.race_id = :race_id
    """), session.bind, params={'race_id': int(race_id)})

    # Only use data available BEFORE this race
    prior = hist[
        (hist['year'] < 2026) |
        ((hist['year'] == 2026) & (hist['round_number'] < round_num))
    ]

    pred_rows = []
    for _, actual_row in actuals.iterrows():
        code  = actual_row['driver_code']
        q_row = quali[quali['driver_code'] == code]
        qpos  = float(q_row['quali_position'].values[0]) \
                if len(q_row) > 0 and pd.notna(q_row['quali_position'].values[0]) else 20.0

        feat = build_features(code, prior, circuit_id, qpos)
        feat['driver_code']     = code
        feat['actual_position'] = actual_row['final_position']
        feat['status']          = actual_row['status']
        pred_rows.append(feat)

    pred_df = pd.DataFrame(pred_rows)
    X = pred_df[FEATURES].fillna(0)
    pred_df['predicted_score'] = model.predict(X)
    pred_df = pred_df.sort_values('predicted_score').reset_index(drop=True)
    pred_df['predicted_rank']  = pred_df.index + 1

    finished = pred_df[~pred_df['status'].isin(['DNS', 'Disqualified'])]
    finished = finished[finished['actual_position'].notna()].copy()
    finished['error'] = abs(finished['predicted_rank'] - finished['actual_position'])

    mae     = finished['error'].mean()
    within2 = (finished['error'] <= 2).sum()
    within5 = (finished['error'] <= 5).sum()
    exact   = (finished['error'] == 0).sum()
    n       = len(finished)

    all_errors.extend(finished['error'].tolist())

    print(f"{SEP}")
    print(f"  {race['year']} {race_name} (Rd {round_num})")
    print(f"{SEP}")
    print(f"  {'Driver':<8} {'Pred':>6} {'Actual':>8} {'Error':>7}   Status")
    print(f"  {'-'*52}")
    for _, row in pred_df.sort_values('actual_position').iterrows():
        pred   = f"P{int(row['predicted_rank'])}"
        actual = f"P{int(row['actual_position'])}" if pd.notna(row['actual_position']) else row['status']
        err    = f"{int(row['error'])}" if pd.notna(row.get('error')) else '-'
        flag   = '<' if pd.notna(row.get('error')) and row.get('error', 99) <= 2 else ''
        print(f"  {row['driver_code']:<8} {pred:>6} {actual:>8} {err:>7}   {row['status']:<12} {flag}")

    print(f"\n  MAE          : {mae:.2f} positions")
    print(f"  Exact        : {exact}/{n}")
    print(f"  Within 2 pos : {within2}/{n} ({within2/n*100:.0f}%)")
    print(f"  Within 5 pos : {within5}/{n} ({within5/n*100:.0f}%)\n")

# -- Overall summary ----------------------------------------------
if all_errors:
    arr = np.array(all_errors)
    print(f"{SEP}")
    print(f"  OVERALL MODEL ACCURACY (all {len(races_2026)} completed 2026 races)")
    print(f"{SEP}")
    print(f"  Total predictions : {len(arr)}")
    print(f"  Overall MAE       : {arr.mean():.2f} positions")
    print(f"  Median error      : {np.median(arr):.2f} positions")
    print(f"  Within 1 position : {(arr <= 1).sum()} ({(arr <= 1).mean()*100:.0f}%)")
    print(f"  Within 2 positions: {(arr <= 2).sum()} ({(arr <= 2).mean()*100:.0f}%)")
    print(f"  Within 5 positions: {(arr <= 5).sum()} ({(arr <= 5).mean()*100:.0f}%)")
    print(f"  Exact predictions : {(arr == 0).sum()} ({(arr == 0).mean()*100:.0f}%)")
    print(f"{SEP}\n")

session.close()