"""
Test all FastAPI endpoints using correct route signatures.
Run with backend running on http://localhost:8000
"""
import requests

BASE = "http://localhost:8000"

def test(label, url, expected_min=None):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else None
            if expected_min and count is not None and count < expected_min:
                print(f"  WARN  [{r.status_code}] {label} -- only {count} items (expected >={expected_min})")
            else:
                cnt_str = f"({count} items)" if count is not None else ""
                print(f"  OK    [{r.status_code}] {label} {cnt_str}")
            return data
        else:
            print(f"  FAIL  [{r.status_code}] {label} -- {r.text[:120]}")
    except Exception as e:
        print(f"  ERROR        {label} -- {e}")
    return None

SEP = "-" * 60
print(f"\n{SEP}\n  API ENDPOINT TEST\n{SEP}\n")

# -- Health -------------------------------------------------------
print("Health:")
test("GET /",        f"{BASE}/")
test("GET /health",  f"{BASE}/health")

# -- Races --------------------------------------------------------
print("\nRaces:")
test("GET /api/races",              f"{BASE}/api/races",             expected_min=200)
test("GET /api/races?year=2023",    f"{BASE}/api/races?year=2023",   expected_min=20)
test("GET /api/races?year=2024",    f"{BASE}/api/races?year=2024",   expected_min=20)
test("GET /api/races/years",        f"{BASE}/api/races/years",       expected_min=10)

# Pick a race known to have full results (2023 Bahrain = round 1)
races = test("GET /api/races?year=2023", f"{BASE}/api/races?year=2023")
race_id = None
if races and isinstance(races, list):
    # Find a non-sprint race with round > 0
    for r in races:
        if r.get('round', 0) >= 3:
            race_id = r['id']
            break

if race_id:
    test(f"GET /api/races/{race_id}", f"{BASE}/api/races/{race_id}")

    # These return {race: ..., results: [...]} so check nested list length
    r = requests.get(f"{BASE}/api/races/{race_id}/results", timeout=10)
    if r.status_code == 200:
        count = len(r.json().get('results', []))
        status = "OK  " if count >= 15 else "WARN"
        print(f"  {status}  [200] GET /api/races/{race_id}/results ({count} results)")
    else:
        print(f"  FAIL  [{r.status_code}] GET /api/races/{race_id}/results")

    r = requests.get(f"{BASE}/api/races/{race_id}/qualifying", timeout=10)
    if r.status_code == 200:
        count = len(r.json().get('qualifying', []))
        status = "OK  " if count >= 15 else "WARN"
        print(f"  {status}  [200] GET /api/races/{race_id}/qualifying ({count} results)")
    else:
        print(f"  FAIL  [{r.status_code}] GET /api/races/{race_id}/qualifying")

# -- Drivers ------------------------------------------------------
print("\nDrivers:")
test("GET /api/drivers",            f"{BASE}/api/drivers",           expected_min=50)

# Use driver code not ID
test("GET /api/drivers/HAM/seasons",   f"{BASE}/api/drivers/HAM/seasons")
test("GET /api/drivers/VER/seasons",   f"{BASE}/api/drivers/VER/seasons")
test("GET /api/drivers/LEC/seasons",   f"{BASE}/api/drivers/LEC/seasons")

# -- Circuits -----------------------------------------------------
print("\nCircuits:")
circuits = test("GET /api/circuits",  f"{BASE}/api/circuits",        expected_min=40)
if circuits and isinstance(circuits, list):
    cid = circuits[0]['id']
    test(f"GET /api/circuits/{cid}",  f"{BASE}/api/circuits/{cid}")

# -- Stats --------------------------------------------------------
print("\nStats:")
test("GET /api/stats",                       f"{BASE}/api/stats")
test("GET /api/stats/top-drivers",           f"{BASE}/api/stats/top-drivers",         expected_min=5)
test("GET /api/stats/top-drivers?season=2023", f"{BASE}/api/stats/top-drivers?season=2023", expected_min=5)
test("GET /api/stats/year/2023",             f"{BASE}/api/stats/year/2023")
test("GET /api/stats/year/2024",             f"{BASE}/api/stats/year/2024")
test("GET /api/stats/circuits/most-races",   f"{BASE}/api/stats/circuits/most-races",  expected_min=5)

# -- Analytics ----------------------------------------------------
print("\nAnalytics:")
test("GET /api/analytics/podium-finishers",              f"{BASE}/api/analytics/podium-finishers",          expected_min=3)
test("GET /api/analytics/performance-trends/HAM",        f"{BASE}/api/analytics/performance-trends/HAM")
test("GET /api/analytics/performance-trends/VER",        f"{BASE}/api/analytics/performance-trends/VER")
test("GET /api/analytics/wins-by-circuit/1",             f"{BASE}/api/analytics/wins-by-circuit/1")

print(f"\n{SEP}\n  Test complete.\n{SEP}\n")