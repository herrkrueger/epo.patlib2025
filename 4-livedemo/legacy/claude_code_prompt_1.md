# Comprehensive Prompt: REE Patent Citation Analysis Jupyter Notebook for EPO TIP Platform

## Executive Summary
Create a comprehensive Jupyter notebook for the EPO Technology Intelligence Platform (TIP) that builds a high-quality Rare Earth Elements (REE) patent dataset with forward and backward citation analysis. This notebook should serve as a template for Patent Information Experts working with PATLIB networks across Germany and Europe.

## Target Audience & Business Context
- **Primary Users**: Patent Information Experts at German and European PATLIBs
- **End Clients**: Students, researchers, professors, entrepreneurs, R&D teams, inventors, patent lawyers
- **Stakeholders**: University library directors, chamber of commerce officials, German federal state politicians, DPMA.de, EPO.org
- **Business Goal**: Demonstrate advanced patent analytics capabilities for consulting opportunities and speaking engagements

## Technical Requirements

### 1. Platform & Environment
- **Platform**: EPO Technology Intelligence Platform (TIP)
- **Database**: PATSTAT Global via SQLAlchemy
- **Language**: Python with SQL integration
- **Format**: Jupyter Notebook (.ipynb)
- **Visualization**: Interactive charts suitable for professional presentations

### 2. Search Strategy Implementation

#### A. Keyword-Based Identification
Implement the adapted Espacenet query logic:
```sql
-- Translate Espacenet proximity search to PATSTAT keyword matching
-- Keywords: "rare earth element*", "light REE*", "heavy REE*", "rare earth metal*", 
-- "rare earth oxide*", "lanthan*", "rare earth"
-- Recovery/Recycling terms: "recov*", "recycl*"
```

#### B. Classification-Based Filtering
Focus on the provided CPC/IPC codes:
```
A43B1/12, B03B9/06, B22F8, B29B7/66, B29B17, B30B9/32, B62D67, B65H73, 
B65D65/46, C03B1/02, C04B7/24-30, CO4B11/26, C04B18/04-305, C04B33/132, 
C08J11, СО9K11/01, C10M175, C22B7, C22B19/28-30, C22B25/06, DO1G11, 
D21B1/08-10, D21B1/32, D21C5/02, D21H17/01, H01B 15/00, H01J 9/52, 
H01M 6/52, H01M 10/54, YO2W30/52, YO2W30/56, YO2W30/58, YO2W30/60, 
YO2W30/62, YO2W30/64, YO2W30/66, YO2W30/74, YO2W30/78, YO2W30/80, 
YO2W30/82, YO2W30/84, YO2W30/91, YO2P10/20
```

### 3. Core Dataset Construction

#### Step 1: High-Quality REE Family Identification
```python
# Implement the provided working example with enhancements:
# 1. Keywords-based family identification (TLS203_APPLN_ABSTR, TLS202_APPLN_TITLE)
# 2. Classification-based identification (TLS224_APPLN_CPC)
# 3. Intersection for high-quality dataset
# 4. Recovery/recycling filter integration
```

#### Step 2: Citation Network Expansion
```python
# Forward Citations (who cites our REE patents)
# - Use TLS212_CITATION table
# - Link via cited_appln_id -> appln_id
# - Extract citing patent information

# Backward Citations (what our REE patents cite)
# - Use TLS211_PAT_PUBLN_CITE for patent citations
# - Use TLS215_CITN_CATEG for citation categories
# - Extract cited patent information and NPL references
```

## 4. Detailed Notebook Structure

### Section 1: Introduction & Methodology (20%)
```markdown
# REE Patent Citation Analysis
## Methodology Overview
- Search strategy explanation
- Database tables used (TLS201, TLS203, TLS202, TLS209/TLS224, TLS212, TLS211)
- Quality assurance approach
- Citation analysis framework

## Business Context
- REE market importance
- Patent landscape significance
- Recovery/recycling technology focus
```

### Section 2: Data Acquisition & Cleaning (25%)
```python
# 2.1 Database Connection Setup
from sqlalchemy import create_engine, func, or_, and_
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 2.2 High-Quality REE Dataset Construction
# Implement keyword + classification intersection approach
# Include data quality metrics and validation

# 2.3 Patent Family Enrichment
# Add bibliographic data, applicant information, geographic data
```

### Section 3: Citation Network Analysis (30%)
```python
# 3.1 Forward Citation Analysis
# - Who is citing REE patents?
# - Geographic distribution of citing entities
# - Technology areas of citing patents
# - Temporal patterns in citations

# 3.2 Backward Citation Analysis  
# - What technologies do REE patents build upon?
# - Non-patent literature (NPL) references
# - Technology convergence patterns

# 3.3 Citation Quality Metrics
# - Citation velocity (time between publication and citation)
# - Citation persistence (continued citation over time)
# - Cross-jurisdictional citation patterns
```

### Section 4: Advanced Analytics & Visualization (20%)
```python
# 4.1 Country-Level Citation Maps
# Similar to Riccardo's forward citation analysis
# Interactive heatmaps showing citing vs cited countries

# 4.2 Technology Flow Analysis
# Classification co-occurrence in citation networks
# Technology transfer patterns via citations

# 4.3 Key Player Identification
# Most cited REE patent holders
# Most active citers of REE technology
# Patent families with highest citation impact
```

### Section 5: Results & Business Intelligence (5%)
```markdown
# Key Findings Summary
- Top REE technology areas by citation impact
- Geographic hotspots for REE innovation and application
- Emerging technology trends in REE recovery/recycling
- Strategic recommendations for stakeholders
```

## 5. Technical Implementation Details

### Database Queries Structure
```python
# Base query template for TIP PATSTAT access
def get_ree_patent_families():
    """
    Optimized query combining keyword and classification approaches
    Returns high-quality REE patent family dataset
    """
    
def get_forward_citations(family_ids):
    """
    Extract all patents citing the REE dataset
    Include bibliographic and applicant data
    """
    
def get_backward_citations(family_ids):
    """
    Extract all patents/NPL cited by REE dataset
    Categorize citation types and relevance
    """

def enrich_with_geographic_data(df):
    """
    Add country codes, regions, economic indicators
    Enable geographic analysis and visualization
    """
```

### Visualization Requirements
```python
# Professional-grade visualizations for PATLIB presentations:
# 1. Interactive geographic citation heatmaps
# 2. Time-series citation trend analysis
# 3. Technology classification co-occurrence matrices
# 4. Network graphs showing citation relationships
# 5. Bubble charts for multi-dimensional patent metrics
```

## 6. Documentation & Reproducibility Standards

### Code Documentation
- Comprehensive docstrings for all functions
- Inline comments explaining complex SQL queries
- Methodology notes for each analytical step
- Data quality checks and validation procedures

### Reproducibility Features
- Parameterized queries for easy customization
- Modular functions for reuse in other domains
- Clear data provenance tracking
- Version control considerations for PATSTAT updates

### Educational Components
- Step-by-step explanation of PATSTAT table relationships
- Citation analysis best practices
- Interpretation guidelines for different stakeholder types
- Common pitfalls and how to avoid them

## 7. Output Specifications

### Datasets Produced
1. **Core REE Patent Families**: High-quality intersection dataset
2. **Forward Citation Network**: Patents citing REE technologies
3. **Backward Citation Network**: Prior art cited by REE patents
4. **Enriched Analytics Dataset**: Combined data with geographic, temporal, and bibliographic enrichments

### Visualizations Delivered
1. **Executive Dashboard**: Key metrics summary for decision-makers
2. **Geographic Citation Maps**: Country-level citation flow analysis
3. **Technology Landscape**: Classification-based technology clustering
4. **Temporal Trends**: Time-series analysis of citation patterns
5. **Network Analysis**: Citation relationship mapping

### Export Formats
- Excel files for business stakeholders
- CSV files for further analysis
- PNG/SVG files for presentations
- Interactive HTML dashboards
- PowerBI-compatible datasets

## 8. Success Metrics & Validation

### Quality Assurance
- Dataset size validation (target: 1,000-10,000 high-quality families)
- Citation completeness checks
- Geographic coverage assessment
- Temporal distribution validation

### Business Value Indicators
- Actionable insights for patent strategy
- Novel patterns discovery capability
- Stakeholder presentation readiness
- Consulting opportunity demonstration value

## 9. Future Extensions & Modularity

### Extensibility Features
- Easy adaptation to other technology domains
- Scalable citation analysis framework
- Integration with external data sources
- API connectivity for real-time updates

### Advanced Analytics Preparation
- Machine learning ready datasets
- Natural language processing preparation
- Semantic patent analysis foundation
- AI-powered insight generation capabilities

This notebook should serve as both a powerful analytical tool and a compelling demonstration of advanced patent intelligence capabilities for the German and European PATLIB community.