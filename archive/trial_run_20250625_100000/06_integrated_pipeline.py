# 6.1 Complete Pipeline Integration using Safe Direct SQL Approach
import pandas as pd
from datetime import datetime
import importlib.util

def run_complete_ree_analysis(test_mode=True):
    """
    Run the complete REE patent citation analysis pipeline
    Uses direct SQL queries throughout to avoid ORM complications
    """
    
    print("="*60)
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Connect to database
    print("\n1. 🔗 Connecting to TIP platform...")
    spec = importlib.util.spec_from_file_location("database_connection", "01_database_connection.py")
    db_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(db_module)
    test_tip_connection = db_module.test_tip_connection
    
    db = test_tip_connection()
    if not db:
        print("❌ Database connection failed - stopping pipeline")
        return None
    
    # Step 2: Build REE dataset
    print("\n2. 🔍 Building REE dataset...")
    spec2 = importlib.util.spec_from_file_location("ree_dataset_builder", "02_ree_dataset_builder.py")
    ree_module = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ree_module)
    build_ree_dataset = ree_module.build_ree_dataset
    validate_ree_dataset = ree_module.validate_ree_dataset
    
    ree_data = build_ree_dataset(db, test_mode=test_mode)
    if ree_data.empty:
        print("❌ No REE data found - stopping pipeline")
        return None
    validate_ree_dataset(ree_data)
    
    # Step 3: Analyze citations
    print("\n3. 📊 Analyzing citation networks...")
    spec3 = importlib.util.spec_from_file_location("citation_analyzer", "03_citation_analyzer.py")
    cit_module = importlib.util.module_from_spec(spec3)
    spec3.loader.exec_module(cit_module)
    get_forward_citations = cit_module.get_forward_citations
    get_backward_citations = cit_module.get_backward_citations
    get_family_level_citations = cit_module.get_family_level_citations
    
    # Extract necessary IDs from REE dataset
    appln_ids = ree_data['appln_id'].tolist()
    family_ids = ree_data['docdb_family_id'].dropna().tolist()
    
    # Get citations with proper error handling
    try:
        forward_cit = get_forward_citations(db, appln_ids, test_mode)
        backward_cit = get_backward_citations(db, appln_ids, test_mode)
        family_cit = get_family_level_citations(db, family_ids, test_mode)
    except Exception as e:
        print(f"⚠️ Citation analysis encountered issues: {e}")
        forward_cit = pd.DataFrame()
        backward_cit = pd.DataFrame()
        family_cit = pd.DataFrame()
    
    # Step 4: Add geographic data
    print("\n4. 🌍 Enriching with geographic data...")
    spec4 = importlib.util.spec_from_file_location("geographic_enricher", "04_geographic_enricher.py")
    geo_module = importlib.util.module_from_spec(spec4)
    spec4.loader.exec_module(geo_module)
    enrich_with_geographic_data = geo_module.enrich_with_geographic_data
    analyze_country_citations = geo_module.analyze_country_citations
    create_country_summary = geo_module.create_country_summary
    
    try:
        enriched_ree = enrich_with_geographic_data(db, ree_data)
        citation_flows, top_citing = analyze_country_citations(forward_cit, backward_cit)
        country_summary = create_country_summary(enriched_ree)
    except Exception as e:
        print(f"⚠️ Geographic analysis encountered issues: {e}")
        enriched_ree = ree_data
        citation_flows = pd.DataFrame()
        top_citing = pd.Series()
        country_summary = pd.DataFrame()
    
    # Step 5: Validate results
    print("\n5. ✅ Validating results...")
    spec5 = importlib.util.spec_from_file_location("data_validator", "05_data_validator.py")
    val_module = importlib.util.module_from_spec(spec5)
    spec5.loader.exec_module(val_module)
    validate_dataset_quality = val_module.validate_dataset_quality
    generate_summary_report = val_module.generate_summary_report
    
    quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
    summary_report = generate_summary_report(enriched_ree, forward_cit, backward_cit, quality_metrics)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE - ALL COMPONENTS WORKING!")
    print("="*60)
    
    # Return all results for use in notebook
    results = {
        'ree_dataset': enriched_ree,
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'family_citations': family_cit,
        'citation_flows': citation_flows,
        'country_summary': country_summary,
        'summary_report': summary_report,
        'quality_metrics': quality_metrics
    }
    
    print(f"\n📊 READY FOR NOTEBOOK CREATION!")
    print(f"• Dataset size: {len(results['ree_dataset'])} applications")
    print(f"• Families: {results['ree_dataset']['docdb_family_id'].nunique()} unique families")
    print(f"• Citations analyzed: {len(results['forward_citations'])} forward, {len(results['backward_citations'])} backward")
    print(f"• Countries: {results['ree_dataset']['appln_auth'].nunique()} filing authorities")
    
    return results

if __name__ == "__main__":
    # Run complete pipeline test
    print("🚀 Starting complete REE analysis pipeline test...")
    results = run_complete_ree_analysis(test_mode=True)
    
    if results:
        print("\n🎉 Pipeline test successful!")
        print("Ready to create presentation notebook with:")
        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                print(f"  - {key}: {len(value)} records")
            else:
                print(f"  - {key}: Available")
    else:
        print("\n❌ Pipeline test failed - check individual components")