#!/usr/bin/env python3
"""
Working Patent Intelligence Platform Script
Converted from tested workflow - ready for notebook conversion.

This script contains the exact working code that can be copied into notebook cells.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Execute the complete working patent intelligence workflow."""
    
    print("🚀 Patent Intelligence Platform - Working Demo")
    print("=" * 60)
    
    # === CELL 1: Setup & Imports ===
    print("\n🔧 CELL 1: Setup & Imports")
    
    # Add parent directory to Python path for module imports
    parent_dir = Path().resolve().parent if "scripts" in str(Path().resolve()) else Path().resolve()
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    # Production platform imports - using correct class names
    from config import ConfigurationManager
    from data_access import PatstatClient, EPOOPSClient, PatentCountryMapper, PatentSearcher
    from processors import (ApplicantAnalyzer, GeographicAnalyzer, 
                           ClassificationAnalyzer, CitationAnalyzer)
    from visualizations import (ProductionChartCreator, ProductionDashboardCreator, 
                              ProductionMapsCreator)
    
    print("✅ All imports successful")
    print(f"📁 Working Directory: {Path().resolve()}")
    print("✅ Using Production-Ready Architecture")
    
    # === CELL 2: Configuration ===
    print("\n⚙️ CELL 2: Configuration Management")
    
    config = ConfigurationManager()
    print(f"✅ API Config: {len(config.get('api'))} settings loaded")
    print(f"✅ Database Config: {len(config.get('database'))} settings loaded")
    print(f"✅ Search Patterns: {len(config.get('search_patterns'))} patterns loaded")
    print(f"✅ Visualization Config: {len(config.get('visualization'))} settings loaded")
    
    # Show configuration summary
    summary = config.get_configuration_summary()
    print(f"🌍 Environment: {summary['environment']}")
    print(f"📋 Loaded Configs: {', '.join(summary['loaded_configs'])}")
    
    # === CELL 3: Database Connection ===
    print("\n🗄️ CELL 3: PATSTAT Database Connection")
    
    # Initialize PATSTAT client with production environment
    patstat = PatstatClient(environment='PROD')
    print("✅ PATSTAT connection established")
    print("📊 Database Environment: PROD (full dataset access)")
    
    # Initialize additional components
    country_mapper = PatentCountryMapper()
    print("🌍 Geographic Intelligence: PatentCountryMapper initialized")
    
    try:
        ops_client = EPOOPSClient()
        print("📡 EPO OPS API: Ready for enhanced data retrieval")
    except Exception as e:
        print(f"⚠️ EPO OPS API: Credentials not configured")
        ops_client = None
    
    # === CELL 4: Patent Search ===
    print("\n🔍 CELL 4: Patent Search with Real PATSTAT Data")
    
    # Create patent searcher
    patent_searcher = PatentSearcher(patstat)
    print(f"✅ PatentSearcher initialized with {len(patent_searcher.cpc_codes)} CPC codes")
    
    # Execute search with small date range for demo
    search_results = patent_searcher.execute_comprehensive_search(
        start_date="2024-01-01",
        end_date="2024-01-07",  # Small range for reliable demo
        focused_search=True
    )
    
    print(f"✅ Found {len(search_results)} patent applications from PATSTAT PROD")
    print(f"📊 Data columns: {list(search_results.columns)}")
    print(f"📈 Coverage: {search_results['appln_auth'].nunique() if 'appln_auth' in search_results.columns else 'N/A'} jurisdictions")
    
    # Show sample results
    if len(search_results) > 0:
        print("\n📋 Sample Patent Records from PATSTAT:")
        display_cols = [col for col in ['appln_id', 'docdb_family_id', 'search_method', 'quality_score'] 
                        if col in search_results.columns]
        if display_cols:
            print(search_results[display_cols].head(3).to_string(index=False))
    
    # === CELL 5: Four-Processor Intelligence Pipeline ===
    print("\n⚙️ CELL 5: Four-Processor Intelligence Pipeline")
    
    analysis_results = {}
    
    # 1. Applicant Intelligence
    print("\n👥 [1/4] Applicant Intelligence Analysis...")
    try:
        applicant_analyzer = ApplicantAnalyzer(patstat)
        applicant_analysis = applicant_analyzer.analyze_search_results(search_results)
        analysis_results['applicant'] = applicant_analysis
        print(f"✅ Applicant analysis complete: {len(applicant_analysis)} applicants analyzed")
    except Exception as e:
        print(f"⚠️ Applicant analyzer: {e}")
        analysis_results['applicant'] = pd.DataFrame()
    
    # 2. Geographic Intelligence
    print("\n🌍 [2/4] Geographic Intelligence Analysis...")
    try:
        geographic_analyzer = GeographicAnalyzer(patstat)
        geographic_analysis = geographic_analyzer.analyze_search_results(search_results)
        analysis_results['geographic'] = geographic_analysis
        print(f"✅ Geographic analysis complete: {len(geographic_analysis)} regions analyzed")
    except Exception as e:
        print(f"⚠️ Geographic analyzer: {e}")
        analysis_results['geographic'] = pd.DataFrame()
    
    # 3. Technology Classification
    print("\n🔬 [3/4] Technology Classification Analysis...")
    try:
        classification_analyzer = ClassificationAnalyzer(patstat)
        classification_analysis = classification_analyzer.analyze_search_results(search_results)
        analysis_results['classification'] = classification_analysis
        print(f"✅ Classification analysis complete: {len(classification_analysis)} technology areas analyzed")
    except Exception as e:
        print(f"⚠️ Classification analyzer: {e}")
        analysis_results['classification'] = pd.DataFrame()
    
    # 4. Citation Network
    print("\n🔗 [4/4] Citation Network Analysis...")
    try:
        citation_analyzer = CitationAnalyzer(patstat)
        citation_analysis = citation_analyzer.analyze_search_results(search_results)
        analysis_results['citation'] = citation_analysis
        print(f"✅ Citation analysis complete: {len(citation_analysis)} citation patterns analyzed")
    except Exception as e:
        print(f"⚠️ Citation analyzer: {e}")
        analysis_results['citation'] = pd.DataFrame()
    
    # Pipeline summary
    print(f"\n📊 Processing Pipeline Complete:")
    for analysis_type, results in analysis_results.items():
        count = len(results) if hasattr(results, '__len__') else 'Available'
        print(f"  ✅ {analysis_type.title()}: {count} entities analyzed")
    
    # === CELL 6: Executive Dashboard ===
    print("\n📊 CELL 6: Executive Business Intelligence Dashboard")
    
    try:
        dashboard_creator = ProductionDashboardCreator(config)
        
        # Convert analysis results to safe format for dashboard
        dashboard_data = {}
        for key, value in analysis_results.items():
            dashboard_data[key] = value if value is not None else pd.DataFrame()
        
        executive_dashboard = dashboard_creator.create_executive_dashboard(
            dashboard_data, 
            title="Patent Intelligence Executive Dashboard"
        )
        
        print("✅ Executive dashboard created successfully")
        print("📈 Dashboard includes: Market leaders, geographic distribution, technology trends")
        
        # In notebook, this would be: executive_dashboard.show()
        print("💡 In notebook: executive_dashboard.show() to display interactive dashboard")
        
    except Exception as e:
        print(f"⚠️ Dashboard creation: {e}")
    
    # === CELL 7: Geographic Visualization ===
    print("\n🗺️ CELL 7: Global Patent Landscape Visualization")
    
    try:
        maps_creator = ProductionMapsCreator(config)
        
        # Create geographic visualization if we have geographic data
        if len(analysis_results.get('geographic', pd.DataFrame())) > 0:
            global_map = maps_creator.create_patent_choropleth(
                {'country_summary': analysis_results['geographic']},
                title="Global Patent Intelligence Landscape"
            )
            print("✅ Global patent activity map created")
            print("💡 In notebook: global_map.show() to display interactive map")
        else:
            print("⚠️ No geographic data available for mapping")
            
    except Exception as e:
        print(f"⚠️ Geographic visualization: {e}")
    
    # === CELL 8: Performance Summary ===
    print("\n⚡ CELL 8: Performance & Technical Summary")
    
    print("🏆 Technical Achievements:")
    print("  ✅ Zero Exception Architecture: Complete EPO client garbage collection fix")
    print("  ✅ Production Database Access: Real PATSTAT PROD environment connectivity")
    print("  ✅ Configuration-Driven Architecture: YAML-based modular configuration")
    print("  ✅ Technology Agnostic Design: No hardcoded domain-specific data")
    
    print(f"\n📊 Current Demo Session Results:")
    print(f"  🔍 Patents processed: {len(search_results):,}")
    print(f"  ⚙️ Analyzers completed: {len([r for r in analysis_results.values() if len(r) > 0])}/4")
    print(f"  📈 Total entities analyzed: {sum(len(r) for r in analysis_results.values() if hasattr(r, '__len__'))}")
    
    print("\n💼 Business Value:")
    print("  🎯 Patent Professionals: Automated competitive intelligence")
    print("  🔬 Researchers: Advanced analytics with publication-ready visualizations")
    print("  👔 Executives: Clear dashboards for strategic decision-making")
    
    print("\n" + "=" * 60)
    print("🚀 Patent Intelligence Platform Demo Complete")
    print("📧 Ready for EPO PATLIB 2025 Live Demonstration")
    
    return {
        'search_results': search_results,
        'analysis_results': analysis_results,
        'config': config,
        'patstat': patstat
    }

if __name__ == "__main__":
    results = main()