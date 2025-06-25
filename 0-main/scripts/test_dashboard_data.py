#!/usr/bin/env python3
"""
Test what data the dashboard is receiving and why it might be empty.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from config import ConfigurationManager
from visualizations import ProductionDashboardCreator
from data_access import PatstatClient, PatentSearcher
from processors import ApplicantAnalyzer, GeographicAnalyzer, ClassificationAnalyzer, CitationAnalyzer

def test_dashboard_data():
    """Test what data goes into the dashboard."""
    print("📊 Testing Dashboard Data Flow")
    print("=" * 50)
    
    # Create search results and analysis
    patstat = PatstatClient(environment='PROD')
    searcher = PatentSearcher(patstat)
    search_results = searcher.execute_comprehensive_search(
        start_date='2024-01-01', 
        end_date='2024-01-02', 
        focused_search=True
    )
    
    # Run all analyses
    analysis_results = {}
    
    # Applicant analysis
    applicant_analyzer = ApplicantAnalyzer(patstat)
    analysis_results['applicant'] = applicant_analyzer.analyze_search_results(search_results)
    
    # Geographic analysis
    geographic_analyzer = GeographicAnalyzer(patstat)
    analysis_results['geographic'] = geographic_analyzer.analyze_search_results(search_results)
    
    # Classification analysis
    classification_analyzer = ClassificationAnalyzer(patstat)
    analysis_results['classification'] = classification_analyzer.analyze_search_results(search_results)
    
    # Citation analysis
    citation_analyzer = CitationAnalyzer(patstat)
    analysis_results['citation'] = citation_analyzer.analyze_search_results(search_results)
    
    print("📊 Analysis Results Summary:")
    for analysis_type, results in analysis_results.items():
        print(f"  {analysis_type}: {len(results) if hasattr(results, '__len__') else 'Available'}")
        if hasattr(results, 'columns') and len(results) > 0:
            print(f"    Columns: {list(results.columns)[:5]}{'...' if len(results.columns) > 5 else ''}")
    
    # Test dashboard creation
    print(f"\n📈 Testing Dashboard Creation...")
    config = ConfigurationManager()
    dashboard_creator = ProductionDashboardCreator(config)
    
    # Convert to the format dashboard expects
    dashboard_data = {}
    for key, value in analysis_results.items():
        dashboard_data[key] = value if value is not None else pd.DataFrame()
    
    try:
        dashboard = dashboard_creator.create_executive_dashboard(
            dashboard_data,
            title="Test Executive Dashboard"
        )
        print("✅ Dashboard created successfully!")
        
        # Check if dashboard has data
        if hasattr(dashboard, 'data') and dashboard.data:
            print(f"📊 Dashboard has {len(dashboard.data)} data traces")
        else:
            print("⚠️ Dashboard appears to be empty - checking data structure...")
            
            # Check what the dashboard creator actually receives
            for key, data in dashboard_data.items():
                print(f"    {key}: {type(data)} with {len(data) if hasattr(data, '__len__') else 'unknown'} items")
        
    except Exception as e:
        print(f"❌ Dashboard creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_data()