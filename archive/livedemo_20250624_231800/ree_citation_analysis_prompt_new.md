# Comprehensive Prompt: REE Patent Citation Analysis Jupyter Notebook for EPO TIP Platform

## Executive Summary
Create a easy to understand Jupyter notebook for the EPO Technology Intelligence Platform (TIP) that builds a Rare Earth Elements (REE) patent dataset with a forward and backward citation analysis and one overview dashboard and one citation network graph visualisation. This notebook should serve as a template for Patent Information Experts working with TIP across Germany and Europe, to demonstrate in easy to understand code examples, how to take an existing search strategy and enhance it with Claude Code with Sonnet 4 model. 

## Target Audience & Business Context
- **Primary Users**: Patent Information Experts at German and European PATLIBs
- **End Clients**: Students, researchers, professors, entrepreneurs, R&D teams, inventors, patent lawyers
- **Stakeholders**: University library directors, chamber of commerce officials, German federal state politicians, DPMA.de, EPO.org
- **Business Goal**: Demonstrate easy to understand tool usage for patent analytics for consulting opportunities and speaking engagements.

## Technical Requirements

### 1. Platform & Environment
- **Platform**: EPO Technology Intelligence Platform (TIP)
- **Database**: PATSTAT within TIP (PatstatClient)
- **Language**: Python with SQL integration
- **Format**: Python scripts, with classes or functions, to live execute within Jupyter Notebook (.ipynb)
- **Visualization**: Interactive charts suitable for professional presentations

### 2. Search Strategy Implementation

#### A. Keyword-Based Identification
Implement the adapted Espacenet query logic for PATSTAT to search for keywords in title and abstract:
```
ree_keywords = [
    # Core REE terms
    'rare earth element', 'rare earth elements',
    'light REE', 'heavy REE', 
    'rare earth metal', 'rare earth metals',
    'rare earth oxide', 'rare earth oxides',
    'lanthanide', 'lanthanides', 'lanthanoid', 'lanthanoids',
    'rare earth',
    
    # Specific REE elements
    'neodymium', 'dysprosium', 'terbium', 'europium', 'yttrium',
    'cerium', 'lanthanum', 'praseodymium', 'samarium', 'gadolinium',
    'holmium', 'erbium', 'thulium', 'ytterbium', 'lutetium',
    'scandium', 'promethium',
    
    # Recovery & Recycling terms
    'REE recovery', 'REE recycling', 'rare earth recovery', 'rare earth recycling',
    'lanthanide recovery', 'lanthanide recycling'
]
```

#### B. Classification-Based Filtering
Implement a second search with these provided CPC codes:

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

Implement the provided working example with enhancements:
1. Keywords-based family identification (TLS203_APPLN_ABSTR, TLS202_APPLN_TITLE)
2. Classification-based identification (TLS209_APPLN_IPC or TLS224_APPLN_CPC)
3. Intersection for high-quality dataset

#### Step 2: Create a summary of the created dataset
Create an easy to understand summary of the results. 
Optional: create easy to understand charts, that show the content of the dataset.

#### Step 2: Citation Network Expansion
```python
# Forward Citations (who cites our REE patents?)
# Backward Citations (what our REE patents cite)

# application citation data enhancements
# TLS201_APPLN.docdb_family_id.label('citing_family_id'),
# TLS201_APPLN.earliest_filing_year.label('citing_year'),
# TLS212_CITATION.cited_appln_id,
# TLS212_CITATION.citing_appln_id,
# TLS212_CITATION.citn_gener_auth,
# TLS212_CITATION.citn_origin
# TLS212_CITATION.pat_publn_id.label('citing_publn_id'),
# TLS212_CITATION.citn_gener_auth

# family citations data set enhancments
# TLS228_DOCDB_FAM_CITN.cited_docdb_family_id.label('cited_family_id'),
# TLS228_DOCDB_FAM_CITN.docdb_family_id.label('citing_family_id')
# TLS228_DOCDB_FAM_CITN.cited_docdb_family_id.in_(family_ids)
    
# - Use TLS212_CITATION table with proper field relationships
# - REE patents appear as CITED patents: TLS212_CITATION.cited_appln_id,
# - Use TLS228_DOCDB_FAM_CITN for family-level citation analysis (recommended)

# - Use TLS212_CITATION where REE patents appear in PAT_PUBLN_ID field
# - Extract CITED_PAT_PUBLN_ID (patent publications cited)
# - Extract CITED_APPLN_ID (patent applications cited)  
# - Extract CITED_NPL_PUBLN_ID (non-patent literature cited)

# - Use TLS215_CITN_CATEG for citation quality categories (X, Y, A, etc.)
```
#### Step 3: Country data
```python
# join and filter to analyse the TLS801_COUNTRY data of each applicaation or familiy
# create a meaningful easy to understand summary and visualisations
# create a scatter plot vizualisation 
# answer the question which country cites which applicants and which country gets cited
```

## 4. Detailed Notebook Structure

### Section 1: Introduction & Methodology (20%)

```markdown
# REE Patent Citation Analysis
## Methodology Overview
- Search strategy explanation
- Database tables used (TLS201, TLS203, TLS202, TLS209/TLS224, TLS212, TLS211, TLS228, TLS801, etc)
- Ease to understand approach
- Citation analysis framework
- Visualisation with one dashboard and one network grahp

## Business Context
- REE market importance
- Recovery/recycling technology extension
- Country relationship focus
- Patent landscape significance
- Collaboration between researchers and TIP and Claude Code capabilities

```

### Section 2: Data Acquisition & Cleaning (25%)
```markdown
- explain the structure and flow of the code
```

```python
# 2.1 TIP PATSTAT Database Connection Setup
from epo.tipdata.patstat import PatstatClient
from epo.tipdata.patstat.database.models import (
    TLS201_APPLN, TLS202_APPLN_TITLE, TLS203_APPLN_ABSTR, 
    TLS209_APPLN_IPC, TLS224_APPLN_CPC, TLS212_CITATION,
    TLS215_CITN_CATEG, TLS228_DOCDB_FAM_CITN, TLS214_NPL_PUBLN,
    TLS227_PERS_PUBLN, TLS207_PERS_APPLN, TLS206_PERSON, TLS211_PAT_PUBLN
)
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import sessionmaker, aliased
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Initialize PATSTAT client for TIP platform
patstat_client = PatstatClient()
session = patstat_client.get_session()

# 2.2 High-Quality REE Dataset Construction
# Implement keyword + classification intersection approach
# Include data quality metrics and validation

# 2.3 Patent Family Enrichment
# Add bibliographic data, applicant information, geographic data

# 2.4 Citation Data Integration
# - TLS212_CITATION: Core citation relationships
# - TLS215_CITN_CATEG: Citation quality categories  
# - TLS228_DOCDB_FAM_CITN: Family-level citations (recommended)
# - TLS214_NPL_PUBLN: Non-patent literature details
# - TLS227_PERS_PUBLN: Publication-person links for geographic analysis
# - TLS207_PERS_APPLN: Application-person links for additional geographic data
```

### Section 3: Citation Network Analysis (30%)
```markdown
- explain the structure and flow of the code
```

```python
# 3.1 Forward Citation Analysis (Who cites our REE patents?)
# - Use TLS212_CITATION where REE patents appear in CITED_* fields
# - Use TLS228_DOCDB_FAM_CITN for family-level analysis (recommended)
# - Geographic distribution of citing entities via TLS227 or TLS228
# - Technology areas of citing patents via TLS224_APPLN_CPC
# - Temporal patterns in citations

# Example TIP PATSTAT query structure:
forward_citations = session.query(
    TLS212_CITATION.pat_publn_id.label('citing_publn_id'),
    TLS212_CITATION.cited_pat_publn_id,
    TLS212_CITATION.cited_appln_id
).filter(
    or_(
        TLS212_CITATION.cited_pat_publn_id.in_(publication_ids),
        TLS212_CITATION.cited_appln_id.in_(appln_ids)
    )
).all()

# 3.2 Backward Citation Analysis (What do our REE patents cite?)
# - Use TLS212_CITATION where REE patents appear in PAT_PUBLN_ID field
# - Include patent citations (CITED_PAT_PUBLN_ID, CITED_APPLN_ID)
# - Include non-patent literature (CITED_NPL_PUBLN_ID) via TLS214_NPL_PUBLN
# - Technology convergence patterns and prior art landscape

# Example TIP PATSTAT query structure:
backward_citations = session.query(
    TLS212_CITATION.pat_publn_id.label('ree_citing_publn_id'),
    TLS212_CITATION.cited_pat_publn_id,
    TLS212_CITATION.cited_appln_id,
    TLS212_CITATION.cited_npl_publn_id
).filter(
    TLS212_CITATION.pat_publn_id.in_(ree_publication_ids)
).all()

# 3.3 Citation Quality Metrics
# - Use TLS215_CITN_CATEG for citation categories (X, Y, A, etc.)
# - Citation velocity (time between publication and citation)
# - Citation persistence (continued citation over time)
# - Cross-jurisdictional citation patterns
# - Citation relevance scoring based on categories
```

### Section 4: Advanced Analytics & Visualization (20%)
```markdown
- explain the structure and flow of the code
```

```python
# 4.1 Country-Level Citation Maps
# Similar to Riccardo's forward citation analysis
# Interactive heatmaps showing citing vs cited countries

# 4.2 Technology Flow Analysis
# Classification co-occurrence in citation networks
# Technology transfer patterns via citations

# 4.3 Key Player Identification
# Most cited REE patent countries
# Most active citers countries of REE technology
# List of top Patent families with highest citation impact
```

### Section 5: Results & Business Intelligence (5%)
```markdown
# Key Findings Summary
- Top REE technology areas by citation impact
- Geographic hotspots for REE innovation and application
- Emerging technology trends in REE market
- Strategic recommendations for stakeholders
```

## 5. Technical Implementation Details

### Database Queries Structure
```python

# Base query template for TIP PATSTAT access
def get_ree_patent_families(session):
    """
    Optimized query combining keyword and classification approaches
    Returns high-quality REE patent family dataset using TIP PatstatClient
    """
    
def get_forward_citations(session, ree_family_ids, ree_appln_ids):
    """
    Extract all patents citing the REE dataset using correct PATSTAT logic
    Forward citations: REE patents appear in CITED_* fields of TLS212_CITATION
    
    Uses TIP PatstatClient session for database access
    
    Returns:
    - citing_publn_id: Publications that cite our REE patents
    - cited_ree_publn_id: Our REE publications being cited
    - cited_ree_appln_id: Our REE applications being cited
    - Include bibliographic and applicant data via joins
    """
    
def get_backward_citations(session, ree_appln_ids):
    """
    Extract all patents/NPL cited by REE dataset using correct PATSTAT logic
    Backward citations: REE patents appear in PAT_PUBLN_ID field of TLS212_CITATION
    
    Uses TIP PatstatClient session for database access
    
    Returns:
    - ree_citing_publn_id: Our REE patents doing the citing
    - cited_pat_publn_id: Patent publications our REE patents cite
    - cited_appln_id: Patent applications our REE patents cite
    - cited_npl_publn_id: Non-patent literature our REE patents cite
    - citn_origin: Source of citation (search report, applicant, etc.)
    """

def get_citation_quality_metrics(session, citation_data):
    """
    Analyze citation quality using TLS215_CITN_CATEG
    Citation categories: X (highly relevant), Y (relevant combined), A (general state of art)
    Include relevant claims analysis for detailed citation impact
    
    Uses TIP PatstatClient session for database access
    """

def get_family_level_citations(session, ree_family_ids):
    """
    Family-to-family citation analysis using TLS228_DOCDB_FAM_CITN
    Recommended approach for technology intelligence as it focuses on inventions
    rather than individual publications
    
    Uses TIP PatstatClient session for database access
    """

def enrich_with_geographic_data(session, df):
    """
    Add country codes, regions, economic indicators from e.g. TLS801 
    Use TLS227_PERS_PUBLN and TLS206_PERSON for applicant geography (publication-level)
    Use TLS207_PERS_APPLN and TLS206_PERSON for applicant geography (application-level)
    Enable geographic analysis and visualization
    
    Uses TIP PatstatClient session for database access
    """
```

### Visualization Requirements
```python
# Professional-grade visualizations for PATLIB presentations:
# 1. Interactive geographic citation heatmaps
# 2. Time-series citation trend analysis
# 3. Technology classification co-occurrence matrices
# 4. Network graphs showing citation relationships
```

## 6. Documentation & Reproducibility Standards

### Code Documentation
- Comprehensive docstrings for all functions
- Inline comments explaining complex SQL queries
- Methodology notes for each analytical step

### Reproducibility Features
- Parameterized queries for easy customization
- Modular functions for reuse in other domains
- Clear data provenance tracking

### Educational Components
- Step-by-step explanation of PATSTAT table relationships
- Citation analysis best practices
- Interpretation guidelines for different stakeholder types
- Common pitfalls and how to avoid them

## 7. Output Specifications

### Datasets Produced
1. **Core REE Patent Families**: High-quality intersection dataset with DOCDB_FAMILY_ID
2. **Forward Citation Network**: Patents citing REE technologies (via TLS212_CITATION and TLS228_DOCDB_FAM_CITN)
3. **Backward Citation Network**: Prior art cited by REE patents (publications, applications, and NPL)
4. **Citation Quality Matrix**: Categories and relevance scores from TLS215_CITN_CATEG
5. **Enriched Analytics Dataset**: Combined data with geographic, temporal, and bibliographic enrichments

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

## 8. Success Metrics & Validation

### Quality Assurance
- Dataset size validation (target: 1,000-85,000 high-quality families)
- Dataset timeframe: 2014-2024
- Citation completeness checks using TLS212_CITATION business rules
- Geographic coverage assessment via TLS227_PERS_PUBLN and TLS207_PERS_APPLN
- Temporal distribution validation
- Citation direction validation (forward vs backward logic)
- Family-level vs publication-level citation consistency checks

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