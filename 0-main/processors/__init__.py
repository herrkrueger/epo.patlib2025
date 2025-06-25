"""
Processors Module for REE Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides specialized processors for different aspects of patent data analysis:
- Applicant analysis and market intelligence
- Geographic analysis and international filing patterns  
- Classification analysis and technology networks
"""

from .applicant import ApplicantAnalyzer, ApplicantDataProcessor, create_applicant_analyzer, create_applicant_processor
from .geographic import GeographicAnalyzer, GeographicDataProcessor, create_geographic_analyzer, create_geographic_processor
from .classification import ClassificationAnalyzer, ClassificationDataProcessor, create_classification_analyzer, create_classification_processor

__version__ = "1.0.0"

__all__ = [
    # Applicant processing
    'ApplicantAnalyzer',
    'ApplicantDataProcessor', 
    'create_applicant_analyzer',
    'create_applicant_processor',
    
    # Geographic processing
    'GeographicAnalyzer',
    'GeographicDataProcessor',
    'create_geographic_analyzer', 
    'create_geographic_processor',
    
    # Classification processing
    'ClassificationAnalyzer',
    'ClassificationDataProcessor',
    'create_classification_analyzer',
    'create_classification_processor'
]

# Quick setup functions for integrated workflows
def setup_complete_analysis_pipeline():
    """
    Setup complete analysis pipeline with all processors.
    
    Returns:
        Dictionary with all configured processor instances
    """
    return {
        'applicant_analyzer': create_applicant_analyzer(),
        'applicant_processor': create_applicant_processor(),
        'geographic_analyzer': create_geographic_analyzer(),
        'geographic_processor': create_geographic_processor(),
        'classification_analyzer': create_classification_analyzer(),
        'classification_processor': create_classification_processor()
    }

def analyze_patent_dataset(patent_data, analysis_type='all'):
    """
    Convenience function to analyze patent dataset with multiple processors.
    
    Args:
        patent_data: Patent data (format depends on analysis_type)
        analysis_type: Type of analysis ('applicant', 'geographic', 'classification', 'all')
        
    Returns:
        Dictionary with analysis results
    """
    results = {}
    
    if analysis_type in ['applicant', 'all']:
        try:
            applicant_analyzer = create_applicant_analyzer()
            applicant_processor = create_applicant_processor()
            
            if isinstance(patent_data, list):
                processed_data = applicant_processor.process_patstat_applicant_data(patent_data)
            else:
                processed_data = patent_data
                
            analyzed_data = applicant_analyzer.analyze_applicants(processed_data)
            summary = applicant_analyzer.generate_market_intelligence_summary()
            
            results['applicant'] = {
                'analyzed_data': analyzed_data,
                'summary': summary,
                'analyzer': applicant_analyzer
            }
        except Exception as e:
            results['applicant'] = {'error': str(e)}
    
    if analysis_type in ['geographic', 'all']:
        try:
            geographic_analyzer = create_geographic_analyzer()
            geographic_processor = create_geographic_processor()
            
            if isinstance(patent_data, list):
                processed_data = geographic_processor.process_patstat_geographic_data(patent_data)
            else:
                processed_data = patent_data
                
            analyzed_data = geographic_analyzer.analyze_geographic_patterns(processed_data)
            summary = geographic_analyzer.generate_geographic_summary()
            
            results['geographic'] = {
                'analyzed_data': analyzed_data,
                'summary': summary,
                'analyzer': geographic_analyzer
            }
        except Exception as e:
            results['geographic'] = {'error': str(e)}
    
    if analysis_type in ['classification', 'all']:
        try:
            classification_analyzer = create_classification_analyzer()
            classification_processor = create_classification_processor()
            
            if isinstance(patent_data, list):
                processed_data = classification_processor.process_patstat_classification_data(patent_data)
            else:
                processed_data = patent_data
                
            analyzed_data = classification_analyzer.analyze_classification_patterns(processed_data)
            network = classification_analyzer.build_classification_network(analyzed_data)
            intelligence = classification_analyzer.generate_classification_intelligence()
            
            results['classification'] = {
                'analyzed_data': analyzed_data,
                'network': network,
                'intelligence': intelligence,
                'analyzer': classification_analyzer
            }
        except Exception as e:
            results['classification'] = {'error': str(e)}
    
    return results

# Analysis workflow templates
class AnalysisWorkflow:
    """
    Integrated analysis workflow for comprehensive patent intelligence.
    """
    
    def __init__(self):
        """Initialize analysis workflow with all processors."""
        self.processors = setup_complete_analysis_pipeline()
        self.results = {}
    
    def run_applicant_analysis(self, applicant_data):
        """Run comprehensive applicant analysis."""
        processor = self.processors['applicant_processor']
        analyzer = self.processors['applicant_analyzer']
        
        if isinstance(applicant_data, list):
            processed_data = processor.process_patstat_applicant_data(applicant_data)
        else:
            processed_data = applicant_data
        
        analyzed_data = analyzer.analyze_applicants(processed_data)
        summary = analyzer.generate_market_intelligence_summary()
        landscape = analyzer.get_competitive_landscape()
        
        self.results['applicant'] = {
            'data': analyzed_data,
            'summary': summary,
            'landscape': landscape
        }
        
        return self.results['applicant']
    
    def run_geographic_analysis(self, geographic_data):
        """Run comprehensive geographic analysis."""
        processor = self.processors['geographic_processor']
        analyzer = self.processors['geographic_analyzer']
        
        if isinstance(geographic_data, list):
            processed_data = processor.process_patstat_geographic_data(geographic_data)
        else:
            processed_data = geographic_data
        
        analyzed_data = analyzer.analyze_geographic_patterns(processed_data)
        summary = analyzer.generate_geographic_summary()
        landscape = analyzer.get_competitive_landscape_by_region()
        evolution = analyzer.analyze_filing_evolution()
        
        self.results['geographic'] = {
            'data': analyzed_data,
            'summary': summary,
            'landscape': landscape,
            'evolution': evolution
        }
        
        return self.results['geographic']
    
    def run_classification_analysis(self, classification_data):
        """Run comprehensive classification analysis."""
        processor = self.processors['classification_processor']
        analyzer = self.processors['classification_analyzer']
        
        if isinstance(classification_data, list):
            processed_data = processor.process_patstat_classification_data(classification_data)
        else:
            processed_data = classification_data
        
        analyzed_data = analyzer.analyze_classification_patterns(processed_data)
        network = analyzer.build_classification_network(analyzed_data)
        intelligence = analyzer.generate_classification_intelligence()
        hotspots = analyzer.get_innovation_hotspots()
        
        self.results['classification'] = {
            'data': analyzed_data,
            'network': network,
            'intelligence': intelligence,
            'hotspots': hotspots
        }
        
        return self.results['classification']
    
    def generate_integrated_report(self):
        """Generate integrated report combining all analysis results."""
        if not self.results:
            raise ValueError("No analysis results available. Run analyses first.")
        
        integrated_report = {
            'executive_summary': {},
            'detailed_findings': self.results,
            'cross_analysis_insights': {},
            'recommendations': []
        }
        
        # Generate cross-analysis insights
        if 'applicant' in self.results and 'geographic' in self.results:
            # Cross-reference top applicants with geographic distribution
            integrated_report['cross_analysis_insights']['applicant_geographic'] = {
                'description': 'Analysis of top applicants by geographic distribution',
                'status': 'Data available for cross-analysis'
            }
        
        if 'classification' in self.results:
            # Technology domain insights
            integrated_report['cross_analysis_insights']['technology_domains'] = {
                'description': 'Technology domain analysis with innovation networks',
                'status': 'Network analysis available'
            }
        
        # Generate high-level recommendations
        integrated_report['recommendations'] = [
            'Monitor cross-domain innovation patterns for emerging technologies',
            'Track geographic shifts in patent filing strategies',
            'Analyze competitive positioning in key technology domains',
            'Investigate patent family size trends for strategic insights'
        ]
        
        return integrated_report
    
    def get_results_summary(self):
        """Get high-level summary of all analysis results."""
        summary = {}
        
        for analysis_type, results in self.results.items():
            if 'summary' in results:
                summary[analysis_type] = results['summary']['overview'] if 'overview' in results['summary'] else results['summary']
        
        return summary