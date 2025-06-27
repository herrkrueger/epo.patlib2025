"""
Geographic Enricher Component for REE Patent Citation Analysis
Geographic context and country mapping for strategic intelligence
"""

import pandas as pd
import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Strategic country groupings for REE analysis
STRATEGIC_COUNTRY_GROUPS = {
    'IP5_OFFICES': ['US', 'EP', 'JP', 'CN', 'KR'],
    'REE_PRODUCERS': ['CN', 'US', 'MY', 'AU', 'MM', 'TH', 'IN', 'BR', 'VN'],
    'REE_CONSUMERS': ['US', 'JP', 'DE', 'KR', 'CN', 'GB', 'FR', 'IT', 'NL'],
    'EU_MEMBERS': ['DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'SE', 'DK', 'FI', 'IE', 'PT', 'GR', 'LU'],
    'EMERGING_MARKETS': ['CN', 'IN', 'BR', 'RU', 'ZA', 'MX', 'TH', 'ID', 'MY', 'VN'],
    'TECH_LEADERS': ['US', 'JP', 'DE', 'KR', 'CN', 'GB', 'FR', 'CA', 'AU', 'SE']
}

# Regional mappings for broader analysis
REGIONAL_MAPPINGS = {
    'NORTH_AMERICA': ['US', 'CA', 'MX'],
    'EUROPE': ['DE', 'FR', 'GB', 'IT', 'ES', 'NL', 'BE', 'AT', 'SE', 'DK', 'FI', 'CH', 'NO'],
    'ASIA_PACIFIC': ['CN', 'JP', 'KR', 'IN', 'AU', 'SG', 'MY', 'TH', 'ID', 'PH', 'VN', 'TW'],
    'LATIN_AMERICA': ['BR', 'MX', 'AR', 'CL', 'CO', 'PE', 'UY'],
    'MIDDLE_EAST_AFRICA': ['ZA', 'IL', 'AE', 'SA', 'EG', 'MA', 'NG', 'KE']
}

def enrich_with_geographic_data(db, ree_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add comprehensive country information and applicant data
    """
    if ree_df.empty:
        logger.warning("Empty dataset provided for geographic enrichment")
        return ree_df
    
    logger.info(f"🌍 Enriching {len(ree_df)} applications with geographic data...")
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # Enhanced geographic query with applicant and inventor information
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        pa.applt_seq_nr,
        pa.invt_seq_nr,
        p.person_ctry_code,
        p.person_name,
        p.person_address,
        c.st3_name as country_name,
        c.iso_alpha3,
        CASE 
            WHEN pa.applt_seq_nr > 0 THEN 'applicant'
            WHEN pa.invt_seq_nr > 0 THEN 'inventor'
            ELSE 'unknown'
        END as person_type
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND (pa.applt_seq_nr > 0 OR pa.invt_seq_nr > 0)
    AND p.person_ctry_code IS NOT NULL
    """
    
    try:
        geo_data = pd.read_sql(geo_query, db.bind)
        
        if not geo_data.empty:
            logger.info(f"✅ Geographic data retrieved: {len(geo_data)} person-application records")
            logger.info(f"   Countries covered: {geo_data['person_ctry_code'].nunique()}")
            logger.info(f"   Applicants: {len(geo_data[geo_data['person_type'] == 'applicant'])}")
            logger.info(f"   Inventors: {len(geo_data[geo_data['person_type'] == 'inventor'])}")
            
            # Merge with REE dataset
            enriched_df = ree_df.merge(geo_data, on='appln_id', how='left')
            
            return enriched_df
        else:
            logger.warning("No geographic data found")
            return ree_df
            
    except Exception as e:
        logger.error(f"❌ Geographic enrichment failed: {e}")
        return ree_df

def add_strategic_country_classifications(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add strategic country group classifications
    """
    if df.empty or 'person_ctry_code' not in df.columns:
        return df
    
    df = df.copy()
    
    # Add strategic group classifications
    for group_name, countries in STRATEGIC_COUNTRY_GROUPS.items():
        df[f'is_{group_name.lower()}'] = df['person_ctry_code'].isin(countries)
    
    # Add regional classifications
    df['region'] = 'OTHER'
    for region_name, countries in REGIONAL_MAPPINGS.items():
        mask = df['person_ctry_code'].isin(countries)
        df.loc[mask, 'region'] = region_name
    
    logger.info("✅ Strategic country classifications added")
    return df

def analyze_geographic_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze geographic distribution patterns
    """
    if df.empty or 'person_ctry_code' not in df.columns:
        return {}
    
    analysis = {}
    
    # Basic country distribution
    country_dist = df['person_ctry_code'].value_counts()
    analysis['top_countries'] = dict(country_dist.head(15))
    analysis['total_countries'] = len(country_dist)
    
    # Regional distribution
    if 'region' in df.columns:
        region_dist = df['region'].value_counts()
        analysis['regional_distribution'] = dict(region_dist)
    
    # Strategic group analysis
    strategic_analysis = {}
    for group_name in STRATEGIC_COUNTRY_GROUPS.keys():
        col_name = f'is_{group_name.lower()}'
        if col_name in df.columns:
            count = df[col_name].sum()
            percentage = (count / len(df)) * 100
            strategic_analysis[group_name] = {
                'count': int(count),
                'percentage': round(percentage, 1)
            }
    
    analysis['strategic_groups'] = strategic_analysis
    
    # Applicant vs Inventor analysis
    if 'person_type' in df.columns:
        person_type_dist = df['person_type'].value_counts()
        analysis['person_type_distribution'] = dict(person_type_dist)
    
    return analysis

def calculate_geographic_diversity_score(df: pd.DataFrame) -> int:
    """
    Calculate geographic diversity score (0-100) for business assessment
    """
    if df.empty or 'person_ctry_code' not in df.columns:
        return 0
    
    score = 0
    unique_countries = df['person_ctry_code'].nunique()
    
    # Country diversity (40 points max)
    if unique_countries >= 20: score += 40
    elif unique_countries >= 15: score += 35
    elif unique_countries >= 10: score += 30
    elif unique_countries >= 7: score += 25
    elif unique_countries >= 5: score += 20
    elif unique_countries >= 3: score += 15
    elif unique_countries >= 2: score += 10
    
    # Regional coverage (25 points max)
    if 'region' in df.columns:
        unique_regions = df['region'].nunique()
        if unique_regions >= 5: score += 25
        elif unique_regions >= 4: score += 20
        elif unique_regions >= 3: score += 15
        elif unique_regions >= 2: score += 10
    
    # Strategic group coverage (25 points max)
    strategic_coverage = 0
    for group_name in STRATEGIC_COUNTRY_GROUPS.keys():
        col_name = f'is_{group_name.lower()}'
        if col_name in df.columns and df[col_name].any():
            strategic_coverage += 1
    
    if strategic_coverage >= 5: score += 25
    elif strategic_coverage >= 4: score += 20
    elif strategic_coverage >= 3: score += 15
    elif strategic_coverage >= 2: score += 10
    elif strategic_coverage >= 1: score += 5
    
    # IP5 coverage bonus (10 points max)
    if 'is_ip5_offices' in df.columns:
        ip5_countries = df[df['is_ip5_offices']]['person_ctry_code'].nunique()
        if ip5_countries >= 4: score += 10
        elif ip5_countries >= 3: score += 8
        elif ip5_countries >= 2: score += 6
        elif ip5_countries >= 1: score += 4
    
    return min(score, 100)

def identify_geographic_hotspots(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identify geographic innovation hotspots and collaboration patterns
    """
    if df.empty:
        return {}
    
    hotspots = {}
    
    # Application hotspots by country
    if 'person_ctry_code' in df.columns:
        country_apps = df.groupby('person_ctry_code')['appln_id'].nunique().sort_values(ascending=False)
        hotspots['innovation_hotspots'] = dict(country_apps.head(10))
    
    # Collaboration patterns (multiple countries per application)
    if 'appln_id' in df.columns and 'person_ctry_code' in df.columns:
        # Find applications with multiple countries
        countries_per_app = df.groupby('appln_id')['person_ctry_code'].nunique()
        collaborative_apps = countries_per_app[countries_per_app > 1]
        
        if not collaborative_apps.empty:
            hotspots['collaboration_rate'] = len(collaborative_apps) / df['appln_id'].nunique()
            hotspots['avg_countries_per_collaborative_app'] = collaborative_apps.mean()
        
        # Find most common collaboration pairs
        collab_apps = collaborative_apps.index
        collab_data = df[df['appln_id'].isin(collab_apps)]
        
        if not collab_data.empty:
            # Group by application and get country combinations
            country_combinations = []
            for app_id in collab_apps:
                app_countries = collab_data[collab_data['appln_id'] == app_id]['person_ctry_code'].unique()
                if len(app_countries) > 1:
                    # Create pairs from countries
                    for i in range(len(app_countries)):
                        for j in range(i+1, len(app_countries)):
                            pair = tuple(sorted([app_countries[i], app_countries[j]]))
                            country_combinations.append(pair)
            
            if country_combinations:
                from collections import Counter
                pair_counts = Counter(country_combinations)
                hotspots['top_collaboration_pairs'] = dict(pair_counts.most_common(10))
    
    # REE-specific strategic positioning
    if 'is_ree_producers' in df.columns and 'is_ree_consumers' in df.columns:
        producer_apps = df[df['is_ree_producers']]['appln_id'].nunique()
        consumer_apps = df[df['is_ree_consumers']]['appln_id'].nunique()
        total_apps = df['appln_id'].nunique()
        
        hotspots['ree_strategic_positioning'] = {
            'producer_country_activity': producer_apps / total_apps if total_apps > 0 else 0,
            'consumer_country_activity': consumer_apps / total_apps if total_apps > 0 else 0
        }
    
    return hotspots

def generate_geographic_intelligence_report(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive geographic intelligence report
    """
    logger.info("🌍 Generating geographic intelligence report...")
    
    # Basic distribution analysis
    distribution = analyze_geographic_distribution(df)
    
    # Diversity scoring
    diversity_score = calculate_geographic_diversity_score(df)
    
    # Hotspot identification
    hotspots = identify_geographic_hotspots(df)
    
    # Compile comprehensive report
    report = {
        'distribution_analysis': distribution,
        'diversity_score': diversity_score,
        'geographic_hotspots': hotspots,
        'summary_statistics': {
            'total_applications': df['appln_id'].nunique() if 'appln_id' in df.columns else len(df),
            'total_countries': distribution.get('total_countries', 0),
            'total_regions': len(distribution.get('regional_distribution', {})),
            'collaboration_rate': hotspots.get('collaboration_rate', 0)
        }
    }
    
    logger.info("✅ Geographic intelligence report generated")
    return report

def perform_complete_geographic_analysis(db, ree_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform comprehensive geographic analysis pipeline
    """
    logger.info("🌍 STARTING COMPREHENSIVE GEOGRAPHIC ANALYSIS")
    logger.info("=" * 50)
    
    # Step 1: Enrich with geographic data
    enriched_df = enrich_with_geographic_data(db, ree_df)
    
    # Step 2: Add strategic classifications
    classified_df = add_strategic_country_classifications(enriched_df)
    
    # Step 3: Generate intelligence report
    intelligence_report = generate_geographic_intelligence_report(classified_df)
    
    # Compile results
    analysis_results = {
        'enriched_dataset': classified_df,
        'intelligence_report': intelligence_report
    }
    
    # Log summary
    logger.info("GEOGRAPHIC ANALYSIS COMPLETE")
    logger.info("=" * 50)
    report = intelligence_report
    logger.info(f"Countries covered: {report['summary_statistics']['total_countries']}")
    logger.info(f"Regions covered: {report['summary_statistics']['total_regions']}")
    logger.info(f"Diversity score: {report['diversity_score']}/100")
    logger.info(f"Collaboration rate: {report['summary_statistics']['collaboration_rate']:.1%}")
    
    return analysis_results

if __name__ == "__main__":
    # Test the geographic enricher
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    
    logger.info("Testing Geographic Enricher...")
    
    # Get database connection
    db = test_tip_connection()
    if not db:
        logger.error("Cannot test geographic enricher without database connection")
        exit(1)
    
    # Build test dataset
    ree_data = build_ree_dataset(db, test_mode=True)
    if ree_data.empty:
        logger.error("Cannot test geographic enricher without REE dataset")
        exit(1)
    
    # Test geographic analysis
    geo_results = perform_complete_geographic_analysis(db, ree_data)
    
    print("\n" + "="*70)
    print("GEOGRAPHIC ENRICHER TEST COMPLETE")
    print("="*70)
    
    if geo_results['intelligence_report']:
        report = geo_results['intelligence_report']
        print(f"✅ Countries: {report['summary_statistics']['total_countries']}")
        print(f"✅ Regions: {report['summary_statistics']['total_regions']}")
        print(f"✅ Diversity score: {report['diversity_score']}/100")
        print(f"✅ Collaboration rate: {report['summary_statistics']['collaboration_rate']:.1%}")
        print("✅ Ready for data validation")
    else:
        print("❌ Geographic analysis returned no results")