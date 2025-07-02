# MANDATORY TESTING TEMPLATES - COPY INTO EACH MODULE
# Use these templates to prevent typos and formal mistakes

def test_database_connection():
    """Test template for database_connection.py"""
    print("Testing database_connection.py...")
    
    try:
        from database_connection_example import get_patstat_connection
        db = get_patstat_connection()
        if db:
            print("✅ Database connection test PASSED")
            return True
        else:
            print("❌ Database connection test FAILED")
            return False
    except Exception as e:
        print(f"❌ Database connection test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dataset_builder():
    """Test template for dataset_builder.py"""
    print("Testing dataset_builder.py...")
    
    try:
        from database_connection_example import get_patstat_connection
        from dataset_builder_example import build_ree_dataset
        
        db = get_patstat_connection()
        if db:
            ree_data = build_ree_dataset(db, test_mode=True)
            if not ree_data.empty:
                print(f"✅ Dataset builder test PASSED: {len(ree_data)} records")
                return True
            else:
                print("❌ Dataset builder test FAILED: No data returned")
                return False
        else:
            print("❌ Cannot test dataset builder: Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Dataset builder test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_geographic_enricher():
    """Test template for geographic_enricher.py"""
    print("Testing geographic_enricher.py...")
    
    try:
        from database_connection_example import get_patstat_connection
        from dataset_builder_example import build_ree_dataset
        from geographic_enricher_example import enrich_with_geographic_data
        
        db = get_patstat_connection()
        if db:
            ree_data = build_ree_dataset(db, test_mode=True)
            if not ree_data.empty:
                enriched_data = enrich_with_geographic_data(db, ree_data)
                if 'primary_applicant_country' in enriched_data.columns:
                    countries_found = enriched_data['primary_applicant_country'].nunique()
                    print(f"✅ Geographic enricher test PASSED: {countries_found} countries")
                    return True
                else:
                    print("❌ Geographic enricher test FAILED: No country data added")
                    return False
            else:
                print("❌ Cannot test geographic enricher: No REE data")
                return False
        else:
            print("❌ Cannot test geographic enricher: Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Geographic enricher test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_validator():
    """Test template for data_validator.py"""
    print("Testing data_validator.py...")
    
    try:
        from data_validator_example import validate_dataset_quality
        import pandas as pd
        
        # Create test data
        test_ree_data = pd.DataFrame({
            'appln_id': range(1, 101),
            'docdb_family_id': range(1, 81),
            'appln_filing_year': [2015] * 100,
            'primary_applicant_country': ['US'] * 30 + ['CN'] * 25 + ['DE'] * 20 + ['JP'] * 15 + ['KR'] * 10
        })
        
        quality_results = validate_dataset_quality(test_ree_data)
        
        if quality_results['quality_score'] > 0:
            print(f"✅ Data validator test PASSED: Score {quality_results['quality_score']}/100")
            return True
        else:
            print("❌ Data validator test FAILED: Score calculation error")
            return False
    except Exception as e:
        print(f"❌ Data validator test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_pipeline():
    """Test template for integrated_pipeline.py"""
    print("Testing integrated_pipeline.py...")
    
    try:
        from integrated_pipeline_example import run_complete_ree_analysis
        
        results = run_complete_ree_analysis(test_mode=True)
        
        if results:
            quality_score = results['quality_metrics'].get('quality_score', 0)
            print(f"✅ Integration pipeline test PASSED: Quality score {quality_score}/100")
            return True
        else:
            print("❌ Integration pipeline test FAILED: No results returned")
            return False
    except Exception as e:
        print(f"❌ Integration pipeline test FAILED with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all component tests in sequence"""
    print("COMPREHENSIVE TESTING SUITE")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Dataset Builder", test_dataset_builder),
        ("Geographic Enricher", test_geographic_enricher),
        ("Data Validator", test_data_validator),
        ("Integrated Pipeline", test_integrated_pipeline)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED - Ready for production")
    else:
        print("⚠️ Some tests failed - Review and fix before proceeding")
    
    return results

# Command line execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        test_map = {
            'database': test_database_connection,
            'dataset': test_dataset_builder,
            'geographic': test_geographic_enricher,
            'validator': test_data_validator,
            'pipeline': test_integrated_pipeline,
            'all': run_all_tests
        }
        
        if test_name in test_map:
            test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        # Run all tests by default
        run_all_tests()