import pandas as pd
from database_connection import get_patstat_connection

def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df, geographic_analysis=None):
    """Comprehensive quality assessment"""
    
    # Basic dataset metrics
    quality_metrics = {
        'total_applications': len(ree_df) if not ree_df.empty else 0,
        'total_families': ree_df['docdb_family_id'].nunique() if not ree_df.empty else 0,
        'forward_citations': len(forward_citations_df) if not forward_citations_df.empty else 0,
        'backward_citations': len(backward_citations_df) if not backward_citations_df.empty else 0,
        'countries_covered': ree_df['appln_auth'].nunique() if not ree_df.empty else 0,
        'year_range': f"{ree_df['appln_filing_year'].min()}-{ree_df['appln_filing_year'].max()}" if not ree_df.empty else "N/A"
    }
    
    # Add geographic metrics if available
    if geographic_analysis and 'distribution_analysis' in geographic_analysis:
        geo_dist = geographic_analysis['distribution_analysis']
        if 'geographic_diversity' in geo_dist:
            quality_metrics['applicant_countries'] = geo_dist['geographic_diversity']['total_countries']
        if 'market_concentration' in geo_dist:
            quality_metrics['market_concentration_percent'] = geo_dist['market_concentration']['concentration_ratio_percent']
    
    # Calculate comprehensive quality score
    quality_score = calculate_comprehensive_quality_score(quality_metrics)
    
    print("DATASET QUALITY REPORT")
    print("=" * 50)
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    
    print(f"\nOverall Quality Score: {quality_score}/100")
    
    # Quality assessment
    if quality_score >= 80:
        quality_rating = "EXCELLENT"
        recommendation = "Dataset ready for professional analysis and executive presentations"
    elif quality_score >= 60:
        quality_rating = "GOOD"
        recommendation = "Dataset suitable for most analyses with strong business value"
    elif quality_score >= 40:
        quality_rating = "FAIR"
        recommendation = "Dataset usable but consider expanding scope for better insights"
    else:
        quality_rating = "POOR"
        recommendation = "Dataset needs significant improvement before business use"
    
    print(f"\nQuality Rating: {quality_rating}")
    print(f"Recommendation: {recommendation}")
    
    return {
        'metrics': quality_metrics,
        'quality_score': quality_score,
        'quality_rating': quality_rating,
        'recommendation': recommendation
    }

def calculate_comprehensive_quality_score(metrics):
    """Calculate overall quality score (0-100) with comprehensive criteria"""
    score = 0
    
    # Application count (25 points max)
    app_count = metrics.get('total_applications', 0)
    if app_count >= 1000:
        score += 25
    elif app_count >= 500:
        score += 20
    elif app_count >= 200:
        score += 15
    elif app_count >= 100:
        score += 10
    elif app_count >= 50:
        score += 5
    
    # Citation coverage (25 points max)
    total_citations = metrics.get('forward_citations', 0) + metrics.get('backward_citations', 0)
    if total_citations >= 2000:
        score += 25
    elif total_citations >= 1000:
        score += 20
    elif total_citations >= 500:
        score += 15
    elif total_citations >= 200:
        score += 10
    elif total_citations >= 50:
        score += 5
    
    # Geographic diversity (20 points max)
    countries = metrics.get('countries_covered', 0)
    if countries >= 20:
        score += 20
    elif countries >= 15:
        score += 15
    elif countries >= 10:
        score += 12
    elif countries >= 5:
        score += 8
    elif countries >= 3:
        score += 5
    
    # Family diversity (15 points max)
    families = metrics.get('total_families', 0)
    applications = metrics.get('total_applications', 1)
    family_ratio = families / applications if applications > 0 else 0
    
    if family_ratio >= 0.8:
        score += 15
    elif family_ratio >= 0.6:
        score += 12
    elif family_ratio >= 0.4:
        score += 9
    elif family_ratio >= 0.2:
        score += 6
    elif family_ratio > 0:
        score += 3
    
    # Market concentration analysis (10 points max)
    concentration = metrics.get('market_concentration_percent', 0)
    if 30 <= concentration <= 70:  # Optimal concentration for analysis
        score += 10
    elif 20 <= concentration <= 80:
        score += 8
    elif 10 <= concentration <= 90:
        score += 6
    elif concentration > 0:
        score += 3
    
    # Applicant country diversity (5 points max)
    applicant_countries = metrics.get('applicant_countries', 0)
    if applicant_countries >= 15:
        score += 5
    elif applicant_countries >= 10:
        score += 4
    elif applicant_countries >= 5:
        score += 3
    elif applicant_countries >= 3:
        score += 2
    elif applicant_countries > 0:
        score += 1
    
    return min(score, 100)

def generate_business_intelligence_summary(ree_df, citation_results, geographic_results, quality_assessment):
    """Generate executive summary for business stakeholders"""
    
    print("\nBUSINESS INTELLIGENCE SUMMARY")
    print("=" * 50)
    
    # Market overview
    total_apps = len(ree_df) if not ree_df.empty else 0
    if total_apps > 0:
        year_min = ree_df['appln_filing_year'].min()
        year_max = ree_df['appln_filing_year'].max()
        
        print(f"📊 MARKET OVERVIEW")
        print(f"   • REE Patent Portfolio: {total_apps:,} applications ({year_min}-{year_max})")
        print(f"   • Patent Family Coverage: {ree_df['docdb_family_id'].nunique():,} unique families")
        print(f"   • Market Activity Period: {year_max - year_min + 1} years")
    
    # Innovation intelligence
    if citation_results:
        forward_cit = len(citation_results.get('forward_citations', []))
        backward_cit = len(citation_results.get('backward_citations', []))
        
        print(f"\n🔬 INNOVATION INTELLIGENCE")
        print(f"   • Technology Impact: {forward_cit:,} forward citations")
        print(f"   • Knowledge Foundation: {backward_cit:,} backward citations")
        
        if forward_cit > 0 and backward_cit > 0:
            innovation_ratio = forward_cit / backward_cit
            if innovation_ratio > 1:
                print(f"   • Innovation Profile: High-impact technology (ratio: {innovation_ratio:.2f})")
            else:
                print(f"   • Innovation Profile: Building on existing knowledge (ratio: {innovation_ratio:.2f})")
    
    # Geographic intelligence
    if geographic_results and 'distribution_analysis' in geographic_results:
        geo_data = geographic_results['distribution_analysis']
        
        print(f"\n🌍 COMPETITIVE LANDSCAPE")
        if 'country_distribution' in geo_data:
            top_countries = list(geo_data['country_distribution'].items())[:3]
            print(f"   • Market Leaders: {', '.join([f'{country} ({count})' for country, count in top_countries])}")
        
        if 'market_concentration' in geo_data:
            concentration = geo_data['market_concentration']['concentration_ratio_percent']
            print(f"   • Market Concentration: {concentration:.1f}% (Top 5 countries)")
            
            if concentration > 70:
                print(f"   • Market Structure: Highly concentrated")
            elif concentration > 50:
                print(f"   • Market Structure: Moderately concentrated")
            else:
                print(f"   • Market Structure: Fragmented/distributed")
    
    # Quality and reliability
    quality_score = quality_assessment['quality_score']
    quality_rating = quality_assessment['quality_rating']
    
    print(f"\n✅ DATA QUALITY & RELIABILITY")
    print(f"   • Analysis Quality Score: {quality_score}/100 ({quality_rating})")
    print(f"   • Business Confidence Level: {get_confidence_level(quality_score)}")
    print(f"   • Recommendation: {quality_assessment['recommendation']}")
    
    # Strategic recommendations
    print(f"\n🎯 STRATEGIC INSIGHTS")
    
    if total_apps >= 500:
        print(f"   • Market Status: Mature technology domain with substantial patent activity")
    elif total_apps >= 100:
        print(f"   • Market Status: Developing technology with growing patent interest")
    else:
        print(f"   • Market Status: Emerging or niche technology area")
    
    if citation_results and len(citation_results.get('forward_citations', [])) > 0:
        print(f"   • Technology Relevance: Active citation network indicates ongoing innovation")
    
    if geographic_results and 'collaboration_analysis' in geographic_results:
        collab_rate = geographic_results['collaboration_analysis'].get('collaboration_rate_percent', 0)
        if collab_rate > 10:
            print(f"   • Innovation Pattern: High international collaboration ({collab_rate:.1f}%)")
        elif collab_rate > 5:
            print(f"   • Innovation Pattern: Moderate international collaboration ({collab_rate:.1f}%)")
        else:
            print(f"   • Innovation Pattern: Primarily domestic innovation")

def get_confidence_level(quality_score):
    """Convert quality score to business confidence level"""
    if quality_score >= 80:
        return "Very High - Suitable for executive decision-making"
    elif quality_score >= 60:
        return "High - Reliable for strategic analysis"
    elif quality_score >= 40:
        return "Medium - Useful for initial assessment"
    else:
        return "Low - Requires additional data validation"

def export_business_data(ree_df, citation_results, geographic_results, quality_assessment, export_prefix="ree_analysis"):
    """Export data in business-friendly formats"""
    
    print(f"\n💾 EXPORTING BUSINESS DATA")
    print("=" * 30)
    
    exports_created = []
    
    # Main dataset export
    if not ree_df.empty:
        main_export = f"{export_prefix}_patent_dataset.csv"
        ree_df.to_csv(main_export, index=False)
        exports_created.append(main_export)
        print(f"✅ Main Dataset: {main_export}")
    
    # Citation data export
    if citation_results:
        if 'forward_citations' in citation_results and not citation_results['forward_citations'].empty:
            forward_export = f"{export_prefix}_forward_citations.csv"
            citation_results['forward_citations'].to_csv(forward_export, index=False)
            exports_created.append(forward_export)
            print(f"✅ Forward Citations: {forward_export}")
        
        if 'backward_citations' in citation_results and not citation_results['backward_citations'].empty:
            backward_export = f"{export_prefix}_backward_citations.csv"
            citation_results['backward_citations'].to_csv(backward_export, index=False)
            exports_created.append(backward_export)
            print(f"✅ Backward Citations: {backward_export}")
    
    # Business summary export
    import json
    
    business_summary = {
        'analysis_metadata': {
            'export_timestamp': pd.Timestamp.now().isoformat(),
            'dataset_size': len(ree_df) if not ree_df.empty else 0,
            'quality_assessment': quality_assessment
        },
        'geographic_intelligence': geographic_results.get('distribution_analysis', {}) if geographic_results else {},
        'collaboration_intelligence': geographic_results.get('collaboration_analysis', {}) if geographic_results else {},
        'citation_intelligence': citation_results.get('citation_patterns', {}) if citation_results else {}
    }
    
    summary_export = f"{export_prefix}_business_summary.json"
    with open(summary_export, 'w') as f:
        json.dump(business_summary, f, indent=2, default=str)
    exports_created.append(summary_export)
    print(f"✅ Business Summary: {summary_export}")
    
    print(f"\n📂 Total exports created: {len(exports_created)}")
    return exports_created

def comprehensive_validation_and_reporting(ree_df, citation_results, geographic_results):
    """Complete validation and business reporting workflow"""
    
    print("COMPREHENSIVE VALIDATION & REPORTING")
    print("=" * 50)
    
    # Step 1: Quality validation
    forward_cit_df = citation_results.get('forward_citations', pd.DataFrame()) if citation_results else pd.DataFrame()
    backward_cit_df = citation_results.get('backward_citations', pd.DataFrame()) if citation_results else pd.DataFrame()
    
    quality_assessment = validate_dataset_quality(ree_df, forward_cit_df, backward_cit_df, geographic_results)
    
    # Step 2: Business intelligence summary
    generate_business_intelligence_summary(ree_df, citation_results, geographic_results, quality_assessment)
    
    # Step 3: Export business data
    export_files = export_business_data(ree_df, citation_results, geographic_results, quality_assessment)
    
    return {
        'quality_assessment': quality_assessment,
        'export_files': export_files
    }

if __name__ == "__main__":
    print("Testing Data Validator...")
    
    # Create sample data for testing
    sample_ree_df = pd.DataFrame({
        'appln_id': range(1, 101),
        'docdb_family_id': range(100, 200),
        'appln_filing_year': [2020] * 50 + [2021] * 30 + [2022] * 20,
        'appln_auth': ['US'] * 40 + ['EP'] * 30 + ['JP'] * 20 + ['CN'] * 10
    })
    
    sample_citations = pd.DataFrame({
        'citing_appln_id': range(2001, 2051),
        'cited_ree_appln_id': range(1, 51)
    })
    
    # Test validation
    results = comprehensive_validation_and_reporting(
        sample_ree_df, 
        {'forward_citations': sample_citations, 'backward_citations': sample_citations}, 
        None
    )
    
    print(f"\n✅ Validation complete!")
    print(f"Quality Score: {results['quality_assessment']['quality_score']}/100")
    print(f"Export Files: {len(results['export_files'])}")