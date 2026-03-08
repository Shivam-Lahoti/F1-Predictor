from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import (
    get_session, Race, RaceResult, QualifyingResult,
    Driver, Team, Circuit
)
from sqlalchemy import desc

router = APIRouter(prefix="/api/races", tags=["races"])


@router.get("/")
def get_races(year: Optional[int] = None):
    """Get all races, optionally filtered by year"""
    session = get_session()
    try:
        query = session.query(Race).join(Circuit, Race.circuit_id == Circuit.id)

        if year:
            query = query.filter(Race.year == year)

        races = query.order_by(Race.year.desc(), Race.round_number).all()

        return [
            {
                "id": r.id,
                "year": r.year,
                "round": r.round_number,
                "name": r.race_name,
                "circuit": r.circuit.name if r.circuit else None,
                "country": r.circuit.country if r.circuit else None,
                "date": str(r.race_date) if r.race_date else None
            }
            for r in races
        ]
    finally:
        session.close()


@router.get("/years")
def get_available_years():
    """Get list of years with race data"""
    session = get_session()
    try:
        from sqlalchemy import distinct
        years = session.query(distinct(Race.year)).order_by(Race.year.desc()).all()
        return [y[0] for y in years]
    finally:
        session.close()


@router.get("/{race_id}")
def get_race(race_id: int):
    """Get a specific race by ID"""
    session = get_session()
    try:
        race = session.query(Race).filter_by(id=race_id).first()
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")

        return {
            "id": race.id,
            "year": race.year,
            "round": race.round_number,
            "name": race.race_name,
            "circuit": race.circuit.name if race.circuit else None,
            "country": race.circuit.country if race.circuit else None,
            "location": race.circuit.location if race.circuit else None,
            "date": str(race.race_date) if race.race_date else None
        }
    finally:
        session.close()


@router.get("/{race_id}/results")
def get_race_results(race_id: int):
    """Get full results for a specific race"""
    session = get_session()
    try:
        race = session.query(Race).filter_by(id=race_id).first()
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")

        results = session.query(RaceResult)\
            .filter_by(race_id=race_id)\
            .order_by(RaceResult.final_position)\
            .all()

        return {
            "race": {
                "id": race.id,
                "name": race.race_name,
                "year": race.year,
                "round": race.round_number,
                "date": str(race.race_date) if race.race_date else None
            },
            "results": [
                {
                    "position": r.final_position,
                    "grid": r.grid_position,
                    "driver_id": r.driver_id,
                    "driver": r.driver.broadcast_name if r.driver else None,
                    "driver_code": r.driver.code if r.driver else None,
                    "team": r.team.name if r.team else None,
                    "points": float(r.points or 0),
                    "status": r.status
                }
                for r in results
            ]
        }
    finally:
        session.close()


@router.get("/{race_id}/qualifying")
def get_race_qualifying(race_id: int):
    """Get qualifying results for a specific race"""
    session = get_session()
    try:
        race = session.query(Race).filter_by(id=race_id).first()
        if not race:
            raise HTTPException(status_code=404, detail="Race not found")

        quali = session.query(QualifyingResult)\
            .filter_by(race_id=race_id)\
            .order_by(QualifyingResult.position)\
            .all()

        return {
            "race": {
                "id": race.id,
                "name": race.race_name,
                "year": race.year,
                "round": race.round_number
            },
            "qualifying": [
                {
                    "position": q.position,
                    "driver_id": q.driver_id,
                    "driver": q.driver.broadcast_name if q.driver else None,
                    "driver_code": q.driver.code if q.driver else None,
                    "q1_time": q.q1_time,
                    "q2_time": q.q2_time,
                    "q3_time": q.q3_time
                }
                for q in quali
            ]
        }
    finally:
        session.close()