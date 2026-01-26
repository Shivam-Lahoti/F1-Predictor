import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Driver

session = get_session()

print("\n" + "="*70)
print("🔧 FIXING DRIVER BROADCAST NAMES")
print("="*70 + "\n")

drivers = session.query(Driver).all()
fixed = 0

for driver in drivers:
    # If broadcast_name is blank
    if not driver.broadcast_name or driver.broadcast_name.strip() == '':
        
        if driver.first_name and driver.last_name:
            # Format: "L. HAMILTON" style
            driver.broadcast_name = f"{driver.first_name[0]}. {driver.last_name}".upper()
            print(f"✅ Fixed {driver.code}: {driver.broadcast_name}")
            fixed += 1
        
        elif driver.last_name:
            driver.broadcast_name = driver.last_name.upper()
            print(f"✅ Fixed {driver.code}: {driver.broadcast_name} (last name only)")
            fixed += 1
        
        else:
            driver.broadcast_name = driver.code
            print(f"⚠️  Using code for {driver.code}")
            fixed += 1

session.commit()

print(f"\n{'='*70}")
print(f"✅ Fixed {fixed} driver names!")
print(f"{'='*70}\n")

session.close()