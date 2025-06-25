#!/usr/bin/env python3
"""
Complete test to verify all fixes are working.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from data_access import PatstatClient, PatentSearcher
from processors import ApplicantAnalyzer, GeographicAnalyzer, ClassificationAnalyzer, CitationAnalyzer
from visualizations import ProductionMapsCreator
from config import ConfigurationManager

def test_complete_platform():
    """Test the complete platform end-to-end."""
    print("🚀 Complete Platform Test")
    print("=" * 50)
    
    # 1. Search
    print("🔍 Step 1: Patent Search...")
    patstat = PatstatClient(environment='PROD')
    searcher = PatentSearcher(patstat)
    
    # Test technology-specific search with proper date range
    search_results = searcher.execute_technology_specific_search(
        technology_areas=['rare_earth_elements'],
        start_date='2024-01-01', 
        end_date='2024-01-07',  # Full week for better results
        focused_search=True
    )
    print(f"✅ Found {len(search_results)} patents")
    
    # 2. Processing
    print(f"\n⚙️ Step 2: Four-Processor Analysis...")
    processors = [
        ("Applicant", ApplicantAnalyzer),
        ("Geographic", GeographicAnalyzer),
        ("Classification", ClassificationAnalyzer),
        ("Citation", CitationAnalyzer)
    ]
    
    analysis_results = {}
    for name, ProcessorClass in processors:
        try:
            processor = ProcessorClass(patstat)
            results = processor.analyze_search_results(search_results)
            analysis_results[name.lower()] = results
            print(f"✅ {name}: {len(results)} entities analyzed")
        except Exception as e:
            print(f"❌ {name}: {e}")
            analysis_results[name.lower()] = None
    
    # 3. Visualization
    print(f"\n📊 Step 3: Visualization...")
    config = ConfigurationManager()
    
    # Test geographic visualization
    if analysis_results['geographic'] is not None and len(analysis_results['geographic']) > 0:
        try:
            maps_creator = ProductionMapsCreator(config)
            global_map = maps_creator.create_patent_choropleth(
                {'country_summary': analysis_results['geographic']},
                title="Test Global Map"
            )
            print("✅ Geographic map created successfully")
        except Exception as e:
            print(f"⚠️ Geographic map: {e}")
    
    # Summary
    print(f"\n📈 Platform Summary:")
    print(f"  🔍 Patents: {len(search_results)}")
    working_processors = sum(1 for r in analysis_results.values() if r is not None and len(r) > 0)
    print(f"  ⚙️ Working processors: {working_processors}/4")
    total_entities = sum(len(r) for r in analysis_results.values() if r is not None and hasattr(r, '__len__'))
    print(f"  📊 Total entities: {total_entities}")
    
    if working_processors >= 3:
        print("🎉 Platform is ready for EPO PATLIB 2025 demo!")
    else:
        print("⚠️ Some processors need attention")
    
    return analysis_results

if __name__ == "__main__":
    test_complete_platform()