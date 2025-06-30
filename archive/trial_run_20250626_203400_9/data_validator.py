"""
Data Validator Component for REE Patent Citation Analysis
Quality assurance and business scoring for comprehensive assessment
"""

import pandas as pd
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quality thresholds for business assessment
QUALITY_THRESHOLDS = {
    'excellent': {'min_applications': 1000, 'min_citations': 1000, 'min_countries': 15, 'min_score': 75},
    'good': {'min_applications': 500, 'min_citations': 500, 'min_countries': 10, 'min_score': 60},
    'fair': {'min_applications': 200, 'min_citations': 200, 'min_countries': 5, 'min_score': 40},
    'poor': {'min_applications': 0, 'min_citations': 0, 'min_countries': 0, 'min_score': 0}
}

def validate_dataset_structure(ree_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the structure and completeness of the REE dataset
    """
    validation_results = {
        'structure_valid': True,
        'issues': [],
        'warnings': [],
        'recommendations': []
    }
    
    # Check required columns
    required_columns = ['appln_id', 'docdb_family_id', 'appln_filing_year', 'appln_auth']
    missing_columns = [col for col in required_columns if col not in ree_df.columns]
    
    if missing_columns:
        validation_results['structure_valid'] = False
        validation_results['issues'].append(f"Missing required columns: {missing_columns}")
    
    # Check for empty dataset
    if ree_df.empty:
        validation_results['structure_valid'] = False
        validation_results['issues'].append("Dataset is empty")
        return validation_results
    
    # Check data types and ranges
    if 'appln_filing_year' in ree_df.columns:
        year_range = ree_df['appln_filing_year'].dropna()
        if not year_range.empty:
            min_year, max_year = year_range.min(), year_range.max()
            if min_year < 1990 or max_year > datetime.now().year:
                validation_results['warnings'].append(f"Unusual year range: {min_year}-{max_year}")
    
    # Check for duplicate applications
    if 'appln_id' in ree_df.columns:
        duplicates = ree_df['appln_id'].duplicated().sum()
        if duplicates > 0:
            validation_results['warnings'].append(f"{duplicates} duplicate application IDs found")
    
    # Check content completeness
    if 'appln_title' in ree_df.columns:
        missing_titles = ree_df['appln_title'].isna().sum()
        title_completeness = (len(ree_df) - missing_titles) / len(ree_df) * 100
        if title_completeness < 80:
            validation_results['warnings'].append(f"Title completeness: {title_completeness:.1f}%")
    
    if 'appln_abstract' in ree_df.columns:
        missing_abstracts = ree_df['appln_abstract'].isna().sum()
        abstract_completeness = (len(ree_df) - missing_abstracts) / len(ree_df) * 100
        if abstract_completeness < 60:
            validation_results['warnings'].append(f"Abstract completeness: {abstract_completeness:.1f}%")
    
    logger.info(f"✅ Dataset structure validation: {'PASSED' if validation_results['structure_valid'] else 'FAILED'}")
    if validation_results['warnings']:
        logger.warning(f"Warnings: {len(validation_results['warnings'])}")
    
    return validation_results

def validate_citation_data(forward_citations: pd.DataFrame, backward_citations: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate citation data quality and completeness
    """
    citation_validation = {
        'forward_citations_valid': True,
        'backward_citations_valid': True,
        'issues': [],
        'warnings': []
    }
    
    # Validate forward citations
    if not forward_citations.empty:
        required_forward_cols = ['citing_appln_id', 'cited_ree_appln_id', 'citn_origin']
        missing_forward = [col for col in required_forward_cols if col not in forward_citations.columns]
        
        if missing_forward:
            citation_validation['forward_citations_valid'] = False
            citation_validation['issues'].append(f"Missing forward citation columns: {missing_forward}")
        
        # Check citation origins
        if 'citn_origin' in forward_citations.columns:
            null_origins = forward_citations['citn_origin'].isna().sum()
            if null_origins > 0:
                citation_validation['warnings'].append(f"{null_origins} forward citations with null origins")
    
    # Validate backward citations
    if not backward_citations.empty:
        required_backward_cols = ['ree_appln_id', 'cited_appln_id', 'citn_origin']
        missing_backward = [col for col in required_backward_cols if col not in backward_citations.columns]
        
        if missing_backward:
            citation_validation['backward_citations_valid'] = False
            citation_validation['issues'].append(f"Missing backward citation columns: {missing_backward}")
    
    # Cross-validation
    if not forward_citations.empty and not backward_citations.empty:
        if 'cited_ree_appln_id' in forward_citations.columns and 'ree_appln_id' in backward_citations.columns:
            forward_apps = set(forward_citations['cited_ree_appln_id'].dropna())
            backward_apps = set(backward_citations['ree_appln_id'].dropna())
            
            overlap = len(forward_apps.intersection(backward_apps))
            if overlap == 0:
                citation_validation['warnings'].append("No overlap between forward and backward citation applications")
    
    logger.info(f"✅ Citation validation: Forward {'PASSED' if citation_validation['forward_citations_valid'] else 'FAILED'}, Backward {'PASSED' if citation_validation['backward_citations_valid'] else 'FAILED'}")
    
    return citation_validation

def validate_geographic_data(enriched_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate geographic enrichment quality
    """
    geo_validation = {
        'geographic_data_valid': True,
        'issues': [],
        'warnings': [],
        'coverage_stats': {}
    }
    
    if enriched_df.empty:
        geo_validation['geographic_data_valid'] = False
        geo_validation['issues'].append("No geographic data to validate")
        return geo_validation
    
    # Check geographic coverage
    if 'person_ctry_code' in enriched_df.columns:
        total_apps = enriched_df['appln_id'].nunique()
        apps_with_geo = enriched_df[enriched_df['person_ctry_code'].notna()]['appln_id'].nunique()
        geo_coverage = apps_with_geo / total_apps * 100 if total_apps > 0 else 0
        
        geo_validation['coverage_stats']['geographic_coverage'] = geo_coverage
        
        if geo_coverage < 70:
            geo_validation['warnings'].append(f"Low geographic coverage: {geo_coverage:.1f}%")
        
        # Country diversity check
        unique_countries = enriched_df['person_ctry_code'].nunique()
        geo_validation['coverage_stats']['unique_countries'] = unique_countries
        
        if unique_countries < 5:
            geo_validation['warnings'].append(f"Limited country diversity: {unique_countries} countries")
    
    # Check strategic classifications
    strategic_cols = [col for col in enriched_df.columns if col.startswith('is_')]
    if not strategic_cols:
        geo_validation['warnings'].append("No strategic country classifications found")
    
    # Regional distribution check
    if 'region' in enriched_df.columns:
        unique_regions = enriched_df['region'].nunique()
        geo_validation['coverage_stats']['unique_regions'] = unique_regions
        
        if unique_regions < 3:
            geo_validation['warnings'].append(f"Limited regional diversity: {unique_regions} regions")
    
    logger.info(f"✅ Geographic validation: {'PASSED' if geo_validation['geographic_data_valid'] else 'FAILED'}")
    
    return geo_validation

def calculate_overall_quality_score(ree_df: pd.DataFrame, citation_metrics: Dict[str, Any], geo_intelligence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate comprehensive quality score for business assessment (0-100)
    """
    quality_assessment = {
        'overall_score': 0,
        'component_scores': {},
        'business_assessment': '',
        'recommendations': []
    }
    
    # Dataset quality score (25 points max)
    dataset_score = 0
    if not ree_df.empty:
        app_count = len(ree_df)
        family_count = ree_df['docdb_family_id'].nunique() if 'docdb_family_id' in ree_df.columns else app_count
        
        # Application volume (15 points)
        if app_count >= 1000: dataset_score += 15
        elif app_count >= 500: dataset_score += 12
        elif app_count >= 200: dataset_score += 9
        elif app_count >= 100: dataset_score += 6
        elif app_count >= 50: dataset_score += 3
        
        # Innovation diversity (10 points)
        family_ratio = family_count / app_count if app_count > 0 else 0
        if family_ratio >= 0.8: dataset_score += 10
        elif family_ratio >= 0.6: dataset_score += 8
        elif family_ratio >= 0.4: dataset_score += 6
        elif family_ratio >= 0.2: dataset_score += 4
    
    quality_assessment['component_scores']['dataset_quality'] = dataset_score
    
    # Citation quality score (35 points max)
    citation_score = citation_metrics.get('citation_intensity_score', 0) * 0.35
    quality_assessment['component_scores']['citation_quality'] = int(citation_score)
    
    # Geographic quality score (25 points max)
    geo_score = geo_intelligence.get('diversity_score', 0) * 0.25
    quality_assessment['component_scores']['geographic_quality'] = int(geo_score)
    
    # Data completeness score (15 points max)
    completeness_score = 0
    if not ree_df.empty:
        # Title completeness (5 points)
        if 'appln_title' in ree_df.columns:
            title_completeness = (ree_df['appln_title'].notna().sum() / len(ree_df))
            completeness_score += title_completeness * 5
        
        # Abstract completeness (5 points)
        if 'appln_abstract' in ree_df.columns:
            abstract_completeness = (ree_df['appln_abstract'].notna().sum() / len(ree_df))
            completeness_score += abstract_completeness * 5
        
        # Geographic completeness (5 points)
        if 'person_ctry_code' in ree_df.columns:
            geo_completeness = (ree_df['person_ctry_code'].notna().sum() / len(ree_df))
            completeness_score += geo_completeness * 5
    
    quality_assessment['component_scores']['data_completeness'] = int(completeness_score)
    
    # Calculate overall score
    overall_score = (
        dataset_score + 
        citation_score + 
        geo_score + 
        completeness_score
    )
    quality_assessment['overall_score'] = min(int(overall_score), 100)
    
    # Business assessment
    score = quality_assessment['overall_score']
    if score >= QUALITY_THRESHOLDS['excellent']['min_score']:
        quality_assessment['business_assessment'] = 'EXCELLENT'
        quality_assessment['recommendations'].append("Dataset exceeds professional standards - ready for executive presentation")
    elif score >= QUALITY_THRESHOLDS['good']['min_score']:
        quality_assessment['business_assessment'] = 'GOOD'
        quality_assessment['recommendations'].append("Dataset meets business analysis requirements")
    elif score >= QUALITY_THRESHOLDS['fair']['min_score']:
        quality_assessment['business_assessment'] = 'FAIR'
        quality_assessment['recommendations'].append("Dataset usable but consider expanding scope for better insights")
    else:
        quality_assessment['business_assessment'] = 'POOR'
        quality_assessment['recommendations'].append("Recommend adjusting search strategy to improve data quality")
    
    return quality_assessment

def generate_data_quality_report(ree_df: pd.DataFrame, forward_citations: pd.DataFrame, 
                                backward_citations: pd.DataFrame, citation_metrics: Dict[str, Any],
                                geo_intelligence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate comprehensive data quality report
    """
    logger.info("🔍 GENERATING COMPREHENSIVE DATA QUALITY REPORT")
    logger.info("=" * 60)
    
    # Structure validation
    structure_validation = validate_dataset_structure(ree_df)
    
    # Citation validation
    citation_validation = validate_citation_data(forward_citations, backward_citations)
    
    # Geographic validation
    geographic_validation = validate_geographic_data(ree_df)
    
    # Overall quality assessment
    quality_assessment = calculate_overall_quality_score(ree_df, citation_metrics, geo_intelligence)
    
    # Compile comprehensive report
    quality_report = {
        'validation_results': {
            'structure_validation': structure_validation,
            'citation_validation': citation_validation,
            'geographic_validation': geographic_validation
        },
        'quality_assessment': quality_assessment,
        'dataset_statistics': {
            'total_applications': len(ree_df) if not ree_df.empty else 0,
            'total_families': ree_df['docdb_family_id'].nunique() if 'docdb_family_id' in ree_df.columns else 0,
            'forward_citations': len(forward_citations),
            'backward_citations': len(backward_citations),
            'countries_covered': ree_df['person_ctry_code'].nunique() if 'person_ctry_code' in ree_df.columns else 0,
            'year_range': f"{ree_df['appln_filing_year'].min()}-{ree_df['appln_filing_year'].max()}" if 'appln_filing_year' in ree_df.columns and not ree_df.empty else "N/A"
        },
        'business_readiness': {
            'ready_for_analysis': quality_assessment['overall_score'] >= 40,
            'ready_for_presentation': quality_assessment['overall_score'] >= 60,
            'ready_for_executive_review': quality_assessment['overall_score'] >= 75
        }
    }
    
    # Log summary
    logger.info("DATA QUALITY ASSESSMENT COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Overall Quality Score: {quality_assessment['overall_score']}/100")
    logger.info(f"Business Assessment: {quality_assessment['business_assessment']}")
    logger.info(f"Applications: {quality_report['dataset_statistics']['total_applications']:,}")
    logger.info(f"Citations: {quality_report['dataset_statistics']['forward_citations'] + quality_report['dataset_statistics']['backward_citations']:,}")
    logger.info(f"Countries: {quality_report['dataset_statistics']['countries_covered']}")
    
    for assessment, ready in quality_report['business_readiness'].items():
        status = "✅ READY" if ready else "❌ NOT READY"
        logger.info(f"{assessment}: {status}")
    
    return quality_report

def validate_dataset_quality(ree_df: pd.DataFrame, forward_citations: pd.DataFrame, 
                           backward_citations: pd.DataFrame, citation_metrics: Dict[str, Any] = None,
                           geo_intelligence: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Comprehensive quality assessment with business scoring
    Main entry point for data validation
    """
    # Default empty dicts if not provided
    citation_metrics = citation_metrics or {}
    geo_intelligence = geo_intelligence or {}
    
    # Generate comprehensive quality report
    quality_report = generate_data_quality_report(
        ree_df, forward_citations, backward_citations, 
        citation_metrics, geo_intelligence
    )
    
    return quality_report

if __name__ == "__main__":
    # Test the data validator
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    from citation_analyzer import perform_complete_citation_analysis
    from geographic_enricher import perform_complete_geographic_analysis
    
    logger.info("Testing Data Validator...")
    
    # Get database connection
    db = test_tip_connection()
    if not db:
        logger.error("Cannot test data validator without database connection")
        exit(1)
    
    # Build test dataset
    ree_data = build_ree_dataset(db, test_mode=True)
    if ree_data.empty:
        logger.error("Cannot test data validator without REE dataset")
        exit(1)
    
    # Perform citation analysis
    appln_ids = ree_data['appln_id'].tolist()[:50]  # Test with smaller subset
    citation_results = perform_complete_citation_analysis(db, appln_ids, ree_data, test_mode=True)
    
    # Perform geographic analysis
    geo_results = perform_complete_geographic_analysis(db, ree_data)
    
    # Validate data quality
    quality_report = validate_dataset_quality(
        geo_results['enriched_dataset'],
        citation_results['forward_citations'],
        citation_results['backward_citations'],
        citation_results['citation_metrics'],
        geo_results['intelligence_report']
    )
    
    print("\n" + "="*80)
    print("DATA VALIDATOR TEST COMPLETE")
    print("="*80)
    
    if quality_report:
        assessment = quality_report['quality_assessment']
        stats = quality_report['dataset_statistics']
        readiness = quality_report['business_readiness']
        
        print(f"✅ Quality Score: {assessment['overall_score']}/100")
        print(f"✅ Assessment: {assessment['business_assessment']}")
        print(f"✅ Applications: {stats['total_applications']:,}")
        print(f"✅ Citations: {stats['forward_citations'] + stats['backward_citations']:,}")
        print(f"✅ Countries: {stats['countries_covered']}")
        print(f"✅ Ready for analysis: {'YES' if readiness['ready_for_analysis'] else 'NO'}")
        print("✅ Ready for integrated pipeline")
    else:
        print("❌ Data validation failed")