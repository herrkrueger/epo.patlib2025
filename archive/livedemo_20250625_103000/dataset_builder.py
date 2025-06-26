# REE Dataset Construction using Direct SQL with 2023 PROD focus
import pandas as pd
import numpy as np
from database_connection import test_tip_connection

def build_ree_dataset(db, test_mode=True):
    """
    Build REE patent dataset using keyword and classification intersection
    Uses PROD environment with 2023 focus for reliable data
    test_mode: If True, limits results for faster testing
    """
    
    print(f"Building REE dataset (test_mode: {test_mode})...")
    print("ℹ️  Using 2013-2023 data range for reliable results in PROD environment")
    
    # Step 1: Keyword-based search focusing on 2023 for reliable data
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
    AND a.appln_filing_year = 2013-2023  -- Focus on 2023 for reliable PROD data
    """
    
    if test_mode:
        keyword_query += " LIMIT 500"  # Smaller limit for faster testing
    
    print("Executing keyword-based search for 2013-2023...")
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} patents with REE keywords in 2023")
    
    # Step 2: Classification-based search with verified CPC codes for 2023
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
        cpc.cpc_class_symbol LIKE 'C22B%' OR          -- Broader metallurgy search
        cpc.cpc_class_symbol LIKE 'Y02W30%' OR        -- Waste recycling
        cpc.cpc_class_symbol LIKE 'Y02P10%' OR        -- Clean production
        cpc.cpc_class_symbol LIKE 'C09K11%' OR        -- Luminescent materials
        cpc.cpc_class_symbol LIKE 'H01F1%'            -- Magnets (often use REE)
    )
    AND a.appln_filing_year => 2013  -- Focus on 2013-2023 for reliable PROD data
    """
    
    if test_mode:
        classification_query += " LIMIT 500"
    
    print("Executing classification-based search for 2023...")
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} patents with relevant classifications in 2023")
    
    # Step 3: Create intersection for high-quality dataset
    if not keyword_results.empty and not classification_results.empty:
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
            print(f"✅ High-quality REE dataset: {len(high_quality_ree)} patents (intersection)")
            return high_quality_ree
        else:
            print("ℹ️  No intersection found, using keyword results (still valuable data)")
            return keyword_results
    else:
        print("ℹ️  Using available results - keyword or classification data")
        return keyword_results if not keyword_results.empty else classification_results

def validate_ree_dataset(ree_df):
    """Validate the quality and coverage of REE dataset"""
    print(f"\nDataset Validation Report:")
    print(f"- Total applications: {len(ree_df)}")
    print(f"- Total families: {ree_df['docdb_family_id'].nunique()}")
    print(f"- Date range: {ree_df['appln_filing_year'].min()} - {ree_df['appln_filing_year'].max()}")
    print(f"- Top countries: {ree_df['appln_auth'].value_counts().head(5).to_dict()}")
    
if __name__ == "__main__":
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            validate_ree_dataset(ree_data)
        else:
            print("⚠️  No REE data found - try broader search criteria")