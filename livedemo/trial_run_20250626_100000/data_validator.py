import pandas as pd
from datetime import datetime

def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """Comprehensive quality checks"""
    
    print("=" * 50)
    print("DATASET QUALITY REPORT")
    print("=" * 50)
    
    quality_metrics = {
        'total_applications': len(ree_df) if not ree_df.empty else 0,
        'total_families': ree_df['docdb_family_id'].nunique() if not ree_df.empty and 'docdb_family_id' in ree_df.columns else 0,
        'forward_citations': len(forward_citations_df) if not forward_citations_df.empty else 0,
        'backward_citations': len(backward_citations_df) if not backward_citations_df.empty else 0,
        'countries_covered': ree_df['appln_auth'].nunique() if not ree_df.empty and 'appln_auth' in ree_df.columns else 0,
        'data_completeness': 0,
        'quality_score': 0
    }
    
    # Data completeness check
    if not ree_df.empty:
        completeness_factors = []
        
        # Check for title data
        if 'appln_title' in ree_df.columns:
            title_completeness = (ree_df['appln_title'].notna().sum() / len(ree_df)) * 100
            completeness_factors.append(title_completeness)
            print(f"Title Coverage: {title_completeness:.1f}%")
        
        # Check for abstract data
        if 'appln_abstract' in ree_df.columns:
            abstract_completeness = (ree_df['appln_abstract'].notna().sum() / len(ree_df)) * 100
            completeness_factors.append(abstract_completeness)
            print(f"Abstract Coverage: {abstract_completeness:.1f}%")
        
        # Check for geographic data
        if 'person_ctry_code' in ree_df.columns:
            geo_completeness = (ree_df['person_ctry_code'].notna().sum() / len(ree_df)) * 100
            completeness_factors.append(geo_completeness)
            print(f"Geographic Coverage: {geo_completeness:.1f}%")
        
        if completeness_factors:
            quality_metrics['data_completeness'] = sum(completeness_factors) / len(completeness_factors)
    
    # Calculate overall quality score
    score_factors = []
    
    # Dataset size factor (0-40 points)
    if quality_metrics['total_applications'] >= 1000:
        score_factors.append(40)
    elif quality_metrics['total_applications'] >= 100:
        score_factors.append(30)
    elif quality_metrics['total_applications'] >= 10:
        score_factors.append(20)
    elif quality_metrics['total_applications'] > 0:
        score_factors.append(10)
    else:
        score_factors.append(0)
    
    # Citation coverage (0-30 points)
    citation_coverage = quality_metrics['forward_citations'] + quality_metrics['backward_citations']
    if citation_coverage >= 1000:
        score_factors.append(30)
    elif citation_coverage >= 100:
        score_factors.append(20)
    elif citation_coverage >= 10:
        score_factors.append(10)
    elif citation_coverage > 0:
        score_factors.append(5)
    else:
        score_factors.append(0)
    
    # Geographic diversity (0-20 points)
    if quality_metrics['countries_covered'] >= 20:
        score_factors.append(20)
    elif quality_metrics['countries_covered'] >= 10:
        score_factors.append(15)
    elif quality_metrics['countries_covered'] >= 5:
        score_factors.append(10)
    elif quality_metrics['countries_covered'] > 0:
        score_factors.append(5)
    else:
        score_factors.append(0)
    
    # Data completeness (0-10 points)
    if quality_metrics['data_completeness'] >= 80:
        score_factors.append(10)
    elif quality_metrics['data_completeness'] >= 60:
        score_factors.append(8)
    elif quality_metrics['data_completeness'] >= 40:
        score_factors.append(6)
    elif quality_metrics['data_completeness'] > 0:
        score_factors.append(4)
    else:
        score_factors.append(0)
    
    quality_metrics['quality_score'] = sum(score_factors)
    
    # Print detailed metrics
    print(f"Total Applications: {quality_metrics['total_applications']}")
    print(f"Total Families: {quality_metrics['total_families']}")
    print(f"Forward Citations: {quality_metrics['forward_citations']}")
    print(f"Backward Citations: {quality_metrics['backward_citations']}")
    print(f"Countries Covered: {quality_metrics['countries_covered']}")
    print(f"Data Completeness: {quality_metrics['data_completeness']:.1f}%")
    print(f"Quality Score: {quality_metrics['quality_score']}/100")
    
    # Quality assessment
    if quality_metrics['quality_score'] >= 80:
        print("🟢 EXCELLENT - Dataset ready for professional analysis")
    elif quality_metrics['quality_score'] >= 60:
        print("🟡 GOOD - Dataset suitable for most analyses")
    elif quality_metrics['quality_score'] >= 40:
        print("🟠 FAIR - Dataset usable but with limitations")
    else:
        print("🔴 POOR - Dataset needs improvement")
    
    return quality_metrics

def generate_summary_report(ree_df, forward_citations_df, quality_metrics):
    """Generate business summary"""
    
    print("\n" + "=" * 50)
    print("BUSINESS SUMMARY REPORT")
    print("=" * 50)
    
    summary = {
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'total_ree_applications': quality_metrics['total_applications'],
        'total_ree_families': quality_metrics['total_families'],
        'forward_citations': quality_metrics['forward_citations'],
        'backward_citations': quality_metrics['backward_citations'],
        'quality_score': quality_metrics['quality_score'],
        'top_countries': {},
        'key_insights': []
    }
    
    # Top countries analysis
    if not ree_df.empty and 'appln_auth' in ree_df.columns:
        summary['top_countries'] = ree_df['appln_auth'].value_counts().head(5).to_dict()
    
    # Generate key insights
    if summary['total_ree_applications'] > 0:
        summary['key_insights'].append(f"Found {summary['total_ree_applications']} REE-related patent applications in 2023")
        
        if summary['total_ree_families'] > 0:
            family_ratio = summary['total_ree_families'] / summary['total_ree_applications']
            if family_ratio > 0.8:
                summary['key_insights'].append("High family diversity indicates global filing strategy")
            elif family_ratio > 0.5:
                summary['key_insights'].append("Moderate family consolidation observed")
            else:
                summary['key_insights'].append("High family consolidation suggests focused innovation")
        
        if summary['forward_citations'] > 0:
            citation_ratio = summary['forward_citations'] / summary['total_ree_applications']
            if citation_ratio > 0.1:
                summary['key_insights'].append("Strong citation activity indicates technological impact")
            else:
                summary['key_insights'].append("Limited forward citations typical for recent patents")
        
        if summary['top_countries']:
            top_country = list(summary['top_countries'].keys())[0]
            top_count = summary['top_countries'][top_country]
            market_share = (top_count / summary['total_ree_applications']) * 100
            summary['key_insights'].append(f"{top_country} leads with {market_share:.1f}% of REE patent activity")
    
    # Print summary
    print(f"Analysis Date: {summary['analysis_date']}")
    print(f"REE Applications: {summary['total_ree_applications']}")
    print(f"Patent Families: {summary['total_ree_families']}")
    print(f"Forward Citations: {summary['forward_citations']}")
    print(f"Backward Citations: {summary['backward_citations']}")
    print(f"Quality Score: {summary['quality_score']}/100")
    
    if summary['top_countries']:
        print("\nTop Filing Countries:")
        for country, count in list(summary['top_countries'].items())[:3]:
            percentage = (count / summary['total_ree_applications']) * 100
            print(f"  {country}: {count} ({percentage:.1f}%)")
    
    if summary['key_insights']:
        print("\nKey Insights:")
        for insight in summary['key_insights'][:3]:
            print(f"  • {insight}")
    
    return summary

def export_validation_results(quality_metrics, summary_report, output_dir="."):
    """Export validation results to files"""
    
    try:
        # Export quality metrics
        quality_df = pd.DataFrame([quality_metrics])
        quality_df.to_csv(f"{output_dir}/ree_quality_metrics.csv", index=False)
        
        # Export summary report
        summary_df = pd.DataFrame([summary_report])
        summary_df.to_csv(f"{output_dir}/ree_summary_report.csv", index=False)
        
        print(f"\n✅ Validation results exported to {output_dir}/")
        return True
        
    except Exception as e:
        print(f"⚠️ Export failed: {e}")
        return False

if __name__ == "__main__":
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    from citation_analyzer import get_forward_citations, get_backward_citations
    from geographic_enricher import enrich_with_geographic_data
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        enriched_ree = enrich_with_geographic_data(db, ree_data)
        
        appln_ids = ree_data['appln_id'].tolist() if not ree_data.empty else []
        forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
        backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
        
        quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
        summary_report = generate_summary_report(enriched_ree, forward_cit, quality_metrics)
        
        export_validation_results(quality_metrics, summary_report)
        print("\nData validation completed!")