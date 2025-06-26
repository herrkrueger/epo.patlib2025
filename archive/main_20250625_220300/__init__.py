"""
Patent Analysis Platform - Main Module
Enhanced from EPO PATLIB 2025 Live Demo Code

This platform provides comprehensive patent intelligence capabilities for 
patent search and analysis, including data access, processing, 
analysis, and visualization components. Originally developed for REE analysis.

Architecture:
- data_access: PATSTAT database and EPO OPS API integration
- processors: Data processing for applicants, geographic, and classification analysis
- analyzers: High-level analysis for regional, technology, and trends intelligence
- visualizations: Interactive charts, maps, and dashboards
- config: Centralized configuration management

Enhanced Features:
- Production-ready PATSTAT integration with proven patterns
- EPO OPS API integration with rate limiting and caching
- Advanced visualization with interactive dashboards
- Comprehensive configuration management
- Business intelligence reporting capabilities
"""

# Core module imports
from . import data_access
from . import processors
from . import analyzers
from . import visualizations
from . import config

# Version information
__version__ = "1.0.0"
__title__ = "Patent Analysis Platform"
__description__ = "Comprehensive patent intelligence platform for technology analysis"
__author__ = "Enhanced from EPO PATLIB 2025 Live Demo Code"

# Platform metadata
PLATFORM_INFO = {
    'name': 'Patent Analysis Platform',
    'version': __version__,
    'description': __description__,
    'components': ['data_access', 'processors', 'analyzers', 'visualizations', 'config'],
    'enhanced_from': 'EPO PATLIB 2025 Live Demo Code',
    'original_focus': 'REE (Rare Earth Elements) analysis',
    'capabilities': {
        'data_sources': ['PATSTAT Database', 'EPO OPS API', 'Market Data Integration'],
        'analysis_types': ['Applicant Intelligence', 'Geographic Analysis', 'Technology Networks', 
                          'Regional Competition', 'Temporal Trends', 'Innovation Metrics'],
        'visualizations': ['Interactive Charts', 'Geographic Maps', 'Network Graphs', 
                          'Executive Dashboards', 'Technical Analysis'],
        'export_formats': ['HTML', 'PNG', 'PDF', 'Excel', 'JSON', 'CSV'],
        'technology_agnostic': True
    }
}

# Quick setup functions
def setup_complete_platform(config_dir=None, theme='patent_intelligence'):
    """
    Setup complete patent analysis platform with all components.
    
    Args:
        config_dir: Directory containing configuration files
        theme: Visualization theme
        
    Returns:
        Dictionary with all platform components
    """
    # Initialize configuration
    config_manager = config.get_config_manager(config_dir)
    
    # Setup data access components
    data_pipeline = data_access.setup_full_pipeline()
    
    # Setup processing components
    processing_pipeline = processors.setup_complete_analysis_pipeline()
    
    # Setup analysis components
    analysis_suite = analyzers.setup_complete_analysis_suite()
    
    # Setup visualization components
    visualization_suite = visualizations.setup_complete_visualization_suite(theme)
    
    platform = {
        'config': config_manager,
        'data_access': data_pipeline,
        'processors': processing_pipeline,
        'analyzers': analysis_suite,
        'visualizations': visualization_suite,
        'metadata': PLATFORM_INFO
    }
    
    return platform

def quick_patent_analysis(search_params=None, analysis_scope='full', export_format=None):
    """
    Quick function to run comprehensive patent analysis.
    
    Args:
        search_params: Search parameters for patent data
        analysis_scope: Scope of analysis ('quick', 'full', 'custom')
        export_format: Export format for results
        
    Returns:
        Complete analysis results with visualizations
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting quick patent analysis...")
    
    # Setup platform
    platform = setup_complete_platform()
    
    # Default search parameters
    if search_params is None:
        search_params = {
            'keywords': ['rare earth', 'lanthan', 'neodymium'],
            'start_date': '2010-01-01',
            'end_date': '2024-12-31',
            'focused_search': True
        }
    
    results = {
        'metadata': {
            'analysis_timestamp': pd.Timestamp.now().isoformat(),
            'search_params': search_params,
            'analysis_scope': analysis_scope,
            'platform_version': __version__
        }
    }
    
    try:
        # Data collection
        logger.info("📊 Collecting patent data...")
        patstat_client, ree_searcher = platform['data_access']['patstat_client'], platform['data_access']['ree_searcher']
        
        if ree_searcher:
            patent_data = ree_searcher.execute_comprehensive_search(**search_params)
            results['data_collection'] = {
                'status': 'Success',
                'records_found': len(patent_data) if patent_data is not None else 0
            }
        else:
            logger.warning("⚠️ PATSTAT searcher not available, using demo data")
            patent_data = _generate_demo_patent_data()
            results['data_collection'] = {
                'status': 'Demo Mode',
                'records_found': len(patent_data)
            }
        
        # Analysis execution
        if patent_data is not None and len(patent_data) > 0:
            logger.info("🔍 Running analysis suite...")
            
            # Prepare data for different analysis types
            analysis_data = {
                'applicant_data': patent_data,
                'geographic_data': patent_data,
                'temporal_data': patent_data,
                'technology_data': patent_data
            }
            
            # Run integrated analysis
            analysis_results = analyzers.run_comprehensive_intelligence_analysis(
                analysis_data, 
                _get_analysis_config(analysis_scope)
            )
            
            results['analysis'] = analysis_results
            
            # Generate visualizations
            logger.info("📊 Creating visualizations...")
            viz_platform = visualizations.create_integrated_visualization_platform()
            
            # Executive summary visualizations
            exec_viz = viz_platform.create_executive_summary_visualization(analysis_results['intelligence_reports'])
            results['executive_visualizations'] = exec_viz
            
            # Detailed technical visualizations
            tech_viz = viz_platform.create_detailed_technical_visualization(analysis_results['intelligence_reports'])
            results['technical_visualizations'] = tech_viz
            
            # Export if requested
            if export_format:
                logger.info(f"💾 Exporting results to {export_format}...")
                export_files = viz_platform.export_visualization_suite(
                    {'executive': exec_viz, 'technical': tech_viz},
                    export_format
                )
                results['export_files'] = export_files
        
        else:
            logger.warning("⚠️ No patent data available for analysis")
            results['analysis'] = {'status': 'No Data'}
        
        results['metadata']['completion_status'] = 'Success'
        logger.info("✅ Quick patent analysis complete")
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        results['metadata']['completion_status'] = 'Error'
        results['metadata']['error_message'] = str(e)
    
    return results

def _get_analysis_config(scope):
    """Get analysis configuration based on scope."""
    configs = {
        'quick': {
            'regional_analysis': True,
            'technology_analysis': False,
            'trends_analysis': True,
            'cross_analysis': False
        },
        'full': {
            'regional_analysis': True,
            'technology_analysis': True, 
            'trends_analysis': True,
            'cross_analysis': True
        },
        'custom': {
            'regional_analysis': True,
            'technology_analysis': True,
            'trends_analysis': False,
            'cross_analysis': True
        }
    }
    return configs.get(scope, configs['full'])

def _generate_demo_patent_data():
    """Generate demo patent data for testing."""
    import pandas as pd
    import numpy as np
    
    np.random.seed(42)
    n_records = 100
    
    countries = ['China', 'United States', 'Japan', 'Germany', 'South Korea']
    applicants = ['Company A', 'University B', 'Institute C', 'Corp D', 'Lab E']
    tech_areas = ['Extraction', 'Materials', 'Electronics', 'Recycling']
    
    demo_data = pd.DataFrame({
        'docdb_family_id': range(100000, 100000 + n_records),
        'appln_id': range(200000, 200000 + n_records),
        'appln_filing_date': pd.date_range('2010-01-01', '2023-12-31', periods=n_records),
        'earliest_filing_year': np.random.randint(2010, 2024, n_records),
        'docdb_family_size': np.random.randint(1, 20, n_records),
        'country_name': np.random.choice(countries, n_records),
        'region': np.random.choice(['East Asia', 'North America', 'Europe'], n_records),
        'Applicant': np.random.choice(applicants, n_records),
        'Patent_Families': np.random.randint(1, 50, n_records),
        'Market_Share_Pct': np.random.uniform(0.1, 10.0, n_records),
        'ree_technology_area': np.random.choice(tech_areas, n_records),
        'search_method': 'Demo Data',
        'quality_score': np.random.uniform(0.7, 1.0, n_records)
    })
    
    demo_data['filing_year'] = demo_data['earliest_filing_year']
    demo_data['family_id'] = demo_data['docdb_family_id']
    
    return demo_data

# Convenience imports for easy access
from .data_access import setup_patstat_connection, setup_epo_ops_client
from .processors import analyze_patent_dataset
from .analyzers import create_integrated_intelligence_platform
from .visualizations import quick_patent_analysis_visualization
from .config import get_config_manager, validate_all_configurations

# Platform status and health check
def get_platform_status():
    """Get platform status and health information."""
    import logging
    
    status = {
        'platform_info': PLATFORM_INFO,
        'configuration_status': {},
        'component_status': {},
        'system_info': {}
    }
    
    try:
        # Configuration validation
        config_manager = config.get_config_manager()
        status['configuration_status'] = config_manager.validate_configuration()
        
        # Component availability
        status['component_status'] = {
            'data_access': True,
            'processors': True, 
            'analyzers': True,
            'visualizations': True,
            'config': True
        }
        
        # System information
        import sys
        import platform as plt
        
        status['system_info'] = {
            'python_version': sys.version,
            'platform': plt.platform(),
            'processor': plt.processor(),
            'architecture': plt.architecture()
        }
        
        # Overall health
        status['overall_health'] = 'Healthy' if all(status['configuration_status'].values()) else 'Issues Detected'
        
    except Exception as e:
        status['overall_health'] = 'Error'
        status['error'] = str(e)
    
    return status

def demo_platform_capabilities():
    """Demonstrate platform capabilities with sample analysis."""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Patent Analysis Platform Demo")
    logger.info("=" * 50)
    
    # Platform status
    status = get_platform_status()
    logger.info(f"📊 Platform Status: {status['overall_health']}")
    logger.info(f"🔧 Components: {', '.join(status['component_status'].keys())}")
    
    # Quick analysis demo
    demo_results = quick_patent_analysis(
        search_params={'focused_search': True},
        analysis_scope='quick'
    )
    
    if demo_results['metadata']['completion_status'] == 'Success':
        logger.info("✅ Demo analysis completed successfully")
        logger.info(f"📈 Data records: {demo_results['data_collection']['records_found']}")
        
        if 'analysis' in demo_results:
            analysis_summary = demo_results['analysis'].get('strategic_synthesis', {}).get('executive_overview', {})
            logger.info(f"🔍 Analysis scope: {analysis_summary.get('data_coverage', 'N/A')}")
        
        if 'executive_visualizations' in demo_results:
            exec_viz = demo_results['executive_visualizations']
            logger.info(f"📊 Executive visualizations: {len(exec_viz.get('key_charts', {}))}")
    else:
        logger.warning(f"⚠️ Demo analysis failed: {demo_results['metadata'].get('error_message', 'Unknown error')}")
    
    logger.info("=" * 50)
    logger.info("🎯 Patent Analysis Platform Ready for Use")
    
    return demo_results

# Module exports
__all__ = [
    # Core modules
    'data_access',
    'processors', 
    'analyzers',
    'visualizations',
    'config',
    
    # Platform functions
    'setup_complete_platform',
    'quick_patent_analysis',
    'get_platform_status',
    'demo_platform_capabilities',
    
    # Convenience functions
    'setup_patstat_connection',
    'setup_epo_ops_client',
    'analyze_patent_dataset',
    'create_integrated_intelligence_platform',
    'quick_patent_analysis_visualization',
    'get_config_manager',
    'validate_all_configurations',
    
    # Metadata
    'PLATFORM_INFO',
    '__version__'
]

# For backwards compatibility
import pandas as pd
import numpy as np