"""
Market Event Analyzer - REE Market Intelligence Extension
Strategic disruption analysis and predictive insights
Built for EPO TIP Platform / PATLIB 2025 demonstration
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta

class MarketEventAnalyzer:
    """
    Strategic analysis of market disruptions and innovation response patterns
    Provides predictive insights for business intelligence
    """
    
    def __init__(self, usgs_collector, patent_market_correlator):
        self.market_collector = usgs_collector
        self.correlator = patent_market_correlator
        self.logger = logging.getLogger(__name__)
        
        # Define disruption categories
        self.disruption_categories = {
            'supply_shock': ['quota', 'restriction', 'ban', 'conflict'],
            'price_shock': ['spike', 'crash', 'volatility'],
            'geopolitical': ['war', 'tension', 'sanction', 'dispute'],
            'regulatory': ['act', 'regulation', 'policy', 'law'],
            'pandemic': ['covid', 'disruption', 'shutdown']
        }
    
    def analyze_historical_disruption_timeline(self) -> Dict:
        """
        Comprehensive timeline analysis of market disruptions and innovation response
        Identifies patterns for predictive modeling
        """
        market_events = self.market_collector.get_market_events_timeline()
        price_shocks = self.market_collector.identify_price_shock_periods()
        
        # Combine market events with price data
        disruption_timeline = []
        
        for event in market_events:
            # Categorize event type
            event_category = self._categorize_event(event['description'].lower())
            
            # Find corresponding price shock if any
            corresponding_shock = None
            for shock in price_shocks:
                if abs(shock['year'] - event['year']) <= 1:
                    corresponding_shock = shock
                    break
            
            disruption_data = {
                'year': event['year'],
                'event': event['event'],
                'description': event['description'],
                'category': event_category,
                'price_impact': corresponding_shock,
                'severity': self._calculate_disruption_severity(event, corresponding_shock),
                'duration_estimate': self._estimate_disruption_duration(event_category),
                'recovery_pattern': self._analyze_recovery_pattern(event['year'])
            }
            disruption_timeline.append(disruption_data)
        
        # Sort by year and analyze patterns
        disruption_timeline.sort(key=lambda x: x['year'])
        
        return {
            'disruption_timeline': disruption_timeline,
            'pattern_analysis': self._analyze_disruption_patterns(disruption_timeline),
            'frequency_analysis': self._analyze_disruption_frequency(disruption_timeline),
            'severity_trends': self._analyze_severity_trends(disruption_timeline)
        }
    
    def generate_innovation_response_patterns(self) -> Dict:
        """
        Analyze how innovation patterns respond to different types of market disruptions
        """
        # Get correlation analysis results
        shock_analysis = self.correlator.analyze_price_shock_patent_response()
        event_analysis = self.correlator.generate_market_event_impact_analysis()
        
        # Analyze response patterns by disruption type
        response_patterns = {}
        
        for event_impact in event_analysis['event_impacts']:
            event_year = event_impact['year']
            response_ratio = event_impact['patent_response']['response_ratio']
            
            # Categorize the event
            event_category = self._categorize_event(event_impact['description'].lower())
            
            if event_category not in response_patterns:
                response_patterns[event_category] = {
                    'events': [],
                    'response_ratios': [],
                    'average_response': 0,
                    'response_consistency': 0
                }
            
            response_patterns[event_category]['events'].append(event_impact)
            response_patterns[event_category]['response_ratios'].append(response_ratio)
        
        # Calculate aggregated metrics for each pattern
        for category, pattern in response_patterns.items():
            if pattern['response_ratios']:
                pattern['average_response'] = np.mean(pattern['response_ratios'])
                pattern['response_consistency'] = 1 - np.std(pattern['response_ratios']) / np.mean(pattern['response_ratios'])
                pattern['response_strength'] = self._categorize_response_strength(pattern['average_response'])
        
        return {
            'response_patterns': response_patterns,
            'strongest_response_category': max(response_patterns.items(), 
                                             key=lambda x: x[1]['average_response'])[0] if response_patterns else None,
            'most_consistent_category': max(response_patterns.items(), 
                                          key=lambda x: x[1]['response_consistency'])[0] if response_patterns else None,
            'innovation_triggers': self._identify_innovation_triggers(response_patterns)
        }
    
    def predict_future_disruption_scenarios(self) -> Dict:
        """
        Generate predictive scenarios based on historical patterns
        Strategic planning for potential future disruptions
        """
        historical_analysis = self.analyze_historical_disruption_timeline()
        response_patterns = self.generate_innovation_response_patterns()
        
        # Define potential future scenarios
        future_scenarios = [
            {
                'scenario': 'China Trade Disruption',
                'probability': 'HIGH',
                'description': 'Escalated trade tensions affecting REE supply',
                'category': 'geopolitical',
                'estimated_impact': 'SEVERE'
            },
            {
                'scenario': 'Alternative Supply Development',
                'probability': 'MEDIUM',
                'description': 'New REE sources reduce China dependency',
                'category': 'supply_shock',
                'estimated_impact': 'MODERATE'
            },
            {
                'scenario': 'Green Technology Demand Surge',
                'probability': 'HIGH',
                'description': 'Climate policies drive REE demand spike',
                'category': 'regulatory',
                'estimated_impact': 'MODERATE'
            },
            {
                'scenario': 'Recycling Technology Breakthrough',
                'probability': 'MEDIUM',
                'description': 'Advanced recycling reduces primary REE demand',
                'category': 'supply_shock',
                'estimated_impact': 'MODERATE'
            }
        ]
        
        # Predict innovation response for each scenario
        for scenario in future_scenarios:
            category = scenario['category']
            if category in response_patterns['response_patterns']:
                avg_response = response_patterns['response_patterns'][category]['average_response']
                scenario['predicted_innovation_response'] = self._predict_innovation_response(avg_response)
                scenario['strategic_recommendations'] = self._generate_strategic_recommendations(scenario)
        
        return {
            'future_scenarios': future_scenarios,
            'scenario_planning': {
                'high_probability_scenarios': [s for s in future_scenarios if s['probability'] == 'HIGH'],
                'severe_impact_scenarios': [s for s in future_scenarios if s['estimated_impact'] == 'SEVERE'],
                'innovation_opportunities': self._identify_innovation_opportunities(future_scenarios)
            },
            'strategic_priorities': self._generate_strategic_priorities(future_scenarios, response_patterns)
        }
    
    def generate_risk_assessment_matrix(self) -> Dict:
        """
        Create comprehensive risk assessment for strategic planning
        """
        supply_risk = self.correlator.create_supply_risk_patent_dashboard_data()
        disruption_analysis = self.analyze_historical_disruption_timeline()
        
        # Create risk matrix
        risk_matrix = {
            'supply_concentration_risk': {
                'score': self._calculate_supply_concentration_risk_score(supply_risk),
                'factors': supply_risk['summary_metrics'],
                'mitigation_strategies': []
            },
            'innovation_dependency_risk': {
                'score': self._calculate_innovation_dependency_risk(supply_risk),
                'factors': supply_risk['key_insights'],
                'mitigation_strategies': []
            },
            'disruption_frequency_risk': {
                'score': self._calculate_disruption_frequency_risk(disruption_analysis),
                'factors': disruption_analysis['frequency_analysis'],
                'mitigation_strategies': []
            },
            'market_volatility_risk': {
                'score': self._calculate_market_volatility_risk(),
                'factors': self.market_collector.identify_price_shock_periods(),
                'mitigation_strategies': []
            }
        }
        
        # Generate mitigation strategies
        for risk_type, risk_data in risk_matrix.items():
            risk_data['mitigation_strategies'] = self._generate_mitigation_strategies(risk_type, risk_data['score'])
        
        # Calculate overall risk score
        risk_scores = [risk['score'] for risk in risk_matrix.values()]
        overall_risk_score = np.mean(risk_scores)
        
        return {
            'risk_matrix': risk_matrix,
            'overall_risk_assessment': {
                'score': overall_risk_score,
                'level': self._categorize_risk_level(overall_risk_score),
                'priority_risks': sorted(risk_matrix.items(), key=lambda x: x[1]['score'], reverse=True)[:2]
            },
            'strategic_recommendations': self._generate_comprehensive_strategic_recommendations(risk_matrix)
        }
    
    def _categorize_event(self, description: str) -> str:
        """Categorize market event based on description keywords"""
        for category, keywords in self.disruption_categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        return 'other'
    
    def _calculate_disruption_severity(self, event: Dict, price_shock: Optional[Dict]) -> str:
        """Calculate severity of market disruption"""
        severity_score = 0
        
        # Base severity from event keywords
        high_impact_keywords = ['crisis', 'ban', 'war', 'conflict', 'shutdown']
        if any(keyword in event['description'].lower() for keyword in high_impact_keywords):
            severity_score += 3
        
        # Price impact contribution
        if price_shock:
            price_change = abs(price_shock.get('price_change_percent', 0))
            if price_change > 100:
                severity_score += 3
            elif price_change > 50:
                severity_score += 2
            elif price_change > 20:
                severity_score += 1
        
        if severity_score >= 4:
            return 'SEVERE'
        elif severity_score >= 2:
            return 'MODERATE'
        else:
            return 'MILD'
    
    def _estimate_disruption_duration(self, category: str) -> str:
        """Estimate disruption duration based on category"""
        duration_map = {
            'supply_shock': 'SHORT_TERM',
            'price_shock': 'SHORT_TERM',
            'geopolitical': 'LONG_TERM',
            'regulatory': 'MEDIUM_TERM',
            'pandemic': 'MEDIUM_TERM'
        }
        return duration_map.get(category, 'UNKNOWN')
    
    def _analyze_recovery_pattern(self, disruption_year: int) -> str:
        """Analyze market recovery pattern after disruption"""
        price_data = self.market_collector.get_price_trends('neodymium')
        
        if price_data.empty:
            return 'UNKNOWN'
        
        # Look at price recovery in years following disruption
        post_disruption = price_data[price_data['year'] > disruption_year].head(3)
        
        if len(post_disruption) < 2:
            return 'INSUFFICIENT_DATA'
        
        price_trend = post_disruption['price_index'].pct_change().mean()
        
        if price_trend > 0.1:
            return 'CONTINUED_INCREASE'
        elif price_trend < -0.1:
            return 'RAPID_RECOVERY'
        else:
            return 'GRADUAL_STABILIZATION'
    
    def _analyze_disruption_patterns(self, timeline: List[Dict]) -> Dict:
        """Analyze patterns in disruption timeline"""
        if not timeline:
            return {}
        
        categories = [event['category'] for event in timeline]
        severities = [event['severity'] for event in timeline]
        
        return {
            'most_common_category': max(set(categories), key=categories.count) if categories else None,
            'most_common_severity': max(set(severities), key=severities.count) if severities else None,
            'escalation_pattern': self._detect_escalation_pattern(timeline),
            'cyclical_patterns': self._detect_cyclical_patterns(timeline)
        }
    
    def _analyze_disruption_frequency(self, timeline: List[Dict]) -> Dict:
        """Analyze frequency of disruptions"""
        if not timeline:
            return {'average_interval': 0, 'trend': 'INSUFFICIENT_DATA'}
        
        years = [event['year'] for event in timeline]
        intervals = [years[i] - years[i-1] for i in range(1, len(years))]
        
        return {
            'total_disruptions': len(timeline),
            'average_interval': np.mean(intervals) if intervals else 0,
            'minimum_interval': min(intervals) if intervals else 0,
            'trend': 'INCREASING' if len(intervals) > 1 and intervals[-1] < intervals[0] else 'STABLE'
        }
    
    def _analyze_severity_trends(self, timeline: List[Dict]) -> Dict:
        """Analyze trends in disruption severity over time"""
        if not timeline:
            return {}
        
        severity_scores = []
        for event in timeline:
            severity_map = {'MILD': 1, 'MODERATE': 2, 'SEVERE': 3}
            severity_scores.append(severity_map.get(event['severity'], 1))
        
        if len(severity_scores) > 1:
            trend = 'ESCALATING' if severity_scores[-1] > severity_scores[0] else 'STABLE'
        else:
            trend = 'INSUFFICIENT_DATA'
        
        return {
            'average_severity': np.mean(severity_scores),
            'severity_trend': trend,
            'severe_event_frequency': severity_scores.count(3) / len(severity_scores)
        }
    
    def _categorize_response_strength(self, response_ratio: float) -> str:
        """Categorize innovation response strength"""
        if response_ratio > 1.5:
            return 'STRONG'
        elif response_ratio > 1.1:
            return 'MODERATE'
        elif response_ratio > 0.9:
            return 'WEAK'
        else:
            return 'NEGATIVE'
    
    def _identify_innovation_triggers(self, response_patterns: Dict) -> List[str]:
        """Identify strongest innovation triggers"""
        triggers = []
        
        for category, pattern in response_patterns.items():
            if pattern['average_response'] > 1.2:
                triggers.append(f"{category} events consistently trigger strong innovation response")
        
        return triggers
    
    def _predict_innovation_response(self, historical_avg_response: float) -> Dict:
        """Predict innovation response based on historical patterns"""
        return {
            'expected_response_ratio': historical_avg_response,
            'confidence_level': 'HIGH' if historical_avg_response > 0 else 'LOW',
            'response_category': self._categorize_response_strength(historical_avg_response)
        }
    
    def _generate_strategic_recommendations(self, scenario: Dict) -> List[str]:
        """Generate strategic recommendations for specific scenario"""
        recommendations = []
        
        if scenario['category'] == 'geopolitical':
            recommendations.append("Diversify supply chains to reduce single-country dependency")
            recommendations.append("Invest in alternative REE sources and recycling technologies")
        elif scenario['category'] == 'supply_shock':
            recommendations.append("Strengthen strategic reserves and stockpiling")
            recommendations.append("Accelerate domestic production capabilities")
        elif scenario['category'] == 'regulatory':
            recommendations.append("Monitor policy developments for early warning signals")
            recommendations.append("Engage in regulatory consultation processes")
        
        return recommendations
    
    def _identify_innovation_opportunities(self, scenarios: List[Dict]) -> List[str]:
        """Identify innovation opportunities from scenario analysis"""
        opportunities = [
            "Advanced REE recycling and urban mining technologies",
            "Alternative materials development and substitution research",
            "Supply chain optimization and risk management systems",
            "Demand reduction through efficiency improvements"
        ]
        return opportunities
    
    def _generate_strategic_priorities(self, scenarios: List[Dict], response_patterns: Dict) -> List[str]:
        """Generate strategic priorities based on analysis"""
        priorities = [
            "Develop comprehensive supply chain risk monitoring system",
            "Invest in innovation response capabilities for rapid market adaptation",
            "Build strategic partnerships for supply diversification",
            "Create early warning system for market disruption detection"
        ]
        return priorities
    
    def _calculate_supply_concentration_risk_score(self, supply_risk: Dict) -> float:
        """Calculate risk score for supply concentration"""
        if not supply_risk['summary_metrics']:
            return 5.0
        
        high_risk_count = supply_risk['summary_metrics']['high_risk_countries_count']
        total_countries = supply_risk['summary_metrics']['total_countries_analyzed']
        
        # Higher concentration = higher risk
        concentration_ratio = high_risk_count / total_countries if total_countries > 0 else 1
        return min(10.0, concentration_ratio * 10)
    
    def _calculate_innovation_dependency_risk(self, supply_risk: Dict) -> float:
        """Calculate risk score for innovation dependency"""
        import_dependency = supply_risk.get('import_dependency', {})
        if not import_dependency:
            return 5.0
        
        avg_dependency = np.mean(list(import_dependency.values()))
        return min(10.0, avg_dependency / 10)  # Convert percentage to 0-10 scale
    
    def _calculate_disruption_frequency_risk(self, disruption_analysis: Dict) -> float:
        """Calculate risk score based on disruption frequency"""
        freq_analysis = disruption_analysis.get('frequency_analysis', {})
        if not freq_analysis:
            return 5.0
        
        avg_interval = freq_analysis.get('average_interval', 5)
        # Shorter intervals = higher risk
        return min(10.0, max(1.0, 10 - avg_interval))
    
    def _calculate_market_volatility_risk(self) -> float:
        """Calculate risk score for market volatility"""
        price_shocks = self.market_collector.identify_price_shock_periods()
        
        if not price_shocks:
            return 3.0
        
        # More frequent and severe shocks = higher risk
        avg_shock_magnitude = np.mean([abs(shock['price_change_percent']) for shock in price_shocks])
        shock_frequency = len(price_shocks) / 15  # Over ~15 year period
        
        return min(10.0, (avg_shock_magnitude / 50) * 5 + shock_frequency * 5)
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize overall risk level"""
        if risk_score >= 7:
            return 'HIGH'
        elif risk_score >= 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_mitigation_strategies(self, risk_type: str, risk_score: float) -> List[str]:
        """Generate mitigation strategies for specific risk type"""
        strategies = {
            'supply_concentration_risk': [
                "Develop alternative supplier relationships",
                "Invest in domestic production capabilities",
                "Create strategic material reserves"
            ],
            'innovation_dependency_risk': [
                "Accelerate R&D investment programs",
                "Foster international innovation partnerships",
                "Develop substitute material technologies"
            ],
            'disruption_frequency_risk': [
                "Implement early warning monitoring systems",
                "Develop rapid response protocols",
                "Build flexible supply chain architectures"
            ],
            'market_volatility_risk': [
                "Implement price hedging strategies",
                "Develop long-term supply contracts",
                "Create demand smoothing mechanisms"
            ]
        }
        
        return strategies.get(risk_type, ["Develop risk monitoring capabilities"])
    
    def _generate_comprehensive_strategic_recommendations(self, risk_matrix: Dict) -> List[str]:
        """Generate comprehensive strategic recommendations"""
        recommendations = [
            "Establish integrated risk monitoring and early warning system",
            "Develop multi-source supply diversification strategy",
            "Invest in breakthrough alternative materials research",
            "Create strategic reserves and emergency response protocols",
            "Build international partnerships for supply security"
        ]
        return recommendations
    
    def _detect_escalation_pattern(self, timeline: List[Dict]) -> str:
        """Detect if disruptions are escalating in severity"""
        if len(timeline) < 3:
            return 'INSUFFICIENT_DATA'
        
        recent_events = timeline[-3:]
        severity_map = {'MILD': 1, 'MODERATE': 2, 'SEVERE': 3}
        recent_severities = [severity_map.get(event['severity'], 1) for event in recent_events]
        
        if recent_severities == sorted(recent_severities):
            return 'ESCALATING'
        else:
            return 'VARIABLE'
    
    def _detect_cyclical_patterns(self, timeline: List[Dict]) -> bool:
        """Detect cyclical patterns in disruptions"""
        if len(timeline) < 4:
            return False
        
        years = [event['year'] for event in timeline]
        intervals = [years[i] - years[i-1] for i in range(1, len(years))]
        
        # Simple cyclical detection - consistent intervals
        if len(set(intervals)) <= 2:
            return True
        
        return False

# Testing function
def test_market_event_analyzer():
    """Test market event analyzer functionality"""
    from usgs_market_collector import USGSMarketDataCollector
    from patent_market_correlator import PatentMarketCorrelator
    
    # Create sample data and components
    sample_patent_data = pd.DataFrame({
        'appln_id': range(1, 101),
        'appln_filing_year': np.random.choice(range(2010, 2024), 100),
        'primary_country': np.random.choice(['China', 'United States', 'Germany', 'Japan'], 100)
    })
    
    usgs_collector = USGSMarketDataCollector()
    correlator = PatentMarketCorrelator(sample_patent_data, usgs_collector)
    analyzer = MarketEventAnalyzer(usgs_collector, correlator)
    
    # Test historical disruption analysis
    disruption_analysis = analyzer.analyze_historical_disruption_timeline()
    assert 'disruption_timeline' in disruption_analysis, "Failed to analyze disruption timeline"
    print("✅ Historical disruption analysis completed")
    print(f"   Disruptions analyzed: {len(disruption_analysis['disruption_timeline'])}")
    
    # Test innovation response patterns
    response_patterns = analyzer.generate_innovation_response_patterns()
    assert 'response_patterns' in response_patterns, "Failed to analyze response patterns"
    print("✅ Innovation response patterns analysis completed")
    print(f"   Pattern categories: {len(response_patterns['response_patterns'])}")
    
    # Test future scenario prediction
    future_scenarios = analyzer.predict_future_disruption_scenarios()
    assert 'future_scenarios' in future_scenarios, "Failed to generate future scenarios"
    print("✅ Future scenario prediction completed")
    print(f"   Scenarios generated: {len(future_scenarios['future_scenarios'])}")
    
    # Test risk assessment matrix
    risk_assessment = analyzer.generate_risk_assessment_matrix()
    assert 'risk_matrix' in risk_assessment, "Failed to generate risk assessment"
    print("✅ Risk assessment matrix completed")
    print(f"   Overall risk level: {risk_assessment['overall_risk_assessment']['level']}")
    
    print("\n🎯 All market event analyzer tests passed!")
    return True

if __name__ == "__main__":
    test_market_event_analyzer()