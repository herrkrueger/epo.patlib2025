import pandas as pd

def build_ree_dataset(db, test_mode=True):
    """Build REE dataset for 2010-2023 timeframe for comprehensive analysis"""
    
    print("Building REE dataset for 2010-2023...")
    
    # Keyword-based search
    keyword_query = """
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        t.appln_title, ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        LOWER(t.appln_title) LIKE '%rare earth%' OR
        LOWER(t.appln_title) LIKE '%neodymium%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth element%' OR
        LOWER(ab.appln_abstract) LIKE '%REE recovery%'
    )
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        keyword_query += " LIMIT 500"
    
    try:
        keyword_results = pd.read_sql(keyword_query, db.bind)
        print(f"Found {len(keyword_results)} keyword matches")
    except Exception as e:
        print(f"⚠️ Keyword search failed: {e}")
        keyword_results = pd.DataFrame()
    
    # Classification-based search with broader patterns
    classification_query = """
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        cpc.cpc_class_symbol
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    WHERE (
        cpc.cpc_class_symbol LIKE 'C22B%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30%' OR
        cpc.cpc_class_symbol LIKE 'H01F1%'
    )
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        classification_query += " LIMIT 500"
    
    try:
        classification_results = pd.read_sql(classification_query, db.bind)
        print(f"Found {len(classification_results)} classification matches")
    except Exception as e:
        print(f"⚠️ Classification search failed: {e}")
        classification_results = pd.DataFrame()
    
    # Return best available dataset
    if not keyword_results.empty:
        return keyword_results
    elif not classification_results.empty:
        return classification_results
    else:
        print("⚠️ No REE data found - trying fallback query...")
        # Fallback to basic metallurgy patents
        fallback_query = """
        SELECT DISTINCT 
            a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth
        FROM tls201_appln a
        JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
        WHERE cpc.cpc_class_symbol LIKE 'C22B%'
        AND a.appln_filing_year BETWEEN 2010 AND 2023
        LIMIT 100
        """
        try:
            fallback_results = pd.read_sql(fallback_query, db.bind)
            print(f"Found {len(fallback_results)} fallback metallurgy patents")
            return fallback_results
        except Exception as e:
            print(f"❌ All searches failed: {e}")
            return pd.DataFrame()

def validate_ree_dataset(ree_df):
    """Validate dataset quality"""
    if ree_df.empty:
        print("❌ Empty dataset")
        return False
    
    print(f"Dataset: {len(ree_df)} applications, {ree_df['docdb_family_id'].nunique()} families")
    print(f"Top countries: {ree_df['appln_auth'].value_counts().head(3).to_dict()}")
    return True

if __name__ == "__main__":
    from database_connection import test_tip_connection
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        validate_ree_dataset(ree_data)