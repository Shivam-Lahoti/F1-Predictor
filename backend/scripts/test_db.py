import sys
from pathlib import Path

# Add parent directory to path so we can import models
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from models.database import get_session, create_database_engine
from sqlalchemy import inspect, text

def test_connection():
    """Test if we can connect to database"""
    try:
        engine = create_database_engine()
        
        print("\n" + "="*60)
        print("PostgreSQL Connection Test")
        print("="*60)
        
        print(f"Database connection successful!")
        print(f"   Database: {engine.url.database}")
        print(f"   Host: {engine.url.host}")
        print(f"   Port: {engine.url.port}")
        print(f"   User: {engine.url.username}")
        
        # Get table names
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"Tables in database ({len(tables)} total):")
        for i, table in enumerate(tables, 1):
            columns = inspector.get_columns(table)
            print(f"   {i}. {table:25} ({len(columns)} columns)")
        
        # Test a simple query
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f" PostgreSQL Version:")
            print(f"   {version.split(',')[0]}")
        
        # Check if tables are empty or have data
        print(f"Table Row Counts:")
        with engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.fetchone()[0]
                print(f"   {table:25} {count:>6} rows")
        
        print("\n" + "="*60)
        print("All database tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f" Database connection failed: {e}\n")
        raise

if __name__ == "__main__":
    test_connection()