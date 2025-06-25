#!/usr/bin/env python3
"""
Test the data flow through processors to identify where appln_id gets lost.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from data_access import PatstatClient, PatentSearcher
from processors import GeographicAnalyzer, ClassificationAnalyzer

def test_processor_data_flow():
    """Test the data flow through processors."""
    print("🔍 Testing Processor Data Flow")
    print("=" * 50)
    
    # Create search results
    print("🔍 Creating search results...")
    patstat = PatstatClient(environment='PROD')
    searcher = PatentSearcher(patstat)
    search_results = searcher.execute_comprehensive_search(
        start_date='2024-01-01', 
        end_date='2024-01-02', 
        focused_search=True
    )
    
    print(f"✅ Search results: {search_results.shape}")
    print(f"📊 Columns: {list(search_results.columns)}")
    print(f"📈 Has appln_id: {'appln_id' in search_results.columns}")
    
    if len(search_results) > 0:
        print(f"📋 Sample appln_id values: {search_results['appln_id'].head(3).tolist()}")
    
    # Test Geographic Analyzer
    print(f"\n🌍 Testing Geographic Analyzer...")
    try:
        geo_analyzer = GeographicAnalyzer(patstat)
        print(f"✅ Geographic analyzer created")
        print(f"🔗 Session available: {geo_analyzer.session is not None}")
        
        # Try the analysis
        geo_results = geo_analyzer.analyze_search_results(search_results)
        print(f"✅ Geographic analysis completed: {len(geo_results)} results")
        if len(geo_results) > 0:
            print(f"📊 Geographic columns: {list(geo_results.columns)}")
            
    except Exception as e:
        print(f"❌ Geographic analyzer failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Classification Analyzer
    print(f"\n🔬 Testing Classification Analyzer...")
    try:
        class_analyzer = ClassificationAnalyzer(patstat)
        print(f"✅ Classification analyzer created")
        print(f"🔗 Session available: {class_analyzer.session is not None}")
        
        # Try the analysis
        class_results = class_analyzer.analyze_search_results(search_results)
        print(f"✅ Classification analysis completed: {len(class_results)} results")
        if len(class_results) > 0:
            print(f"📊 Classification columns: {list(class_results.columns)}")
            
    except Exception as e:
        print(f"❌ Classification analyzer failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_processor_data_flow()