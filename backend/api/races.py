from fastapi import APIRouter, HTTPException, Query
from typing import List
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Race, Circuit, Driver, RaceResult, QualifyingResult, Team

router = APIRouter(prefix="/api/races", tags=["races"])


@router.get("/")
def get_all_races(year: int = None):
    """Get all races, optionally filtered by year"""
    
    print(f"API called with year={year}")
    
    session = get_session()
    
    try:
        query = session.query(Race).join(Circuit)
        
        if year:
            query = query.filter(Race.year == year)
        
        races = query.order_by(Race.year.desc(), Race.round_number).limit(100).all()
        
        print(f"Found {len(races)} races")
        
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
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


@router.get("/{race_id}")
def get_race(race_id:int):
    """ Get a specific RACE BY ID"""
    session = get_session()

    try:
        race = session.query(Race).join(Circuit).filter(Race.id == race_id).first()
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")
        
        return {
            "id": race.id,
            "year": race.year,
            "round_number": race.round_number,
            "race_name": race.race_name,
            "race_date": str(race.race_date) if race.race_date else None,
            "circuit": {
                "id": race.circuit.id,
                "name": race.circuit.name,
                "location": race.circuit.location,
                "country": race.circuit.country,
                "length_km": race.circuit.length_km,
                "laps": race.circuit.laps
            } if race.circuit else None
        }
        
    finally:
        session.close()


@router.get("/{race_id}/results")
def get_race_results(race_id: int):
    session = get_session()

    try:
        results= session.query(RaceResult, Driver)\
            .join(Driver)\
            .filter(RaceResult.race_id == race_id)\
            .order_by(RaceResult.final_position)\
            .all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No results found for this race")
        
        return [
            {
                "driver_name": driver.broadcast_name,
                "driver_code": driver.code,
                "grid_position": result.grid_position,
                "final_position": result.final_position,
                "points": result.points,
                "status": result.status
            }
            for result, driver in results
        ]
        
    finally:
        session.close()

        
@router.get("/{race_id}/qualifying")
def get_qualifying_results(race_id: int):
    session = get_session()
    
    try:
        results = session.query(QualifyingResult, Driver)\
            .join(Driver)\
            .filter(QualifyingResult.race_id == race_id)\
            .order_by(QualifyingResult.position)\
            .all()
        
        if not results:
            raise HTTPException(status_code=404, detail="No qualifying results found")
        
        return [
            {
                "position": result.position,
                "driver_name": driver.broadcast_name,
                "driver_code": driver.code,
                "q1_time": result.q1_time,
                "q2_time": result.q2_time,
                "q3_time": result.q3_time
            }
            for result, driver in results
        ]
        
    finally:
        session.close()


@router.get("/seasons/{year}/summary")
def get_season_summary(year: int):
    session = get_session()
    
    try:
        races = session.query(Race)\
            .filter(Race.year == year)\
            .order_by(Race.round_number)\
            .all()
        
        if not races:
            raise HTTPException(status_code=404, detail=f"No races found for {year}")
        
        return {
            "year": year,
            "total_races": len(races),
            "races": [
                {
                    "round": r.round_number,
                    "name": r.race_name,
                    "date": str(r.race_date) if r.race_date else None
                } 
                for r in races
            ]
        }
        
    finally:
        session.close()
