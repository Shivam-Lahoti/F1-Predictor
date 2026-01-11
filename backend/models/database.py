
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env from backend folder (parent directory of models/)
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

print(f" Loading .env from: {env_path}")
print(f" .env exists: {env_path.exists()}")
print(f" DATABASE_URL loaded: {os.getenv('DATABASE_URL') is not None}\n")

Base = declarative_base()

class Circuit(Base):
    """F1 Circuit/Track information"""
    __tablename__ = 'circuits'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    circuit_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    location = Column(String(200))
    country = Column(String(100))
    length_km = Column(Float)
    laps = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    races = relationship("Race", back_populates="circuit")


class Driver(Base):
    """F1 Driver information"""
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    driver_number = Column(Integer, unique=True)
    code = Column(String(3))
    first_name = Column(String(100))
    last_name = Column(String(100))
    broadcast_name = Column(String(100))
    nationality = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    qualifying_results = relationship("QualifyingResult", back_populates="driver")
    race_results = relationship("RaceResult", back_populates="driver")
    lap_times = relationship("LapTime", back_populates="driver")


class Team(Base):
    """F1 Team/Constructor information"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_key = Column(String(100), unique=True)
    name = Column(String(200), nullable=False)
    nationality = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race_results = relationship("RaceResult", back_populates="team")


class Race(Base):
    """F1 Race Event"""
    __tablename__ = 'races'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    round_number = Column(Integer, nullable=False)
    race_name = Column(String(200), nullable=False)
    circuit_id = Column(Integer, ForeignKey('circuits.id'))
    race_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    circuit = relationship("Circuit", back_populates="races")
    qualifying_results = relationship("QualifyingResult", back_populates="race")
    race_results = relationship("RaceResult", back_populates="race")
    lap_times = relationship("LapTime", back_populates="race")
    pit_stops = relationship("PitStop", back_populates="race")
    weather = relationship("Weather", back_populates="race")




class QualifyingResult(Base):
    """Qualifying session results"""
    __tablename__ = 'qualifying_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    position = Column(Integer)
    q1_time = Column(Float)
    q2_time = Column(Float)
    q3_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship("Race", back_populates="qualifying_results")
    driver = relationship("Driver", back_populates="qualifying_results")


class RaceResult(Base):
    """Final race results"""
    __tablename__ = 'race_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'))
    grid_position = Column(Integer)
    final_position = Column(Integer)
    points = Column(Float)
    status = Column(String(100))
    fastest_lap = Column(Boolean, default=False)
    fastest_lap_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship("Race", back_populates="race_results")
    driver = relationship("Driver", back_populates="race_results")
    team = relationship("Team", back_populates="race_results")




class LapTime(Base):
    """Lap-by-lap timing data"""
    __tablename__ = 'lap_times'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    lap_number = Column(Integer, nullable=False)
    lap_time = Column(Float)
    sector1_time = Column(Float)
    sector2_time = Column(Float)
    sector3_time = Column(Float)
    compound = Column(String(20))
    tyre_life = Column(Integer)
    is_personal_best = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship("Race", back_populates="lap_times")
    driver = relationship("Driver", back_populates="lap_times")


class PitStop(Base):
    """Pit stop information"""
    __tablename__ = 'pit_stops'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    lap_number = Column(Integer, nullable=False)
    pit_duration = Column(Float)
    compound_before = Column(String(20))
    compound_after = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship("Race", back_populates="pit_stops")
    driver = relationship("Driver")


class Weather(Base):
    """Weather conditions during race"""
    __tablename__ = 'weather'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    race_id = Column(Integer, ForeignKey('races.id'), nullable=False)
    lap_number = Column(Integer)
    air_temp = Column(Float)
    track_temp = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    rainfall = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    race = relationship("Race", back_populates="weather")



def get_database_url():
    """Get database URL from .env file"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError(
            "DATABASE_URL not found in environment variables. "
            "Please create a .env file with DATABASE_URL specified."
        )
    
    return database_url


def create_database_engine():
    """Create SQLAlchemy engine"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=True)
    return engine


def create_all_tables():
    """Create all tables in the database"""
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    print("All tables created successfully!")


def get_session():
    """Get database session"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Creating F1 Database Tables")
    print("="*60 + "\n")
    create_all_tables()