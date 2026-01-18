from fastapi import APIRouter
from typing import List
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Race, Circuit

router = APIRouter(prefix="/api/races", tags=["races"])


@router.get("/")
def get_all_races(year: int = None):
    """Get all races, optionally filtered by year"""
    
    print(f"🔍 API called with year={year}")
    
    session = get_session()
    
    try:
        query = session.query(Race).join(Circuit)
        
        if year:
            query = query.filter(Race.year == year)
        
        races = query.order_by(Race.year.desc(), Race.round_number).limit(100).all()
        
        print(f"✅ Found {len(races)} races")
        
        # Return simple dict instead of Pydantic model
        result = []
        for race in races:
            result.append({
                "id": race.id,
                "year": race.year,
                "round_number": race.round_number,
                "race_name": race.race_name,
                "race_date": str(race.race_date) if race.race_date else None,
                "circuit": {
                    "id": race.circuit.id if race.circuit else 0,
                    "name": race.circuit.name if race.circuit else "Unknown",
                    "location": race.circuit.location if race.circuit else "Unknown",
                    "country": race.circuit.country if race.circuit else "Unknown"
                }
            })
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()