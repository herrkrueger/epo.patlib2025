"""
Market Visualization Examples - Code Templates
Enhanced dashboards combining patent and market data
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List

class MarketPatentDashboard:
    """
    Enhanced visualization templates combining patent analytics with market intelligence
    Professional-grade dashboards for executive presentations
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'accent': '#2ca02c',
            'warning': '#d62728',
            'neutral': '#7f7f7f'
        }
    
    def create_integrated_executive_dashboard(self, correlation_data: Dict, risk_data: Dict) -> go.Figure:
        """
        4-Panel Executive Dashboard: Patents + Market Intelligence
        Panel 1: Patent vs Price Trends | Panel 2: Supply Risk Matrix
        Panel 3: Geographic Innovation | Panel 4: Market Event Timeline
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Patent Filings vs REE Price Index',
                'Supply Risk vs Innovation Matrix', 
                'Geographic Innovation Distribution',
                'Market Event Impact Timeline'
            ],
            specs=[
                [{"secondary_y": True}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Panel 1: Patent vs Price correlation
        if 'correlation_data' in correlation_data:
            corr_df = pd.DataFrame(correlation_data['correlation_data'])
            
            # Patents trend
            fig.add_trace(
                go.Scatter(
                    x=corr_df['year'],
                    y=corr_df['patent_count'],
                    name='Patent Filings',
                    line=dict(color=self.color_palette['primary'], width=3),
                    yaxis='y1'
                ),
                row=1, col=1
            )
            
            # Price trend on secondary y-axis
            fig.add_trace(
                go.Scatter(
                    x=corr_df['year'],
                    y=corr_df['price_index'],
                    name='Price Index',
                    line=dict(color=self.color_palette['warning'], width=3),
                    yaxis='y2'
                ),
                row=1, col=1, secondary_y=True
            )
        
        # Panel 2: Supply Risk Matrix
        if 'supply_risk_analysis' in risk_data:
            risk_df = pd.DataFrame(risk_data['supply_risk_analysis'])
            
            fig.add_trace(
                go.Scatter(
                    x=risk_df['production_share_percent'],
                    y=risk_df['patent_share_percent'],
                    mode='markers+text',
                    text=risk_df['country'],
                    textposition='top center',
                    marker=dict(
                        size=risk_df['patent_count'] / 10,  # Size by patent count
                        color=[self._get_risk_color(risk) for risk in risk_df['risk_category']],
                        showscale=True,
                        colorscale='RdYlGn_r'
                    ),
                    name='Countries'
                ),
                row=1, col=2
            )
        
        # Panel 3: Geographic Innovation
        if 'supply_risk_analysis' in risk_data:
            top_countries = risk_df.nlargest(10, 'patent_count')
            
            fig.add_trace(
                go.Bar(
                    x=top_countries['country'],
                    y=top_countries['patent_count'],
                    marker_color=self.color_palette['accent'],
                    name='Patent Count'
                ),
                row=2, col=1
            )
        
        # Panel 4: Market Event Timeline
        if 'event_impacts' in correlation_data:
            events = correlation_data['event_impacts']
            years = [e['year'] for e in events]
            responses = [e['patent_response']['response_ratio'] for e in events]
            
            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=responses,
                    mode='markers+lines+text',
                    text=[e['event'].split()[0] for e in events],  # Abbreviated event names
                    textposition='top center',
                    marker=dict(size=12, color=self.color_palette['secondary']),
                    name='Event Impact'
                ),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="REE Patent & Market Intelligence Dashboard",
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # Axis labels
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_yaxes(title_text="Patent Count", row=1, col=1)
        fig.update_yaxes(title_text="Price Index", secondary_y=True, row=1, col=1)
        
        fig.update_xaxes(title_text="Production Share (%)", row=1, col=2)
        fig.update_yaxes(title_text="Patent Share (%)", row=1, col=2)
        
        fig.update_xaxes(title_text="Country", row=2, col=1)
        fig.update_yaxes(title_text="Patent Count", row=2, col=1)
        
        fig.update_xaxes(title_text="Event Year", row=2, col=2)
        fig.update_yaxes(title_text="Patent Response Ratio", row=2, col=2)
        
        return fig
    
    def create_price_shock_analysis_chart(self, shock_analysis: Dict) -> go.Figure:
        """
        Detailed price shock vs patent response analysis
        Shows innovation spikes following market disruptions
        """
        if not shock_analysis.get('shock_responses'):
            return go.Figure().add_annotation(text="No shock response data available")
        
        shock_df = pd.DataFrame(shock_analysis['shock_responses'])
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Price Shock Magnitude vs Patent Response', 'Patent Response Timeline'],
            specs=[[{"type": "scatter"}, {"type": "bar"}]]
        )
        
        # Shock magnitude vs response
        fig.add_trace(
            go.Scatter(
                x=shock_df['price_change_percent'],
                y=shock_df['patent_response_ratio'],
                mode='markers+text',
                text=shock_df['shock_year'],
                textposition='top center',
                marker=dict(
                    size=15,
                    color=[self.color_palette['warning'] if x > 0 else self.color_palette['accent'] 
                          for x in shock_df['price_change_percent']],
                    opacity=0.7
                ),
                name='Price Shocks'
            ),
            row=1, col=1
        )
        
        # Patent response timeline
        fig.add_trace(
            go.Bar(
                x=shock_df['shock_year'],
                y=shock_df['patent_response_ratio'],
                marker_color=[self._get_response_color(ratio) for ratio in shock_df['patent_response_ratio']],
                name='Response Ratio'
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title="Market Shock Impact on Patent Innovation",
            height=500,
            template='plotly_white'
        )
        
        fig.update_xaxes(title_text="Price Change (%)", row=1, col=1)
        fig.update_yaxes(title_text="Patent Response Ratio", row=1, col=1)
        
        fig.update_xaxes(title_text="Shock Year", row=1, col=2)
        fig.update_yaxes(title_text="Patent Response Ratio", row=1, col=2)
        
        return fig
    
    def create_supply_chain_risk_heatmap(self, risk_data: Dict) -> go.Figure:
        """
        Supply chain vulnerability heatmap
        Critical for strategic planning and risk assessment
        """
        if not risk_data.get('supply_risk_analysis'):
            return go.Figure().add_annotation(text="No supply risk data available")
        
        risk_df = pd.DataFrame(risk_data['supply_risk_analysis'])
        
        # Create risk matrix data
        countries = risk_df['country'].tolist()
        risk_categories = ['Production Concentration', 'Innovation Deficit', 'Supply Vulnerability']
        
        # Calculate risk scores
        risk_matrix = []
        for _, row in risk_df.iterrows():
            production_risk = min(row['production_share_percent'] / 20, 5)  # Normalize to 0-5
            innovation_risk = 5 - min(row['patent_share_percent'] / 10, 5)  # Inverse for deficit
            supply_risk = production_risk + innovation_risk  # Combined vulnerability
            
            risk_matrix.append([production_risk, innovation_risk, supply_risk])
        
        fig = go.Figure(data=go.Heatmap(
            z=risk_matrix,
            x=risk_categories,
            y=countries,
            colorscale='RdYlGn_r',
            hoverongaps=False,
            hovertemplate='Country: %{y}<br>Risk Type: %{x}<br>Risk Score: %{z:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="REE Supply Chain Risk Assessment Matrix",
            xaxis_title="Risk Category",
            yaxis_title="Country",
            height=max(400, len(countries) * 30),
            template='plotly_white'
        )
        
        return fig
    
    def create_cost_savings_demonstration(self) -> go.Figure:
        """
        ROI visualization: Commercial tools vs Open Source solution
        Critical for business case presentations
        """
        categories = ['Initial Setup', 'Annual License', 'Training', 'Maintenance', 'Total 3-Year']
        commercial_costs = [15000, 45000, 8000, 12000, 159000]  # EUR
        open_source_costs = [2000, 0, 1500, 1000, 4500]  # EUR
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Commercial Tools',
            x=categories,
            y=commercial_costs,
            marker_color=self.color_palette['warning'],
            text=[f'€{cost:,}' for cost in commercial_costs],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Open Source Solution',
            x=categories,
            y=open_source_costs,
            marker_color=self.color_palette['accent'],
            text=[f'€{cost:,}' for cost in open_source_costs],
            textposition='auto'
        ))
        
        # Add savings annotation
        total_savings = commercial_costs[-1] - open_source_costs[-1]
        savings_percent = (total_savings / commercial_costs[-1]) * 100
        
        fig.add_annotation(
            x=4, y=commercial_costs[-1] * 0.8,
            text=f"SAVINGS<br>€{total_savings:,}<br>({savings_percent:.0f}%)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=self.color_palette['accent'],
            font=dict(size=14, color=self.color_palette['accent'])
        )
        
        fig.update_layout(
            title="Cost Comparison: Commercial vs Open Source Patent Analytics",
            xaxis_title="Cost Category",
            yaxis_title="Cost (EUR)",
            barmode='group',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def _get_risk_color(self, risk_category: str) -> str:
        """Map risk categories to colors"""
        color_map = {
            'high_risk': self.color_palette['warning'],
            'medium_risk': self.color_palette['secondary'],
            'low_risk': self.color_palette['accent']
        }
        return color_map.get(risk_category, self.color_palette['neutral'])
    
    def _get_response_color(self, response_ratio: float) -> str:
        """Map response ratios to colors"""
        if response_ratio > 1.5:
            return self.color_palette['accent']  # Strong positive
        elif response_ratio > 1.1:
            return self.color_palette['secondary']  # Moderate positive
        elif response_ratio > 0.9:
            return self.color_palette['neutral']  # Stable
        else:
            return self.color_palette['warning']  # Decline

# Testing function
def test_market_visualizations():
    """Test market visualization functionality"""
    dashboard = MarketPatentDashboard()
    
    # Create sample data
    sample_correlation = {
        'correlation_data': [
            {'year': 2020, 'patent_count': 100, 'price_index': 200},
            {'year': 2021, 'patent_count': 150, 'price_index': 380},
            {'year': 2022, 'patent_count': 180, 'price_index': 420}
        ],
        'shock_responses': [
            {'shock_year': 2021, 'price_change_percent': 90, 'patent_response_ratio': 1.5}
        ],
        'event_impacts': [
            {'year': 2021, 'event': 'Market Recovery', 'patent_response': {'response_ratio': 1.3}}
        ]
    }
    
    sample_risk = {
        'supply_risk_analysis': [
            {'country': 'China', 'production_share_percent': 85, 'patent_share_percent': 45, 
             'patent_count': 500, 'risk_category': 'high_risk'},
            {'country': 'USA', 'production_share_percent': 15, 'patent_share_percent': 25, 
             'patent_count': 300, 'risk_category': 'medium_risk'}
        ]
    }
    
    # Test dashboard creation
    dashboard_fig = dashboard.create_integrated_executive_dashboard(sample_correlation, sample_risk)
    assert dashboard_fig, "Failed to create executive dashboard"
    print("✅ Executive dashboard created")
    
    # Test price shock chart
    shock_fig = dashboard.create_price_shock_analysis_chart(sample_correlation)
    assert shock_fig, "Failed to create price shock analysis"
    print("✅ Price shock analysis chart created")
    
    # Test risk heatmap
    risk_fig = dashboard.create_supply_chain_risk_heatmap(sample_risk)
    assert risk_fig, "Failed to create risk heatmap"
    print("✅ Supply chain risk heatmap created")
    
    # Test cost savings chart
    cost_fig = dashboard.create_cost_savings_demonstration()
    assert cost_fig, "Failed to create cost savings chart"
    print("✅ Cost savings demonstration created")
    
    print("🎯 All market visualization tests passed!")
    return True

if __name__ == "__main__":
    test_market_visualizations()