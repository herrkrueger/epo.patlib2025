import pandas as pd
from database_connection import get_patstat_connection

def enrich_with_geographic_data(db, ree_df):
    """Add comprehensive country information"""
    
    if ree_df.empty:
        print("❌ Empty REE dataset provided")
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    print("🌍 Enriching with geographic data...")
    
    # Get applicant country information
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
        
        # Get primary applicant country (first applicant)
        primary_applicants = geo_data[geo_data['applt_seq_nr'] == 1][['appln_id', 'person_ctry_code', 'country_name']].copy()
        primary_applicants.columns = ['appln_id', 'primary_applicant_country', 'primary_applicant_country_name']
        
        # Merge with original dataset
        enriched_df = ree_df.merge(primary_applicants, on='appln_id', how='left')
        
        print(f"Primary applicant countries: {enriched_df['primary_applicant_country'].nunique()}")
        
        return enriched_df
    else:
        print("❌ No geographic data found")
        return ree_df

def get_geographic_distribution(enriched_df):
    """Analyze geographic distribution patterns"""
    
    if enriched_df.empty or 'primary_applicant_country' not in enriched_df.columns:
        return {}
    
    # Country distribution analysis
    country_dist = enriched_df['primary_applicant_country'].value_counts()
    
    # Regional groupings (based on common patent analytics)
    regional_mapping = {
        'US': 'North America',
        'CA': 'North America',
        'MX': 'North America',
        'JP': 'Asia Pacific',
        'CN': 'Asia Pacific', 
        'KR': 'Asia Pacific',
        'IN': 'Asia Pacific',
        'AU': 'Asia Pacific',
        'SG': 'Asia Pacific',
        'TW': 'Asia Pacific',
        'DE': 'Europe',
        'GB': 'Europe',
        'FR': 'Europe',
        'IT': 'Europe',
        'NL': 'Europe',
        'SE': 'Europe',
        'CH': 'Europe',
        'DK': 'Europe',
        'FI': 'Europe',
        'NO': 'Europe',
        'AT': 'Europe',
        'BE': 'Europe',
        'ES': 'Europe',
        'PT': 'Europe',
        'IE': 'Europe',
        'LU': 'Europe',
        'BR': 'Latin America',
        'AR': 'Latin America',
        'CL': 'Latin America',
        'CO': 'Latin America',
        'PE': 'Latin America',
        'RU': 'Eurasia',
        'TR': 'Eurasia',
        'IL': 'Middle East & Africa',
        'ZA': 'Middle East & Africa',
        'EG': 'Middle East & Africa',
        'SA': 'Middle East & Africa',
        'AE': 'Middle East & Africa'
    }
    
    # Add regional classification
    enriched_df_copy = enriched_df.copy()
    enriched_df_copy['region'] = enriched_df_copy['primary_applicant_country'].map(regional_mapping)
    enriched_df_copy['region'] = enriched_df_copy['region'].fillna('Other')
    
    regional_dist = enriched_df_copy['region'].value_counts()
    
    # Time-based geographic trends
    yearly_country_trends = enriched_df_copy.groupby(['appln_filing_year', 'primary_applicant_country']).size().unstack(fill_value=0)
    
    # Market concentration analysis
    top_5_countries = country_dist.head(5)
    concentration_ratio = (top_5_countries.sum() / country_dist.sum()) * 100
    
    geographic_analysis = {
        'country_distribution': country_dist.to_dict(),
        'regional_distribution': regional_dist.to_dict(),
        'market_concentration': {
            'top_5_countries': top_5_countries.to_dict(),
            'concentration_ratio_percent': round(concentration_ratio, 2)
        },
        'geographic_diversity': {
            'total_countries': len(country_dist),
            'total_regions': len(regional_dist)
        }
    }
    
    return geographic_analysis

def analyze_geographic_collaboration(db, ree_df):
    """Analyze international collaboration patterns"""
    
    if ree_df.empty:
        return {}
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # Multi-country applications (international collaboration)
    collaboration_query = f"""
    SELECT 
        pa.appln_id,
        COUNT(DISTINCT p.person_ctry_code) as country_count,
        STRING_AGG(DISTINCT p.person_ctry_code, ',') as collaborating_countries
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    GROUP BY pa.appln_id
    HAVING COUNT(DISTINCT p.person_ctry_code) > 1
    """
    
    print("🤝 Analyzing international collaboration...")
    collaboration_data = pd.read_sql(collaboration_query, db.bind)
    
    collaboration_analysis = {}
    
    if not collaboration_data.empty:
        print(f"✅ Found {len(collaboration_data)} international collaborations")
        
        collaboration_analysis = {
            'total_collaborations': len(collaboration_data),
            'collaboration_rate_percent': round((len(collaboration_data) / len(ree_df)) * 100, 2),
            'average_countries_per_collaboration': round(collaboration_data['country_count'].mean(), 2),
            'max_countries_in_collaboration': collaboration_data['country_count'].max()
        }
        
        # Most common collaboration patterns
        country_pair_analysis = {}
        for _, row in collaboration_data.iterrows():
            countries = sorted(row['collaborating_countries'].split(','))
            if len(countries) == 2:
                pair = f"{countries[0]}-{countries[1]}"
                country_pair_analysis[pair] = country_pair_analysis.get(pair, 0) + 1
        
        if country_pair_analysis:
            collaboration_analysis['top_bilateral_collaborations'] = dict(
                sorted(country_pair_analysis.items(), key=lambda x: x[1], reverse=True)[:5]
            )
    else:
        print("❌ No international collaborations found")
        collaboration_analysis = {
            'total_collaborations': 0,
            'collaboration_rate_percent': 0
        }
    
    return collaboration_analysis

def get_comprehensive_geographic_intelligence(ree_df, test_mode=True):
    """Complete geographic intelligence analysis"""
    
    print("GEOGRAPHIC INTELLIGENCE ANALYSIS")
    print("=" * 40)
    
    db = get_patstat_connection()
    if not db:
        print("❌ Database connection failed")
        return None
    
    # Step 1: Enrich with geographic data
    print("\n🌍 GEOGRAPHIC ENRICHMENT")
    print("-" * 25)
    enriched_df = enrich_with_geographic_data(db, ree_df)
    
    # Step 2: Analyze distribution patterns
    print("\n📊 DISTRIBUTION ANALYSIS")
    print("-" * 25)
    distribution_analysis = get_geographic_distribution(enriched_df)
    
    for category, data in distribution_analysis.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {data}")
    
    # Step 3: Analyze collaboration patterns
    print("\n🤝 COLLABORATION ANALYSIS")
    print("-" * 25)
    collaboration_analysis = analyze_geographic_collaboration(db, ree_df)
    
    for metric, value in collaboration_analysis.items():
        print(f"  {metric.replace('_', ' ').title()}: {value}")
    
    return {
        'enriched_dataset': enriched_df,
        'distribution_analysis': distribution_analysis,
        'collaboration_analysis': collaboration_analysis
    }

if __name__ == "__main__":
    print("Testing Geographic Enricher...")
    
    # Create sample dataset for testing
    sample_data = pd.DataFrame({
        'appln_id': [12345, 23456, 34567],
        'docdb_family_id': [100, 200, 300],
        'appln_filing_year': [2020, 2021, 2022],
        'appln_auth': ['EP', 'US', 'JP']
    })
    
    results = get_comprehensive_geographic_intelligence(sample_data, test_mode=True)
    
    if results:
        print("\n✅ Geographic analysis complete!")
        enriched_data = results['enriched_dataset']
        print(f"Enriched dataset: {len(enriched_data)} records")
        if 'primary_applicant_country' in enriched_data.columns:
            print(f"Countries identified: {enriched_data['primary_applicant_country'].nunique()}")
    else:
        print("❌ Geographic analysis failed")