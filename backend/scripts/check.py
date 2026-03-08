"""
Show 2026 Australian GP qualifying grid from DB.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from sqlalchemy import text
from models.database import get_session

s = get_session()

rows = s.execute(text("""
    SELECT qr.position, d.code, d.first_name, d.last_name,
           qr.q1_time, qr.q2_time, qr.q3_time
    FROM qualifying_results qr
    JOIN races r ON qr.race_id = r.id
    JOIN drivers d ON qr.driver_id = d.id
    WHERE r.year = 2026 AND r.race_name = 'Australian Grand Prix'
    ORDER BY qr.position
""")).fetchall()

print("\n2026 Australian GP - Qualifying Grid")
print("="*55)
print(f"{'Pos':<5} {'Code':<6} {'Driver':<25} {'Best Time'}")
print("-"*55)
for row in rows:
    pos, code, first, last, q1, q2, q3 = row
    best = q3 or q2 or q1
    best_str = f"{best:.3f}s" if best else "N/A"
    pos_str  = str(pos) if pos else '?'
    name     = f"{first or ''} {last or ''}".strip() or code
    print(f"  P{pos_str:<3} {code:<6} {name:<25} {best_str}")
print("="*55)
s.close()