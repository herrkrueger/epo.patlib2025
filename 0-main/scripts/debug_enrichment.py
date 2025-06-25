#!/usr/bin/env python3
"""
Debug the enrichment process to see what columns are returned.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from data_access import PatstatClient, PatentSearcher
from processors import GeographicAnalyzer

def debug_enrichment():
    """Debug the enrichment process step by step."""
    print("🔍 Debugging Enrichment Process")
    print("=" * 50)
    
    # Create search results
    patstat = PatstatClient(environment='PROD')
    searcher = PatentSearcher(patstat)
    search_results = searcher.execute_comprehensive_search(
        start_date='2024-01-01', 
        end_date='2024-01-02', 
        focused_search=True
    )
    
    print(f"📊 Original search results: {search_results.shape}")
    print(f"📋 Original columns: {list(search_results.columns)}")
    
    # Create geographic analyzer
    geo_analyzer = GeographicAnalyzer(patstat)
    
    # Test the enrichment method directly
    print(f"\n🔍 Testing enrichment method directly...")
    try:
        enriched_data = geo_analyzer._enrich_with_geographic_data(search_results)
        print(f"✅ Enrichment returned: {enriched_data.shape}")
        print(f"📋 Enriched columns: {list(enriched_data.columns)}")
        print(f"📈 Has appln_id: {'appln_id' in enriched_data.columns}")
        
        if len(enriched_data) > 0:
            print(f"📋 Sample enriched row keys: {list(enriched_data.iloc[0].keys())}")
            
    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_enrichment()