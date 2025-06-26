# 1.1 TIP PATSTAT Database Connection Setup (VERIFIED APPROACH)
from epo.tipdata.patstat import PatstatClient
import pandas as pd
import numpy as np
from datetime import datetime

def test_tip_connection():
    """Test TIP platform connection using verified pattern"""
    print("Libraries imported successfully!")
    print(f"Analysis started at: {datetime.now()}")
    
    # Initialize PATSTAT client for TIP platform - VERIFIED PATTERN
    environment = 'PROD'  # Use PROD for full dataset access as per CLAUDE.md
    print(f"Connecting to PATSTAT {environment} environment...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        print(f"✅ Connected to PATSTAT {environment} environment")
        print(f"Database engine: {db.bind}")
        
        # Simple test query using direct SQL - SAFE APPROACH
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year >= 2020
        LIMIT 5
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Test query successful: Retrieved {len(test_result)} sample records")
        print("Sample data:")
        print(test_result.head())
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def get_database_connection():
    """Get database connection for other components"""
    return test_tip_connection()

if __name__ == "__main__":
    db = test_tip_connection()