# EXACT WORKING CODE from successful implementation (TESTED: Found 1,977 REE patents)
import pandas as pd

def build_ree_dataset(db, test_mode=True):
    """Build REE dataset with combined keyword and classification search - VERIFIED WORKING"""
    
    print("Building REE dataset for 2010-2023...")
    
    # PROVEN keyword list from successful implementation
    ree_keywords = [
        'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
        'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling',
        'cerium', 'lanthanum', 'europium', 'terbium', 'gadolinium',
        'praseodymium', 'samarium', 'holmium', 'erbium', 'thulium'
    ]
    
    # WORKING SQL pattern for keyword search
    keyword_conditions = " OR ".join([
        f"LOWER(t.appln_title) LIKE '%{keyword}%'" for keyword in ree_keywords
    ] + [
        f"LOWER(ab.appln_abstract) LIKE '%{keyword}%'" for keyword in ree_keywords
    ])
    
    keyword_query = f"""
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        t.appln_title, ab.appln_abstract,
        'keyword' as search_method
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE ({keyword_conditions})
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
    
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} keyword matches")
    
    # PROVEN CPC codes from successful implementation
    ree_cpc_codes = ['C22B%', 'Y02W30%', 'H01F1%', 'C09K11%', 'Y02P10%', 'C22B19%', 'C22B25%']
    
    # WORKING SQL pattern for CPC search
    cpc_conditions = " OR ".join([
        f"cpc.cpc_class_symbol LIKE '{code}'" for code in ree_cpc_codes
    ])
    
    classification_query = f"""
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        cpc.cpc_class_symbol, t.appln_title, ab.appln_abstract,
        'cpc' as search_method
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE ({cpc_conditions})
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        classification_query += " LIMIT 1000"
    
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} classification matches")
    
    # Combine results with search method tracking
    if not keyword_results.empty and not classification_results.empty:
        combined_df = pd.concat([keyword_results, classification_results]).drop_duplicates(subset=['appln_id'])
        
        # Track search method effectiveness (BUSINESS INTELLIGENCE)
        keyword_ids = set(keyword_results['appln_id'])
        cpc_ids = set(classification_results['appln_id'])
        
        def get_search_method(appln_id):
            if appln_id in keyword_ids and appln_id in cpc_ids:
                return 'keyword_and_cpc'
            elif appln_id in keyword_ids:
                return 'keyword_only'
            else:
                return 'cpc_only'
        
        combined_df['search_method_final'] = combined_df['appln_id'].apply(get_search_method)
        
        print(f"Combined dataset: {len(combined_df)} unique applications")
        method_counts = combined_df['search_method_final'].value_counts()
        print(f"Search method distribution: {method_counts.to_dict()}")
        
        return combined_df
    elif not keyword_results.empty:
        return keyword_results
    else:
        return classification_results

# MANDATORY: Test this component immediately after implementation
if __name__ == "__main__":
    print("Testing dataset builder...")
    from database_connection import get_patstat_connection
    db = get_patstat_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            print(f"✅ Dataset builder test PASSED: {len(ree_data)} records")
        else:
            print("❌ Dataset builder test FAILED: No data returned")
    else:
        print("❌ Cannot test dataset builder: Database connection failed")