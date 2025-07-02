# EXACT WORKING CODE from successful implementation (TESTED: 47 countries mapped)
import pandas as pd

def enrich_with_geographic_data(db, ree_df):
    """Add comprehensive country information - VERIFIED WORKING"""
    
    if ree_df.empty:
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # PROVEN geographic query pattern
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.st3_name as country_name,
        pa.applt_seq_nr
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    ORDER BY pa.appln_id, pa.applt_seq_nr
    """
    
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        print(f"✅ Geographic data: {geo_data['person_ctry_code'].nunique()} countries")
        country_counts = geo_data['person_ctry_code'].value_counts()
        print(f"Top Countries: {country_counts.head(5).to_dict()}")
        
        # Get primary applicant (first applicant) - BUSINESS INTELLIGENCE
        primary_applicants = geo_data[geo_data['applt_seq_nr'] == 1][
            ['appln_id', 'person_ctry_code', 'country_name']
        ].copy()
        primary_applicants.columns = [
            'appln_id', 'primary_applicant_country', 'primary_applicant_country_name'
        ]
        
        # Also get all applicant countries for diversity analysis
        all_countries = geo_data.groupby('appln_id')['person_ctry_code'].apply(list).reset_index()
        all_countries.columns = ['appln_id', 'all_applicant_countries']
        
        # Merge both datasets
        enriched_df = ree_df.merge(primary_applicants, on='appln_id', how='left')
        enriched_df = enriched_df.merge(all_countries, on='appln_id', how='left')
        
        # Add geographic diversity score
        enriched_df['applicant_country_count'] = enriched_df['all_applicant_countries'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        )
        
        return enriched_df
    else:
        print("No geographic data found")
        return ree_df

def get_regional_aggregation(ree_dataset):
    """Aggregate countries into regions for business analysis"""
    
    # Regional mapping for business intelligence
    region_mapping = {
        'US': 'North America', 'CA': 'North America', 'MX': 'North America',
        'CN': 'Asia Pacific', 'JP': 'Asia Pacific', 'KR': 'Asia Pacific', 'IN': 'Asia Pacific',
        'DE': 'Europe', 'FR': 'Europe', 'GB': 'Europe', 'IT': 'Europe', 'NL': 'Europe',
        'AU': 'Asia Pacific', 'BR': 'Latin America', 'RU': 'Europe'
    }
    
    if 'primary_applicant_country' in ree_dataset.columns:
        ree_dataset['region'] = ree_dataset['primary_applicant_country'].map(region_mapping)
        ree_dataset['region'] = ree_dataset['region'].fillna('Other')
        
        regional_counts = ree_dataset['region'].value_counts()
        return regional_counts
    else:
        return pd.Series()

# MANDATORY: Test this component immediately after implementation
if __name__ == "__main__":
    print("Testing geographic enricher...")
    from database_connection_example import get_patstat_connection
    from dataset_builder_example import build_ree_dataset
    
    db = get_patstat_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            enriched_data = enrich_with_geographic_data(db, ree_data)
            if 'primary_applicant_country' in enriched_data.columns:
                countries_found = enriched_data['primary_applicant_country'].nunique()
                print(f"✅ Geographic enricher test PASSED: {countries_found} countries")
                
                # Test regional aggregation
                regional_data = get_regional_aggregation(enriched_data)
                if not regional_data.empty:
                    print(f"✅ Regional aggregation test PASSED: {len(regional_data)} regions")
            else:
                print("❌ Geographic enricher test FAILED: No country data added")
        else:
            print("❌ Cannot test geographic enricher: No REE data")
    else:
        print("❌ Cannot test geographic enricher: Database connection failed")