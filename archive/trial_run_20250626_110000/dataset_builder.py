"""
Dataset Builder Module for REE Patent Citation Analysis
Combined keyword and CPC classification search strategies
"""

import pandas as pd
from datetime import datetime
import traceback

def build_ree_dataset(db, test_mode=True):
    """
    Build REE dataset with combined keyword and classification search
    
    Args:
        db: Database connection from database_connection module
        test_mode: If True, limits results for faster testing
    
    Returns:
        DataFrame with REE patent applications
    """
    
    print("Building REE dataset for 2010-2023...")
    print("=" * 50)
    
    # REE Keywords for title/abstract search
    ree_keywords = [
        'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
        'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling',
        'cerium', 'lanthanum', 'praseodymium', 'samarium', 'europium',
        'gadolinium', 'terbium', 'holmium', 'erbium', 'thulium', 'ytterbium', 'lutetium'
    ]
    
    # CPC Classification codes for REE technologies
    ree_cpc_codes = [
        'C22B%',      # Metallurgy & Metal Extraction
        'Y02W30%',    # Waste Management & Recycling  
        'H01F1%',     # Magnets & Magnetic Materials
        'C09K11%',    # Luminescent Materials
        'Y02P10%'     # Clean Production Technologies
    ]
    
    keyword_results = search_by_keywords(db, ree_keywords, test_mode)
    classification_results = search_by_classification(db, ree_cpc_codes, test_mode)
    
    # Combine and deduplicate results
    combined_df = combine_search_results(keyword_results, classification_results)
    
    print(f"\n✅ FINAL DATASET: {len(combined_df)} unique applications")
    print(f"✅ Year range: {combined_df['appln_filing_year'].min()}-{combined_df['appln_filing_year'].max()}")
    print(f"✅ Countries: {combined_df['appln_auth'].nunique()}")
    print(f"✅ Families: {combined_df['docdb_family_id'].nunique()}")
    
    return combined_df

def search_by_keywords(db, keywords, test_mode=True):
    """
    Search patents by keywords in title and abstract
    """
    print(f"🔍 Keyword search: {len(keywords)} terms")
    
    # Build keyword conditions for SQL
    keyword_conditions = []
    for keyword in keywords:
        keyword_conditions.append(f"LOWER(t.appln_title) LIKE '%{keyword.lower()}%'")
        keyword_conditions.append(f"LOWER(ab.appln_abstract) LIKE '%{keyword.lower()}%'")
    
    keyword_where = " OR ".join(keyword_conditions)
    
    keyword_query = f"""
    SELECT DISTINCT 
        a.appln_id, 
        a.docdb_family_id, 
        a.appln_filing_year, 
        a.appln_auth,
        t.appln_title, 
        ab.appln_abstract,
        'keyword' as search_type
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE ({keyword_where})
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    AND a.appln_auth IS NOT NULL
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
    
    try:
        keyword_results = pd.read_sql(keyword_query, db.bind)
        print(f"✅ Keyword matches: {len(keyword_results)}")
        
        if not keyword_results.empty:
            # Show keyword hit distribution
            year_dist = keyword_results['appln_filing_year'].value_counts().sort_index()
            print(f"   Year distribution: {year_dist.head(3).to_dict()}...")
            
        return keyword_results
        
    except Exception as e:
        print(f"❌ Keyword search failed: {e}")
        return pd.DataFrame()

def search_by_classification(db, cpc_codes, test_mode=True):
    """
    Search patents by CPC classification codes
    """
    print(f"🔍 Classification search: {len(cpc_codes)} CPC patterns")
    
    # Build CPC conditions for SQL
    cpc_conditions = []
    for cpc_code in cpc_codes:
        cpc_conditions.append(f"cpc.cpc_class_symbol LIKE '{cpc_code}'")
    
    cpc_where = " OR ".join(cpc_conditions)
    
    classification_query = f"""
    SELECT DISTINCT 
        a.appln_id, 
        a.docdb_family_id, 
        a.appln_filing_year, 
        a.appln_auth,
        cpc.cpc_class_symbol,
        'classification' as search_type
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    WHERE ({cpc_where})
    AND a.appln_filing_year BETWEEN 2010 AND 2023
    AND a.appln_auth IS NOT NULL
    """
    
    if test_mode:
        classification_query += " LIMIT 1000"
    
    try:
        classification_results = pd.read_sql(classification_query, db.bind)
        print(f"✅ Classification matches: {len(classification_results)}")
        
        if not classification_results.empty:
            # Show CPC hit distribution
            cpc_dist = classification_results['cpc_class_symbol'].str[:6].value_counts()
            print(f"   Top CPC classes: {cpc_dist.head(3).to_dict()}")
            
        return classification_results
        
    except Exception as e:
        print(f"❌ Classification search failed: {e}")
        return pd.DataFrame()

def combine_search_results(keyword_results, classification_results):
    """
    Combine keyword and classification search results with deduplication
    """
    print("🔗 Combining search results...")
    
    if keyword_results.empty and classification_results.empty:
        print("❌ No results from either search method")
        return pd.DataFrame()
    
    elif keyword_results.empty:
        print("⚠️  Only classification results available")
        return classification_results
    
    elif classification_results.empty:
        print("⚠️  Only keyword results available")
        return keyword_results
    
    else:
        # Combine both result sets
        # Ensure consistent columns
        keyword_cols = ['appln_id', 'docdb_family_id', 'appln_filing_year', 'appln_auth', 'search_type']
        classification_cols = ['appln_id', 'docdb_family_id', 'appln_filing_year', 'appln_auth', 'search_type']
        
        keyword_subset = keyword_results[keyword_cols]
        classification_subset = classification_results[classification_cols]
        
        combined_df = pd.concat([keyword_subset, classification_subset], ignore_index=True)
        
        # Deduplicate by appln_id
        before_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['appln_id'])
        after_dedup = len(combined_df)
        
        print(f"✅ Combined: {before_dedup} → {after_dedup} (removed {before_dedup - after_dedup} duplicates)")
        
        # Add search method tracking
        search_method_counts = combined_df['search_type'].value_counts()
        print(f"   Search methods: {search_method_counts.to_dict()}")
        
        return combined_df

def enrich_dataset_with_titles_abstracts(db, dataset):
    """
    Enrich dataset with complete title and abstract information
    """
    if dataset.empty:
        return dataset
    
    print("📄 Enriching with titles and abstracts...")
    
    appln_ids_str = ','.join(map(str, dataset['appln_id']))
    
    enrichment_query = f"""
    SELECT 
        a.appln_id,
        t.appln_title,
        ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE a.appln_id IN ({appln_ids_str})
    """
    
    try:
        enrichment_data = pd.read_sql(enrichment_query, db.bind)
        
        # Merge with original dataset
        enriched_dataset = dataset.merge(enrichment_data, on='appln_id', how='left')
        
        # Count data availability
        title_coverage = enriched_dataset['appln_title'].notna().sum()
        abstract_coverage = enriched_dataset['appln_abstract'].notna().sum()
        
        print(f"✅ Title coverage: {title_coverage}/{len(enriched_dataset)} ({title_coverage/len(enriched_dataset)*100:.1f}%)")
        print(f"✅ Abstract coverage: {abstract_coverage}/{len(enriched_dataset)} ({abstract_coverage/len(enriched_dataset)*100:.1f}%)")
        
        return enriched_dataset
        
    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        return dataset

def validate_dataset_structure(dataset):
    """
    Validate dataset structure and content quality
    """
    print("🔍 Validating dataset structure...")
    
    required_columns = ['appln_id', 'docdb_family_id', 'appln_filing_year', 'appln_auth']
    missing_columns = [col for col in required_columns if col not in dataset.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return False
    
    # Check for null values in critical columns
    null_counts = dataset[required_columns].isnull().sum()
    if null_counts.sum() > 0:
        print(f"⚠️  Null values found: {null_counts.to_dict()}")
    
    # Check year distribution
    year_range = dataset['appln_filing_year'].min(), dataset['appln_filing_year'].max()
    if year_range[0] < 2010 or year_range[1] > 2023:
        print(f"⚠️  Year range outside expected bounds: {year_range}")
    
    print(f"✅ Dataset structure valid")
    return True

if __name__ == "__main__":
    from database_connection import get_database_connection
    
    print("REE DATASET BUILDER - STANDALONE TEST")
    print("=" * 50)
    
    # Get database connection
    db = get_database_connection()
    if not db:
        print("❌ Database connection failed")
        exit(1)
    
    # Build dataset
    ree_dataset = build_ree_dataset(db, test_mode=True)
    
    if not ree_dataset.empty:
        # Enrich with full text
        enriched_dataset = enrich_dataset_with_titles_abstracts(db, ree_dataset)
        
        # Validate structure
        if validate_dataset_structure(enriched_dataset):
            print("\n🎯 Dataset building successful!")
            print(f"   Final dataset: {len(enriched_dataset)} REE applications")
            
            # Save sample for inspection
            sample_file = "ree_dataset_sample.csv"
            enriched_dataset.head(10).to_csv(sample_file, index=False)
            print(f"   Sample saved: {sample_file}")
        else:
            print("\n❌ Dataset validation failed")
    else:
        print("\n❌ No REE dataset created")