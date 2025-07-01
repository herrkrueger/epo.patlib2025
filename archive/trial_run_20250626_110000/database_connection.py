"""
Database Connection Module for REE Patent Citation Analysis
EPO Technology Intelligence Platform (TIP) - PATSTAT PROD Environment
"""

from epo.tipdata.patstat import PatstatClient
import pandas as pd
from datetime import datetime
import sys
import traceback

def test_tip_connection():
    """
    Connect to PATSTAT PROD environment with 2010-2023 timeframe
    Returns database connection object for subsequent analysis
    """
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
        print(f"✅ Year range: {test_result['appln_filing_year'].min()}-{test_result['appln_filing_year'].max()}")
        print(f"✅ Countries: {test_result['appln_auth'].unique()}")
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"❌ Error details: {traceback.format_exc()}")
        return None

def validate_patstat_tables(db):
    """
    Validate access to required PATSTAT tables for citation analysis
    """
    required_tables = [
        'tls201_appln',           # Applications
        'tls202_appln_title',     # Titles
        'tls203_appln_abstr',     # Abstracts
        'tls211_pat_publn',       # Publications
        'tls212_citation',        # Citations
        'tls224_appln_cpc',       # CPC Classifications
        'tls207_pers_appln',      # Person-Application links
        'tls206_person',          # Person data
        'tls801_country'          # Country codes
    ]
    
    print("Validating PATSTAT table access...")
    
    accessible_tables = []
    failed_tables = []
    
    for table in required_tables:
        try:
            test_query = f"SELECT COUNT(*) as cnt FROM {table} LIMIT 1"
            result = pd.read_sql(test_query, db.bind)
            accessible_tables.append(table)
            print(f"✅ {table}: accessible")
        except Exception as e:
            failed_tables.append(table)
            print(f"❌ {table}: {str(e)[:100]}")
    
    print(f"\nTable Access Summary:")
    print(f"✅ Accessible: {len(accessible_tables)}/{len(required_tables)}")
    
    if failed_tables:
        print(f"❌ Failed: {failed_tables}")
        return False
    
    return True

def test_citation_table_structure(db):
    """
    Test citation table structure and sample data
    Critical for proper citation analysis implementation
    """
    print("Testing citation table structure...")
    
    try:
        # Test citation table schema
        citation_schema_query = """
        SELECT pat_publn_id, cited_pat_publn_id, cited_appln_id, citn_origin
        FROM tls212_citation
        WHERE pat_publn_id IS NOT NULL 
        AND cited_pat_publn_id IS NOT NULL
        LIMIT 10
        """
        
        citation_sample = pd.read_sql(citation_schema_query, db.bind)
        
        if not citation_sample.empty:
            print(f"✅ Citation table: {len(citation_sample)} sample records")
            print(f"✅ Citation origins: {citation_sample['citn_origin'].unique()}")
            
            # Test publication linkage
            publn_test_query = """
            SELECT pat_publn_id, appln_id, publn_auth, publn_date
            FROM tls211_pat_publn
            WHERE pat_publn_id IN (
                SELECT DISTINCT pat_publn_id FROM tls212_citation LIMIT 5
            )
            """
            
            publn_sample = pd.read_sql(publn_test_query, db.bind)
            print(f"✅ Publication linkage: {len(publn_sample)} records")
            
            return True
        else:
            print("❌ No citation data accessible")
            return False
            
    except Exception as e:
        print(f"❌ Citation table test failed: {e}")
        return False

def get_database_connection():
    """
    Main function to establish and validate database connection
    Returns validated database connection or None
    """
    print("REE PATENT CITATION ANALYSIS - DATABASE CONNECTION")
    print("=" * 60)
    
    # Step 1: Connect to PATSTAT
    db = test_tip_connection()
    if not db:
        return None
    
    # Step 2: Validate table access
    if not validate_patstat_tables(db):
        print("❌ Critical tables not accessible")
        return None
    
    # Step 3: Test citation functionality
    if not test_citation_table_structure(db):
        print("❌ Citation analysis not possible")
        return None
    
    print("\n" + "=" * 60)
    print("✅ DATABASE CONNECTION ESTABLISHED")
    print("✅ All required tables accessible")
    print("✅ Citation analysis ready")
    print("=" * 60)
    
    return db

if __name__ == "__main__":
    db_connection = get_database_connection()
    
    if db_connection:
        print("\n🎯 Database connection successful!")
        print("   Ready for REE patent analysis pipeline")
    else:
        print("\n❌ Database connection failed!")
        print("   Check TIP environment and credentials")
        sys.exit(1)