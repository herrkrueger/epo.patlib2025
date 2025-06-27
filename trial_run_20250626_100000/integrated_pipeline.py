"""
REE Patent Citation Analysis - Integrated Pipeline
Complete workflow for REE patent analysis with citation and geographic intelligence
"""

import pandas as pd
from datetime import datetime
import traceback

def run_complete_ree_analysis(test_mode=True, export_results=True):
    """Complete REE analysis pipeline"""
    
    print("=" * 60)
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    print(f"Test Mode: {test_mode}")
    print()
    
    results = {
        'pipeline_status': 'started',
        'components_status': {},
        'data': {},
        'exports': {},
        'errors': []
    }
    
    try:
        # Step 1: Database Connection
        print("🔗 STEP 1: Connecting to PATSTAT...")
        from database_connection import test_tip_connection
        db = test_tip_connection()
        
        if not db:
            results['pipeline_status'] = 'failed'
            results['errors'].append('Database connection failed')
            return results
        
        results['components_status']['database'] = 'success'
        print("✅ Database connection established")
        print()
        
        # Step 2: Dataset Building
        print("📊 STEP 2: Building REE dataset...")
        from dataset_builder import build_ree_dataset, validate_ree_dataset
        ree_data = build_ree_dataset(db, test_mode)
        
        if ree_data.empty:
            results['pipeline_status'] = 'failed'
            results['errors'].append('No REE data found')
            return results
        
        dataset_valid = validate_ree_dataset(ree_data)
        results['components_status']['dataset_builder'] = 'success' if dataset_valid else 'warning'
        results['data']['ree_dataset'] = ree_data
        print("✅ REE dataset built successfully")
        print()
        
        # Step 3: Citation Analysis
        print("🔍 STEP 3: Analyzing citations...")
        from citation_analyzer import get_forward_citations, get_backward_citations, analyze_citation_patterns
        
        appln_ids = ree_data['appln_id'].tolist()
        
        forward_cit = get_forward_citations(db, appln_ids, test_mode)
        backward_cit = get_backward_citations(db, appln_ids, test_mode)
        citation_analysis = analyze_citation_patterns(forward_cit, backward_cit)
        
        results['components_status']['citation_analyzer'] = 'success'
        results['data']['forward_citations'] = forward_cit
        results['data']['backward_citations'] = backward_cit
        results['data']['citation_analysis'] = citation_analysis
        print("✅ Citation analysis completed")
        print()
        
        # Step 4: Geographic Enrichment
        print("🌍 STEP 4: Geographic enrichment...")
        from geographic_enricher import (
            enrich_with_geographic_data, 
            analyze_country_citations, 
            get_geographic_distribution,
            create_citation_network_data
        )
        
        enriched_ree = enrich_with_geographic_data(db, ree_data)
        geo_stats = get_geographic_distribution(enriched_ree)
        top_citing = analyze_country_citations(forward_cit)
        network_data = create_citation_network_data(enriched_ree, forward_cit, backward_cit)
        
        results['components_status']['geographic_enricher'] = 'success'
        results['data']['enriched_dataset'] = enriched_ree
        results['data']['geographic_stats'] = geo_stats
        results['data']['top_citing_countries'] = top_citing
        results['data']['network_data'] = network_data
        print("✅ Geographic enrichment completed")
        print()
        
        # Step 5: Data Validation
        print("✅ STEP 5: Data validation...")
        from data_validator import validate_dataset_quality, generate_summary_report, export_validation_results
        
        quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
        summary_report = generate_summary_report(enriched_ree, forward_cit, quality_metrics)
        
        results['components_status']['data_validator'] = 'success'
        results['data']['quality_metrics'] = quality_metrics
        results['data']['summary_report'] = summary_report
        print("✅ Data validation completed")
        print()
        
        # Step 6: Export Results
        if export_results:
            print("💾 STEP 6: Exporting results...")
            
            export_status = {}
            
            # Export main datasets
            try:
                enriched_ree.to_csv('ree_dataset_enriched.csv', index=False)
                export_status['ree_dataset'] = 'success'
            except Exception as e:
                export_status['ree_dataset'] = f'failed: {e}'
            
            if not forward_cit.empty:
                try:
                    forward_cit.to_csv('ree_forward_citations.csv', index=False)
                    export_status['forward_citations'] = 'success'
                except Exception as e:
                    export_status['forward_citations'] = f'failed: {e}'
            
            if not backward_cit.empty:
                try:
                    backward_cit.to_csv('ree_backward_citations.csv', index=False)
                    export_status['backward_citations'] = 'success'
                except Exception as e:
                    export_status['backward_citations'] = f'failed: {e}'
            
            # Export validation results
            try:
                validation_export = export_validation_results(quality_metrics, summary_report)
                export_status['validation'] = 'success' if validation_export else 'failed'
            except Exception as e:
                export_status['validation'] = f'failed: {e}'
            
            # Export network data
            if network_data and network_data['nodes']:
                try:
                    import json
                    with open('ree_citation_network.json', 'w') as f:
                        json.dump(network_data, f, indent=2)
                    export_status['network_data'] = 'success'
                except Exception as e:
                    export_status['network_data'] = f'failed: {e}'
            
            results['exports'] = export_status
            print("✅ Results exported")
            print()
        
        # Final Pipeline Status
        results['pipeline_status'] = 'success'
        
        print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("FINAL SUMMARY:")
        print(f"• REE Applications: {len(enriched_ree)}")
        print(f"• Patent Families: {enriched_ree['docdb_family_id'].nunique()}")
        print(f"• Forward Citations: {len(forward_cit)}")
        print(f"• Backward Citations: {len(backward_cit)}")
        print(f"• Countries: {enriched_ree['appln_auth'].nunique()}")
        print(f"• Quality Score: {quality_metrics['quality_score']}/100")
        
        if export_results:
            successful_exports = sum(1 for status in export_status.values() if status == 'success')
            print(f"• Exports: {successful_exports}/{len(export_status)} successful")
        
        print("=" * 60)
        
        return results
        
    except Exception as e:
        error_msg = f"Pipeline failed: {str(e)}"
        print(f"❌ {error_msg}")
        print("Traceback:")
        traceback.print_exc()
        
        results['pipeline_status'] = 'error'
        results['errors'].append(error_msg)
        return results
    
    finally:
        print(f"Pipeline ended at: {datetime.now()}")

def run_quick_test():
    """Quick test of all components"""
    
    print("🧪 QUICK COMPONENT TEST")
    print("=" * 40)
    
    test_results = {}
    
    # Test 1: Database Connection
    try:
        from database_connection import test_tip_connection
        db = test_tip_connection()
        test_results['database'] = 'pass' if db else 'fail'
    except Exception as e:
        test_results['database'] = f'error: {e}'
    
    # Test 2: Dataset Builder
    try:
        from dataset_builder import build_ree_dataset
        if db:
            ree_data = build_ree_dataset(db, test_mode=True)
            test_results['dataset_builder'] = 'pass' if not ree_data.empty else 'no_data'
        else:
            test_results['dataset_builder'] = 'skip_no_db'
    except Exception as e:
        test_results['dataset_builder'] = f'error: {e}'
    
    # Test 3: Citation Analyzer
    try:
        from citation_analyzer import get_forward_citations, get_backward_citations
        test_results['citation_analyzer'] = 'pass'
    except Exception as e:
        test_results['citation_analyzer'] = f'error: {e}'
    
    # Test 4: Geographic Enricher
    try:
        from geographic_enricher import enrich_with_geographic_data
        test_results['geographic_enricher'] = 'pass'
    except Exception as e:
        test_results['geographic_enricher'] = f'error: {e}'
    
    # Test 5: Data Validator
    try:
        from data_validator import validate_dataset_quality
        test_results['data_validator'] = 'pass'
    except Exception as e:
        test_results['data_validator'] = f'error: {e}'
    
    # Print results
    for component, status in test_results.items():
        emoji = "✅" if status == 'pass' else "⚠️" if 'no_data' in status or 'skip' in status else "❌"
        print(f"{emoji} {component}: {status}")
    
    passed = sum(1 for status in test_results.values() if status == 'pass')
    total = len(test_results)
    print(f"\nTest Results: {passed}/{total} components passed")
    
    return test_results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Quick test mode
        run_quick_test()
    else:
        # Full pipeline
        results = run_complete_ree_analysis(test_mode=True, export_results=True)
        
        if results['pipeline_status'] == 'success':
            print("\n🚀 Ready for Jupyter notebook creation!")
        else:
            print(f"\n❌ Pipeline issues: {results['errors']}")