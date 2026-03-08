
import sys
from pathlib import Path
import fastf1
import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
fastf1.Cache.enable_cache(str(backend_dir / 'fastf1_cache'))

schedule = fastf1.get_event_schedule(2025)
today = pd.Timestamp.now()

past  = schedule[(schedule['EventDate'] < today) & (schedule['RoundNumber'] > 0)]
future = schedule[(schedule['EventDate'] >= today) & (schedule['RoundNumber'] > 0)]

print(f"\n2025 races that have HAPPENED ({len(past)}):")
for _, row in past.iterrows():
    print(f"  Rd{row['RoundNumber']:>2}  {str(row['EventDate'].date()):<12}  {row['EventName']}")

print(f"\n2025 races NOT YET HAPPENED ({len(future)}):")
for _, row in future.iterrows():
    print(f"  Rd{row['RoundNumber']:>2}  {str(row['EventDate'].date()):<12}  {row['EventName']}")