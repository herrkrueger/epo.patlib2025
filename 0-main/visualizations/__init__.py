"""
Visualizations Module for REE Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive visualization capabilities for patent intelligence
including interactive charts, geographic maps, and business intelligence dashboards.
"""

from .charts import (
    ChartCreator, create_chart_creator,
    quick_scatter, quick_bar, quick_pie, quick_timeseries
)
from .maps import (
    MapsCreator, create_maps_creator,
    quick_choropleth, quick_strategic_map
)
from .dashboards import (
    DashboardCreator, create_dashboard_creator,
    quick_executive_dashboard, quick_technology_dashboard, quick_competitive_dashboard
)

__version__ = "1.0.0"

__all__ = [
    # Chart creation
    'ChartCreator',
    'create_chart_creator',
    'quick_scatter',
    'quick_bar', 
    'quick_pie',
    'quick_timeseries',
    
    # Map creation
    'MapsCreator',
    'create_maps_creator', 
    'quick_choropleth',
    'quick_strategic_map',
    
    # Dashboard creation
    'DashboardCreator',
    'create_dashboard_creator',
    'quick_executive_dashboard',
    'quick_technology_dashboard', 
    'quick_competitive_dashboard'
]

# Integrated visualization workflow
def setup_complete_visualization_suite(theme: str = 'patent_intelligence'):
    """
    Setup complete visualization suite with all creators.
    
    Args:
        theme: Visualization theme for consistent styling
        
    Returns:
        Dictionary with all configured visualization instances
    """
    return {
        'chart_creator': create_chart_creator(theme),
        'maps_creator': create_maps_creator(),
        'dashboard_creator': create_dashboard_creator(theme)
    }

def create_comprehensive_visualization_report(data: Dict, 
                                            analysis_results: Dict,
                                            export_format: str = 'html'):
    """
    Create comprehensive visualization report from analysis results.
    
    Args:
        data: Raw patent data dictionary
        analysis_results: Results from analysis modules
        export_format: Export format ('html', 'pdf', 'png')
        
    Returns:
        Dictionary with visualization report components
    """
    import plotly.io as pio
    from datetime import datetime
    
    # Initialize visualization suite
    viz_suite = setup_complete_visualization_suite()
    
    report_components = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'data_sources': list(data.keys()),
            'analysis_scope': list(analysis_results.keys()),
            'export_format': export_format
        },
        'visualizations': {},
        'export_files': []
    }
    
    try:
        # Executive Dashboard
        if 'applicant' in analysis_results or 'geographic' in analysis_results:
            exec_data = {}
            
            if 'applicant' in analysis_results:
                exec_data['applicant_data'] = analysis_results['applicant']['data']
            if 'geographic' in analysis_results:
                exec_data['geographic_data'] = analysis_results['geographic']['data']
            if 'temporal_data' in data:
                exec_data['temporal_data'] = data['temporal_data']
            
            executive_dashboard = viz_suite['dashboard_creator'].create_executive_dashboard(
                exec_data,
                title="REE Patent Intelligence - Executive Summary"
            )
            
            report_components['visualizations']['executive_dashboard'] = executive_dashboard
        
        # Technology Dashboard
        if 'technology' in analysis_results:
            tech_results = analysis_results['technology']
            tech_data = {
                'technology_data': tech_results.get('data'),
                'network_graph': tech_results.get('network'),
                'innovation_metrics': tech_results.get('intelligence', {}).get('executive_summary', {}),
                'evolution_data': tech_results.get('data')  # Assuming temporal data in tech results
            }
            
            technology_dashboard = viz_suite['dashboard_creator'].create_technology_dashboard(
                tech_data,
                title="Technology Intelligence & Innovation Networks"
            )
            
            report_components['visualizations']['technology_dashboard'] = technology_dashboard
        
        # Competitive Landscape Dashboard
        if 'regional' in analysis_results and 'applicant' in analysis_results:
            competitive_data = {
                'geographic_data': analysis_results['regional']['data'],
                'applicant_data': analysis_results['applicant']['data'],
                'regional_data': analysis_results['regional'].get('landscape', {}),
                'competitive_tiers': analysis_results['applicant'].get('landscape', {}).get('competitive_tiers', {})
            }
            
            competitive_dashboard = viz_suite['dashboard_creator'].create_competitive_landscape_dashboard(
                competitive_data,
                title="Global Competitive Landscape Analysis"
            )
            
            report_components['visualizations']['competitive_dashboard'] = competitive_dashboard
        
        # Trends Dashboard
        if 'trends' in analysis_results:
            trends_results = analysis_results['trends']
            trends_data = {
                'temporal_data': trends_results.get('data'),
                'technology_growth': trends_results.get('intelligence', {}).get('technology_trends', {}),
                'lifecycle_data': trends_results.get('intelligence', {}).get('technology_lifecycle', {}),
                'correlation_data': trends_results.get('intelligence', {}).get('market_events_impact', {})
            }
            
            trends_dashboard = viz_suite['dashboard_creator'].create_trends_dashboard(
                trends_data,
                title="Market Trends & Temporal Intelligence"
            )
            
            report_components['visualizations']['trends_dashboard'] = trends_dashboard
        
        # Individual Charts for Detailed Analysis
        
        # Top Applicants Chart
        if 'applicant' in analysis_results:
            applicant_data = analysis_results['applicant']['data']
            if len(applicant_data) > 0:
                applicant_chart = viz_suite['chart_creator'].create_ranking_bar(
                    applicant_data.head(20),
                    'Applicant', 'Patent_Families',
                    title="Top 20 REE Patent Applicants",
                    orientation='h'
                )
                report_components['visualizations']['top_applicants_chart'] = applicant_chart
        
        # Geographic Choropleth
        if 'geographic' in analysis_results:
            geo_data = analysis_results['geographic']['data']
            if len(geo_data) > 0:
                geo_chart = viz_suite['maps_creator'].create_patent_choropleth(
                    geo_data,
                    'country_name', 'unique_families',
                    title="Global REE Patent Distribution"
                )
                report_components['visualizations']['geographic_map'] = geo_chart
        
        # Technology Network
        if 'technology' in analysis_results and 'network' in analysis_results['technology']:
            network_graph = analysis_results['technology']['network']
            if network_graph and network_graph.number_of_nodes() > 0:
                network_viz = viz_suite['dashboard_creator'].create_network_visualization_panel(
                    network_graph,
                    title="REE Technology Co-occurrence Network"
                )
                report_components['visualizations']['technology_network'] = network_viz
        
        # Time Series Analysis
        if 'trends' in analysis_results:
            trends_data = analysis_results['trends']['data']
            if len(trends_data) > 0 and 'filing_year' in trends_data.columns:
                timeseries_chart = viz_suite['chart_creator'].create_time_series(
                    trends_data,
                    'filing_year', 'unique_families_annual',
                    title="REE Patent Filing Trends Over Time",
                    trend_line=True
                )
                report_components['visualizations']['filing_trends'] = timeseries_chart
        
        # Export visualizations
        if export_format and report_components['visualizations']:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for viz_name, fig in report_components['visualizations'].items():
                if export_format == 'html':
                    filename = f"ree_patent_{viz_name}_{timestamp}.html"
                    fig.write_html(filename)
                    report_components['export_files'].append(filename)
                elif export_format == 'png':
                    filename = f"ree_patent_{viz_name}_{timestamp}.png"
                    fig.write_image(filename, width=1200, height=800)
                    report_components['export_files'].append(filename)
        
        report_components['metadata']['status'] = 'Success'
        report_components['metadata']['visualization_count'] = len(report_components['visualizations'])
        
    except Exception as e:
        report_components['metadata']['status'] = 'Error'
        report_components['metadata']['error_message'] = str(e)
        logger.error(f"❌ Visualization report creation failed: {e}")
    
    return report_components

class IntegratedVisualizationPlatform:
    """
    Integrated visualization platform for comprehensive patent intelligence reporting.
    """
    
    def __init__(self, theme: str = 'patent_intelligence'):
        """
        Initialize integrated visualization platform.
        
        Args:
            theme: Visualization theme for consistent styling
        """
        self.theme = theme
        self.viz_suite = setup_complete_visualization_suite(theme)
        self.report_history = []
    
    def create_executive_summary_visualization(self, analysis_results: Dict) -> Dict[str, Any]:
        """
        Create executive-level visualization summary.
        
        Args:
            analysis_results: Results from analysis modules
            
        Returns:
            Dictionary with executive visualizations
        """
        logger.info("📊 Creating executive summary visualizations...")
        
        exec_viz = {
            'summary_metrics': {},
            'key_charts': {},
            'strategic_insights': {}
        }
        
        try:
            # Key Performance Indicators
            if 'applicant' in analysis_results:
                applicant_summary = analysis_results['applicant']['summary']
                exec_viz['summary_metrics']['market_overview'] = applicant_summary['market_overview']
            
            if 'geographic' in analysis_results:
                geo_summary = analysis_results['geographic']['summary']
                exec_viz['summary_metrics']['geographic_overview'] = geo_summary['overview']
            
            if 'technology' in analysis_results:
                tech_summary = analysis_results['technology']['intelligence']
                exec_viz['summary_metrics']['technology_overview'] = tech_summary['executive_summary']
            
            # Create key executive charts
            if 'applicant' in analysis_results:
                # Market leaders chart
                applicant_data = analysis_results['applicant']['data']
                leaders_chart = self.viz_suite['chart_creator'].create_bubble_scatter(
                    applicant_data.head(10),
                    'Patent_Families', 'Market_Share_Pct', 'Patent_Families',
                    color_col='Market_Share_Pct', text_col='Applicant',
                    title="Market Leaders Analysis",
                    x_title="Patent Families", y_title="Market Share (%)"
                )
                exec_viz['key_charts']['market_leaders'] = leaders_chart
            
            if 'geographic' in analysis_results:
                # Global distribution map
                geo_data = analysis_results['geographic']['data']
                global_map = self.viz_suite['maps_creator'].create_patent_choropleth(
                    geo_data,
                    'country_name', 'unique_families',
                    title="Global Patent Distribution"
                )
                exec_viz['key_charts']['global_distribution'] = global_map
            
            # Strategic insights compilation
            insights = []
            for analysis_type, results in analysis_results.items():
                if 'summary' in results and 'strategic_insights' in results['summary']:
                    insights.extend(results['summary']['strategic_insights'])
            
            exec_viz['strategic_insights'] = insights[:5]  # Top 5 insights
            
        except Exception as e:
            logger.error(f"❌ Executive visualization creation failed: {e}")
            exec_viz['error'] = str(e)
        
        return exec_viz
    
    def create_detailed_technical_visualization(self, analysis_results: Dict) -> Dict[str, Any]:
        """
        Create detailed technical visualization suite.
        
        Args:
            analysis_results: Results from analysis modules
            
        Returns:
            Dictionary with detailed technical visualizations
        """
        logger.info("🔬 Creating detailed technical visualizations...")
        
        tech_viz = {
            'technology_analysis': {},
            'network_analysis': {},
            'statistical_analysis': {},
            'trend_analysis': {}
        }
        
        try:
            # Technology landscape analysis
            if 'technology' in analysis_results:
                tech_results = analysis_results['technology']
                
                # Technology distribution
                if 'data' in tech_results:
                    tech_data = tech_results['data']
                    
                    # Domain distribution pie chart
                    if 'ree_technology_area' in tech_data.columns:
                        domain_chart = self.viz_suite['chart_creator'].create_market_share_pie(
                            tech_data,
                            'ree_technology_area', 'family_id',
                            title="Technology Domain Distribution"
                        )
                        tech_viz['technology_analysis']['domain_distribution'] = domain_chart
                
                # Technology network
                if 'network' in tech_results:
                    network_viz = self.viz_suite['dashboard_creator'].create_network_visualization_panel(
                        tech_results['network'],
                        title="Technology Co-occurrence Network"
                    )
                    tech_viz['network_analysis']['cooccurrence_network'] = network_viz
            
            # Statistical correlations
            if 'trends' in analysis_results:
                trends_data = analysis_results['trends']['data']
                
                # Correlation analysis
                numeric_cols = trends_data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 1:
                    correlation_chart = self.viz_suite['chart_creator'].create_correlation_heatmap(
                        trends_data,
                        columns=numeric_cols[:5],  # Top 5 numeric columns
                        title="Patent Metrics Correlation Analysis"
                    )
                    tech_viz['statistical_analysis']['correlations'] = correlation_chart
            
            # Trend analysis
            if 'trends' in analysis_results:
                trends_results = analysis_results['trends']
                
                if 'data' in trends_results and 'filing_year' in trends_results['data'].columns:
                    # Filing evolution
                    annual_data = trends_results['data'].groupby('filing_year').size().reset_index(name='count')
                    trends_chart = self.viz_suite['chart_creator'].create_time_series(
                        annual_data,
                        'filing_year', 'count',
                        title="Patent Filing Evolution",
                        trend_line=True
                    )
                    tech_viz['trend_analysis']['filing_evolution'] = trends_chart
        
        except Exception as e:
            logger.error(f"❌ Technical visualization creation failed: {e}")
            tech_viz['error'] = str(e)
        
        return tech_viz
    
    def export_visualization_suite(self, visualizations: Dict[str, Any], 
                                 format: str = 'html',
                                 filename_prefix: str = 'ree_patent_analysis') -> List[str]:
        """
        Export complete visualization suite to files.
        
        Args:
            visualizations: Dictionary with visualization components
            format: Export format ('html', 'png', 'pdf')
            filename_prefix: Prefix for exported files
            
        Returns:
            List of exported file paths
        """
        logger.info(f"💾 Exporting visualization suite: {format}")
        
        import plotly.io as pio
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exported_files = []
        
        try:
            def export_figure(fig, name):
                filename = f"{filename_prefix}_{name}_{timestamp}.{format}"
                
                if format == 'html':
                    fig.write_html(filename)
                elif format == 'png':
                    fig.write_image(filename, width=1200, height=800, scale=2)
                elif format == 'pdf':
                    fig.write_image(filename, width=1200, height=800, format='pdf')
                
                exported_files.append(filename)
                return filename
            
            # Recursively export all figures
            def export_recursive(obj, prefix=''):
                if hasattr(obj, 'write_html'):  # It's a Plotly figure
                    export_figure(obj, prefix)
                elif isinstance(obj, dict):
                    for key, value in obj.items():
                        new_prefix = f"{prefix}_{key}" if prefix else key
                        export_recursive(value, new_prefix)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        new_prefix = f"{prefix}_{i}" if prefix else str(i)
                        export_recursive(item, new_prefix)
            
            export_recursive(visualizations)
            
            logger.info(f"✅ Exported {len(exported_files)} visualization files")
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            exported_files.append(f"ERROR: {str(e)}")
        
        return exported_files
    
    def get_visualization_summary(self) -> Dict[str, Any]:
        """Get summary of visualization capabilities and recent activity."""
        return {
            'theme': self.theme,
            'available_creators': list(self.viz_suite.keys()),
            'report_history_count': len(self.report_history),
            'capabilities': {
                'charts': ['scatter', 'bar', 'pie', 'timeseries', 'heatmap', 'histogram'],
                'maps': ['choropleth', 'strategic_positioning', 'evolution', 'clusters'],
                'dashboards': ['executive', 'technology', 'competitive', 'trends'],
                'networks': ['co-occurrence', 'technology', 'citation']
            }
        }

# Convenience functions
def create_integrated_visualization_platform(theme: str = 'patent_intelligence'):
    """Create configured integrated visualization platform."""
    return IntegratedVisualizationPlatform(theme)

def quick_patent_analysis_visualization(analysis_results: Dict, export_format: str = None):
    """
    Quick function to create comprehensive patent analysis visualization.
    
    Args:
        analysis_results: Results from patent analysis
        export_format: Optional export format
        
    Returns:
        Visualization report components
    """
    platform = create_integrated_visualization_platform()
    
    # Create executive summary
    exec_viz = platform.create_executive_summary_visualization(analysis_results)
    
    # Create detailed technical analysis
    tech_viz = platform.create_detailed_technical_visualization(analysis_results)
    
    report = {
        'executive_summary': exec_viz,
        'technical_analysis': tech_viz,
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'analysis_scope': list(analysis_results.keys())
        }
    }
    
    # Export if requested
    if export_format:
        exported_files = platform.export_visualization_suite(report, export_format)
        report['exported_files'] = exported_files
    
    return report

# For backwards compatibility
import pandas as pd
import numpy as np
from datetime import datetime
import logging

logger = logging.getLogger(__name__)