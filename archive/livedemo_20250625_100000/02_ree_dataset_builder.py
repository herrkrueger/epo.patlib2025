# 2.1 REE Dataset Construction using Direct SQL
import pandas as pd
from datetime import datetime

def build_ree_dataset(db, test_mode=True):
    """
    Build REE patent dataset using keyword and classification intersection
    test_mode: If True, limits results for faster testing
    Uses direct SQL queries to avoid ORM complications
    """
    
    print(f"Building REE dataset (test_mode: {test_mode})...")
    
    # Step 1: Keyword-based search using direct SQL
    keyword_query = """
    SELECT DISTINCT 
        a.appln_id,
        a.docdb_family_id,
        a.appln_filing_year,
        a.appln_auth,
        t.appln_title,
        ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        LOWER(t.appln_title) LIKE '%rare earth%' OR
        LOWER(t.appln_title) LIKE '%neodymium%' OR
        LOWER(t.appln_title) LIKE '%dysprosium%' OR
        LOWER(t.appln_title) LIKE '%lanthanide%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth element%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth metal%' OR
        LOWER(ab.appln_abstract) LIKE '%REE recovery%' OR
        LOWER(ab.appln_abstract) LIKE '%lanthanide%'
    )
    AND a.appln_filing_year >= 2014
    AND a.appln_filing_year <= 2024
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
    
    print("Executing keyword-based search...")
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} patents with REE keywords")
    
    # Step 2: Classification-based search using direct SQL
    classification_query = """
    SELECT DISTINCT 
        a.appln_id,
        a.docdb_family_id,
        a.appln_filing_year,
        a.appln_auth,
        cpc.cpc_class_symbol
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    WHERE (
        cpc.cpc_class_symbol LIKE 'C22B7%' OR
        cpc.cpc_class_symbol LIKE 'C22B19/28%' OR
        cpc.cpc_class_symbol LIKE 'C22B19/30%' OR
        cpc.cpc_class_symbol LIKE 'C22B25/06%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30/52%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30/84%' OR
        cpc.cpc_class_symbol LIKE 'Y02P10/20%'
    )
    AND a.appln_filing_year >= 2014
    AND a.appln_filing_year <= 2024
    """
    
    if test_mode:
        classification_query += " LIMIT 1000"
    
    print("Executing classification-based search...")
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} patents with REE classifications")
    
    # Step 3: Create intersection for high-quality dataset
    common_appln_ids = set(keyword_results['appln_id']).intersection(
        set(classification_results['appln_id'])
    )
    
    if common_appln_ids:
        # Get detailed data for intersection
        intersection_query = f"""
        SELECT DISTINCT 
            a.appln_id,
            a.docdb_family_id,
            a.appln_filing_year,
            a.appln_auth,
            t.appln_title,
            ab.appln_abstract
        FROM tls201_appln a
        LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
        LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
        WHERE a.appln_id IN ({','.join(map(str, common_appln_ids))})
        """
        
        high_quality_ree = pd.read_sql(intersection_query, db.bind)
        print(f"High-quality REE dataset: {len(high_quality_ree)} patents (intersection)")
        return high_quality_ree
    else:
        print("No intersection found, using keyword results")
        return keyword_results

def validate_ree_dataset(ree_df):
    """Validate the quality and coverage of REE dataset"""
    print(f"\nDataset Validation Report:")
    print(f"- Total applications: {len(ree_df)}")
    print(f"- Total families: {ree_df['docdb_family_id'].nunique()}")
    print(f"- Date range: {ree_df['appln_filing_year'].min()} - {ree_df['appln_filing_year'].max()}")
    print(f"- Top countries: {ree_df['appln_auth'].value_counts().head(5).to_dict()}")
    print(f"- Years with most patents: {ree_df['appln_filing_year'].value_counts().head(3).to_dict()}")
    
if __name__ == "__main__":
    import importlib.util
    spec = importlib.util.spec_from_file_location("database_connection", "01_database_connection.py")
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    test_tip_connection = db_module.test_tip_connection
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        validate_ree_dataset(ree_data)