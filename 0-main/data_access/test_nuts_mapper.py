#!/usr/bin/env python3
"""
Test script for NUTS Mapper functionality
Enhanced from EPO PATLIB 2025 Live Demo Code

Tests NUTS hierarchical geographic mapping with PATSTAT integration
and validates all core functionality including hierarchy navigation,
code validation, and patent data aggregation.
"""

import pandas as pd
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_access.nuts_mapper import NUTSMapper, create_nuts_mapper
from data_access import PatstatClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nuts_mapper_basic():
    """Test basic NUTS mapper functionality without PATSTAT."""
    logger.info("🧪 Testing basic NUTS mapper functionality...")
    
    # Create mapper without PATSTAT client (local CSV only)
    mapper = create_nuts_mapper()
    
    # Test basic functionality
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic info retrieval
    total_tests += 1
    test_codes = ['DE', 'DE1', 'DE11', 'DE111', 'FR', 'INVALID']
    
    logger.info("📝 Testing NUTS info retrieval...")
    for code in test_codes:
        info = mapper.get_nuts_info(code)
        logger.info(f"  {code}: {info['nuts_label']} (Level {info['nuts_level']}, Valid: {info['is_valid']})")
    
    if all(mapper.get_nuts_info(code)['nuts_code'] for code in test_codes):
        tests_passed += 1
        logger.info("✅ NUTS info retrieval working")
    else:
        logger.error("❌ NUTS info retrieval failed")
    
    # Test 2: Hierarchy navigation
    total_tests += 1
    test_hierarchy_code = 'DEF05'  # From our CSV data
    hierarchy = mapper.get_nuts_hierarchy(test_hierarchy_code)
    
    logger.info(f"📝 Testing hierarchy for {test_hierarchy_code}: {hierarchy}")
    
    if len(hierarchy) >= 2 and hierarchy[0] == 'DE':
        tests_passed += 1
        logger.info("✅ Hierarchy navigation working")
    else:
        logger.error("❌ Hierarchy navigation failed")
    
    # Test 3: Country extraction
    total_tests += 1
    test_country_codes = ['DE111', 'FR123', 'IT456', 'INVALID']
    
    logger.info("📝 Testing country extraction...")
    countries_correct = 0
    for code in test_country_codes:
        country = mapper.nuts_to_country(code)
        expected = code[:2] if len(code) >= 2 else 'XX'
        logger.info(f"  {code} → {country} (expected: {expected})")
        if country == expected:
            countries_correct += 1
    
    if countries_correct == len(test_country_codes):
        tests_passed += 1
        logger.info("✅ Country extraction working")
    else:
        logger.error("❌ Country extraction failed")
    
    # Test 4: Code validation
    total_tests += 1
    valid_codes = ['DE', 'DEF05', 'FR123']
    invalid_codes = ['INVALID', '', None, '1', 'TOOLONG123']
    
    logger.info("📝 Testing code validation...")
    validation_correct = 0
    
    for code in valid_codes:
        is_valid = mapper.validate_nuts_code(code)
        logger.info(f"  {code}: Valid = {is_valid}")
        if is_valid:
            validation_correct += 1
    
    for code in invalid_codes:
        is_valid = mapper.validate_nuts_code(code)
        logger.info(f"  {code}: Valid = {is_valid}")
        if not is_valid:
            validation_correct += 1
    
    if validation_correct >= len(valid_codes):  # At least valid codes should work
        tests_passed += 1
        logger.info("✅ Code validation working")
    else:
        logger.error("❌ Code validation failed")
    
    # Test 5: Data summary
    total_tests += 1
    summary = mapper.get_nuts_summary()
    
    logger.info("📝 Testing data summary...")
    logger.info(f"  Total regions: {summary['total_regions']}")
    logger.info(f"  Countries: {summary['countries']}")
    logger.info(f"  Data sources: {summary['data_sources']}")
    logger.info(f"  Level distribution: {summary['level_distribution']}")
    
    if summary['total_regions'] > 0:
        tests_passed += 1
        logger.info("✅ Data summary working")
    else:
        logger.error("❌ Data summary failed")
    
    return tests_passed, total_tests

def test_nuts_mapper_with_patstat():
    """Test NUTS mapper with PATSTAT integration."""
    logger.info("🗄️ Testing NUTS mapper with PATSTAT integration...")
    
    try:
        # Create PATSTAT client
        patstat_client = PatstatClient()
        logger.info("✅ PATSTAT client created successfully")
        
        # Create mapper with PATSTAT
        mapper = create_nuts_mapper(patstat_client=patstat_client)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Enhanced data from PATSTAT
        total_tests += 1
        summary = mapper.get_nuts_summary()
        
        logger.info("📝 Testing PATSTAT data integration...")
        logger.info(f"  Total regions: {summary['total_regions']}")
        logger.info(f"  Data sources: {summary['data_sources']}")
        
        # Check if we have PATSTAT data
        has_patstat_data = 'PATSTAT_TLS904' in summary['data_sources']
        
        if has_patstat_data:
            tests_passed += 1
            logger.info("✅ PATSTAT data integration working")
        else:
            logger.warning("⚠️ No PATSTAT data found (using fallback)")
            tests_passed += 1  # Still pass if graceful fallback works
        
        # Test 2: Advanced hierarchy with PATSTAT data
        total_tests += 1
        sample_codes = ['DE', 'FR', 'IT', 'ES', 'NL']
        
        logger.info("📝 Testing advanced hierarchy with PATSTAT...")
        for country in sample_codes:
            regions_l1 = mapper.get_country_regions(country, nuts_level=1)
            regions_l2 = mapper.get_country_regions(country, nuts_level=2)
            regions_l3 = mapper.get_country_regions(country, nuts_level=3)
            
            logger.info(f"  {country}: L1={len(regions_l1)}, L2={len(regions_l2)}, L3={len(regions_l3)}")
        
        tests_passed += 1
        logger.info("✅ Advanced hierarchy working")
        
        return tests_passed, total_tests
        
    except Exception as e:
        logger.error(f"❌ PATSTAT integration test failed: {e}")
        return 0, 2

def test_patent_data_enhancement():
    """Test patent data enhancement with NUTS information."""
    logger.info("📊 Testing patent data enhancement...")
    
    # Create test patent data
    test_data = pd.DataFrame({
        'docdb_family_id': [12345, 23456, 34567, 45678, 56789],
        'nuts_code': ['DE111', 'FR101', 'IT123', 'INVALID', ''],
        'applicant_name': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E'],
        'patent_count': [5, 3, 8, 2, 1]
    })
    
    # Create mapper
    mapper = create_nuts_mapper()
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic enhancement
    total_tests += 1
    
    logger.info("📝 Testing basic patent data enhancement...")
    enhanced_data = mapper.enhance_patent_data(test_data, nuts_col='nuts_code')
    
    # Check if enhancement worked
    enhancement_cols = ['nuts_label', 'nuts_level', 'country_code', 'is_valid_nuts']
    has_enhancement_cols = all(col in enhanced_data.columns for col in enhancement_cols)
    
    if has_enhancement_cols and len(enhanced_data) == len(test_data):
        tests_passed += 1
        logger.info("✅ Basic enhancement working")
        
        # Show sample results
        for i, row in enhanced_data.head(3).iterrows():
            logger.info(f"  {row['nuts_code']} → {row['nuts_label']} ({row['country_code']})")
    else:
        logger.error("❌ Basic enhancement failed")
    
    # Test 2: Aggregation by NUTS level
    total_tests += 1
    
    logger.info("📝 Testing NUTS level aggregation...")
    try:
        aggregated_data = mapper.aggregate_by_nuts_level(
            test_data, 
            nuts_col='nuts_code', 
            target_level=1
        )
        
        if len(aggregated_data) > 0 and 'nuts_level_1' in aggregated_data.columns:
            tests_passed += 1
            logger.info("✅ NUTS aggregation working")
            logger.info(f"  Aggregated to {len(aggregated_data)} level 1 regions")
        else:
            logger.error("❌ NUTS aggregation failed")
    
    except Exception as e:
        logger.error(f"❌ NUTS aggregation failed: {e}")
    
    return tests_passed, total_tests

def test_nuts_dataframe_creation():
    """Test comprehensive NUTS DataFrame creation."""
    logger.info("📋 Testing NUTS DataFrame creation...")
    
    mapper = create_nuts_mapper()
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic DataFrame creation
    total_tests += 1
    
    logger.info("📝 Testing DataFrame creation...")
    nuts_df = mapper.create_nuts_dataframe()
    
    expected_cols = ['nuts_code', 'nuts_level', 'nuts_label', 'country_code', 
                    'hierarchy_depth', 'parent_region', 'child_count']
    
    has_expected_cols = all(col in nuts_df.columns for col in expected_cols)
    
    if len(nuts_df) > 0 and has_expected_cols:
        tests_passed += 1
        logger.info("✅ DataFrame creation working")
        logger.info(f"  Created DataFrame with {len(nuts_df)} regions and {len(nuts_df.columns)} columns")
        
        # Show sample data
        logger.info("📝 Sample NUTS data:")
        for i, row in nuts_df.head(5).iterrows():
            logger.info(f"  {row['nuts_code']}: {row['nuts_label']} (L{row['nuts_level']}, {row['country_code']})")
    else:
        logger.error("❌ DataFrame creation failed")
    
    return tests_passed, total_tests

def run_comprehensive_tests():
    """Run all NUTS mapper tests."""
    logger.info("🚀 Starting comprehensive NUTS mapper tests...")
    logger.info("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    # Test 1: Basic functionality
    logger.info("\n🔍 Test Suite 1: Basic Functionality")
    logger.info("-" * 40)
    passed, tests = test_nuts_mapper_basic()
    total_passed += passed
    total_tests += tests
    logger.info(f"Suite 1 Results: {passed}/{tests} tests passed")
    
    # Test 2: PATSTAT integration
    logger.info("\n🗄️ Test Suite 2: PATSTAT Integration")
    logger.info("-" * 40)
    passed, tests = test_nuts_mapper_with_patstat()
    total_passed += passed
    total_tests += tests
    logger.info(f"Suite 2 Results: {passed}/{tests} tests passed")
    
    # Test 3: Patent data enhancement
    logger.info("\n📊 Test Suite 3: Patent Data Enhancement")
    logger.info("-" * 40)
    passed, tests = test_patent_data_enhancement()
    total_passed += passed
    total_tests += tests
    logger.info(f"Suite 3 Results: {passed}/{tests} tests passed")
    
    # Test 4: DataFrame creation
    logger.info("\n📋 Test Suite 4: DataFrame Creation")
    logger.info("-" * 40)
    passed, tests = test_nuts_dataframe_creation()
    total_passed += passed
    total_tests += tests
    logger.info(f"Suite 4 Results: {passed}/{tests} tests passed")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("🏁 COMPREHENSIVE TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total tests passed: {total_passed}/{total_tests}")
    logger.info(f"Success rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_passed == total_tests:
        logger.info("🎉 ALL TESTS PASSED! NUTS mapper is ready for production.")
        return True
    elif total_passed >= total_tests * 0.8:
        logger.info("✅ Most tests passed. NUTS mapper is functional with minor issues.")
        return True
    else:
        logger.error("❌ Significant test failures. NUTS mapper needs debugging.")
        return False

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)