"""
Data Processing Module for Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive patent data processing capabilities including
search functionality, applicant analysis, classification intelligence, geographic patterns, and citation analysis.
"""

import pandas as pd

from .search import PatentSearchProcessor, create_patent_search_processor
from .applicant import ApplicantAnalyzer, create_applicant_analyzer
from .classification import ClassificationAnalyzer, create_classification_analyzer
from .geographic import GeographicAnalyzer, create_geographic_analyzer
from .citation import CitationAnalyzer, create_citation_analyzer

__version__ = "1.0.0"

__all__ = [
    # Patent Search (Foundation)
    'PatentSearchProcessor',
    'create_patent_search_processor',
    
    # Applicant Analysis
    'ApplicantAnalyzer',
    'create_applicant_analyzer',
    
    # Classification Analysis
    'ClassificationAnalyzer',
    'create_classification_analyzer',
    
    # Geographic Analysis
    'GeographicAnalyzer',
    'create_geographic_analyzer',
    
    # Citation Analysis
    'CitationAnalyzer',
    'create_citation_analyzer'
]

# Unified processor setup functions
def setup_full_processing_pipeline():
    """
    Setup complete processing pipeline with search processor as foundation plus all enhancement processors.
    
    Returns:
        Dictionary with all configured processors
    """
    return {
        'search_processor': create_patent_search_processor(),
        'applicant_analyzer': create_applicant_analyzer(),
        'classification_analyzer': create_classification_analyzer(),
        'geographic_analyzer': create_geographic_analyzer(),
        'citation_analyzer': create_citation_analyzer()
    }

def create_analysis_pipeline():
    """
    Create analysis pipeline (search processor + analyzers).
    
    Returns:
        Dictionary with analysis components
    """
    return {
        'search_processor': create_patent_search_processor(),
        'applicant_analyzer': create_applicant_analyzer(),
        'classification_analyzer': create_classification_analyzer(),
        'geographic_analyzer': create_geographic_analyzer(),
        'citation_analyzer': create_citation_analyzer()
    }

# Comprehensive analysis workflow for the new refactored processors
class ComprehensiveAnalysisWorkflow:
    """
    Integrated analysis workflow for comprehensive patent intelligence across all dimensions.
    
    This workflow uses the refactored processors that work with PatentSearchProcessor results.
    """
    
    def __init__(self, patstat_client=None):
        """Initialize comprehensive analysis workflow with all processors."""
        self.processors = {
            'search_processor': create_patent_search_processor(),
            'applicant_analyzer': create_applicant_analyzer(patstat_client),
            'classification_analyzer': create_classification_analyzer(patstat_client),
            'geographic_analyzer': create_geographic_analyzer(patstat_client),
            'citation_analyzer': create_citation_analyzer(patstat_client)
        }
        self.search_results = None
        self.analysis_results = {}
    
    def run_patent_search(self, keywords=None, technology_areas=None, date_range=None, 
                         quality_mode='intersection', max_results=None):
        """
        Run patent family search using PatentSearchProcessor.
        
        Args:
            keywords: List of keywords to search for
            technology_areas: List of technology areas from config
            date_range: Tuple of (start_date, end_date)
            quality_mode: Search quality mode ('intersection', 'union', etc.)
            max_results: Maximum number of results to return
            
        Returns:
            Search results DataFrame
        """
        search_processor = self.processors['search_processor']
        
        self.search_results = search_processor.search_patent_families(
            keywords=keywords,
            technology_areas=technology_areas,
            date_range=date_range,
            quality_mode=quality_mode,
            max_results=max_results
        )
        
        return self.search_results
    
    def run_applicant_analysis(self, search_results=None):
        """Run applicant analysis on search results."""
        if search_results is None:
            if self.search_results is None:
                raise ValueError("No search results available. Run run_patent_search() first.")
            search_results = self.search_results
        
        analyzer = self.processors['applicant_analyzer']
        self.analysis_results['applicant'] = analyzer.analyze_search_results(search_results)
        
        return self.analysis_results['applicant']
    
    def run_classification_analysis(self, search_results=None):
        """Run classification analysis on search results."""
        if search_results is None:
            if self.search_results is None:
                raise ValueError("No search results available. Run run_patent_search() first.")
            search_results = self.search_results
        
        analyzer = self.processors['classification_analyzer']
        self.analysis_results['classification'] = analyzer.analyze_search_results(search_results)
        
        return self.analysis_results['classification']
    
    def run_geographic_analysis(self, search_results=None):
        """Run geographic analysis on search results."""
        if search_results is None:
            if self.search_results is None:
                raise ValueError("No search results available. Run run_patent_search() first.")
            search_results = self.search_results
        
        analyzer = self.processors['geographic_analyzer']
        self.analysis_results['geographic'] = analyzer.analyze_search_results(search_results)
        
        return self.analysis_results['geographic']
    
    def run_citation_analysis(self, search_results=None):
        """Run citation analysis on search results."""
        if search_results is None:
            if self.search_results is None:
                raise ValueError("No search results available. Run run_patent_search() first.")
            search_results = self.search_results
        
        analyzer = self.processors['citation_analyzer']
        self.analysis_results['citation'] = analyzer.analyze_search_results(search_results)
        
        return self.analysis_results['citation']
    
    def run_complete_analysis(self, search_results=None):
        """
        Run complete analysis workflow on search results.
        
        Args:
            search_results: DataFrame from PatentSearchProcessor (optional, uses cached if available)
            
        Returns:
            Dictionary with all analysis results
        """
        if search_results is None:
            if self.search_results is None:
                raise ValueError("No search results available. Run run_patent_search() first.")
            search_results = self.search_results
        
        # Run all analyses
        self.run_applicant_analysis(search_results)
        self.run_classification_analysis(search_results)
        self.run_geographic_analysis(search_results)
        self.run_citation_analysis(search_results)
        
        return self.analysis_results
    
    def get_comprehensive_summary(self):
        """
        Generate comprehensive summary across all analyses.
        
        Returns:
            Dictionary with integrated summary
        """
        if not self.analysis_results:
            return {'status': 'No analysis results available'}
        
        summary = {
            'search_overview': {
                'total_families': len(self.search_results) if self.search_results is not None else 0,
                'search_quality': self.search_results['quality_score'].mean() if self.search_results is not None else 0
            },
            'analyses_completed': list(self.analysis_results.keys()),
            'analysis_summaries': {}
        }
        
        # Get summaries from each analyzer
        for analysis_type, results in self.analysis_results.items():
            if hasattr(self.processors[f'{analysis_type}_analyzer'], f'get_{analysis_type}_summary'):
                summary_method = getattr(self.processors[f'{analysis_type}_analyzer'], f'get_{analysis_type}_summary')
                summary['analysis_summaries'][analysis_type] = summary_method()
            else:
                summary['analysis_summaries'][analysis_type] = {
                    'status': 'Analysis completed',
                    'records': len(results) if hasattr(results, '__len__') else 'N/A'
                }
        
        return summary
    
    def export_all_results(self, base_filename=None):
        """
        Export all analysis results to files.
        
        Args:
            base_filename: Base filename for exports (timestamp will be added if None)
            
        Returns:
            Dictionary with export filenames
        """
        from datetime import datetime
        
        if base_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"comprehensive_patent_analysis_{timestamp}"
        
        exports = {}
        
        # Export search results
        if self.search_results is not None:
            search_file = f"{base_filename}_search_results.xlsx"
            self.search_results.to_excel(search_file, index=False)
            exports['search_results'] = search_file
        
        # Export each analysis
        for analysis_type, analyzer in self.processors.items():
            if analysis_type != 'search_processor' and hasattr(analyzer, f'export_{analysis_type.replace("_analyzer", "")}_analysis'):
                export_method = getattr(analyzer, f'export_{analysis_type.replace("_analyzer", "")}_analysis')
                try:
                    filename = export_method(f"{base_filename}_{analysis_type.replace('_analyzer', '')}_analysis.xlsx")
                    exports[analysis_type] = filename
                except Exception as e:
                    exports[analysis_type] = f"Export failed: {e}"
        
        return exports

# Quick analysis function for the refactored processors
def run_comprehensive_patent_analysis(keywords=None, technology_areas=None, date_range=None, 
                                     patstat_client=None, max_results=None):
    """
    Run comprehensive patent analysis using the refactored processor workflow.
    
    Args:
        keywords: List of keywords to search for
        technology_areas: List of technology areas from config
        date_range: Tuple of (start_date, end_date)
        patstat_client: PATSTAT client instance (optional)
        max_results: Maximum number of search results
        
    Returns:
        Dictionary with complete analysis results
    """
    workflow = ComprehensiveAnalysisWorkflow(patstat_client)
    
    # Run search
    search_results = workflow.run_patent_search(
        keywords=keywords,
        technology_areas=technology_areas,
        date_range=date_range,
        max_results=max_results
    )
    
    # Run complete analysis
    analysis_results = workflow.run_complete_analysis(search_results)
    
    # Get summary
    summary = workflow.get_comprehensive_summary()
    
    return {
        'workflow': workflow,
        'search_results': search_results,
        'analysis_results': analysis_results,
        'summary': summary
    }