"""
Geographic Enrichment Module for REE Patent Analysis
Country intelligence and network data for strategic analysis
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import traceback

def enrich_with_geographic_data(db, ree_df):
    """
    Add comprehensive country information to REE dataset
    
    Args:
        db: Database connection
        ree_df: DataFrame with REE applications
    
    Returns:
        DataFrame enriched with geographic data
    """
    
    if ree_df.empty:
        print("❌ No REE data provided for geographic enrichment")
        return ree_df
    
    print(f"🌍 Geographic enrichment for {len(ree_df)} REE applications...")
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # Comprehensive geographic query
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        pa.applt_seq_nr,
        p.person_ctry_code,
        c.st3_name as country_name,
        c.ctry_code as country_code_2char,
        pa.invt_seq_nr
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND (pa.applt_seq_nr > 0 OR pa.invt_seq_nr > 0)
    """
    
    try:
        geo_data = pd.read_sql(geo_query, db.bind)
        
        if not geo_data.empty:
            print(f"✅ Geographic data: {geo_data['person_ctry_code'].nunique()} countries")
            
            # Country distribution
            country_counts = geo_data['person_ctry_code'].value_counts()
            print(f"   Top countries: {country_counts.head(5).to_dict()}")
            
            # Process applicant and inventor data separately
            applicant_data = geo_data[geo_data['applt_seq_nr'] > 0].copy()
            inventor_data = geo_data[geo_data['invt_seq_nr'] > 0].copy()
            
            # Merge with original dataset
            enriched_df = merge_geographic_data(ree_df, applicant_data, inventor_data)
            
            return enriched_df
        else:
            print("❌ No geographic data found")
            return ree_df
            
    except Exception as e:
        print(f"❌ Geographic enrichment failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return ree_df

def merge_geographic_data(ree_df, applicant_data, inventor_data):
    """
    Merge applicant and inventor geographic data with REE dataset
    """
    
    print("🔗 Merging geographic data...")
    
    # Aggregate applicant countries per application
    if not applicant_data.empty:
        applicant_agg = applicant_data.groupby('appln_id').agg({
            'person_ctry_code': lambda x: ';'.join(sorted(set(x))),
            'country_name': lambda x: ';'.join(sorted(set(x)))
        }).reset_index()
        
        applicant_agg.columns = ['appln_id', 'applicant_countries', 'applicant_country_names']
        
        # Count of applicant countries
        applicant_agg['applicant_country_count'] = applicant_agg['applicant_countries'].str.count(';') + 1
        
        ree_df = ree_df.merge(applicant_agg, on='appln_id', how='left')
        print(f"✅ Applicant data merged: {applicant_data['person_ctry_code'].nunique()} countries")
    else:
        ree_df['applicant_countries'] = None
        ree_df['applicant_country_names'] = None
        ree_df['applicant_country_count'] = 0
    
    # Aggregate inventor countries per application
    if not inventor_data.empty:
        inventor_agg = inventor_data.groupby('appln_id').agg({
            'person_ctry_code': lambda x: ';'.join(sorted(set(x))),
            'country_name': lambda x: ';'.join(sorted(set(x)))
        }).reset_index()
        
        inventor_agg.columns = ['appln_id', 'inventor_countries', 'inventor_country_names']
        
        # Count of inventor countries
        inventor_agg['inventor_country_count'] = inventor_agg['inventor_countries'].str.count(';') + 1
        
        ree_df = ree_df.merge(inventor_agg, on='appln_id', how='left')
        print(f"✅ Inventor data merged: {inventor_data['person_ctry_code'].nunique()} countries")
    else:
        ree_df['inventor_countries'] = None
        ree_df['inventor_country_names'] = None
        ree_df['inventor_country_count'] = 0
    
    return ree_df

def analyze_geographic_patterns(enriched_df):
    """
    Analyze geographic patterns for business intelligence
    
    Args:
        enriched_df: DataFrame enriched with geographic data
    
    Returns:
        Dictionary with geographic analysis results
    """
    
    print("📊 Analyzing geographic patterns...")
    
    if enriched_df.empty:
        return {}
    
    analysis = {
        'total_applications': len(enriched_df),
        'filing_countries': {},
        'applicant_countries': {},
        'inventor_countries': {},
        'international_collaboration': {},
        'regional_patterns': {},
        'strategic_insights': []
    }
    
    # Filing country analysis
    if 'appln_auth' in enriched_df.columns:
        filing_countries = enriched_df['appln_auth'].value_counts()
        analysis['filing_countries'] = filing_countries.to_dict()
        print(f"   Filing countries: {len(filing_countries)} different authorities")
    
    # Applicant country analysis
    if 'applicant_countries' in enriched_df.columns:
        applicant_countries = extract_country_frequencies(enriched_df, 'applicant_countries')
        analysis['applicant_countries'] = applicant_countries
        print(f"   Applicant countries: {len(applicant_countries)} unique countries")
    
    # Inventor country analysis
    if 'inventor_countries' in enriched_df.columns:
        inventor_countries = extract_country_frequencies(enriched_df, 'inventor_countries')
        analysis['inventor_countries'] = inventor_countries
        print(f"   Inventor countries: {len(inventor_countries)} unique countries")
    
    # International collaboration analysis
    collaboration_analysis = analyze_collaboration_patterns(enriched_df)
    analysis['international_collaboration'] = collaboration_analysis
    
    # Regional patterns
    regional_patterns = analyze_regional_patterns(enriched_df)
    analysis['regional_patterns'] = regional_patterns
    
    # Strategic insights
    strategic_insights = generate_strategic_insights(analysis)
    analysis['strategic_insights'] = strategic_insights
    
    print(f"✅ Geographic pattern analysis complete")
    
    return analysis

def extract_country_frequencies(df, column_name):
    """
    Extract country frequencies from semicolon-separated country strings
    """
    
    country_freq = defaultdict(int)
    
    for countries_str in df[column_name].dropna():
        if isinstance(countries_str, str) and countries_str:
            countries = countries_str.split(';')
            for country in countries:
                country = country.strip()
                if country:
                    country_freq[country] += 1
    
    return dict(sorted(country_freq.items(), key=lambda x: x[1], reverse=True))

def analyze_collaboration_patterns(enriched_df):
    """
    Analyze international collaboration patterns
    """
    
    collaboration = {
        'total_applications': len(enriched_df),
        'single_country_applicants': 0,
        'multi_country_applicants': 0,
        'single_country_inventors': 0,
        'multi_country_inventors': 0,
        'cross_border_innovation': 0
    }
    
    if 'applicant_country_count' in enriched_df.columns:
        single_app = (enriched_df['applicant_country_count'] == 1).sum()
        multi_app = (enriched_df['applicant_country_count'] > 1).sum()
        
        collaboration['single_country_applicants'] = int(single_app)
        collaboration['multi_country_applicants'] = int(multi_app)
    
    if 'inventor_country_count' in enriched_df.columns:
        single_inv = (enriched_df['inventor_country_count'] == 1).sum()
        multi_inv = (enriched_df['inventor_country_count'] > 1).sum()
        
        collaboration['single_country_inventors'] = int(single_inv)
        collaboration['multi_country_inventors'] = int(multi_inv)
    
    # Cross-border innovation (inventors from different countries than applicants)
    if 'applicant_countries' in enriched_df.columns and 'inventor_countries' in enriched_df.columns:
        cross_border = 0
        for _, row in enriched_df.iterrows():
            app_countries = set(str(row['applicant_countries']).split(';')) if pd.notna(row['applicant_countries']) else set()
            inv_countries = set(str(row['inventor_countries']).split(';')) if pd.notna(row['inventor_countries']) else set()
            
            if app_countries and inv_countries and not app_countries.intersection(inv_countries):
                cross_border += 1
        
        collaboration['cross_border_innovation'] = cross_border
    
    return collaboration

def analyze_regional_patterns(enriched_df):
    """
    Analyze regional patterns and strategic groupings
    """
    
    # Define strategic regional groupings
    regional_groups = {
        'IP5': ['US', 'JP', 'DE', 'KR', 'CN'],  # Major IP offices
        'EU': ['DE', 'FR', 'GB', 'IT', 'ES', 'NL', 'SE', 'FI', 'AT', 'BE', 'DK'],
        'Asia_Pacific': ['JP', 'KR', 'CN', 'AU', 'SG', 'TW', 'IN'],
        'North_America': ['US', 'CA', 'MX'],
        'Emerging_Markets': ['CN', 'IN', 'BR', 'RU', 'ZA']
    }
    
    regional_analysis = {}
    
    for region, countries in regional_groups.items():
        regional_analysis[region] = analyze_region_activity(enriched_df, countries)
    
    return regional_analysis

def analyze_region_activity(enriched_df, region_countries):
    """
    Analyze patent activity within a specific region
    """
    
    activity = {
        'filing_count': 0,
        'applicant_count': 0,
        'inventor_count': 0,
        'countries_active': []
    }
    
    # Filing activity
    if 'appln_auth' in enriched_df.columns:
        filing_in_region = enriched_df['appln_auth'].isin(region_countries).sum()
        activity['filing_count'] = int(filing_in_region)
    
    # Applicant activity
    if 'applicant_countries' in enriched_df.columns:
        applicant_count = 0
        for countries_str in enriched_df['applicant_countries'].dropna():
            if isinstance(countries_str, str):
                countries = countries_str.split(';')
                if any(country.strip() in region_countries for country in countries):
                    applicant_count += 1
        activity['applicant_count'] = applicant_count
    
    # Inventor activity
    if 'inventor_countries' in enriched_df.columns:
        inventor_count = 0
        for countries_str in enriched_df['inventor_countries'].dropna():
            if isinstance(countries_str, str):
                countries = countries_str.split(';')
                if any(country.strip() in region_countries for country in countries):
                    inventor_count += 1
        activity['inventor_count'] = inventor_count
    
    # Active countries in region
    all_countries = set()
    for col in ['applicant_countries', 'inventor_countries']:
        if col in enriched_df.columns:
            for countries_str in enriched_df[col].dropna():
                if isinstance(countries_str, str):
                    countries = [c.strip() for c in countries_str.split(';')]
                    all_countries.update(countries)
    
    active_in_region = [country for country in region_countries if country in all_countries]
    activity['countries_active'] = active_in_region
    
    return activity

def generate_strategic_insights(analysis):
    """
    Generate strategic insights from geographic analysis
    """
    
    insights = []
    
    # Market concentration insights
    if 'filing_countries' in analysis and analysis['filing_countries']:
        top_filing = list(analysis['filing_countries'].keys())[0]
        top_count = analysis['filing_countries'][top_filing]
        total = analysis['total_applications']
        concentration = (top_count / total) * 100
        
        if concentration > 50:
            insights.append(f"High market concentration: {top_filing} dominates with {concentration:.1f}% of filings")
        elif concentration > 30:
            insights.append(f"Moderate market concentration: {top_filing} leads with {concentration:.1f}% of filings")
        else:
            insights.append(f"Distributed market: {top_filing} leads but only {concentration:.1f}% of filings")
    
    # Collaboration insights
    if 'international_collaboration' in analysis:
        collab = analysis['international_collaboration']
        total = collab.get('total_applications', 0)
        
        if total > 0:
            multi_app_pct = (collab.get('multi_country_applicants', 0) / total) * 100
            multi_inv_pct = (collab.get('multi_country_inventors', 0) / total) * 100
            
            if multi_app_pct > 20:
                insights.append(f"High international applicant collaboration: {multi_app_pct:.1f}% of applications")
            
            if multi_inv_pct > 30:
                insights.append(f"Strong cross-border R&D: {multi_inv_pct:.1f}% have international inventor teams")
    
    # Regional insights
    if 'regional_patterns' in analysis:
        regions = analysis['regional_patterns']
        
        # Find most active region
        region_activity = {}
        for region, data in regions.items():
            region_activity[region] = data.get('applicant_count', 0) + data.get('inventor_count', 0)
        
        if region_activity:
            most_active = max(region_activity, key=region_activity.get)
            insights.append(f"Most active region: {most_active} with highest combined activity")
    
    return insights

def export_geographic_analysis(enriched_df, geographic_analysis, output_prefix="ree_geographic"):
    """
    Export geographic analysis results
    """
    
    print("💾 Exporting geographic analysis...")
    
    try:
        # Export enriched dataset
        if not enriched_df.empty:
            enriched_file = f"{output_prefix}_enriched.csv"
            enriched_df.to_csv(enriched_file, index=False)
            print(f"✅ Enriched dataset: {enriched_file}")
        
        # Export geographic analysis summary
        if geographic_analysis:
            import json
            analysis_file = f"{output_prefix}_analysis.json"
            with open(analysis_file, 'w') as f:
                json.dump(geographic_analysis, f, indent=2)
            print(f"✅ Geographic analysis: {analysis_file}")
        
        print("✅ Geographic export complete")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    from database_connection import get_database_connection
    from dataset_builder import build_ree_dataset
    
    print("GEOGRAPHIC ENRICHER - STANDALONE TEST")
    print("=" * 50)
    
    # Get database connection
    db = get_database_connection()
    if not db:
        print("❌ Database connection failed")
        exit(1)
    
    # Build REE dataset for testing
    print("\n📊 Building test dataset...")
    ree_dataset = build_ree_dataset(db, test_mode=True)
    
    if ree_dataset.empty:
        print("❌ No REE dataset available for geographic testing")
        exit(1)
    
    # Test geographic enrichment
    print(f"\n🌍 Testing geographic enrichment with {len(ree_dataset)} applications...")
    
    # Enrich with geographic data
    enriched_data = enrich_with_geographic_data(db, ree_dataset)
    
    # Analyze geographic patterns
    geographic_analysis = analyze_geographic_patterns(enriched_data)
    
    # Export results
    export_geographic_analysis(enriched_data, geographic_analysis, "test_ree_geographic")
    
    print("\n🎯 Geographic enrichment test complete!")
    print(f"   Applications: {len(enriched_data)}")
    print(f"   Countries: {len(geographic_analysis.get('applicant_countries', {}))}")
    print(f"   Insights: {len(geographic_analysis.get('strategic_insights', []))}")