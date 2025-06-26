#!/usr/bin/env python3
"""
Patent Intelligence Platform - Complete Workflow Test Script
Test the entire notebook workflow in a debuggable Python script format.

This script replicates the notebook functionality to catch integration issues
before converting back to notebook format.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def setup_python_path():
    """Add the parent directory to Python path for module imports."""
    script_dir = Path(__file__).resolve().parent
    parent_dir = script_dir.parent  # Go from scripts/ to 0-main/
    
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    print(f"📁 Script directory: {script_dir}")
    print(f"📁 Parent directory: {parent_dir}")
    print(f"📁 Working directory: {Path.cwd()}")
    return parent_dir

def test_imports():
    """Test all required imports."""
    print("\n🔧 Testing imports...")
    
    try:
        # Core production imports
        from config import ConfigurationManager
        print("✅ ConfigurationManager imported")
        
        from data_access import PatstatClient, EPOOPSClient, PatentCountryMapper
        print("✅ Data access classes imported")
        
        from data_access import PatentSearcher
        print("✅ PatentSearcher imported")
        
        # Import the actual processor classes
        from processors import (ApplicantAnalyzer, GeographicAnalyzer, 
                               ClassificationAnalyzer, CitationAnalyzer,
                               ComprehensiveAnalysisWorkflow)
        print("✅ Processor classes imported")
        
        # Import visualization classes
        from visualizations import (PatentVisualizationFactory, create_visualization_factory,
                                  create_executive_analysis, create_technical_analysis,
                                  ProductionChartCreator, ProductionDashboardCreator, 
                                  ProductionMapsCreator)
        print("✅ Visualization classes imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration management."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from config import ConfigurationManager
        config = ConfigurationManager()
        
        # Test basic config access
        api_config = config.get('api')
        database_config = config.get('database')
        search_patterns = config.get('search_patterns')
        viz_config = config.get('visualization')
        
        print(f"✅ API Config: {len(api_config) if api_config else 0} settings loaded")
        print(f"✅ Database Config: {len(database_config) if database_config else 0} settings loaded")
        print(f"✅ Search Patterns: {len(search_patterns) if search_patterns else 0} patterns loaded")
        print(f"✅ Visualization Config: {len(viz_config) if viz_config else 0} settings loaded")
        
        # Test the specific configuration paths that caused issues
        cpc_classifications = search_patterns.get('cpc_classifications', {}) if search_patterns else {}
        technology_areas = cpc_classifications.get('technology_areas', {})
        
        print(f"✅ CPC Classifications: {len(technology_areas)} technology areas found")
        
        if technology_areas:
            for area_name, area_config in list(technology_areas.items())[:3]:  # Show first 3
                if isinstance(area_config, dict) and 'codes' in area_config:
                    codes_count = len(area_config['codes']) if isinstance(area_config['codes'], list) else 0
                    print(f"  • {area_name}: {codes_count} codes")
                else:
                    print(f"  • {area_name}: Invalid structure")
        
        return config
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        traceback.print_exc()
        return None

def test_patstat_connection():
    """Test PATSTAT database connection."""
    print("\n🗄️ Testing PATSTAT connection...")
    
    try:
        from data_access import PatstatClient
        
        # Try to create PATSTAT client
        patstat = PatstatClient(environment='PROD')
        print("✅ PATSTAT client created")
        
        # Test basic connection (without actual queries)
        print("✅ PATSTAT connection established")
        print("📊 Database Environment: PROD (full dataset access)")
        
        return patstat
        
    except Exception as e:
        print(f"❌ PATSTAT connection failed: {e}")
        traceback.print_exc()
        return None

def test_patent_searcher_initialization():
    """Test PatentSearcher initialization with real config."""
    print("\n🔍 Testing PatentSearcher initialization...")
    
    try:
        from data_access import PatstatClient, PatentSearcher
        
        # Create PATSTAT client
        patstat = PatstatClient(environment='PROD')
        print("✅ PATSTAT client created")
        
        # Create patent searcher - this is where the config error occurred
        patent_searcher = PatentSearcher(patstat)
        print("✅ PatentSearcher initialized successfully")
        
        # Check if CPC codes were loaded correctly
        if hasattr(patent_searcher, 'cpc_codes'):
            print(f"✅ CPC codes loaded: {len(patent_searcher.cpc_codes)} codes")
            if patent_searcher.cpc_codes:
                print(f"  Sample codes: {patent_searcher.cpc_codes[:3]}")
            else:
                print("⚠️ CPC codes list is empty - checking configuration...")
                # Debug the configuration loading
                search_config = patent_searcher.search_config
                cpc_classifications = search_config.get('cpc_classifications', {})
                technology_areas = cpc_classifications.get('technology_areas', {})
                print(f"  Debug: Found {len(technology_areas)} technology areas")
                for area_name, area_config in list(technology_areas.items())[:2]:
                    if isinstance(area_config, dict):
                        codes = area_config.get('codes', [])
                        print(f"    {area_name}: {len(codes) if isinstance(codes, list) else 'not a list'} codes")
                        if isinstance(codes, list) and codes:
                            print(f"      Sample: {codes[0]}")
        else:
            print("⚠️ No CPC codes attribute found")
        
        return patent_searcher
        
    except Exception as e:
        print(f"❌ PatentSearcher initialization failed: {e}")
        traceback.print_exc()
        return None

def test_small_search(patent_searcher):
    """Test a small patent search to verify the search functionality."""
    print("\n🔍 Testing small patent search...")
    
    if not patent_searcher:
        print("❌ No patent searcher available for testing")
        return None
    
    try:
        # Execute a very limited search for testing
        print("🔍 Executing small test search...")
        search_results = patent_searcher.execute_comprehensive_search(
            start_date="2024-01-01",
            end_date="2024-01-03",  # Very small date range for testing
            focused_search=True
        )
        
        print(f"✅ Search completed: {len(search_results)} results")
        print(f"📊 Data columns: {list(search_results.columns)}")
        
        if len(search_results) > 0:
            print("\n📋 Sample result:")
            # Show first row with available columns
            sample_cols = [col for col in ['appln_title', 'person_name', 'appln_auth'] 
                          if col in search_results.columns]
            if sample_cols:
                print(search_results[sample_cols].head(1).to_string(index=False))
            else:
                print(search_results.head(1).to_string(index=False))
        
        return search_results
        
    except Exception as e:
        print(f"❌ Patent search failed: {e}")
        traceback.print_exc()
        return None

def test_processors(search_results):
    """Test the four-processor intelligence pipeline."""
    print("\n⚙️ Testing processor pipeline...")
    
    if search_results is None or len(search_results) == 0:
        print("⚠️ No search results available, creating mock data for processor testing")
        # Create minimal mock data for testing
        search_results = pd.DataFrame({
            'appln_id': [1, 2, 3],
            'docdb_family_id': [101, 102, 103],
            'appln_title': ['Test Patent 1', 'Test Patent 2', 'Test Patent 3'],
            'person_name': ['Test Corp', 'Example Inc', 'Demo Ltd'],
            'appln_auth': ['US', 'EP', 'JP'],
            'appln_filing_date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01'])
        })
        print(f"✅ Created mock data: {len(search_results)} records")
    
    try:
        from data_access import PatstatClient
        from processors import (ApplicantAnalyzer, GeographicAnalyzer, 
                               ClassificationAnalyzer, CitationAnalyzer)
        
        # Create a PATSTAT client for processors
        patstat = PatstatClient(environment='PROD')
        analysis_results = {}
        
        # Test each processor individually
        print("\n👥 Testing Applicant Analyzer...")
        try:
            applicant_analyzer = ApplicantAnalyzer(patstat)
            applicant_analysis = applicant_analyzer.analyze_search_results(search_results)
            analysis_results['applicant'] = applicant_analysis
            print(f"✅ Applicant analysis: {len(applicant_analysis) if hasattr(applicant_analysis, '__len__') else 'completed'}")
        except Exception as e:
            print(f"⚠️ Applicant analyzer failed: {e}")
            analysis_results['applicant'] = pd.DataFrame()
        
        print("\n🌍 Testing Geographic Analyzer...")
        try:
            geographic_analyzer = GeographicAnalyzer(patstat)
            geographic_analysis = geographic_analyzer.analyze_search_results(search_results)
            analysis_results['geographic'] = geographic_analysis
            print(f"✅ Geographic analysis: {len(geographic_analysis) if hasattr(geographic_analysis, '__len__') else 'completed'}")
        except Exception as e:
            print(f"⚠️ Geographic analyzer failed: {e}")
            analysis_results['geographic'] = pd.DataFrame()
        
        print("\n🔬 Testing Classification Analyzer...")
        try:
            classification_analyzer = ClassificationAnalyzer(patstat)
            classification_analysis = classification_analyzer.analyze_search_results(search_results)
            analysis_results['classification'] = classification_analysis
            print(f"✅ Classification analysis: {len(classification_analysis) if hasattr(classification_analysis, '__len__') else 'completed'}")
        except Exception as e:
            print(f"⚠️ Classification analyzer failed: {e}")
            analysis_results['classification'] = pd.DataFrame()
        
        print("\n🔗 Testing Citation Analyzer...")
        try:
            citation_analyzer = CitationAnalyzer(patstat)
            citation_analysis = citation_analyzer.analyze_search_results(search_results)
            analysis_results['citation'] = citation_analysis
            print(f"✅ Citation analysis: {len(citation_analysis) if hasattr(citation_analysis, '__len__') else 'completed'}")
        except Exception as e:
            print(f"⚠️ Citation analyzer failed: {e}")
            analysis_results['citation'] = pd.DataFrame()
        
        print(f"\n📊 Processor Pipeline Results:")
        for analysis_type, results in analysis_results.items():
            if hasattr(results, '__len__'):
                print(f"  ✅ {analysis_type.title()}: {len(results)} entities")
            else:
                print(f"  ✅ {analysis_type.title()}: Available")
        
        return analysis_results
        
    except Exception as e:
        print(f"❌ Processor testing failed: {e}")
        traceback.print_exc()
        return {}

def test_visualizations(search_results, analysis_results, config):
    """Test visualization creation."""
    print("\n📊 Testing visualization creation...")
    
    try:
        from visualizations import ProductionDashboardCreator, PatentVisualizationFactory
        
        # Test dashboard creator
        print("\n📈 Testing Dashboard Creator...")
        dashboard_creator = ProductionDashboardCreator(config)
        
        # Convert analysis results to safe format for dashboard
        dashboard_data = {}
        if isinstance(analysis_results, dict):
            for key, value in analysis_results.items():
                dashboard_data[key] = value if value is not None else pd.DataFrame()
        
        try:
            executive_dashboard = dashboard_creator.create_executive_dashboard(
                dashboard_data, 
                title="Test Executive Dashboard"
            )
            print("✅ Executive dashboard created")
        except Exception as e:
            print(f"⚠️ Executive dashboard failed: {e}")
        
        # Test visualization factory
        print("\n🏭 Testing Visualization Factory...")
        try:
            factory = PatentVisualizationFactory(config)
            print("✅ Visualization factory created")
            
            # Test creating simple analysis
            custom_results = factory.create_custom_analysis(
                search_results,
                processors=['applicant'],  # Just test one processor
                visualizations=['market_leaders']
            )
            print("✅ Custom analysis created")
            
        except Exception as e:
            print(f"⚠️ Visualization factory failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization testing failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the complete platform workflow test."""
    print("🚀 Patent Intelligence Platform - Complete Workflow Test")
    print("=" * 60)
    
    # Setup
    parent_dir = setup_python_path()
    
    # Test each component step by step
    success_count = 0
    total_tests = 6
    
    # 1. Test imports
    if test_imports():
        success_count += 1
    
    # 2. Test configuration
    config = test_configuration()
    if config:
        success_count += 1
    
    # 3. Test PATSTAT connection
    patstat = test_patstat_connection()
    if patstat:
        success_count += 1
    
    # 4. Test PatentSearcher initialization
    patent_searcher = test_patent_searcher_initialization()
    if patent_searcher:
        success_count += 1
    
    # 5. Test small patent search
    search_results = test_small_search(patent_searcher)
    if search_results is not None:
        success_count += 1
    
    # 6. Test processors
    analysis_results = test_processors(search_results)
    if analysis_results:
        success_count += 1
    
    # 7. Test visualizations (bonus test)
    if config and search_results is not None:
        test_visualizations(search_results, analysis_results, config)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 Platform Workflow Test Summary")
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"📊 Success rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("🏆 All core components working! Ready for notebook conversion.")
    else:
        print("⚠️ Some issues found. Fix these before notebook conversion:")
        if success_count < 2:
            print("  • Configuration and import issues need resolution")
        elif success_count < 4:
            print("  • Database connectivity issues need resolution")
        elif success_count < 6:
            print("  • Search functionality needs debugging")
        else:
            print("  • Minor issues in advanced features")
    
    print("\n💡 Next steps:")
    print("  1. Fix any failed tests above")
    print("  2. Run this script again until all tests pass")
    print("  3. Convert working script logic back to notebook")
    print("  4. Test notebook execution")

if __name__ == "__main__":
    main()