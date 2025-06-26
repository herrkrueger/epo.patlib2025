"""
Analyzers Module for REE Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides high-level analyzers that combine multiple data processing
capabilities to generate comprehensive patent intelligence insights:
- Regional competitive analysis and market dynamics
- Technology landscape analysis and innovation networks
- Temporal trends analysis and predictive forecasting
"""

from .regional import RegionalAnalyzer, create_regional_analyzer
from .technology import TechnologyAnalyzer, create_technology_analyzer  
from .trends import TrendsAnalyzer, create_trends_analyzer

__version__ = "1.0.0"

__all__ = [
    # Regional analysis
    'RegionalAnalyzer',
    'create_regional_analyzer',
    
    # Technology analysis
    'TechnologyAnalyzer', 
    'create_technology_analyzer',
    
    # Trends analysis
    'TrendsAnalyzer',
    'create_trends_analyzer'
]

# Integrated analysis workflows
def setup_complete_analysis_suite():
    """
    Setup complete analysis suite with all analyzers.
    
    Returns:
        Dictionary with all configured analyzer instances
    """
    return {
        'regional_analyzer': create_regional_analyzer(),
        'technology_analyzer': create_technology_analyzer(),
        'trends_analyzer': create_trends_analyzer()
    }

def run_comprehensive_intelligence_analysis(patent_data, analysis_config=None):
    """
    Run comprehensive patent intelligence analysis across all dimensions.
    
    Args:
        patent_data: Patent dataset (DataFrame or dictionary with different data types)
        analysis_config: Configuration for analysis parameters
        
    Returns:
        Dictionary with comprehensive intelligence results
    """
    if analysis_config is None:
        analysis_config = {
            'regional_analysis': True,
            'technology_analysis': True,
            'trends_analysis': True,
            'cross_analysis': True
        }
    
    results = {
        'analysis_metadata': {
            'timestamp': pd.Timestamp.now().isoformat(),
            'data_records': len(patent_data) if hasattr(patent_data, '__len__') else 'Unknown',
            'analysis_scope': list(analysis_config.keys())
        },
        'intelligence_reports': {},
        'cross_dimensional_insights': {},
        'strategic_synthesis': {}
    }
    
    # Initialize analyzers
    analyzers = setup_complete_analysis_suite()
    
    try:
        # Regional analysis
        if analysis_config.get('regional_analysis', True):
            regional_analyzer = analyzers['regional_analyzer']
            
            if 'regional_data' in patent_data:
                regional_df = regional_analyzer.analyze_regional_dynamics(patent_data['regional_data'])
                regional_intelligence = regional_analyzer.generate_regional_intelligence_report()
                competitive_matrix = regional_analyzer.create_competitive_matrix()
                
                results['intelligence_reports']['regional'] = {
                    'intelligence_report': regional_intelligence,
                    'competitive_matrix': competitive_matrix.to_dict('index') if competitive_matrix is not None else {},
                    'analysis_status': 'Complete'
                }
            else:
                results['intelligence_reports']['regional'] = {'analysis_status': 'Skipped - No regional data'}
        
        # Technology analysis
        if analysis_config.get('technology_analysis', True):
            technology_analyzer = analyzers['technology_analyzer']
            
            if 'technology_data' in patent_data:
                tech_df = technology_analyzer.analyze_technology_landscape(patent_data['technology_data'])
                tech_network = technology_analyzer.build_technology_network(tech_df)
                tech_intelligence = technology_analyzer.generate_technology_intelligence()
                innovation_opportunities = technology_analyzer.identify_innovation_opportunities()
                
                results['intelligence_reports']['technology'] = {
                    'intelligence_report': tech_intelligence,
                    'network_metrics': {
                        'nodes': tech_network.number_of_nodes(),
                        'edges': tech_network.number_of_edges(),
                        'density': nx.density(tech_network) if tech_network.number_of_nodes() > 0 else 0
                    } if tech_network else {},
                    'innovation_opportunities': innovation_opportunities,
                    'analysis_status': 'Complete'
                }
            else:
                results['intelligence_reports']['technology'] = {'analysis_status': 'Skipped - No technology data'}
        
        # Trends analysis
        if analysis_config.get('trends_analysis', True):
            trends_analyzer = analyzers['trends_analyzer']
            
            if 'temporal_data' in patent_data:
                trends_df = trends_analyzer.analyze_temporal_trends(patent_data['temporal_data'])
                trends_intelligence = trends_analyzer.generate_trends_intelligence_report()
                cycles_analysis = trends_analyzer.analyze_innovation_cycles()
                
                results['intelligence_reports']['trends'] = {
                    'intelligence_report': trends_intelligence,
                    'innovation_cycles': cycles_analysis,
                    'forecasting_data': trends_analyzer.predictions,
                    'analysis_status': 'Complete'
                }
            else:
                results['intelligence_reports']['trends'] = {'analysis_status': 'Skipped - No temporal data'}
        
        # Cross-dimensional analysis
        if analysis_config.get('cross_analysis', True):
            cross_insights = generate_cross_dimensional_insights(results['intelligence_reports'])
            results['cross_dimensional_insights'] = cross_insights
        
        # Strategic synthesis
        strategic_synthesis = generate_strategic_synthesis(results)
        results['strategic_synthesis'] = strategic_synthesis
        
        results['analysis_metadata']['completion_status'] = 'Success'
        
    except Exception as e:
        results['analysis_metadata']['completion_status'] = 'Error'
        results['analysis_metadata']['error_message'] = str(e)
        logger.error(f"❌ Comprehensive analysis failed: {e}")
    
    return results

def generate_cross_dimensional_insights(intelligence_reports):
    """
    Generate insights from cross-dimensional analysis.
    
    Args:
        intelligence_reports: Dictionary with intelligence reports from different analyzers
        
    Returns:
        Dictionary with cross-dimensional insights
    """
    cross_insights = {
        'regional_technology_convergence': {},
        'temporal_regional_dynamics': {},
        'technology_lifecycle_regional_patterns': {},
        'integrated_competitive_landscape': {}
    }
    
    # Regional-Technology convergence
    if ('regional' in intelligence_reports and 'technology' in intelligence_reports and
        intelligence_reports['regional']['analysis_status'] == 'Complete' and
        intelligence_reports['technology']['analysis_status'] == 'Complete'):
        
        regional_leaders = intelligence_reports['regional']['intelligence_report']['executive_summary']
        tech_leaders = intelligence_reports['technology']['intelligence_report']['executive_summary']
        
        cross_insights['regional_technology_convergence'] = {
            'dominant_region': regional_leaders.get('market_leader', 'N/A'),
            'dominant_technology': tech_leaders.get('dominant_area', 'N/A'),
            'convergence_opportunity': 'High' if regional_leaders.get('emerging_regions', 0) > 0 and tech_leaders.get('emerging_technologies', 0) > 0 else 'Moderate',
            'strategic_alignment': 'Analyze alignment between leading regions and emerging technologies'
        }
    
    # Temporal-Regional dynamics
    if ('trends' in intelligence_reports and 'regional' in intelligence_reports and
        intelligence_reports['trends']['analysis_status'] == 'Complete' and
        intelligence_reports['regional']['analysis_status'] == 'Complete'):
        
        market_momentum = intelligence_reports['trends']['intelligence_report']['executive_summary']['market_momentum']
        regional_competition = intelligence_reports['regional']['intelligence_report']['competitive_landscape']
        
        cross_insights['temporal_regional_dynamics'] = {
            'market_momentum': market_momentum,
            'regional_competitive_intensity': len(regional_competition.get('competitive_tiers', {})),
            'dynamic_assessment': f"Market showing {market_momentum.lower()} with active regional competition",
            'strategic_timing': 'Optimal' if market_momentum in ['Strong Growth', 'Moderate Growth'] else 'Cautious'
        }
    
    return cross_insights

def generate_strategic_synthesis(analysis_results):
    """
    Generate strategic synthesis from all analysis results.
    
    Args:
        analysis_results: Complete analysis results dictionary
        
    Returns:
        Dictionary with strategic synthesis
    """
    synthesis = {
        'executive_overview': {},
        'key_findings': [],
        'strategic_priorities': [],
        'recommended_actions': [],
        'risk_assessment': {}
    }
    
    # Executive overview
    completed_analyses = [
        analysis for analysis, report in analysis_results['intelligence_reports'].items()
        if report.get('analysis_status') == 'Complete'
    ]
    
    synthesis['executive_overview'] = {
        'analysis_scope': completed_analyses,
        'data_coverage': f"{len(completed_analyses)} dimensional analysis",
        'intelligence_confidence': 'High' if len(completed_analyses) >= 3 else 'Moderate',
        'strategic_readiness': 'Ready for decision making' if len(completed_analyses) >= 2 else 'Requires additional data'
    }
    
    # Key findings compilation
    for analysis_type, report in analysis_results['intelligence_reports'].items():
        if report.get('analysis_status') == 'Complete' and 'intelligence_report' in report:
            exec_summary = report['intelligence_report'].get('executive_summary', {})
            
            if analysis_type == 'regional':
                synthesis['key_findings'].append(f"Regional Leadership: {exec_summary.get('market_leader', 'Unknown')} dominates with {exec_summary.get('leader_share', 0):.1f}% market share")
            
            elif analysis_type == 'technology':
                synthesis['key_findings'].append(f"Technology Focus: {exec_summary.get('dominant_area', 'Unknown')} leads with {exec_summary.get('emerging_technologies', 0)} emerging technologies")
            
            elif analysis_type == 'trends':
                synthesis['key_findings'].append(f"Market Dynamics: {exec_summary.get('market_momentum', 'Unknown')} momentum with {exec_summary.get('yoy_growth', 0):.1f}% YoY growth")
    
    # Strategic priorities
    if analysis_results['cross_dimensional_insights']:
        cross_insights = analysis_results['cross_dimensional_insights']
        
        if 'regional_technology_convergence' in cross_insights:
            convergence = cross_insights['regional_technology_convergence']
            if convergence.get('convergence_opportunity') == 'High':
                synthesis['strategic_priorities'].append('Capitalize on regional-technology convergence opportunities')
        
        if 'temporal_regional_dynamics' in cross_insights:
            dynamics = cross_insights['temporal_regional_dynamics']
            if dynamics.get('strategic_timing') == 'Optimal':
                synthesis['strategic_priorities'].append('Market timing favorable for strategic initiatives')
    
    # Recommended actions
    synthesis['recommended_actions'] = [
        'Monitor leading regions for competitive intelligence',
        'Track emerging technologies for innovation opportunities',
        'Analyze market timing for strategic investments',
        'Develop cross-dimensional strategy alignment'
    ]
    
    # Risk assessment
    synthesis['risk_assessment'] = {
        'data_completeness': 'High' if len(completed_analyses) >= 3 else 'Medium',
        'market_volatility': 'Monitor trends analysis for volatility indicators',
        'competitive_pressure': 'Assess regional competitive landscape',
        'technology_disruption': 'Track emerging technology indicators'
    }
    
    return synthesis

class IntegratedPatentIntelligence:
    """
    Integrated patent intelligence platform combining all analyzers.
    """
    
    def __init__(self):
        """Initialize integrated intelligence platform."""
        self.analyzers = setup_complete_analysis_suite()
        self.results_cache = {}
        self.analysis_history = []
    
    def run_full_intelligence_analysis(self, data_sources, analysis_scope='full'):
        """
        Run comprehensive intelligence analysis.
        
        Args:
            data_sources: Dictionary with different data types
            analysis_scope: Scope of analysis ('full', 'quick', 'custom')
            
        Returns:
            Comprehensive intelligence results
        """
        import pandas as pd
        
        logger.debug(f"🚀 Starting {analysis_scope} intelligence analysis...")
        
        analysis_config = self._get_analysis_config(analysis_scope)
        results = run_comprehensive_intelligence_analysis(data_sources, analysis_config)
        
        # Cache results
        analysis_id = f"analysis_{len(self.analysis_history) + 1}"
        self.results_cache[analysis_id] = results
        self.analysis_history.append({
            'id': analysis_id,
            'timestamp': pd.Timestamp.now(),
            'scope': analysis_scope,
            'status': results['analysis_metadata']['completion_status']
        })
        
        logger.debug(f"✅ Intelligence analysis complete - ID: {analysis_id}")
        return results
    
    def _get_analysis_config(self, scope):
        """Get analysis configuration based on scope."""
        configs = {
            'full': {
                'regional_analysis': True,
                'technology_analysis': True,
                'trends_analysis': True,
                'cross_analysis': True
            },
            'quick': {
                'regional_analysis': True,
                'technology_analysis': False,
                'trends_analysis': True,
                'cross_analysis': False
            },
            'custom': {
                'regional_analysis': True,
                'technology_analysis': True,
                'trends_analysis': False,
                'cross_analysis': True
            }
        }
        return configs.get(scope, configs['full'])
    
    def get_analysis_summary(self, analysis_id=None):
        """Get summary of analysis results."""
        if analysis_id is None:
            analysis_id = self.analysis_history[-1]['id'] if self.analysis_history else None
        
        if analysis_id not in self.results_cache:
            return {'error': 'Analysis not found'}
        
        results = self.results_cache[analysis_id]
        return results['strategic_synthesis']['executive_overview']
    
    def export_intelligence_report(self, analysis_id=None, format='dict'):
        """Export intelligence report in specified format."""
        if analysis_id is None:
            analysis_id = self.analysis_history[-1]['id'] if self.analysis_history else None
        
        if analysis_id not in self.results_cache:
            return {'error': 'Analysis not found'}
        
        results = self.results_cache[analysis_id]
        
        if format == 'summary':
            return results['strategic_synthesis']
        elif format == 'detailed':
            return results['intelligence_reports']
        else:
            return results

# Convenience functions
def create_integrated_intelligence_platform():
    """Create configured integrated intelligence platform."""
    return IntegratedPatentIntelligence()

# For backwards compatibility
import networkx as nx
import pandas as pd