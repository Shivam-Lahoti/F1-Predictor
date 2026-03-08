"""
F1 Race Predictor - ML Model Training
Trains on 2015-2025 data, predicts 2026 Australian GP finishing positions.
Features: qualifying position, driver form, circuit history, team performance.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import text

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

from models.database import get_session

session = get_session()

print("\n" + "="*60)
print("  F1 RACE PREDICTOR - ML TRAINING")
print("="*60)

# ── 1. LOAD TRAINING DATA ─────────────────────────────────────
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
    WHERE r.year BETWEEN 2015 AND 2025
      AND rr.final_position IS NOT NULL
    ORDER BY r.year, r.round_number, rr.final_position
"""), session.bind)

print(f"  Loaded {len(df):,} race results across {df['year'].nunique()} seasons")

# ── 2. FEATURE ENGINEERING ────────────────────────────────────
print("\n[2/6] Engineering features...")

df = df.sort_values(['year', 'round_number', 'final_position'])

# -- Feature 1: qualifying position (fill missing with 20)
df['quali_pos'] = df['quali_position'].fillna(20).astype(float)

# -- Feature 2: driver recent form (avg points last 3 races)
df['driver_avg_pts_last3'] = (
    df.groupby('driver_code')['points']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    .fillna(0)
)

# -- Feature 3: driver recent avg finishing position last 3 races
df['driver_avg_pos_last3'] = (
    df.groupby('driver_code')['final_position']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    .fillna(10)
)

# -- Feature 4: circuit-specific driver win rate
circuit_driver = df.groupby(['circuit_id', 'driver_code']).agg(
    circuit_races=('final_position', 'count'),
    circuit_wins=('final_position', lambda x: (x == 1).sum()),
    circuit_avg_pos=('final_position', 'mean'),
    circuit_avg_pts=('points', 'mean')
).reset_index()
circuit_driver['circuit_win_rate'] = (
    circuit_driver['circuit_wins'] / circuit_driver['circuit_races']
)
df = df.merge(circuit_driver[['circuit_id','driver_code','circuit_win_rate',
                               'circuit_avg_pos','circuit_avg_pts']],
              on=['circuit_id','driver_code'], how='left')
df['circuit_win_rate'] = df['circuit_win_rate'].fillna(0)
df['circuit_avg_pos']  = df['circuit_avg_pos'].fillna(12)
df['circuit_avg_pts']  = df['circuit_avg_pts'].fillna(0)

# -- Feature 5: team season avg points
team_season = df.groupby(['team_id','year'])['points'].mean().reset_index()
team_season.columns = ['team_id','year','team_avg_pts']
df = df.merge(team_season, on=['team_id','year'], how='left')
df['team_avg_pts'] = df['team_avg_pts'].fillna(0)

# -- Feature 6: driver total career races (experience)
driver_exp = df.groupby('driver_code')['id'].count().reset_index()
driver_exp.columns = ['driver_code', 'career_races']
df = df.merge(driver_exp, on='driver_code', how='left')

# -- Feature 7: grid vs quali delta (did they improve/drop in grid?)
df['grid_quali_delta'] = df['grid_position'].fillna(df['quali_pos']) - df['quali_pos']

FEATURES = [
    'quali_pos',
    'driver_avg_pts_last3',
    'driver_avg_pos_last3',
    'circuit_win_rate',
    'circuit_avg_pos',
    'circuit_avg_pts',
    'team_avg_pts',
    'career_races',
    'grid_quali_delta',
]

print(f"  Features: {FEATURES}")

# ── 3. TRAIN MODEL ────────────────────────────────────────────
print("\n[3/6] Training model...")

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import joblib

X = df[FEATURES].fillna(0)
y = df['final_position']

# Train/test split by year (train on 2015-2024, test on 2025)
train_mask = df['year'] <= 2024
test_mask  = df['year'] == 2025

X_train, y_train = X[train_mask], y[train_mask]
X_test,  y_test  = X[test_mask],  y[test_mask]

print(f"  Train: {len(X_train):,} samples (2015-2024)")
print(f"  Test:  {len(X_test):,} samples (2025)")

# Gradient Boosting
gbr = GradientBoostingRegressor(
    n_estimators=200, learning_rate=0.05,
    max_depth=4, min_samples_split=5,
    random_state=42
)
gbr.fit(X_train, y_train)

# Random Forest for comparison
rfr = RandomForestRegressor(
    n_estimators=200, max_depth=6,
    min_samples_split=5, random_state=42
)
rfr.fit(X_train, y_train)

# ── 4. EVALUATE ───────────────────────────────────────────────
print("\n[4/6] Evaluating on 2025 season...")

from sklearn.metrics import mean_absolute_error

gbr_pred = gbr.predict(X_test)
rfr_pred = rfr.predict(X_test)

gbr_mae = mean_absolute_error(y_test, gbr_pred)
rfr_mae = mean_absolute_error(y_test, rfr_pred)

print(f"  GradientBoosting MAE: {gbr_mae:.2f} positions")
print(f"  RandomForest     MAE: {rfr_mae:.2f} positions")

# Use best model
best_model = gbr if gbr_mae <= rfr_mae else rfr
best_name  = "GradientBoosting" if gbr_mae <= rfr_mae else "RandomForest"
print(f"  Best model: {best_name}")

# Feature importance
fi = pd.DataFrame({
    'feature': FEATURES,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)
print(f"\n  Feature Importances:")
for _, row in fi.iterrows():
    bar = '#' * int(row['importance'] * 50)
    print(f"    {row['feature']:<25} {row['importance']:.3f}  {bar}")

# ── 5. PREDICT 2026 AUSTRALIAN GP ─────────────────────────────
print("\n[5/6] Predicting 2026 Australian GP...")

# 2026 qualifying grid
quali_2026 = pd.read_sql(text("""
    SELECT d.code AS driver_code, d.id AS driver_id,
           qr.position AS quali_position,
           qr.q1_time, qr.q2_time, qr.q3_time
    FROM qualifying_results qr
    JOIN races r    ON qr.race_id   = r.id
    JOIN drivers d  ON qr.driver_id = d.id
    WHERE r.year = 2026 AND r.race_name = 'Australian Grand Prix'
    ORDER BY qr.position
"""), session.bind)

# Melbourne circuit_id
melbourne_circuit = pd.read_sql(text("""
    SELECT id FROM circuits
    WHERE name ILIKE '%australian%' OR circuit_key ILIKE '%australian%'
    LIMIT 1
"""), session.bind)
circuit_id = int(melbourne_circuit['id'].iloc[0]) if len(melbourne_circuit) > 0 else None

# Build prediction features for each driver
pred_rows = []
for _, q in quali_2026.iterrows():
    code = q['driver_code']
    qpos = q['quali_position'] if pd.notna(q['quali_position']) else 20

    # Get driver's recent form from 2025
    driver_hist = df[(df['driver_code'] == code) & (df['year'] == 2025)]
    avg_pts_last3 = driver_hist['points'].tail(3).mean() if len(driver_hist) > 0 else 0
    avg_pos_last3 = driver_hist['final_position'].tail(3).mean() if len(driver_hist) > 0 else 12

    # Circuit history at Melbourne
    if circuit_id:
        circ_hist = df[(df['driver_code'] == code) & (df['circuit_id'] == circuit_id)]
        circuit_win_rate = (circ_hist['final_position'] == 1).mean() if len(circ_hist) > 0 else 0
        circuit_avg_pos  = circ_hist['final_position'].mean() if len(circ_hist) > 0 else 12
        circuit_avg_pts  = circ_hist['points'].mean() if len(circ_hist) > 0 else 0
    else:
        circuit_win_rate, circuit_avg_pos, circuit_avg_pts = 0, 12, 0

    # Team avg pts from 2025
    driver_team = df[(df['driver_code'] == code) & (df['year'] == 2025)]
    team_avg_pts = driver_team['team_avg_pts'].mean() if len(driver_team) > 0 else 0

    career_races = len(df[df['driver_code'] == code])

    pred_rows.append({
        'driver_code':          code,
        'quali_pos':            float(qpos),
        'driver_avg_pts_last3': float(avg_pts_last3 or 0),
        'driver_avg_pos_last3': float(avg_pos_last3 or 12),
        'circuit_win_rate':     float(circuit_win_rate),
        'circuit_avg_pos':      float(circuit_avg_pos),
        'circuit_avg_pts':      float(circuit_avg_pts),
        'team_avg_pts':         float(team_avg_pts or 0),
        'career_races':         float(career_races),
        'grid_quali_delta':     0.0,
    })

pred_df = pd.DataFrame(pred_rows)
X_pred  = pred_df[FEATURES].fillna(0)
pred_df['predicted_position'] = best_model.predict(X_pred)
pred_df = pred_df.sort_values('predicted_position').reset_index(drop=True)
pred_df['predicted_rank'] = pred_df.index + 1

# ── 6. PRINT PREDICTIONS ──────────────────────────────────────
print("\n[6/6] 2026 Australian GP Predictions")
print("="*60)
print(f"{'Pred':>5}  {'Grid':>5}  {'Driver':<8}  {'Score':>8}")
print("-"*60)
for _, row in pred_df.iterrows():
    q_row = quali_2026[quali_2026['driver_code'] == row['driver_code']]
    grid  = int(q_row['quali_position'].values[0]) if len(q_row) > 0 and pd.notna(q_row['quali_position'].values[0]) else '?'
    print(f"  P{int(row['predicted_rank']):<3}  P{str(grid):<4}  {row['driver_code']:<8}  {row['predicted_position']:.2f}")
print("="*60)

# ── SAVE MODEL ────────────────────────────────────────────────
model_dir = backend_dir / 'ml'
model_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(best_model, model_dir / 'race_predictor.pkl')
pred_df[['driver_code','predicted_rank','predicted_position']].to_csv(
    model_dir / 'predictions_2026_australia.csv', index=False
)

print(f"\nModel saved to: {model_dir / 'race_predictor.pkl'}")
print(f"Predictions saved to: {model_dir / 'predictions_2026_australia.csv'}")

session.close()