import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

@dataclass
class ROIScenario:
    """Data class for ROI calculation scenarios"""
    scenario_name: str
    initial_investment: float
    annual_savings: float
    implementation_time_months: int
    payback_period_months: int
    five_year_roi_percent: float
    risk_level: str
    confidence_level: str

class ROICalculator:
    """
    ROI Calculator for PATLIB Business Case Demonstrations
    Demonstrates 90% cost savings vs. commercial databases
    Provides compelling financial justification for patent-market analytics adoption
    """
    
    def __init__(self):
        # Commercial database costs (annual licensing)
        self.commercial_costs = {
            'clarivate_derwent': 45000,      # €45k Derwent Innovation
            'lexisnexis_totalpatent': 35000, # €35k TotalPatent
            'questel_orbit': 40000,          # €40k Orbit Intelligence
            'patent_analytics_premium': 25000, # €25k Premium analytics
            'market_intelligence_tools': 30000, # €30k Market intelligence
            'consulting_services': 150000     # €150k Annual consulting
        }
        
        # PATLIB solution costs
        self.patlib_costs = {
            'initial_setup': 5000,           # €5k Initial setup
            'annual_maintenance': 2000,      # €2k Annual maintenance
            'training_costs': 3000,          # €3k Staff training
            'infrastructure': 1000,          # €1k Infrastructure
            'continuous_updates': 1500       # €1.5k Updates and improvements
        }
        
        # Value multipliers by client type
        self.value_multipliers = {
            'university_library': 1.2,      # 20% additional value from research enhancement
            'corporate_library': 1.5,       # 50% additional value from competitive intelligence
            'sme_manufacturing': 2.0,        # 100% additional value from supply chain insights
            'consulting_firm': 3.0,          # 200% additional value from client services
            'government_agency': 1.8         # 80% additional value from policy insights
        }
    
    def calculate_cost_savings_analysis(self, client_type: str = 'corporate_library', years: int = 5) -> Dict:
        """
        Calculate comprehensive cost savings analysis
        Demonstrates financial benefits vs. commercial alternatives
        """
        print(f"💰 CALCULATING COST SAVINGS ANALYSIS - {client_type.upper()}")
        print("-" * 55)
        
        # Total commercial solution costs
        annual_commercial_cost = sum([
            self.commercial_costs['clarivate_derwent'],
            self.commercial_costs['patent_analytics_premium'],
            self.commercial_costs['market_intelligence_tools'],
            self.commercial_costs['consulting_services'] * 0.3  # 30% of consulting
        ])
        
        total_commercial_cost = annual_commercial_cost * years
        
        # PATLIB solution costs
        total_patlib_cost = (
            self.patlib_costs['initial_setup'] +
            self.patlib_costs['training_costs'] +
            (self.patlib_costs['annual_maintenance'] + 
             self.patlib_costs['infrastructure'] + 
             self.patlib_costs['continuous_updates']) * years
        )
        
        # Cost savings calculation
        absolute_savings = total_commercial_cost - total_patlib_cost
        savings_percentage = (absolute_savings / total_commercial_cost) * 100
        
        # Value enhancement calculation
        value_multiplier = self.value_multipliers.get(client_type, 1.0)
        enhanced_value = total_patlib_cost * value_multiplier
        net_value_creation = enhanced_value - total_patlib_cost
        
        cost_savings_analysis = {
            'analysis_parameters': {
                'client_type': client_type,
                'analysis_period_years': years,
                'value_multiplier': value_multiplier,
                'calculation_date': datetime.now().isoformat()
            },
            'commercial_solution_costs': {
                'annual_licensing_fees': annual_commercial_cost,
                'total_cost_over_period': total_commercial_cost,
                'breakdown': {
                    'derwent_innovation': self.commercial_costs['clarivate_derwent'] * years,
                    'patent_analytics': self.commercial_costs['patent_analytics_premium'] * years,
                    'market_intelligence': self.commercial_costs['market_intelligence_tools'] * years,
                    'consulting_services': self.commercial_costs['consulting_services'] * 0.3 * years
                }
            },
            'patlib_solution_costs': {
                'initial_investment': self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs'],
                'annual_operating_costs': (self.patlib_costs['annual_maintenance'] + 
                                         self.patlib_costs['infrastructure'] + 
                                         self.patlib_costs['continuous_updates']),
                'total_cost_over_period': total_patlib_cost,
                'breakdown': {
                    'setup_and_training': self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs'],
                    'maintenance_and_infrastructure': (self.patlib_costs['annual_maintenance'] + 
                                                     self.patlib_costs['infrastructure']) * years,
                    'updates_and_improvements': self.patlib_costs['continuous_updates'] * years
                }
            },
            'savings_analysis': {
                'absolute_savings_euros': absolute_savings,
                'percentage_savings': savings_percentage,
                'annual_savings': absolute_savings / years,
                'monthly_savings': absolute_savings / (years * 12),
                'savings_category': 'EXCEPTIONAL' if savings_percentage > 80 else 'HIGH' if savings_percentage > 60 else 'MODERATE'
            },
            'value_enhancement': {
                'value_multiplier_applied': value_multiplier,
                'enhanced_solution_value': enhanced_value,
                'net_value_creation': net_value_creation,
                'total_economic_benefit': absolute_savings + net_value_creation
            }
        }
        
        print(f"✅ Cost savings: €{absolute_savings:,.0f} ({savings_percentage:.1f}% savings)")
        print(f"   Commercial cost: €{total_commercial_cost:,.0f}")
        print(f"   PATLIB cost: €{total_patlib_cost:,.0f}")
        print(f"   Enhanced value: €{enhanced_value:,.0f}")
        
        return cost_savings_analysis
    
    def generate_roi_scenarios(self, client_type: str = 'corporate_library') -> Dict:
        """
        Generate multiple ROI scenarios for different implementation approaches
        Provides risk-adjusted return calculations
        """
        print(f"📊 GENERATING ROI SCENARIOS - {client_type.upper()}")
        print("-" * 45)
        
        # Base cost savings
        base_analysis = self.calculate_cost_savings_analysis(client_type, 5)
        annual_savings = base_analysis['savings_analysis']['annual_savings']
        
        # Define scenarios
        scenarios = []
        
        # Conservative scenario
        conservative = ROIScenario(
            scenario_name="Conservative Implementation",
            initial_investment=self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs'],
            annual_savings=annual_savings * 0.7,  # 70% of projected savings
            implementation_time_months=6,
            payback_period_months=int((self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) / (annual_savings * 0.7 / 12)),
            five_year_roi_percent=((annual_savings * 0.7 * 5) / (self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) - 1) * 100,
            risk_level="LOW",
            confidence_level="HIGH"
        )
        scenarios.append(conservative)
        
        # Base case scenario
        base_case = ROIScenario(
            scenario_name="Base Case Implementation",
            initial_investment=self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs'],
            annual_savings=annual_savings,
            implementation_time_months=4,
            payback_period_months=int((self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) / (annual_savings / 12)),
            five_year_roi_percent=((annual_savings * 5) / (self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) - 1) * 100,
            risk_level="MODERATE",
            confidence_level="HIGH"
        )
        scenarios.append(base_case)
        
        # Optimistic scenario (with value enhancement)
        value_multiplier = self.value_multipliers.get(client_type, 1.0)
        enhanced_savings = annual_savings * value_multiplier
        
        optimistic = ROIScenario(
            scenario_name="Value-Enhanced Implementation",
            initial_investment=self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs'],
            annual_savings=enhanced_savings,
            implementation_time_months=3,
            payback_period_months=int((self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) / (enhanced_savings / 12)),
            five_year_roi_percent=((enhanced_savings * 5) / (self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) - 1) * 100,
            risk_level="MODERATE",
            confidence_level="MODERATE"
        )
        scenarios.append(optimistic)
        
        # Enterprise scenario (full consulting replacement)
        enterprise_savings = annual_savings + (self.commercial_costs['consulting_services'] * 0.7)
        enterprise_investment = (self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']) * 2
        
        enterprise = ROIScenario(
            scenario_name="Enterprise Consulting Replacement",
            initial_investment=enterprise_investment,
            annual_savings=enterprise_savings,
            implementation_time_months=8,
            payback_period_months=int(enterprise_investment / (enterprise_savings / 12)),
            five_year_roi_percent=((enterprise_savings * 5) / enterprise_investment - 1) * 100,
            risk_level="HIGH",
            confidence_level="MODERATE"
        )
        scenarios.append(enterprise)
        
        # Scenario comparison analysis
        scenario_comparison = {
            'scenarios': [scenario.__dict__ for scenario in scenarios],
            'best_payback_period': min(scenarios, key=lambda x: x.payback_period_months).scenario_name,
            'highest_roi': max(scenarios, key=lambda x: x.five_year_roi_percent).scenario_name,
            'lowest_risk': min(scenarios, key=lambda x: {'LOW': 1, 'MODERATE': 2, 'HIGH': 3}[x.risk_level]).scenario_name,
            'recommended_scenario': self._recommend_scenario(scenarios, client_type)
        }
        
        print(f"✅ ROI scenarios generated: {len(scenarios)} scenarios")
        print(f"   Best payback: {scenario_comparison['best_payback_period']}")
        print(f"   Highest ROI: {scenario_comparison['highest_roi']}")
        print(f"   Recommended: {scenario_comparison['recommended_scenario']}")
        
        return scenario_comparison
    
    def create_business_case_presentation(self, client_type: str = 'corporate_library') -> Dict:
        """
        Create comprehensive business case presentation materials
        Executive-ready financial justification
        """
        print(f"📋 CREATING BUSINESS CASE PRESENTATION - {client_type.upper()}")
        print("-" * 55)
        
        # Get comprehensive analysis
        cost_analysis = self.calculate_cost_savings_analysis(client_type, 5)
        roi_scenarios = self.generate_roi_scenarios(client_type)
        
        # Executive summary for business case
        executive_summary = {
            'financial_opportunity': f"€{cost_analysis['savings_analysis']['absolute_savings_euros']:,.0f} savings over 5 years",
            'percentage_savings': f"{cost_analysis['savings_analysis']['percentage_savings']:.1f}% cost reduction",
            'payback_period': f"{min([s['payback_period_months'] for s in roi_scenarios['scenarios']])} months",
            'five_year_roi': f"{max([s['five_year_roi_percent'] for s in roi_scenarios['scenarios']]):.0f}% return on investment",
            'risk_assessment': 'LOW to MODERATE implementation risk',
            'strategic_value': 'Unique patent-market correlation capabilities unavailable elsewhere',
            'competitive_advantage': 'Government-grade data authority (USGS + EPO) at fraction of commercial cost'
        }
        
        # Key value propositions
        value_propositions = [
            {
                'proposition': 'Exceptional Cost Savings',
                'description': f"90%+ cost reduction vs. commercial databases (€{cost_analysis['commercial_solution_costs']['total_cost_over_period']:,.0f} → €{cost_analysis['patlib_solution_costs']['total_cost_over_period']:,.0f})",
                'quantified_benefit': f"€{cost_analysis['savings_analysis']['absolute_savings_euros']:,.0f} saved over 5 years"
            },
            {
                'proposition': 'Unique Market Intelligence',
                'description': 'Patent-market correlation analysis unavailable in commercial tools',
                'quantified_benefit': 'Competitive advantage in strategic planning and risk assessment'
            },
            {
                'proposition': 'Government-Grade Data Authority',
                'description': 'USGS + EPO official data sources provide unmatched credibility',
                'quantified_benefit': 'Enhanced stakeholder confidence and decision-making authority'
            },
            {
                'proposition': 'Rapid Implementation',
                'description': f"Deployment in {min([s['implementation_time_months'] for s in roi_scenarios['scenarios']])} months with immediate value delivery",
                'quantified_benefit': f"Break-even achieved in {min([s['payback_period_months'] for s in roi_scenarios['scenarios']])} months"
            },
            {
                'proposition': 'Scalable Platform',
                'description': 'Technology-agnostic system adaptable to any domain beyond REE',
                'quantified_benefit': 'Future expansion opportunities without additional licensing costs'
            }
        ]
        
        # Implementation roadmap for business case
        implementation_roadmap = [
            {
                'milestone': 'Business Case Approval',
                'duration': '2-4 weeks',
                'activities': ['Stakeholder presentations', 'Budget approval', 'Team formation'],
                'investment': '€0',
                'deliverables': ['Approved budget', 'Project team', 'Implementation plan']
            },
            {
                'milestone': 'System Setup and Training',
                'duration': '4-8 weeks',
                'activities': ['Infrastructure setup', 'Staff training', 'Initial data integration'],
                'investment': f"€{self.patlib_costs['initial_setup'] + self.patlib_costs['training_costs']:,}",
                'deliverables': ['Operational system', 'Trained staff', 'Initial analysis capability']
            },
            {
                'milestone': 'Pilot Analysis and Validation',
                'duration': '4-6 weeks',
                'activities': ['Pilot projects', 'Result validation', 'Process optimization'],
                'investment': '€2,000',
                'deliverables': ['Validated results', 'Optimized processes', 'User feedback']
            },
            {
                'milestone': 'Full Deployment',
                'duration': '2-4 weeks',
                'activities': ['System scaling', 'User onboarding', 'Performance monitoring'],
                'investment': '€1,000',
                'deliverables': ['Full capability', 'User adoption', 'Performance metrics']
            }
        ]
        
        # Risk mitigation strategies
        risk_mitigation = {
            'technical_risks': {
                'data_integration_challenges': 'Proven API connections and data validation procedures',
                'system_performance_issues': 'Scalable cloud infrastructure and performance monitoring',
                'user_adoption_barriers': 'Comprehensive training and change management support'
            },
            'financial_risks': {
                'cost_overruns': 'Fixed-price implementation with transparent cost structure',
                'lower_than_expected_savings': 'Conservative savings estimates with upside potential',
                'hidden_costs': 'All-inclusive pricing with no licensing surprises'
            },
            'operational_risks': {
                'staff_capacity_limitations': 'Efficient automated processes requiring minimal manual intervention',
                'knowledge_transfer_gaps': 'Comprehensive documentation and training materials',
                'system_maintenance_burden': 'Automated updates and minimal maintenance requirements'
            }
        }
        
        # Financial projections
        financial_projections = self._create_financial_projections(cost_analysis, 5)
        
        business_case = {
            'executive_summary': executive_summary,
            'value_propositions': value_propositions,
            'cost_savings_analysis': cost_analysis,
            'roi_scenarios': roi_scenarios,
            'implementation_roadmap': implementation_roadmap,
            'risk_mitigation': risk_mitigation,
            'financial_projections': financial_projections,
            'recommendation': {
                'recommended_approach': roi_scenarios['recommended_scenario'],
                'key_success_factors': [
                    'Executive sponsorship and stakeholder buy-in',
                    'Dedicated project team with clear accountability',
                    'Phased implementation with early wins demonstration',
                    'Continuous value measurement and optimization'
                ],
                'next_steps': [
                    'Secure executive approval and budget allocation',
                    'Form implementation team and assign project manager',
                    'Begin vendor evaluation and contract negotiation',
                    'Schedule stakeholder briefings and communication plan'
                ]
            },
            'presentation_metadata': {
                'client_type': client_type,
                'analysis_date': datetime.now().isoformat(),
                'validity_period': '12 months',
                'contact_information': 'PATLIB consulting team'
            }
        }
        
        print(f"✅ Business case presentation created")
        print(f"   Value propositions: {len(value_propositions)}")
        print(f"   Implementation milestones: {len(implementation_roadmap)}")
        print(f"   Financial projections: {len(financial_projections['annual_projections'])} years")
        
        return business_case
    
    def _recommend_scenario(self, scenarios: List[ROIScenario], client_type: str) -> str:
        """Recommend best scenario based on client type and risk profile"""
        client_preferences = {
            'university_library': 'conservative',  # Budget-conscious, risk-averse
            'corporate_library': 'base_case',      # Balanced approach
            'sme_manufacturing': 'optimistic',     # Value-focused, growth-oriented
            'consulting_firm': 'enterprise',       # Revenue-focused, high capability
            'government_agency': 'conservative'    # Risk-averse, budget-conscious
        }
        
        preference = client_preferences.get(client_type, 'base_case')
        
        recommendation_map = {
            'conservative': scenarios[0].scenario_name,  # Conservative
            'base_case': scenarios[1].scenario_name,     # Base case
            'optimistic': scenarios[2].scenario_name,    # Value-enhanced
            'enterprise': scenarios[3].scenario_name     # Enterprise
        }
        
        return recommendation_map.get(preference, scenarios[1].scenario_name)
    
    def _create_financial_projections(self, cost_analysis: Dict, years: int) -> Dict:
        """Create detailed financial projections"""
        annual_savings = cost_analysis['savings_analysis']['annual_savings']
        annual_costs = cost_analysis['patlib_solution_costs']['annual_operating_costs']
        
        projections = {
            'annual_projections': [],
            'cumulative_savings': [],
            'break_even_analysis': {}
        }
        
        cumulative_savings = 0
        initial_investment = cost_analysis['patlib_solution_costs']['breakdown']['setup_and_training']
        
        for year in range(1, years + 1):
            annual_net_savings = annual_savings - annual_costs
            cumulative_savings += annual_net_savings
            
            projections['annual_projections'].append({
                'year': year,
                'annual_savings': annual_savings,
                'annual_costs': annual_costs,
                'net_annual_benefit': annual_net_savings,
                'cumulative_net_benefit': cumulative_savings,
                'roi_to_date': ((cumulative_savings / initial_investment) * 100) if initial_investment > 0 else 0
            })
        
        # Break-even analysis
        monthly_net_savings = annual_net_savings / 12
        break_even_months = int(initial_investment / monthly_net_savings) if monthly_net_savings > 0 else 999
        
        projections['break_even_analysis'] = {
            'break_even_months': break_even_months,
            'break_even_date': (datetime.now() + timedelta(days=break_even_months * 30)).strftime('%Y-%m-%d'),
            'monthly_net_savings': monthly_net_savings,
            'total_five_year_benefit': cumulative_savings
        }
        
        return projections
    
    def create_roi_visualization(self, business_case: Dict) -> go.Figure:
        """Create interactive ROI visualization for presentations"""
        print("📊 Creating ROI visualization...")
        
        # Extract financial projections
        projections = business_case['financial_projections']['annual_projections']
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Cumulative Savings vs Investment', 'Annual ROI Progression', 
                           'Cost Comparison', 'Scenario Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Cumulative savings chart
        years = [p['year'] for p in projections]
        cumulative_benefits = [p['cumulative_net_benefit'] for p in projections]
        
        fig.add_trace(
            go.Scatter(x=years, y=cumulative_benefits, mode='lines+markers',
                      name='Cumulative Savings', line=dict(color='green', width=3)),
            row=1, col=1
        )
        
        # Annual ROI progression
        annual_roi = [p['roi_to_date'] for p in projections]
        fig.add_trace(
            go.Scatter(x=years, y=annual_roi, mode='lines+markers',
                      name='ROI %', line=dict(color='blue', width=3)),
            row=1, col=2
        )
        
        # Cost comparison
        commercial_cost = business_case['cost_savings_analysis']['commercial_solution_costs']['total_cost_over_period']
        patlib_cost = business_case['cost_savings_analysis']['patlib_solution_costs']['total_cost_over_period']
        
        fig.add_trace(
            go.Bar(x=['Commercial Solution', 'PATLIB Solution'], 
                   y=[commercial_cost, patlib_cost],
                   name='5-Year Costs', marker_color=['red', 'green']),
            row=2, col=1
        )
        
        # Scenario analysis
        scenarios = business_case['roi_scenarios']['scenarios']
        scenario_names = [s['scenario_name'] for s in scenarios]
        scenario_rois = [s['five_year_roi_percent'] for s in scenarios]
        
        fig.add_trace(
            go.Bar(x=scenario_names, y=scenario_rois,
                   name='5-Year ROI %', marker_color='orange'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text="PATLIB ROI Analysis Dashboard",
            height=700,
            showlegend=True
        )
        
        print("✅ ROI visualization created")
        return fig

def test_roi_calculator():
    """Test ROI calculator functionality"""
    print("🧪 Testing ROI Calculator...")
    
    calculator = ROICalculator()
    
    # Test cost savings analysis
    print("\n💰 Testing cost savings analysis...")
    cost_analysis = calculator.calculate_cost_savings_analysis('corporate_library', 5)
    print(f"✅ Cost savings: €{cost_analysis['savings_analysis']['absolute_savings_euros']:,.0f}")
    
    # Test ROI scenarios
    print("\n📊 Testing ROI scenarios...")
    roi_scenarios = calculator.generate_roi_scenarios('corporate_library')
    print(f"✅ ROI scenarios: {len(roi_scenarios['scenarios'])} scenarios generated")
    
    # Test business case
    print("\n📋 Testing business case presentation...")
    business_case = calculator.create_business_case_presentation('corporate_library')
    print(f"✅ Business case: {len(business_case['value_propositions'])} value propositions")
    
    # Test visualization
    print("\n📊 Testing ROI visualization...")
    roi_viz = calculator.create_roi_visualization(business_case)
    print(f"✅ ROI visualization: Interactive dashboard created")
    
    return {
        'cost_analysis': cost_analysis,
        'roi_scenarios': roi_scenarios,
        'business_case': business_case,
        'roi_visualization': roi_viz
    }

if __name__ == "__main__":
    test_results = test_roi_calculator()
    print(f"\n🎉 ROI Calculator test complete!")