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
        quality_metrics['avg_patents_per_year'] = round(ree_df['appln_filing_year'].value_counts().mean(), 1)
        quality_metrics['years_covered'] = ree_df['appln_filing_year'].nunique()
    
    # Geographic coverage
    if 'appln_auth' in ree_df.columns:
        quality_metrics['countries_covered'] = ree_df['appln_auth'].nunique()
        quality_metrics['top_filing_country'] = ree_df['appln_auth'].value_counts().index[0] if len(ree_df) > 0 else 'N/A'
    
    # Citation rates
    if not forward_citations_df.empty and 'cited_ree_appln_id' in forward_citations_df.columns:
        cited_patents = forward_citations_df['cited_ree_appln_id'].nunique()
        quality_metrics['forward_citation_rate'] = f"{(cited_patents / len(ree_df) * 100):.1f}%"
        quality_metrics['avg_citations_per_patent'] = round(len(forward_citations_df) / cited_patents, 1) if cited_patents > 0 else 0
    
    # Data completeness
    quality_metrics['title_completeness'] = f"{(ree_df['appln_title'].notna().sum() / len(ree_df) * 100):.1f}%" if 'appln_title' in ree_df.columns else 'N/A'
    quality_metrics['abstract_completeness'] = f"{(ree_df['appln_abstract'].notna().sum() / len(ree_df) * 100):.1f}%" if 'appln_abstract' in ree_df.columns else 'N/A'
    quality_metrics['family_completeness'] = f"{(ree_df['docdb_family_id'].notna().sum() / len(ree_df) * 100):.1f}%" if 'docdb_family_id' in ree_df.columns else 'N/A'
    
    print("\n" + "="*60)
    print("DATASET QUALITY REPORT")
    print("="*60)
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    print("="*60)
    
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
            'countries_analyzed': quality_metrics.get('countries_covered', 0),
            'years_covered': quality_metrics.get('years_covered', 0)
        },
        'citation_insights': {
            'forward_citations': quality_metrics.get('total_forward_citations', 0),
            'backward_citations': quality_metrics.get('total_backward_citations', 0),
            'citation_rate': quality_metrics.get('forward_citation_rate', 'N/A'),
            'avg_citations_per_patent': quality_metrics.get('avg_citations_per_patent', 0)
        },
        'data_quality': {
            'title_completeness': quality_metrics.get('title_completeness', 'N/A'),
            'abstract_completeness': quality_metrics.get('abstract_completeness', 'N/A'),
            'family_completeness': quality_metrics.get('family_completeness', 'N/A')
        }
    }
    
    # Add top countries if available
    if 'appln_auth' in ree_df.columns:
        summary['top_countries'] = ree_df['appln_auth'].value_counts().head(5).to_dict()
    
    # Add temporal trends if available
    if 'appln_filing_year' in ree_df.columns:
        summary['temporal_trends'] = ree_df['appln_filing_year'].value_counts().sort_index().tail(5).to_dict()
    
    # Add citation patterns
    if not forward_citations_df.empty and 'citing_country' in forward_citations_df.columns:
        summary['citing_countries'] = forward_citations_df['citing_country'].value_counts().head(5).to_dict()
    
    print("\n" + "="*60)
    print("BUSINESS SUMMARY REPORT")
    print("="*60)
    print(f"📊 REE Patent Landscape Analysis Results:")
    print(f"  • Total REE Applications: {summary['executive_summary']['total_ree_applications']:,}")
    print(f"  • Unique Patent Families: {summary['executive_summary']['total_ree_families']:,}")
    print(f"  • Time Period: {summary['executive_summary']['date_coverage']}")
    print(f"  • Years Covered: {summary['executive_summary']['years_covered']}")
    print(f"  • Filing Countries: {summary['executive_summary']['countries_analyzed']}")
    print(f"  • Forward Citations: {summary['citation_insights']['forward_citations']:,}")
    print(f"  • Backward Citations: {summary['citation_insights']['backward_citations']:,}")
    print(f"  • Citation Rate: {summary['citation_insights']['citation_rate']}")
    
    if 'top_countries' in summary:
        print(f"  • Top Filing Countries: {list(summary['top_countries'].keys())[:3]}")
    
    if 'citing_countries' in summary:
        print(f"  • Top Citing Countries: {list(summary['citing_countries'].keys())[:3]}")
    
    print(f"\n📈 Data Quality Metrics:")
    print(f"  • Title Completeness: {summary['data_quality']['title_completeness']}")
    print(f"  • Abstract Completeness: {summary['data_quality']['abstract_completeness']}")
    print(f"  • Family Completeness: {summary['data_quality']['family_completeness']}")
    
    print("="*60)
    
    return summary

def check_data_consistency(ree_df, forward_citations_df, backward_citations_df):
    """
    Check for data consistency issues
    """
    
    print(f"\n{'='*50}")
    print("DATA CONSISTENCY CHECKS")
    print(f"{'='*50}")
    
    issues = []
    
    # Check for missing critical data
    if ree_df.empty:
        issues.append("❌ No REE patents found")
    
    if 'appln_id' not in ree_df.columns:
        issues.append("❌ Missing application ID column")
    
    if 'appln_filing_year' in ree_df.columns:
        min_year = ree_df['appln_filing_year'].min()
        max_year = ree_df['appln_filing_year'].max()
        if min_year < 1990 or max_year > 2025:
            issues.append(f"⚠️ Unusual year range: {min_year} - {max_year}")
    
    # Check citation consistency
    if not forward_citations_df.empty and 'cited_ree_appln_id' in forward_citations_df.columns:
        ree_ids = set(ree_df['appln_id'])
        cited_ids = set(forward_citations_df['cited_ree_appln_id'])
        orphaned_citations = cited_ids - ree_ids
        if orphaned_citations:
            issues.append(f"⚠️ {len(orphaned_citations)} forward citations reference unknown REE patents")
    
    # Check for duplicates
    if 'appln_id' in ree_df.columns:
        duplicates = ree_df['appln_id'].duplicated().sum()
        if duplicates > 0:
            issues.append(f"⚠️ {duplicates} duplicate application IDs found")
    
    if not issues:
        print("✅ All consistency checks passed")
    else:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
    
    print(f"{'='*50}")
    
    return issues

def export_validation_report(quality_metrics, summary, issues, filename="validation_report.txt"):
    """
    Export validation results to file
    """
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""
REE PATENT CITATION ANALYSIS - VALIDATION REPORT
Generated: {timestamp}

=== QUALITY METRICS ===
"""
    
    for metric, value in quality_metrics.items():
        report_content += f"{metric.replace('_', ' ').title()}: {value}\n"
    
    report_content += f"""
=== EXECUTIVE SUMMARY ===
Total Applications: {summary['executive_summary']['total_ree_applications']:,}
Total Families: {summary['executive_summary']['total_ree_families']:,}
Date Coverage: {summary['executive_summary']['date_coverage']}
Countries: {summary['executive_summary']['countries_analyzed']}
Forward Citations: {summary['citation_insights']['forward_citations']:,}
Citation Rate: {summary['citation_insights']['citation_rate']}

=== DATA CONSISTENCY ===
"""
    
    if not issues:
        report_content += "✅ All checks passed\n"
    else:
        report_content += "Issues found:\n"
        for issue in issues:
            report_content += f"  {issue}\n"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"📝 Validation report saved to: {filename}")
    except Exception as e:
        print(f"❌ Failed to save report: {e}")
    
    return report_content

if __name__ == "__main__":
    # Test validation functions
    print("Testing data validation...")
    from database_connection import get_database_connection
    from ree_dataset_builder import build_ree_dataset
    from citation_analyzer import get_forward_citations, get_backward_citations
    
    db = get_database_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:50]  # Test with subset
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            quality_metrics = validate_dataset_quality(ree_data, forward_cit, backward_cit)
            summary_report = generate_summary_report(ree_data, forward_cit, backward_cit, quality_metrics)
            consistency_issues = check_data_consistency(ree_data, forward_cit, backward_cit)
            
            # Export report
            export_validation_report(quality_metrics, summary_report, consistency_issues)