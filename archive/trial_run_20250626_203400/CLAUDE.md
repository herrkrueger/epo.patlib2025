# REE Patent Citation Analysis for EPO TIP Platform - Live Demo 9

## Executive Summary
Create a professional Jupyter notebook for the EPO Technology Intelligence Platform (TIP) that delivers comprehensive REE patent analysis with citation intelligence, executive dashboards, and business insights. This serves as a template for Patent Information Experts across German and European PATLIBs, demonstrating how to enhance existing search strategies and deliver professional analytics at a fraction of commercial tool costs.

## Target Audience & Business Goal
- **Primary Users**: Patent Information Experts at German and European PATLIBs
- **End Clients**: Students, researchers, entrepreneurs, R&D teams, inventors, patent lawyers
- **Stakeholders**: University library directors, chamber of commerce officials, DPMA.de, EPO.org
- **Goal**: Demonstrate professional patent analytics for consulting and speaking opportunities
- **Value Proposition**: Professional-grade analytics comparable to €15,000-20,000 commercial solutions

## Technical Requirements

### Platform & Environment
- **Platform**: EPO Technology Intelligence Platform (TIP)
- **Database**: PATSTAT within TIP (PatstatClient)
- **Environment**: PROD with 2014-2024 comprehensive timeframe
- **Language**: Python with optimized SQL queries
- **Format**: Modular Python scripts → professional Jupyter Notebook
- **Citation Strategy**: Complete citation coverage for maximum intelligence

### Search Strategy

#### Keywords (Title/Abstract Search)
```python
ree_keywords = [
    'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
    'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling',
    'scandium', 'erbium', 'terbium', 'europium', 'gadolinium'
]
```

#### Classification Codes (CPC patterns)
```python
ree_cpc_codes = [
    'C22B%',      # Metallurgy & Metal Extraction
    'Y02W30%',    # Waste Management & Recycling  
    'H01F1%',     # Magnets & Magnetic Materials
    'C09K11%',    # Luminescent Materials
    'Y02P10%',    # Clean Production Technologies
    'C01F17%'     # Rare Earth Compounds
]
```

### Key Implementation Insights

#### Citation Architecture Best Practice
**Learning**: PATSTAT citations require proper linkage via publications, not direct application IDs.

```python
# Correct approach for citation analysis
def get_forward_citations(db, ree_appln_ids):
    # Step 1: Get publication IDs for REE applications
    ree_publications = get_publications_for_applications(appln_ids)
    
    # Step 2: Find citations via publication linkage
    forward_query = """
    SELECT c.*, citing_info.*
    FROM tls212_citation c
    JOIN tls211_pat_publn p_citing ON c.pat_publn_id = p_citing.pat_publn_id
    WHERE c.cited_pat_publn_id IN (ree_publication_ids)
    """
```

#### Comprehensive Citation Coverage
Include all citation origins for complete intelligence:
- **SEA** (Search Report): Official examiner citations
- **APP** (Applicant): Self-reported citations  
- **ISR** (International Search): PCT official citations
- **EXA** (Examiner): Direct examiner citations
- **Plus 7 additional origins** for complete coverage

#### Timeframe Optimization
**2014-2024 provides optimal balance**:
- Sufficient data volume for robust analysis
- Recent enough for current relevance
- Long enough timeframe to capture citation patterns

## Development Architecture

### Component Dependencies
```python
dependencies = {
    'database_connection': [],
    'dataset_builder': ['database_connection'],
    'citation_analyzer': ['database_connection', 'dataset_builder'],
    'geographic_enricher': ['database_connection', 'dataset_builder'],
    'data_validator': ['all_analysis_components'],
    'integrated_pipeline': ['all_above'],
    'final_notebook': ['integrated_pipeline']
}
```

### Implementation Sequence
```
📁 ree_patent_analysis/
├── database_connection.py         # ✅ BUILD FIRST
├── dataset_builder.py             # ✅ Search strategies  
├── citation_analyzer.py           # ✅ Citation intelligence
├── geographic_enricher.py         # ✅ Geographic analysis
├── data_validator.py              # ✅ Quality assessment
├── integrated_pipeline.py         # ✅ Integration testing
└── REE_Citation_Analysis_Demo.ipynb   # ✅ Final presentation
```

## Component Implementation

### Component 1: Database Connection
```python
from epo.tipdata.patstat import PatstatClient
import pandas as pd

def test_tip_connection():
    """Connect to PROD environment with 2014-2024 timeframe"""
    environment = 'PROD'
    print(f"Connecting to PATSTAT {environment}...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        # Test with comprehensive timeframe
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year BETWEEN 2014 AND 2024
        LIMIT 10
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Retrieved {len(test_result)} sample records")
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None
```

### Component 2: Dataset Builder
```python
def build_ree_dataset(db, test_mode=True):
    """Build REE dataset with combined search strategies"""
    
    print("Building REE dataset for 2014-2024...")
    
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
        LOWER(ab.appln_abstract) LIKE '%rare earth element%'
    )
    AND a.appln_filing_year BETWEEN 2014 AND 2024
    """
    
    # Classification-based search
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
    AND a.appln_filing_year BETWEEN 2014 AND 2024
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
        classification_query += " LIMIT 1000"
    
    # Execute searches and combine results
    keyword_results = pd.read_sql(keyword_query, db.bind)
    classification_results = pd.read_sql(classification_query, db.bind)
    
    # Combine and deduplicate
    if not keyword_results.empty and not classification_results.empty:
        combined_df = pd.concat([keyword_results, classification_results]).drop_duplicates(subset=['appln_id'])
        print(f"Combined dataset: {len(combined_df)} unique applications")
        return combined_df
    elif not keyword_results.empty:
        return keyword_results
    else:
        return classification_results
```

### Component 3: Citation Analyzer
```python
def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """Find forward citations using proper publication linkage"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Step 1: Get publication IDs for REE applications
    ree_publications_query = f"""
    SELECT appln_id as ree_appln_id, pat_publn_id as ree_publn_id
    FROM tls211_pat_publn
    WHERE appln_id IN ({appln_ids_str})
    """
    
    ree_publications = pd.read_sql(ree_publications_query, db.bind)
    
    if ree_publications.empty:
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['ree_publn_id']))
    
    # Step 2: Find citations via publication linkage
    forward_query = f"""
    SELECT 
        c.pat_publn_id as citing_publn_id,
        c.cited_pat_publn_id as cited_ree_publn_id,
        p_citing.appln_id as citing_appln_id,
        p_citing.publn_auth as citing_country,
        a_citing.appln_filing_year as citing_year,
        c.citn_origin,
        ree_pub.ree_appln_id as cited_ree_appln_id
    FROM tls212_citation c
    JOIN tls211_pat_publn p_citing ON c.pat_publn_id = p_citing.pat_publn_id
    JOIN tls201_appln a_citing ON p_citing.appln_id = a_citing.appln_id
    JOIN ({ree_publications_query}) ree_pub ON c.cited_pat_publn_id = ree_pub.ree_publn_id
    WHERE c.cited_pat_publn_id IN ({publn_ids_str})
    AND a_citing.appln_filing_year BETWEEN 2010 AND 2024
    """
    
    if test_mode:
        forward_query += " LIMIT 2000"
    
    forward_citations = pd.read_sql(forward_query, db.bind)
    
    if not forward_citations.empty:
        print(f"✅ Found {len(forward_citations)} forward citations")
        origin_counts = forward_citations['citn_origin'].value_counts()
        print(f"Citation origins: {dict(origin_counts.head(5))}")
    
    return forward_citations

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """Find backward citations for prior art analysis"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    # Get publication IDs for our REE patents
    publn_query = f"""
    SELECT pat_publn_id, appln_id FROM tls211_pat_publn
    WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    """
    
    ree_publications = pd.read_sql(publn_query, db.bind)
    
    if ree_publications.empty:
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
    
    # Find backward citations
    backward_query = f"""
    SELECT 
        c.pat_publn_id as ree_citing_publn_id,
        c.cited_pat_publn_id,
        c.cited_appln_id,
        c.citn_origin,
        p_cited.publn_auth as cited_country,
        a_cited.appln_filing_year as cited_year
    FROM tls212_citation c
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    LEFT JOIN tls201_appln a_cited ON c.cited_appln_id = a_cited.appln_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND (a_cited.appln_filing_year >= 2000 OR a_cited.appln_filing_year IS NULL)
    """
    
    if test_mode:
        backward_query += " LIMIT 2000"
    
    backward_citations = pd.read_sql(backward_query, db.bind)
    
    if not backward_citations.empty:
        print(f"✅ Found {len(backward_citations)} backward citations")
    
    return backward_citations
```

### Component 4: Geographic Enricher
```python
def enrich_with_geographic_data(db, ree_df):
    """Add comprehensive country information"""
    
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
        print(f"✅ Geographic data: {geo_data['person_ctry_code'].nunique()} countries")
        return ree_df.merge(geo_data, on='appln_id', how='left')
    else:
        return ree_df
```

### Component 5: Data Validator
```python
def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """Comprehensive quality assessment with business scoring"""
    
    quality_metrics = {
        'total_applications': len(ree_df),
        'total_families': ree_df['docdb_family_id'].nunique(),
        'forward_citations': len(forward_citations_df),
        'backward_citations': len(backward_citations_df),
        'countries_covered': ree_df['appln_auth'].nunique(),
        'year_range': f"{ree_df['appln_filing_year'].min()}-{ree_df['appln_filing_year'].max()}"
    }
    
    # Calculate quality score (0-100)
    quality_score = calculate_quality_score(quality_metrics)
    quality_metrics['quality_score'] = quality_score
    
    print("DATASET QUALITY ASSESSMENT")
    print(f"Applications: {quality_metrics['total_applications']:,}")
    print(f"Patent Families: {quality_metrics['total_families']:,}")
    print(f"Forward Citations: {quality_metrics['forward_citations']:,}")
    print(f"Backward Citations: {quality_metrics['backward_citations']:,}")
    print(f"Countries: {quality_metrics['countries_covered']}")
    print(f"Quality Score: {quality_score}/100")
    
    # Business assessment
    if quality_score >= 75:
        print("✅ EXCELLENT - Ready for professional analysis")
    elif quality_score >= 60:
        print("✅ GOOD - Suitable for most business analyses")
    elif quality_score >= 40:
        print("⚠️  FAIR - Usable but consider expanding scope")
    else:
        print("❌ POOR - Recommend adjusting search strategy")
    
    return quality_metrics

def calculate_quality_score(metrics):
    """Calculate business-oriented quality score"""
    score = 0
    
    # Application volume (30 points)
    if metrics['total_applications'] >= 1000: score += 30
    elif metrics['total_applications'] >= 500: score += 20
    elif metrics['total_applications'] >= 200: score += 15
    elif metrics['total_applications'] >= 100: score += 10
    
    # Citation coverage (30 points)
    total_citations = metrics['forward_citations'] + metrics['backward_citations']
    if total_citations >= 1000: score += 30
    elif total_citations >= 500: score += 25
    elif total_citations >= 200: score += 20
    elif total_citations >= 100: score += 15
    elif total_citations >= 50: score += 10
    
    # Geographic diversity (25 points)
    if metrics['countries_covered'] >= 15: score += 25
    elif metrics['countries_covered'] >= 10: score += 20
    elif metrics['countries_covered'] >= 5: score += 15
    elif metrics['countries_covered'] >= 3: score += 10
    
    # Innovation diversity (15 points)
    family_ratio = metrics['total_families'] / max(metrics['total_applications'], 1)
    if family_ratio >= 0.8: score += 15
    elif family_ratio >= 0.6: score += 12
    elif family_ratio >= 0.4: score += 8
    elif family_ratio >= 0.2: score += 5
    
    return min(score, 100)
```

### Component 6: Integrated Pipeline
```python
def run_complete_ree_analysis(test_mode=True):
    """Execute complete REE analysis pipeline"""
    
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("=" * 50)
    
    # Step 1: Database connection
    from database_connection import test_tip_connection
    db = test_tip_connection()
    if not db:
        return None
    
    # Step 2: Build dataset
    from dataset_builder import build_ree_dataset
    ree_data = build_ree_dataset(db, test_mode)
    if ree_data.empty:
        print("❌ No REE data found")
        return None
    
    # Step 3: Citation analysis
    from citation_analyzer import get_forward_citations, get_backward_citations
    appln_ids = ree_data['appln_id'].tolist()
    
    print("\n🔍 Analyzing Citations...")
    forward_cit = get_forward_citations(db, appln_ids, test_mode)
    backward_cit = get_backward_citations(db, appln_ids, test_mode)
    
    # Step 4: Geographic enrichment
    from geographic_enricher import enrich_with_geographic_data
    print("\n🌍 Adding Geographic Intelligence...")
    enriched_ree = enrich_with_geographic_data(db, ree_data)
    
    # Step 5: Quality validation
    from data_validator import validate_dataset_quality
    print("\n✅ Quality Assessment...")
    quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
    
    print("\n" + "=" * 50)
    print("✅ ANALYSIS COMPLETE")
    
    return {
        'ree_dataset': enriched_ree,
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'quality_metrics': quality_metrics
    }
```

## Visualization & Presentation

### Executive Dashboard Components
1. **Overview Panel**: Key metrics and quality score
2. **Geographic Analysis**: Country distribution and innovation clusters
3. **Citation Network**: Technology transfer visualization
4. **Trend Analysis**: Evolution over 2014-2024 timeframe

### Export Capabilities
- **CSV**: Stakeholder reports and further analysis
- **JSON**: API integration and data exchange
- **PNG/SVG**: High-quality presentation graphics
- **HTML**: Interactive dashboards

## Success Criteria

### Quality Targets
- **Minimum viable**: 200+ applications, 100+ citations, 5+ countries
- **Good analysis**: 500+ applications, 500+ citations, 10+ countries  
- **Excellent coverage**: 1000+ applications, 1000+ citations, 15+ countries

### Business Value
- **Cost Comparison**: €15,000-20,000 commercial equivalent vs TIP access + analyst time
- **Template Value**: Reusable across technology domains
- **Stakeholder Impact**: Executive-ready insights and recommendations

## Implementation Best Practices

### Critical Development Order
1. **database_connection.py** - Foundation (test connectivity first)
2. **dataset_builder.py** - Core search functionality
3. **citation_analyzer.py** - Citation intelligence (remember publication linkage)
4. **geographic_enricher.py** - Geographic context
5. **data_validator.py** - Quality assurance
6. **integrated_pipeline.py** - End-to-end testing
7. **Final notebook** - Professional presentation

### Common Troubleshooting
- **Empty citations**: Verify publication linkage, not direct application IDs
- **Low quality score**: Expand timeframe or broaden search terms
- **Missing geographic data**: Check person-application table joins
- **Performance issues**: Use test_mode=True for development

### Testing Strategy
```bash
# Component testing
python database_connection.py      # Verify TIP access
python dataset_builder.py          # Test search strategies
python citation_analyzer.py        # Validate citation logic
python integrated_pipeline.py      # Full pipeline test
```

## Final Presentation Structure

**REE_Citation_Analysis_Demo.ipynb**:
- **Executive Summary**: Business context and key findings
- **Methodology**: Search strategy and data sources
- **Results**: Interactive visualizations and insights
- **Business Intelligence**: Geographic hotspots and market opportunities
- **Conclusions**: Strategic recommendations and next steps

---

**Template Status**: Professional-grade, balanced implementation guide  
**Analysis Scope**: 2014-2024 comprehensive REE patent intelligence  
**Quality Focus**: Business-ready deliverables with proven methodology  
**Target Audience**: PATLIB community and patent information professionals