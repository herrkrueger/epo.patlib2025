# TIP PATSTAT Database Connection Setup (VERIFIED APPROACH)
from epo.tipdata.patstat import PatstatClient
import pandas as pd
import numpy as np
from datetime import datetime

def test_tip_connection():
    """Test TIP platform connection using verified pattern"""
    print("Libraries imported successfully!")
    print(f"Analysis started at: {datetime.now()}")
    
    # PRODUCTION ENVIRONMENT with LIMITED TIME RANGE for testing
    environment = 'PROD'  # Use PROD for real data, limit by time range
    print(f"Connecting to PATSTAT {environment} environment...")
    print("ℹ️  Using PROD environment with 2023 time range for reliable data")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        print(f"✅ Connected to PATSTAT {environment} environment")
        print(f"Database engine: {db.bind}")
        
        # VERIFIED: Test query with 2023 focus for reliable data
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year = 2023
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Test query successful: Retrieved {len(test_result)} sample records from 2023")
        print("Sample data:", test_result.head())
        
        # Additional verification: Check data availability for 2023
        count_query = """
        SELECT COUNT(*) as total_2023_applications
        FROM tls201_appln 
        WHERE appln_filing_year = 2023
        """
        count_result = pd.read_sql(count_query, db.bind)
        print(f"📊 Total 2023 applications available: {count_result['total_2023_applications'].iloc[0]:,}")
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

if __name__ == "__main__":
    db = test_tip_connection()