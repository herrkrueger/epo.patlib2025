#!/usr/bin/env python3
"""
Configuration Testing Script for Patent Analysis Platform
Enhanced from EPO PATLIB 2025 Live Demo Code

This script validates all configuration files, centralized search patterns,
environment handling, and geographic configuration integration.

Usage:
    python config/test_config.py
    python -m config.test_config
    ./config/test_config.py
"""

import sys
import os
from pathlib import Path
import logging
from typing import Dict, Any, List

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

def print_subsection(title: str, char: str = '-', width: int = 40):
    """Print a formatted subsection header."""
    print(f'\n{title}')
    print(char * width)

def test_yaml_file_syntax():
    """Test 1: Validate YAML file syntax and structure."""
    print_section('🔍 Test 1: YAML Configuration Files Syntax')
    
    import yaml
    
    config_files = [
        'api_config.yaml',
        'database_config.yaml', 
        'visualization_config.yaml',
        'search_patterns_config.yaml'
    ]
    
    config_dir = Path(__file__).parent
    results = {}
    
    for config_file in config_files:
        try:
            config_path = config_dir / config_file
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Count environment variable references
            def count_env_vars(data, path=''):
                count = 0
                if isinstance(data, dict):
                    for key, value in data.items():
                        new_path = f'{path}.{key}' if path else key
                        count += count_env_vars(value, new_path)
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        new_path = f'{path}[{i}]'
                        count += count_env_vars(item, new_path)
                elif isinstance(data, str) and data.startswith('${ENV:'):
                    count += 1
                    print(f'   📝 Environment variable: {data} at {path}')
                return count
            
            env_vars = count_env_vars(config_data)
            results[config_file] = {
                'status': 'Valid',
                'top_level_keys': len(config_data),
                'env_vars': env_vars
            }
            
            print(f'✅ {config_file}: Valid YAML, {len(config_data)} top-level keys')
            if env_vars > 0:
                print(f'   🔧 Found {env_vars} environment variable references')
                
        except Exception as e:
            results[config_file] = {'status': 'Error', 'error': str(e)}
            print(f'❌ {config_file}: Error - {e}')
    
    return all(r['status'] == 'Valid' for r in results.values())

def test_configuration_manager():
    """Test 2: Configuration manager functionality."""
    print_section('🔧 Test 2: Configuration Manager Functionality')
    
    try:
        from config import ConfigurationManager, get_config_manager
        
        # Test basic initialization
        config_manager = ConfigurationManager()
        print('✅ Configuration manager initialized')
        
        # Test configuration loading
        summary = config_manager.get_configuration_summary()
        print(f'📊 Configuration Summary:')
        print(f'   Environment: {summary["environment"]}')
        print(f'   Loaded configs: {summary["loaded_configs"]}')
        print(f'   Configuration directory: {summary["config_directory"]}')
        
        # Test specific configuration access
        print_subsection('Configuration Access Tests')
        
        # API config test
        base_url = config_manager.get_api_config('epo_ops.endpoints.base_url')
        print(f'   EPO OPS Base URL: {base_url}')
        
        # Database config test
        patstat_env = config_manager.get_database_config('patstat.connection.environment')
        print(f'   PATSTAT Environment: {patstat_env}')
        
        # Visualization config test
        default_theme = config_manager.get_visualization_config('general.themes.default_theme')
        print(f'   Default Theme: {default_theme}')
        
        # Search patterns config test
        search_sections = config_manager.get_search_patterns_config()
        print(f'   Search patterns sections: {list(search_sections.keys())}')
        
        return True
        
    except Exception as e:
        print(f'❌ Configuration manager test failed: {e}')
        return False

def test_configuration_validation():
    """Test 3: Configuration validation and helper functions."""
    print_section('📋 Test 3: Configuration Validation')
    
    try:
        from config import validate_all_configurations
        
        # Test validation function
        validation_results = validate_all_configurations()
        
        print('📊 Validation Results:')
        for config_type, is_valid in validation_results.items():
            status = '✅' if is_valid else '⚠️'
            print(f'   {status} {config_type}: {"Valid" if is_valid else "Issues Found"}')
        
        return validation_results.get('overall', False)
        
    except Exception as e:
        print(f'❌ Configuration validation test failed: {e}')
        return False

def test_centralized_search_patterns():
    """Test 4: Centralized search patterns configuration."""
    print_section('🎯 Test 4: Centralized Search Patterns')
    
    try:
        from config import (
            get_patent_search_config,
            get_technology_taxonomy,
            get_classification_descriptions,
            get_search_strategy_config,
            get_search_patterns_config
        )
        
        # Test search patterns config loading
        print_subsection('Search Patterns Configuration')
        search_config = get_search_patterns_config()
        print(f'   Top-level sections: {list(search_config.keys())}')
        
        # Test technology taxonomy
        print_subsection('Technology Taxonomy')
        taxonomy = get_technology_taxonomy()
        for tech_area, details in taxonomy.items():
            codes_count = len(details.get('codes', []))
            maturity = details.get('maturity', 'Unknown')
            strategic_value = details.get('strategic_value', 'Unknown')
            print(f'   {tech_area}: {codes_count} codes, {maturity} maturity, {strategic_value} value')
        
        # Test classification descriptions
        print_subsection('Classification Descriptions')
        descriptions = get_classification_descriptions()
        print(f'   Total descriptions: {len(descriptions)}')
        for code, desc in list(descriptions.items())[:3]:  # Show first 3
            print(f'   {code}: {desc}')
        if len(descriptions) > 3:
            print(f'   ... and {len(descriptions) - 3} more')
        
        # Test search strategy
        print_subsection('Search Strategy Configuration')
        strategy = get_search_strategy_config('focused_high_precision')
        print(f'   Description: {strategy.get("description", "N/A")}')
        print(f'   Steps: {list(strategy.get("steps", {}).keys()) if strategy.get("steps") else "N/A"}')
        print(f'   Quality threshold: {strategy.get("quality_threshold", "N/A")}')
        
        # Test comprehensive patent search config (using generic function)
        print_subsection('Comprehensive Patent Search Configuration')
        patent_config = get_patent_search_config()
        print(f'   Configuration sections: {list(patent_config.keys())}')
        
        # Show keyword counts
        keywords = patent_config.get('keywords', {})
        for category, word_list in keywords.items():
            if isinstance(word_list, list):
                print(f'   {category} keywords: {len(word_list)}')
        
        
        return True
        
    except Exception as e:
        print(f'❌ Centralized search patterns test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_configuration_reorganization():
    """Test 5: Proper configuration reorganization."""
    print_section('🏗️ Test 5: Configuration Architecture Reorganization')
    
    try:
        from config import (
            get_api_config,
            get_search_patterns_config,
            get_market_data_integration_config,
            get_epo_ops_query_templates
        )
        
        # Test API config is clean (only API-related settings)
        print_subsection('API Config Structure (should only contain API settings)')
        epo_ops = get_api_config('epo_ops')
        if epo_ops:
            print(f'   EPO OPS sections: {list(epo_ops.keys())}')
        
        patstat = get_api_config('patstat')
        if patstat:
            print(f'   PATSTAT sections: {list(patstat.keys())}')
        
        # Test search patterns config contains the moved sections
        print_subsection('Search Patterns Config (should contain search logic)')
        search_config = get_search_patterns_config()
        print(f'   Top-level sections: {list(search_config.keys())}')
        
        # Test market data integration config
        print_subsection('Market Data Integration')
        market_config = get_market_data_integration_config()
        if market_config:
            data_sources = market_config.get('data_sources', {})
            print(f'   Data sources: {list(data_sources.keys())}')
            correlation_patterns = market_config.get('correlation_patterns', {})
            print(f'   Correlation patterns: {list(correlation_patterns.keys())}')
        
        # Test EPO OPS query templates
        print_subsection('EPO OPS Query Templates')
        ops_templates = get_epo_ops_query_templates()
        if ops_templates:
            print(f'   Template count: {len(ops_templates)}')
            for template_name in list(ops_templates.keys())[:5]:  # Show first 5
                print(f'   - {template_name}')
        
        return True
        
    except Exception as e:
        print(f'❌ Configuration reorganization test failed: {e}')
        return False

def test_environment_handling():
    """Test 6: Environment variable handling and .env file loading."""
    print_section('🔑 Test 6: Environment Variable Handling')
    
    try:
        # Test current environment variables
        print_subsection('Current Environment Variables')
        print(f'   OPS_KEY: {"Set" if os.getenv("OPS_KEY") else "Not Set"}')
        print(f'   OPS_SECRET: {"Set" if os.getenv("OPS_SECRET") else "Not Set"}')
        
        # Test .env file detection
        print_subsection('.env File Detection')
        env_paths = [
            '/home/jovyan/patlib/.env',
            '../.env',
            '../../.env',
            '../../../.env'
        ]
        
        env_file_found = False
        for env_path in env_paths:
            if os.path.exists(env_path):
                print(f'   ✅ Found .env file at: {env_path}')
                with open(env_path, 'r') as f:
                    content = f.read()
                    lines = content.strip().split('\n')
                    print(f'   📄 Contains {len(lines)} configuration lines')
                env_file_found = True
                break
        
        if not env_file_found:
            print('   ⚠️ No .env file found in expected locations')
        
        # Test EPO client environment loading
        print_subsection('EPO Client Environment Loading')
        try:
            # Import should trigger .env loading
            from data_access.ops_client import EPOOPSClient
            print('   ✅ EPO client import successful')
            print(f'   OPS_KEY after import: {"Set" if os.getenv("OPS_KEY") else "Not Set"}')
            print(f'   OPS_SECRET after import: {"Set" if os.getenv("OPS_SECRET") else "Not Set"}')
        except Exception as e:
            print(f'   ⚠️ EPO client import failed: {e}')
        
        return env_file_found
        
    except Exception as e:
        print(f'❌ Environment handling test failed: {e}')
        return False

def test_data_access_integration():
    """Test 7: Data access module integration with centralized config."""
    print_section('📊 Test 7: Data Access Integration')
    
    try:
        # Test PATSTAT client configuration
        print_subsection('PATSTAT Client Configuration')
        from config import get_database_config
        
        tip_config = get_database_config('patstat.environments.tip_environment')
        print(f'   TIP Environment enabled: {tip_config.get("enabled", "N/A")}')
        print(f'   Use PATSTAT Client module: {tip_config.get("use_patstat_client_module", "N/A")}')
        
        external_config = get_database_config('patstat.environments.external_environment')
        print(f'   External Environment enabled: {external_config.get("enabled", "N/A")}')
        
        # Test data access imports
        print_subsection('Data Access Module Imports')
        try:
            from data_access.patstat_client import PatstatClient, PatentSearcher
            print('   ✅ PATSTAT client imports successful')
            
            from data_access.ops_client import EPOOPSClient
            print('   ✅ EPO OPS client imports successful')
            
            from data_access.cache_manager import PatentDataCache
            print('   ✅ Cache manager imports successful')
            
        except Exception as e:
            print(f'   ⚠️ Data access imports failed: {e}')
            return False
        
        # Test patent searcher with centralized config
        print_subsection('Patent Searcher Configuration')
        try:
            client = PatstatClient(environment='PROD')
            print(f'   ✅ PATSTAT client initialized: {client.environment}')
            
            searcher = PatentSearcher(client)
            print('   ✅ Patent searcher initialized with centralized config')
            print(f'   Keywords loaded: {len(searcher.search_keywords)}')
            print(f'   IPC codes: {len(searcher.ipc_codes)}')
            print(f'   CPC codes: {len(searcher.cpc_codes)}')
            print(f'   Search strategies: {list(searcher.search_strategies.keys())}')
            
        except Exception as e:
            print(f'   ⚠️ Patent searcher test failed: {e}')
        
        return True
        
    except Exception as e:
        print(f'❌ Data access integration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_geographic_configuration():
    """Test 8: Geographic configuration and country mapping integration."""
    print_section('🌍 Test 8: Geographic Configuration')
    
    try:
        # Test geographic config loading
        print_subsection('Geographic Configuration Loading')
        from config import ConfigurationManager
        
        config_manager = ConfigurationManager()
        geographic_config_path = config_manager.config_dir / 'geographic_config.yaml'
        
        if geographic_config_path.exists():
            print(f'   ✅ Geographic config file exists: {geographic_config_path}')
        else:
            print(f'   ❌ Geographic config file missing: {geographic_config_path}')
            return False
        
        # Test country mapper integration
        print_subsection('Country Mapper Integration')
        try:
            from data_access.country_mapper import create_country_mapper, PatentCountryMapper
            print('   ✅ Country mapper imports successful')
            
            # Create country mapper instance
            mapper = create_country_mapper()
            print(f'   ✅ Country mapper created with {len(mapper.country_cache)} countries')
            print(f'   ✅ Regional groups loaded: {len(mapper.regional_groups)}')
            
            # Test specific country mappings
            us_info = mapper.get_country_info('US')
            print(f'   ✅ US mapping: {us_info["name"]} - {us_info["continent"]}')
            
            de_info = mapper.get_country_info('DE')
            print(f'   ✅ DE mapping: {de_info["name"]} - {de_info["continent"]}')
            
            # Test regional groupings
            ip5_countries = mapper.get_countries_in_group('ip5_offices')
            print(f'   ✅ IP5 offices: {len(ip5_countries)} countries')
            
            # Test country group membership
            us_groups = mapper.get_country_groups('US')
            print(f'   ✅ US regional groups: {len(us_groups)} groups')
            
            # Test data_access module exports
            from data_access import setup_geographic_analysis
            test_mapper = setup_geographic_analysis()
            print('   ✅ data_access geographic setup function working')
            
        except Exception as e:
            print(f'   ❌ Country mapper test failed: {e}')
            return False
        
        # Test geographic processor integration
        print_subsection('Geographic Processor Integration')
        try:
            from processors.geographic import create_geographic_analyzer
            analyzer = create_geographic_analyzer()
            print('   ✅ Geographic analyzer created with enhanced mapping')
            
            # Verify analyzer has country mapper
            if hasattr(analyzer, 'country_mapper'):
                print(f'   ✅ Analyzer has country mapper with {len(analyzer.country_mapper.country_cache)} countries')
            else:
                print('   ❌ Analyzer missing country mapper')
                return False
                
        except Exception as e:
            print(f'   ❌ Geographic processor test failed: {e}')
            return False
        
        return True
        
    except Exception as e:
        print(f'❌ Geographic configuration test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def generate_test_report(results: Dict[str, bool]) -> str:
    """Generate a comprehensive test report."""
    print_section('📋 Test Results Summary', '=', 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f'Total Tests: {total_tests}')
    print(f'Passed: {passed_tests} ✅')
    print(f'Failed: {failed_tests} ❌')
    print(f'Success Rate: {(passed_tests/total_tests)*100:.1f}%')
    
    print('\nDetailed Results:')
    for test_name, passed in results.items():
        status = '✅ PASS' if passed else '❌ FAIL'
        print(f'   {status} {test_name}')
    
    if failed_tests == 0:
        print('\n🎉 All configuration tests passed!')
        print('🎯 Patent Analysis Platform configuration is ready!')
        return 'SUCCESS'
    else:
        print(f'\n⚠️ {failed_tests} test(s) failed. Please review the issues above.')
        return 'FAILURE'

def main():
    """Main test execution function."""
    logger = setup_logging()
    
    print('🚀 Patent Analysis Platform - Configuration Test Suite')
    print('Enhanced from EPO PATLIB 2025 Live Demo Code')
    print('=' * 60)
    
    # Execute all tests
    test_results = {}
    
    try:
        test_results['YAML File Syntax'] = test_yaml_file_syntax()
        test_results['Configuration Manager'] = test_configuration_manager()
        test_results['Configuration Validation'] = test_configuration_validation()
        test_results['Centralized Search Patterns'] = test_centralized_search_patterns()
        test_results['Configuration Reorganization'] = test_configuration_reorganization()
        test_results['Environment Handling'] = test_environment_handling()
        test_results['Data Access Integration'] = test_data_access_integration()
        test_results['Geographic Configuration'] = test_geographic_configuration()
        
    except KeyboardInterrupt:
        print('\n⚠️ Test execution interrupted by user')
        return 1
    except Exception as e:
        print(f'\n❌ Test execution failed: {e}')
        import traceback
        traceback.print_exc()
        return 1
    
    # Generate final report
    result = generate_test_report(test_results)
    
    return 0 if result == 'SUCCESS' else 1

if __name__ == '__main__':
    sys.exit(main())