import pandas as pd
from database_connection import test_tip_connection
from dataset_builder import build_ree_dataset

def enrich_with_geographic_data(db, ree_df):
    """Add country information using verified table relationships"""
    
    if ree_df.empty:
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.st3_name as country_name
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    """
    
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        print(f"Found geographic data for {len(geo_data)} applicant-application pairs")
        enriched_df = ree_df.merge(geo_data, on='appln_id', how='left')
        return enriched_df
    else:
        print("ℹ️  No geographic data found")
        return ree_df

def analyze_country_citations(forward_citations_df):
    """Analyze citation flows between countries"""
    
    if not forward_citations_df.empty:
        top_citing = forward_citations_df['citing_country'].value_counts().head(10)
        print(f"Top citing countries: {top_citing.to_dict()}")
        return top_citing
    else:
        print("ℹ️  No forward citations to analyze")
        return pd.Series()

if __name__ == "__main__":
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            enriched_ree = enrich_with_geographic_data(db, ree_data)
            print(f"Enriched dataset: {len(enriched_ree)} applications")
            
            if 'country_name' in enriched_ree.columns:
                print(f"Country coverage: {enriched_ree['country_name'].value_counts().head(5).to_dict()}")
            
            # Test citation analysis (would need forward citations)
            forward_cit = pd.DataFrame()  # Empty for 2023 data
            top_citing = analyze_country_citations(forward_cit)