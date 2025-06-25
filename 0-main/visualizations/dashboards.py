"""
Dashboards Module for REE Patent Analysis Interactive Visualizations
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive dashboard creation capabilities for patent intelligence
with multi-panel layouts, interactive features, and business intelligence formatting.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import networkx as nx
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from datetime import datetime
import json

# Import our other visualization modules
from .charts import ChartCreator
from .maps import MapsCreator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardCreator:
    """
    Professional dashboard creation for comprehensive patent intelligence analysis.
    """
    
    # Dashboard layout templates
    DASHBOARD_LAYOUTS = {
        'executive_summary': {
            'rows': 2, 'cols': 2,
            'specs': [[{"secondary_y": False}, {"type": "pie"}],
                     [{"type": "bar"}, {"type": "scatter"}]],
            'titles': ['Market Leaders', 'Market Share', 'Geographic Distribution', 'Activity Timeline']
        },
        'technology_intelligence': {
            'rows': 2, 'cols': 3,
            'specs': [[{"secondary_y": False}, {"type": "pie"}, {"type": "bar"}],
                     [{"colspan": 2}, None, {"type": "scatter"}]],
            'titles': ['Technology Network', 'Domain Distribution', 'Innovation Metrics', 
                      'Technology Evolution', '', 'Emergence Patterns']
        },
        'competitive_landscape': {
            'rows': 3, 'cols': 2,
            'specs': [[{"type": "geo", "colspan": 2}, None],
                     [{"secondary_y": False}, {"type": "pie"}],
                     [{"type": "bar"}, {"type": "scatter"}]],
            'titles': ['Global Patent Landscape', '', 'Market Leaders', 'Regional Distribution',
                      'Competitive Tiers', 'Strategic Positioning']
        },
        'trends_analysis': {
            'rows': 2, 'cols': 3,
            'specs': [[{"secondary_y": True}, {"type": "bar"}, {"type": "pie"}],
                     [{"colspan": 3}, None, None]],
            'titles': ['Filing Trends', 'Technology Growth', 'Lifecycle Distribution',
                      'Market Events & Correlation Analysis']
        }
    }
    
    # Professional color themes
    DASHBOARD_THEMES = {
        'corporate': {
            'background': '#f8f9fa',
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'accent': '#2ca02c',
            'text': '#2c3e50'
        },
        'patent_intelligence': {
            'background': '#ffffff',
            'primary': '#3498db',
            'secondary': '#e74c3c',
            'accent': '#27ae60',
            'text': '#34495e'
        },
        'scientific': {
            'background': '#f5f5f5',
            'primary': '#2E8B57',
            'secondary': '#4169E1',
            'accent': '#FF6347',
            'text': '#2F4F4F'
        }
    }
    
    def __init__(self, theme: str = 'patent_intelligence'):
        """
        Initialize dashboard creator with theme.
        
        Args:
            theme: Dashboard color theme
        """
        self.theme = theme
        self.chart_creator = ChartCreator(theme='professional')
        self.maps_creator = MapsCreator()
        self.dashboard_counter = 0
    
    def create_executive_dashboard(self, data: Dict[str, pd.DataFrame],
                                 title: str = "REE Patent Intelligence - Executive Dashboard") -> go.Figure:
        """
        Create comprehensive executive dashboard for patent intelligence.
        
        Args:
            data: Dictionary with different data types (applicant, geographic, temporal)
            title: Dashboard title
            
        Returns:
            Plotly figure with multi-panel dashboard
        """
        logger.info(f"📊 Creating executive dashboard: {title}")
        
        layout = self.DASHBOARD_LAYOUTS['executive_summary']
        
        # Create subplot structure
        fig = make_subplots(
            rows=layout['rows'], 
            cols=layout['cols'],
            specs=layout['specs'],
            subplot_titles=layout['titles'],
            horizontal_spacing=0.1,
            vertical_spacing=0.15
        )
        
        # Panel 1: Market Leaders (Bubble Scatter)
        if 'applicant_data' in data and len(data['applicant_data']) > 0:
            applicant_data = data['applicant_data'].head(20)
            
            fig.add_trace(
                go.Scatter(
                    x=applicant_data.get('Patent_Families', applicant_data.iloc[:, 1]),
                    y=list(range(len(applicant_data))),
                    mode='markers+text',
                    marker=dict(
                        size=applicant_data.get('Market_Share_Pct', applicant_data.iloc[:, 1]),
                        sizeref=2. * applicant_data.get('Market_Share_Pct', applicant_data.iloc[:, 1]).max() / (40**2),
                        sizemin=8,
                        color=applicant_data.get('Market_Share_Pct', applicant_data.iloc[:, 1]),
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(x=0.48, len=0.4)
                    ),
                    text=applicant_data.iloc[:, 0].str[:25],
                    textposition='middle right',
                    name='Patent Leaders',
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Patent Families: %{x}<br>" +
                        "Market Share: %{marker.color:.1f}%<br>" +
                        "<extra></extra>"
                    )
                ),
                row=1, col=1
            )
        
        # Panel 2: Market Share (Pie Chart)
        if 'applicant_data' in data and len(data['applicant_data']) > 0:
            top_applicants = data['applicant_data'].head(10)
            share_col = 'Market_Share_Pct' if 'Market_Share_Pct' in top_applicants.columns else top_applicants.columns[1]
            
            # Create top 10 + others
            top_10_share = top_applicants[share_col].sum()
            others_share = 100 - top_10_share if top_10_share < 100 else 0
            
            pie_values = list(top_applicants[share_col]) + ([others_share] if others_share > 0 else [])
            pie_labels = list(top_applicants.iloc[:, 0].str[:20]) + (['Others'] if others_share > 0 else [])
            
            fig.add_trace(
                go.Pie(
                    values=pie_values,
                    labels=pie_labels,
                    hole=0.3,
                    textinfo='label+percent',
                    textposition='auto',
                    name='Market Share'
                ),
                row=1, col=2
            )
        
        # Panel 3: Geographic Distribution (Bar Chart)
        if 'geographic_data' in data and len(data['geographic_data']) > 0:
            geo_data = data['geographic_data']
            country_col = 'country_name' if 'country_name' in geo_data.columns else geo_data.columns[0]
            value_col = 'unique_families' if 'unique_families' in geo_data.columns else geo_data.columns[1]
            
            geo_summary = geo_data.groupby(country_col)[value_col].sum().sort_values(ascending=True).tail(15)
            
            fig.add_trace(
                go.Bar(
                    x=geo_summary.values,
                    y=geo_summary.index,
                    orientation='h',
                    marker_color='lightblue',
                    name='Geographic Distribution',
                    hovertemplate=(
                        "<b>%{y}</b><br>" +
                        f"{value_col.replace('_', ' ').title()}: %{{x}}<br>" +
                        "<extra></extra>"
                    )
                ),
                row=2, col=1
            )
        
        # Panel 4: Activity Timeline (Line Chart)
        if 'temporal_data' in data and len(data['temporal_data']) > 0:
            temporal_data = data['temporal_data']
            year_col = 'filing_year' if 'filing_year' in temporal_data.columns else temporal_data.columns[0]
            
            annual_activity = temporal_data.groupby(year_col).size().reset_index(name='patent_count')
            
            fig.add_trace(
                go.Scatter(
                    x=annual_activity[year_col],
                    y=annual_activity['patent_count'],
                    mode='lines+markers',
                    line=dict(color='red', width=3),
                    marker=dict(size=8),
                    name='Filing Activity',
                    hovertemplate=(
                        "Year: %{x}<br>" +
                        "Patent Count: %{y}<br>" +
                        "<extra></extra>"
                    )
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title=f"🎯 {title}",
            title_font_size=20,
            height=800,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor=self.DASHBOARD_THEMES[self.theme]['background']
        )
        
        return fig
    
    def create_technology_dashboard(self, data: Dict[str, Any],
                                  title: str = "Technology Intelligence Dashboard") -> go.Figure:
        """
        Create comprehensive technology intelligence dashboard.
        
        Args:
            data: Dictionary with technology analysis results
            title: Dashboard title
            
        Returns:
            Plotly figure with technology analysis panels
        """
        logger.info(f"📊 Creating technology dashboard: {title}")
        
        layout = self.DASHBOARD_LAYOUTS['technology_intelligence']
        
        # Create subplot structure
        fig = make_subplots(
            rows=layout['rows'], 
            cols=layout['cols'],
            specs=layout['specs'],
            subplot_titles=layout['titles'],
            horizontal_spacing=0.08,
            vertical_spacing=0.15
        )
        
        # Panel 1: Technology Network (if network data available)
        if 'network_graph' in data and data['network_graph']:
            network = data['network_graph']
            pos = nx.spring_layout(network, k=3, iterations=50, seed=42)
            
            # Add edges
            edge_x = []
            edge_y = []
            for edge in network.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            fig.add_trace(
                go.Scatter(
                    x=edge_x, y=edge_y,
                    line=dict(width=1, color='lightgray'),
                    hoverinfo='none',
                    mode='lines',
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # Add nodes
            node_x = [pos[node][0] for node in network.nodes()]
            node_y = [pos[node][1] for node in network.nodes()]
            node_text = list(network.nodes())
            
            fig.add_trace(
                go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    marker=dict(size=15, color='lightblue', line=dict(width=2, color='darkblue')),
                    text=node_text,
                    textposition="middle center",
                    textfont=dict(size=8),
                    name='Technology Network',
                    hovertemplate="<b>%{text}</b><extra></extra>"
                ),
                row=1, col=1
            )
        
        # Panel 2: Domain Distribution (Pie Chart)
        if 'technology_data' in data and len(data['technology_data']) > 0:
            tech_data = data['technology_data']
            domain_col = 'ree_technology_area' if 'ree_technology_area' in tech_data.columns else 'domain'
            
            if domain_col in tech_data.columns:
                domain_dist = tech_data[domain_col].value_counts()
                
                fig.add_trace(
                    go.Pie(
                        values=domain_dist.values,
                        labels=domain_dist.index,
                        hole=0.3,
                        textinfo='label+percent',
                        name='Technology Domains'
                    ),
                    row=1, col=2
                )
        
        # Panel 3: Innovation Metrics (Bar Chart)
        if 'innovation_metrics' in data:
            metrics = data['innovation_metrics']
            
            fig.add_trace(
                go.Bar(
                    x=list(metrics.keys()),
                    y=list(metrics.values()),
                    marker_color='orange',
                    name='Innovation Metrics',
                    hovertemplate="<b>%{x}</b><br>Value: %{y}<extra></extra>"
                ),
                row=1, col=3
            )
        
        # Panel 4: Technology Evolution (Large panel)
        if 'evolution_data' in data and len(data['evolution_data']) > 0:
            evolution_data = data['evolution_data']
            
            # Create time series for major technology areas
            tech_areas = evolution_data['technology_area'].unique()[:5]  # Top 5 areas
            colors = px.colors.qualitative.Set1
            
            for i, tech_area in enumerate(tech_areas):
                tech_time_data = evolution_data[evolution_data['technology_area'] == tech_area]
                
                fig.add_trace(
                    go.Scatter(
                        x=tech_time_data['year'],
                        y=tech_time_data['patent_families'],
                        mode='lines+markers',
                        name=tech_area[:20],
                        line=dict(color=colors[i % len(colors)], width=3),
                        hovertemplate=(
                            f"<b>{tech_area}</b><br>" +
                            "Year: %{x}<br>" +
                            "Patents: %{y}<br>" +
                            "<extra></extra>"
                        )
                    ),
                    row=2, col=1
                )
        
        # Panel 5: Emergence Patterns (Scatter)
        if 'emergence_data' in data and len(data['emergence_data']) > 0:
            emergence_data = data['emergence_data']
            
            fig.add_trace(
                go.Scatter(
                    x=emergence_data.get('emergence_score', range(len(emergence_data))),
                    y=emergence_data.get('novelty_score', range(len(emergence_data))),
                    mode='markers',
                    marker=dict(
                        size=emergence_data.get('total_families', [10]*len(emergence_data)),
                        color='green',
                        opacity=0.7
                    ),
                    text=emergence_data.get('technology', emergence_data.iloc[:, 0] if len(emergence_data.columns) > 0 else []),
                    name='Emerging Technologies',
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Emergence Score: %{x}<br>" +
                        "Novelty Score: %{y}<br>" +
                        "<extra></extra>"
                    )
                ),
                row=2, col=3
            )
        
        # Update layout
        fig.update_layout(
            title=f"🔬 {title}",
            title_font_size=20,
            height=900,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor=self.DASHBOARD_THEMES[self.theme]['background']
        )
        
        return fig
    
    def create_competitive_landscape_dashboard(self, data: Dict[str, Any],
                                             title: str = "Competitive Landscape Dashboard") -> go.Figure:
        """
        Create comprehensive competitive landscape dashboard.
        
        Args:
            data: Dictionary with competitive analysis results
            title: Dashboard title
            
        Returns:
            Plotly figure with competitive analysis panels
        """
        logger.info(f"📊 Creating competitive landscape dashboard: {title}")
        
        layout = self.DASHBOARD_LAYOUTS['competitive_landscape']
        
        # Create subplot structure
        fig = make_subplots(
            rows=layout['rows'], 
            cols=layout['cols'],
            specs=layout['specs'],
            subplot_titles=layout['titles'],
            horizontal_spacing=0.1,
            vertical_spacing=0.12
        )
        
        # Panel 1: Global Patent Landscape (Geographic - spans 2 columns)
        if 'geographic_data' in data and len(data['geographic_data']) > 0:
            geo_data = data['geographic_data']
            
            # Prepare ISO country mapping for choropleth
            iso_mapping = {
                'China': 'CHN', 'United States': 'USA', 'Japan': 'JPN', 'Germany': 'DEU',
                'South Korea': 'KOR', 'France': 'FRA', 'United Kingdom': 'GBR',
                'Canada': 'CAN', 'Australia': 'AUS', 'Italy': 'ITA'
            }
            
            country_col = 'country_name' if 'country_name' in geo_data.columns else geo_data.columns[0]
            value_col = 'unique_families' if 'unique_families' in geo_data.columns else geo_data.columns[1]
            
            geo_summary = geo_data.groupby(country_col)[value_col].sum().reset_index()
            geo_summary['iso_code'] = geo_summary[country_col].map(iso_mapping)
            geo_summary = geo_summary[geo_summary['iso_code'].notna()]
            
            if len(geo_summary) > 0:
                fig.add_trace(
                    go.Choropleth(
                        locations=geo_summary['iso_code'],
                        z=geo_summary[value_col],
                        locationmode='ISO-3',
                        colorscale='Blues',
                        text=geo_summary[country_col],
                        hovertemplate=(
                            "<b>%{text}</b><br>" +
                            f"{value_col.replace('_', ' ').title()}: %{{z}}<br>" +
                            "<extra></extra>"
                        ),
                        showscale=True,
                        colorbar=dict(x=1.0, len=0.3)
                    ),
                    row=1, col=1
                )
        
        # Panel 2: Market Leaders (Bubble Chart)
        if 'applicant_data' in data and len(data['applicant_data']) > 0:
            applicant_data = data['applicant_data'].head(15)
            
            fig.add_trace(
                go.Scatter(
                    x=applicant_data.get('Patent_Families', applicant_data.iloc[:, 1]),
                    y=applicant_data.get('Market_Share_Pct', range(len(applicant_data))),
                    mode='markers+text',
                    marker=dict(
                        size=applicant_data.get('Patent_Families', applicant_data.iloc[:, 1]),
                        sizeref=2. * applicant_data.get('Patent_Families', applicant_data.iloc[:, 1]).max() / (30**2),
                        sizemin=8,
                        color='red',
                        opacity=0.7
                    ),
                    text=applicant_data.iloc[:, 0].str[:15],
                    textposition='middle right',
                    name='Market Leaders',
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Patents: %{x}<br>" +
                        "Market Share: %{y:.1f}%<br>" +
                        "<extra></extra>"
                    )
                ),
                row=2, col=1
            )
        
        # Panel 3: Regional Distribution (Pie Chart)
        if 'regional_data' in data:
            regional_data = data['regional_data']
            
            if isinstance(regional_data, dict):
                fig.add_trace(
                    go.Pie(
                        values=list(regional_data.values()),
                        labels=list(regional_data.keys()),
                        hole=0.3,
                        textinfo='label+percent',
                        name='Regional Distribution'
                    ),
                    row=2, col=2
                )
        
        # Panel 4: Competitive Tiers (Bar Chart)
        if 'competitive_tiers' in data:
            tiers_data = data['competitive_tiers']
            
            if isinstance(tiers_data, dict):
                fig.add_trace(
                    go.Bar(
                        x=list(tiers_data.keys()),
                        y=list(tiers_data.values()),
                        marker_color=['gold', 'silver', '#CD7F32', 'gray'],
                        name='Competitive Tiers',
                        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
                    ),
                    row=3, col=1
                )
        
        # Panel 5: Strategic Positioning (Scatter)
        if 'strategic_positioning' in data and len(data['strategic_positioning']) > 0:
            strategic_data = data['strategic_positioning']
            
            fig.add_trace(
                go.Scatter(
                    x=strategic_data.get('market_position', range(len(strategic_data))),
                    y=strategic_data.get('innovation_potential', range(len(strategic_data))),
                    mode='markers+text',
                    marker=dict(size=12, color='blue', opacity=0.7),
                    text=strategic_data.get('entity', strategic_data.iloc[:, 0] if len(strategic_data.columns) > 0 else []),
                    textposition='top center',
                    name='Strategic Position',
                    hovertemplate=(
                        "<b>%{text}</b><br>" +
                        "Market Position: %{x}<br>" +
                        "Innovation Potential: %{y}<br>" +
                        "<extra></extra>"
                    )
                ),
                row=3, col=2
            )
        
        # Update geo layout for choropleth
        fig.update_geos(
            projection_type='natural earth',
            showframe=False,
            showcoastlines=True,
            showland=True,
            landcolor="lightgray",
            showocean=True,
            oceancolor="white"
        )
        
        # Update layout
        fig.update_layout(
            title=f"🏆 {title}",
            title_font_size=20,
            height=1000,
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor=self.DASHBOARD_THEMES[self.theme]['background']
        )
        
        return fig
    
    def create_trends_dashboard(self, data: Dict[str, Any],
                              title: str = "Patent Trends & Market Intelligence Dashboard") -> go.Figure:
        """
        Create comprehensive trends analysis dashboard.
        
        Args:
            data: Dictionary with trends analysis results
            title: Dashboard title
            
        Returns:
            Plotly figure with trends analysis panels
        """
        logger.info(f"📊 Creating trends dashboard: {title}")
        
        layout = self.DASHBOARD_LAYOUTS['trends_analysis']
        
        # Create subplot structure
        fig = make_subplots(
            rows=layout['rows'], 
            cols=layout['cols'],
            specs=layout['specs'],
            subplot_titles=layout['titles'],
            horizontal_spacing=0.08,
            vertical_spacing=0.15,
            secondary_y=True
        )
        
        # Panel 1: Filing Trends with Market Events
        if 'temporal_data' in data and len(data['temporal_data']) > 0:
            temporal_data = data['temporal_data']
            year_col = 'filing_year' if 'filing_year' in temporal_data.columns else temporal_data.columns[0]
            
            annual_activity = temporal_data.groupby(year_col).size().reset_index(name='patent_count')
            
            # Primary y-axis: Patent filings
            fig.add_trace(
                go.Scatter(
                    x=annual_activity[year_col],
                    y=annual_activity['patent_count'],
                    mode='lines+markers',
                    line=dict(color='blue', width=3),
                    marker=dict(size=8),
                    name='Patent Filings'
                ),
                row=1, col=1, secondary_y=False
            )
            
            # Add market events as annotations
            market_events = {
                2010: "REE Crisis", 2011: "Price Peak", 2014: "Stabilization",
                2017: "EV Boom", 2020: "COVID Impact", 2022: "Supply Chain"
            }
            
            for year, event in market_events.items():
                if year in annual_activity[year_col].values:
                    fig.add_annotation(
                        x=year, y=annual_activity[annual_activity[year_col] == year]['patent_count'].iloc[0],
                        text=event, showarrow=True, arrowhead=2,
                        row=1, col=1
                    )
        
        # Panel 2: Technology Growth Rates
        if 'technology_growth' in data:
            growth_data = data['technology_growth']
            
            if isinstance(growth_data, dict):
                fig.add_trace(
                    go.Bar(
                        x=list(growth_data.keys()),
                        y=list(growth_data.values()),
                        marker_color='green',
                        name='Growth Rates',
                        hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>"
                    ),
                    row=1, col=2
                )
        
        # Panel 3: Technology Lifecycle Distribution
        if 'lifecycle_data' in data:
            lifecycle_data = data['lifecycle_data']
            
            if isinstance(lifecycle_data, dict):
                fig.add_trace(
                    go.Pie(
                        values=list(lifecycle_data.values()),
                        labels=list(lifecycle_data.keys()),
                        hole=0.3,
                        textinfo='label+percent',
                        name='Lifecycle Stages'
                    ),
                    row=1, col=3
                )
        
        # Panel 4: Market Events & Correlation Analysis (Large panel)
        if 'correlation_data' in data and len(data['correlation_data']) > 0:
            corr_data = data['correlation_data']
            
            # Create heatmap for correlations
            fig.add_trace(
                go.Heatmap(
                    z=corr_data.values if hasattr(corr_data, 'values') else [[0.5, 0.3], [0.3, 0.8]],
                    x=corr_data.columns if hasattr(corr_data, 'columns') else ['Market Events', 'Patent Activity'],
                    y=corr_data.index if hasattr(corr_data, 'index') else ['Filing Rate', 'Growth Rate'],
                    colorscale='RdBu_r',
                    zmid=0,
                    text=corr_data.round(2).values if hasattr(corr_data, 'values') else [['0.5', '0.3'], ['0.3', '0.8']],
                    texttemplate='%{text}',
                    textfont=dict(size=12),
                    name='Correlations'
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=f"📈 {title}",
            title_font_size=20,
            height=800,
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor=self.DASHBOARD_THEMES[self.theme]['background']
        )
        
        return fig
    
    def create_network_visualization_panel(self, network_graph: nx.Graph,
                                         title: str = "Technology Network Analysis",
                                         layout_algorithm: str = 'spring') -> go.Figure:
        """
        Create specialized network visualization panel.
        
        Args:
            network_graph: NetworkX graph object
            title: Panel title
            layout_algorithm: Layout algorithm ('spring', 'circular', 'random')
            
        Returns:
            Plotly figure with network visualization
        """
        logger.info(f"🕸️ Creating network visualization: {title}")
        
        if not network_graph or network_graph.number_of_nodes() == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="No network data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            return fig
        
        # Calculate layout
        if layout_algorithm == 'spring':
            pos = nx.spring_layout(network_graph, k=3, iterations=50, seed=42)
        elif layout_algorithm == 'circular':
            pos = nx.circular_layout(network_graph)
        else:
            pos = nx.random_layout(network_graph, seed=42)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        edge_x = []
        edge_y = []
        edge_weights = []
        
        for edge in network_graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2].get('weight', 1))
        
        # Edge trace
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='rgba(128,128,128,0.5)'),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
        # Add nodes
        node_x = [pos[node][0] for node in network_graph.nodes()]
        node_y = [pos[node][1] for node in network_graph.nodes()]
        node_text = list(network_graph.nodes())
        
        # Node sizes based on degree
        node_degrees = [network_graph.degree(node) for node in network_graph.nodes()]
        max_degree = max(node_degrees) if node_degrees else 1
        node_sizes = [20 + (degree/max_degree) * 30 for degree in node_degrees]
        
        # Node colors based on attributes
        node_colors = []
        for node in network_graph.nodes(data=True):
            domain = node[1].get('domain', 'Other')
            color_map = {
                'Extraction': '#FF6B6B',
                'Materials': '#4ECDC4', 
                'Energy': '#45B7D1',
                'Electronics': '#96CEB4',
                'Other': '#FECA57'
            }
            node_colors.append(color_map.get(domain, '#FECA57'))
        
        # Node trace
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=node_text,
            textposition="middle center",
            textfont=dict(size=8, color='white'),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Connections: %{marker.size}<br>" +
                "<extra></extra>"
            ),
            showlegend=False
        ))
        
        # Layout
        fig.update_layout(
            title=f"🕸️ {title}",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            annotations=[ dict(
                text="Network shows technology co-occurrence patterns",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.005, y=-0.002,
                xanchor='left', yanchor='bottom',
                font=dict(color='gray', size=10)
            )],
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        return fig
    
    def export_dashboard_data(self, dashboard_data: Dict[str, Any], 
                            filename_prefix: str = "patent_intelligence") -> Dict[str, str]:
        """
        Export dashboard data to multiple formats for business intelligence.
        
        Args:
            dashboard_data: Dictionary with dashboard data
            filename_prefix: Prefix for exported files
            
        Returns:
            Dictionary with export file paths
        """
        logger.info(f"💾 Exporting dashboard data: {filename_prefix}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_files = {}
        
        try:
            # Export summary to JSON
            summary_file = f"{filename_prefix}_summary_{timestamp}.json"
            with open(summary_file, 'w') as f:
                # Convert DataFrames to dict for JSON serialization
                json_data = {}
                for key, value in dashboard_data.items():
                    if isinstance(value, pd.DataFrame):
                        json_data[key] = value.to_dict('records')
                    elif isinstance(value, (dict, list, str, int, float)):
                        json_data[key] = value
                    else:
                        json_data[key] = str(value)
                
                json.dump(json_data, f, indent=2, default=str)
            
            export_files['summary'] = summary_file
            
            # Export detailed data to Excel (if pandas DataFrames present)
            excel_data = {k: v for k, v in dashboard_data.items() if isinstance(v, pd.DataFrame)}
            if excel_data:
                excel_file = f"{filename_prefix}_detailed_{timestamp}.xlsx"
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    for sheet_name, df in excel_data.items():
                        # Limit sheet name length
                        clean_sheet_name = sheet_name[:30].replace('/', '_')
                        df.to_excel(writer, sheet_name=clean_sheet_name, index=False)
                
                export_files['detailed'] = excel_file
            
            logger.info(f"✅ Export complete: {len(export_files)} files created")
            
        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            export_files['error'] = str(e)
        
        return export_files

def create_dashboard_creator(theme: str = 'patent_intelligence') -> DashboardCreator:
    """
    Factory function to create configured dashboard creator.
    
    Args:
        theme: Dashboard theme
        
    Returns:
        Configured DashboardCreator instance
    """
    return DashboardCreator(theme)

# Convenience functions for quick dashboard creation
def quick_executive_dashboard(data: Dict[str, pd.DataFrame], **kwargs) -> go.Figure:
    """Quick executive dashboard creation."""
    creator = create_dashboard_creator()
    return creator.create_executive_dashboard(data, **kwargs)

def quick_technology_dashboard(data: Dict[str, Any], **kwargs) -> go.Figure:
    """Quick technology dashboard creation."""
    creator = create_dashboard_creator()
    return creator.create_technology_dashboard(data, **kwargs)

def quick_competitive_dashboard(data: Dict[str, Any], **kwargs) -> go.Figure:
    """Quick competitive landscape dashboard creation."""
    creator = create_dashboard_creator()
    return creator.create_competitive_landscape_dashboard(data, **kwargs)

# Example usage and demo functions
def demo_dashboard_creation():
    """Demonstrate dashboard creation capabilities."""
    logger.info("🚀 Dashboard Creation Demo")
    
    # Create sample data
    np.random.seed(42)
    
    sample_data = {
        'applicant_data': pd.DataFrame({
            'Applicant': [f'Company_{i}' for i in range(1, 21)],
            'Patent_Families': np.random.randint(10, 100, 20),
            'Market_Share_Pct': np.random.uniform(1, 15, 20)
        }),
        'geographic_data': pd.DataFrame({
            'country_name': ['China', 'United States', 'Japan', 'Germany', 'South Korea'],
            'unique_families': np.random.randint(50, 500, 5)
        }),
        'temporal_data': pd.DataFrame({
            'filing_year': list(range(2010, 2024)) * 5,
            'patent_count': np.random.randint(10, 100, 70)
        })
    }
    
    # Create dashboard
    creator = create_dashboard_creator()
    
    executive_dashboard = creator.create_executive_dashboard(
        sample_data,
        title="REE Patent Intelligence - Demo Dashboard"
    )
    
    logger.info("✅ Demo dashboard created successfully")
    
    return executive_dashboard

if __name__ == "__main__":
    demo_dashboard_creation()