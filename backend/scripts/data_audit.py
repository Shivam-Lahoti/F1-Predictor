import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

from sqlalchemy import create_engine, text
from models.database import (Driver, Team, Circuit,Race, RaceResult, LapTime, PitStop, QualifyingResult)
from sqlalchemy.orm import sessionmaker
import os

DATBASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATBASE_URL)
Session = sessionmaker(bind= engine)
session = Session()

SEP = "=" * 70

def section(title):
    print(f"\n{SEP}\n{title}\n{SEP}\n")

def ok(message):
    print(f"ALL GOOD: {message}")

def error(message):
    print(f"ERROR: {message}")

def warning(message):
    print(f"Warning: {message}")

def info(message):
    print(f"INFO: {message}")


section("1. TABLE ROW COUNTS")
tables = {
    "drivers":           Driver,
    "teams":             Team,
    "circuits":          Circuit,
    "races":             Race,
    "qualifying_results": QualifyingResult,
    "race_results":      RaceResult,
    "lap_times":         LapTime,
    "pit_stops":         PitStop,
}
totals = {}
for name, model in tables.items():
    count = session.query(model).count()
    totals[name] = count
    status = ok if count > 0 else error
    status(f"{name:<25} {count:>8,} rows")

# ─────────────────────────────────────────────
# 2. DRIVERS AUDIT
# ─────────────────────────────────────────────
section("2. DRIVERS AUDIT")
drivers = session.query(Driver).all()
info(f"Total drivers: {len(drivers)}")

missing_broadcast = [d for d in drivers if not d.broadcast_name or d.broadcast_name.strip() == '']
missing_nationality = [d for d in drivers if not d.nationality or d.nationality.strip() == '']
missing_code = [d for d in drivers if not d.code or d.code.strip() == '']

if missing_broadcast:
    error(f"Missing broadcast_name: {len(missing_broadcast)}")
    for d in missing_broadcast[:10]:
        print(f"     [{d.code}] {d.first_name} {d.last_name}")
    if len(missing_broadcast) > 10:
        print(f"     ... and {len(missing_broadcast)-10} more")
else:
    ok("All drivers have broadcast_name")

if missing_nationality:
    error(f"Missing nationality: {len(missing_nationality)}")
    for d in missing_nationality[:10]:
        print(f"     [{d.code}] {d.first_name} {d.last_name}")
else:
    ok("All drivers have nationality")

if missing_code:
    error(f"Missing driver code: {len(missing_code)}")
else:
    ok("All drivers have code")

# ─────────────────────────────────────────────
# 3. RACES AUDIT
# ─────────────────────────────────────────────
section("3. RACES AUDIT")
races = session.query(Race).all()
info(f"Total races: {len(races)}")

# Races per year
from collections import Counter
by_year = Counter(r.year for r in races)
for year in sorted(by_year):
    count = by_year[year]
    flag = "All Clear" if count >= 20 else ("Error " if count >= 15 else "Not Found")
    print(f"  {flag} {year}: {count} races")

missing_circuit = [r for r in races if not r.circuit_id]
missing_date    = [r for r in races if not r.race_date]
if missing_circuit:
    error(f"Races missing circuit_id: {len(missing_circuit)}")
else:
    ok("All races have circuit_id")
if missing_date:
    error(f"Races missing date: {len(missing_date)}")
else:
    ok("All races have date")

# ─────────────────────────────────────────────
# 4. RACE RESULTS AUDIT
# ─────────────────────────────────────────────
section("4. RACE RESULTS AUDIT")
results = session.query(RaceResult).all()
info(f"Total race results: {len(results):,}")

# Avg results per race
avg = len(results) / len(races) if races else 0
if avg >= 18:
    ok(f"Avg results per race: {avg:.1f}")
elif avg >= 15:
    warning(f"Avg results per race: {avg:.1f} (some races may be incomplete)")
else:
    error(f"Avg results per race: {avg:.1f} (too low - data may be missing)")

# Missing points
missing_points = [r for r in results if r.points is None]
missing_pos    = [r for r in results if r.final_position is None and r.status not in ('DNF','DNS','DSQ')]
if missing_points:
    warning(f"Results missing points field: {len(missing_points):,}")
else:
    ok("All results have points field")
if missing_pos:
    warning(f"Results missing position (non-DNF): {len(missing_pos):,}")
else:
    ok("All finishers have position")

# DNF rate
dnf_count = sum(1 for r in results if r.status and 'DNF' in r.status.upper())
dnf_rate  = dnf_count / len(results) * 100 if results else 0
info(f"DNF rate: {dnf_rate:.1f}% ({dnf_count:,} DNFs)")

# ─────────────────────────────────────────────
# 5. QUALIFYING RESULTS AUDIT
# ─────────────────────────────────────────────
section("5. QUALIFYING RESULTS AUDIT")
qual = session.query(QualifyingResult).all()
info(f"Total qualifying results: {len(qual):,}")

avg_qual = len(qual) / len(races) if races else 0
if avg_qual >= 18:
    ok(f"Avg qualifying results per race: {avg_qual:.1f}")
else:
    warning(f"Avg qualifying results per race: {avg_qual:.1f} (may be incomplete)")

missing_q1 = sum(1 for q in qual if not q.q1_time)
missing_q3 = sum(1 for q in qual if not q.q3_time)
info(f"Missing Q1 time: {missing_q1:,} (expected for eliminated drivers)")
info(f"Missing Q3 time: {missing_q3:,} (expected — only top 10 do Q3)")

# ─────────────────────────────────────────────
# 6. CIRCUITS AUDIT
# ─────────────────────────────────────────────
section("6. CIRCUITS AUDIT")
circuits = session.query(Circuit).all()
info(f"Total circuits: {len(circuits)}")

missing_country  = [c for c in circuits if not c.country]
missing_location = [c for c in circuits if not c.location]
if missing_country:
    error(f"Circuits missing country: {len(missing_country)}")
    for c in missing_country:
        print(f"     {c.name}")
else:
    ok("All circuits have country")
if missing_location:
    warning(f"Circuits missing location: {len(missing_location)}")
else:
    ok("All circuits have location")

# ─────────────────────────────────────────────
# 7. TEAMS AUDIT
# ─────────────────────────────────────────────
section("7. TEAMS AUDIT")
teams = session.query(Team).all()
info(f"Total teams: {len(teams)}")
missing_nationality_t = [t for t in teams if not t.nationality]
if missing_nationality_t:
    warning(f"Teams missing nationality: {len(missing_nationality_t)}")
    for t in missing_nationality_t[:5]:
        print(f"     {t.name}")
else:
    ok("All teams have nationality")

# ─────────────────────────────────────────────
# 8. CHAMPIONSHIP POINTS SPOT CHECK
# ─────────────────────────────────────────────
section("8. CHAMPIONSHIP POINTS SPOT CHECK (2023)")
try:
    rows = session.execute(text("""
        SELECT d.first_name || ' ' || d.last_name AS driver,
               SUM(rr.points) AS total_points
        FROM race_results rr
        JOIN drivers d ON rr.driver_id = d.id
        JOIN races r ON rr.race_id = r.id
        WHERE r.year = 2023
        GROUP BY driver
        ORDER BY total_points DESC
        LIMIT 10
    """)).fetchall()

    # Official 2023 top 5 for comparison
    official = {
        "Max Verstappen": 575, "Sergio Perez": 285,
        "Fernando Alonso": 206, "Lewis Hamilton": 234,
        "Carlos Sainz": 200
    }

    info("Your DB  vs  Official 2023 standings:")
    print(f"  {'Driver':<25} {'DB Points':>10}  {'Official':>10}  {'Match?':>8}")
    print(f"  {'-'*55}")
    for row in rows:
        name   = row[0]
        db_pts = int(row[1]) if row[1] else 0
        off    = official.get(name, "N/A")
        match  = "All Good" if off == "N/A" else ("All Good" if abs(db_pts - off) <= 2 else "Not Found")
        print(f"  {name:<25} {db_pts:>10}  {str(off):>10}  {match:>8}")
except Exception as e:
    error(f"Could not run points check: {e}")

# ─────────────────────────────────────────────
# 9. LAP TIMES AUDIT
# ─────────────────────────────────────────────
section("9. LAP TIMES AUDIT")
lap_count = totals.get("lap_times", 0)
if lap_count > 50000:
    ok(f"Lap times: {lap_count:,} rows (good coverage)")
elif lap_count > 10000:
    warning(f"Lap times: {lap_count:,} rows (partial coverage)")
else:
    error(f"Lap times: {lap_count:,} rows (very low — may affect ML features)")

# ─────────────────────────────────────────────
# 10. SUMMARY SCORECARD
# ─────────────────────────────────────────────
section("10. AUDIT SUMMARY SCORECARD")
issues = []
if missing_broadcast:     issues.append(f"{len(missing_broadcast)} drivers missing broadcast_name")
if missing_nationality:   issues.append(f"{len(missing_nationality)} drivers missing nationality")
if missing_country:       issues.append(f"{len(missing_country)} circuits missing country")
if avg < 15:              issues.append(f"Low avg race results per race ({avg:.1f})")
if totals.get("lap_times",0) < 10000: issues.append("Very few lap time rows")

if not issues:
    ok("Database looks clean — ready for ML!")
else:
    warning(f"Found {len(issues)} issue(s) to fix before ML:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")

print(f"\n{SEP}")
print("  Audit complete.")
print(SEP)
session.close()
