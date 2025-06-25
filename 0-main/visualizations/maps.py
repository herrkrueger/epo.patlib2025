"""
Maps Module for REE Patent Analysis Geographic Visualizations
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive geographic visualization capabilities including
choropleth maps, regional analysis, and strategic geographic intelligence.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Union
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MapsCreator:
    """
    Professional geographic visualization creator for patent intelligence.
    """
    
    # ISO country code mapping for choropleth maps
    ISO_COUNTRY_MAPPING = {
        'CN': 'CHN', 'US': 'USA', 'JP': 'JPN', 'KR': 'KOR', 'TW': 'TWN',
        'DE': 'DEU', 'FR': 'FRA', 'GB': 'GBR', 'IT': 'ITA', 'ES': 'ESP',
        'NL': 'NLD', 'BE': 'BEL', 'CH': 'CHE', 'AT': 'AUT', 'SE': 'SWE',
        'NO': 'NOR', 'DK': 'DNK', 'FI': 'FIN', 'IE': 'IRL', 'PT': 'PRT',
        'CA': 'CAN', 'AU': 'AUS', 'NZ': 'NZL', 'IN': 'IND', 'BR': 'BRA',
        'RU': 'RUS', 'MX': 'MEX', 'ZA': 'ZAF', 'SG': 'SGP', 'MY': 'MYS',
        'TH': 'THA', 'ID': 'IDN', 'PH': 'PHL', 'VN': 'VNM', 'HK': 'HKG'
    }
    
    # Regional color schemes
    REGIONAL_COLOR_SCHEMES = {
        'patent_activity': px.colors.sequential.Blues,
        'market_share': px.colors.sequential.Reds,
        'innovation_intensity': px.colors.sequential.Viridis,
        'competitive_strength': px.colors.sequential.Plasma,
        'growth_rate': px.colors.diverging.RdYlGn,
        'strategic_priority': px.colors.sequential.OrRd
    }
    
    # Map projection types
    MAP_PROJECTIONS = {
        'world': 'equirectangular',
        'asia': 'mercator',
        'europe': 'mercator',
        'americas': 'mercator',
        'natural_earth': 'natural earth'
    }
    
    def __init__(self):
        """Initialize maps creator."""
        self.map_counter = 0
    
    def create_patent_choropleth(self, data: pd.DataFrame,
                               country_col: str, value_col: str,
                               title: str = "Global Patent Analysis",
                               color_scheme: str = 'patent_activity',
                               projection: str = 'world',
                               hover_data: List[str] = None) -> go.Figure:
        """
        Create professional choropleth map for patent geographic analysis.
        
        Args:
            data: DataFrame with country-level patent data
            country_col: Column with country codes/names
            value_col: Column with values to map
            title: Map title
            color_scheme: Color scheme for mapping
            projection: Map projection type
            hover_data: Additional columns for hover information
            
        Returns:
            Plotly figure object
        """
        logger.info(f"🗺️ Creating patent choropleth: {title}")
        
        # Data preparation
        map_data = data.copy()
        
        # Convert country codes to ISO format for choropleth
        map_data['iso_country'] = map_data[country_col].map(self.ISO_COUNTRY_MAPPING)
        map_data = map_data[map_data['iso_country'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes found for mapping")
            # Create empty map
            fig = go.Figure()
            fig.add_annotation(
                text="No valid geographic data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Prepare hover information
        hover_template = f"<b>%{{hovertext}}</b><br>{value_col.replace('_', ' ').title()}: %{{z}}<br>"
        if hover_data:
            for col in hover_data:
                if col in map_data.columns:
                    hover_template += f"{col.replace('_', ' ').title()}: %{{customdata[{hover_data.index(col)}]}}<br>"
        hover_template += "<extra></extra>"
        
        # Custom data for hover
        custom_data = []
        if hover_data:
            custom_data = map_data[hover_data].values
        
        # Create choropleth map
        fig = go.Figure()
        
        fig.add_trace(go.Choropleth(
            locations=map_data['iso_country'],
            z=map_data[value_col],
            locationmode='ISO-3',
            text=map_data[country_col],
            hovertext=map_data[country_col],
            customdata=custom_data if len(custom_data) > 0 else None,
            colorscale=self.REGIONAL_COLOR_SCHEMES.get(color_scheme, self.REGIONAL_COLOR_SCHEMES['patent_activity']),
            hovertemplate=hover_template,
            colorbar=dict(
                title=value_col.replace('_', ' ').title(),
                titleside='right',
                thickness=15,
                len=0.7
            )
        ))
        
        # Layout styling
        fig.update_layout(
            title=f"🌍 {title}",
            title_font_size=18,
            geo=dict(
                projection_type=self.MAP_PROJECTIONS.get(projection, 'equirectangular'),
                showframe=False,
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="lightblue",
                showlakes=True,
                lakecolor="lightblue",
                showrivers=True,
                rivercolor="lightblue"
            ),
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def create_regional_comparison_map(self, data: pd.DataFrame,
                                     country_col: str, 
                                     metrics: List[str],
                                     title: str = "Regional Comparison Analysis") -> go.Figure:
        """
        Create multi-metric regional comparison with subplots.
        
        Args:
            data: DataFrame with country-level data
            country_col: Column with country codes/names
            metrics: List of metric columns to compare
            title: Overall title
            
        Returns:
            Plotly figure with subplots
        """
        logger.info(f"🗺️ Creating regional comparison: {title}")
        
        # Prepare data
        map_data = data.copy()
        map_data['iso_country'] = map_data[country_col].map(self.ISO_COUNTRY_MAPPING)
        map_data = map_data[map_data['iso_country'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes for regional comparison")
            return go.Figure()
        
        # Create subplots
        n_metrics = len(metrics)
        cols = min(2, n_metrics)
        rows = (n_metrics + 1) // 2
        
        subplot_titles = [metric.replace('_', ' ').title() for metric in metrics]
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=subplot_titles,
            specs=[[{"type": "geo"}] * cols for _ in range(rows)],
            horizontal_spacing=0.02,
            vertical_spacing=0.1
        )
        
        # Add choropleth for each metric
        for i, metric in enumerate(metrics):
            row = i // cols + 1
            col = i % cols + 1
            
            # Color scheme rotation
            color_schemes = list(self.REGIONAL_COLOR_SCHEMES.values())
            color_scheme = color_schemes[i % len(color_schemes)]
            
            fig.add_trace(
                go.Choropleth(
                    locations=map_data['iso_country'],
                    z=map_data[metric],
                    locationmode='ISO-3',
                    text=map_data[country_col],
                    colorscale=color_scheme,
                    showscale=True,
                    colorbar=dict(
                        title=metric.replace('_', ' ').title(),
                        titleside='right',
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
        fig.update_layout(
            title=f"🌍 {title}",
            title_font_size=18,
            height=300 * rows + 100,
            margin=dict(l=0, r=100, t=80, b=0)
        )
        
        return fig
    
    def create_strategic_positioning_map(self, data: pd.DataFrame,
                                       country_col: str,
                                       x_metric: str, y_metric: str,
                                       size_metric: str = None,
                                       title: str = "Strategic Positioning Analysis") -> go.Figure:
        """
        Create strategic positioning map with bubble overlay on world map.
        
        Args:
            data: DataFrame with country positioning data
            country_col: Column with country codes/names
            x_metric: Metric for x-axis positioning
            y_metric: Metric for y-axis positioning
            size_metric: Metric for bubble sizes (optional)
            title: Map title
            
        Returns:
            Plotly figure object
        """
        logger.info(f"🗺️ Creating strategic positioning map: {title}")
        
        # Country coordinates for bubble placement (major countries)
        COUNTRY_COORDINATES = {
            'China': {'lat': 35.0, 'lon': 105.0},
            'United States': {'lat': 40.0, 'lon': -100.0},
            'Japan': {'lat': 36.0, 'lon': 138.0},
            'Germany': {'lat': 51.0, 'lon': 9.0},
            'South Korea': {'lat': 36.0, 'lon': 128.0},
            'France': {'lat': 46.0, 'lon': 2.0},
            'United Kingdom': {'lat': 54.0, 'lon': -2.0},
            'Canada': {'lat': 60.0, 'lon': -95.0},
            'Australia': {'lat': -25.0, 'lon': 135.0},
            'Italy': {'lat': 42.0, 'lon': 12.0},
            'Spain': {'lat': 40.0, 'lon': -4.0},
            'Netherlands': {'lat': 52.0, 'lon': 5.0},
            'Sweden': {'lat': 60.0, 'lon': 18.0},
            'Switzerland': {'lat': 47.0, 'lon': 8.0},
            'India': {'lat': 20.0, 'lon': 77.0},
            'Brazil': {'lat': -14.0, 'lon': -51.0},
            'Russia': {'lat': 60.0, 'lon': 100.0},
            'Singapore': {'lat': 1.0, 'lon': 104.0},
            'Taiwan': {'lat': 24.0, 'lon': 121.0}
        }
        
        # Prepare data with coordinates
        map_data = data.copy()
        
        # Add coordinates
        map_data['lat'] = map_data[country_col].map(lambda x: COUNTRY_COORDINATES.get(x, {}).get('lat'))
        map_data['lon'] = map_data[country_col].map(lambda x: COUNTRY_COORDINATES.get(x, {}).get('lon'))
        
        # Filter out countries without coordinates
        map_data = map_data[map_data['lat'].notna() & map_data['lon'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No countries with coordinates found")
            return go.Figure()
        
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
        
        # Prepare bubble sizes
        if size_metric and size_metric in map_data.columns:
            bubble_sizes = map_data[size_metric]
            size_ref = 2. * max(bubble_sizes) / (50**2)
        else:
            bubble_sizes = [20] * len(map_data)
            size_ref = 1
        
        # Create strategic quadrants based on median values
        x_median = map_data[x_metric].median()
        y_median = map_data[y_metric].median()
        
        def get_quadrant(x_val, y_val):
            if x_val >= x_median and y_val >= y_median:
                return 'Leaders'
            elif x_val >= x_median and y_val < y_median:
                return 'Challengers'
            elif x_val < x_median and y_val >= y_median:
                return 'Innovators'
            else:
                return 'Followers'
        
        map_data['strategic_quadrant'] = map_data.apply(
            lambda row: get_quadrant(row[x_metric], row[y_metric]), axis=1
        )
        
        # Color mapping for quadrants
        quadrant_colors = {
            'Leaders': '#2E8B57',      # Sea Green
            'Challengers': '#FF6347',  # Tomato
            'Innovators': '#4169E1',   # Royal Blue
            'Followers': '#DAA520'     # Golden Rod
        }
        
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
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                text=quadrant_data[country_col],
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
        fig.update_layout(
            title=f"🎯 {title}",
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
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        return fig
    
    def create_filing_evolution_map(self, data: pd.DataFrame,
                                  country_col: str, year_col: str, value_col: str,
                                  title: str = "Patent Filing Evolution",
                                  animation_speed: int = 1000) -> go.Figure:
        """
        Create animated choropleth showing patent filing evolution over time.
        
        Args:
            data: DataFrame with temporal country data
            country_col: Column with country codes/names
            year_col: Column with years
            value_col: Column with values to animate
            title: Map title
            animation_speed: Animation speed in milliseconds
            
        Returns:
            Plotly figure with animation
        """
        logger.info(f"🗺️ Creating filing evolution map: {title}")
        
        # Data preparation
        map_data = data.copy()
        map_data['iso_country'] = map_data[country_col].map(self.ISO_COUNTRY_MAPPING)
        map_data = map_data[map_data['iso_country'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes for evolution map")
            return go.Figure()
        
        # Ensure all years have all countries (fill missing with 0)
        years = sorted(map_data[year_col].unique())
        countries = map_data['iso_country'].unique()
        
        # Create complete year-country grid
        full_data = []
        for year in years:
            year_data = map_data[map_data[year_col] == year]
            for country in countries:
                country_info = map_data[map_data['iso_country'] == country].iloc[0]
                
                if country in year_data['iso_country'].values:
                    value = year_data[year_data['iso_country'] == country][value_col].iloc[0]
                else:
                    value = 0
                
                full_data.append({
                    year_col: year,
                    'iso_country': country,
                    country_col: country_info[country_col],
                    value_col: value
                })
        
        full_df = pd.DataFrame(full_data)
        
        # Create animated choropleth
        fig = px.choropleth(
            full_df,
            locations='iso_country',
            color=value_col,
            animation_frame=year_col,
            hover_name=country_col,
            color_continuous_scale='Blues',
            range_color=[0, full_df[value_col].max()],
            title=f"🗺️ {title}",
            labels={value_col: value_col.replace('_', ' ').title()}
        )
        
        # Update layout
        fig.update_geos(
            projection_type='natural earth',
            showframe=False,
            showcoastlines=True,
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="lightblue"
        )
        
        fig.update_layout(
            title_font_size=18,
            height=600,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        # Configure animation
        fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = animation_speed
        fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = animation_speed // 2
        
        return fig
    
    def create_regional_clusters_map(self, data: pd.DataFrame,
                                   country_col: str, cluster_col: str,
                                   title: str = "Regional Clusters Analysis") -> go.Figure:
        """
        Create map showing regional clusters and groupings.
        
        Args:
            data: DataFrame with country cluster data
            country_col: Column with country codes/names
            cluster_col: Column with cluster assignments
            title: Map title
            
        Returns:
            Plotly figure object
        """
        logger.info(f"🗺️ Creating regional clusters map: {title}")
        
        # Data preparation
        map_data = data.copy()
        map_data['iso_country'] = map_data[country_col].map(self.ISO_COUNTRY_MAPPING)
        map_data = map_data[map_data['iso_country'].notna()].copy()
        
        if len(map_data) == 0:
            logger.warning("⚠️ No valid country codes for clusters map")
            return go.Figure()
        
        # Create discrete color mapping for clusters
        unique_clusters = sorted(map_data[cluster_col].unique())
        colors = px.colors.qualitative.Set3[:len(unique_clusters)]
        
        fig = go.Figure()
        
        for i, cluster in enumerate(unique_clusters):
            cluster_data = map_data[map_data[cluster_col] == cluster]
            
            fig.add_trace(go.Choropleth(
                locations=cluster_data['iso_country'],
                z=[i] * len(cluster_data),  # Use index for color
                locationmode='ISO-3',
                text=cluster_data[country_col],
                name=str(cluster),
                colorscale=[[0, colors[i]], [1, colors[i]]],
                showscale=False,
                hovertemplate=(
                    f"<b>%{{text}}</b><br>" +
                    f"Cluster: {cluster}<br>" +
                    "<extra></extra>"
                )
            ))
        
        # Layout styling
        fig.update_layout(
            title=f"🌍 {title}",
            title_font_size=18,
            geo=dict(
                projection_type='natural earth',
                showframe=False,
                showcoastlines=True,
                showland=True,
                landcolor="lightgray",
                showocean=True,
                oceancolor="lightblue"
            ),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.02
            ),
            height=600,
            margin=dict(l=0, r=0, t=60, b=0)
        )
        
        return fig

def create_maps_creator() -> MapsCreator:
    """
    Factory function to create configured maps creator.
    
    Returns:
        Configured MapsCreator instance
    """
    return MapsCreator()

# Convenience functions for quick map creation
def quick_choropleth(data: pd.DataFrame, country: str, value: str, **kwargs) -> go.Figure:
    """Quick choropleth map creation."""
    creator = create_maps_creator()
    return creator.create_patent_choropleth(data, country, value, **kwargs)

def quick_strategic_map(data: pd.DataFrame, country: str, x: str, y: str, **kwargs) -> go.Figure:
    """Quick strategic positioning map creation."""
    creator = create_maps_creator()
    return creator.create_strategic_positioning_map(data, country, x, y, **kwargs)

# Example usage and demo functions
def demo_maps_creation():
    """Demonstrate maps creation capabilities."""
    logger.info("🚀 Maps Creation Demo")
    
    # Create sample geographic data
    np.random.seed(42)
    
    countries = ['China', 'United States', 'Japan', 'Germany', 'South Korea', 
                'France', 'United Kingdom', 'Canada', 'Australia', 'Italy']
    
    sample_data = pd.DataFrame({
        'country_name': countries,
        'patent_families': np.random.randint(50, 500, len(countries)),
        'market_share': np.random.uniform(2, 25, len(countries)),
        'innovation_intensity': np.random.uniform(0.1, 1.0, len(countries)),
        'growth_rate': np.random.uniform(-5, 20, len(countries))
    })
    
    # Create maps
    creator = create_maps_creator()
    
    # Choropleth map
    choropleth_fig = creator.create_patent_choropleth(
        sample_data, 'country_name', 'patent_families',
        title="Global Patent Activity"
    )
    
    # Strategic positioning map
    strategic_fig = creator.create_strategic_positioning_map(
        sample_data, 'country_name', 'market_share', 'innovation_intensity',
        size_metric='patent_families',
        title="Strategic Positioning Analysis"
    )
    
    logger.info("✅ Demo maps created successfully")
    
    return choropleth_fig, strategic_fig

if __name__ == "__main__":
    demo_maps_creation()