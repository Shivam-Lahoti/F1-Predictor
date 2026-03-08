import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

from models.database import get_session, Driver

# Known nationality map: driver code -> IOC/FastF1 country code
KNOWN_NATIONALITIES = {
    
    'ROS': 'GER',  # Nico Rosberg
    'VET': 'GER',  # Sebastian Vettel
    'MAS': 'MAL',  # Felipe Massa
    'RAI': 'FIN',  # Kimi Raikkonen
    'KVY': 'RUS',  # Daniil Kvyat
    'GRO': 'FRA',  # Romain Grosjean
    'MAL': 'FRA',  # Pastor Maldonado - Venezuelan but FastF1 uses FRA? No - VEN
    'MAL': 'VEN',  # Pastor Maldonado
    'BUT': 'GBR',  # Jenson Button
    'ERI': 'SWE',  # Marcus Ericsson
    'NAS': 'BRA',  # Felipe Nasr
    'SIR': 'RUS',  # Sergey Sirotkin
    'MER': 'ESP',  # Roberto Merhi
    'HAR': 'INA',  # Rio Haryanto
    'GUT': 'MEX',  # Esteban Gutierrez
    'DIR': 'GBR',  # Paul di Resta
    'WEH': 'GER',  # Pascal Wehrlein
    'ERI': 'SWE',  # Marcus Ericsson
    'OKO': 'FIN',  # Valtteri Bottas's replacement
    'KUB': 'POL',  # Robert Kubica
    'GIO': 'ITA',  # Antonio Giovinazzi
    'AIT': 'GBR',  # Jack Aitken
    'FIT': 'BRA',  # Pietro Fittipaldi
    'MSC': 'GER',  # Mick Schumacher
    'MAZ': 'RUS',  # Nikita Mazepin
    'DEV': 'FRA',  # Nyck de Vries
    'LAW': 'NZL',  # Liam Lawson
    'ZHO': 'CHN',  # Zhou Guanyu
    'SAR': 'USA',  # Logan Sargeant
    'COL': 'ARG',  # Franco Colapinto
    'BEA': 'FRA',  # Oliver Bearman
    'ANT': 'BRA',  # Gabriel Bortoleto? No - ANT is likely someone else
    'DOO': 'AUS',  # Jack Doohan
    'HAD': 'FRA',  # Isack Hadjar - French
    'STE': 'GBR',  # Will Stevens
    'RSS': 'USA',  # Alexander Rossi
    'PAL': 'GBR',  # Jolyon Palmer
    'VAN': 'BEL',  # Stoffel Vandoorne
    'LAT': 'CAN',  # Nicholas Latifi
    'BOR': 'BRA',  # Gabriel Bortoleto
    'ANT': 'ITA',  # Andrea Kimi Antonelli - Italian
}

session = get_session()

drivers = session.query(Driver).filter(
    (Driver.nationality == None) |
    (Driver.nationality == '') |
    (Driver.nationality == 'Unknown')
).all()

print(f"\nDrivers missing nationality: {len(drivers)}\n")

fixed = 0
skipped = 0

for d in drivers:
    nat = KNOWN_NATIONALITIES.get(d.code)
    if nat:
        print(f"  {d.code:<6} {d.first_name} {d.last_name:<20} -> {nat}")
        d.nationality = nat
        fixed += 1
    else:
        print(f"  {d.code:<6} {d.first_name} {d.last_name:<20} -> NOT IN MAP (skipped)")
        skipped += 1

session.commit()

# Force-correct any known wrong values regardless of current state
corrections = {
    'HAD': 'FRA',  # was incorrectly set to USA
    'ANT': 'ITA',  # was incorrectly set to BRA
}
for code, nat in corrections.items():
    d = session.query(Driver).filter_by(code=code).first()
    if d and d.nationality != nat:
        print(f"  Correcting {code}: {d.nationality} -> {nat}")
        d.nationality = nat
session.commit()
session.close()

print(f"\nFixed: {fixed}  |  Skipped (not in map): {skipped}")
print("Run data_audit.py to verify.\n")