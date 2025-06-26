import pandas as pd
from database_connection import test_tip_connection
from dataset_builder import build_ree_dataset, validate_ree_dataset
from citation_analyzer import get_forward_citations, get_backward_citations
from geographic_enricher import enrich_with_geographic_data

def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """Comprehensive quality checks"""
    
    quality_metrics = {
        'total_applications': len(ree_df),
        'total_families': ree_df['docdb_family_id'].nunique(),
        'forward_citations': len(forward_citations_df),
        'backward_citations': len(backward_citations_df),
        'countries_covered': ree_df['appln_auth'].nunique()
    }
    
    print("DATASET QUALITY REPORT")
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    
    return quality_metrics

def generate_summary_report(ree_df, forward_citations_df, quality_metrics):
    """Generate business summary"""
    
    summary = {
        'total_ree_applications': quality_metrics['total_applications'],
        'total_ree_families': quality_metrics['total_families'],
        'forward_citations': quality_metrics['forward_citations'],
        'top_countries': ree_df['appln_auth'].value_counts().head(3).to_dict()
    }
    
    print("BUSINESS SUMMARY")
    print(f"• REE Applications: {summary['total_ree_applications']}")
    print(f"• Patent Families: {summary['total_ree_families']}")
    print(f"• Forward Citations: {summary['forward_citations']}")
    print(f"• Top Countries: {summary['top_countries']}")
    
    return summary

if __name__ == "__main__":
    db = test_tip_connection()
    if db:
        # Build dataset
        ree_data = build_ree_dataset(db, test_mode=True)
        validate_ree_dataset(ree_data)
        
        if not ree_data.empty:
            # Get citations
            appln_ids = ree_data['appln_id'].tolist()
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            # Validate quality
            quality_metrics = validate_dataset_quality(ree_data, forward_cit, backward_cit)
            summary_report = generate_summary_report(ree_data, forward_cit, quality_metrics)
            
            print("✅ Data validation complete")