"""
Statistics and analytics API endpoints
"""
from fastapi import APIRouter
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Race, Driver, Circuit, RaceResult, LapTime, PitStop
from sqlalchemy import func, desc, case

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/")
def get_overall_stats():
    """Get overall database statistics"""
    session = get_session()
    
    try:
        stats = {
            "total_races": session.query(Race).count(),
            "total_drivers": session.query(Driver).count(),
            "total_circuits": session.query(Circuit).count(),
            "total_results": session.query(RaceResult).count(),
            "total_lap_times": session.query(LapTime).count(),
            "total_pit_stops": session.query(PitStop).count(),
            "years_covered": session.query(func.count(func.distinct(Race.year))).scalar(),
            "earliest_year": session.query(func.min(Race.year)).scalar(),
            "latest_year": session.query(func.max(Race.year)).scalar(),
            "seasons": [
                y[0] for y in session.query(Race.year)\
                    .distinct()\
                    .order_by(Race.year.desc())\
                    .all()
            ]
        }
        
        return stats
        
    finally:
        session.close()


@router.get("/top-drivers")
def get_top_drivers(limit: int = 10):
    """Get top drivers by total points"""
    session = get_session()
    
    try:
        # Top drivers by points - FIXED
        top_drivers = session.query(
            Driver.code,
            Driver.broadcast_name,
            func.sum(RaceResult.points).label('total_points'),
            func.count(RaceResult.id).label('races'),
            func.sum(case((RaceResult.final_position == 1, 1), else_=0)).label('wins'),
            func.sum(case((RaceResult.final_position <= 3, 1), else_=0)).label('podiums')
        )\
        .join(RaceResult, Driver.id == RaceResult.driver_id)\
        .group_by(Driver.id, Driver.code, Driver.broadcast_name)\
        .order_by(desc('total_points'))\
        .limit(limit)\
        .all()
        
        return [
            {
                "code": d.code,
                "name": d.broadcast_name,
                "total_points": float(d.total_points or 0),
                "races": d.races,
                "wins": d.wins,
                "podiums": d.podiums
            }
            for d in top_drivers
        ]
        
    finally:
        session.close()


@router.get("/year/{year}")
def get_year_stats(year: int):
    """Get statistics for a specific year"""
    session = get_session()
    
    try:
        races = session.query(Race).filter_by(year=year).all()
        
        if not races:
            raise HTTPException(status_code=404, detail=f"No data for {year}")
        
        # Year champion (most points)
        champion = session.query(
            Driver.broadcast_name,
            func.sum(RaceResult.points).label('points')
        )\
        .join(RaceResult, Driver.id == RaceResult.driver_id)\
        .join(Race, RaceResult.race_id == Race.id)\
        .filter(Race.year == year)\
        .group_by(Driver.id, Driver.broadcast_name)\
        .order_by(desc('points'))\
        .first()
        
        return {
            "year": year,
            "total_races": len(races),
            "champion": {
                "name": champion[0] if champion else None,
                "points": float(champion[1]) if champion else 0
            }
        }
        
    finally:
        session.close()


@router.get("/circuits/most-races")
def get_circuits_by_race_count(limit: int = 10):
    """Get circuits with most races held"""
    session = get_session()
    
    try:
        circuits = session.query(
            Circuit.name,
            Circuit.location,
            Circuit.country,
            func.count(Race.id).label('race_count')
        )\
        .join(Race, Circuit.id == Race.circuit_id)\
        .group_by(Circuit.id, Circuit.name, Circuit.location, Circuit.country)\
        .order_by(desc('race_count'))\
        .limit(limit)\
        .all()
        
        return [
            {
                "circuit_name": c.name,
                "location": c.location,
                "country": c.country,
                "races_held": c.race_count
            }
            for c in circuits
        ]
        
    finally:
        session.close()