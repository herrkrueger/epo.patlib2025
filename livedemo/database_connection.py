from epo.tipdata.patstat import PatstatClient
import pandas as pd

def test_tip_connection():
    """Connect to PROD environment with 2010-2023 timeframe"""
    environment = 'PROD'
    print(f"Connecting to PATSTAT {environment} environment...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        # Test with comprehensive timeframe
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year BETWEEN 2010 AND 2023
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Retrieved {len(test_result)} sample records")
        print(f"   Year range: {test_result['appln_filing_year'].min()}-{test_result['appln_filing_year'].max()}")
        print(f"   Countries: {test_result['appln_auth'].unique()}")
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def get_patstat_connection():
    """Get production PATSTAT database connection"""
    return test_tip_connection()

if __name__ == "__main__":
    print("Testing PATSTAT TIP Connection...")
    db = test_tip_connection()
    if db:
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")