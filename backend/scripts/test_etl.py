import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from scripts.etl_historical import load_race_weekend, get_session

def test_single_race():
    """Test with 2024 Monaco GP"""
    print("\n🧪 Testing ETL with 2024 Monaco Grand Prix\n")
    
    session_obj = get_session()
    
    try:
        load_race_weekend(2024, 'Monaco Grand Prix', session_obj)
        print("\n✅ Test successful!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        session_obj.close()

if __name__ == "__main__":
    test_single_race()
