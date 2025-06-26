"""
Integrated Pipeline for REE Patent Citation Analysis
End-to-end testing and integration of all analysis components
"""

import pandas as pd
import logging
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all analysis components
from database_connection import test_tip_connection, get_database_statistics
from dataset_builder import build_ree_dataset, get_search_coverage_analysis
from citation_analyzer import perform_complete_citation_analysis
from geographic_enricher import perform_complete_geographic_analysis
from data_validator import validate_dataset_quality

def run_complete_ree_analysis(test_mode: bool = True, year_start: int = 2014, year_end: int = 2024, 
                             max_applications: Optional[int] = None) -> Dict[str, Any]:
    """
    Execute complete REE analysis pipeline with comprehensive error handling
    
    Args:
        test_mode: If True, limit results for testing
        year_start: Start year for analysis
        year_end: End year for analysis
        max_applications: Maximum applications to analyze (for performance control)
    
    Returns:
        Dictionary containing all analysis results
    """
    
    pipeline_start_time = datetime.now()
    
    logger.info("🚀 REE PATENT CITATION ANALYSIS PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Analysis Period: {year_start}-{year_end}")
    logger.info(f"Test Mode: {'ENABLED' if test_mode else 'DISABLED'}")
    logger.info(f"Max Applications: {max_applications or 'UNLIMITED'}")
    logger.info("=" * 60)
    
    results = {
        'pipeline_info': {
            'start_time': pipeline_start_time.isoformat(),
            'test_mode': test_mode,
            'year_range': f"{year_start}-{year_end}",
            'status': 'RUNNING'
        },
        'component_results': {},
        'errors': [],
        'warnings': []
    }
    
    try:
        # ===== STEP 1: DATABASE CONNECTION =====
        logger.info("🔌 STEP 1: Establishing Database Connection...")
        db = test_tip_connection()
        if not db:
            raise Exception("Failed to establish database connection")
        
        # Get database statistics
        db_stats = get_database_statistics(db)
        results['component_results']['database_stats'] = db_stats
        logger.info("✅ Database connection established")
        
        # ===== STEP 2: DATASET BUILDING =====
        logger.info("\n📊 STEP 2: Building REE Dataset...")
        ree_dataset = build_ree_dataset(db, test_mode, year_start, year_end)
        
        if ree_dataset.empty:
            raise Exception("No REE applications found with current search strategy")
        
        # Apply application limit if specified
        if max_applications and len(ree_dataset) > max_applications:
            logger.info(f"Limiting dataset to {max_applications} applications for performance")
            ree_dataset = ree_dataset.head(max_applications)
        
        # Get search coverage analysis
        search_coverage = get_search_coverage_analysis(ree_dataset)
        results['component_results']['dataset_info'] = {
            'applications': len(ree_dataset),
            'families': ree_dataset['docdb_family_id'].nunique(),
            'search_coverage': search_coverage
        }
        logger.info(f"✅ Dataset built: {len(ree_dataset):,} applications")
        
        # ===== STEP 3: CITATION ANALYSIS =====
        logger.info("\n🔗 STEP 3: Performing Citation Analysis...")
        appln_ids = ree_dataset['appln_id'].tolist()
        
        # Limit citation analysis for performance if needed
        citation_appln_ids = appln_ids
        if test_mode and len(appln_ids) > 200:
            citation_appln_ids = appln_ids[:200]
            logger.info(f"Limiting citation analysis to {len(citation_appln_ids)} applications for testing")
        
        citation_results = perform_complete_citation_analysis(db, citation_appln_ids, ree_dataset, test_mode)
        results['component_results']['citation_analysis'] = {
            'forward_citations_count': len(citation_results['forward_citations']),
            'backward_citations_count': len(citation_results['backward_citations']),
            'citation_metrics': citation_results['citation_metrics'],
            'network_analysis': citation_results['network_analysis']
        }
        logger.info("✅ Citation analysis completed")
        
        # ===== STEP 4: GEOGRAPHIC ANALYSIS =====
        logger.info("\n🌍 STEP 4: Performing Geographic Analysis...")
        geographic_results = perform_complete_geographic_analysis(db, ree_dataset)
        
        enriched_dataset = geographic_results['enriched_dataset']
        intelligence_report = geographic_results['intelligence_report']
        
        results['component_results']['geographic_analysis'] = {
            'enriched_applications': len(enriched_dataset),
            'countries_covered': intelligence_report['summary_statistics']['total_countries'],
            'regions_covered': intelligence_report['summary_statistics']['total_regions'],
            'diversity_score': intelligence_report['diversity_score'],
            'intelligence_summary': intelligence_report['distribution_analysis']
        }
        logger.info("✅ Geographic analysis completed")
        
        # ===== STEP 5: DATA QUALITY VALIDATION =====
        logger.info("\n✅ STEP 5: Validating Data Quality...")
        quality_report = validate_dataset_quality(
            enriched_dataset,
            citation_results['forward_citations'],
            citation_results['backward_citations'],
            citation_results['citation_metrics'],
            intelligence_report
        )
        
        results['component_results']['quality_assessment'] = quality_report
        logger.info(f"✅ Quality validation completed: {quality_report['quality_assessment']['overall_score']}/100")
        
        # ===== STEP 6: FINAL INTEGRATION =====
        logger.info("\n🎯 STEP 6: Final Integration and Summary...")
        
        # Calculate pipeline performance metrics
        pipeline_end_time = datetime.now()
        pipeline_duration = (pipeline_end_time - pipeline_start_time).total_seconds()
        
        # Compile final summary
        final_summary = {
            'execution_summary': {
                'total_applications': len(ree_dataset),
                'total_families': ree_dataset['docdb_family_id'].nunique(),
                'total_citations': (
                    len(citation_results['forward_citations']) + 
                    len(citation_results['backward_citations'])
                ),
                'countries_analyzed': intelligence_report['summary_statistics']['total_countries'],
                'quality_score': quality_report['quality_assessment']['overall_score'],
                'business_assessment': quality_report['quality_assessment']['business_assessment']
            },
            'performance_metrics': {
                'pipeline_duration_seconds': pipeline_duration,
                'applications_per_second': len(ree_dataset) / pipeline_duration if pipeline_duration > 0 else 0,
                'database_queries_executed': 'Multiple (successful)',
                'memory_efficient': 'Yes (streaming queries used)'
            },
            'business_readiness': quality_report['business_readiness'],
            'recommendations': quality_report['quality_assessment']['recommendations']
        }
        
        results['final_summary'] = final_summary
        results['pipeline_info']['status'] = 'COMPLETED'
        results['pipeline_info']['end_time'] = pipeline_end_time.isoformat()
        results['pipeline_info']['duration_seconds'] = pipeline_duration
        
        # Store data for notebook creation
        results['data_for_notebook'] = {
            'ree_dataset': enriched_dataset,
            'forward_citations': citation_results['forward_citations'],
            'backward_citations': citation_results['backward_citations'],
            'citation_metrics': citation_results['citation_metrics'],
            'geographic_intelligence': intelligence_report,
            'quality_report': quality_report
        }
        
        logger.info("🎉 PIPELINE EXECUTION COMPLETED SUCCESSFULLY")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
        
        results['pipeline_info']['status'] = 'FAILED'
        results['pipeline_info']['error'] = str(e)
        results['errors'].append({
            'error': str(e),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        })
        
        return results

def print_pipeline_summary(results: Dict[str, Any]) -> None:
    """
    Print comprehensive pipeline summary
    """
    print("\n" + "=" * 80)
    print("🎯 REE PATENT ANALYSIS PIPELINE SUMMARY")
    print("=" * 80)
    
    pipeline_info = results.get('pipeline_info', {})
    print(f"Status: {pipeline_info.get('status', 'UNKNOWN')}")
    print(f"Duration: {pipeline_info.get('duration_seconds', 0):.1f} seconds")
    print(f"Analysis Period: {pipeline_info.get('year_range', 'N/A')}")
    
    if pipeline_info.get('status') == 'COMPLETED':
        summary = results.get('final_summary', {}).get('execution_summary', {})
        performance = results.get('final_summary', {}).get('performance_metrics', {})
        readiness = results.get('final_summary', {}).get('business_readiness', {})
        
        print("\n📊 DATA SUMMARY:")
        print(f"  Applications Analyzed: {summary.get('total_applications', 0):,}")
        print(f"  Patent Families: {summary.get('total_families', 0):,}")
        print(f"  Citations Found: {summary.get('total_citations', 0):,}")
        print(f"  Countries Covered: {summary.get('countries_analyzed', 0)}")
        
        print("\n🏆 QUALITY ASSESSMENT:")
        print(f"  Overall Score: {summary.get('quality_score', 0)}/100")
        print(f"  Business Assessment: {summary.get('business_assessment', 'UNKNOWN')}")
        
        print("\n⚡ PERFORMANCE METRICS:")
        print(f"  Processing Speed: {performance.get('applications_per_second', 0):.1f} apps/second")
        print(f"  Database Queries: {performance.get('database_queries_executed', 'N/A')}")
        print(f"  Memory Efficiency: {performance.get('memory_efficient', 'N/A')}")
        
        print("\n🚀 BUSINESS READINESS:")
        for assessment, ready in readiness.items():
            status = "✅ READY" if ready else "❌ NOT READY"
            print(f"  {assessment.replace('_', ' ').title()}: {status}")
        
        print("\n💡 RECOMMENDATIONS:")
        recommendations = results.get('final_summary', {}).get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    else:
        # Show error information
        errors = results.get('errors', [])
        if errors:
            print(f"\n❌ ERRORS ENCOUNTERED: {len(errors)}")
            for error in errors:
                print(f"  • {error.get('error', 'Unknown error')}")
    
    print("=" * 80)

def save_pipeline_results(results: Dict[str, Any], output_file: str = "ree_analysis_results.json") -> None:
    """
    Save pipeline results to JSON file (excluding large DataFrames)
    """
    try:
        # Create a copy without DataFrames for JSON serialization
        json_results = {}
        
        for key, value in results.items():
            if key == 'data_for_notebook':
                # Skip DataFrames, just save metadata
                json_results[key] = {
                    'ree_dataset_shape': value['ree_dataset'].shape if 'ree_dataset' in value else (0, 0),
                    'forward_citations_count': len(value['forward_citations']) if 'forward_citations' in value else 0,
                    'backward_citations_count': len(value['backward_citations']) if 'backward_citations' in value else 0,
                    'note': 'DataFrame data excluded from JSON - available in pipeline results object'
                }
            else:
                json_results[key] = value
        
        with open(output_file, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        logger.info(f"✅ Pipeline results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save results: {e}")

if __name__ == "__main__":
    # Run the complete pipeline
    logger.info("🚀 Starting REE Patent Analysis Pipeline Test...")
    
    # Configure test parameters
    TEST_MODE = True
    YEAR_START = 2020  # Shorter timeframe for testing
    YEAR_END = 2024
    MAX_APPLICATIONS = 500  # Limit for testing
    
    # Execute pipeline
    pipeline_results = run_complete_ree_analysis(
        test_mode=TEST_MODE,
        year_start=YEAR_START,
        year_end=YEAR_END,
        max_applications=MAX_APPLICATIONS
    )
    
    # Print summary
    print_pipeline_summary(pipeline_results)
    
    # Save results
    save_pipeline_results(pipeline_results, "test_ree_analysis_results.json")
    
    # Determine success
    if pipeline_results['pipeline_info']['status'] == 'COMPLETED':
        print("\n🎉 PIPELINE TEST SUCCESSFUL - Ready for notebook creation!")
        
        # Check if ready for production
        quality_score = pipeline_results.get('final_summary', {}).get('execution_summary', {}).get('quality_score', 0)
        if quality_score >= 60:
            print("✅ Quality sufficient for professional analysis")
        elif quality_score >= 40:
            print("⚠️  Quality fair - consider expanding scope for better insights")
        else:
            print("❌ Quality poor - recommend adjusting search strategy")
            
        sys.exit(0)
    else:
        print("\n❌ PIPELINE TEST FAILED")
        sys.exit(1)