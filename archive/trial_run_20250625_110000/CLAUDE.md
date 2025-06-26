# REE Patent Citation Analysis for EPO TIP Platform

## Executive Summary
Create an easy-to-understand Jupyter notebook for the EPO Technology Intelligence Platform (TIP) that builds a Rare Earth Elements (REE) patent dataset with forward/backward citation analysis, overview dashboard, and citation network graph. This serves as a template for Patent Information Experts across German and European PATLIBs, demonstrating how to enhance existing search strategies with Claude Code.

## Target Audience & Business Goal
- **Primary Users**: Patent Information Experts at German and European PATLIBs
- **End Clients**: Students, researchers, entrepreneurs, R&D teams, inventors, patent lawyers
- **Stakeholders**: University library directors, chamber of commerce officials, DPMA.de, EPO.org
- **Goal**: Demonstrate accessible patent analytics for consulting and speaking opportunities

## Technical Requirements

### Platform & Environment
- **Platform**: EPO Technology Intelligence Platform (TIP)
- **Database**: PATSTAT within TIP (PatstatClient)
- **Environment**: PROD with 2023 focus for reliable data
- **Language**: Python with direct SQL queries
- **Format**: Modular Python scripts → final Jupyter Notebook

### Search Strategy

#### Keywords (Title/Abstract Search)
```python
ree_keywords = [
    'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
    'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling'
]
```

#### Classification Codes (Verified CPC patterns)
```python
ree_cpc_codes = [
    'C22B%',      # Metallurgy
    'Y02W30%',    # Waste recycling  
    'Y02P10%',    # Clean production
    'C09K11%',    # Luminescent materials
    'H01F1%'      # Magnets
]
```

## Development Strategy - CORRECT ORDER

### Phase 1: Individual Components (Build in sequence)
```
📁 ree_patent_analysis/
├── database_connection.py         # ✅ BUILD FIRST
├── dataset_builder.py             # ✅ Requires database_connection
├── citation_analyzer.py           # ✅ Requires database_connection, dataset_builder  
├── geographic_enricher.py         # ✅ Requires database_connection, dataset_builder
├── data_validator.py              # ✅ Requires above components
```

### Phase 2: Integration Testing
```
integrated_pipeline.py             # ✅ Requires ALL components above
```

### Phase 3: Final Presentation - LAST STEP
```
REE_Citation_Analysis_Demo.ipynb   # ✅ Requires working pipeline
```

## Component Implementation

### Component 1: Database Connection (database_connection.py)

```python
from epo.tipdata.patstat import PatstatClient
import pandas as pd
from datetime import datetime

def test_tip_connection():
    """Test TIP platform connection with PROD environment"""
    print(f"Analysis started at: {datetime.now()}")
    
    # PROD ENVIRONMENT with 2023 focus for reliable data
    environment = 'PROD'
    print(f"Connecting to PATSTAT {environment} environment...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        print(f"✅ Connected to PATSTAT {environment}")
        
        # Test query with 2023 focus
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year = 2023
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Retrieved {len(test_result)} sample records from 2023")
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

if __name__ == "__main__":
    db = test_tip_connection()
```

### Component 2: Dataset Builder (dataset_builder.py)

```python
def build_ree_dataset(db, test_mode=True):
    """Build REE dataset focusing on 2023 for reliable PROD data"""
    
    print("Building REE dataset for 2023...")
    
    # Keyword-based search
    keyword_query = """
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        t.appln_title, ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        LOWER(t.appln_title) LIKE '%rare earth%' OR
        LOWER(t.appln_title) LIKE '%neodymium%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth element%' OR
        LOWER(ab.appln_abstract) LIKE '%REE recovery%'
    )
    AND a.appln_filing_year = 2023
    """
    
    if test_mode:
        keyword_query += " LIMIT 500"
    
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} keyword matches")
    
    # Classification-based search with broader patterns
    classification_query = """
    SELECT DISTINCT 
        a.appln_id, a.docdb_family_id, a.appln_filing_year, a.appln_auth,
        cpc.cpc_class_symbol
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    WHERE (
        cpc.cpc_class_symbol LIKE 'C22B%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30%' OR
        cpc.cpc_class_symbol LIKE 'H01F1%'
    )
    AND a.appln_filing_year = 2023
    """
    
    if test_mode:
        classification_query += " LIMIT 500"
    
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} classification matches")
    
    # Return best available dataset
    if not keyword_results.empty:
        return keyword_results
    else:
        return classification_results

def validate_ree_dataset(ree_df):
    """Validate dataset quality"""
    print(f"Dataset: {len(ree_df)} applications, {ree_df['docdb_family_id'].nunique()} families")
    print(f"Top countries: {ree_df['appln_auth'].value_counts().head(3).to_dict()}")
```

### Component 3: Citation Analyzer (citation_analyzer.py)

```python
def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """Find patents citing our REE patents"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Forward citations with 2022-2024 timeframe
    forward_query = f"""
    SELECT 
        c.pat_publn_id as citing_publn_id,
        c.cited_appln_id as cited_ree_appln_id,
        p.publn_auth as citing_country,
        a.appln_filing_year as citing_year
    FROM tls212_citation c
    JOIN tls211_pat_publn p ON c.pat_publn_id = p.pat_publn_id
    JOIN tls201_appln a ON p.appln_id = a.appln_id
    WHERE c.cited_appln_id IN ({appln_ids_str})
    AND c.citn_origin = 'SEA'
    AND a.appln_filing_year >= 2022
    """
    
    if test_mode:
        forward_query += " LIMIT 1000"
    
    forward_citations = pd.read_sql(forward_query, db.bind)
    
    if forward_citations.empty:
        print("ℹ️  No forward citations found - normal for recent 2023 patents")
    
    return forward_citations

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """Find patents/literature cited by our REE patents"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    # Get publication IDs
    publn_query = f"""
    SELECT pat_publn_id FROM tls211_pat_publn
    WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    """
    
    ree_publications = pd.read_sql(publn_query, db.bind)
    
    if ree_publications.empty:
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
    
    # Backward citations
    backward_query = f"""
    SELECT 
        c.pat_publn_id as ree_citing_publn_id,
        c.cited_pat_publn_id,
        c.cited_appln_id,
        p_cited.publn_auth as cited_country
    FROM tls212_citation c
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND c.citn_origin = 'SEA'
    """
    
    if test_mode:
        backward_query += " LIMIT 1000"
    
    return pd.read_sql(backward_query, db.bind)
```

### Component 4: Geographic Enricher (geographic_enricher.py)

```python
def enrich_with_geographic_data(db, ree_df):
    """Add country information using verified table relationships"""
    
    if ree_df.empty:
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.st3_name as country_name
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    """
    
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        return ree_df.merge(geo_data, on='appln_id', how='left')
    else:
        return ree_df

def analyze_country_citations(forward_citations_df):
    """Analyze citation flows between countries"""
    
    if not forward_citations_df.empty:
        top_citing = forward_citations_df['citing_country'].value_counts().head(10)
        print(f"Top citing countries: {top_citing.to_dict()}")
        return top_citing
    
    return pd.Series()
```

### Component 5: Data Validator (data_validator.py)

```python
def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """Comprehensive quality checks"""
    
    quality_metrics = {
        'total_applications': len(ree_df),
        'total_families': ree_df['docdb_family_id'].nunique(),
        'forward_citations': len(forward_citations_df),
        'backward_citations': len(backward_citations_df),
        'countries_covered': ree_df['appln_auth'].nunique()
    }
    
    print("DATASET QUALITY REPORT")
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    
    return quality_metrics

def generate_summary_report(ree_df, forward_citations_df, quality_metrics):
    """Generate business summary"""
    
    summary = {
        'total_ree_applications': quality_metrics['total_applications'],
        'total_ree_families': quality_metrics['total_families'],
        'forward_citations': quality_metrics['forward_citations'],
        'top_countries': ree_df['appln_auth'].value_counts().head(3).to_dict()
    }
    
    print("BUSINESS SUMMARY")
    print(f"• REE Applications: {summary['total_ree_applications']}")
    print(f"• Patent Families: {summary['total_ree_families']}")
    print(f"• Forward Citations: {summary['forward_citations']}")
    
    return summary
```

### Component 6: Integration Pipeline (integrated_pipeline.py)

```python
def run_complete_ree_analysis(test_mode=True):
    """Complete REE analysis pipeline"""
    
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    
    # Step 1: Connect
    from database_connection import test_tip_connection
    db = test_tip_connection()
    if not db:
        return None
    
    # Step 2: Build dataset
    from dataset_builder import build_ree_dataset, validate_ree_dataset
    ree_data = build_ree_dataset(db, test_mode)
    if ree_data.empty:
        return None
    validate_ree_dataset(ree_data)
    
    # Step 3: Analyze citations
    from citation_analyzer import get_forward_citations, get_backward_citations
    appln_ids = ree_data['appln_id'].tolist()
    
    forward_cit = get_forward_citations(db, appln_ids, test_mode)
    backward_cit = get_backward_citations(db, appln_ids, test_mode)
    
    # Step 4: Add geography
    from geographic_enricher import enrich_with_geographic_data, analyze_country_citations
    enriched_ree = enrich_with_geographic_data(db, ree_data)
    top_citing = analyze_country_citations(forward_cit)
    
    # Step 5: Validate
    from data_validator import validate_dataset_quality, generate_summary_report
    quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
    summary_report = generate_summary_report(enriched_ree, forward_cit, quality_metrics)
    
    print("✅ PIPELINE COMPLETE")
    
    return {
        'ree_dataset': enriched_ree,
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'summary_report': summary_report,
        'quality_metrics': quality_metrics
    }

if __name__ == "__main__":
    results = run_complete_ree_analysis(test_mode=True)
```

## Final Presentation Notebook Structure

**REE_Citation_Analysis_Demo.ipynb** (Created LAST after all components work):

```markdown
# REE Patent Citation Analysis for PATLIB Community

## Executive Summary
- Business context and key findings
- Strategic recommendations

## Methodology 
- Search strategy explanation
- Cost comparison vs. commercial tools

## Results Visualizations
- Interactive dashboard with key metrics
- Citation network graph
- Country-level analysis charts

## Business Insights
- Geographic hotspots for REE innovation
- Technology transfer patterns
- Market opportunities

## Technical Appendix
- Data sources and methodology details
```

## Visualization Requirements

1. **Interactive Executive Dashboard** - Key metrics, time trends, top countries
2. **Citation Network Graph** - Visual citation relationships with country colors
3. **Geographic Analysis** - World map showing patent activity and citation flows
4. **Technology Landscape** - Classification analysis and evolution trends

## Success Metrics

- **Dataset**: 100-1,000 high-quality 2023 REE families
- **Citations**: Search report citations (citn_origin='SEA')
- **Geography**: Complete country coverage via PROD environment
- **Business Value**: Professional presentation quality for stakeholders

## CORRECTED Todo List

### Phase 1: Individual Components
1. ✅ database_connection.py - **BUILD FIRST**
2. ✅ dataset_builder.py - Requires database_connection
3. ✅ citation_analyzer.py - Requires database_connection, dataset_builder
4. ✅ geographic_enricher.py - Requires database_connection, dataset_builder
5. ✅ data_validator.py - Requires above components

### Phase 2: Integration Testing
6. ✅ integrated_pipeline.py - Requires ALL components above

### Phase 3: Final Presentation - LAST STEP
7. ✅ REE_Citation_Analysis_Demo.ipynb - Requires working pipeline

**CRITICAL: Never create the Jupyter notebook until ALL other components are tested and working!**