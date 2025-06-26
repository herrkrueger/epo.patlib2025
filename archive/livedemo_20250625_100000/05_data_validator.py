# 5.1 Data Quality Validation using Direct DataFrame Operations
import pandas as pd
from datetime import datetime

def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """
    Comprehensive quality checks for REE patent dataset
    Uses direct DataFrame operations
    """
    
    quality_metrics = {}
    
    # Dataset size validation
    quality_metrics['total_applications'] = len(ree_df)
    quality_metrics['total_families'] = ree_df['docdb_family_id'].nunique() if 'docdb_family_id' in ree_df.columns else 0
    quality_metrics['total_forward_citations'] = len(forward_citations_df)
    quality_metrics['total_backward_citations'] = len(backward_citations_df)
    
    # Temporal distribution
    if 'appln_filing_year' in ree_df.columns:
        quality_metrics['year_range'] = f"{ree_df['appln_filing_year'].min()} - {ree_df['appln_filing_year'].max()}"
        quality_metrics['avg_patents_per_year'] = ree_df['appln_filing_year'].value_counts().mean()
    
    # Geographic coverage
    if 'appln_auth' in ree_df.columns:
        quality_metrics['countries_covered'] = ree_df['appln_auth'].nunique()
    
    # Citation rates
    if not forward_citations_df.empty and 'cited_ree_appln_id' in forward_citations_df.columns:
        cited_patents = forward_citations_df['cited_ree_appln_id'].nunique()
        quality_metrics['forward_citation_rate'] = f"{(cited_patents / len(ree_df) * 100):.1f}%"
    
    print("\n" + "="*50)
    print("DATASET QUALITY REPORT")
    print("="*50)
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    print("="*50)
    
    return quality_metrics

def generate_summary_report(ree_df, forward_citations_df, backward_citations_df, quality_metrics):
    """
    Generate business-friendly summary of findings
    """
    
    summary = {
        'executive_summary': {
            'total_ree_applications': quality_metrics.get('total_applications', 0),
            'total_ree_families': quality_metrics.get('total_families', 0),
            'date_coverage': quality_metrics.get('year_range', 'Unknown'),
            'countries_analyzed': quality_metrics.get('countries_covered', 0)
        },
        'citation_insights': {
            'forward_citations': quality_metrics.get('total_forward_citations', 0),
            'backward_citations': quality_metrics.get('total_backward_citations', 0),
            'citation_rate': quality_metrics.get('forward_citation_rate', 'N/A')
        }
    }
    
    # Add top countries if available
    if 'appln_auth' in ree_df.columns:
        summary['top_countries'] = ree_df['appln_auth'].value_counts().head(5).to_dict()
    
    # Add temporal trends if available
    if 'appln_filing_year' in ree_df.columns:
        summary['temporal_trends'] = ree_df['appln_filing_year'].value_counts().sort_index().tail(5).to_dict()
    
    print("\n" + "="*50)
    print("BUSINESS SUMMARY REPORT")
    print("="*50)
    print(f"REE Patent Landscape Analysis Results:")
    print(f"• Total REE Applications: {summary['executive_summary']['total_ree_applications']}")
    print(f"• Unique Patent Families: {summary['executive_summary']['total_ree_families']}")
    print(f"• Time Period: {summary['executive_summary']['date_coverage']}")
    print(f"• Countries Involved: {summary['executive_summary']['countries_analyzed']}")
    print(f"• Forward Citations Found: {summary['citation_insights']['forward_citations']}")
    print(f"• Citation Rate: {summary['citation_insights']['citation_rate']}")
    
    if 'top_countries' in summary:
        print(f"• Top Filing Countries: {list(summary['top_countries'].keys())[:3]}")
    
    print("="*50)
    
    return summary

if __name__ == "__main__":
    # Test validation functions
    print("Testing data validation...")
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
    
    # Import citation analyzer
    spec3 = importlib.util.spec_from_file_location("citation_analyzer", "03_citation_analyzer.py")
    cit_module = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(cit_module)
    get_forward_citations = cit_module.get_forward_citations
    get_backward_citations = cit_module.get_backward_citations
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:50]  # Test with subset
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            quality_metrics = validate_dataset_quality(ree_data, forward_cit, backward_cit)
            summary_report = generate_summary_report(ree_data, forward_cit, backward_cit, quality_metrics)