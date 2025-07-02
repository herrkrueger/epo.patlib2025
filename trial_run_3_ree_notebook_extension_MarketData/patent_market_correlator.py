"""
Patent-Market Correlator - REE Market Intelligence Extension
Connects existing REE patent data with USGS market intelligence
Built for EPO TIP Platform / PATLIB 2025 demonstration
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy.stats import pearsonr
from datetime import datetime

class PatentMarketCorrelator:
    """
    Core correlation analysis between patent filings and market events
    Uses existing patent dataset + USGS market data
    """
    
    def __init__(self, patent_dataset: pd.DataFrame, usgs_collector):
        self.patent_data = patent_dataset
        self.market_collector = usgs_collector
        self.logger = logging.getLogger(__name__)
        
        # Ensure patent data has required columns
        required_cols = ['appln_filing_year', 'primary_country', 'appln_id']
        missing_cols = [col for col in required_cols if col not in self.patent_data.columns]
        if missing_cols:
            raise ValueError(f"Patent dataset missing required columns: {missing_cols}")
    
    def analyze_price_shock_patent_response(self, shock_threshold: float = 50.0) -> Dict:
        """
        Correlate USGS price spikes with patent filing patterns
        Key innovation: Quantify innovation response to market disruptions
        """
        # Get price shock periods from USGS data
        price_shocks = self.market_collector.identify_price_shock_periods(shock_threshold)
        
        # Aggregate patent filings by year
        patent_yearly = self.patent_data.groupby('appln_filing_year').size().reset_index()
        patent_yearly.columns = ['year', 'patent_count']
        
        # Get market price trends
        price_trends = self.market_collector.get_price_trends('neodymium')
        
        # Merge datasets for correlation analysis
        correlation_data = pd.merge(patent_yearly, price_trends, on='year', how='inner')
        
        # Calculate correlation metrics
        if len(correlation_data) > 2:
            correlation_coef, p_value = pearsonr(
                correlation_data['patent_count'], 
                correlation_data['price_index']
            )
        else:
            correlation_coef, p_value = 0.0, 1.0
        
        # Analyze patent response to specific shocks
        shock_responses = []
        for shock in price_shocks:
            shock_year = int(shock['year'])
            
            # Get patent counts around shock period
            pre_shock = patent_yearly[patent_yearly['year'] == shock_year - 1]
            shock_year_data = patent_yearly[patent_yearly['year'] == shock_year]
            post_shock = patent_yearly[patent_yearly['year'] == shock_year + 1]
            
            if not pre_shock.empty and not shock_year_data.empty and not post_shock.empty:
                response_data = {
                    'shock_year': shock_year,
                    'shock_type': shock['shock_type'],
                    'price_change': shock['price_change_percent'],
                    'pre_shock_patents': pre_shock.iloc[0]['patent_count'],
                    'shock_year_patents': shock_year_data.iloc[0]['patent_count'],
                    'post_shock_patents': post_shock.iloc[0]['patent_count'],
                    'patent_response_ratio': (post_shock.iloc[0]['patent_count'] / 
                                           pre_shock.iloc[0]['patent_count']) if pre_shock.iloc[0]['patent_count'] > 0 else 0
                }
                shock_responses.append(response_data)
        
        return {
            'overall_correlation': {
                'correlation_coefficient': correlation_coef,
                'p_value': p_value,
                'significance': 'significant' if p_value < 0.05 else 'not_significant',
                'interpretation': self._interpret_correlation(correlation_coef, p_value)
            },
            'shock_responses': shock_responses,
            'correlation_data': correlation_data.to_dict('records'),
            'summary': {
                'total_shocks_analyzed': len(shock_responses),
                'average_patent_response': np.mean([r['patent_response_ratio'] for r in shock_responses]) if shock_responses else 0,
                'strongest_response_year': max(shock_responses, key=lambda x: x['patent_response_ratio'])['shock_year'] if shock_responses else None
            }
        }
    
    def create_supply_risk_patent_dashboard_data(self) -> Dict:
        """
        Combine USGS supply concentration with patent geographic distribution
        Critical for strategic planning and risk assessment
        """
        # Get supply concentration from USGS
        supply_concentration = self.market_collector.calculate_supply_concentration()
        
        # Get patent distribution by country
        patent_by_country = self.patent_data.groupby('primary_country').agg({
            'appln_id': 'count',
            'appln_filing_year': ['min', 'max']
        }).reset_index()
        
        patent_by_country.columns = ['country', 'patent_count', 'first_patent_year', 'last_patent_year']
        
        # Calculate innovation vs production ratios
        risk_analysis = []
        for country, production_share in supply_concentration.items():
            country_patents = patent_by_country[patent_by_country['country'] == country]
            
            if not country_patents.empty:
                patent_count = country_patents.iloc[0]['patent_count']
                patent_share = (patent_count / patent_by_country['patent_count'].sum()) * 100
                
                risk_metrics = {
                    'country': country,
                    'production_share_percent': production_share,
                    'patent_share_percent': patent_share,
                    'production_patent_ratio': production_share / patent_share if patent_share > 0 else float('inf'),
                    'risk_category': self._categorize_supply_risk(production_share, patent_share),
                    'patent_count': patent_count,
                    'innovation_period': f"{country_patents.iloc[0]['first_patent_year']}-{country_patents.iloc[0]['last_patent_year']}"
                }
                risk_analysis.append(risk_metrics)
        
        # Calculate dependency risk scores
        import_dependency = self.market_collector.get_import_dependency_data()
        
        return {
            'supply_risk_analysis': risk_analysis,
            'import_dependency': import_dependency,
            'key_insights': {
                'highest_risk_countries': [r for r in risk_analysis if r['risk_category'] == 'high_risk'],
                'innovation_leaders': sorted(risk_analysis, key=lambda x: x['patent_share_percent'], reverse=True)[:5],
                'production_leaders': sorted(risk_analysis, key=lambda x: x['production_share_percent'], reverse=True)[:5]
            },
            'summary_metrics': {
                'total_countries_analyzed': len(risk_analysis),
                'high_risk_countries_count': len([r for r in risk_analysis if r['risk_category'] == 'high_risk']),
                'average_import_dependency': np.mean(list(import_dependency.values())) if import_dependency else 0
            }
        }
    
    def generate_market_event_impact_analysis(self) -> Dict:
        """
        Timeline analysis: Market disruptions → Patent filing response
        Historical correlation for predictive insights
        """
        market_events = self.market_collector.get_market_events_timeline()
        
        # Analyze patent response to each major market event
        event_impacts = []
        for event in market_events:
            event_year = event['year']
            
            # Get patent filing patterns around event
            pre_event_years = [event_year - 2, event_year - 1]
            post_event_years = [event_year + 1, event_year + 2]
            
            pre_event_patents = self.patent_data[
                self.patent_data['appln_filing_year'].isin(pre_event_years)
            ].groupby('appln_filing_year').size().mean()
            
            post_event_patents = self.patent_data[
                self.patent_data['appln_filing_year'].isin(post_event_years)
            ].groupby('appln_filing_year').size().mean()
            
            # Calculate geographic response
            pre_countries = self.patent_data[
                self.patent_data['appln_filing_year'].isin(pre_event_years)
            ]['primary_country'].nunique()
            
            post_countries = self.patent_data[
                self.patent_data['appln_filing_year'].isin(post_event_years)
            ]['primary_country'].nunique()
            
            impact_analysis = {
                'event': event['event'],
                'year': event_year,
                'description': event['description'],
                'patent_response': {
                    'pre_event_avg_patents': pre_event_patents,
                    'post_event_avg_patents': post_event_patents,
                    'response_ratio': post_event_patents / pre_event_patents if pre_event_patents > 0 else 0,
                    'response_magnitude': self._categorize_response_magnitude(
                        post_event_patents / pre_event_patents if pre_event_patents > 0 else 0
                    )
                },
                'geographic_response': {
                    'pre_event_countries': pre_countries,
                    'post_event_countries': post_countries,
                    'geographic_expansion': post_countries - pre_countries
                }
            }
            event_impacts.append(impact_analysis)
        
        return {
            'event_impacts': event_impacts,
            'trend_analysis': {
                'average_patent_response': np.mean([e['patent_response']['response_ratio'] for e in event_impacts]),
                'most_impactful_event': max(event_impacts, key=lambda x: x['patent_response']['response_ratio']) if event_impacts else None,
                'geographic_innovation_trend': sum([e['geographic_response']['geographic_expansion'] for e in event_impacts])
            },
            'predictive_insights': self._generate_predictive_insights(event_impacts)
        }
    
    def _interpret_correlation(self, correlation: float, p_value: float) -> str:
        """Interpret correlation strength and significance"""
        if p_value >= 0.05:
            return "No statistically significant correlation"
        
        abs_corr = abs(correlation)
        if abs_corr < 0.3:
            strength = "weak"
        elif abs_corr < 0.7:
            strength = "moderate"
        else:
            strength = "strong"
        
        direction = "positive" if correlation > 0 else "negative"
        return f"{strength.capitalize()} {direction} correlation (r={correlation:.3f}, p={p_value:.3f})"
    
    def _categorize_supply_risk(self, production_share: float, patent_share: float) -> str:
        """Categorize supply risk based on production vs innovation balance"""
        ratio = production_share / patent_share if patent_share > 0 else float('inf')
        
        if ratio > 3:  # High production, low innovation
            return "high_risk"
        elif ratio > 1.5:
            return "medium_risk"
        else:
            return "low_risk"
    
    def _categorize_response_magnitude(self, response_ratio: float) -> str:
        """Categorize patent response magnitude"""
        if response_ratio > 1.5:
            return "strong_increase"
        elif response_ratio > 1.1:
            return "moderate_increase"
        elif response_ratio > 0.9:
            return "stable"
        else:
            return "decrease"
    
    def _generate_predictive_insights(self, event_impacts: List[Dict]) -> List[str]:
        """Generate predictive insights based on historical patterns"""
        insights = []
        
        # Analyze response patterns
        response_ratios = [e['patent_response']['response_ratio'] for e in event_impacts]
        avg_response = np.mean(response_ratios) if response_ratios else 0
        
        if avg_response > 1.2:
            insights.append("Historical pattern: Market disruptions typically trigger 20%+ increase in REE patent filings")
        
        # Geographic expansion patterns
        geo_expansions = [e['geographic_response']['geographic_expansion'] for e in event_impacts]
        if sum(geo_expansions) > 0:
            insights.append("Market crises drive geographic diversification of innovation")
        
        # Strong responses analysis
        strong_responses = [e for e in event_impacts if e['patent_response']['response_magnitude'] == 'strong_increase']
        if strong_responses:
            insights.append(f"Supply disruptions show strongest correlation with innovation response ({len(strong_responses)} events)")
        
        return insights

# Testing function
def test_patent_market_correlator():
    """Test patent-market correlation functionality"""
    # Import required modules
    from usgs_market_collector import USGSMarketDataCollector
    
    # Create sample patent data for testing
    sample_data = pd.DataFrame({
        'appln_id': range(1, 101),
        'appln_filing_year': np.random.choice(range(2010, 2024), 100),
        'primary_country': np.random.choice(['China', 'United States', 'Germany', 'Japan'], 100)
    })
    
    # Initialize components
    usgs_collector = USGSMarketDataCollector()
    correlator = PatentMarketCorrelator(sample_data, usgs_collector)
    
    # Test price shock analysis
    shock_analysis = correlator.analyze_price_shock_patent_response()
    assert 'overall_correlation' in shock_analysis, "Failed to analyze price shocks"
    print("✅ Price shock analysis completed")
    print(f"   Correlation: {shock_analysis['overall_correlation']['interpretation']}")
    
    # Test supply risk analysis
    risk_analysis = correlator.create_supply_risk_patent_dashboard_data()
    assert 'supply_risk_analysis' in risk_analysis, "Failed to create risk analysis"
    print("✅ Supply risk analysis completed")
    print(f"   Countries analyzed: {risk_analysis['summary_metrics']['total_countries_analyzed']}")
    
    # Test market event impact
    event_analysis = correlator.generate_market_event_impact_analysis()
    assert 'event_impacts' in event_analysis, "Failed to analyze market events"
    print("✅ Market event analysis completed")
    print(f"   Events analyzed: {len(event_analysis['event_impacts'])}")
    print(f"   Predictive insights: {len(event_analysis['predictive_insights'])}")
    
    print("\n🎯 All patent-market correlation tests passed!")
    return True

if __name__ == "__main__":
    test_patent_market_correlator()