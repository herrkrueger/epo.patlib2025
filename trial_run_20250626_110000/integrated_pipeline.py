"""
Integrated Pipeline for REE Patent Citation Analysis
Complete workflow orchestration for professional patent intelligence
"""

import pandas as pd
import json
from datetime import datetime
import traceback
import sys
import os

# Import all components
from database_connection import get_database_connection
from dataset_builder import build_ree_dataset, enrich_dataset_with_titles_abstracts
from citation_analyzer import get_forward_citations, get_backward_citations, analyze_citation_patterns, calculate_citation_metrics
from geographic_enricher import enrich_with_geographic_data, analyze_geographic_patterns
from data_validator import validate_dataset_quality, export_quality_report

def run_complete_ree_analysis(test_mode=True, output_prefix="ree_analysis"):
    """
    Complete REE patent citation analysis pipeline
    
    Args:
        test_mode: If True, limits dataset size for faster execution
        output_prefix: Prefix for all output files
    
    Returns:
        Dictionary with all analysis results and quality metrics
    """
    
    print("🚀 REE PATENT CITATION ANALYSIS PIPELINE")
    print("=" * 60)
    print(f"Mode: {'TEST' if test_mode else 'FULL PRODUCTION'}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    pipeline_results = {
        'metadata': {
            'execution_time': datetime.now().isoformat(),
            'test_mode': test_mode,
            'pipeline_version': '1.0',
            'components_executed': []
        },
        'dataset': None,
        'citations': {
            'forward': None,
            'backward': None,
            'patterns': None,
            'metrics': None
        },
        'geographic': {
            'enriched_data': None,
            'analysis': None
        },
        'quality': None,
        'exports': {
            'files_created': [],
            'total_size_mb': 0
        },
        'summary': {}
    }
    
    try:
        # Step 1: Database Connection
        print("\n🔌 STEP 1: DATABASE CONNECTION")
        print("-" * 40)
        
        db = get_database_connection()
        if not db:
            raise Exception("Database connection failed - cannot proceed")
        
        pipeline_results['metadata']['components_executed'].append('database_connection')
        print("✅ Database connection established")
        
        # Step 2: Dataset Building
        print("\n📊 STEP 2: REE DATASET CONSTRUCTION")
        print("-" * 40)
        
        ree_dataset = build_ree_dataset(db, test_mode)
        if ree_dataset.empty:
            raise Exception("No REE dataset created - check search parameters")
        
        # Enrich with full title/abstract data
        enriched_dataset = enrich_dataset_with_titles_abstracts(db, ree_dataset)
        pipeline_results['dataset'] = enriched_dataset
        pipeline_results['metadata']['components_executed'].append('dataset_builder')
        
        print(f"✅ Dataset created: {len(enriched_dataset)} REE applications")
        
        # Step 3: Citation Analysis
        print("\n🔍 STEP 3: CITATION INTELLIGENCE")
        print("-" * 40)
        
        appln_ids = enriched_dataset['appln_id'].tolist()
        
        # Forward citations
        print("Analyzing forward citations...")
        forward_citations = get_forward_citations(db, appln_ids, test_mode)
        pipeline_results['citations']['forward'] = forward_citations
        
        # Backward citations
        print("Analyzing backward citations...")
        backward_citations = get_backward_citations(db, appln_ids, test_mode)
        pipeline_results['citations']['backward'] = backward_citations
        
        # Citation patterns
        print("Analyzing citation patterns...")
        citation_patterns = analyze_citation_patterns(forward_citations, backward_citations)
        pipeline_results['citations']['patterns'] = citation_patterns
        
        # Citation metrics
        print("Calculating citation metrics...")
        citation_metrics = calculate_citation_metrics(enriched_dataset, forward_citations, backward_citations)
        pipeline_results['citations']['metrics'] = citation_metrics
        
        pipeline_results['metadata']['components_executed'].append('citation_analyzer')
        print(f"✅ Citation analysis complete")
        print(f"   Forward: {len(forward_citations)}, Backward: {len(backward_citations)}")
        
        # Step 4: Geographic Intelligence
        print("\n🌍 STEP 4: GEOGRAPHIC INTELLIGENCE")
        print("-" * 40)
        
        # Geographic enrichment
        print("Enriching with geographic data...")
        geo_enriched_data = enrich_with_geographic_data(db, enriched_dataset)
        pipeline_results['geographic']['enriched_data'] = geo_enriched_data
        
        # Geographic analysis
        print("Analyzing geographic patterns...")
        geographic_analysis = analyze_geographic_patterns(geo_enriched_data)
        pipeline_results['geographic']['analysis'] = geographic_analysis
        
        pipeline_results['metadata']['components_executed'].append('geographic_enricher')
        print(f"✅ Geographic analysis complete")
        print(f"   Countries: {len(geographic_analysis.get('applicant_countries', {}))}")
        
        # Step 5: Quality Validation
        print("\n✅ STEP 5: QUALITY VALIDATION")
        print("-" * 40)
        
        quality_metrics = validate_dataset_quality(
            geo_enriched_data, 
            forward_citations, 
            backward_citations, 
            geographic_analysis
        )
        pipeline_results['quality'] = quality_metrics
        pipeline_results['metadata']['components_executed'].append('data_validator')
        
        overall_score = quality_metrics.get('quality_scores', {}).get('overall_score', 0)
        readiness_level = quality_metrics.get('business_readiness', {}).get('readiness_level', 'UNKNOWN')
        
        print(f"✅ Quality validation complete")
        print(f"   Overall Score: {overall_score}/100")
        print(f"   Readiness: {readiness_level}")
        
        # Step 6: Export Results
        print("\n💾 STEP 6: EXPORTING RESULTS")
        print("-" * 40)
        
        export_summary = export_pipeline_results(pipeline_results, output_prefix)
        pipeline_results['exports'] = export_summary
        
        print(f"✅ Export complete: {len(export_summary['files_created'])} files")
        
        # Step 7: Generate Summary
        print("\n📋 STEP 7: GENERATING SUMMARY")
        print("-" * 40)
        
        summary = generate_pipeline_summary(pipeline_results)
        pipeline_results['summary'] = summary
        
        print("✅ Summary generated")
        
        # Final Report
        print("\n" + "=" * 60)
        print("🎯 PIPELINE EXECUTION COMPLETE")
        print("=" * 60)
        
        print_pipeline_summary(summary)
        
        return pipeline_results
        
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        print(f"Error details: {traceback.format_exc()}")
        
        # Record failure
        pipeline_results['metadata']['error'] = str(e)
        pipeline_results['metadata']['error_details'] = traceback.format_exc()
        
        return pipeline_results

def export_pipeline_results(pipeline_results, output_prefix):
    """
    Export all pipeline results to files
    """
    
    export_summary = {
        'files_created': [],
        'total_size_mb': 0
    }
    
    try:
        # Export main dataset
        if pipeline_results['dataset'] is not None and not pipeline_results['dataset'].empty:
            dataset_file = f"{output_prefix}_dataset.csv"
            pipeline_results['dataset'].to_csv(dataset_file, index=False)
            export_summary['files_created'].append(dataset_file)
        
        # Export geographic enriched data
        geo_data = pipeline_results['geographic']['enriched_data']
        if geo_data is not None and not geo_data.empty:
            geo_file = f"{output_prefix}_geographic.csv"
            geo_data.to_csv(geo_file, index=False)
            export_summary['files_created'].append(geo_file)
        
        # Export forward citations
        forward_cit = pipeline_results['citations']['forward']
        if forward_cit is not None and not forward_cit.empty:
            forward_file = f"{output_prefix}_forward_citations.csv"
            forward_cit.to_csv(forward_file, index=False)
            export_summary['files_created'].append(forward_file)
        
        # Export backward citations
        backward_cit = pipeline_results['citations']['backward']
        if backward_cit is not None and not backward_cit.empty:
            backward_file = f"{output_prefix}_backward_citations.csv"
            backward_cit.to_csv(backward_file, index=False)
            export_summary['files_created'].append(backward_file)
        
        # Export citation metrics
        cit_metrics = pipeline_results['citations']['metrics']
        if cit_metrics is not None and not cit_metrics.empty:
            metrics_file = f"{output_prefix}_citation_metrics.csv"
            cit_metrics.to_csv(metrics_file, index=False)
            export_summary['files_created'].append(metrics_file)
        
        # Export geographic analysis (JSON)
        geo_analysis = pipeline_results['geographic']['analysis']
        if geo_analysis:
            geo_analysis_file = f"{output_prefix}_geographic_analysis.json"
            with open(geo_analysis_file, 'w') as f:
                json.dump(geo_analysis, f, indent=2, default=str)
            export_summary['files_created'].append(geo_analysis_file)
        
        # Export citation patterns (JSON)
        cit_patterns = pipeline_results['citations']['patterns']
        if cit_patterns:
            patterns_file = f"{output_prefix}_citation_patterns.json"
            with open(patterns_file, 'w') as f:
                json.dump(cit_patterns, f, indent=2, default=str)
            export_summary['files_created'].append(patterns_file)
        
        # Export quality report
        quality_metrics = pipeline_results['quality']
        if quality_metrics:
            quality_file = f"{output_prefix}_quality_report.json"
            export_quality_report(quality_metrics, quality_file)
            export_summary['files_created'].append(quality_file)
        
        # Export complete pipeline results
        pipeline_file = f"{output_prefix}_complete_results.json"
        with open(pipeline_file, 'w') as f:
            # Create a serializable version
            serializable_results = make_serializable(pipeline_results)
            json.dump(serializable_results, f, indent=2, default=str)
        export_summary['files_created'].append(pipeline_file)
        
        # Calculate total file size
        total_size = 0
        for file_path in export_summary['files_created']:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
        
        export_summary['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        print(f"✅ Exported {len(export_summary['files_created'])} files ({export_summary['total_size_mb']} MB)")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    return export_summary

def make_serializable(obj):
    """
    Convert pandas DataFrames and other non-serializable objects to serializable format
    """
    
    if isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, pd.DataFrame):
        if obj.empty:
            return None
        return {
            'type': 'DataFrame',
            'shape': obj.shape,
            'columns': list(obj.columns),
            'sample_data': obj.head(3).to_dict('records') if len(obj) > 0 else []
        }
    elif pd.isna(obj):
        return None
    else:
        return obj

def generate_pipeline_summary(pipeline_results):
    """
    Generate executive summary of pipeline results
    """
    
    summary = {
        'execution_status': 'COMPLETED' if 'error' not in pipeline_results['metadata'] else 'FAILED',
        'execution_time': pipeline_results['metadata']['execution_time'],
        'components_executed': len(pipeline_results['metadata']['components_executed']),
        'dataset_statistics': {},
        'citation_statistics': {},
        'geographic_statistics': {},
        'quality_assessment': {},
        'business_insights': [],
        'recommended_actions': []
    }
    
    # Dataset statistics
    dataset = pipeline_results['dataset']
    if dataset is not None and not dataset.empty:
        summary['dataset_statistics'] = {
            'total_applications': len(dataset),
            'unique_families': dataset['docdb_family_id'].nunique() if 'docdb_family_id' in dataset.columns else 0,
            'year_range': f"{dataset['appln_filing_year'].min()}-{dataset['appln_filing_year'].max()}" if 'appln_filing_year' in dataset.columns else 'N/A',
            'filing_authorities': dataset['appln_auth'].nunique() if 'appln_auth' in dataset.columns else 0
        }
    
    # Citation statistics
    forward_cit = pipeline_results['citations']['forward']
    backward_cit = pipeline_results['citations']['backward']
    
    summary['citation_statistics'] = {
        'forward_citations': len(forward_cit) if forward_cit is not None else 0,
        'backward_citations': len(backward_cit) if backward_cit is not None else 0,
        'total_citations': (len(forward_cit) if forward_cit is not None else 0) + (len(backward_cit) if backward_cit is not None else 0)
    }
    
    # Geographic statistics
    geo_analysis = pipeline_results['geographic']['analysis']
    if geo_analysis:
        summary['geographic_statistics'] = {
            'applicant_countries': len(geo_analysis.get('applicant_countries', {})),
            'inventor_countries': len(geo_analysis.get('inventor_countries', {})),
            'international_collaboration': geo_analysis.get('international_collaboration', {}).get('multi_country_applicants', 0)
        }
    
    # Quality assessment
    quality_metrics = pipeline_results['quality']
    if quality_metrics:
        quality_scores = quality_metrics.get('quality_scores', {})
        business_readiness = quality_metrics.get('business_readiness', {})
        
        summary['quality_assessment'] = {
            'overall_score': quality_scores.get('overall_score', 0),
            'readiness_level': business_readiness.get('readiness_level', 'UNKNOWN'),
            'stakeholder_confidence': business_readiness.get('stakeholder_confidence', 'Unknown'),
            'presentation_suitability': business_readiness.get('presentation_suitability', 'Unknown')
        }
    
    # Business insights
    insights = []
    
    # Dataset insights
    dataset_stats = summary['dataset_statistics']
    if dataset_stats.get('total_applications', 0) >= 1000:
        insights.append("Large-scale analysis: Dataset size supports robust statistical conclusions")
    elif dataset_stats.get('total_applications', 0) >= 500:
        insights.append("Medium-scale analysis: Dataset suitable for most business intelligence needs")
    
    # Citation insights
    citation_stats = summary['citation_statistics']
    total_citations = citation_stats.get('total_citations', 0)
    if total_citations >= 1000:
        insights.append("Rich citation network: Strong foundation for innovation impact analysis")
    
    # Quality insights
    quality_assessment = summary['quality_assessment']
    overall_score = quality_assessment.get('overall_score', 0)
    if overall_score >= 80:
        insights.append("Excellent data quality: Ready for executive presentations and strategic decisions")
    elif overall_score >= 60:
        insights.append("Good data quality: Suitable for professional analysis and reporting")
    
    summary['business_insights'] = insights
    
    # Recommended actions
    actions = []
    
    if quality_metrics and 'recommendations' in quality_metrics:
        actions.extend(quality_metrics['recommendations'][:3])  # Top 3 recommendations
    
    if overall_score >= 70:
        actions.append("Proceed with stakeholder presentations and strategic analysis")
    else:
        actions.append("Consider data quality improvements before business presentations")
    
    summary['recommended_actions'] = actions
    
    return summary

def print_pipeline_summary(summary):
    """
    Print executive summary of pipeline results
    """
    
    print(f"📊 EXECUTIVE SUMMARY")
    print(f"   Status: {summary['execution_status']}")
    print(f"   Components: {summary['components_executed']}/6 executed")
    
    print(f"\n📈 Dataset Overview:")
    dataset_stats = summary['dataset_statistics']
    print(f"   Applications: {dataset_stats.get('total_applications', 0):,}")
    print(f"   Families: {dataset_stats.get('unique_families', 0):,}")
    print(f"   Time Period: {dataset_stats.get('year_range', 'N/A')}")
    print(f"   Filing Authorities: {dataset_stats.get('filing_authorities', 0)}")
    
    print(f"\n🔗 Citation Intelligence:")
    citation_stats = summary['citation_statistics']
    print(f"   Forward Citations: {citation_stats.get('forward_citations', 0):,}")
    print(f"   Backward Citations: {citation_stats.get('backward_citations', 0):,}")
    print(f"   Total Citation Network: {citation_stats.get('total_citations', 0):,}")
    
    print(f"\n🌍 Geographic Coverage:")
    geo_stats = summary['geographic_statistics']
    print(f"   Applicant Countries: {geo_stats.get('applicant_countries', 0)}")
    print(f"   Inventor Countries: {geo_stats.get('inventor_countries', 0)}")
    print(f"   International Collaborations: {geo_stats.get('international_collaboration', 0)}")
    
    print(f"\n✅ Quality Assessment:")
    quality = summary['quality_assessment']
    print(f"   Overall Score: {quality.get('overall_score', 0)}/100")
    print(f"   Business Readiness: {quality.get('readiness_level', 'UNKNOWN')}")
    print(f"   Stakeholder Confidence: {quality.get('stakeholder_confidence', 'Unknown')}")
    
    print(f"\n💡 Key Insights:")
    for insight in summary['business_insights'][:3]:
        print(f"   • {insight}")
    
    print(f"\n🎯 Recommended Actions:")
    for action in summary['recommended_actions'][:3]:
        print(f"   • {action}")

def run_pipeline_test():
    """
    Run pipeline in test mode for validation
    """
    
    print("🧪 RUNNING PIPELINE TEST")
    print("=" * 50)
    
    results = run_complete_ree_analysis(test_mode=True, output_prefix="test_ree")
    
    if results['summary']['execution_status'] == 'COMPLETED':
        print("\n✅ PIPELINE TEST SUCCESSFUL")
        return True
    else:
        print("\n❌ PIPELINE TEST FAILED")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='REE Patent Citation Analysis Pipeline')
    parser.add_argument('--test', action='store_true', help='Run in test mode (limited dataset)')
    parser.add_argument('--output', default='ree_analysis', help='Output file prefix')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # Default: run test mode
        print("Running in default test mode...")
        results = run_complete_ree_analysis(test_mode=True, output_prefix=args.output)
    else:
        results = run_complete_ree_analysis(test_mode=args.test, output_prefix=args.output)
    
    # Exit with appropriate code
    if results['summary']['execution_status'] == 'COMPLETED':
        print(f"\n🎉 Pipeline completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 Pipeline failed!")
        sys.exit(1)