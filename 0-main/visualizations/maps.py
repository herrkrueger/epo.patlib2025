"""
Production Maps Module for Patent Analysis Geographic Visualizations
Integrated with production config, processors, data access, and geographic intelligence

This module provides comprehensive geographic visualization capabilities including
choropleth maps, regional analysis, strategic geographic intelligence, and seamless
integration with the production-ready patent analysis platform.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from pathlib import Path

# Production imports
from config import ConfigurationManager
from data_access.country_mapper import PatentCountryMapper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionMapsCreator:
    """
    Production-ready geographic visualization creator for patent intelligence.
    Integrates seamlessly with the production patent analysis platform.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None):
        """
        Initialize production maps creator with configuration management.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager or ConfigurationManager()
        self.country_mapper = PatentCountryMapper()
        self.map_counter = 0
        
        # Load configuration-driven settings
        self._load_maps_config()
    
    def _load_maps_config(self):
        """Load maps configuration from YAML files."""
        viz_config = self.config.get('visualization')
        
        # Maps configuration
        self.maps_config = viz_config.get('maps', {})
        
        # Regional color schemes from configuration
        charts_config = viz_config.get('charts', {}).get('color_schemes', {})
        self.regional_color_schemes = charts_config.get('sequential', {
            'patent_activity': 'Blues',
            'market_share': 'Reds',
            'innovation_intensity': 'Viridis',
            'competitive_strength': 'Plasma',
            'growth_rate': 'RdYlGn',
            'strategic_priority': 'OrRd'
        })
        
        # Get branding configuration
        self.branding = viz_config.get('general', {}).get('branding', {})
        
        # Country coordinates from configuration
        self.country_coordinates = viz_config.get('maps', {}).get('country_coordinates', {})
    
    def create_patent_choropleth(self, processor_results: Dict[str, Any],
                               title: str = "Global Patent Analysis",
                               color_scheme: str = 'patent_activity',
                               projection: str = 'natural_earth') -> go.Figure:
        """
        Create professional choropleth map using processor results.
        
        Args:
            processor_results: Results from GeographicProcessor.export_results_for_visualization()
            title: Map title
            color_scheme: Color scheme for mapping
            projection: Map projection type
            
        Returns:
            Plotly figure object with geographic visualization
        """
        logger.debug(f"🗺️ Creating patent choropleth: {title}")
        
        # Extract data from processor results
        if 'country_summary' not in processor_results:
            logger.warning("No country summary data found in processor results")
            return self._create_empty_map("No geographic data available")
        
        map_data = processor_results['country_summary'].copy()
        
        # Map country names to ISO codes for choropleth visualization
        if 'country_name' in map_data.columns:
            # Basic country name to ISO code mapping
            name_to_iso = {
                'United States': 'US', 'China': 'CN', 'Japan': 'JP', 'Germany': 'DE',
                'United Kingdom': 'GB', 'France': 'FR', 'South Korea': 'KR', 
                'Canada': 'CA', 'Italy': 'IT', 'Netherlands': 'NL', 'Switzerland': 'CH',
                'Sweden': 'SE', 'Australia': 'AU', 'India': 'IN', 'Unknown': 'XX'
            }
            map_data['iso_code'] = map_data['country_name'].map(name_to_iso).fillna('XX')
        elif 'country_code' in map_data.columns:
            # If we have country codes, use them directly as ISO codes
            map_data['iso_code'] = map_data['country_code']
        else:
            # Fallback: create a dummy ISO code column
            map_data['iso_code'] = 'XX'
        
        # Filter for valid ISO codes
        map_data = map_data[map_data['iso_code'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes found for mapping")
            return self._create_empty_map("No valid geographic data available")
        
        # Determine value column
        value_col = 'unique_families' if 'unique_families' in map_data.columns else map_data.columns[-1]
        
        # Get choropleth configuration
        choropleth_config = self.maps_config.get('choropleth', {})
        
        # Create choropleth map
        fig = go.Figure()
        
        colorscale = self.regional_color_schemes.get(color_scheme, 'Blues')
        
        fig.add_trace(go.Choropleth(
            locations=map_data['iso_code'],
            z=map_data[value_col],
            locationmode='ISO-3',
            text=map_data.get('country_name', map_data['iso_code']),
            hovertext=map_data.get('country_name', map_data['iso_code']),
            colorscale=colorscale,
            hovertemplate=(
                "<b>%{hovertext}</b><br>" +
                f"{value_col.replace('_', ' ').title()}: %{{z}}<br>" +
                "<extra></extra>"
            ),
            colorbar=dict(
                title=value_col.replace('_', ' ').title(),
                thickness=choropleth_config.get('color_bar_thickness', 15),
                len=choropleth_config.get('color_bar_length', 0.7)
            )
        ))
        
        # Layout styling with configuration
        title_prefix = self.branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            title_font_size=18,
            geo=dict(
                projection_type=choropleth_config.get('projection', 'natural earth'),
                showframe=choropleth_config.get('show_frame', False),
                showcoastlines=choropleth_config.get('show_coastlines', True),
                coastlinecolor=choropleth_config.get('coastline_color', 'gray'),
                showland=choropleth_config.get('show_land', True),
                landcolor=choropleth_config.get('land_color', 'lightgray'),
                showocean=choropleth_config.get('show_ocean', True),
                oceancolor=choropleth_config.get('ocean_color', 'lightblue'),
                showlakes=choropleth_config.get('show_lakes', True),
                lakecolor=choropleth_config.get('lake_color', 'lightblue')
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0),
            annotations=[
                dict(
                    text=self.branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ]
        )
        
        return fig
    
    def create_strategic_positioning_map(self, processor_results: Dict[str, Any],
                                       x_metric: str = 'patent_families', 
                                       y_metric: str = 'market_share',
                                       size_metric: str = None,
                                       title: str = "Strategic Positioning Analysis") -> go.Figure:
        """
        Create strategic positioning map with enhanced country data.
        
        Args:
            processor_results: Results from GeographicProcessor
            x_metric: Metric for x-axis positioning
            y_metric: Metric for y-axis positioning
            size_metric: Metric for bubble sizes (optional)
            title: Map title
            
        Returns:
            Plotly figure object with strategic positioning
        """
        logger.debug(f"🗺️ Creating strategic positioning map: {title}")
        
        # Extract data from processor results
        if 'country_summary' not in processor_results:
            logger.warning("No country summary data found in processor results")
            return self._create_empty_map("No geographic data available")
        
        map_data = processor_results['country_summary'].copy()
        
        # Add ISO codes for mapping
        if 'country_name' in map_data.columns:
            # Basic country name to ISO code mapping
            name_to_iso = {
                'United States': 'US', 'China': 'CN', 'Japan': 'JP', 'Germany': 'DE',
                'United Kingdom': 'GB', 'France': 'FR', 'South Korea': 'KR', 
                'Canada': 'CA', 'Italy': 'IT', 'Netherlands': 'NL', 'Switzerland': 'CH',
                'Sweden': 'SE', 'Australia': 'AU', 'India': 'IN', 'Unknown': 'XX'
            }
            map_data['iso_code'] = map_data['country_name'].map(name_to_iso).fillna('XX')
        elif 'country_code' in map_data.columns:
            map_data['iso_code'] = map_data['country_code']
        
        # Add coordinates using country mapper or configuration
        map_data = self._add_country_coordinates(map_data)
        
        # Filter out countries without coordinates
        map_data = map_data[map_data['lat'].notna() & map_data['lon'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No countries with coordinates found")
            return self._create_empty_map("No countries with coordinates available")
        
        # Prepare metrics
        x_values = map_data.get(x_metric, map_data.iloc[:, 1])
        y_values = map_data.get(y_metric, map_data.iloc[:, 2] if len(map_data.columns) > 2 else range(len(map_data)))
        
        # Prepare bubble sizes
        if size_metric and size_metric in map_data.columns:
            bubble_sizes = map_data[size_metric]
            size_ref = 2. * max(bubble_sizes) / (40**2)
        else:
            bubble_sizes = [15] * len(map_data)
            size_ref = 1
        
        # Create strategic quadrants based on median values
        x_median = x_values.median() if hasattr(x_values, 'median') else np.median(x_values)
        y_median = y_values.median() if hasattr(y_values, 'median') else np.median(y_values)
        
        def get_quadrant(x_val, y_val):
            if x_val >= x_median and y_val >= y_median:
                return 'Leaders'
            elif x_val >= x_median and y_val < y_median:
                return 'Challengers'
            elif x_val < x_median and y_val >= y_median:
                return 'Innovators'
            else:
                return 'Followers'
        
        map_data['strategic_quadrant'] = [get_quadrant(x, y) for x, y in zip(x_values, y_values)]
        
        # Get strategic map configuration
        strategic_config = self.maps_config.get('strategic_maps', {})
        quadrant_colors = strategic_config.get('quadrant_colors', {
            'Leaders': '#2E8B57',      # Sea Green
            'Challengers': '#FF6347',  # Tomato
            'Innovators': '#4169E1',   # Royal Blue
            'Followers': '#DAA520'     # Golden Rod
        })
        
        # Create figure with base map
        fig = go.Figure()
        
        # Add base world map
        fig.add_trace(go.Scattergeo(
            lon=[0], lat=[0],
            mode='markers',
            marker=dict(size=0, opacity=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add bubbles for each quadrant
        for quadrant in map_data['strategic_quadrant'].unique():
            quadrant_data = map_data[map_data['strategic_quadrant'] == quadrant]
            
            fig.add_trace(go.Scattergeo(
                lon=quadrant_data['lon'],
                lat=quadrant_data['lat'],
                mode='markers+text',
                marker=dict(
                    size=bubble_sizes[quadrant_data.index] if size_metric else 20,
                    sizemode='diameter',
                    sizeref=size_ref,
                    sizemin=8,
                    color=quadrant_colors.get(quadrant, '#808080'),
                    opacity=strategic_config.get('bubble_opacity', 0.7),
                    line=dict(
                        width=strategic_config.get('bubble_line_width', 2), 
                        color=strategic_config.get('bubble_line_color', 'white')
                    )
                ),
                text=quadrant_data.get('country_name', quadrant_data['iso_code']),
                textposition="middle center",
                textfont=dict(size=8, color='white'),
                name=f'{quadrant}',
                hovertemplate=(
                    f"<b>%{{text}}</b><br>" +
                    f"{x_metric.replace('_', ' ').title()}: %{{customdata[0]}}<br>" +
                    f"{y_metric.replace('_', ' ').title()}: %{{customdata[1]}}<br>" +
                    (f"{size_metric.replace('_', ' ').title()}: %{{customdata[2]}}<br>" if size_metric else "") +
                    f"Category: {quadrant}<br>" +
                    "<extra></extra>"
                ),
                customdata=quadrant_data[[x_metric, y_metric] + ([size_metric] if size_metric else [])].values
            ))
        
        # Layout styling
        title_prefix = self.branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            title_font_size=18,
            geo=dict(
                projection_type='natural earth',
                showframe=False,
                showcoastlines=True,
                coastlinecolor="gray",
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="lightblue",
                showlakes=True,
                lakecolor="lightblue"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=0.02,
                xanchor="center",
                x=0.5
            ),
            height=600,
            margin=dict(l=0, r=0, t=60, b=0),
            annotations=[
                dict(
                    text=self.branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ]
        )
        
        return fig
    
    def create_regional_comparison_map(self, processor_results: Dict[str, Any],
                                     metrics: List[str],
                                     title: str = "Regional Comparison Analysis") -> go.Figure:
        """
        Create multi-metric regional comparison with subplots.
        
        Args:
            processor_results: Results from GeographicProcessor
            metrics: List of metric columns to compare
            title: Overall title
            
        Returns:
            Plotly figure with regional comparison subplots
        """
        logger.debug(f"🗺️ Creating regional comparison: {title}")
        
        # Extract data from processor results
        if 'country_summary' not in processor_results:
            logger.warning("No country summary data found in processor results")
            return self._create_empty_map("No geographic data available")
        
        map_data = processor_results['country_summary'].copy()
        
        # Add ISO codes for choropleth mapping
        if 'country_name' in map_data.columns:
            # Basic country name to ISO code mapping
            name_to_iso = {
                'United States': 'US', 'China': 'CN', 'Japan': 'JP', 'Germany': 'DE',
                'United Kingdom': 'GB', 'France': 'FR', 'South Korea': 'KR', 
                'Canada': 'CA', 'Italy': 'IT', 'Netherlands': 'NL', 'Switzerland': 'CH',
                'Sweden': 'SE', 'Australia': 'AU', 'India': 'IN', 'Unknown': 'XX'
            }
            map_data['iso_code'] = map_data['country_name'].map(name_to_iso).fillna('XX')
        elif 'country_code' in map_data.columns:
            map_data['iso_code'] = map_data['country_code']
        
        map_data = map_data[map_data['iso_code'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes for regional comparison")
            return self._create_empty_map("No valid geographic data available")
        
        # Filter metrics to only those available in data
        available_metrics = [m for m in metrics if m in map_data.columns]
        if not available_metrics:
            logger.warning("⚠️ No specified metrics found in data")
            return self._create_empty_map("No specified metrics available")
        
        # Create subplots
        n_metrics = len(available_metrics)
        cols = min(2, n_metrics)
        rows = (n_metrics + 1) // 2
        
        subplot_titles = [metric.replace('_', ' ').title() for metric in available_metrics]
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=subplot_titles,
            specs=[[{"type": "geo"}] * cols for _ in range(rows)],
            horizontal_spacing=0.02,
            vertical_spacing=0.1
        )
        
        # Add choropleth for each metric
        color_schemes = list(self.regional_color_schemes.values())
        
        for i, metric in enumerate(available_metrics):
            row = i // cols + 1
            col = i % cols + 1
            
            # Color scheme rotation
            color_scheme = color_schemes[i % len(color_schemes)]
            
            fig.add_trace(
                go.Choropleth(
                    locations=map_data['iso_code'],
                    z=map_data[metric],
                    locationmode='ISO-3',
                    text=map_data.get('country_name', map_data['iso_code']),
                    colorscale=color_scheme,
                    showscale=True,
                    colorbar=dict(
                        title=metric.replace('_', ' ').title(),
                        thickness=10,
                        len=0.3,
                        x=1.02 if col == cols else 0.48,
                        y=0.8 - (row-1) * 0.5
                    ),
                    hovertemplate=(
                        f"<b>%{{text}}</b><br>" +
                        f"{metric.replace('_', ' ').title()}: %{{z}}<br>" +
                        "<extra></extra>"
                    )
                ),
                row=row, col=col
            )
        
        # Update geo styling for all subplots
        for i in range(1, rows * cols + 1):
            fig.update_geos(
                projection_type='natural earth',
                showframe=False,
                showcoastlines=True,
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="white",
                selector=dict(row=(i-1)//cols + 1, col=(i-1)%cols + 1)
            )
        
        # Layout styling
        title_prefix = self.branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            title_font_size=18,
            height=300 * rows + 100,
            margin=dict(l=0, r=100, t=80, b=0)
        )
        
        return fig
    
    def _add_country_coordinates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Add latitude and longitude coordinates to country data."""
        # Basic country coordinates for major countries
        country_coords = {
            'United States': {'lat': 39.8283, 'lon': -98.5795},
            'China': {'lat': 35.8617, 'lon': 104.1954},
            'Japan': {'lat': 36.2048, 'lon': 138.2529},
            'Germany': {'lat': 51.1657, 'lon': 10.4515},
            'United Kingdom': {'lat': 55.3781, 'lon': -3.4360},
            'France': {'lat': 46.2276, 'lon': 2.2137},
            'South Korea': {'lat': 35.9078, 'lon': 127.7669},
            'Canada': {'lat': 56.1304, 'lon': -106.3468},
            'Italy': {'lat': 41.8719, 'lon': 12.5674},
            'Netherlands': {'lat': 52.1326, 'lon': 5.2913},
            'Switzerland': {'lat': 46.8182, 'lon': 8.2275},
            'Sweden': {'lat': 60.1282, 'lon': 18.6435},
            'Australia': {'lat': -25.2744, 'lon': 133.7751},
            'India': {'lat': 20.5937, 'lon': 78.9629},
            'Unknown': {'lat': 0, 'lon': 0}
        }
        
        # Add lat/lon columns
        data['lat'] = None
        data['lon'] = None
        
        country_col = 'country_name' if 'country_name' in data.columns else data.columns[0]
        
        for idx, row in data.iterrows():
            country_name = row[country_col]
            if country_name in country_coords:
                coords = country_coords[country_name]
                data.at[idx, 'lat'] = coords['lat']
                data.at[idx, 'lon'] = coords['lon']
            elif country_name in self.country_coordinates:
                coords = self.country_coordinates[country_name]
                data.at[idx, 'lat'] = coords['lat']
                data.at[idx, 'lon'] = coords['lon']
        
        return data
    
    def _create_empty_map(self, message: str = "No data available") -> go.Figure:
        """Create empty map with informative message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(
            height=400,
            geo=dict(
                projection_type='natural earth',
                showframe=False,
                showcoastlines=True,
                showland=True,
                landcolor="lightgray"
            )
        )
        return fig

def create_production_maps_creator(config_manager: ConfigurationManager = None) -> ProductionMapsCreator:
    """
    Factory function to create configured production maps creator.
    
    Args:
        config_manager: Configuration manager instance
        
    Returns:
        Configured ProductionMapsCreator instance
    """
    return ProductionMapsCreator(config_manager)

# Production convenience functions for processor integration
def create_choropleth_map(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create choropleth map from processor results."""
    creator = create_production_maps_creator()
    return creator.create_patent_choropleth(processor_results, **kwargs)

def create_strategic_map(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create strategic positioning map from processor results."""
    creator = create_production_maps_creator()
    return creator.create_strategic_positioning_map(processor_results, **kwargs)

def create_regional_comparison(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create regional comparison map from processor results."""
    creator = create_production_maps_creator()
    return creator.create_regional_comparison_map(processor_results, **kwargs)

# Legacy compatibility
def create_maps_creator() -> ProductionMapsCreator:
    """Legacy factory function for backward compatibility."""
    return create_production_maps_creator()

# Production integration example
def demo_production_maps_creation():
    """Demonstrate production maps creation with processor integration."""
    logger.debug("🚀 Production Maps Creation Demo")
    
    try:
        # Initialize production components
        config_manager = ConfigurationManager()
        creator = create_production_maps_creator(config_manager)
        
        # Create sample processor results structure
        np.random.seed(42)
        sample_results = {
            'country_summary': pd.DataFrame({
                'country_name': ['China', 'United States', 'Japan', 'Germany', 'South Korea', 
                               'France', 'United Kingdom', 'Canada', 'Australia', 'Italy'],
                'unique_families': np.random.randint(50, 500, 10),
                'market_share': np.random.uniform(2, 25, 10),
                'innovation_intensity': np.random.uniform(0.1, 1.0, 10),
                'growth_rate': np.random.uniform(-5, 20, 10)
            })
        }
        
        # Create production maps
        choropleth_map = creator.create_patent_choropleth(
            sample_results, title="Global Patent Activity"
        )
        
        strategic_map = creator.create_strategic_positioning_map(
            sample_results, 
            x_metric='unique_families', 
            y_metric='innovation_intensity',
            size_metric='market_share',
            title="Strategic Positioning Analysis"
        )
        
        regional_comparison = creator.create_regional_comparison_map(
            sample_results,
            metrics=['unique_families', 'market_share', 'innovation_intensity'],
            title="Regional Comparison Analysis"
        )
        
        logger.debug("✅ Production demo maps created successfully")
        
        return choropleth_map, strategic_map, regional_comparison
        
    except Exception as e:
        logger.error(f"❌ Maps demo failed: {e}")
        return None, None, None

if __name__ == "__main__":
    demo_production_maps_creation()