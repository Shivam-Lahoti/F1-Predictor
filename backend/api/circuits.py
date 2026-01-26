from fastapi import APIRouter, HTTPException
from typing import List
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, Circuit, Race

router = APIRouter(prefix="/api/circuits", tags=["circuits"])


@router.get("/")
def get_all_circuits():
    """Get all circuits"""
    session = get_session()
    
    try:
        circuits = session.query(Circuit)\
            .order_by(Circuit.name)\
            .all()
        
        return [
            {
                "id": c.id,
                "name": c.name,
                "location": c.location,
                "country": c.country,
                "length_km": c.length_km,
                "laps": c.laps
            }
            for c in circuits
        ]
        
    finally:
        session.close()


@router.get("/{circuit_id}")
def get_circuit(circuit_id: int):
    """Get specific circuit"""
    session = get_session()
    
    try:
        circuit = session.query(Circuit).filter_by(id=circuit_id).first()
        
        if not circuit:
            raise HTTPException(status_code=404, detail="Circuit not found")
        
        # Get races at this circuit
        races = session.query(Race)\
            .filter_by(circuit_id=circuit_id)\
            .order_by(Race.year.desc())\
            .all()
        
        return {
            "id": circuit.id,
            "name": circuit.name,
            "location": circuit.location,
            "country": circuit.country,
            "length_km": circuit.length_km,
            "laps": circuit.laps,
            "total_races": len(races),
            "races": [
                {
                    "year": r.year,
                    "round": r.round_number,
                    "name": r.race_name
                }
                for r in races
            ]
        }
        
    finally:
        session.close()