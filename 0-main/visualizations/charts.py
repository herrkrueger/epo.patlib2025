"""
Charts Module for Production Patent Analysis Visualizations
Integrated with production config, processors, and data access layers

This module provides comprehensive chart creation capabilities for patent intelligence
with interactive Plotly visualizations, professional styling, and seamless integration
with the production-ready patent analysis platform.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Union, Any
import logging
from datetime import datetime
from pathlib import Path

# Production imports
from config import ConfigurationManager
from data_access.country_mapper import PatentCountryMapper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionChartCreator:
    """
    Production-ready chart creation for patent intelligence with configuration-driven styling.
    Integrates seamlessly with the production patent analysis platform.
    """
    
    def __init__(self, config_manager: ConfigurationManager = None, theme: str = None):
        """
        Initialize production chart creator with configuration management.
        
        Args:
            config_manager: Configuration manager instance
            theme: Override theme from configuration
        """
        self.config = config_manager or ConfigurationManager()
        self.theme = theme or self.config.get_visualization_config('general.themes.default_theme')
        self.chart_counter = 0
        self.country_mapper = PatentCountryMapper()
        
        # Load configuration-driven settings
        self._load_styling_config()
    
    def _load_styling_config(self):
        """Load styling configuration from YAML files."""
        viz_config = self.config.get_visualization_config()
        
        # Color schemes from configuration
        self.color_schemes = {
            'primary': viz_config.get('charts', {}).get('color_schemes', {}).get('patent_analysis', 
                                    ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']),
            'qualitative': viz_config.get('charts', {}).get('color_schemes', {}).get('qualitative_professional',
                                         ['#2E8B57', '#4169E1', '#FF6347', '#32CD32', '#FF69B4']),
            'sequential': viz_config.get('charts', {}).get('color_schemes', {}).get('sequential', {}),
            'diverging': viz_config.get('charts', {}).get('color_schemes', {}).get('diverging', {})
        }
        
        # Layout configuration
        layout_config = viz_config.get('charts', {}).get('layout', {})
        self.default_layout = {
            'height': layout_config.get('default_height', 600),
            'width': layout_config.get('default_width', 800),
            'font': {
                'family': layout_config.get('font_family', 'Arial, sans-serif'),
                'size': layout_config.get('font_size', 12)
            },
            'title': {
                'font': {
                    'size': layout_config.get('title_font_size', 18),
                    'family': layout_config.get('title_font_family', 'Arial Black')
                }
            },
            'margin': {
                'l': layout_config.get('margin_left', 80),
                'r': layout_config.get('margin_right', 80),
                't': layout_config.get('margin_top', 100),
                'b': layout_config.get('margin_bottom', 80)
            },
            'plot_bgcolor': layout_config.get('plot_bgcolor', 'white'),
            'paper_bgcolor': layout_config.get('paper_bgcolor', '#f8f9fa')
        }
        
        # Chart-specific configurations
        self.scatter_config = viz_config.get('charts', {}).get('scatter_plots', {})
        self.bar_config = viz_config.get('charts', {}).get('bar_charts', {})
        self.pie_config = viz_config.get('charts', {}).get('pie_charts', {})
        self.timeseries_config = viz_config.get('charts', {}).get('time_series', {})
        self.heatmap_config = viz_config.get('charts', {}).get('heatmaps', {})
    
    def _create_empty_figure(self, message: str = "No data available") -> go.Figure:
        """Create empty figure with informative message."""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(**self.default_layout)
        return fig
    
    def create_applicant_bubble_scatter(self, processor_results: Dict[str, Any],
                                      title: str = "Patent Leaders Market Analysis",
                                      max_points: int = 20) -> go.Figure:
        """
        Create professional applicant bubble scatter plot using processor results.
        
        Args:
            processor_results: Results from ApplicantProcessor.export_results_for_visualization()
            title: Chart title
            max_points: Maximum number of applicants to display
            
        Returns:
            Plotly figure object with applicant analysis
        """
        logger.debug(f"📊 Creating applicant bubble scatter: {title}")
        
        # Extract data from processor results
        if 'applicant_ranking' not in processor_results:
            logger.warning("No applicant ranking data found in processor results")
            return self._create_empty_figure("No applicant data available")
        
        data = processor_results['applicant_ranking'].head(max_points).copy()
        
        # Get bubble scatter configuration
        bubble_config = self.scatter_config.get('bubble_scatter', {})
        
        # Handle text positioning - avoid Plotly range() error
        data['text_y_pos'] = list(range(len(data)))
        
        # Create figure
        fig = go.Figure()
        
        # Use configured color scheme
        colors = data.get('Market_Share_Pct', data.iloc[:, 1])
        colorscale = self.color_schemes['sequential'].get('market_share', 'Reds')
        
        # Add scatter trace with production configuration
        size_col = 'Patent_Families' if 'Patent_Families' in data.columns else data.columns[1]
        patent_families = data[size_col]
        
        fig.add_trace(go.Scatter(
            x=patent_families,
            y=data['text_y_pos'],
            mode='markers+text',
            marker=dict(
                size=patent_families,
                sizemode='diameter',
                sizeref=bubble_config.get('size_reference_factor', 2.0) * max(patent_families) / (bubble_config.get('max_bubble_size', 50)**2),
                sizemin=bubble_config.get('min_bubble_size', 8),
                color=colors,
                colorscale=colorscale,
                showscale=True,
                opacity=bubble_config.get('opacity', 0.7),
                line=dict(
                    width=bubble_config.get('line_width', 2), 
                    color=bubble_config.get('line_color', 'rgba(255,255,255,0.8)')
                ),
                colorbar=dict(title="Market Share %", x=1.02)
            ),
            text=data.iloc[:, 0].str[:25],  # Applicant names
            textposition=bubble_config.get('text_position', 'middle right'),
            textfont=dict(
                size=bubble_config.get('text_font_size', 10), 
                color='black'
            ),
            hovertemplate=(
                "<b>%{text}</b><br>" +
                "Patent Families: %{x}<br>" +
                "Market Position: %{y}<br>" +
                "Market Share: %{marker.color:.1f}%<br>" +
                "<extra></extra>"
            ),
            name='Patent Leaders'
        ))
        
        # Layout styling with configuration
        branding = self.config.get('visualization', 'general.branding', {})
        title_prefix = branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            xaxis_title="Patent Families",
            yaxis_title="Market Position Ranking",
            annotations=[
                dict(
                    text=branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ],
            **self.default_layout
        )
        
        return fig
    
    def create_geographic_bar_ranking(self, processor_results: Dict[str, Any],
                                     title: str = "Geographic Patent Distribution",
                                     top_n: int = 15,
                                     orientation: str = 'h') -> go.Figure:
        """
        Create professional geographic ranking bar chart using processor results.
        
        Args:
            processor_results: Results from GeographicProcessor.export_results_for_visualization()
            title: Chart title
            top_n: Number of top countries to show
            orientation: Chart orientation ('h' for horizontal, 'v' for vertical)
            
        Returns:
            Plotly figure object with geographic analysis
        """
        logger.debug(f"📊 Creating geographic bar ranking: {title}")
        
        # Extract data from processor results
        if 'country_summary' not in processor_results:
            logger.warning("No country summary data found in processor results")
            return self._create_empty_figure("No geographic data available")
        
        data = processor_results['country_summary']
        
        # Use country mapper for proper country names
        if 'country_code' in data.columns:
            data = self.country_mapper.enhance_country_data(data, 'country_code')
        
        # Prepare chart data
        value_col = 'unique_families' if 'unique_families' in data.columns else data.columns[-1]
        country_col = 'country_name' if 'country_name' in data.columns else data.columns[0]
        
        chart_data = data.sort_values(value_col, ascending=False).head(top_n).copy()
        
        if orientation == 'h':
            # Reverse order for horizontal bars (top at top)
            chart_data = chart_data.iloc[::-1]
        
        # Get bar chart configuration
        bar_config = self.bar_config.get('horizontal_bars' if orientation == 'h' else 'vertical_bars', {})
        
        # Color mapping from configuration
        colorscale = self.color_schemes['sequential'].get('patent_activity', 'Blues')
        color_values = chart_data[value_col]
        
        # Create figure with configuration
        fig = go.Figure()
        
        if orientation == 'h':
            fig.add_trace(go.Bar(
                x=chart_data[value_col],
                y=chart_data[country_col],
                orientation=bar_config.get('orientation', 'h'),
                marker=dict(
                    color=color_values,
                    colorscale=colorscale,
                    showscale=True,
                    opacity=bar_config.get('bar_opacity', 0.8),
                    line=dict(
                        width=bar_config.get('border_width', 1),
                        color=bar_config.get('border_color', 'white')
                    ),
                    colorbar=dict(title=value_col.replace('_', ' ').title())
                ),
                text=chart_data[value_col] if bar_config.get('show_values', True) else None,
                textposition=bar_config.get('text_position', 'outside'),
                texttemplate=bar_config.get('text_template', '%{x}'),
                hovertemplate=(
                    "<b>%{y}</b><br>" +
                    f"{value_col.replace('_', ' ').title()}: %{{x}}<br>" +
                    "<extra></extra>"
                )
            ))
        else:
            fig.add_trace(go.Bar(
                x=chart_data[country_col],
                y=chart_data[value_col],
                marker=dict(
                    color=color_values,
                    colorscale=colorscale,
                    showscale=True,
                    opacity=bar_config.get('bar_opacity', 0.8),
                    colorbar=dict(title=value_col.replace('_', ' ').title())
                ),
                text=chart_data[value_col] if bar_config.get('show_values', True) else None,
                textposition=bar_config.get('text_position', 'outside'),
                texttemplate=bar_config.get('text_template', '%{y}'),
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    f"{value_col.replace('_', ' ').title()}: %{{y}}<br>" +
                    "<extra></extra>"
                )
            ))
        
        # Layout styling with configuration
        branding = self.config.get('visualization', 'general.branding', {})
        title_prefix = branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            xaxis_title=value_col.replace('_', ' ').title() if orientation == 'h' else "Countries",
            yaxis_title="Countries" if orientation == 'h' else value_col.replace('_', ' ').title(),
            showlegend=False,
            annotations=[
                dict(
                    text=branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ],
            **self.default_layout
        )
        
        return fig
    
    def create_market_share_pie(self, data: pd.DataFrame,
                               category_col: str, value_col: str,
                               title: str = "Market Share Analysis",
                               top_n: int = 10,
                               show_others: bool = True) -> go.Figure:
        """
        Create professional market share pie chart with top N + others pattern.
        
        Args:
            data: DataFrame with market share data
            category_col: Column with categories
            value_col: Column with values
            title: Chart title
            top_n: Number of top categories to show individually
            show_others: Whether to group remaining as "Others"
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"📊 Creating market share pie: {title}")
        
        # Data preparation
        sorted_data = data.sort_values(value_col, ascending=False)
        
        if show_others and len(sorted_data) > top_n:
            top_data = sorted_data.head(top_n)
            others_value = sorted_data.tail(len(sorted_data) - top_n)[value_col].sum()
            
            # Create pie data with top N + others
            pie_values = list(top_data[value_col]) + [others_value]
            pie_labels = list(top_data[category_col].str[:20]) + ['Others']
        else:
            pie_values = list(sorted_data[value_col])
            pie_labels = list(sorted_data[category_col].str[:20])
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            values=pie_values,
            labels=pie_labels,
            hole=0.3,  # Donut style
            textinfo='label+percent',
            textposition='auto',
            textfont=dict(size=11),
            marker=dict(
                colors=self.COLOR_SCHEMES['primary'][:len(pie_values)],
                line=dict(color='white', width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>" +
                "Value: %{value}<br>" +
                "Percentage: %{percent}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Layout styling
        fig.update_layout(
            title=f"📈 {title}",
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            **self.default_layout
        )
        
        return fig
    
    def create_temporal_trends_chart(self, processor_results: Dict[str, Any],
                                    title: str = "Patent Filing Trends Over Time",
                                    show_trend_line: bool = True,
                                    show_market_events: bool = True) -> go.Figure:
        """
        Create professional temporal trends chart using processor results.
        
        Args:
            processor_results: Results from any processor with temporal analysis
            title: Chart title
            show_trend_line: Whether to add trend line
            show_market_events: Whether to add market event annotations
            
        Returns:
            Plotly figure object with temporal analysis
        """
        logger.debug(f"📊 Creating temporal trends chart: {title}")
        
        # Extract temporal data from processor results
        temporal_data = None
        if 'temporal_summary' in processor_results:
            temporal_data = processor_results['temporal_summary']
        elif 'annual_activity' in processor_results:
            temporal_data = processor_results['annual_activity']
        
        if temporal_data is None or len(temporal_data) == 0:
            logger.warning("No temporal data found in processor results")
            return self._create_empty_figure("No temporal data available")
        
        # Data preparation
        chart_data = temporal_data.copy()
        time_col = 'filing_year' if 'filing_year' in chart_data.columns else chart_data.columns[0]
        value_col = 'patent_count' if 'patent_count' in chart_data.columns else chart_data.columns[1]
        
        chart_data[time_col] = pd.to_datetime(chart_data[time_col], format='%Y')
        chart_data = chart_data.sort_values(time_col)
        
        # Create figure
        fig = go.Figure()
        
        # Get time series configuration
        line_config = self.timeseries_config.get('line_charts', {})
        colors = self.color_schemes['primary']
        
        # Single series temporal chart
        fig.add_trace(go.Scatter(
            x=chart_data[time_col],
            y=chart_data[value_col],
            mode=line_config.get('mode', 'lines+markers'),
            name=value_col.replace('_', ' ').title(),
            line=dict(
                color=colors[0], 
                width=line_config.get('line_width', 3)
            ),
            marker=dict(
                size=line_config.get('marker_size', 8), 
                color=colors[1]
            ),
            hovertemplate=(
                "Year: %{x|%Y}<br>" +
                f"{value_col.replace('_', ' ').title()}: %{{y}}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Add trend line if requested
        if show_trend_line and line_config.get('show_trend', True) and len(chart_data) > 2:
            try:
                from scipy import stats
                x_numeric = pd.to_numeric(chart_data[time_col])
                slope, intercept, r_value, _, _ = stats.linregress(x_numeric, chart_data[value_col])
                
                trend_y = slope * x_numeric + intercept
                
                fig.add_trace(go.Scatter(
                    x=chart_data[time_col],
                    y=trend_y,
                    mode='lines',
                    name=f'Trend (R²={r_value**2:.3f})',
                    line=dict(
                        dash='dash', 
                        color='red', 
                        width=2
                    ),
                    hovertemplate="Trend Line<extra></extra>"
                ))
            except ImportError:
                logger.warning("Scipy not available for trend line calculation")
        
        # Add market events annotations if requested
        if show_market_events:
            market_events = {
                2010: "Technology Crisis", 2011: "Market Peak", 2014: "Stabilization",
                2017: "Innovation Boom", 2020: "COVID Impact", 2022: "Supply Chain Issues"
            }
            
            for year, event in market_events.items():
                if year in chart_data[time_col].dt.year.values:
                    year_data = chart_data[chart_data[time_col].dt.year == year]
                    if len(year_data) > 0:
                        fig.add_annotation(
                            x=year_data[time_col].iloc[0],
                            y=year_data[value_col].iloc[0],
                            text=event,
                            showarrow=True,
                            arrowhead=2,
                            arrowcolor="gray",
                            font=dict(size=9, color="gray")
                        )
        
        # Layout styling with configuration
        branding = self.config.get('visualization', 'general.branding', {})
        title_prefix = branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            xaxis_title="Year",
            yaxis_title=value_col.replace('_', ' ').title(),
            hovermode='x unified',
            annotations=fig.layout.annotations + (
                dict(
                    text=branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                ),
            ),
            **self.default_layout
        )
        
        return fig
    
    def create_technology_distribution_pie(self, processor_results: Dict[str, Any],
                                         title: str = "Technology Distribution Analysis",
                                         max_categories: int = 10) -> go.Figure:
        """
        Create professional technology distribution pie chart using processor results.
        
        Args:
            processor_results: Results from ClassificationProcessor.export_results_for_visualization()
            title: Chart title
            max_categories: Maximum number of categories to show individually
            
        Returns:
            Plotly figure object with technology distribution
        """
        logger.debug(f"📊 Creating technology distribution pie: {title}")
        
        # Extract data from processor results
        if 'cpc_distribution' not in processor_results:
            logger.warning("No CPC distribution data found in processor results")
            return self._create_empty_figure("No technology distribution data available")
        
        data = processor_results['cpc_distribution']
        
        # Get pie chart configuration
        pie_config = self.pie_config.get('market_share', {})
        
        # Prepare data for pie chart
        sorted_data = data.sort_values(data.columns[1], ascending=False)
        
        if pie_config.get('max_categories', 10) and len(sorted_data) > max_categories:
            top_data = sorted_data.head(max_categories)
            others_value = sorted_data.tail(len(sorted_data) - max_categories).iloc[:, 1].sum()
            
            # Create pie data with top N + others
            pie_values = list(top_data.iloc[:, 1]) + [others_value]
            pie_labels = list(top_data.iloc[:, 0].str[:25]) + ['Others']
        else:
            pie_values = list(sorted_data.iloc[:, 1])
            pie_labels = list(sorted_data.iloc[:, 0].str[:25])
        
        # Create figure
        fig = go.Figure()
        
        fig.add_trace(go.Pie(
            values=pie_values,
            labels=pie_labels,
            hole=pie_config.get('hole_size', 0.3),
            textinfo=pie_config.get('text_info', 'label+percent'),
            textposition=pie_config.get('text_position', 'auto'),
            textfont=dict(size=11),
            marker=dict(
                colors=self.color_schemes['primary'][:len(pie_values)],
                line=dict(color='white', width=2)
            ),
            hovertemplate=(
                "<b>%{label}</b><br>" +
                "Count: %{value}<br>" +
                "Percentage: %{percent}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Layout styling with configuration
        branding = self.config.get('visualization', 'general.branding', {})
        title_prefix = branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            showlegend=pie_config.get('show_legend', True),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            annotations=[
                dict(
                    text=branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ],
            **self.default_layout
        )
        
        return fig
    
    def create_citation_network_heatmap(self, processor_results: Dict[str, Any],
                                      title: str = "Citation Network Analysis",
                                      max_entities: int = 20) -> go.Figure:
        """
        Create professional citation network heatmap using processor results.
        
        Args:
            processor_results: Results from CitationProcessor.export_results_for_visualization()
            title: Chart title
            max_entities: Maximum number of entities to include in heatmap
            
        Returns:
            Plotly figure object with citation network analysis
        """
        logger.debug(f"📊 Creating citation network heatmap: {title}")
        
        # Extract data from processor results
        if 'citation_matrix' not in processor_results:
            logger.warning("No citation matrix data found in processor results")
            return self._create_empty_figure("No citation network data available")
        
        citation_matrix = processor_results['citation_matrix']
        
        # Limit size for readability
        if len(citation_matrix) > max_entities:
            citation_matrix = citation_matrix.iloc[:max_entities, :max_entities]
        
        # Get heatmap configuration
        heatmap_config = self.heatmap_config.get('correlation', {})
        
        # Create figure
        fig = go.Figure()
        
        # Create heatmap
        fig.add_trace(go.Heatmap(
            z=citation_matrix.values,
            x=citation_matrix.columns,
            y=citation_matrix.index,
            colorscale=heatmap_config.get('color_scale', 'Blues'),
            text=citation_matrix.values if heatmap_config.get('show_annotations', True) else None,
            texttemplate='%{text}' if heatmap_config.get('show_annotations', True) else None,
            textfont=dict(size=heatmap_config.get('annotation_font_size', 10)),
            hovertemplate=(
                "Citing: %{y}<br>" +
                "Cited: %{x}<br>" +
                "Citations: %{z}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Layout styling with configuration
        branding = self.config.get('visualization', 'general.branding', {})
        title_prefix = branding.get('title_prefix', '🎯 ')
        
        fig.update_layout(
            title=f"{title_prefix}{title}",
            xaxis_title="Cited Entities",
            yaxis_title="Citing Entities",
            annotations=[
                dict(
                    text=branding.get('watermark', 'Generated with Claude Code'),
                    xref="paper", yref="paper",
                    x=1.0, y=0.0, xanchor='right', yanchor='bottom',
                    showarrow=False, font=dict(size=8, color='gray')
                )
            ],
            **self.default_layout
        )
        
        return fig
    
    def create_correlation_heatmap(self, data: pd.DataFrame,
                                  columns: List[str] = None,
                                  title: str = "Correlation Analysis",
                                  annotate: bool = True) -> go.Figure:
        """
        Create professional correlation heatmap.
        
        Args:
            data: DataFrame with numeric data
            columns: Columns to include in correlation (optional)
            title: Chart title
            annotate: Whether to show correlation values
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"📊 Creating correlation heatmap: {title}")
        
        # Data preparation
        if columns:
            correlation_data = data[columns]
        else:
            correlation_data = data.select_dtypes(include=[np.number])
        
        corr_matrix = correlation_data.corr()
        
        # Create figure
        fig = go.Figure()
        
        # Create heatmap
        fig.add_trace(go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.round(2).values if annotate else None,
            texttemplate='%{text}' if annotate else None,
            textfont=dict(size=10),
            hovertemplate=(
                "X: %{x}<br>" +
                "Y: %{y}<br>" +
                "Correlation: %{z:.3f}<br>" +
                "<extra></extra>"
            )
        ))
        
        # Layout styling
        fig.update_layout(
            title=f"🔗 {title}",
            xaxis_title="Variables",
            yaxis_title="Variables",
            **self.default_layout
        )
        
        return fig
    
    def create_distribution_histogram(self, data: pd.DataFrame,
                                    value_col: str,
                                    category_col: Optional[str] = None,
                                    title: str = "Distribution Analysis",
                                    bins: int = 30,
                                    show_stats: bool = True) -> go.Figure:
        """
        Create professional distribution histogram with statistics.
        
        Args:
            data: DataFrame with distribution data
            value_col: Column with values to analyze
            category_col: Column for grouped histograms (optional)
            title: Chart title
            bins: Number of histogram bins
            show_stats: Whether to show statistical annotations
            
        Returns:
            Plotly figure object
        """
        logger.debug(f"📊 Creating distribution histogram: {title}")
        
        # Create figure
        fig = go.Figure()
        
        colors = self.COLOR_SCHEMES['primary']
        
        if category_col and category_col in data.columns:
            # Multiple distributions
            for i, category in enumerate(data[category_col].unique()):
                category_data = data[data[category_col] == category][value_col]
                
                fig.add_trace(go.Histogram(
                    x=category_data,
                    name=str(category)[:30],
                    nbinsx=bins,
                    opacity=0.7,
                    marker_color=colors[i % len(colors)],
                    hovertemplate=(
                        f"<b>{category}</b><br>" +
                        "Range: %{x}<br>" +
                        "Count: %{y}<br>" +
                        "<extra></extra>"
                    )
                ))
        else:
            # Single distribution
            fig.add_trace(go.Histogram(
                x=data[value_col],
                nbinsx=bins,
                marker_color=colors[0],
                opacity=0.8,
                hovertemplate=(
                    "Range: %{x}<br>" +
                    "Count: %{y}<br>" +
                    "<extra></extra>"
                )
            ))
            
            # Add statistical annotations if requested
            if show_stats:
                mean_val = data[value_col].mean()
                median_val = data[value_col].median()
                std_val = data[value_col].std()
                
                # Add vertical lines for mean and median
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                             annotation_text=f"Mean: {mean_val:.2f}")
                fig.add_vline(x=median_val, line_dash="dot", line_color="blue",
                             annotation_text=f"Median: {median_val:.2f}")
        
        # Layout styling
        fig.update_layout(
            title=f"📊 {title}",
            xaxis_title=value_col.replace('_', ' ').title(),
            yaxis_title="Frequency",
            barmode='overlay',
            **self.default_layout
        )
        
        return fig

def create_production_chart_creator(config_manager: ConfigurationManager = None, theme: str = None) -> ProductionChartCreator:
    """
    Factory function to create configured production chart creator.
    
    Args:
        config_manager: Configuration manager instance
        theme: Styling theme override
        
    Returns:
        Configured ProductionChartCreator instance
    """
    return ProductionChartCreator(config_manager, theme)

def create_chart_creator(theme: str = 'professional') -> ProductionChartCreator:
    """
    Legacy factory function for backward compatibility.
    
    Args:
        theme: Styling theme for charts
        
    Returns:
        Configured ProductionChartCreator instance
    """
    return create_production_chart_creator(theme=theme)

# Production convenience functions for processor integration
def create_applicant_chart(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create applicant analysis chart from processor results."""
    creator = create_production_chart_creator()
    return creator.create_applicant_bubble_scatter(processor_results, **kwargs)

def create_geographic_chart(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create geographic analysis chart from processor results."""
    creator = create_production_chart_creator()
    return creator.create_geographic_bar_ranking(processor_results, **kwargs)

def create_temporal_chart(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create temporal analysis chart from processor results."""
    creator = create_production_chart_creator()
    return creator.create_temporal_trends_chart(processor_results, **kwargs)

def create_technology_chart(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create technology distribution chart from processor results."""
    creator = create_production_chart_creator()
    return creator.create_technology_distribution_pie(processor_results, **kwargs)

def create_citation_chart(processor_results: Dict[str, Any], **kwargs) -> go.Figure:
    """Create citation network chart from processor results."""
    creator = create_production_chart_creator()
    return creator.create_citation_network_heatmap(processor_results, **kwargs)

# Legacy convenience functions for backward compatibility
def quick_scatter(data: pd.DataFrame, x: str, y: str, size: str, **kwargs) -> go.Figure:
    """Legacy function - use processor-based functions instead."""
    logger.warning("quick_scatter is deprecated - use processor-based chart functions")
    creator = create_chart_creator()
    return creator.create_applicant_bubble_scatter({'applicant_ranking': data}, **kwargs)

def quick_bar(data: pd.DataFrame, category: str, value: str, **kwargs) -> go.Figure:
    """Legacy function - use processor-based functions instead."""
    logger.warning("quick_bar is deprecated - use processor-based chart functions")
    creator = create_chart_creator()
    return creator.create_geographic_bar_ranking({'country_summary': data}, **kwargs)

def quick_pie(data: pd.DataFrame, category: str, value: str, **kwargs) -> go.Figure:
    """Legacy function - use processor-based functions instead."""
    logger.warning("quick_pie is deprecated - use processor-based chart functions")
    creator = create_chart_creator()
    return creator.create_technology_distribution_pie({'cpc_distribution': data}, **kwargs)

def quick_timeseries(data: pd.DataFrame, time: str, value: str, **kwargs) -> go.Figure:
    """Legacy function - use processor-based functions instead."""
    logger.warning("quick_timeseries is deprecated - use processor-based chart functions")
    creator = create_chart_creator()
    return creator.create_temporal_trends_chart({'temporal_summary': data}, **kwargs)

# Production integration example
def demo_production_chart_creation():
    """Demonstrate production chart creation with processor integration."""
    logger.debug("🚀 Production Chart Creation Demo")
    
    try:
        # Initialize production components
        config_manager = ConfigurationManager()
        creator = create_production_chart_creator(config_manager)
        
        # Create sample processor results structure
        np.random.seed(42)
        sample_results = {
            'applicant_ranking': pd.DataFrame({
                'Applicant': [f'Company_{i}' for i in range(1, 11)],
                'Patent_Families': np.random.randint(10, 100, 10),
                'Market_Share_Pct': np.random.uniform(2, 20, 10)
            }),
            'country_summary': pd.DataFrame({
                'country_name': ['China', 'United States', 'Japan', 'Germany', 'South Korea'],
                'unique_families': np.random.randint(50, 500, 5)
            }),
            'temporal_summary': pd.DataFrame({
                'filing_year': list(range(2010, 2024)),
                'patent_count': np.random.randint(20, 150, 14)
            }),
            'cpc_distribution': pd.DataFrame({
                'cpc_class': ['H01M', 'C22B', 'G06F', 'H01L', 'C09K'],
                'patent_count': np.random.randint(50, 200, 5)
            })
        }
        
        # Create production charts
        applicant_fig = creator.create_applicant_bubble_scatter(
            sample_results, title="Patent Leaders Market Analysis"
        )
        
        geographic_fig = creator.create_geographic_bar_ranking(
            sample_results, title="Global Patent Distribution"
        )
        
        temporal_fig = creator.create_temporal_trends_chart(
            sample_results, title="Patent Filing Trends"
        )
        
        technology_fig = creator.create_technology_distribution_pie(
            sample_results, title="Technology Distribution"
        )
        
        logger.debug("✅ Production demo charts created successfully")
        
        return applicant_fig, geographic_fig, temporal_fig, technology_fig
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        return None, None, None, None

if __name__ == "__main__":
    demo_production_chart_creation()