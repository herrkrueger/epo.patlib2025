from epo.tipdata.patstat import PatstatClient
import pandas as pd
from datetime import datetime

def test_tip_connection():
    """Test TIP platform connection with PROD environment"""
    print(f"Analysis started at: {datetime.now()}")
    
    # PROD ENVIRONMENT with 2010-2023 timeframe for comprehensive data
    environment = 'PROD'
    print(f"Connecting to PATSTAT {environment} environment...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        print(f"✅ Connected to PATSTAT {environment}")
        
        # Test query with 2010-2023 timeframe
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year BETWEEN 2010 AND 2023
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Retrieved {len(test_result)} sample records from 2010-2023")
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

if __name__ == "__main__":
    db = test_tip_connection()