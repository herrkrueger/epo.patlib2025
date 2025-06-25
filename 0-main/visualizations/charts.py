"""
Charts Module for REE Patent Analysis Visualizations
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive chart creation capabilities for patent intelligence
with interactive Plotly visualizations and professional styling.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChartCreator:
    """
    Professional chart creation for patent intelligence with consistent styling.
    """
    
    # Professional color schemes
    COLOR_SCHEMES = {
        'primary': px.colors.qualitative.Set3,
        'sequential': px.colors.sequential.Viridis,
        'diverging': px.colors.diverging.RdYlBu_r,
        'ree_specific': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
        'geographic': px.colors.sequential.Blues,
        'technology': px.colors.qualitative.Pastel1
    }
    
    # Chart styling defaults
    DEFAULT_LAYOUT = {
        'height': 700,
        'font': {'family': 'Arial, sans-serif', 'size': 12},
        'title': {'font': {'size': 18, 'family': 'Arial Black'}},
        'margin': {'l': 80, 'r': 80, 't': 100, 'b': 80},
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white'
    }
    
    def __init__(self, theme: str = 'professional'):
        """
        Initialize chart creator with styling theme.
        
        Args:
            theme: Styling theme ('professional', 'colorful', 'minimal')
        """
        self.theme = theme
        self.chart_counter = 0
    
    def create_bubble_scatter(self, data: pd.DataFrame,
                            x_col: str, y_col: str, size_col: str,
                            color_col: Optional[str] = None,
                            text_col: Optional[str] = None,
                            title: str = "Bubble Scatter Analysis",
                            x_title: str = None, y_title: str = None,
                            size_max: int = 50,
                            color_scheme: str = 'primary') -> go.Figure:
        """
        Create professional bubble scatter plot for market intelligence.
        
        Args:
            data: DataFrame with chart data
            x_col: Column for x-axis values
            y_col: Column for y-axis values  
            size_col: Column for bubble sizes
            color_col: Column for color mapping (optional)
            text_col: Column for text labels (optional)
            title: Chart title
            x_title: X-axis title
            y_title: Y-axis title
            size_max: Maximum bubble size
            color_scheme: Color scheme to use
            
        Returns:
            Plotly figure object
        """
        logger.info(f"📊 Creating bubble scatter: {title}")
        
        # Data preparation
        chart_data = data.copy()
        
        # Handle text positioning - avoid Plotly range() error
        if text_col and y_col in chart_data.columns:
            # Create y-positions for text labels
            chart_data['text_y_pos'] = list(range(len(chart_data)))
        
        # Create figure
        fig = go.Figure()
        
        # Color mapping
        if color_col and color_col in chart_data.columns:
            colors = chart_data[color_col]
            colorscale = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES['primary'])
        else:
            colors = self.COLOR_SCHEMES['ree_specific'][0]
            colorscale = None
        
        # Add scatter trace
        fig.add_trace(go.Scatter(
            x=chart_data[x_col],
            y=chart_data.get('text_y_pos', chart_data[y_col]) if text_col else chart_data[y_col],
            mode='markers+text' if text_col else 'markers',
            marker=dict(
                size=chart_data[size_col],
                sizemode='diameter',
                sizeref=2. * max(chart_data[size_col]) / (size_max**2),
                sizemin=4,
                color=colors,
                colorscale=colorscale if colorscale else None,
                showscale=True if colorscale else False,
                opacity=0.7,
                line=dict(width=2, color='rgba(255,255,255,0.8)')
            ),
            text=chart_data[text_col].str[:25] if text_col else None,
            textposition='middle right' if text_col else None,
            textfont=dict(size=10, color='black'),
            hovertemplate=(
                f"<b>%{{text}}</b><br>" if text_col else "" +
                f"{x_title or x_col}: %{{x}}<br>" +
                f"{y_title or y_col}: %{{y}}<br>" +
                f"Size: %{{marker.size}}<br>" +
                (f"Color: %{{marker.color}}<br>" if color_col else "") +
                "<extra></extra>"
            ),
            name='Data Points'
        ))
        
        # Layout styling
        fig.update_layout(
            title=f"🎯 {title}",
            xaxis_title=x_title or x_col.replace('_', ' ').title(),
            yaxis_title=y_title or y_col.replace('_', ' ').title(),
            **self.DEFAULT_LAYOUT
        )
        
        return fig
    
    def create_ranking_bar(self, data: pd.DataFrame,
                          category_col: str, value_col: str,
                          orientation: str = 'h',
                          title: str = "Ranking Analysis",
                          top_n: int = 20,
                          color_scheme: str = 'sequential') -> go.Figure:
        """
        Create professional ranking bar chart.
        
        Args:
            data: DataFrame with ranking data
            category_col: Column with categories to rank
            value_col: Column with values for ranking
            orientation: Chart orientation ('h' for horizontal, 'v' for vertical)
            title: Chart title
            top_n: Number of top items to show
            color_scheme: Color scheme to use
            
        Returns:
            Plotly figure object
        """
        logger.info(f"📊 Creating ranking bar chart: {title}")
        
        # Data preparation
        chart_data = data.sort_values(value_col, ascending=False).head(top_n).copy()
        
        if orientation == 'h':
            # Reverse order for horizontal bars (top at top)
            chart_data = chart_data.iloc[::-1]
        
        # Color mapping
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES['sequential'])
        color_values = chart_data[value_col]
        
        # Create figure
        fig = go.Figure()
        
        if orientation == 'h':
            fig.add_trace(go.Bar(
                x=chart_data[value_col],
                y=chart_data[category_col],
                orientation='h',
                marker=dict(
                    color=color_values,
                    colorscale=colors,
                    showscale=True,
                    colorbar=dict(title=value_col.replace('_', ' ').title())
                ),
                text=chart_data[value_col],
                textposition='outside',
                texttemplate='%{text}',
                hovertemplate=(
                    "<b>%{y}</b><br>" +
                    f"{value_col.replace('_', ' ').title()}: %{{x}}<br>" +
                    "<extra></extra>"
                )
            ))
        else:
            fig.add_trace(go.Bar(
                x=chart_data[category_col],
                y=chart_data[value_col],
                marker=dict(
                    color=color_values,
                    colorscale=colors,
                    showscale=True,
                    colorbar=dict(title=value_col.replace('_', ' ').title())
                ),
                text=chart_data[value_col],
                textposition='outside',
                texttemplate='%{text}',
                hovertemplate=(
                    "<b>%{x}</b><br>" +
                    f"{value_col.replace('_', ' ').title()}: %{{y}}<br>" +
                    "<extra></extra>"
                )
            ))
        
        # Layout styling
        fig.update_layout(
            title=f"🏆 {title}",
            xaxis_title=value_col.replace('_', ' ').title() if orientation == 'h' else category_col.replace('_', ' ').title(),
            yaxis_title=category_col.replace('_', ' ').title() if orientation == 'h' else value_col.replace('_', ' ').title(),
            showlegend=False,
            **self.DEFAULT_LAYOUT
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
        logger.info(f"📊 Creating market share pie: {title}")
        
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
            **self.DEFAULT_LAYOUT
        )
        
        return fig
    
    def create_time_series(self, data: pd.DataFrame,
                          time_col: str, value_col: str,
                          category_col: Optional[str] = None,
                          title: str = "Time Series Analysis",
                          trend_line: bool = True,
                          color_scheme: str = 'primary') -> go.Figure:
        """
        Create professional time series chart with trend analysis.
        
        Args:
            data: DataFrame with time series data
            time_col: Column with time/date values
            value_col: Column with values to plot
            category_col: Column for multiple series (optional)
            title: Chart title
            trend_line: Whether to add trend line
            color_scheme: Color scheme to use
            
        Returns:
            Plotly figure object
        """
        logger.info(f"📊 Creating time series: {title}")
        
        # Data preparation
        chart_data = data.copy()
        chart_data[time_col] = pd.to_datetime(chart_data[time_col])
        chart_data = chart_data.sort_values(time_col)
        
        # Create figure
        fig = go.Figure()
        
        colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES['primary'])
        
        if category_col and category_col in chart_data.columns:
            # Multiple series
            for i, category in enumerate(chart_data[category_col].unique()):
                category_data = chart_data[chart_data[category_col] == category]
                
                fig.add_trace(go.Scatter(
                    x=category_data[time_col],
                    y=category_data[value_col],
                    mode='lines+markers',
                    name=str(category)[:30],
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=(
                        f"<b>{category}</b><br>" +
                        "Date: %{x}<br>" +
                        f"{value_col.replace('_', ' ').title()}: %{{y}}<br>" +
                        "<extra></extra>"
                    )
                ))
        else:
            # Single series
            fig.add_trace(go.Scatter(
                x=chart_data[time_col],
                y=chart_data[value_col],
                mode='lines+markers',
                name=value_col.replace('_', ' ').title(),
                line=dict(color=colors[0], width=4),
                marker=dict(size=8, color=colors[1]),
                hovertemplate=(
                    "Date: %{x}<br>" +
                    f"{value_col.replace('_', ' ').title()}: %{{y}}<br>" +
                    "<extra></extra>"
                )
            ))
            
            # Add trend line if requested
            if trend_line and len(chart_data) > 2:
                from scipy import stats
                x_numeric = pd.to_numeric(chart_data[time_col])
                slope, intercept, r_value, _, _ = stats.linregress(x_numeric, chart_data[value_col])
                
                trend_y = slope * x_numeric + intercept
                
                fig.add_trace(go.Scatter(
                    x=chart_data[time_col],
                    y=trend_y,
                    mode='lines',
                    name=f'Trend (R²={r_value**2:.3f})',
                    line=dict(dash='dash', color='red', width=2),
                    hovertemplate="Trend Line<extra></extra>"
                ))
        
        # Layout styling
        fig.update_layout(
            title=f"📈 {title}",
            xaxis_title="Time Period",
            yaxis_title=value_col.replace('_', ' ').title(),
            hovermode='x unified',
            **self.DEFAULT_LAYOUT
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
        logger.info(f"📊 Creating correlation heatmap: {title}")
        
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
            **self.DEFAULT_LAYOUT
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
        logger.info(f"📊 Creating distribution histogram: {title}")
        
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
            **self.DEFAULT_LAYOUT
        )
        
        return fig

def create_chart_creator(theme: str = 'professional') -> ChartCreator:
    """
    Factory function to create configured chart creator.
    
    Args:
        theme: Styling theme for charts
        
    Returns:
        Configured ChartCreator instance
    """
    return ChartCreator(theme)

# Convenience functions for quick chart creation
def quick_scatter(data: pd.DataFrame, x: str, y: str, size: str, **kwargs) -> go.Figure:
    """Quick bubble scatter chart creation."""
    creator = create_chart_creator()
    return creator.create_bubble_scatter(data, x, y, size, **kwargs)

def quick_bar(data: pd.DataFrame, category: str, value: str, **kwargs) -> go.Figure:
    """Quick ranking bar chart creation."""
    creator = create_chart_creator()
    return creator.create_ranking_bar(data, category, value, **kwargs)

def quick_pie(data: pd.DataFrame, category: str, value: str, **kwargs) -> go.Figure:
    """Quick market share pie chart creation."""
    creator = create_chart_creator()
    return creator.create_market_share_pie(data, category, value, **kwargs)

def quick_timeseries(data: pd.DataFrame, time: str, value: str, **kwargs) -> go.Figure:
    """Quick time series chart creation."""
    creator = create_chart_creator()
    return creator.create_time_series(data, time, value, **kwargs)

# Example usage and demo functions
def demo_chart_creation():
    """Demonstrate chart creation capabilities."""
    logger.info("🚀 Chart Creation Demo")
    
    # Create sample data
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'applicant': [f'Company_{i}' for i in range(1, 21)],
        'patent_families': np.random.randint(5, 100, 20),
        'market_share': np.random.uniform(1, 15, 20),
        'filing_year': np.random.randint(2010, 2023, 20),
        'technology_area': np.random.choice(['Materials', 'Electronics', 'Energy'], 20)
    })
    
    # Create charts
    creator = create_chart_creator()
    
    # Bubble scatter
    bubble_fig = creator.create_bubble_scatter(
        sample_data, 'patent_families', 'market_share', 'patent_families',
        color_col='market_share', text_col='applicant',
        title="Patent Leaders Market Analysis"
    )
    
    # Ranking bar
    bar_fig = creator.create_ranking_bar(
        sample_data, 'applicant', 'patent_families',
        title="Top Patent Applicants"
    )
    
    # Market share pie
    pie_fig = creator.create_market_share_pie(
        sample_data, 'applicant', 'market_share',
        title="Market Share Distribution"
    )
    
    logger.info("✅ Demo charts created successfully")
    
    return bubble_fig, bar_fig, pie_fig

if __name__ == "__main__":
    demo_chart_creation()