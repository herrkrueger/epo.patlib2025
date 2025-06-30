# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-enhanced patent analytics platform for EPO PATLIB 2025, demonstrating how Claude Code transforms patent analysis into interactive business intelligence. The project integrates PATSTAT database queries with USGS market data to create unique patent-market correlation insights.

## Common Development Commands

### Running the Live Demo

```bash
# Navigate to the active development environment
cd livedemo/

# Launch Jupyter for executive presentations
jupyter lab

# Open the main demo notebooks:
# - REE_Citation_Analysis_Demo.ipynb (patent analytics)
# - REE_Enhanced_Market_Intelligence_Demo.ipynb (market integration)
```

### Testing the Complete Pipeline

```bash
# Run the integrated pipeline (patent + market analysis)
cd livedemo/
python integrated_market_pipeline.py

# Test individual components
python -m database_connection  # Test PATSTAT connectivity
python -m dataset_builder      # Test patent search
python -m citation_analyzer    # Test citation analysis
python -m usgs_market_collector # Test market data integration
```

### Environment Setup

```bash
# Install dependencies (based on imports in codebase)
pip install pandas numpy matplotlib plotly networkx jupyter sqlalchemy python-dotenv requests openpyxl
```

## High-Level Architecture

### Core Patent Analytics Pipeline (livedemo/)

The system follows a modular pipeline architecture:

```
1. Database Connection (database_connection.py)
   ↓
2. Dataset Building (dataset_builder.py)
   - Combined keyword + CPC classification search
   - Quality scoring (intersection approach)
   ↓
3. Citation Analysis (citation_analyzer.py)
   - Forward/backward citations via publication linkage
   - Critical: Citations work through pat_publn_id, not appln_id
   ↓
4. Geographic Intelligence (geographic_enricher.py)
   - Country-level analysis
   - Strategic positioning insights
   ↓
5. Data Validation (data_validator.py)
   - Quality metrics and business reporting
   ↓
6. Market Intelligence Integration (NEW)
   - USGS market data correlation (usgs_market_collector.py)
   - Patent-market insights (patent_market_correlator.py)
   - Business reports (business_intelligence.py)
```

### Key Architectural Patterns

#### PATSTAT Connection Pattern
```python
# Always use PROD environment for full dataset access
from epo.tipdata.patstat import PatstatClient
patstat = PatstatClient(env='PROD')
db = patstat.orm()

# Critical tables for patent analysis:
# - tls201_appln: Applications (primary)
# - tls211_pat_publn: Publications (for citations)
# - tls212_citation: Citation relationships
# - tls202_appln_title, tls203_appln_abstr: Text search
# - tls224_appln_cpc: CPC classifications
```

#### Citation Analysis Pattern
```python
# Citations link through publications, not applications
# 1. Get publications for your applications
# 2. Find citations via publication linkage
# This is a critical architectural understanding!
```

#### Search Strategy Architecture
- **Keyword Search**: User provides terms → System searches title/abstract
- **CPC Search**: System uses predefined classification codes
- **Quality Mode**: Intersection of both approaches for precision

### Market Intelligence Layer (NEW)

The latest enhancement integrates USGS Mineral Commodity Summaries data:

```python
# USGS Data Integration Points
usgs_data = {
    'source': 'DOI 10.5066/P13XCP3R',
    'url': 'https://www.sciencebase.gov/catalog/item/677eaf95d34e760b392c4970',
    'key_files': [
        'Salient_Commodity_Data_Release_Grouped_MCS_2025.zip',
        'World_Data_Release_MCS_2025.zip'
    ]
}

# Patent-Market Correlation Analysis
# Correlates market events (price spikes, supply disruptions) 
# with patent filing patterns and innovation responses
```

### Business Intelligence Outputs

The system generates three types of deliverables:

1. **Executive Dashboards** (enhanced_dashboard.py)
   - 4-panel visualizations combining patent and market data
   - Professional Plotly interactive charts
   
2. **Consulting Reports** (business_intelligence.py)
   - SME risk assessments
   - Investment opportunity analysis
   - Policy recommendations
   
3. **Data Exports**
   - Excel files for further analysis
   - JSON for programmatic access
   - CSV for data interchange

## Critical Technical Details

### PATSTAT Specifics
- **Environment**: Always use `env='PROD'` (TEST has restrictions)
- **Date Range**: '2010-01-01' to '2024-12-31' works reliably
- **Primary Key**: `appln_id` is the central identifier
- **Citations**: Work through `pat_publn_id` linkage

### Performance Targets
- Dataset: 1,000+ patents for statistical validity
- Citations: 1,000+ for meaningful network analysis
- Countries: 15+ for global perspective
- Quality Score: 80+ for business use
- Execution: <10 minutes for complete pipeline

### Demo Requirements
- **90-second rule**: Each notebook cell must execute within demo timeframe
- **Fallback data**: Always have demo data ready if connections fail
- **Visual impact**: Focus on immediate business insights
- **Professional output**: Export-ready formats for stakeholders

## Common Issues and Solutions

1. **PATSTAT Connection**: always use PROD
2. **Citation Queries**: Remember to use publication IDs, not application IDs
3. **Performance**: Use appropriate limits for demo vs. production runs
4. **Market Data**: Cache USGS data locally after first download
5. **Visualizations**: Pre-render complex charts for smooth demos

## Business Context

This platform demonstrates 90% cost savings (€45k → €4.5k) compared to commercial patent databases while adding unique patent-market correlation capabilities. Target users include:
- Patent information centers (PATLIB network)
- SMEs needing supply chain intelligence
- Policy makers requiring strategic materials insights
- Researchers analyzing innovation patterns

The REE (Rare Earth Elements) focus serves as a compelling demonstration case due to critical supply chain issues and high commercial relevance.