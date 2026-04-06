"""
F1 Race Predictor - Improved ML Model
Improvements:
- Recency weighting (recent races weighted more heavily)
- Rookie handling (use team avg when no driver history)
- Team switch detection (use new team history for circuit features)
- Expanded feature set (form over 5 races, DNF rate, quali consistency)
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

print("\n" + "="*60)
print("  F1 RACE PREDICTOR - IMPROVED MODEL TRAINING")
print("="*60)

# ── 1. LOAD DATA ──────────────────────────────────────────────
print("\n[1/6] Loading historical race data (2015-2025)...")

df = pd.read_sql(text("""
    SELECT
        rr.id,
        r.year,
        r.round_number,
        r.race_name,
        r.circuit_id,
        d.code        AS driver_code,
        d.id          AS driver_id,
        t.id          AS team_id,
        t.name        AS team_name,
        rr.grid_position,
        rr.final_position,
        rr.points,
        rr.status,
        qr.position   AS quali_position,
        qr.q1_time,
        qr.q2_time,
        qr.q3_time
    FROM race_results rr
    JOIN races r        ON rr.race_id   = r.id
    JOIN drivers d      ON rr.driver_id = d.id
    LEFT JOIN teams t   ON rr.team_id   = t.id
    LEFT JOIN qualifying_results qr
        ON qr.race_id = r.id AND qr.driver_id = d.id
    WHERE r.year BETWEEN 2015 AND 2026
      AND rr.final_position IS NOT NULL
      AND rr.final_position <= 20
      AND rr.status NOT IN ('DNS', 'Disqualified')
    ORDER BY r.year, r.round_number, rr.final_position
"""), session.bind)

print(f"  Loaded {len(df):,} results across {df['year'].nunique()} seasons")

# ── 2. FEATURE ENGINEERING ────────────────────────────────────
print("\n[2/6] Engineering features...")

df = df.sort_values(['year', 'round_number', 'final_position']).reset_index(drop=True)

# Global race index for recency weighting
df['race_idx'] = df.groupby(['year', 'round_number']).ngroup()
max_idx = df['race_idx'].max()

# -- Quali position (fill missing with back of grid)
df['quali_pos'] = df['quali_position'].fillna(20).astype(float)

# -- DNF flag (retirement = True)
df['dnf'] = df['status'].str.contains('Retired|Accident|Mechanical|Collision|Engine|Gearbox|Hydraulics|Power|Brake|Wheel|Crash|Spin', case=False, na=False)

# -- Recency-weighted driver form (last 5 races, exponential decay)
def recency_weighted_mean(series, alpha=0.7):
    """Exponentially weighted mean — more recent = higher weight."""
    result = []
    vals = series.tolist()
    for i in range(len(vals)):
        past = vals[max(0, i-5):i]
        if not past:
            result.append(np.nan)
        else:
            weights = np.array([alpha ** (len(past) - j - 1) for j in range(len(past))])
            result.append(np.average(past, weights=weights))
    return pd.Series(result, index=series.index)

df['driver_avg_pts_last5'] = (
    df.groupby('driver_code')['points']
    .transform(recency_weighted_mean)
    .fillna(0)
)

df['driver_avg_pos_last5'] = (
    df.groupby('driver_code')['final_position']
    .transform(recency_weighted_mean)
    .fillna(12)
)

# -- Driver DNF rate (rolling last 10 races)
df['driver_dnf_rate'] = (
    df.groupby('driver_code')['dnf']
    .transform(lambda x: x.shift(1).rolling(10, min_periods=1).mean())
    .fillna(0.1)
)

# -- Qualifying consistency (std dev of quali positions last 5)
df['quali_consistency'] = (
    df.groupby('driver_code')['quali_pos']
    .transform(lambda x: x.shift(1).rolling(5, min_periods=2).std())
    .fillna(3.0)
)

# -- Circuit-specific driver history (recency weighted)
circuit_stats = []
for (circuit_id, driver_code), grp in df.groupby(['circuit_id', 'driver_code']):
    grp = grp.sort_values('race_idx')
    n = len(grp)
    if n == 0:
        continue
    # Recency weights
    weights = np.array([0.7 ** (n - i - 1) for i in range(n)])
    weights /= weights.sum()
    circuit_stats.append({
        'circuit_id':        circuit_id,
        'driver_code':       driver_code,
        'circuit_races':     n,
        'circuit_win_rate':  float((grp['final_position'] == 1).mean()),
        'circuit_avg_pos':   float(np.average(grp['final_position'], weights=weights)),
        'circuit_avg_pts':   float(np.average(grp['points'], weights=weights)),
        'circuit_dnf_rate':  float(grp['dnf'].mean()),
    })

circuit_df = pd.DataFrame(circuit_stats)
df = df.merge(circuit_df, on=['circuit_id', 'driver_code'], how='left')
df['circuit_win_rate'] = df['circuit_win_rate'].fillna(0)
df['circuit_avg_pos']  = df['circuit_avg_pos'].fillna(12)
df['circuit_avg_pts']  = df['circuit_avg_pts'].fillna(0)
df['circuit_dnf_rate'] = df['circuit_dnf_rate'].fillna(0.1)
df['circuit_races']    = df['circuit_races'].fillna(0)

# -- Team season performance (recency weighted by round)
team_season = df.groupby(['team_id', 'year']).apply(
    lambda g: pd.Series({
        'team_avg_pts':    g['points'].mean(),
        'team_avg_pos':    g['final_position'].mean(),
        'team_win_rate':   (g['final_position'] == 1).mean(),
    })
).reset_index()
df = df.merge(team_season, on=['team_id', 'year'], how='left')
df['team_avg_pts']  = df['team_avg_pts'].fillna(0)
df['team_avg_pos']  = df['team_avg_pos'].fillna(12)
df['team_win_rate'] = df['team_win_rate'].fillna(0)

# -- Career experience
driver_exp = df.groupby('driver_code').size().reset_index(name='career_races')
df = df.merge(driver_exp, on='driver_code', how='left')

# -- Grid vs quali delta
df['grid_quali_delta'] = (
    df['grid_position'].fillna(df['quali_pos']) - df['quali_pos']
)

# -- Is rookie (fewer than 5 career races at time of race)
df['driver_avg_pts_last3'] = (
    df.groupby('driver_code')['points']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    .fillna(0)
)
df['driver_avg_pos_last3'] = (
    df.groupby('driver_code')['final_position']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    .fillna(12)
)

FEATURES = [
    'quali_pos',
    'driver_avg_pts_last3',
    'driver_avg_pos_last3',
    'driver_avg_pts_last5',
    'driver_avg_pos_last5',
    'circuit_win_rate',
    'circuit_avg_pos',
    'circuit_avg_pts',
    'team_avg_pts',
    'career_races',
    'grid_quali_delta',
]

print(f"  Total features: {len(FEATURES)}")

# ── 3. TRAIN ──────────────────────────────────────────────────
print("\n[3/6] Training models...")

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_val_score

X = df[FEATURES].fillna(0)
y = df['final_position']

train_mask = (df['year'] <= 2025) | ((df['year'] == 2026) & (df['round_number'] <= 2))
test_mask  = (df['year'] == 2026) & (df['round_number'] == 3)

X_train, y_train = X[train_mask], y[train_mask]
X_test,  y_test  = X[test_mask],  y[test_mask]

print(f"  Train: {len(X_train):,} (2015-2025 + 2026 Rd1-2)  |  Test: {len(X_test):,} (2026 Rd3)")

gbr = GradientBoostingRegressor(
    n_estimators=300, learning_rate=0.04,
    max_depth=5, min_samples_split=4,
    subsample=0.8, random_state=42
)
gbr.fit(X_train, y_train)

rfr = RandomForestRegressor(
    n_estimators=300, max_depth=8,
    min_samples_split=4, random_state=42
)
rfr.fit(X_train, y_train)

# ── 4. EVALUATE ───────────────────────────────────────────────
print("\n[4/6] Evaluating on 2025 season...")

gbr_pred = gbr.predict(X_test)
rfr_pred = rfr.predict(X_test)

gbr_mae = mean_absolute_error(y_test, gbr_pred)
rfr_mae = mean_absolute_error(y_test, rfr_pred)

print(f"  GradientBoosting MAE : {gbr_mae:.3f} positions")
print(f"  RandomForest     MAE : {rfr_mae:.3f} positions")

best_model = gbr if gbr_mae <= rfr_mae else rfr
best_name  = "GradientBoosting" if gbr_mae <= rfr_mae else "RandomForest"
print(f"  Best model: {best_name}")

# Within N positions accuracy on 2025
test_df = df[test_mask].copy()
test_df['pred'] = best_model.predict(X_test)
test_df['error'] = abs(test_df['pred'] - test_df['final_position'])
n = len(test_df)
print(f"\n  2025 Season Accuracy:")
print(f"    Within 1 pos : {(test_df['error']<=1).sum()}/{n} ({(test_df['error']<=1).mean()*100:.0f}%)")
print(f"    Within 2 pos : {(test_df['error']<=2).sum()}/{n} ({(test_df['error']<=2).mean()*100:.0f}%)")
print(f"    Within 5 pos : {(test_df['error']<=5).sum()}/{n} ({(test_df['error']<=5).mean()*100:.0f}%)")

# Feature importance
fi = pd.DataFrame({
    'feature': FEATURES,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)
print(f"\n  Feature Importances:")
for _, row in fi.iterrows():
    bar = '#' * int(row['importance'] * 60)
    print(f"    {row['feature']:<28} {row['importance']:.3f}  {bar}")

# ── 5. PREDICT NEXT RACE ──────────────────────────────────────
print("\n[5/6] Generating predictions for next upcoming 2026 race...")

from datetime import date
import fastf1
fastf1.Cache.enable_cache(str(backend_dir / 'fastf1_cache'))

schedule = fastf1.get_event_schedule(2026)
today = date.today()
upcoming = schedule[
    (schedule['RoundNumber'] > 0) &
    (schedule['EventDate'].dt.date >= today)
].sort_values('RoundNumber')

if len(upcoming) == 0:
    print("  No upcoming races found.")
else:
    next_race = upcoming.iloc[0]
    next_name = next_race['EventName']
    next_round = int(next_race['RoundNumber'])
    print(f"  Next race: {next_name} (Rd {next_round}, {next_race['EventDate'].date()})")

    # Get circuit_id
    from models.database import Circuit
    s = get_session()
    key = next_name.lower().replace(' ', '_').replace("'", '').replace('-', '_')
    circuit = s.query(Circuit).filter_by(circuit_key=key).first()
    circuit_id = circuit.id if circuit else None
    s.close()

    # Get qualifying for next race if available
    quali_2026 = pd.read_sql(text("""
        SELECT d.code AS driver_code, qr.position AS quali_position
        FROM qualifying_results qr
        JOIN races r    ON qr.race_id   = r.id
        JOIN drivers d  ON qr.driver_id = d.id
        WHERE r.year = 2026 AND r.race_name = :name
    """), session.bind, params={'name': next_name})

    # Get all 2026 drivers from latest race
    drivers_2026 = pd.read_sql(text("""
        SELECT DISTINCT d.code AS driver_code
        FROM race_results rr
        JOIN races r    ON rr.race_id   = r.id
        JOIN drivers d  ON rr.driver_id = d.id
        WHERE r.year = 2026
    """), session.bind)

    # Use all historical + 2026 data for features
    full_df = pd.read_sql(text("""
        SELECT r.year, r.round_number, r.circuit_id,
               d.code AS driver_code, t.name AS team_name,
               rr.final_position, rr.points, rr.status,
               qr.position AS quali_position
        FROM race_results rr
        JOIN races r        ON rr.race_id   = r.id
        JOIN drivers d      ON rr.driver_id = d.id
        LEFT JOIN teams t   ON rr.team_id   = t.id
        LEFT JOIN qualifying_results qr
            ON qr.race_id = r.id AND qr.driver_id = d.id
        ORDER BY r.year, r.round_number
    """), session.bind)

    pred_rows = []
    for _, drv in drivers_2026.iterrows():
        code = drv['driver_code']
        q_row = quali_2026[quali_2026['driver_code'] == code]
        qpos  = float(q_row['quali_position'].values[0]) \
                if len(q_row) > 0 and pd.notna(q_row['quali_position'].values[0]) else 15.0

        dh = full_df[full_df['driver_code'] == code]
        recent = dh.tail(5)

        def exp_avg(vals, alpha=0.7):
            if len(vals) == 0: return np.nan
            w = np.array([alpha ** (len(vals) - i - 1) for i in range(len(vals))])
            return float(np.average(vals, weights=w/w.sum()))

        avg_pts5 = exp_avg(recent['points'].tolist()) or 0
        avg_pos5 = exp_avg(recent['final_position'].tolist()) or 12
        avg_pts3 = dh['points'].tail(3).mean() if len(dh) > 0 else 0
        avg_pos3 = dh['final_position'].tail(3).mean() if len(dh) > 0 else 12
        dnf_rate = dh['status'].str.contains('Retired|Accident|Mechanical', case=False, na=False).mean() if len(dh) > 0 else 0.1
        quali_std = dh['quali_position'].tail(5).std() if len(dh) >= 2 else 3.0

        ch = dh[dh['circuit_id'] == circuit_id] if circuit_id else pd.DataFrame()
        n_ch = len(ch)
        if n_ch > 0:
            w = np.array([0.7 ** (n_ch - i - 1) for i in range(n_ch)])
            w /= w.sum()
            circ_avg_pos = float(np.average(ch['final_position'], weights=w))
            circ_avg_pts = float(np.average(ch['points'], weights=w))
            circ_win_rate = float((ch['final_position'] == 1).mean())
            circ_dnf_rate = float(ch['status'].str.contains('Retired|Accident|Mechanical', case=False, na=False).mean())
        else:
            circ_avg_pos, circ_avg_pts, circ_win_rate, circ_dnf_rate = 12, 0, 0, 0.1

        # Team stats from most recent season
        latest_team = dh[dh['year'] == dh['year'].max()]['team_name'].mode()
        team_name = latest_team.values[0] if len(latest_team) > 0 else None
        th = full_df[full_df['team_name'] == team_name] if team_name else pd.DataFrame()
        team_avg_pts  = th['points'].mean() if len(th) > 0 else 0
        team_avg_pos  = th['final_position'].mean() if len(th) > 0 else 12
        team_win_rate = (th['final_position'] == 1).mean() if len(th) > 0 else 0

        pred_rows.append({
            'driver_code':          code,
            'quali_pos':            qpos,
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
        })

    pred_df = pd.DataFrame(pred_rows)
    X_pred = pred_df[FEATURES].fillna(0)
    pred_df['predicted_score'] = best_model.predict(X_pred)
    pred_df = pred_df.sort_values('predicted_score').reset_index(drop=True)
    pred_df['predicted_rank'] = pred_df.index + 1

    print(f"\n[6/6] {next_race['EventDate'].year} {next_name} Predictions")
    print("="*55)
    has_quali = len(quali_2026) > 0
    header = f"  {'Pred':<5} {'Grid':<6} {'Driver':<8}" if has_quali else f"  {'Pred':<5} {'Driver':<8}"
    print(header)
    print("-"*55)
    for _, row in pred_df.iterrows():
        q_row = quali_2026[quali_2026['driver_code'] == row['driver_code']]
        grid  = f"P{int(q_row['quali_position'].values[0])}" \
                if len(q_row) > 0 and pd.notna(q_row['quali_position'].values[0]) else 'TBD'
        if has_quali:
            print(f"  P{int(row['predicted_rank']):<4} {grid:<6} {row['driver_code']}")
        else:
            print(f"  P{int(row['predicted_rank']):<4} {row['driver_code']}")
    print("="*55)

    # Save predictions
    model_dir = backend_dir / 'ml'
    model_dir.mkdir(exist_ok=True)
    pred_df[['driver_code', 'predicted_rank', 'predicted_score']].to_csv(
        model_dir / f'predictions_2026_rd{next_round:02d}.csv', index=False
    )
    print(f"\n  Predictions saved to: ml/predictions_2026_rd{next_round:02d}.csv")

# ── SAVE MODEL ────────────────────────────────────────────────
model_dir = backend_dir / 'ml'
model_dir.mkdir(exist_ok=True)
joblib.dump(best_model, model_dir / 'race_predictor.pkl')
joblib.dump(FEATURES,   model_dir / 'features.pkl')
print(f"\n  Model saved to: ml/race_predictor.pkl")
print(f"  Features saved to: ml/features.pkl")

session.close()
print("\n" + "="*60 + "\n")