#!/usr/bin/env python3
"""
Check what columns the geographic data actually has for visualization.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from data_access import PatstatClient, PatentSearcher
from processors import GeographicAnalyzer

def check_geographic_data():
    """Check the structure of geographic analysis results."""
    print("🌍 Checking Geographic Data Structure")
    print("=" * 50)
    
    # Create search results
    patstat = PatstatClient(environment='PROD')
    searcher = PatentSearcher(patstat)
    search_results = searcher.execute_comprehensive_search(
        start_date='2024-01-01', 
        end_date='2024-01-02', 
        focused_search=True
    )
    
    # Run geographic analysis
    geo_analyzer = GeographicAnalyzer(patstat)
    geo_results = geo_analyzer.analyze_search_results(search_results)
    
    print(f"📊 Geographic results shape: {geo_results.shape}")
    print(f"📋 Geographic columns: {list(geo_results.columns)}")
    
    if len(geo_results) > 0:
        print(f"\n📋 Sample geographic data:")
        print(geo_results.head(2).to_string())
        
        # Check for country-related columns
        country_cols = [col for col in geo_results.columns if 'country' in col.lower()]
        print(f"\n🌍 Country-related columns: {country_cols}")
        
        # Check for region-related columns  
        region_cols = [col for col in geo_results.columns if 'region' in col.lower()]
        print(f"🗺️ Region-related columns: {region_cols}")

if __name__ == "__main__":
    check_geographic_data()