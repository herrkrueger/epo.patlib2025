import pandas as pd
from database_connection import get_patstat_connection

def build_ree_dataset(db, test_mode=True):
    """Build REE dataset with combined keyword and classification search"""
    
    print("Building REE dataset for 2010-2023...")
    
    # REE Keywords from CLAUDE.md specification
    ree_keywords = [
        'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
        'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling'
    ]
    
    # Keyword-based search
    keyword_conditions = " OR ".join([
        f"LOWER(t.appln_title) LIKE '%{keyword}%'" for keyword in ree_keywords
    ] + [
        f"LOWER(ab.appln_abstract) LIKE '%{keyword}%'" for keyword in ree_keywords
    ])
    
    keyword_query = f"""
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        t.appln_title, ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        {keyword_conditions}
    )
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
    
    print("🔍 Executing keyword search...")
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} keyword matches")
    
    # CPC Classification-based search (from CLAUDE.md specification)
    ree_cpc_codes = [
        'C22B%',      # Metallurgy & Metal Extraction
        'Y02W30%',    # Waste Management & Recycling  
        'H01F1%',     # Magnets & Magnetic Materials
        'C09K11%',    # Luminescent Materials
        'Y02P10%'     # Clean Production Technologies
    ]
    
    cpc_conditions = " OR ".join([
        f"cpc.cpc_class_symbol LIKE '{code}'" for code in ree_cpc_codes
    ])
    
    classification_query = f"""
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        cpc.cpc_class_symbol,
        t.appln_title, ab.appln_abstract
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        {cpc_conditions}
    )
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    """
    
    if test_mode:
        classification_query += " LIMIT 1000"
    
    print("🔍 Executing CPC classification search...")
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} classification matches")
    
    # Combine results
    if not keyword_results.empty and not classification_results.empty:
        combined_df = pd.concat([keyword_results, classification_results]).drop_duplicates(subset=['appln_id'])
        print(f"✅ Combined dataset: {len(combined_df)} unique applications")
        
        # Add search method tracking
        keyword_ids = set(keyword_results['appln_id'])
        cpc_ids = set(classification_results['appln_id'])
        
        def get_search_method(appln_id):
            if appln_id in keyword_ids and appln_id in cpc_ids:
                return 'keyword_and_cpc'
            elif appln_id in keyword_ids:
                return 'keyword_only'
            else:
                return 'cpc_only'
        
        combined_df['search_method'] = combined_df['appln_id'].apply(get_search_method)
        
        print(f"Search method distribution:")
        print(combined_df['search_method'].value_counts())
        
        return combined_df
    elif not keyword_results.empty:
        keyword_results['search_method'] = 'keyword_only'
        return keyword_results
    elif not classification_results.empty:
        classification_results['search_method'] = 'cpc_only'
        return classification_results
    else:
        print("❌ No REE patents found")
        return pd.DataFrame()

def get_ree_dataset(test_mode=True):
    """Main function to get REE dataset"""
    db = get_patstat_connection()
    if not db:
        return pd.DataFrame()
    
    return build_ree_dataset(db, test_mode)

if __name__ == "__main__":
    print("Testing REE Dataset Builder...")
    ree_data = get_ree_dataset(test_mode=True)
    
    if not ree_data.empty:
        print(f"\n✅ Dataset Summary:")
        print(f"   Total Applications: {len(ree_data):,}")
        print(f"   Unique Families: {ree_data['docdb_family_id'].nunique():,}")
        print(f"   Year Range: {ree_data['appln_filing_year'].min()}-{ree_data['appln_filing_year'].max()}")
        print(f"   Countries: {ree_data['appln_auth'].nunique()}")
        print(f"   Top Countries: {ree_data['appln_auth'].value_counts().head(3).to_dict()}")
    else:
        print("❌ No data retrieved")