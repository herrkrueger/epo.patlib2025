def run_complete_ree_analysis(test_mode=True):
    """Complete REE analysis pipeline"""
    
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("=" * 40)
    
    # Step 1: Connect
    from database_connection import test_tip_connection
    print("Step 1: Database Connection")
    db = test_tip_connection()
    if not db:
        print("❌ Pipeline failed: No database connection")
        return None
    
    # Step 2: Build dataset
    from dataset_builder import build_ree_dataset, validate_ree_dataset
    print("\nStep 2: Dataset Building")
    ree_data = build_ree_dataset(db, test_mode)
    if ree_data.empty:
        print("❌ Pipeline failed: No REE data found")
        return None
    validate_ree_dataset(ree_data)
    
    # Step 3: Analyze citations
    from citation_analyzer import get_forward_citations, get_backward_citations
    print("\nStep 3: Citation Analysis")
    appln_ids = ree_data['appln_id'].tolist()
    
    forward_cit = get_forward_citations(db, appln_ids, test_mode)
    backward_cit = get_backward_citations(db, appln_ids, test_mode)
    
    # Step 4: Add geography
    from geographic_enricher import enrich_with_geographic_data, analyze_country_citations
    print("\nStep 4: Geographic Enrichment")
    enriched_ree = enrich_with_geographic_data(db, ree_data)
    top_citing = analyze_country_citations(forward_cit)
    
    # Step 5: Validate
    from data_validator import validate_dataset_quality, generate_summary_report
    print("\nStep 5: Quality Validation")
    quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
    summary_report = generate_summary_report(enriched_ree, forward_cit, quality_metrics)
    
    print("\n" + "=" * 40)
    print("✅ PIPELINE COMPLETE")
    print("=" * 40)
    
    return {
        'ree_dataset': enriched_ree,
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'summary_report': summary_report,
        'quality_metrics': quality_metrics
    }

if __name__ == "__main__":
    results = run_complete_ree_analysis(test_mode=True)
    
    if results:
        print(f"\nFinal Results Summary:")
        print(f"- REE Dataset: {len(results['ree_dataset'])} applications")
        print(f"- Forward Citations: {len(results['forward_citations'])}")
        print(f"- Backward Citations: {len(results['backward_citations'])}")
        print(f"- Quality Score: {results['quality_metrics']['total_families']}/{results['quality_metrics']['total_applications']} families/apps")