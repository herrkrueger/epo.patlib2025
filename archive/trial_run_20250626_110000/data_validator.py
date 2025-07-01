"""
Data Validation Module for REE Patent Citation Analysis
Quality metrics and business reporting for professional presentations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import traceback

def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df, geographic_analysis=None):
    """
    Comprehensive quality assessment for REE patent analysis
    
    Args:
        ree_df: DataFrame with REE applications
        forward_citations_df: DataFrame with forward citations
        backward_citations_df: DataFrame with backward citations
        geographic_analysis: Dictionary with geographic analysis (optional)
    
    Returns:
        Dictionary with quality metrics and assessment
    """
    
    print("🔍 DATASET QUALITY VALIDATION")
    print("=" * 50)
    
    quality_metrics = {
        'dataset_overview': {},
        'coverage_metrics': {},
        'citation_metrics': {},
        'geographic_metrics': {},
        'quality_scores': {},
        'business_readiness': {},
        'recommendations': []
    }
    
    # Dataset overview
    quality_metrics['dataset_overview'] = analyze_dataset_overview(ree_df)
    
    # Coverage analysis
    quality_metrics['coverage_metrics'] = analyze_coverage_quality(ree_df)
    
    # Citation quality
    quality_metrics['citation_metrics'] = analyze_citation_quality(forward_citations_df, backward_citations_df)
    
    # Geographic quality
    quality_metrics['geographic_metrics'] = analyze_geographic_quality(ree_df, geographic_analysis)
    
    # Calculate overall quality scores
    quality_metrics['quality_scores'] = calculate_quality_scores(quality_metrics)
    
    # Business readiness assessment
    quality_metrics['business_readiness'] = assess_business_readiness(quality_metrics)
    
    # Generate recommendations
    quality_metrics['recommendations'] = generate_quality_recommendations(quality_metrics)
    
    # Print quality report
    print_quality_report(quality_metrics)
    
    return quality_metrics

def analyze_dataset_overview(ree_df):
    """
    Analyze basic dataset characteristics
    """
    
    overview = {
        'total_applications': len(ree_df),
        'total_families': 0,
        'year_range': {},
        'countries_covered': 0,
        'data_completeness': {}
    }
    
    if not ree_df.empty:
        # Family analysis
        if 'docdb_family_id' in ree_df.columns:
            overview['total_families'] = ree_df['docdb_family_id'].nunique()
        
        # Year range
        if 'appln_filing_year' in ree_df.columns:
            years = ree_df['appln_filing_year'].dropna()
            if not years.empty:
                overview['year_range'] = {
                    'min': int(years.min()),
                    'max': int(years.max()),
                    'span': int(years.max() - years.min() + 1)
                }
        
        # Country coverage
        if 'appln_auth' in ree_df.columns:
            overview['countries_covered'] = ree_df['appln_auth'].nunique()
        
        # Data completeness
        total_records = len(ree_df)
        completeness = {}
        
        for col in ['appln_title', 'appln_abstract', 'applicant_countries', 'inventor_countries']:
            if col in ree_df.columns:
                non_null_count = ree_df[col].notna().sum()
                completeness[col] = {
                    'available': int(non_null_count),
                    'percentage': float(non_null_count / total_records * 100)
                }
        
        overview['data_completeness'] = completeness
    
    return overview

def analyze_coverage_quality(ree_df):
    """
    Analyze data coverage quality
    """
    
    coverage = {
        'temporal_coverage': {},
        'geographic_coverage': {},
        'content_coverage': {},
        'coverage_score': 0
    }
    
    if not ree_df.empty:
        # Temporal coverage
        if 'appln_filing_year' in ree_df.columns:
            years = ree_df['appln_filing_year'].dropna()
            if not years.empty:
                year_distribution = years.value_counts().sort_index()
                coverage['temporal_coverage'] = {
                    'years_covered': len(year_distribution),
                    'min_year': int(years.min()),
                    'max_year': int(years.max()),
                    'average_per_year': float(len(ree_df) / len(year_distribution)),
                    'distribution_consistency': calculate_distribution_consistency(year_distribution)
                }
        
        # Geographic coverage
        if 'appln_auth' in ree_df.columns:
            auth_distribution = ree_df['appln_auth'].value_counts()
            coverage['geographic_coverage'] = {
                'authorities_covered': len(auth_distribution),
                'top_authorities': auth_distribution.head(5).to_dict(),
                'concentration_ratio': float(auth_distribution.iloc[0] / len(ree_df)) if len(auth_distribution) > 0 else 0
            }
        
        # Content coverage
        content_metrics = {}
        if 'appln_title' in ree_df.columns:
            titles_available = ree_df['appln_title'].notna().sum()
            content_metrics['title_coverage'] = float(titles_available / len(ree_df))
        
        if 'appln_abstract' in ree_df.columns:
            abstracts_available = ree_df['appln_abstract'].notna().sum()
            content_metrics['abstract_coverage'] = float(abstracts_available / len(ree_df))
        
        coverage['content_coverage'] = content_metrics
        
        # Calculate coverage score
        coverage['coverage_score'] = calculate_coverage_score(coverage)
    
    return coverage

def analyze_citation_quality(forward_citations_df, backward_citations_df):
    """
    Analyze citation data quality
    """
    
    citation_quality = {
        'forward_citations': {},
        'backward_citations': {},
        'citation_balance': {},
        'origin_diversity': {},
        'temporal_patterns': {},
        'citation_score': 0
    }
    
    # Forward citation analysis
    if not forward_citations_df.empty:
        citation_quality['forward_citations'] = {
            'total_count': len(forward_citations_df),
            'unique_citing_apps': forward_citations_df['citing_appln_id'].nunique() if 'citing_appln_id' in forward_citations_df.columns else 0,
            'geographic_diversity': forward_citations_df['citing_country'].nunique() if 'citing_country' in forward_citations_df.columns else 0,
            'temporal_span': analyze_temporal_span(forward_citations_df, 'citing_year')
        }
    
    # Backward citation analysis
    if not backward_citations_df.empty:
        citation_quality['backward_citations'] = {
            'total_count': len(backward_citations_df),
            'unique_cited_apps': backward_citations_df['cited_appln_id'].nunique() if 'cited_appln_id' in backward_citations_df.columns else 0,
            'geographic_diversity': backward_citations_df['cited_country'].nunique() if 'cited_country' in backward_citations_df.columns else 0,
            'temporal_span': analyze_temporal_span(backward_citations_df, 'cited_year')
        }
    
    # Citation balance
    forward_count = len(forward_citations_df)
    backward_count = len(backward_citations_df)
    
    if forward_count > 0 or backward_count > 0:
        citation_quality['citation_balance'] = {
            'forward_count': forward_count,
            'backward_count': backward_count,
            'balance_ratio': float(forward_count / backward_count) if backward_count > 0 else float('inf'),
            'total_citations': forward_count + backward_count
        }
    
    # Citation origin diversity
    all_origins = []
    if not forward_citations_df.empty and 'citn_origin' in forward_citations_df.columns:
        all_origins.extend(forward_citations_df['citn_origin'].tolist())
    if not backward_citations_df.empty and 'citn_origin' in backward_citations_df.columns:
        all_origins.extend(backward_citations_df['citn_origin'].tolist())
    
    if all_origins:
        origin_counts = pd.Series(all_origins).value_counts()
        citation_quality['origin_diversity'] = {
            'unique_origins': len(origin_counts),
            'origin_distribution': origin_counts.to_dict()
        }
    
    # Calculate citation score
    citation_quality['citation_score'] = calculate_citation_score(citation_quality)
    
    return citation_quality

def analyze_geographic_quality(ree_df, geographic_analysis):
    """
    Analyze geographic data quality
    """
    
    geo_quality = {
        'country_coverage': {},
        'collaboration_metrics': {},
        'regional_distribution': {},
        'data_availability': {},
        'geographic_score': 0
    }
    
    if not ree_df.empty:
        # Country coverage
        if 'appln_auth' in ree_df.columns:
            filing_countries = ree_df['appln_auth'].nunique()
            geo_quality['country_coverage']['filing_authorities'] = filing_countries
        
        if 'applicant_countries' in ree_df.columns:
            applicant_coverage = analyze_country_field_coverage(ree_df, 'applicant_countries')
            geo_quality['country_coverage']['applicant_countries'] = applicant_coverage
        
        if 'inventor_countries' in ree_df.columns:
            inventor_coverage = analyze_country_field_coverage(ree_df, 'inventor_countries')
            geo_quality['country_coverage']['inventor_countries'] = inventor_coverage
        
        # Collaboration metrics
        if 'applicant_country_count' in ree_df.columns and 'inventor_country_count' in ree_df.columns:
            multi_app = (ree_df['applicant_country_count'] > 1).sum()
            multi_inv = (ree_df['inventor_country_count'] > 1).sum()
            
            geo_quality['collaboration_metrics'] = {
                'multi_country_applicants': int(multi_app),
                'multi_country_inventors': int(multi_inv),
                'collaboration_rate': float((multi_app + multi_inv) / (2 * len(ree_df)))
            }
        
        # Data availability
        geo_fields = ['applicant_countries', 'inventor_countries', 'applicant_country_names', 'inventor_country_names']
        availability = {}
        
        for field in geo_fields:
            if field in ree_df.columns:
                available_count = ree_df[field].notna().sum()
                availability[field] = float(available_count / len(ree_df))
        
        geo_quality['data_availability'] = availability
        
        # Regional distribution from geographic analysis
        if geographic_analysis and 'regional_patterns' in geographic_analysis:
            geo_quality['regional_distribution'] = geographic_analysis['regional_patterns']
        
        # Calculate geographic score
        geo_quality['geographic_score'] = calculate_geographic_score(geo_quality)
    
    return geo_quality

def calculate_quality_scores(quality_metrics):
    """
    Calculate overall quality scores (0-100 scale)
    """
    
    scores = {
        'dataset_score': 0,
        'coverage_score': 0,
        'citation_score': 0,
        'geographic_score': 0,
        'overall_score': 0
    }
    
    # Dataset score (based on size and completeness)
    overview = quality_metrics.get('dataset_overview', {})
    total_apps = overview.get('total_applications', 0)
    
    dataset_score = 0
    if total_apps >= 1000:
        dataset_score += 40
    elif total_apps >= 500:
        dataset_score += 30
    elif total_apps >= 100:
        dataset_score += 20
    elif total_apps >= 50:
        dataset_score += 10
    
    # Add completeness bonus
    completeness = overview.get('data_completeness', {})
    for field, data in completeness.items():
        if data.get('percentage', 0) > 50:
            dataset_score += 5
    
    scores['dataset_score'] = min(dataset_score, 100)
    
    # Coverage score
    coverage = quality_metrics.get('coverage_metrics', {})
    scores['coverage_score'] = coverage.get('coverage_score', 0)
    
    # Citation score
    citation = quality_metrics.get('citation_metrics', {})
    scores['citation_score'] = citation.get('citation_score', 0)
    
    # Geographic score
    geographic = quality_metrics.get('geographic_metrics', {})
    scores['geographic_score'] = geographic.get('geographic_score', 0)
    
    # Overall score (weighted average)
    weights = {'dataset_score': 0.3, 'coverage_score': 0.2, 'citation_score': 0.3, 'geographic_score': 0.2}
    
    overall_score = sum(scores[key] * weights[key] for key in weights.keys())
    scores['overall_score'] = round(overall_score, 1)
    
    return scores

def assess_business_readiness(quality_metrics):
    """
    Assess readiness for business presentation
    """
    
    overall_score = quality_metrics.get('quality_scores', {}).get('overall_score', 0)
    
    readiness = {
        'overall_score': overall_score,
        'readiness_level': '',
        'presentation_suitability': '',
        'stakeholder_confidence': '',
        'recommended_use_cases': []
    }
    
    if overall_score >= 80:
        readiness['readiness_level'] = 'EXCELLENT'
        readiness['presentation_suitability'] = 'Executive presentations and strategic decision making'
        readiness['stakeholder_confidence'] = 'High - suitable for all stakeholder types'
        readiness['recommended_use_cases'] = [
            'Board presentations',
            'Strategic planning',
            'Investment decisions',
            'Academic research',
            'Policy recommendations'
        ]
    elif overall_score >= 60:
        readiness['readiness_level'] = 'GOOD'
        readiness['presentation_suitability'] = 'Professional analysis and reporting'
        readiness['stakeholder_confidence'] = 'Medium-High - suitable for technical audiences'
        readiness['recommended_use_cases'] = [
            'Technical reports',
            'R&D planning',
            'Market analysis',
            'Academic collaboration'
        ]
    elif overall_score >= 40:
        readiness['readiness_level'] = 'FAIR'
        readiness['presentation_suitability'] = 'Preliminary analysis with caveats'
        readiness['stakeholder_confidence'] = 'Medium - requires quality disclaimers'
        readiness['recommended_use_cases'] = [
            'Initial exploration',
            'Proof of concept',
            'Method development'
        ]
    else:
        readiness['readiness_level'] = 'POOR'
        readiness['presentation_suitability'] = 'Not recommended for business use'
        readiness['stakeholder_confidence'] = 'Low - significant quality concerns'
        readiness['recommended_use_cases'] = [
            'Technical debugging',
            'Method refinement'
        ]
    
    return readiness

def generate_quality_recommendations(quality_metrics):
    """
    Generate specific recommendations for quality improvement
    """
    
    recommendations = []
    
    # Dataset size recommendations
    overview = quality_metrics.get('dataset_overview', {})
    total_apps = overview.get('total_applications', 0)
    
    if total_apps < 100:
        recommendations.append("CRITICAL: Expand dataset size to at least 100 applications for meaningful analysis")
    elif total_apps < 500:
        recommendations.append("Recommend expanding dataset to 500+ applications for robust statistical analysis")
    
    # Coverage recommendations
    coverage = quality_metrics.get('coverage_metrics', {})
    content_coverage = coverage.get('content_coverage', {})
    
    if content_coverage.get('title_coverage', 0) < 0.8:
        recommendations.append("Improve title coverage - currently below 80%")
    
    if content_coverage.get('abstract_coverage', 0) < 0.6:
        recommendations.append("Improve abstract coverage - currently below 60%")
    
    # Citation recommendations
    citation = quality_metrics.get('citation_metrics', {})
    forward_count = citation.get('forward_citations', {}).get('total_count', 0)
    backward_count = citation.get('backward_citations', {}).get('total_count', 0)
    
    if forward_count < 50:
        recommendations.append("Limited forward citations - consider expanding time window or search scope")
    
    if backward_count < 100:
        recommendations.append("Limited backward citations - verify citation linkage methodology")
    
    # Geographic recommendations
    geographic = quality_metrics.get('geographic_metrics', {})
    country_coverage = geographic.get('country_coverage', {})
    
    if country_coverage.get('filing_authorities', 0) < 5:
        recommendations.append("Limited geographic scope - consider expanding to major patent offices")
    
    return recommendations

def print_quality_report(quality_metrics):
    """
    Print comprehensive quality report
    """
    
    print("\n📊 QUALITY ASSESSMENT REPORT")
    print("=" * 60)
    
    # Overview
    overview = quality_metrics.get('dataset_overview', {})
    print(f"📈 Dataset Overview:")
    print(f"   Applications: {overview.get('total_applications', 0):,}")
    print(f"   Families: {overview.get('total_families', 0):,}")
    print(f"   Year Range: {overview.get('year_range', {}).get('min', 'N/A')}-{overview.get('year_range', {}).get('max', 'N/A')}")
    print(f"   Countries: {overview.get('countries_covered', 0)}")
    
    # Quality Scores
    scores = quality_metrics.get('quality_scores', {})
    print(f"\n🎯 Quality Scores:")
    print(f"   Dataset Quality: {scores.get('dataset_score', 0)}/100")
    print(f"   Coverage Quality: {scores.get('coverage_score', 0)}/100")
    print(f"   Citation Quality: {scores.get('citation_score', 0)}/100")
    print(f"   Geographic Quality: {scores.get('geographic_score', 0)}/100")
    print(f"   OVERALL SCORE: {scores.get('overall_score', 0)}/100")
    
    # Business Readiness
    readiness = quality_metrics.get('business_readiness', {})
    print(f"\n💼 Business Readiness: {readiness.get('readiness_level', 'UNKNOWN')}")
    print(f"   Confidence Level: {readiness.get('stakeholder_confidence', 'Unknown')}")
    print(f"   Suitable For: {readiness.get('presentation_suitability', 'Unknown')}")
    
    # Recommendations
    recommendations = quality_metrics.get('recommendations', [])
    if recommendations:
        print(f"\n🔧 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")
    
    print("=" * 60)

# Helper functions
def calculate_distribution_consistency(distribution):
    """Calculate how consistent the distribution is over time"""
    if len(distribution) <= 1:
        return 1.0
    
    mean_val = distribution.mean()
    std_val = distribution.std()
    
    if mean_val == 0:
        return 0.0
    
    coefficient_of_variation = std_val / mean_val
    consistency = max(0, 1 - (coefficient_of_variation / 2))
    
    return consistency

def calculate_coverage_score(coverage):
    """Calculate overall coverage score"""
    score = 0
    
    # Temporal coverage (40 points)
    temporal = coverage.get('temporal_coverage', {})
    years_covered = temporal.get('years_covered', 0)
    if years_covered >= 10:
        score += 40
    elif years_covered >= 5:
        score += 30
    elif years_covered >= 3:
        score += 20
    
    # Geographic coverage (30 points)
    geographic = coverage.get('geographic_coverage', {})
    authorities = geographic.get('authorities_covered', 0)
    if authorities >= 10:
        score += 30
    elif authorities >= 5:
        score += 20
    elif authorities >= 3:
        score += 10
    
    # Content coverage (30 points)
    content = coverage.get('content_coverage', {})
    title_cov = content.get('title_coverage', 0)
    abstract_cov = content.get('abstract_coverage', 0)
    
    if title_cov >= 0.8:
        score += 15
    elif title_cov >= 0.6:
        score += 10
    
    if abstract_cov >= 0.6:
        score += 15
    elif abstract_cov >= 0.4:
        score += 10
    
    return min(score, 100)

def calculate_citation_score(citation_quality):
    """Calculate citation quality score"""
    score = 0
    
    # Forward citations (40 points)
    forward = citation_quality.get('forward_citations', {})
    forward_count = forward.get('total_count', 0)
    if forward_count >= 500:
        score += 40
    elif forward_count >= 200:
        score += 30
    elif forward_count >= 50:
        score += 20
    elif forward_count >= 10:
        score += 10
    
    # Backward citations (30 points)
    backward = citation_quality.get('backward_citations', {})
    backward_count = backward.get('total_count', 0)
    if backward_count >= 1000:
        score += 30
    elif backward_count >= 500:
        score += 25
    elif backward_count >= 100:
        score += 15
    elif backward_count >= 20:
        score += 10
    
    # Citation balance (20 points)
    balance = citation_quality.get('citation_balance', {})
    balance_ratio = balance.get('balance_ratio', 0)
    if 0.5 <= balance_ratio <= 2.0:
        score += 20
    elif 0.2 <= balance_ratio <= 5.0:
        score += 15
    elif balance_ratio > 0:
        score += 10
    
    # Origin diversity (10 points)
    origins = citation_quality.get('origin_diversity', {})
    unique_origins = origins.get('unique_origins', 0)
    if unique_origins >= 3:
        score += 10
    elif unique_origins >= 2:
        score += 5
    
    return min(score, 100)

def calculate_geographic_score(geo_quality):
    """Calculate geographic quality score"""
    score = 0
    
    # Country coverage (50 points)
    coverage = geo_quality.get('country_coverage', {})
    filing_auth = coverage.get('filing_authorities', 0)
    if filing_auth >= 15:
        score += 25
    elif filing_auth >= 10:
        score += 20
    elif filing_auth >= 5:
        score += 15
    
    applicant_countries = coverage.get('applicant_countries', {}).get('unique_countries', 0)
    if applicant_countries >= 20:
        score += 25
    elif applicant_countries >= 10:
        score += 20
    elif applicant_countries >= 5:
        score += 15
    
    # Data availability (30 points)
    availability = geo_quality.get('data_availability', {})
    for field, pct in availability.items():
        if pct >= 0.8:
            score += 7.5
        elif pct >= 0.6:
            score += 5
    
    # Collaboration metrics (20 points)
    collab = geo_quality.get('collaboration_metrics', {})
    collab_rate = collab.get('collaboration_rate', 0)
    if collab_rate >= 0.3:
        score += 20
    elif collab_rate >= 0.2:
        score += 15
    elif collab_rate >= 0.1:
        score += 10
    
    return min(score, 100)

def analyze_temporal_span(df, year_column):
    """Analyze temporal span of citations"""
    if df.empty or year_column not in df.columns:
        return {}
    
    years = df[year_column].dropna()
    if years.empty:
        return {}
    
    return {
        'min_year': int(years.min()),
        'max_year': int(years.max()),
        'span_years': int(years.max() - years.min() + 1)
    }

def analyze_country_field_coverage(df, field):
    """Analyze coverage of country fields"""
    if field not in df.columns:
        return {}
    
    # Count unique countries
    all_countries = set()
    for countries_str in df[field].dropna():
        if isinstance(countries_str, str) and countries_str:
            countries = [c.strip() for c in countries_str.split(';')]
            all_countries.update(countries)
    
    # Data availability
    available_count = df[field].notna().sum()
    total_count = len(df)
    
    return {
        'unique_countries': len(all_countries),
        'data_availability': float(available_count / total_count),
        'coverage_ratio': len(all_countries) / max(available_count, 1)
    }

def export_quality_report(quality_metrics, output_file="quality_report.json"):
    """
    Export quality report to JSON file
    """
    
    try:
        with open(output_file, 'w') as f:
            json.dump(quality_metrics, f, indent=2, default=str)
        print(f"✅ Quality report exported: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Quality report export failed: {e}")
        return False

if __name__ == "__main__":
    from database_connection import get_database_connection
    from dataset_builder import build_ree_dataset
    from citation_analyzer import get_forward_citations, get_backward_citations
    from geographic_enricher import enrich_with_geographic_data, analyze_geographic_patterns
    
    print("DATA VALIDATOR - STANDALONE TEST")
    print("=" * 50)
    
    # Get database connection
    db = get_database_connection()
    if not db:
        print("❌ Database connection failed")
        exit(1)
    
    # Build test dataset
    print("\n📊 Building test dataset...")
    ree_dataset = build_ree_dataset(db, test_mode=True)
    
    if ree_dataset.empty:
        print("❌ No REE dataset available for validation testing")
        exit(1)
    
    # Get citations
    appln_ids = ree_dataset['appln_id'].tolist()[:100]
    
    print(f"\n🔍 Getting citations for {len(appln_ids)} applications...")
    forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
    backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
    
    # Get geographic data
    print("\n🌍 Getting geographic data...")
    enriched_data = enrich_with_geographic_data(db, ree_dataset)
    geographic_analysis = analyze_geographic_patterns(enriched_data)
    
    # Validate quality
    print("\n✅ Running quality validation...")
    quality_report = validate_dataset_quality(enriched_data, forward_cit, backward_cit, geographic_analysis)
    
    # Export report
    export_quality_report(quality_report, "test_quality_report.json")
    
    print(f"\n🎯 Quality validation test complete!")
    print(f"   Overall Score: {quality_report.get('quality_scores', {}).get('overall_score', 0)}/100")
    print(f"   Readiness: {quality_report.get('business_readiness', {}).get('readiness_level', 'UNKNOWN')}")