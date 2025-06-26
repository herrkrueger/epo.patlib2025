# 4.1 Geographic Data Enhancement using Direct SQL
import pandas as pd
from datetime import datetime

def enrich_with_geographic_data(db, ree_df):
    """
    Add country codes and geographic information
    Uses direct SQL queries to avoid ORM complications
    """
    
    if ree_df.empty:
        print("No REE data provided for geographic enrichment")
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # VERIFIED: Get geographic data through person-application links using documented table relationships
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.iso_alpha3,
        c.st3_name as country_name,
        pa.applt_seq_nr
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0  -- Only applicants, not inventors
    """
    
    print("Enriching with geographic data...")
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        # Merge with REE data
        enriched_df = ree_df.merge(
            geo_data, 
            on='appln_id', 
            how='left'
        )
        print(f"Geographic enrichment: {len(geo_data)} geographic records added")
        return enriched_df
    else:
        print("No geographic data found")
        return ree_df

def analyze_country_citations(forward_citations_df, backward_citations_df):
    """
    Analyze citation flows between countries
    Uses direct DataFrame operations
    """
    
    print("\nCountry Citation Analysis:")
    
    if not forward_citations_df.empty:
        # Top citing countries
        top_citing = forward_citations_df['citing_country'].value_counts().head(10)
        print(f"Top citing countries: {top_citing.to_dict()}")
        
        # Citation flows (if we have both citing and cited country data)
        if 'cited_country' in forward_citations_df.columns:
            citation_flows = forward_citations_df.groupby(
                ['citing_country', 'cited_country']
            ).size().reset_index(name='citation_count')
            
            print(f"Citation flows identified: {len(citation_flows)} country pairs")
            return citation_flows, top_citing
    
    return pd.DataFrame(), pd.Series()

def create_country_summary(enriched_ree_df):
    """Create summary statistics by country"""
    
    if 'country_name' not in enriched_ree_df.columns:
        print("No country data available for summary")
        return pd.DataFrame()
    
    country_summary = enriched_ree_df.groupby('country_name').agg({
        'appln_id': 'count',
        'docdb_family_id': 'nunique',
        'appln_filing_year': ['min', 'max']
    }).round(2)
    
    country_summary.columns = ['total_applications', 'unique_families', 'first_year', 'last_year']
    country_summary = country_summary.sort_values('total_applications', ascending=False)
    
    print(f"\nCountry Summary (Top 10):")
    print(country_summary.head(10))
    
    return country_summary

if __name__ == "__main__":
    # Test geographic analysis
    print("Testing geographic enrichment...")
    import importlib.util
    
    # Import database connection
    spec = importlib.util.spec_from_file_location("database_connection", "01_database_connection.py")
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    test_tip_connection = db_module.test_tip_connection
    
    # Import REE dataset builder
    spec2 = importlib.util.spec_from_file_location("ree_dataset_builder", "02_ree_dataset_builder.py")
    ree_module = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ree_module)
    build_ree_dataset = ree_module.build_ree_dataset
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            enriched_data = enrich_with_geographic_data(db, ree_data)
            country_summary = create_country_summary(enriched_data)