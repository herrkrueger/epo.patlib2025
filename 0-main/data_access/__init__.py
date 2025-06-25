"""
Data Access Module for Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides unified access to PATSTAT database, EPO OPS API,
and intelligent caching for patent analysis workflows.
Technology-agnostic patent analysis using centralized configuration.
"""

from .patstat_client import PatstatClient, PatentSearcher, CitationAnalyzer
from .ops_client import EPOOPSClient, PatentValidator, create_search_queries, correlate_patent_market_data
from .cache_manager import PatentDataCache, PatstatQueryCache, EPSOPSCache, AnalysisCache, create_cache_manager, create_specialized_caches
from .country_mapper import PatentCountryMapper, create_country_mapper, get_enhanced_country_mapping

__version__ = "1.0.0"

__all__ = [
    # PATSTAT integration
    'PatstatClient',
    'PatentSearcher',
    'CitationAnalyzer',
    
    # EPO OPS integration
    'EPOOPSClient', 
    'PatentValidator',
    'create_search_queries',
    'correlate_patent_market_data',
    
    # Caching
    'PatentDataCache',
    'PatstatQueryCache',
    'EPSOPSCache', 
    'AnalysisCache',
    'create_cache_manager',
    'create_specialized_caches',
    
    # Geographic data
    'PatentCountryMapper',
    'create_country_mapper',
    'get_enhanced_country_mapping'
]

# Quick setup functions for common use cases
def setup_patstat_connection(environment: str = 'PROD'):
    """
    Quick setup for PATSTAT connection with patent search capabilities.
    
    Args:
        environment: PATSTAT environment ('PROD' or 'TEST')
        
    Returns:
        Tuple of (PatstatClient, PatentSearcher)
    """
    client = PatstatClient(environment)
    searcher = PatentSearcher(client)
    return client, searcher

def setup_citation_analysis(environment: str = 'PROD'):
    """
    Quick setup for citation analysis with PATSTAT connection.
    
    Args:
        environment: PATSTAT environment ('PROD' or 'TEST')
        
    Returns:
        Tuple of (PatstatClient, PatentSearcher, CitationAnalyzer)
    """
    client = PatstatClient(environment)
    searcher = PatentSearcher(client)
    citation_analyzer = CitationAnalyzer(client)
    return client, searcher, citation_analyzer

def setup_epo_ops_client(consumer_key: str = None, consumer_secret: str = None):
    """
    Quick setup for EPO OPS client with validation capabilities.
    
    Args:
        consumer_key: EPO OPS consumer key (uses ENV if None)
        consumer_secret: EPO OPS consumer secret (uses ENV if None)
        
    Returns:
        Tuple of (EPOOPSClient, PatentValidator)
    """
    client = EPOOPSClient(consumer_key, consumer_secret)
    validator = PatentValidator(client)
    return client, validator

def setup_geographic_analysis(patstat_client=None):
    """
    Setup geographic analysis with enhanced country mapping.
    
    Args:
        patstat_client: Optional PATSTAT client for TLS801_COUNTRY access
        
    Returns:
        Configured PatentCountryMapper instance
    """
    return create_country_mapper(patstat_client)

def setup_full_pipeline(cache_dir: str = "./cache", patstat_env: str = 'PROD'):
    """
    Setup complete patent analysis pipeline with all components including citation analysis.
    
    Args:
        cache_dir: Directory for cache storage
        patstat_env: PATSTAT environment
        
    Returns:
        Dictionary with all configured components
    """
    # Setup caching
    cache_manager = create_cache_manager(cache_dir)
    specialized_caches = create_specialized_caches(cache_manager)
    
    # Setup PATSTAT with citation analysis
    patstat_client, patent_searcher, citation_analyzer = setup_citation_analysis(patstat_env)
    
    # Setup EPO OPS
    ops_client, patent_validator = setup_epo_ops_client()
    
    # Setup geographic analysis
    country_mapper = setup_geographic_analysis(patstat_client)
    
    return {
        'cache_manager': cache_manager,
        'caches': specialized_caches,
        'patstat_client': patstat_client,
        'patent_searcher': patent_searcher,
        'citation_analyzer': citation_analyzer,
        'ops_client': ops_client,
        'patent_validator': patent_validator,
        'country_mapper': country_mapper
    }