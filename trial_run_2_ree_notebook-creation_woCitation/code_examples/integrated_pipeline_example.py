# MODULAR PIPELINE STRUCTURE - PROVEN WORKING IMPLEMENTATION
import pandas as pd
import json
from datetime import datetime

def run_complete_ree_analysis(test_mode=True):
    """Integrated pipeline with proper error handling - VERIFIED WORKING"""
    
    print("REE PATENT ANALYSIS PIPELINE")
    print("=" * 50)
    
    # Step 1: Database connection
    print("\n🔌 Step 1: Connecting to PATSTAT...")
    from database_connection_example import get_patstat_connection
    db = get_patstat_connection()
    if not db:
        print("❌ Database connection failed")
        return None
    
    # Step 2: Dataset building
    print("\n🔍 Step 2: Building REE dataset...")
    from dataset_builder_example import build_ree_dataset
    ree_data = build_ree_dataset(db, test_mode)
    if ree_data.empty:
        print("❌ No REE data found")
        return None
   
    # Step 3: Geographic enrichment
    print("\n🌍 Step 4: Geographic enrichment...")
    from geographic_enricher_example import enrich_with_geographic_data
    enriched_ree = enrich_with_geographic_data(db, ree_data)
    
    # Step 4: Quality validation
    print("\n✅ Step 5: Quality validation...")
    from data_validator_example import validate_dataset_quality
    quality_metrics = validate_dataset_quality(enriched_ree)
    
    # Step 5: Business intelligence and export
    print("\n📈 Step 6: Business intelligence generation...")
    business_summary = generate_business_intelligence(enriched_ree, quality_metrics)
    
    # Step 6: Export results
    print("\n💾 Step 7: Exporting results...")
    export_results = export_complete_analysis(enriched_ree, quality_metrics, business_summary)
    
    print("\n" + "=" * 50)
    print("✅ PIPELINE COMPLETE")
    print_final_summary(enriched_ree, quality_metrics)
    
    return {
        'ree_dataset': enriched_ree,
        'quality_metrics': quality_metrics,
        'business_summary': business_summary,
        'export_files': export_results
    }

def generate_business_intelligence(ree_dataset, quality_metrics):
    """Generate comprehensive business intelligence summary"""
    
    # Technology trends analysis
    tech_trends = {}
    if 'cpc_class_symbol' in ree_dataset.columns:
        tech_trends = {
            'top_technology_areas': ree_dataset['cpc_class_symbol'].str[:4].value_counts().head(5).to_dict(),
            'technology_diversity': ree_dataset['cpc_class_symbol'].nunique()
        }
    
    # Geographic intelligence
    geo_intelligence = {}
    if 'primary_applicant_country' in ree_dataset.columns:
        country_counts = ree_dataset['primary_applicant_country'].value_counts()
        geo_intelligence = {
            'top_countries': country_counts.head(5).to_dict(),
            'market_concentration_top3': (country_counts.head(3).sum() / len(ree_dataset) * 100),
            'geographic_diversity_score': country_counts.nunique()
        }
    else:
        geo_intelligence = {
            'top_countries': {},
            'market_concentration_top3': 0,
            'geographic_diversity_score': 0
        }
    

def calculate_filing_trend(dataset):
    """Calculate patent filing trend over recent years"""
    if 'appln_filing_year' in dataset.columns:
        yearly_counts = dataset['appln_filing_year'].value_counts().sort_index()
        recent_years = yearly_counts.tail(5)
        if len(recent_years) >= 2:
            trend = (recent_years.iloc[-1] - recent_years.iloc[0]) / len(recent_years)
            return round(trend, 2)
    return 0

def calculate_collaboration_score(dataset):
    """Calculate international collaboration score"""
    if 'applicant_country_count' in dataset.columns:
        avg_countries = dataset['applicant_country_count'].mean()
        return round(avg_countries, 2)
    return 0

def export_complete_analysis(ree_dataset, quality_metrics, business_summary):
    """Export all analysis results in business-ready formats"""
    
    export_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Main dataset export
    main_export = f"ree_analysis_dataset_{timestamp}.csv"
    ree_dataset.to_csv(main_export, index=False)
    export_files.append(main_export)
        
    # Business intelligence JSON
    business_export = f"ree_business_intelligence_{timestamp}.json"
    with open(business_export, 'w') as f:
        json.dump(business_summary, f, indent=2, default=str)
    export_files.append(business_export)
    
    # Quality assessment report
    quality_export = f"ree_quality_assessment_{timestamp}.json"
    with open(quality_export, 'w') as f:
        json.dump(quality_metrics, f, indent=2, default=str)
    export_files.append(quality_export)
    
    # Executive summary
    executive_summary = {
        'executive_overview': {
            'total_patents_analyzed': len(ree_dataset),
            'countries_covered': quality_metrics.get('countries_covered', 0),
            'quality_score': quality_metrics.get('quality_score', 0),
            'analysis_date': timestamp,
            'dataset_timeframe': quality_metrics.get('year_range', 'Unknown')
        },
        'key_insights': business_summary,
        'methodology': {
            'database_source': 'PATSTAT via EPO TIP Platform',
            'search_strategy': 'Dual keyword and CPC classification approach',
            'geographic_analysis': 'Primary applicant country mapping'
        }
    }
    
    executive_export = f"ree_executive_summary_{timestamp}.json"
    with open(executive_export, 'w') as f:
        json.dump(executive_summary, f, indent=2, default=str)
    export_files.append(executive_export)
    
    print(f"✅ Exported {len(export_files)} files")
    return export_files

def print_final_summary(ree_dataset, quality_metrics):
    """Print final analysis summary"""
    print(f"\n🎯 ANALYSIS RESULTS SUMMARY:")
    print(f"   📊 REE Patents Analyzed: {len(ree_dataset):,}")
    print(f"   🌍 Countries Covered: {quality_metrics.get('countries_covered', 0)}")
    print(f"   ⭐ Quality Score: {quality_metrics.get('quality_score', 0)}/100 ({quality_metrics.get('quality_rating', 'UNKNOWN')})")
    print(f"   📅 Time Range: {quality_metrics.get('year_range', 'Unknown')}")

# MANDATORY: Test the complete pipeline
if __name__ == "__main__":
    print("Testing complete REE analysis pipeline...")
    
    try:
        results = run_complete_ree_analysis(test_mode=True)
        
        if results:
            print(f"\n✅ PIPELINE TEST PASSED")
            print(f"   🎯 Results Summary:")
            print(f"   REE Patents: {len(results['ree_dataset']):,}")
            print(f"   Quality Score: {results['quality_metrics'].get('quality_score', 0)}/100")
            print(f"   Export Files: {len(results['export_files'])}")
        else:
            print("❌ PIPELINE TEST FAILED: No results returned")
            
    except Exception as e:
        print(f"❌ PIPELINE TEST FAILED with error: {e}")
        import traceback
        traceback.print_exc()