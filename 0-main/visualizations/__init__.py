"""
Production Visualizations Module for Patent Analysis Platform
Comprehensive visualization suite with charts, dashboards, maps, and factory integration

This module provides a complete visualization solution for patent intelligence
with seamless integration to the production-ready patent analysis platform.
"""

# Production visualization classes
from .charts import (
    ProductionChartCreator,
    create_production_chart_creator,
    create_applicant_chart,
    create_geographic_chart,
    create_temporal_chart,
    create_technology_chart,
    create_citation_chart
)

from .dashboards import (
    ProductionDashboardCreator,
    create_production_dashboard_creator,
    create_executive_dashboard,
    create_comprehensive_dashboard
)

from .maps import (
    ProductionMapsCreator,
    create_production_maps_creator,
    create_choropleth_map,
    create_strategic_map,
    create_regional_comparison
)

from .factory import (
    PatentVisualizationFactory,
    create_visualization_factory,
    create_full_analysis,
    create_executive_analysis,
    create_technical_analysis
)

# Legacy compatibility imports
from .charts import create_chart_creator, quick_scatter, quick_bar, quick_pie, quick_timeseries
from .dashboards import create_dashboard_creator
from .maps import create_maps_creator

# Version and metadata
__version__ = "1.0.0"
__author__ = "Claude Code Patent Analysis Platform"
__description__ = "Production-ready visualization suite for patent intelligence"

# Main factory function for easy access
def create_patent_visualizations(search_results, analysis_type='executive', **kwargs):
    """
    Main entry point for creating patent visualizations.
    
    Args:
        search_results: DataFrame with patent search results
        analysis_type: Type of analysis ('executive', 'technical', 'full')
        **kwargs: Additional arguments passed to the factory
        
    Returns:
        Dictionary with visualizations and analysis results
    """
    factory = create_visualization_factory()
    return factory.create_comprehensive_analysis(
        search_results, 
        analysis_type=analysis_type, 
        **kwargs
    )

# Convenience functions for common visualizations
def create_quick_executive_dashboard(processor_results, **kwargs):
    """Quick executive dashboard creation."""
    return create_executive_dashboard(processor_results, **kwargs)

def create_quick_patent_map(processor_results, **kwargs):
    """Quick patent choropleth map creation."""
    return create_choropleth_map(processor_results, **kwargs)

def create_quick_market_analysis(processor_results, **kwargs):
    """Quick market analysis chart creation."""
    return create_applicant_chart(processor_results, **kwargs)

# Export lists for documentation and IDE support
__all__ = [
    # Production classes
    'ProductionChartCreator',
    'ProductionDashboardCreator', 
    'ProductionMapsCreator',
    'PatentVisualizationFactory',
    
    # Factory functions
    'create_production_chart_creator',
    'create_production_dashboard_creator',
    'create_production_maps_creator',
    'create_visualization_factory',
    
    # Convenience functions
    'create_applicant_chart',
    'create_geographic_chart',
    'create_temporal_chart',
    'create_technology_chart',
    'create_citation_chart',
    'create_executive_dashboard',
    'create_comprehensive_dashboard',
    'create_choropleth_map',
    'create_strategic_map',
    'create_regional_comparison',
    
    # High-level analysis functions
    'create_full_analysis',
    'create_executive_analysis',
    'create_technical_analysis',
    'create_patent_visualizations',
    
    # Quick convenience functions
    'create_quick_executive_dashboard',
    'create_quick_patent_map',
    'create_quick_market_analysis',
    
    # Legacy compatibility
    'create_chart_creator',
    'create_dashboard_creator',
    'create_maps_creator',
    'quick_scatter',
    'quick_bar',
    'quick_pie',
    'quick_timeseries'
]