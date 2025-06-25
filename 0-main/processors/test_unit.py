#!/usr/bin/env python3
"""
Unit Tests for Individual Processors
Enhanced from EPO PATLIB 2025 Live Demo Code

This script tests each processor individually to ensure core functionality.
Use this for debugging specific processor issues.

Usage:
    python processors/test_unit.py
    python processors/test_unit.py --processor search
    python processors/test_unit.py --processor applicant
"""

import sys
import os
from pathlib import Path
import logging
import pandas as pd
import time
from typing import Dict, Any, List
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def setup_logging():
    """Setup test logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger(__name__)

def print_section(title: str, char: str = '=', width: int = 60):
    """Print a formatted section header."""
    print(f'\n{title}')
    print(char * width)

def print_subsection(title: str):
    """Print a formatted subsection header."""
    print(f'\n{title}')
    print('-' * 40)

def test_search_processor():
    """Test PatentSearchProcessor individually."""
    print_section('🔍 Search Processor Unit Test')
    
    try:
        from processors import create_patent_search_processor
        
        print_subsection('Initialization & Configuration')
        processor = create_patent_search_processor()
        config = processor.config
        print(f'   ✅ Processor created with {len(config)} config sections')
        
        print_subsection('Keyword Extraction')
        keywords = processor._get_all_configured_keywords()
        print(f'   ✅ Extracted {len(keywords)} keywords')
        
        print_subsection('PATSTAT Connection')
        if processor.patstat_client:
            print('   ✅ PATSTAT client available')
        else:
            print('   ⚠️ No PATSTAT client (testing mode)')
            
        print_subsection('Search Logic Test')
        empty_results = processor._combine_search_results([], 'intersection')
        print(f'   ✅ Empty result handling: {len(empty_results)} families')
        
        return True
        
    except Exception as e:
        print(f'❌ Search processor test failed: {e}')
        return False

def test_applicant_processor():
    """Test ApplicantAnalyzer individually."""
    print_section('👥 Applicant Processor Unit Test')
    
    try:
        from processors import create_applicant_analyzer
        import pandas as pd
        import numpy as np
        
        print_subsection('Initialization')
        analyzer = create_applicant_analyzer()
        print('   ✅ Applicant analyzer created')
        
        print_subsection('Mock Data Processing')
        mock_search_results = pd.DataFrame({
            'docdb_family_id': [12345, 23456],
            'quality_score': [3, 2],
            'match_type': ['intersection', 'keyword'],
            'earliest_filing_year': [2020, 2019],
            'family_size': [5, 3]
        })
        
        result = analyzer.analyze_search_results(mock_search_results)
        print(f'   ✅ Processed {len(result)} applicant records')
        print(f'   📊 Columns: {len(result.columns)} attributes')
        
        print_subsection('Summary Generation')
        summary = analyzer.get_applicant_summary()
        print(f'   ✅ Summary generated: {summary["status"]}')
        
        return True
        
    except Exception as e:
        print(f'❌ Applicant processor test failed: {e}')
        return False

def test_classification_processor():
    """Test ClassificationAnalyzer individually."""
    print_section('🏷️ Classification Processor Unit Test')
    
    try:
        from processors import create_classification_analyzer
        import pandas as pd
        
        print_subsection('Initialization')
        analyzer = create_classification_analyzer()
        print('   ✅ Classification analyzer created')
        
        print_subsection('Mock Data Processing')
        mock_search_results = pd.DataFrame({
            'docdb_family_id': [12345, 23456],
            'quality_score': [3, 2],
            'match_type': ['intersection', 'keyword'],
            'earliest_filing_year': [2020, 2019],
            'family_size': [5, 3]
        })
        
        result = analyzer.analyze_search_results(mock_search_results)
        print(f'   ✅ Processed {len(result)} classification records')
        if not result.empty:
            print(f'   📊 Columns: {len(result.columns)} attributes')
        
        return True
        
    except Exception as e:
        print(f'❌ Classification processor test failed: {e}')
        return False

def test_citation_processor():
    """Test CitationAnalyzer individually."""
    print_section('🔗 Citation Processor Unit Test')
    
    try:
        from processors import create_citation_analyzer
        import pandas as pd
        
        print_subsection('Initialization')
        analyzer = create_citation_analyzer()
        print('   ✅ Citation analyzer created')
        
        print_subsection('Mock Data Processing')
        mock_search_results = pd.DataFrame({
            'docdb_family_id': [12345, 23456],
            'quality_score': [3, 2],
            'match_type': ['intersection', 'keyword'],
            'earliest_filing_year': [2020, 2019],
            'family_size': [5, 3]
        })
        
        result = analyzer.analyze_search_results(mock_search_results)
        print(f'   ✅ Processed {len(result)} citation records')
        if not result.empty:
            print(f'   📊 Columns: {len(result.columns)} attributes')
        else:
            print('   📝 No citation data (expected with mock family IDs)')
        
        return True
        
    except Exception as e:
        print(f'❌ Citation processor test failed: {e}')
        return False

def test_geographic_processor():
    """Test GeographicAnalyzer individually."""
    print_section('🌍 Geographic Processor Unit Test')
    
    try:
        from processors import create_geographic_analyzer
        import pandas as pd
        
        print_subsection('Initialization')
        analyzer = create_geographic_analyzer()
        print('   ✅ Geographic analyzer created')
        
        print_subsection('Mock Data Processing')
        mock_search_results = pd.DataFrame({
            'docdb_family_id': [12345, 23456],
            'quality_score': [3, 2],
            'match_type': ['intersection', 'keyword'],
            'earliest_filing_year': [2020, 2019],
            'family_size': [5, 3]
        })
        
        result = analyzer.analyze_search_results(mock_search_results)
        print(f'   ✅ Processed {len(result)} geographic records')
        if not result.empty:
            print(f'   📊 Columns: {len(result.columns)} attributes')
        else:
            print('   📝 No geographic data (expected with mock family IDs)')
        
        return True
        
    except Exception as e:
        print(f'❌ Geographic processor test failed: {e}')
        return False

def run_all_unit_tests():
    """Run all unit tests."""
    tests = [
        ('Search Processor', test_search_processor),
        ('Applicant Processor', test_applicant_processor),
        ('Classification Processor', test_classification_processor),
        ('Citation Processor', test_citation_processor),
        ('Geographic Processor', test_geographic_processor)
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
    return results

def generate_unit_test_report(results: Dict[str, bool]) -> str:
    """Generate unit test report."""
    print_section('📋 Unit Test Results Summary', '=', 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f'Total Unit Tests: {total_tests}')
    print(f'Passed: {passed_tests} ✅')
    print(f'Failed: {failed_tests} ❌')
    print(f'Success Rate: {(passed_tests/total_tests)*100:.1f}%')
    
    print('\nDetailed Results:')
    for test_name, passed in results.items():
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f'   {status} {test_name}')
    
    if failed_tests == 0:
        print('\n🎉 All unit tests passed!')
        return 'SUCCESS'
    else:
        print(f'\n⚠️ {failed_tests} unit test(s) failed.')
        return 'FAILURE'

def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(description='Unit tests for individual processors')
    parser.add_argument('--processor', choices=['search', 'applicant', 'classification', 'citation', 'geographic'], 
                       help='Test only a specific processor')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    print('🔬 Patent Analysis Platform - Unit Tests')
    print('Enhanced from EPO PATLIB 2025 Live Demo Code')
    print('=' * 60)
    
    if args.processor:
        # Test specific processor
        processor_tests = {
            'search': test_search_processor,
            'applicant': test_applicant_processor,
            'classification': test_classification_processor,
            'citation': test_citation_processor,
            'geographic': test_geographic_processor
        }
        
        test_func = processor_tests[args.processor]
        result = test_func()
        
        print(f'\n📊 {args.processor.title()} Processor Test: {"PASS" if result else "FAIL"}')
        return 0 if result else 1
    
    else:
        # Run all unit tests
        try:
            results = run_all_unit_tests()
            final_status = generate_unit_test_report(results)
            return 0 if final_status == 'SUCCESS' else 1
            
        except KeyboardInterrupt:
            print('\n⚠️ Unit tests interrupted by user')
            return 1
        except Exception as e:
            print(f'\n❌ Unit test execution failed: {e}')
            return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)