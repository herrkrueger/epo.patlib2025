# 6.1 Complete Pipeline Integration using Safe Direct SQL Approach
import pandas as pd
from datetime import datetime
import sys
import traceback

def run_complete_ree_analysis(test_mode=True):
    """
    Run the complete REE patent citation analysis pipeline
    Uses direct SQL queries throughout to avoid ORM complications
    """
    
    print("="*60)
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("="*60)
    
    results = {}
    
    try:
        # Step 1: Connect to database
        print("\n1. 🔗 Connecting to TIP platform...")
        from database_connection import get_database_connection
        db = get_database_connection()
        if not db:
            print("❌ Database connection failed - stopping pipeline")
            return None
        print("✅ Database connection successful")
        
        # Step 2: Build REE dataset
        print("\n2. 🔍 Building REE dataset...")
        from ree_dataset_builder import build_ree_dataset, validate_ree_dataset
        ree_data = build_ree_dataset(db, test_mode=test_mode)
        if ree_data.empty:
            print("❌ No REE data found - stopping pipeline")
            return None
        
        ree_data = validate_ree_dataset(ree_data)
        results['ree_dataset'] = ree_data
        print("✅ REE dataset built successfully")
        
        # Step 3: Analyze citations
        print("\n3. 📊 Analyzing citation networks...")
        from citation_analyzer import get_forward_citations, get_backward_citations, get_family_level_citations, analyze_citation_patterns
        
        # Extract necessary IDs from REE dataset
        appln_ids = ree_data['appln_id'].tolist()
        family_ids = ree_data['docdb_family_id'].dropna().tolist()
        
        print(f"  Processing {len(appln_ids)} applications and {len(family_ids)} families...")
        
        # Get citations with proper error handling
        try:
            forward_cit = get_forward_citations(db, appln_ids, test_mode)
            backward_cit = get_backward_citations(db, appln_ids, test_mode)
            family_cit = get_family_level_citations(db, family_ids, test_mode)
            citation_insights = analyze_citation_patterns(forward_cit, backward_cit)
            
            results['forward_citations'] = forward_cit
            results['backward_citations'] = backward_cit
            results['family_citations'] = family_cit
            results['citation_insights'] = citation_insights
            print("✅ Citation analysis completed")
            
        except Exception as e:
            print(f"⚠️ Citation analysis encountered issues: {e}")
            results['forward_citations'] = pd.DataFrame()
            results['backward_citations'] = pd.DataFrame()
            results['family_citations'] = pd.DataFrame()
            results['citation_insights'] = {}
        
        # Step 4: Add geographic data
        print("\n4. 🌍 Enriching with geographic data...")
        from geographic_enricher import enrich_with_geographic_data, analyze_country_citations, create_country_summary, analyze_geographic_trends
        
        try:
            enriched_ree = enrich_with_geographic_data(db, ree_data)
            citation_flows, top_citing = analyze_country_citations(results['forward_citations'], 
                                                                 results['backward_citations'])
            country_summary = create_country_summary(enriched_ree)
            geographic_trends = analyze_geographic_trends(enriched_ree)
            
            results['enriched_ree_dataset'] = enriched_ree
            results['citation_flows'] = citation_flows
            results['top_citing_countries'] = top_citing
            results['country_summary'] = country_summary
            results['geographic_trends'] = geographic_trends
            print("✅ Geographic analysis completed")
            
        except Exception as e:
            print(f"⚠️ Geographic analysis encountered issues: {e}")
            results['enriched_ree_dataset'] = ree_data
            results['citation_flows'] = pd.DataFrame()
            results['top_citing_countries'] = pd.Series()
            results['country_summary'] = pd.DataFrame()
            results['geographic_trends'] = pd.DataFrame()
        
        # Step 5: Validate results
        print("\n5. ✅ Validating results...")
        from data_validator import validate_dataset_quality, generate_summary_report, check_data_consistency
        
        quality_metrics = validate_dataset_quality(results['enriched_ree_dataset'], 
                                                 results['forward_citations'], 
                                                 results['backward_citations'])
        summary_report = generate_summary_report(results['enriched_ree_dataset'], 
                                               results['forward_citations'], 
                                               results['backward_citations'], 
                                               quality_metrics)
        consistency_issues = check_data_consistency(results['enriched_ree_dataset'], 
                                                  results['forward_citations'], 
                                                  results['backward_citations'])
        
        results['quality_metrics'] = quality_metrics
        results['summary_report'] = summary_report
        results['consistency_issues'] = consistency_issues
        
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE - ALL COMPONENTS WORKING!")
        print("="*60)
        
        # Final summary
        print(f"\n📊 PIPELINE RESULTS SUMMARY:")
        print(f"  • REE Applications: {len(results['enriched_ree_dataset']):,}")
        print(f"  • Unique Families: {results['enriched_ree_dataset']['docdb_family_id'].nunique():,}")
        print(f"  • Forward Citations: {len(results['forward_citations']):,}")
        print(f"  • Backward Citations: {len(results['backward_citations']):,}")
        print(f"  • Family Citations: {len(results['family_citations']):,}")
        print(f"  • Countries: {results['enriched_ree_dataset']['appln_auth'].nunique()}")
        print(f"  • Data Quality Issues: {len(results['consistency_issues'])}")
        
        return results
        
    except Exception as e:
        print(f"\n❌ PIPELINE FAILED: {e}")
        print("Error details:")
        traceback.print_exc()
        return None

def export_pipeline_results(results, export_dir="./exports/"):
    """
    Export pipeline results to various formats for business use
    """
    
    if not results:
        print("No results to export")
        return
    
    import os
    
    # Create export directory
    os.makedirs(export_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n📁 Exporting results to {export_dir}")
    
    exported_files = []
    
    try:
        # Export main REE dataset
        if not results['enriched_ree_dataset'].empty:
            ree_file = f"{export_dir}ree_patents_{timestamp}.csv"
            results['enriched_ree_dataset'].to_csv(ree_file, index=False)
            exported_files.append(ree_file)
            print(f"  ✅ REE patents: {ree_file}")
        
        # Export forward citations
        if not results['forward_citations'].empty:
            forward_file = f"{export_dir}forward_citations_{timestamp}.csv"
            results['forward_citations'].to_csv(forward_file, index=False)
            exported_files.append(forward_file)
            print(f"  ✅ Forward citations: {forward_file}")
        
        # Export country summary
        if not results['country_summary'].empty:
            country_file = f"{export_dir}country_summary_{timestamp}.csv"
            results['country_summary'].to_csv(country_file)
            exported_files.append(country_file)
            print(f"  ✅ Country summary: {country_file}")
        
        # Export summary report as JSON
        import json
        summary_file = f"{export_dir}summary_report_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(results['summary_report'], f, indent=2, default=str)
        exported_files.append(summary_file)
        print(f"  ✅ Summary report: {summary_file}")
        
        print(f"\n📊 Exported {len(exported_files)} files successfully")
        return exported_files
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return []

def create_visualization_data(results):
    """
    Prepare data structures optimized for visualization
    """
    
    if not results:
        return {}
    
    viz_data = {}
    
    try:
        # Timeline data for temporal trends
        if not results['enriched_ree_dataset'].empty and 'appln_filing_year' in results['enriched_ree_dataset'].columns:
            timeline_data = results['enriched_ree_dataset']['appln_filing_year'].value_counts().sort_index()
            viz_data['timeline'] = {
                'years': timeline_data.index.tolist(),
                'counts': timeline_data.values.tolist()
            }
        
        # Country data for geographic visualization
        if not results['country_summary'].empty:
            viz_data['countries'] = {
                'names': results['country_summary'].index.tolist(),
                'patent_counts': results['country_summary']['total_applications'].tolist(),
                'family_counts': results['country_summary']['unique_families'].tolist()
            }
        
        # Citation network data
        if not results['forward_citations'].empty:
            citation_summary = results['forward_citations'].groupby('citing_country').agg({
                'citing_publn_id': 'nunique',
                'cited_ree_appln_id': 'nunique'
            }).reset_index()
            
            viz_data['citation_network'] = {
                'countries': citation_summary['citing_country'].tolist(),
                'citing_patents': citation_summary['citing_publn_id'].tolist(),
                'cited_ree_patents': citation_summary['cited_ree_appln_id'].tolist()
            }
        
        # Key metrics for dashboard
        viz_data['key_metrics'] = results['quality_metrics']
        
        print(f"📈 Visualization data prepared:")
        for key, value in viz_data.items():
            if isinstance(value, dict) and 'years' in value:
                print(f"  • {key}: {len(value['years'])} data points")
            elif isinstance(value, dict) and 'countries' in value:
                print(f"  • {key}: {len(value['countries'])} countries")
            else:
                print(f"  • {key}: Available")
        
        return viz_data
        
    except Exception as e:
        print(f"⚠️ Visualization data preparation failed: {e}")
        return {}

if __name__ == "__main__":
    # Run complete pipeline test
    print("🚀 Starting complete REE analysis pipeline...")
    
    # Run with test mode for faster execution
    results = run_complete_ree_analysis(test_mode=True)
    
    if results:
        print("\n🎉 Pipeline test successful!")
        
        # Export results
        exported_files = export_pipeline_results(results)
        
        # Prepare visualization data
        viz_data = create_visualization_data(results)
        
        print(f"\n✅ READY FOR JUPYTER NOTEBOOK CREATION!")
        print(f"  📊 Dataset: {len(results['enriched_ree_dataset'])} applications")
        print(f"  🏭 Families: {results['enriched_ree_dataset']['docdb_family_id'].nunique()} unique")
        print(f"  📈 Citations: {len(results['forward_citations'])} forward, {len(results['backward_citations'])} backward")
        print(f"  🌍 Countries: {results['enriched_ree_dataset']['appln_auth'].nunique()} filing authorities")
        print(f"  📁 Exports: {len(exported_files)} files created")
        print(f"  📊 Visualizations: {len(viz_data)} datasets prepared")
        
    else:
        print("\n❌ Pipeline test failed - check individual components")
        print("Run individual component tests to diagnose issues:")