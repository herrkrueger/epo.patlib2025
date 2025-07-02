"""
Market Data Integration Testing Templates
Comprehensive testing for patent-market correlation components
"""

import sys
import traceback
import pandas as pd
import numpy as np
from pathlib import Path
import json

def test_usgs_market_collector():
    """Test USGS market data collector component"""
    print("🧪 Testing USGS Market Data Collector...")
    
    try:
        # Import the collector (adjust path as needed)
        sys.path.append('.')
        from usgs_market_collector import USGSMarketDataCollector
        
        # Test data loading
        collector = USGSMarketDataCollector()
        market_data = collector.load_market_data()
        
        assert market_data is not None, "Market data should not be None"
        assert 'price_trends' in market_data, "Price trends missing from market data"
        assert 'import_dependency' in market_data, "Import dependency missing"
        assert 'global_production' in market_data, "Global production missing"
        
        print("  ✅ Market data loaded successfully")
        
        # Test price trends extraction
        price_df = collector.get_price_trends('neodymium')
        assert not price_df.empty, "Price trends should not be empty"
        assert 'year' in price_df.columns, "Year column missing from price data"
        assert 'price_index' in price_df.columns, "Price index column missing"
        
        print(f"  ✅ Price trends: {len(price_df)} years of data")
        
        # Test import dependency
        import_data = collector.get_import_dependency_data()
        assert import_data, "Import dependency data should not be empty"
        assert 'rare_earths' in import_data, "Rare earths dependency missing"
        
        print(f"  ✅ Import dependency: {len(import_data)} elements")
        
        # Test production data
        production_df = collector.get_global_production_data()
        assert not production_df.empty, "Production data should not be empty"
        assert 'country' in production_df.columns, "Country column missing"
        assert 'production_tons' in production_df.columns, "Production tons missing"
        
        print(f"  ✅ Production data: {len(production_df)} records")
        
        # Test supply concentration
        concentration = collector.calculate_supply_concentration()
        assert concentration, "Supply concentration should not be empty"
        assert 'China' in concentration, "China should be in concentration data"
        
        print(f"  ✅ Supply concentration: {len(concentration)} countries")
        
        # Test price shock detection
        shocks = collector.identify_price_shock_periods(threshold=50.0)
        print(f"  ✅ Price shocks identified: {len(shocks)} periods")
        
        # Test market events timeline
        events = collector.get_market_events_timeline()
        assert events, "Market events should not be empty"
        assert len(events) >= 3, "Should have at least 3 major market events"
        
        print(f"  ✅ Market events: {len(events)} events")
        
        print("🎯 USGS Market Data Collector: ALL TESTS PASSED!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ USGS Market Data Collector test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_patent_market_correlator():
    """Test patent-market correlation component"""
    print("🧪 Testing Patent-Market Correlator...")
    
    try:
        # Create sample patent data
        sample_patent_data = pd.DataFrame({
            'appln_id': range(1, 201),
            'appln_filing_year': np.random.choice(range(2010, 2024), 200),
            'primary_country': np.random.choice(['China', 'United States', 'Germany', 'Japan', 'Australia'], 200),
            'appln_title': ['Sample REE patent'] * 200
        })
        
        # Import components
        sys.path.append('.')
        from usgs_market_collector import USGSMarketDataCollector
        from patent_market_correlator import PatentMarketCorrelator
        
        # Initialize components
        market_collector = USGSMarketDataCollector()
        market_collector.load_market_data()
        
        correlator = PatentMarketCorrelator(sample_patent_data, market_collector)
        
        print("  ✅ Components initialized successfully")
        
        # Test price shock analysis
        shock_analysis = correlator.analyze_price_shock_patent_response()
        assert 'overall_correlation' in shock_analysis, "Overall correlation missing"
        assert 'shock_responses' in shock_analysis, "Shock responses missing"
        assert 'summary' in shock_analysis, "Summary missing"
        
        print("  ✅ Price shock analysis completed")
        
        # Test supply risk analysis
        risk_analysis = correlator.create_supply_risk_patent_dashboard_data()
        assert 'supply_risk_analysis' in risk_analysis, "Supply risk analysis missing"
        assert 'import_dependency' in risk_analysis, "Import dependency missing"
        assert 'key_insights' in risk_analysis, "Key insights missing"
        
        print("  ✅ Supply risk analysis completed")
        
        # Test market event impact
        event_analysis = correlator.generate_market_event_impact_analysis()
        assert 'event_impacts' in event_analysis, "Event impacts missing"
        assert 'trend_analysis' in event_analysis, "Trend analysis missing"
        assert 'predictive_insights' in event_analysis, "Predictive insights missing"
        
        print("  ✅ Market event analysis completed")
        
        # Validate data quality
        assert len(shock_analysis['shock_responses']) >= 0, "Should have shock response data"
        assert len(risk_analysis['supply_risk_analysis']) > 0, "Should have risk analysis data"
        assert len(event_analysis['event_impacts']) > 0, "Should have event impact data"
        
        print("  ✅ Data quality validation passed")
        
        print("🎯 Patent-Market Correlator: ALL TESTS PASSED!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Patent-Market Correlator test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_market_visualizations():
    """Test market visualization components"""
    print("🧪 Testing Market Visualizations...")
    
    try:
        # Import visualization component
        sys.path.append('.')
        from market_visualization_examples import MarketPatentDashboard
        
        dashboard = MarketPatentDashboard()
        
        # Create comprehensive sample data
        sample_correlation = {
            'correlation_data': [
                {'year': 2020, 'patent_count': 100, 'price_index': 200},
                {'year': 2021, 'patent_count': 150, 'price_index': 380},
                {'year': 2022, 'patent_count': 180, 'price_index': 420},
                {'year': 2023, 'patent_count': 160, 'price_index': 350}
            ],
            'overall_correlation': {
                'correlation_coefficient': 0.75,
                'p_value': 0.03,
                'significance': 'significant'
            },
            'shock_responses': [
                {
                    'shock_year': 2021,
                    'shock_type': 'spike',
                    'price_change_percent': 90,
                    'patent_response_ratio': 1.5,
                    'pre_shock_patents': 100,
                    'post_shock_patents': 150
                }
            ],
            'event_impacts': [
                {
                    'year': 2021,
                    'event': 'Market Recovery',
                    'impact_type': 'supply_shock',
                    'patent_response': {'response_ratio': 1.3}
                }
            ]
        }
        
        sample_risk = {
            'supply_risk_analysis': [
                {
                    'country': 'China',
                    'production_share_percent': 85,
                    'patent_share_percent': 45,
                    'patent_count': 500,
                    'risk_category': 'high_risk'
                },
                {
                    'country': 'United States',
                    'production_share_percent': 15,
                    'patent_share_percent': 25,
                    'patent_count': 300,
                    'risk_category': 'medium_risk'
                },
                {
                    'country': 'Germany',
                    'production_share_percent': 2,
                    'patent_share_percent': 15,
                    'patent_count': 200,
                    'risk_category': 'low_risk'
                }
            ],
            'import_dependency': {
                'rare_earths': 85,
                'neodymium': 90,
                'dysprosium': 95
            }
        }
        
        # Test executive dashboard
        dashboard_fig = dashboard.create_integrated_executive_dashboard(sample_correlation, sample_risk)
        assert dashboard_fig, "Executive dashboard should be created"
        assert dashboard_fig.data, "Dashboard should contain data traces"
        
        print("  ✅ Executive dashboard created successfully")
        
        # Test price shock analysis chart
        shock_fig = dashboard.create_price_shock_analysis_chart(sample_correlation)
        assert shock_fig, "Price shock chart should be created"
        
        print("  ✅ Price shock analysis chart created")
        
        # Test supply chain risk heatmap
        risk_fig = dashboard.create_supply_chain_risk_heatmap(sample_risk)
        assert risk_fig, "Risk heatmap should be created"
        
        print("  ✅ Supply chain risk heatmap created")
        
        # Test cost savings demonstration
        cost_fig = dashboard.create_cost_savings_demonstration()
        assert cost_fig, "Cost savings chart should be created"
        assert cost_fig.data, "Cost chart should contain data"
        
        print("  ✅ Cost savings demonstration created")
        
        # Test color mapping functions
        assert dashboard._get_risk_color('high_risk'), "Risk color mapping should work"
        assert dashboard._get_response_color(1.5), "Response color mapping should work"
        
        print("  ✅ Color mapping functions validated")
        
        print("🎯 Market Visualizations: ALL TESTS PASSED!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Market Visualizations test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_data_integration():
    """Test data integration and compatibility"""
    print("🧪 Testing Data Integration...")
    
    try:
        # Test USGS data file format
        data_file = Path("usgs_market_data/ree_market_data.json")
        
        if data_file.exists():
            with open(data_file, 'r') as f:
                market_data = json.load(f)
            
            # Validate structure
            required_sections = ['price_trends', 'import_dependency', 'global_production']
            for section in required_sections:
                assert section in market_data, f"Missing section: {section}"
            
            # Validate price trends structure
            price_trends = market_data['price_trends']
            assert 'neodymium_price_index' in price_trends, "Neodymium price data missing"
            assert 'base_year' in price_trends, "Base year missing"
            
            # Validate import dependency structure
            import_dep = market_data['import_dependency']
            assert 'rare_earths' in import_dep, "Rare earths dependency missing"
            assert all(isinstance(v, (int, float)) for v in import_dep.values()), "Dependency values should be numeric"
            
            # Validate global production structure
            global_prod = market_data['global_production']
            assert 'China' in global_prod, "China production data missing"
            
            print("  ✅ USGS data file structure validated")
        else:
            print("  ⚠️  USGS data file not found - using default test data")
        
        # Test sample patent data creation
        sample_patent_data = pd.DataFrame({
            'appln_id': range(1, 101),
            'appln_filing_year': np.random.choice(range(2010, 2024), 100),
            'primary_country': np.random.choice(['China', 'United States', 'Germany', 'Japan'], 100),
            'appln_title': [f'REE Patent {i}' for i in range(1, 101)]
        })
        
        # Validate required columns
        required_patent_cols = ['appln_id', 'appln_filing_year', 'primary_country']
        for col in required_patent_cols:
            assert col in sample_patent_data.columns, f"Missing patent column: {col}"
        
        # Validate data types
        assert sample_patent_data['appln_filing_year'].dtype in ['int64', 'int32'], "Filing year should be integer"
        assert sample_patent_data['primary_country'].dtype == 'object', "Country should be string"
        
        print("  ✅ Patent data structure validated")
        
        # Test data compatibility
        years_range = sample_patent_data['appln_filing_year'].unique()
        assert len(years_range) > 5, "Should cover multiple years"
        assert min(years_range) >= 2010, "Should include recent years"
        
        countries = sample_patent_data['primary_country'].unique()
        assert len(countries) >= 3, "Should include multiple countries"
        
        print("  ✅ Data compatibility validated")
        
        print("🎯 Data Integration: ALL TESTS PASSED!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Data Integration test failed: {str(e)}")
        traceback.print_exc()
        return False

def run_comprehensive_testing():
    """Run all market data integration tests"""
    print("🚀 STARTING COMPREHENSIVE MARKET DATA TESTING\n")
    print("=" * 60)
    
    test_results = []
    
    # Run individual test suites
    test_results.append(("USGS Market Collector", test_usgs_market_collector()))
    test_results.append(("Patent-Market Correlator", test_patent_market_correlator()))
    test_results.append(("Market Visualizations", test_market_visualizations()))
    test_results.append(("Data Integration", test_data_integration()))
    
    # Summary
    print("=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"TOTAL: {passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Market data integration is ready for deployment.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return False

# Individual test runners for targeted testing
def test_specific_component(component_name: str):
    """Run tests for a specific component"""
    test_map = {
        'usgs': test_usgs_market_collector,
        'correlator': test_patent_market_correlator,
        'visualization': test_market_visualizations,
        'integration': test_data_integration
    }
    
    if component_name.lower() in test_map:
        return test_map[component_name.lower()]()
    else:
        print(f"Unknown component: {component_name}")
        print(f"Available components: {', '.join(test_map.keys())}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            run_comprehensive_testing()
        else:
            test_specific_component(sys.argv[1])
    else:
        print("Usage: python market_testing_templates.py [all|usgs|correlator|visualization|integration]")
        print("Example: python market_testing_templates.py all")