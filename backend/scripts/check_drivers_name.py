import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Driver

session = get_session()

print("\n" + "="*70)
print("🔍 DRIVER NAME AUDIT")
print("="*70)

# Get all drivers
drivers = session.query(Driver).order_by(Driver.code).all()

blank_broadcast = []
blank_first = []
blank_last = []
completely_blank = []

for driver in drivers:
    # Check broadcast name
    if not driver.broadcast_name or driver.broadcast_name.strip() == '':
        blank_broadcast.append(driver)
        
        # Check if completely blank
        if (not driver.first_name or driver.first_name.strip() == '') and \
           (not driver.last_name or driver.last_name.strip() == ''):
            completely_blank.append(driver)
    
    # Check first name
    if not driver.first_name or driver.first_name.strip() == '':
        blank_first.append(driver)
    
    # Check last name
    if not driver.last_name or driver.last_name.strip() == '':
        blank_last.append(driver)

print(f"\nTotal Drivers: {len(drivers)}")
print(f"\n❌ Missing broadcast_name: {len(blank_broadcast)}")
if blank_broadcast:
    for d in blank_broadcast[:10]:  # Show first 10
        print(f"   - {d.code}: broadcast='{d.broadcast_name}', first='{d.first_name}', last='{d.last_name}'")

print(f"\n❌ Missing first_name: {len(blank_first)}")
print(f"❌ Missing last_name: {len(blank_last)}")
print(f"\n🚨 COMPLETELY BLANK: {len(completely_blank)}")

if completely_blank:
    print("\nDrivers with NO name data:")
    for d in completely_blank:
        print(f"   - Code: {d.code}, Number: {d.driver_number}")

print("\n" + "="*70 + "\n")

session.close()