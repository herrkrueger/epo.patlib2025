"""
Production Visualization Factory for Patent Analysis Platform
Integrated factory class connecting all visualization modules with all four processors

This module provides a comprehensive factory class that orchestrates the creation
of charts, dashboards, and maps using results from all four processors in the
production-ready patent analysis platform.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from datetime import datetime
from pathlib import Path

# Production imports
from config import ConfigurationManager
from data_access.country_mapper import PatentCountryMapper

# Processor imports - using correct analyzer class names
from processors.applicant import ApplicantAnalyzer
from processors.geographic import GeographicAnalyzer
from processors.classification import ClassificationAnalyzer
from processors.citation import CitationAnalyzer

# Visualization imports
from .charts import ProductionChartCreator, create_production_chart_creator
from .dashboards import ProductionDashboardCreator, create_production_dashboard_creator
from .maps import ProductionMapsCreator, create_production_maps_creator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatentVisualizationFactory:
    """
    Production-ready visualization factory that integrates all visualization modules
    with all four processors for comprehensive patent analysis.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        """
        Initialize the visualization factory with configuration management.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager or ConfigurationManager()
        self.country_mapper = PatentCountryMapper()
        
        # Initialize visualization creators
        self.chart_creator = create_production_chart_creator(self.config)
        self.dashboard_creator = create_production_dashboard_creator(self.config)
        self.maps_creator = create_production_maps_creator(self.config)
        
        # Load configuration
        self._load_factory_config()
        
        logger.debug("🏭 PatentVisualizationFactory initialized with production configuration")
    
    def _load_factory_config(self):
        """Load factory configuration from YAML files."""
        viz_config = self.config.get('visualization')
        
        # Get branding and general settings
        self.branding = viz_config.get('general', {}).get('branding', {})
        self.output_config = viz_config.get('general', {}).get('output', {})
        
        # Performance settings
        self.performance_config = viz_config.get('performance', {})
    
    def create_comprehensive_analysis(self, search_results: pd.DataFrame,
                                    analysis_type: str = 'full',
                                    export_data: bool = True) -> Dict[str, Any]:
        """
        Create comprehensive analysis with all visualization types using all processors.
        
        Args:
            search_results: DataFrame with patent search results
            analysis_type: Type of analysis ('full', 'executive', 'technical')
            export_data: Whether to export underlying data
            
        Returns:
            Dictionary with all visualizations and data
        """
        logger.debug(f"🔬 Creating comprehensive analysis: {analysis_type}")
        
        # Step 1: Run all processors
        processor_results = self._run_all_processors(search_results)
        
        # Step 2: Create visualizations based on analysis type
        if analysis_type == 'executive':
            visualizations = self._create_executive_visualizations(processor_results)
        elif analysis_type == 'technical':
            visualizations = self._create_technical_visualizations(processor_results)
        else:  # full
            visualizations = self._create_full_visualizations(processor_results)
        
        # Step 3: Prepare comprehensive results
        results = {
            'visualizations': visualizations,
            'processor_results': processor_results,
            'metadata': {
                'analysis_type': analysis_type,
                'data_count': len(search_results),
                'creation_time': datetime.now().isoformat(),
                'factory_version': 'production_v1.0'
            }
        }
        
        # Step 4: Export data if requested
        if export_data:
            export_files = self._export_analysis_data(results)
            results['export_files'] = export_files
        
        logger.debug(f"✅ Comprehensive analysis complete: {len(visualizations)} visualizations created")
        
        return results
    
    def _run_all_processors(self, search_results: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Run all four processors on the search results."""
        logger.debug("⚙️ Running all processors on search results")
        
        processor_results = {}
        
        try:
            # Applicant Analyzer
            applicant_analyzer = ApplicantAnalyzer(self.config)
            applicant_analysis = applicant_analyzer.analyze_search_results(search_results)
            processor_results['applicant'] = applicant_analysis
            logger.debug(f"✅ Applicant analysis complete: {len(applicant_analysis)} applicants")
            
        except Exception as e:
            logger.error(f"❌ Applicant analyzer failed: {e}")
            processor_results['applicant'] = {}
        
        try:
            # Geographic Analyzer
            geographic_analyzer = GeographicAnalyzer(self.config)
            geographic_analysis = geographic_analyzer.analyze_search_results(search_results)
            processor_results['geographic'] = geographic_analysis
            logger.debug(f"✅ Geographic analysis complete: {len(geographic_analysis)} countries")
            
        except Exception as e:
            logger.error(f"❌ Geographic analyzer failed: {e}")
            processor_results['geographic'] = {}
        
        try:
            # Classification Analyzer
            classification_analyzer = ClassificationAnalyzer(self.config)
            classification_analysis = classification_analyzer.analyze_search_results(search_results)
            processor_results['classification'] = classification_analysis
            logger.debug(f"✅ Classification analysis complete: {len(classification_analysis)} tech areas")
            
        except Exception as e:
            logger.error(f"❌ Classification analyzer failed: {e}")
            processor_results['classification'] = {}
        
        try:
            # Citation Analyzer
            citation_analyzer = CitationAnalyzer(self.config)
            citation_analysis = citation_analyzer.analyze_search_results(search_results)
            processor_results['citation'] = citation_analysis
            logger.debug(f"✅ Citation analysis complete: {len(citation_analysis)} citation patterns")
            
        except Exception as e:
            logger.error(f"❌ Citation analyzer failed: {e}")
            processor_results['citation'] = {}
        
        return processor_results
    
    def _create_executive_visualizations(self, processor_results: Dict[str, Dict[str, Any]]) -> Dict[str, go.Figure]:
        """Create executive-level visualizations."""
        logger.debug("📊 Creating executive visualizations")
        
        visualizations = {}
        
        # Executive Dashboard
        try:
            visualizations['executive_dashboard'] = self.dashboard_creator.create_executive_dashboard(
                processor_results, title="Executive Patent Intelligence Dashboard"
            )
        except Exception as e:
            logger.error(f"❌ Executive dashboard failed: {e}")
        
        # Key Charts
        if 'applicant' in processor_results:
            try:
                visualizations['market_leaders'] = self.chart_creator.create_applicant_bubble_scatter(
                    processor_results['applicant'], title="Market Leaders Analysis"
                )
            except Exception as e:
                logger.error(f"❌ Market leaders chart failed: {e}")
        
        if 'geographic' in processor_results:
            try:
                visualizations['global_landscape'] = self.maps_creator.create_patent_choropleth(
                    processor_results['geographic'], title="Global Patent Landscape"
                )
            except Exception as e:
                logger.error(f"❌ Global landscape map failed: {e}")
        
        return visualizations
    
    def _create_technical_visualizations(self, processor_results: Dict[str, Dict[str, Any]]) -> Dict[str, go.Figure]:
        """Create technical-level visualizations."""
        logger.debug("📊 Creating technical visualizations")
        
        visualizations = {}
        
        # Technical analysis charts
        if 'classification' in processor_results:
            try:
                visualizations['technology_distribution'] = self.chart_creator.create_technology_distribution_pie(
                    processor_results['classification'], title="Technology Distribution Analysis"
                )
            except Exception as e:
                logger.error(f"❌ Technology distribution failed: {e}")
        
        if 'citation' in processor_results:
            try:
                visualizations['citation_network'] = self.chart_creator.create_citation_network_heatmap(
                    processor_results['citation'], title="Citation Network Analysis"
                )
            except Exception as e:
                logger.error(f"❌ Citation network failed: {e}")
        
        if 'geographic' in processor_results:
            try:
                visualizations['strategic_positioning'] = self.maps_creator.create_strategic_positioning_map(
                    processor_results['geographic'], title="Strategic Geographic Positioning"
                )
            except Exception as e:
                logger.error(f"❌ Strategic positioning failed: {e}")
        
        # Temporal analysis from any processor with temporal data
        temporal_data = None
        for processor_name, results in processor_results.items():
            if 'temporal_summary' in results or 'annual_activity' in results:
                try:
                    visualizations['temporal_trends'] = self.chart_creator.create_temporal_trends_chart(
                        results, title="Patent Filing Trends Analysis"
                    )
                    break
                except Exception as e:
                    logger.error(f"❌ Temporal trends failed: {e}")
        
        return visualizations
    
    def _create_full_visualizations(self, processor_results: Dict[str, Dict[str, Any]]) -> Dict[str, go.Figure]:
        """Create full set of visualizations."""
        logger.debug("📊 Creating full visualization suite")
        
        visualizations = {}
        
        # Executive visualizations
        exec_viz = self._create_executive_visualizations(processor_results)
        visualizations.update(exec_viz)
        
        # Technical visualizations
        tech_viz = self._create_technical_visualizations(processor_results)
        visualizations.update(tech_viz)
        
        # Additional comprehensive visualizations
        try:
            visualizations['comprehensive_dashboard'] = self.dashboard_creator.create_comprehensive_analysis_dashboard(
                processor_results, title="Comprehensive Patent Analysis Dashboard"
            )
        except Exception as e:
            logger.error(f"❌ Comprehensive dashboard failed: {e}")
        
        # Geographic analysis suite
        if 'geographic' in processor_results:
            try:
                # Regional comparison with multiple metrics
                available_metrics = []
                geo_data = processor_results['geographic'].get('country_summary', pd.DataFrame())
                
                potential_metrics = ['unique_families', 'patent_count', 'market_share', 'innovation_intensity']
                available_metrics = [m for m in potential_metrics if m in geo_data.columns]
                
                if len(available_metrics) >= 2:
                    visualizations['regional_comparison'] = self.maps_creator.create_regional_comparison_map(
                        processor_results['geographic'], 
                        metrics=available_metrics[:3],  # Limit to 3 for readability
                        title="Regional Comparison Analysis"
                    )
            except Exception as e:
                logger.error(f"❌ Regional comparison failed: {e}")
        
        # Geographic ranking chart
        if 'geographic' in processor_results:
            try:
                visualizations['geographic_ranking'] = self.chart_creator.create_geographic_bar_ranking(
                    processor_results['geographic'], title="Geographic Patent Distribution"
                )
            except Exception as e:
                logger.error(f"❌ Geographic ranking failed: {e}")
        
        return visualizations
    
    def _export_analysis_data(self, results: Dict[str, Any]) -> Dict[str, str]:
        """Export analysis data to multiple formats."""
        logger.debug("💾 Exporting comprehensive analysis data")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_files = {}
        
        try:
            # Export processor results to Excel
            processor_data = results['processor_results']
            excel_file = f"patent_analysis_data_{timestamp}.xlsx"
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                for processor_name, processor_results in processor_data.items():
                    for result_type, data in processor_results.items():
                        if isinstance(data, pd.DataFrame) and len(data) > 0:
                            sheet_name = f"{processor_name}_{result_type}"[:30]
                            data.to_excel(writer, sheet_name=sheet_name, index=False)
            
            export_files['data'] = excel_file
            
            # Export metadata as JSON
            import json
            metadata_file = f"patent_analysis_metadata_{timestamp}.json"
            with open(metadata_file, 'w') as f:
                json.dump(results['metadata'], f, indent=2, default=str)
            
            export_files['metadata'] = metadata_file
            
            # Export visualizations as HTML (if configured)
            if self.output_config.get('default_format') == 'html':
                for viz_name, figure in results['visualizations'].items():
                    try:
                        html_file = f"patent_analysis_{viz_name}_{timestamp}.html"
                        figure.write_html(html_file, include_plotlyjs='cdn')
                        export_files[f'viz_{viz_name}'] = html_file
                    except Exception as e:
                        logger.warning(f"Failed to export {viz_name} to HTML: {e}")
            
            logger.debug(f"✅ Export complete: {len(export_files)} files created")
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            export_files['error'] = str(e)
        
        return export_files
    
    def create_custom_analysis(self, search_results: pd.DataFrame,
                             processors: List[str] = None,
                             visualizations: List[str] = None) -> Dict[str, Any]:
        """
        Create custom analysis with specific processors and visualizations.
        
        Args:
            search_results: DataFrame with patent search results
            processors: List of processor names to run ('applicant', 'geographic', 'classification', 'citation')
            visualizations: List of visualization types to create
            
        Returns:
            Dictionary with selected visualizations and data
        """
        logger.debug(f"🎨 Creating custom analysis with {processors} processors")
        
        # Default to all processors if none specified
        if processors is None:
            processors = ['applicant', 'geographic', 'classification', 'citation']
        
        # Run selected processors
        processor_results = {}
        
        if 'applicant' in processors:
            try:
                applicant_analyzer = ApplicantAnalyzer(self.config)
                applicant_analysis = applicant_analyzer.analyze_search_results(search_results)
                processor_results['applicant'] = applicant_analysis
            except Exception as e:
                logger.error(f"❌ Applicant analyzer failed: {e}")
        
        if 'geographic' in processors:
            try:
                geographic_analyzer = GeographicAnalyzer(self.config)
                geographic_analysis = geographic_analyzer.analyze_search_results(search_results)
                processor_results['geographic'] = geographic_analysis
            except Exception as e:
                logger.error(f"❌ Geographic analyzer failed: {e}")
        
        if 'classification' in processors:
            try:
                classification_analyzer = ClassificationAnalyzer(self.config)
                classification_analysis = classification_analyzer.analyze_search_results(search_results)
                processor_results['classification'] = classification_analysis
            except Exception as e:
                logger.error(f"❌ Classification analyzer failed: {e}")
        
        if 'citation' in processors:
            try:
                citation_analyzer = CitationAnalyzer(self.config)
                citation_analysis = citation_analyzer.analyze_search_results(search_results)
                processor_results['citation'] = citation_analysis
            except Exception as e:
                logger.error(f"❌ Citation analyzer failed: {e}")
        
        # Create selected visualizations
        custom_visualizations = {}
        
        if visualizations is None:
            # Create executive suite by default
            custom_visualizations = self._create_executive_visualizations(processor_results)
        else:
            # Create specific visualizations
            for viz_type in visualizations:
                try:
                    if viz_type == 'executive_dashboard':
                        custom_visualizations[viz_type] = self.dashboard_creator.create_executive_dashboard(processor_results)
                    elif viz_type == 'comprehensive_dashboard':
                        custom_visualizations[viz_type] = self.dashboard_creator.create_comprehensive_analysis_dashboard(processor_results)
                    elif viz_type == 'market_leaders' and 'applicant' in processor_results:
                        custom_visualizations[viz_type] = self.chart_creator.create_applicant_bubble_scatter(processor_results['applicant'])
                    elif viz_type == 'global_map' and 'geographic' in processor_results:
                        custom_visualizations[viz_type] = self.maps_creator.create_patent_choropleth(processor_results['geographic'])
                    elif viz_type == 'technology_pie' and 'classification' in processor_results:
                        custom_visualizations[viz_type] = self.chart_creator.create_technology_distribution_pie(processor_results['classification'])
                    elif viz_type == 'citation_heatmap' and 'citation' in processor_results:
                        custom_visualizations[viz_type] = self.chart_creator.create_citation_network_heatmap(processor_results['citation'])
                    # Add more visualization types as needed
                except Exception as e:
                    logger.error(f"❌ Custom visualization {viz_type} failed: {e}")
        
        results = {
            'visualizations': custom_visualizations,
            'processor_results': processor_results,
            'metadata': {
                'analysis_type': 'custom',
                'processors_used': processors,
                'visualizations_requested': visualizations,
                'data_count': len(search_results),
                'creation_time': datetime.now().isoformat()
            }
        }
        
        logger.debug(f"✅ Custom analysis complete: {len(custom_visualizations)} visualizations created")
        
        return results

def create_visualization_factory(config_manager: ConfigurationManager = None) -> PatentVisualizationFactory:
    """
    Factory function to create configured patent visualization factory.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Configured PatentVisualizationFactory instance
    """
    return PatentVisualizationFactory(config_manager)

# Production convenience functions
def create_full_analysis(search_results: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Create full patent analysis with all visualizations."""
    factory = create_visualization_factory()
    return factory.create_comprehensive_analysis(search_results, analysis_type='full', **kwargs)

def create_executive_analysis(search_results: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Create executive-level patent analysis."""
    factory = create_visualization_factory()
    return factory.create_comprehensive_analysis(search_results, analysis_type='executive', **kwargs)

def create_technical_analysis(search_results: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Create technical-level patent analysis."""
    factory = create_visualization_factory()
    return factory.create_comprehensive_analysis(search_results, analysis_type='technical', **kwargs)

# Production integration example
def demo_visualization_factory():
    """Demonstrate the visualization factory with sample data."""
    logger.debug("🚀 Visualization Factory Demo")
    
    try:
        # Create sample patent search results
        np.random.seed(42)
        sample_search_results = pd.DataFrame({
            'appln_id': range(1000, 1100),
            'appln_title': [f'Patent Title {i}' for i in range(100)],
            'appln_filing_date': pd.date_range('2010-01-01', periods=100, freq='30D'),
            'person_name': [f'Company_{i%20}' for i in range(100)],
            'appln_auth': np.random.choice(['CN', 'US', 'JP', 'DE', 'KR'], 100),
            'cpc_class_symbol': np.random.choice(['H01M', 'C22B', 'G06F', 'H01L'], 100)
        })
        
        # Create factory
        factory = create_visualization_factory()
        
        # Create comprehensive analysis
        results = factory.create_comprehensive_analysis(
            sample_search_results,
            analysis_type='executive',
            export_data=False  # Skip export for demo
        )
        
        logger.debug(f"✅ Demo complete: {len(results['visualizations'])} visualizations created")
        logger.debug(f"📊 Available visualizations: {list(results['visualizations'].keys())}")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        return None

if __name__ == "__main__":
    demo_visualization_factory()