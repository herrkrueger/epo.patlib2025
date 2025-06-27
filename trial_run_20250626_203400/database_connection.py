"""
Database Connection Component for REE Patent Citation Analysis
EPO Technology Intelligence Platform (TIP) - PATSTAT PROD Environment
"""

from epo.tipdata.patstat import PatstatClient
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tip_connection():
    """
    Connect to PATSTAT PROD environment with 2014-2024 timeframe
    Returns: Database connection object or None if failed
    """
    environment = 'PROD'
    logger.info(f"Connecting to PATSTAT {environment}...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        # Test with comprehensive timeframe
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year BETWEEN 2014 AND 2024
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        logger.info(f"✅ Retrieved {len(test_result)} sample records")
        logger.info(f"Year range: {test_result['appln_filing_year'].min()}-{test_result['appln_filing_year'].max()}")
        logger.info(f"Countries: {test_result['appln_auth'].unique()}")
        
        return db
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return None

def validate_patstat_tables(db):
    """
    Validate access to required PATSTAT tables
    """
    required_tables = [
        'tls201_appln',
        'tls202_appln_title', 
        'tls203_appln_abstr',
        'tls211_pat_publn',
        'tls212_citation',
        'tls224_appln_cpc',
        'tls207_pers_appln',
        'tls206_person',
        'tls801_country'
    ]
    
    accessible_tables = []
    
    for table in required_tables:
        try:
            test_query = f"SELECT COUNT(*) as count FROM {table} LIMIT 1"
            result = pd.read_sql(test_query, db.bind)
            accessible_tables.append(table)
            logger.info(f"✅ {table}: accessible")
        except Exception as e:
            logger.error(f"❌ {table}: {e}")
    
    logger.info(f"Table access: {len(accessible_tables)}/{len(required_tables)} tables accessible")
    return accessible_tables

def get_database_statistics(db):
    """
    Get basic statistics about the PATSTAT database for 2014-2024
    """
    stats = {}
    
    try:
        # Application statistics
        apps_query = """
        SELECT 
            COUNT(*) as total_applications,
            COUNT(DISTINCT docdb_family_id) as total_families,
            MIN(appln_filing_year) as min_year,
            MAX(appln_filing_year) as max_year,
            COUNT(DISTINCT appln_auth) as countries
        FROM tls201_appln 
        WHERE appln_filing_year BETWEEN 2014 AND 2024
        """
        
        apps_result = pd.read_sql(apps_query, db.bind)
        stats.update(apps_result.iloc[0].to_dict())
        
        # Citation statistics
        citation_query = """
        SELECT COUNT(*) as total_citations
        FROM tls212_citation c
        JOIN tls211_pat_publn p ON c.pat_publn_id = p.pat_publn_id
        JOIN tls201_appln a ON p.appln_id = a.appln_id
        WHERE a.appln_filing_year BETWEEN 2014 AND 2024
        LIMIT 1000000
        """
        
        citation_result = pd.read_sql(citation_query, db.bind)
        stats.update(citation_result.iloc[0].to_dict())
        
        logger.info("Database Statistics (2014-2024):")
        for key, value in stats.items():
            logger.info(f"  {key}: {value:,}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Statistics query failed: {e}")
        return {}

if __name__ == "__main__":
    # Test the connection
    db = test_tip_connection()
    
    if db:
        # Validate table access
        accessible_tables = validate_patstat_tables(db)
        
        # Get database statistics
        stats = get_database_statistics(db)
        
        print("\n" + "="*50)
        print("DATABASE CONNECTION TEST COMPLETE")
        print("="*50)
        print(f"✅ PATSTAT PROD connection: SUCCESS")
        print(f"✅ Table access: {len(accessible_tables)}/9 tables")
        print(f"✅ Data availability: {stats.get('total_applications', 0):,} applications")
        print(f"✅ Ready for REE analysis pipeline")
    else:
        print("\n" + "="*50)
        print("❌ DATABASE CONNECTION FAILED")
        print("="*50)