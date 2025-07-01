import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json

# Import all our modules
from integrated_market_pipeline import IntegratedMarketPipeline
from usgs_market_collector import USGSMineralDataCollector
from patent_market_correlator import PatentMarketCorrelator
from roi_calculator import ROICalculator

class EnhancedREEDashboard:
    """
    Enhanced REE Dashboard with Market Intelligence Overlay
    Upgrades existing visualization with comprehensive patent-market analysis
    Executive-ready business intelligence dashboards
    """
    
    def __init__(self):
        self.pipeline = IntegratedMarketPipeline()
        self.usgs_collector = USGSMineralDataCollector()
        self.roi_calculator = ROICalculator()
        
        # Color schemes for professional presentations
        self.color_schemes = {
            'patent_trends': '#1f77b4',
            'market_prices': '#ff7f0e', 
            'supply_risk': '#d62728',
            'business_value': '#2ca02c',
            'correlation': '#9467bd',
            'geographic': '#8c564b'
        }
        
    def create_integrated_executive_dashboard(self, integrated_results: Optional[Dict] = None) -> go.Figure:
        """
        Create comprehensive 4-panel executive dashboard
        Combines patent analytics with market intelligence overlay
        """
        print("📊 CREATING INTEGRATED EXECUTIVE DASHBOARD")
        print("-" * 45)
        
        # Get integrated results if not provided
        if not integrated_results:
            print("Running integrated analysis for dashboard...")
            integrated_results = self.pipeline.run_integrated_analysis(test_mode=True, generate_reports=False)
        
        if not integrated_results.get('pipeline_metadata', {}).get('execution_success', False):
            print("❌ Cannot create dashboard - pipeline failed")
            return self._create_error_dashboard("Pipeline execution failed")
        
        # Extract data components
        patent_data = integrated_results['patent_analytics']['ree_dataset']
        correlation_data = integrated_results['correlation_analysis']
        market_data = integrated_results['market_intelligence']['market_data']
        
        # Create 2x2 subplot layout
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📈 Patent Filing Trends vs REE Price Volatility',
                '🌍 Geographic Innovation vs Supply Chain Risk',
                '⚡ Market Event Impact on Patent Activity', 
                '💰 Business Value: Cost Savings & ROI Analysis'
            ),
            specs=[
                [{"secondary_y": True}, {"type": "geo"}],
                [{"secondary_y": False}, {"secondary_y": True}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )
        
        # Panel 1: Patent Trends vs Price Volatility
        self._add_patent_price_correlation_panel(fig, patent_data, market_data, row=1, col=1)
        
        # Panel 2: Geographic Innovation vs Supply Risk
        self._add_geographic_supply_risk_panel(fig, patent_data, correlation_data, row=1, col=2)
        
        # Panel 3: Market Event Impact Analysis
        self._add_market_event_impact_panel(fig, patent_data, correlation_data, row=2, col=1)
        
        # Panel 4: Business Value Analysis
        self._add_business_value_panel(fig, integrated_results, row=2, col=2)
        
        # Update layout for executive presentation
        fig.update_layout(
            title={
                'text': "🏆 REE Patent-Market Intelligence Dashboard<br><sub>Professional Business Intelligence for PATLIB Consulting Services</sub>",
                'x': 0.5,
                'font': {'size': 20}
            },
            height=900,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(248,249,250,0.8)'
        )
        
        print("✅ Integrated executive dashboard created")
        return fig
    
    def _add_patent_price_correlation_panel(self, fig, patent_data, market_data, row, col):
        """Add patent filing trends vs price volatility panel"""
        # Patent filings by year
        patent_by_year = patent_data.groupby('appln_filing_year').size().reset_index()
        patent_by_year.columns = ['year', 'patent_filings']
        
        # Market price data
        price_trends = market_data['price_trends']['neodymium_price_index']
        price_df = pd.DataFrame([
            {'year': year, 'price_index': price} 
            for year, price in price_trends.items()
        ])
        
        # Merge data
        combined_data = pd.merge(patent_by_year, price_df, on='year', how='outer').fillna(0)
        combined_data = combined_data[(combined_data['year'] >= 2010) & (combined_data['year'] <= 2024)]
        
        # Patent filings trend
        fig.add_trace(
            go.Scatter(
                x=combined_data['year'],
                y=combined_data['patent_filings'],
                mode='lines+markers',
                name='Patent Filings',
                line=dict(color=self.color_schemes['patent_trends'], width=3),
                marker=dict(size=8),
                yaxis='y'
            ),
            row=row, col=col
        )
        
        # Price index trend (secondary y-axis)
        fig.add_trace(
            go.Scatter(
                x=combined_data['year'],
                y=combined_data['price_index'],
                mode='lines+markers',
                name='REE Price Index',
                line=dict(color=self.color_schemes['market_prices'], width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond'),
                yaxis='y2'
            ),
            row=row, col=col, secondary_y=True
        )
        
        # Highlight major market events
        major_events = {
            2011: '2011 China Quota Crisis',
            2020: '2020 COVID Disruption',
            2022: '2022 Ukraine Conflict'
        }
        
        for year, event in major_events.items():
            if year in combined_data['year'].values:
                y_val = combined_data[combined_data['year'] == year]['patent_filings'].iloc[0]
                fig.add_annotation(
                    x=year, y=y_val,
                    text=f"⚡ {event}",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="red",
                    row=row, col=col
                )
    
    def _add_geographic_supply_risk_panel(self, fig, patent_data, correlation_data, row, col):
        """Add geographic innovation vs supply chain risk panel"""
        # Top patent countries
        top_countries = patent_data['appln_auth'].value_counts().head(10)
        
        # Country codes for proper mapping
        country_mapping = {
            'CN': 'CHN', 'US': 'USA', 'JP': 'JPN', 'DE': 'DEU', 'KR': 'KOR',
            'GB': 'GBR', 'FR': 'FRA', 'CA': 'CAN', 'AU': 'AUS', 'RU': 'RUS',
            'FI': 'FIN', 'BE': 'BEL', 'BR': 'BRA', 'IL': 'ISR', 'IT': 'ITA'
        }
        
        # Supply risk levels (China=highest, diversified countries=lower)
        supply_risk_scores = {
            'CHN': 95, 'USA': 25, 'JPN': 30, 'DEU': 35, 'KOR': 40,
            'GBR': 30, 'FRA': 35, 'CAN': 20, 'AUS': 15, 'RUS': 60,
            'FIN': 40, 'BEL': 45, 'BRA': 50, 'ISR': 50, 'ITA': 40
        }
        
        # Prepare data for choropleth
        countries_data = []
        for country_code, count in top_countries.items():
            iso_code = country_mapping.get(country_code, country_code)
            risk_score = supply_risk_scores.get(iso_code, 50)
            countries_data.append({
                'iso_alpha': iso_code,
                'country': country_code,
                'patent_count': count,
                'supply_risk': risk_score,
                'innovation_intensity': count / risk_score * 100  # Patents per risk unit
            })
        
        countries_df = pd.DataFrame(countries_data)
        
        # Create choropleth map
        fig.add_trace(
            go.Choropleth(
                locations=countries_df['iso_alpha'],
                z=countries_df['innovation_intensity'],
                text=countries_df['country'],
                colorscale='RdYlGn',
                reversescale=False,
                marker_line_color='darkgray',
                marker_line_width=0.5,
                colorbar=dict(
                    title="Innovation Intensity<br>(Patents/Risk)",
                    len=0.4,
                    x=1.02
                ),
                name='Innovation vs Risk'
            ),
            row=row, col=col
        )
    
    def _add_market_event_impact_panel(self, fig, patent_data, correlation_data, row, col):
        """Add market event impact analysis panel"""
        # Market events timeline
        market_events = correlation_data.get('market_event_analysis', {}).get('major_events_analysis', [])
        
        if not market_events:
            # Fallback with synthetic data
            market_events = [
                {'period': '2010-2011', 'event': 'China REE Export Quota Crisis'},
                {'period': '2020-2022', 'event': 'COVID-19 Supply Chain Disruption'},
                {'period': '2022-2023', 'event': 'Ukraine Conflict Effects'},
                {'period': '2023-2024', 'event': 'EU Critical Raw Materials Act'}
            ]
        
        # Patent filing response analysis
        event_years = []
        baseline_patents = []
        response_patents = []
        event_labels = []
        
        for event in market_events:
            period = event['period']
            start_year = int(period.split('-')[0])
            event_years.append(start_year)
            event_labels.append(event['event'][:30] + '...' if len(event['event']) > 30 else event['event'])
            
            # Calculate baseline (2 years before)
            baseline_data = patent_data[
                (patent_data['appln_filing_year'] >= start_year-2) & 
                (patent_data['appln_filing_year'] < start_year)
            ]
            baseline_avg = len(baseline_data) / 2 if len(baseline_data) > 0 else 50
            baseline_patents.append(baseline_avg)
            
            # Calculate response (2 years after)
            response_data = patent_data[
                (patent_data['appln_filing_year'] >= start_year) & 
                (patent_data['appln_filing_year'] <= start_year+2)
            ]
            response_avg = len(response_data) / 3 if len(response_data) > 0 else 60
            response_patents.append(response_avg)
        
        # Baseline vs Response comparison
        fig.add_trace(
            go.Bar(
                x=event_labels,
                y=baseline_patents,
                name='Pre-Event Baseline',
                marker_color=self.color_schemes['patent_trends'],
                opacity=0.7
            ),
            row=row, col=col
        )
        
        fig.add_trace(
            go.Bar(
                x=event_labels,
                y=response_patents,
                name='Post-Event Response',
                marker_color=self.color_schemes['supply_risk'],
                opacity=0.9
            ),
            row=row, col=col
        )
    
    def _add_business_value_panel(self, fig, integrated_results, row, col):
        """Add business value and ROI analysis panel"""
        # ROI analysis
        roi_analysis = self.roi_calculator.calculate_cost_savings_analysis('corporate_library', 5)
        
        # Cost comparison
        commercial_cost = roi_analysis['commercial_solution_costs']['total_cost_over_period'] / 1000  # In thousands
        patlib_cost = roi_analysis['patlib_solution_costs']['total_cost_over_period'] / 1000
        savings = roi_analysis['savings_analysis']['absolute_savings_euros'] / 1000
        
        # Cost comparison bar chart
        fig.add_trace(
            go.Bar(
                x=['Commercial<br>Databases', 'PATLIB<br>Solution', 'Net<br>Savings'],
                y=[commercial_cost, patlib_cost, savings],
                marker_color=[self.color_schemes['supply_risk'], 
                             self.color_schemes['business_value'], 
                             self.color_schemes['correlation']],
                text=[f'€{commercial_cost:.0f}k', f'€{patlib_cost:.0f}k', f'€{savings:.0f}k'],
                textposition='auto',
                name='5-Year Costs (€000s)'
            ),
            row=row, col=col
        )
        
        # ROI timeline (secondary y-axis)
        years = list(range(1, 6))
        cumulative_roi = []
        initial_investment = patlib_cost / 5
        annual_savings = savings / 5
        
        for year in years:
            total_savings = annual_savings * year
            roi = (total_savings / initial_investment - 1) * 100
            cumulative_roi.append(roi)
        
        fig.add_trace(
            go.Scatter(
                x=years,
                y=cumulative_roi,
                mode='lines+markers',
                name='ROI % Over Time',
                line=dict(color=self.color_schemes['market_prices'], width=3),
                marker=dict(size=10),
                yaxis='y2'
            ),
            row=row, col=col, secondary_y=True
        )
    
    def create_supply_chain_risk_dashboard(self, integrated_results: Optional[Dict] = None) -> go.Figure:
        """
        Create specialized supply chain risk dashboard
        Focus on Chinese dominance and mitigation strategies
        """
        print("🌍 CREATING SUPPLY CHAIN RISK DASHBOARD")
        print("-" * 40)
        
        if not integrated_results:
            integrated_results = self.pipeline.run_integrated_analysis(test_mode=True, generate_reports=False)
        
        # Create 2x2 subplot for supply chain analysis
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '🏭 Global REE Supply Concentration',
                '📊 Patent Innovation by Supply Risk Level',
                '⚠️ Supply Vulnerability Assessment',
                '🛡️ Risk Mitigation Strategies'
            ),
            specs=[
                [{"type": "pie"}, {"type": "scatter"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # Panel 1: Supply concentration pie chart
        supply_data = {
            'China': 85,
            'USA': 6,
            'Australia': 4,
            'Myanmar': 3,
            'Others': 2
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(supply_data.keys()),
                values=list(supply_data.values()),
                hole=0.4,
                marker_colors=['#d62728', '#2ca02c', '#ff7f0e', '#1f77b4', '#9467bd'],
                textinfo='label+percent',
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Panel 2: Patent innovation vs supply risk scatter
        if integrated_results.get('patent_analytics', {}).get('ree_dataset') is not None:
            patent_data = integrated_results['patent_analytics']['ree_dataset']
            country_patents = patent_data['appln_auth'].value_counts().head(10)
            
            risk_levels = {
                'CN': 95, 'US': 25, 'JP': 30, 'DE': 35, 'KR': 40,
                'GB': 30, 'FR': 35, 'CA': 20, 'AU': 15, 'RU': 60
            }
            
            x_data = [risk_levels.get(country, 50) for country in country_patents.index]
            y_data = country_patents.values
            
            fig.add_trace(
                go.Scatter(
                    x=x_data,
                    y=y_data,
                    mode='markers+text',
                    text=country_patents.index,
                    textposition='top center',
                    marker=dict(
                        size=[count/10 for count in y_data],
                        color=x_data,
                        colorscale='RdYlGn_r',
                        showscale=True,
                        colorbar=dict(title="Supply Risk Level", x=0.48)
                    ),
                    name='Countries'
                ),
                row=1, col=2
            )
        
        # Panel 3: Vulnerability assessment
        vulnerability_categories = [
            'Processing Capacity',
            'Raw Material Supply',
            'Technology Access',
            'Market Control',
            'Regulatory Influence'
        ]
        
        china_dominance = [90, 85, 70, 80, 60]  # China's control percentage
        western_capacity = [10, 15, 30, 20, 40]  # Western alternative capacity
        
        fig.add_trace(
            go.Bar(
                x=vulnerability_categories,
                y=china_dominance,
                name='Chinese Control %',
                marker_color='#d62728',
                opacity=0.8
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=vulnerability_categories,
                y=western_capacity,
                name='Western Alternatives %',
                marker_color='#2ca02c',
                opacity=0.8
            ),
            row=2, col=1
        )
        
        # Panel 4: Mitigation strategies effectiveness
        strategies = [
            'Recycling Programs',
            'Alternative Materials',
            'Strategic Reserves',
            'New Suppliers',
            'Processing Facilities'
        ]
        
        implementation_cost = [20, 100, 50, 80, 200]  # Million EUR
        risk_reduction = [40, 70, 30, 50, 80]  # Percentage risk reduction
        
        fig.add_trace(
            go.Bar(
                x=strategies,
                y=implementation_cost,
                name='Investment Required (M€)',
                marker_color='#ff7f0e',
                yaxis='y3'
            ),
            row=2, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=strategies,
                y=risk_reduction,
                mode='markers+lines',
                name='Risk Reduction %',
                marker=dict(size=12, color='#1f77b4'),
                yaxis='y4'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': "🛡️ REE Supply Chain Risk Assessment Dashboard<br><sub>Strategic Intelligence for Supply Security Planning</sub>",
                'x': 0.5,
                'font': {'size': 18}
            },
            height=800,
            showlegend=True
        )
        
        print("✅ Supply chain risk dashboard created")
        return fig
    
    def create_cost_savings_demonstration(self) -> go.Figure:
        """
        Create cost savings demonstration dashboard
        ROI calculator showing €45k commercial tools vs €4.5k free solution
        """
        print("💰 CREATING COST SAVINGS DEMONSTRATION")
        print("-" * 40)
        
        # Create ROI comparison dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '💸 5-Year Total Cost Comparison',
                '📈 ROI Timeline Analysis',
                '🏢 Savings by Client Type',
                '⚖️ Cost-Benefit Analysis'
            ),
            specs=[
                [{"type": "bar"}, {"secondary_y": True}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Panel 1: Total cost comparison
        client_types = ['University\nLibrary', 'Corporate\nLibrary', 'SME\nManufacturing', 'Consulting\nFirm']
        
        commercial_costs = []
        patlib_costs = []
        savings_pct = []
        
        for client_type in ['university_library', 'corporate_library', 'sme_manufacturing', 'consulting_firm']:
            cost_analysis = self.roi_calculator.calculate_cost_savings_analysis(client_type, 5)
            
            commercial = cost_analysis['commercial_solution_costs']['total_cost_over_period'] / 1000
            patlib = cost_analysis['patlib_solution_costs']['total_cost_over_period'] / 1000
            savings = cost_analysis['savings_analysis']['percentage_savings']
            
            commercial_costs.append(commercial)
            patlib_costs.append(patlib)
            savings_pct.append(savings)
        
        fig.add_trace(
            go.Bar(
                x=client_types,
                y=commercial_costs,
                name='Commercial Solutions',
                marker_color='#d62728',
                text=[f'€{cost:.0f}k' for cost in commercial_costs],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=client_types,
                y=patlib_costs,
                name='PATLIB Solution',
                marker_color='#2ca02c',
                text=[f'€{cost:.0f}k' for cost in patlib_costs],
                textposition='auto'
            ),
            row=1, col=1
        )
        
        # Panel 2: ROI timeline
        years = list(range(1, 6))
        base_analysis = self.roi_calculator.calculate_cost_savings_analysis('corporate_library', 5)
        annual_savings = base_analysis['savings_analysis']['annual_savings'] / 1000
        initial_investment = base_analysis['patlib_solution_costs']['breakdown']['setup_and_training'] / 1000
        
        cumulative_savings = []
        roi_percentage = []
        
        for year in years:
            total_savings = annual_savings * year
            cumulative_savings.append(total_savings)
            roi = (total_savings / initial_investment - 1) * 100
            roi_percentage.append(roi)
        
        fig.add_trace(
            go.Bar(
                x=years,
                y=cumulative_savings,
                name='Cumulative Savings (€k)',
                marker_color='#1f77b4'
            ),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Scatter(
                x=years,
                y=roi_percentage,
                mode='lines+markers',
                name='ROI %',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=10),
                yaxis='y2'
            ),
            row=1, col=2, secondary_y=True
        )
        
        # Panel 3: Savings by client type
        fig.add_trace(
            go.Bar(
                x=client_types,
                y=savings_pct,
                name='Savings Percentage',
                marker_color='#9467bd',
                text=[f'{pct:.1f}%' for pct in savings_pct],
                textposition='auto'
            ),
            row=2, col=1
        )
        
        # Panel 4: Cost-benefit analysis scatter
        business_scenarios = self.roi_calculator.generate_roi_scenarios('corporate_library')
        scenarios = business_scenarios['scenarios']
        
        scenario_names = [s['scenario_name'].replace('Implementation', '').strip() for s in scenarios]
        payback_months = [s['payback_period_months'] for s in scenarios]
        roi_5_year = [s['five_year_roi_percent'] for s in scenarios]
        
        fig.add_trace(
            go.Scatter(
                x=payback_months,
                y=roi_5_year,
                mode='markers+text',
                text=scenario_names,
                textposition='top center',
                marker=dict(
                    size=20,
                    color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'],
                    opacity=0.8
                ),
                name='ROI Scenarios'
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title={
                'text': "💰 PATLIB Cost Savings & ROI Demonstration<br><sub>90%+ Savings vs Commercial Database Solutions</sub>",
                'x': 0.5,
                'font': {'size': 18}
            },
            height=800,
            showlegend=True
        )
        
        print("✅ Cost savings demonstration created")
        return fig
    
    def _create_error_dashboard(self, error_message: str) -> go.Figure:
        """Create error dashboard when data is unavailable"""
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"Dashboard Error: {error_message}<br>Please check data pipeline and try again",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="red")
        )
        
        fig.update_layout(
            title="❌ Dashboard Error",
            height=400
        )
        
        return fig

def test_enhanced_dashboard():
    """Test enhanced dashboard functionality"""
    print("🧪 Testing Enhanced REE Dashboard...")
    
    dashboard = EnhancedREEDashboard()
    
    # Test integrated executive dashboard
    print("\n📊 Testing integrated executive dashboard...")
    try:
        exec_dashboard = dashboard.create_integrated_executive_dashboard()
        print("✅ Integrated executive dashboard created successfully")
    except Exception as e:
        print(f"⚠️ Executive dashboard test failed: {str(e)}")
        exec_dashboard = None
    
    # Test supply chain risk dashboard
    print("\n🌍 Testing supply chain risk dashboard...")
    try:
        risk_dashboard = dashboard.create_supply_chain_risk_dashboard()
        print("✅ Supply chain risk dashboard created successfully")
    except Exception as e:
        print(f"⚠️ Risk dashboard test failed: {str(e)}")
        risk_dashboard = None
    
    # Test cost savings demonstration
    print("\n💰 Testing cost savings demonstration...")
    try:
        savings_dashboard = dashboard.create_cost_savings_demonstration()
        print("✅ Cost savings demonstration created successfully")
    except Exception as e:
        print(f"⚠️ Savings dashboard test failed: {str(e)}")
        savings_dashboard = None
    
    return {
        'executive_dashboard': exec_dashboard,
        'risk_dashboard': risk_dashboard,
        'savings_dashboard': savings_dashboard,
        'test_success': all([exec_dashboard, risk_dashboard, savings_dashboard])
    }

def create_presentation_ready_dashboards():
    """Create all dashboards for presentation"""
    print("🎨 CREATING PRESENTATION-READY DASHBOARDS")
    print("=" * 50)
    
    dashboard = EnhancedREEDashboard()
    
    # Create integrated analysis first
    print("Running integrated analysis...")
    integrated_results = dashboard.pipeline.run_integrated_analysis(test_mode=True, generate_reports=False)
    
    if integrated_results.get('pipeline_metadata', {}).get('execution_success', False):
        print("✅ Integrated analysis successful")
        
        # Create all dashboards
        print("\n📊 Creating executive dashboard...")
        exec_fig = dashboard.create_integrated_executive_dashboard(integrated_results)
        
        print("🌍 Creating supply risk dashboard...")
        risk_fig = dashboard.create_supply_chain_risk_dashboard(integrated_results)
        
        print("💰 Creating cost savings dashboard...")
        savings_fig = dashboard.create_cost_savings_demonstration()
        
        # Export as HTML for presentations
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        exec_file = f"executive_dashboard_{timestamp}.html"
        risk_file = f"supply_risk_dashboard_{timestamp}.html"
        savings_file = f"cost_savings_dashboard_{timestamp}.html"
        
        exec_fig.write_html(exec_file)
        risk_fig.write_html(risk_file)
        savings_fig.write_html(savings_file)
        
        print(f"\n🎉 PRESENTATION DASHBOARDS COMPLETE!")
        print(f"📂 Files created:")
        print(f"   • {exec_file}")
        print(f"   • {risk_file}")
        print(f"   • {savings_file}")
        
        return {
            'files': [exec_file, risk_file, savings_file],
            'success': True
        }
    else:
        print("❌ Integrated analysis failed - cannot create dashboards")
        return {'success': False}

if __name__ == "__main__":
    test_results = test_enhanced_dashboard()
    
    if test_results['test_success']:
        print(f"\n🎉 Enhanced Dashboard test complete - All dashboards functional!")
        
        # Create presentation files
        presentation_results = create_presentation_ready_dashboards()
        if presentation_results['success']:
            print("📊 Presentation-ready dashboard files created!")
    else:
        print(f"\n⚠️ Some dashboard tests failed - Check individual components")