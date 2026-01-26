from fastapi import APIRouter, HTTPException
from typing import List, Optional
import sys
from pathlib import Path
from sqlalchemy import func, desc, case

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Race, Driver, RaceResult, Circuit
from sqlalchemy import func, desc

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/podium-finishers")
def get_podium_leaders(limit: int = 10):
    """Get drivers with most podium finishes"""
    session = get_session()
    
    try:
        podium_leaders = session.query(
            Driver.code,
            Driver.broadcast_name,
            func.count(RaceResult.id).label('podiums')
        )\
        .join(RaceResult, Driver.id == RaceResult.driver_id)\
        .filter(RaceResult.final_position <= 3)\
        .filter(RaceResult.final_position.isnot(None))\
        .group_by(Driver.id, Driver.code, Driver.broadcast_name)\
        .order_by(desc('podiums'))\
        .limit(limit)\
        .all()
        
        return [
            {
                "code": d.code,
                "name": d.broadcast_name,
                "podiums": d.podiums
            }
            for d in podium_leaders
        ]
        
    finally:
        session.close()


@router.get("/wins-by-circuit/{circuit_id}")
def get_circuit_win_distribution(circuit_id: int):
    """Get win distribution at a specific circuit"""
    session = get_session()
    
    try:
        wins = session.query(
            Driver.broadcast_name,
            func.count(RaceResult.id).label('wins')
        )\
        .join(RaceResult, Driver.id == RaceResult.driver_id)\
        .join(Race, RaceResult.race_id == Race.id)\
        .filter(Race.circuit_id == circuit_id)\
        .filter(RaceResult.final_position == 1)\
        .group_by(Driver.id, Driver.broadcast_name)\
        .order_by(desc('wins'))\
        .all()
        
        return [
            {
                "driver": w[0],
                "wins": w[1]
            }
            for w in wins
        ]
        
    finally:
        session.close()


def compare_seasons(years: str):
    """Compare multiple seasons (comma-separated years)"""
    session = get_session()
    
    try:
        year_list = [int(y.strip()) for y in years.split(',')]
        
        comparison = []
        for year in year_list:
            race_count = session.query(Race).filter_by(year=year).count()
            
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
            
            comparison.append({
                "year": year,
                "races": race_count,
                "champion": champion[0] if champion else None,
                "champion_points": float(champion[1]) if champion else 0
            })
        
        return comparison
        
    finally:
        session.close()


@router.get("/performance-trends/{driver_code}")
def get_driver_performance_trend(driver_code: str):
    """Get year-by-year performance for a driver"""
    session = get_session()
    
    try:
        driver = session.query(Driver).filter_by(code=driver_code.upper()).first()
        
        if not driver:
            raise HTTPException(status_code=404, detail="Driver not found")
        
        yearly_stats = session.query(
            Race.year,
            func.count(RaceResult.id).label('races'),
            func.sum(RaceResult.points).label('points'),
            func.sum(case((RaceResult.final_position == 1, 1), else_=0)).label('wins')  # FIXED
        )\
        .join(RaceResult, Race.id == RaceResult.race_id)\
        .filter(RaceResult.driver_id == driver.id)\
        .group_by(Race.year)\
        .order_by(Race.year)\
        .all()
        
        return {
            "driver": driver.broadcast_name,
            "code": driver.code,
            "performance_by_year": [
                {
                    "year": stat.year,
                    "races": stat.races,
                    "points": float(stat.points or 0),
                    "wins": stat.wins
                }
                for stat in yearly_stats
            ]
        }
        
    finally:
        session.close()