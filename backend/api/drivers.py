from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path
from sqlalchemy import func, desc, case

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Driver, RaceResult, Race
from sqlalchemy import func, desc

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


@router.get("/")
def get_all_drivers(sort_by: str = "name"):
    """Get all drivers sorted alphabetically"""
    session = get_session()
    
    try:
        # Get drivers with their stats
        drivers = session.query(
            Driver.id,
            Driver.code,
            Driver.broadcast_name,
            Driver.nationality,
            Driver.driver_number,
            func.count(RaceResult.id).label('races'),
            func.sum(RaceResult.points).label('total_points'),
            func.sum(case((RaceResult.final_position == 1, 1), else_=0)).label('wins'),
            func.sum(case((RaceResult.final_position <= 3, 1), else_=0)).label('podiums')
        )\
        .outerjoin(RaceResult, Driver.id == RaceResult.driver_id)\
        .group_by(Driver.id, Driver.code, Driver.broadcast_name, Driver.nationality, Driver.driver_number)\
        .order_by(Driver.broadcast_name)\
        .all()
        
        return [
            {
                "id": d.id,
                "code": d.code,
                "name": d.broadcast_name or d.code,
                "nationality": d.nationality,
                "number": d.driver_number,
                "races": d.races or 0,
                "total_points": float(d.total_points or 0),
                "wins": d.wins or 0,
                "podiums": d.podiums or 0
            }
            for d in drivers
            if d.broadcast_name and d.broadcast_name.strip()  # Filter out blanks
        ]
        
    finally:
        session.close()


@router.get("/{driver_code}/seasons")
def get_driver_seasons(driver_code: str):
    """Get season-by-season performance for a driver"""
    session = get_session()
    
    try:
        driver = session.query(Driver).filter_by(code=driver_code.upper()).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        # Get performance by season - FIXED
        seasons = session.query(
            Race.year,
            func.count(RaceResult.id).label('races'),
            func.sum(RaceResult.points).label('points'),
            func.sum(case((RaceResult.final_position == 1, 1), else_=0)).label('wins'),  # Fixed!
            func.sum(case((RaceResult.final_position <= 3, 1), else_=0)).label('podiums'),  # Fixed!
            func.avg(RaceResult.final_position).label('avg_position')
        )\
        .join(RaceResult, Race.id == RaceResult.race_id)\
        .filter(RaceResult.driver_id == driver.id)\
        .filter(RaceResult.final_position.isnot(None))\
        .group_by(Race.year)\
        .order_by(Race.year.desc())\
        .all()
        
        return {
            "driver": {
                "code": driver.code,
                "name": driver.broadcast_name or driver.code,
                "nationality": driver.nationality or 'Unknown',
                "number": driver.driver_number
            },
            "seasons": [
                {
                    "year": s.year,
                    "races": s.races,
                    "points": float(s.points or 0),
                    "wins": s.wins or 0,
                    "podiums": s.podiums or 0,
                    "avg_position": round(float(s.avg_position or 0), 2)
                }
                for s in seasons
            ],
            "career_totals": {
                "total_races": sum(s.races for s in seasons),
                "total_points": sum(float(s.points or 0) for s in seasons),
                "total_wins": sum(s.wins or 0 for s in seasons),
                "total_podiums": sum(s.podiums or 0 for s in seasons)
            }
        }
        
    finally:
        session.close()