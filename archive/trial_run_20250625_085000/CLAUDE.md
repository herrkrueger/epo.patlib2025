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
- **Development Strategy**: Build and test components in Python scripts first, then create final Jupyter notebook
- **Format**: Modular Python scripts (.py) for development, final Jupyter Notebook (.ipynb) for presentation
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
Implement a second search with these corrected CPC codes:

```
A43B1/12, B03B9/06, B22F8, B29B7/66, B29B17, B30B9/32, B62D67, B65H73, 
B65D65/46, C03B1/02, C04B7/24, C04B7/26, C04B7/28, C04B7/30, C04B11/26, 
C04B18/04, C04B18/305, C04B33/132, C08J11, C09K11/01, C10M175, C22B7, 
C22B19/28, C22B19/30, C22B25/06, D01G11, D21B1/08, D21B1/10, D21B1/32, 
D21C5/02, D21H17/01, H01B15/00, H01J9/52, H01M6/52, H01M10/54, Y02W30/52, 
Y02W30/56, Y02W30/58, Y02W30/60, Y02W30/62, Y02W30/64, Y02W30/66, Y02W30/74, 
Y02W30/78, Y02W30/80, Y02W30/82, Y02W30/84, Y02W30/91, Y02P10/20
```

### 3. Core Dataset Construction

#### Step 1: High-Quality REE Family Identification

Implement using direct SQL queries:
1. Keywords-based family identification (TLS203_APPLN_ABSTR, TLS202_APPLN_TITLE)
2. Classification-based identification (TLS209_APPLN_IPC or TLS224_APPLN_CPC)
3. Intersection for high-quality dataset

#### Step 2: Create a summary of the created dataset
Create an easy to understand summary of the results. 
Optional: create easy to understand charts, that show the content of the dataset.

#### Step 3: Citation Network Expansion
```sql
-- Forward Citations (who cites our REE patents?)
-- Query TLS212_CITATION where REE patents appear in cited_pat_publn_id or cited_appln_id

-- Backward Citations (what our REE patents cite)
-- Query TLS212_CITATION where REE patents appear in pat_publn_id

-- Family-level citations using TLS228_DOCDB_FAM_CITN (recommended)
-- More robust for technology intelligence analysis

-- Citation quality using TLS215_CITN_CATEG
-- Categories: X (highly relevant), Y (relevant combined), A (general state of art)
```

#### Step 4: Country data
```sql
-- Join with TLS801_COUNTRY, TLS206_PERSON, TLS227_PERS_PUBLN tables
-- Create meaningful country-level analysis and visualizations
-- Answer: which country cites which applicants and which country gets cited
```

## 4. Development Strategy & Workflow

### Why Use This Approach?
Jupyter notebooks can be challenging to debug when working with complex database queries and large datasets. Our strategy breaks down the work into manageable, testable pieces that can be developed and verified step-by-step.

### Development Phases

#### Phase 1: Build & Test Components (Python Scripts)
Create individual Python scripts that focus on one task each:

```
📁 ree_patent_analysis/
├── 01_database_connection.py      # Test TIP platform connection
├── 02_ree_dataset_builder.py      # Build REE patent dataset
├── 03_citation_analyzer.py        # Analyze citation networks
├── 04_geographic_enricher.py      # Add country analysis
├── 05_data_validator.py           # Check data quality
└── utils/
    ├── sql_queries.py              # Reusable SQL query templates
    └── config.py                   # Settings and parameters
```

**Benefits of this approach:**
- **Easier debugging**: Test each component independently
- **Faster development**: Fix problems quickly without rerunning everything
- **Better understanding**: See exactly what each step does
- **Reusable code**: Functions work in multiple contexts

#### Phase 2: Integration Testing
```
06_integrated_pipeline.py          # Combine all components together
```
Test that all components work together before creating the final presentation.

#### Phase 3: Final Presentation Notebook
```
REE_Citation_Analysis_Demo.ipynb   # Professional presentation with visualizations
```
Focus the notebook on:
- Clear explanations for stakeholders
- Professional visualizations
- Business insights and recommendations
- Easy-to-understand results

### Development Process
1. **Start Small**: Test with small datasets (100-1000 records)
2. **Verify Each Step**: Make sure each component works before moving to the next
3. **Scale Gradually**: Increase dataset size once logic is proven
4. **Create Presentation**: Build final notebook using tested components

## 5. Detailed Implementation Structure

### Component 1: Database Connection Testing (01_database_connection.py)

**Purpose**: Verify that TIP platform connection works properly

```python
# 1.1 TIP PATSTAT Database Connection Setup (VERIFIED APPROACH)
from epo.tipdata.patstat import PatstatClient
import pandas as pd
import numpy as np
from datetime import datetime

def test_tip_connection():
    """Test TIP platform connection using verified pattern"""
    print("Libraries imported successfully!")
    print(f"Analysis started at: {datetime.now()}")
    
    # Initialize PATSTAT client for TIP platform - VERIFIED PATTERN
    environment = 'TEST'  # Start with TEST environment for development
    print(f"Connecting to PATSTAT {environment} environment...")
    
    try:
        patstat = PatstatClient(env=environment)
        db = patstat.orm()
        
        print(f"✅ Connected to PATSTAT {environment} environment")
        print(f"Database engine: {db.bind}")
        
        # Simple test query using direct SQL - SAFE APPROACH
        test_query = """
        SELECT appln_id, appln_auth, appln_filing_year 
        FROM tls201_appln 
        WHERE appln_filing_year >= 2020
        LIMIT 5
        """
        
        test_result = pd.read_sql(test_query, db.bind)
        print(f"✅ Test query successful: Retrieved {len(test_result)} sample records")
        print("Sample data:", test_result.head())
        
        return db
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

if __name__ == "__main__":
    db = test_tip_connection()
```

### Component 2: REE Dataset Builder (02_ree_dataset_builder.py)

**Purpose**: Create high-quality REE patent dataset using keywords and classification codes

```python
# 2.1 REE Dataset Construction using Direct SQL
def build_ree_dataset(db, test_mode=True):
    """
    Build REE patent dataset using keyword and classification intersection
    test_mode: If True, limits results for faster testing
    Uses direct SQL queries to avoid ORM complications
    """
    
    print(f"Building REE dataset (test_mode: {test_mode})...")
    
    # Step 1: Keyword-based search using direct SQL
    keyword_query = """
    SELECT DISTINCT 
        a.appln_id,
        a.docdb_family_id,
        a.appln_filing_year,
        a.appln_auth,
        t.appln_title,
        ab.appln_abstract
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        LOWER(t.appln_title) LIKE '%rare earth%' OR
        LOWER(t.appln_title) LIKE '%neodymium%' OR
        LOWER(t.appln_title) LIKE '%dysprosium%' OR
        LOWER(t.appln_title) LIKE '%lanthanide%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth element%' OR
        LOWER(ab.appln_abstract) LIKE '%rare earth metal%' OR
        LOWER(ab.appln_abstract) LIKE '%REE recovery%' OR
        LOWER(ab.appln_abstract) LIKE '%lanthanide%'
    )
    AND a.appln_filing_year >= 2014
    AND a.appln_filing_year <= 2024
    """
    
    if test_mode:
        keyword_query += " LIMIT 1000"
    
    print("Executing keyword-based search...")
    keyword_results = pd.read_sql(keyword_query, db.bind)
    print(f"Found {len(keyword_results)} patents with REE keywords")
    
    # Step 2: Classification-based search using direct SQL
    classification_query = """
    SELECT DISTINCT 
        a.appln_id,
        a.docdb_family_id,
        a.appln_filing_year,
        a.appln_auth,
        cpc.cpc_class_symbol
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    WHERE (
        cpc.cpc_class_symbol LIKE 'C22B7%' OR
        cpc.cpc_class_symbol LIKE 'C22B19/28%' OR
        cpc.cpc_class_symbol LIKE 'C22B19/30%' OR
        cpc.cpc_class_symbol LIKE 'C22B25/06%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30/52%' OR
        cpc.cpc_class_symbol LIKE 'Y02W30/84%' OR
        cpc.cpc_class_symbol LIKE 'Y02P10/20%'
    )
    AND a.appln_filing_year >= 2014
    AND a.appln_filing_year <= 2024
    """
    
    if test_mode:
        classification_query += " LIMIT 1000"
    
    print("Executing classification-based search...")
    classification_results = pd.read_sql(classification_query, db.bind)
    print(f"Found {len(classification_results)} patents with REE classifications")
    
    # Step 3: Create intersection for high-quality dataset
    common_appln_ids = set(keyword_results['appln_id']).intersection(
        set(classification_results['appln_id'])
    )
    
    if common_appln_ids:
        # Get detailed data for intersection
        intersection_query = f"""
        SELECT DISTINCT 
            a.appln_id,
            a.docdb_family_id,
            a.appln_filing_year,
            a.appln_auth,
            t.appln_title,
            ab.appln_abstract
        FROM tls201_appln a
        LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
        LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
        WHERE a.appln_id IN ({','.join(map(str, common_appln_ids))})
        """
        
        high_quality_ree = pd.read_sql(intersection_query, db.bind)
        print(f"High-quality REE dataset: {len(high_quality_ree)} patents (intersection)")
        return high_quality_ree
    else:
        print("No intersection found, using keyword results")
        return keyword_results

def validate_ree_dataset(ree_df):
    """Validate the quality and coverage of REE dataset"""
    print(f"\nDataset Validation Report:")
    print(f"- Total applications: {len(ree_df)}")
    print(f"- Total families: {ree_df['docdb_family_id'].nunique()}")
    print(f"- Date range: {ree_df['appln_filing_year'].min()} - {ree_df['appln_filing_year'].max()}")
    print(f"- Top countries: {ree_df['appln_auth'].value_counts().head(5).to_dict()}")
    print(f"- Years with most patents: {ree_df['appln_filing_year'].value_counts().head(3).to_dict()}")
    
if __name__ == "__main__":
    from database_connection import test_tip_connection
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        validate_ree_dataset(ree_data)
```

### Component 3: Citation Network Analysis (03_citation_analyzer.py)

**Purpose**: Analyze forward and backward citation patterns for REE patents

```python
# 3.1 Citation Analysis using Direct SQL Queries
def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """
    Find all patents that cite our REE patents (forward citations)
    Uses direct SQL to avoid ORM complications
    """
    
    if not ree_appln_ids:
        print("No REE application IDs provided")
        return pd.DataFrame()
    
    # Convert to comma-separated string for SQL IN clause
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Forward citations: Find patents that cite our REE patents
    forward_query = f"""
    SELECT 
        c.pat_publn_id as citing_publn_id,
        c.cited_appln_id as cited_ree_appln_id,
        c.citn_origin,
        c.citn_gener_auth,
        p.publn_auth as citing_country,
        a.appln_filing_year as citing_year,
        a.docdb_family_id as citing_family_id
    FROM tls212_citation c
    JOIN tls211_pat_publn p ON c.pat_publn_id = p.pat_publn_id
    JOIN tls201_appln a ON p.appln_id = a.appln_id
    WHERE c.cited_appln_id IN ({appln_ids_str})
    AND c.citn_origin = 'SEA'  -- Focus on search report citations
    """
    
    if test_mode:
        forward_query += " LIMIT 5000"
    
    print("Analyzing forward citations...")
    forward_citations = pd.read_sql(forward_query, db.bind)
    print(f"Found {len(forward_citations)} forward citations")
    
    return forward_citations

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """
    Find all patents/literature cited by our REE patents (backward citations)
    Uses direct SQL to avoid ORM complications
    """
    
    if not ree_appln_ids:
        print("No REE application IDs provided")
        return pd.DataFrame()
    
    # Get publication IDs for REE applications
    publn_query = f"""
    SELECT pat_publn_id, appln_id
    FROM tls211_pat_publn
    WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    """
    
    ree_publications = pd.read_sql(publn_query, db.bind)
    
    if ree_publications.empty:
        print("No publications found for REE applications")
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
    
    # Backward citations: Find what our REE patents cite
    backward_query = f"""
    SELECT 
        c.pat_publn_id as ree_citing_publn_id,
        c.cited_pat_publn_id,
        c.cited_appln_id,
        c.cited_npl_publn_id,
        c.citn_origin,
        p_cited.publn_auth as cited_country
    FROM tls212_citation c
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND c.citn_origin = 'SEA'  -- Focus on search report citations
    """
    
    if test_mode:
        backward_query += " LIMIT 5000"
    
    print("Analyzing backward citations...")
    backward_citations = pd.read_sql(backward_query, db.bind)
    print(f"Found {len(backward_citations)} backward citations")
    
    return backward_citations

def get_family_level_citations(db, ree_family_ids, test_mode=True):
    """
    Family-to-family citation analysis using TLS228_DOCDB_FAM_CITN
    Recommended approach for technology intelligence
    """
    
    if not ree_family_ids:
        print("No REE family IDs provided")
        return pd.DataFrame()
    
    family_ids_str = ','.join(map(str, ree_family_ids))
    
    # Family-level forward citations
    family_query = f"""
    SELECT 
        fc.cited_docdb_family_id as cited_ree_family_id,
        fc.docdb_family_id as citing_family_id,
        COUNT(*) as citation_count
    FROM tls228_docdb_fam_citn fc
    WHERE fc.cited_docdb_family_id IN ({family_ids_str})
    GROUP BY fc.cited_docdb_family_id, fc.docdb_family_id
    """
    
    if test_mode:
        family_query += " LIMIT 3000"
    
    print("Analyzing family-level citations...")
    family_citations = pd.read_sql(family_query, db.bind)
    print(f"Found {len(family_citations)} family citation relationships")
    
    return family_citations

if __name__ == "__main__":
    # Test citation analysis with sample data
    print("Testing citation analysis...")
    from database_connection import test_tip_connection
    from ree_dataset_builder import build_ree_dataset
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:100]  # Test with first 100
            family_ids = ree_data['docdb_family_id'].dropna().tolist()[:100]
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            family_cit = get_family_level_citations(db, family_ids, test_mode=True)
```

### Component 4: Geographic Analysis (04_geographic_enricher.py)

**Purpose**: Add country-level analysis to understand geographic patterns

```python
# 4.1 Geographic Data Enhancement using Direct SQL
def enrich_with_geographic_data(db, ree_df):
    """
    Add country codes and geographic information
    Uses direct SQL queries to avoid ORM complications
    """
    
    if ree_df.empty:
        print("No REE data provided for geographic enrichment")
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # Get geographic data through person-application links
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.iso_alpha3,
        c.st3_name as country_name,
        pa.applt_seq_nr
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0  -- Only applicants, not inventors
    """
    
    print("Enriching with geographic data...")
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        # Merge with REE data
        enriched_df = ree_df.merge(
            geo_data, 
            on='appln_id', 
            how='left'
        )
        print(f"Geographic enrichment: {len(geo_data)} geographic records added")
        return enriched_df
    else:
        print("No geographic data found")
        return ree_df

def analyze_country_citations(forward_citations_df, backward_citations_df):
    """
    Analyze citation flows between countries
    Uses direct DataFrame operations
    """
    
    print("\nCountry Citation Analysis:")
    
    if not forward_citations_df.empty:
        # Top citing countries
        top_citing = forward_citations_df['citing_country'].value_counts().head(10)
        print(f"Top citing countries: {top_citing.to_dict()}")
        
        # Citation flows (if we have both citing and cited country data)
        if 'cited_country' in forward_citations_df.columns:
            citation_flows = forward_citations_df.groupby(
                ['citing_country', 'cited_country']
            ).size().reset_index(name='citation_count')
            
            print(f"Citation flows identified: {len(citation_flows)} country pairs")
            return citation_flows, top_citing
    
    return pd.DataFrame(), pd.Series()

def create_country_summary(enriched_ree_df):
    """Create summary statistics by country"""
    
    if 'country_name' not in enriched_ree_df.columns:
        print("No country data available for summary")
        return pd.DataFrame()
    
    country_summary = enriched_ree_df.groupby('country_name').agg({
        'appln_id': 'count',
        'docdb_family_id': 'nunique',
        'appln_filing_year': ['min', 'max']
    }).round(2)
    
    country_summary.columns = ['total_applications', 'unique_families', 'first_year', 'last_year']
    country_summary = country_summary.sort_values('total_applications', ascending=False)
    
    print(f"\nCountry Summary (Top 10):")
    print(country_summary.head(10))
    
    return country_summary

if __name__ == "__main__":
    # Test geographic analysis
    print("Testing geographic enrichment...")
    from database_connection import test_tip_connection
    from ree_dataset_builder import build_ree_dataset
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            enriched_data = enrich_with_geographic_data(db, ree_data)
            country_summary = create_country_summary(enriched_data)
```

### Component 5: Data Validation (05_data_validator.py)

**Purpose**: Ensure data quality and provide summary statistics

```python
# 5.1 Data Quality Validation using Direct DataFrame Operations
def validate_dataset_quality(ree_df, forward_citations_df, backward_citations_df):
    """
    Comprehensive quality checks for REE patent dataset
    Uses direct DataFrame operations
    """
    
    quality_metrics = {}
    
    # Dataset size validation
    quality_metrics['total_applications'] = len(ree_df)
    quality_metrics['total_families'] = ree_df['docdb_family_id'].nunique() if 'docdb_family_id' in ree_df.columns else 0
    quality_metrics['total_forward_citations'] = len(forward_citations_df)
    quality_metrics['total_backward_citations'] = len(backward_citations_df)
    
    # Temporal distribution
    if 'appln_filing_year' in ree_df.columns:
        quality_metrics['year_range'] = f"{ree_df['appln_filing_year'].min()} - {ree_df['appln_filing_year'].max()}"
        quality_metrics['avg_patents_per_year'] = ree_df['appln_filing_year'].value_counts().mean()
    
    # Geographic coverage
    if 'appln_auth' in ree_df.columns:
        quality_metrics['countries_covered'] = ree_df['appln_auth'].nunique()
    
    # Citation rates
    if not forward_citations_df.empty and 'cited_ree_appln_id' in forward_citations_df.columns:
        cited_patents = forward_citations_df['cited_ree_appln_id'].nunique()
        quality_metrics['forward_citation_rate'] = f"{(cited_patents / len(ree_df) * 100):.1f}%"
    
    print("\n" + "="*50)
    print("DATASET QUALITY REPORT")
    print("="*50)
    for metric, value in quality_metrics.items():
        print(f"- {metric.replace('_', ' ').title()}: {value}")
    print("="*50)
    
    return quality_metrics

def generate_summary_report(ree_df, forward_citations_df, backward_citations_df, quality_metrics):
    """
    Generate business-friendly summary of findings
    """
    
    summary = {
        'executive_summary': {
            'total_ree_applications': quality_metrics.get('total_applications', 0),
            'total_ree_families': quality_metrics.get('total_families', 0),
            'date_coverage': quality_metrics.get('year_range', 'Unknown'),
            'countries_analyzed': quality_metrics.get('countries_covered', 0)
        },
        'citation_insights': {
            'forward_citations': quality_metrics.get('total_forward_citations', 0),
            'backward_citations': quality_metrics.get('total_backward_citations', 0),
            'citation_rate': quality_metrics.get('forward_citation_rate', 'N/A')
        }
    }
    
    # Add top countries if available
    if 'appln_auth' in ree_df.columns:
        summary['top_countries'] = ree_df['appln_auth'].value_counts().head(5).to_dict()
    
    # Add temporal trends if available
    if 'appln_filing_year' in ree_df.columns:
        summary['temporal_trends'] = ree_df['appln_filing_year'].value_counts().sort_index().tail(5).to_dict()
    
    print("\n" + "="*50)
    print("BUSINESS SUMMARY REPORT")
    print("="*50)
    print(f"REE Patent Landscape Analysis Results:")
    print(f"• Total REE Applications: {summary['executive_summary']['total_ree_applications']}")
    print(f"• Unique Patent Families: {summary['executive_summary']['total_ree_families']}")
    print(f"• Time Period: {summary['executive_summary']['date_coverage']}")
    print(f"• Countries Involved: {summary['executive_summary']['countries_analyzed']}")
    print(f"• Forward Citations Found: {summary['citation_insights']['forward_citations']}")
    print(f"• Citation Rate: {summary['citation_insights']['citation_rate']}")
    
    if 'top_countries' in summary:
        print(f"• Top Filing Countries: {list(summary['top_countries'].keys())[:3]}")
    
    print("="*50)
    
    return summary

if __name__ == "__main__":
    # Test validation functions
    print("Testing data validation...")
    from database_connection import test_tip_connection
    from ree_dataset_builder import build_ree_dataset
    from citation_analyzer import get_forward_citations, get_backward_citations
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:50]  # Test with subset
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            quality_metrics = validate_dataset_quality(ree_data, forward_cit, backward_cit)
            summary_report = generate_summary_report(ree_data, forward_cit, backward_cit, quality_metrics)
```

### Integration Pipeline (06_integrated_pipeline.py)

**Purpose**: Test that all components work together before creating the final notebook

```python
# 6.1 Complete Pipeline Integration using Safe Direct SQL Approach
def run_complete_ree_analysis(test_mode=True):
    """
    Run the complete REE patent citation analysis pipeline
    Uses direct SQL queries throughout to avoid ORM complications
    """
    
    print("="*60)
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("="*60)
    
    # Step 1: Connect to database
    print("\n1. 🔗 Connecting to TIP platform...")
    from database_connection import test_tip_connection
    db = test_tip_connection()
    if not db:
        print("❌ Database connection failed - stopping pipeline")
        return None
    
    # Step 2: Build REE dataset
    print("\n2. 🔍 Building REE dataset...")
    from ree_dataset_builder import build_ree_dataset, validate_ree_dataset
    ree_data = build_ree_dataset(db, test_mode=test_mode)
    if ree_data.empty:
        print("❌ No REE data found - stopping pipeline")
        return None
    validate_ree_dataset(ree_data)
    
    # Step 3: Analyze citations
    print("\n3. 📊 Analyzing citation networks...")
    from citation_analyzer import get_forward_citations, get_backward_citations, get_family_level_citations
    
    # Extract necessary IDs from REE dataset
    appln_ids = ree_data['appln_id'].tolist()
    family_ids = ree_data['docdb_family_id'].dropna().tolist()
    
    # Get citations with proper error handling
    try:
        forward_cit = get_forward_citations(db, appln_ids, test_mode)
        backward_cit = get_backward_citations(db, appln_ids, test_mode)
        family_cit = get_family_level_citations(db, family_ids, test_mode)
    except Exception as e:
        print(f"⚠️ Citation analysis encountered issues: {e}")
        forward_cit = pd.DataFrame()
        backward_cit = pd.DataFrame()
        family_cit = pd.DataFrame()
    
    # Step 4: Add geographic data
    print("\n4. 🌍 Enriching with geographic data...")
    from geographic_enricher import enrich_with_geographic_data, analyze_country_citations, create_country_summary
    
    try:
        enriched_ree = enrich_with_geographic_data(db, ree_data)
        citation_flows, top_citing = analyze_country_citations(forward_cit, backward_cit)
        country_summary = create_country_summary(enriched_ree)
    except Exception as e:
        print(f"⚠️ Geographic analysis encountered issues: {e}")
        enriched_ree = ree_data
        citation_flows = pd.DataFrame()
        top_citing = pd.Series()
        country_summary = pd.DataFrame()
    
    # Step 5: Validate results
    print("\n5. ✅ Validating results...")
    from data_validator import validate_dataset_quality, generate_summary_report
    
    quality_metrics = validate_dataset_quality(enriched_ree, forward_cit, backward_cit)
    summary_report = generate_summary_report(enriched_ree, forward_cit, backward_cit, quality_metrics)
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE - ALL COMPONENTS WORKING!")
    print("="*60)
    
    # Return all results for use in notebook
    results = {
        'ree_dataset': enriched_ree,
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'family_citations': family_cit,
        'citation_flows': citation_flows,
        'country_summary': country_summary,
        'summary_report': summary_report,
        'quality_metrics': quality_metrics
    }
    
    print(f"\n📊 READY FOR NOTEBOOK CREATION!")
    print(f"• Dataset size: {len(results['ree_dataset'])} applications")
    print(f"• Families: {results['ree_dataset']['docdb_family_id'].nunique()} unique families")
    print(f"• Citations analyzed: {len(results['forward_citations'])} forward, {len(results['backward_citations'])} backward")
    print(f"• Countries: {results['ree_dataset']['appln_auth'].nunique()} filing authorities")
    
    return results

if __name__ == "__main__":
    # Run complete pipeline test
    print("🚀 Starting complete REE analysis pipeline test...")
    results = run_complete_ree_analysis(test_mode=True)
    
    if results:
        print("\n🎉 Pipeline test successful!")
        print("Ready to create presentation notebook with:")
        for key, value in results.items():
            if isinstance(value, pd.DataFrame):
                print(f"  - {key}: {len(value)} records")
            else:
                print(f"  - {key}: Available")
    else:
        print("\n❌ Pipeline test failed - check individual components")
```

### Final Presentation Notebook Structure

Once all components are tested and working, create the final Jupyter notebook:

#### REE_Citation_Analysis_Demo.ipynb

**Focus on presentation and visualization:**

```markdown
# REE Patent Citation Analysis for PATLIB Community

## Executive Summary
- Clear business context and value proposition
- Key findings presented upfront
- Strategic recommendations for patent professionals

## Methodology 
- Simple explanation of our approach
- Why this analysis matters for patent landscape intelligence
- Cost comparison vs. commercial solutions

## Data Sources & Quality
- PATSTAT database coverage and reliability
- REE patent identification methodology
- Citation analysis framework

## Results Visualizations
- Interactive dashboard with key metrics
- Citation network graph
- Country-level analysis charts
- Technology trend visualizations

## Business Insights
- Geographic hotspots for REE innovation
- Citation patterns and technology transfer flows
- Market opportunities and competitive landscape
- Strategic recommendations for stakeholders

## Technical Appendix
- Data sources and quality metrics
- Methodology details for technical audience
- Reproducibility notes
```

**Key Notebook Principles:**
- Import pre-tested functions from Python scripts using safe SQL approach
- Focus on storytelling and professional visualization
- Minimize data processing complexity in notebook cells
- Use clear, business-friendly language throughout
- Include executive summary tailored for decision-makers
- Demonstrate clear ROI vs. commercial patent analysis tools

## 6. Visualization Requirements

### Professional-grade visualizations for PATLIB presentations:

1. **Interactive Executive Dashboard**
   - Key metrics summary (total families, citations, countries)
   - Time-series trends of REE patent filings and citations
   - Top countries and applicants overview with market share

2. **Citation Network Graph** 
   - Visual representation of citation relationships between countries
   - Node sizes based on patent counts or citation volumes
   - Color coding for different regions or technology areas
   - Interactive hover details for deeper insights

3. **Geographic Analysis**
   - Interactive world map showing REE patent activity by country
   - Citation flow visualization between countries
   - Regional innovation hubs and collaboration patterns
   - Technology transfer routes identification

4. **Technology Landscape**
   - Classification co-occurrence analysis
   - Technology evolution timeline
   - Emerging REE application areas
   - Patent activity intensity by technology domain

**Implementation Notes:**
- Use Plotly for interactive charts suitable for web presentation and export
- Ensure charts work well in both light and dark themes
- Export options: PNG/SVG for presentations, HTML for interactive sharing
- Professional color schemes appropriate for business presentations
- Clear legends and annotations for non-technical stakeholders
- Mobile-friendly responsive design for tablet presentations

## 7. Output Specifications

### Datasets Produced
1. **Core REE Patent Dataset**: High-quality applications with keyword+classification intersection
2. **Forward Citation Network**: Patents citing REE technologies with geographic attribution
3. **Backward Citation Network**: Prior art cited by REE patents (patents and NPL)
4. **Citation Quality Analysis**: Categories and relevance scores from search reports
5. **Geographic Intelligence**: Country-level statistics with citation flows
6. **Technology Mapping**: Classification analysis with temporal trends

### Visualizations Delivered
1. **Executive Dashboard**: One-page summary for decision-makers
2. **Citation Network Graph**: Interactive visualization of citation relationships
3. **Geographic Analysis**: Country-level maps and flow diagrams
4. **Technology Trends**: Time-series and classification analytics
5. **Competitive Intelligence**: Market position and opportunity analysis

### Export Formats
- Excel files for business stakeholders and further analysis
- CSV files for data sharing and integration
- PNG/SVG files for presentations and reports
- Interactive HTML dashboards for web sharing
- PowerBI-compatible datasets for integration

## 8. Success Metrics & Validation

### Quality Assurance
- Dataset size validation (target: 1,000-10,000 high-quality families for meaningful analysis)
- Dataset timeframe: 2014-2024 (recent 10-year window for current relevance)
- Citation completeness using search report citations (TLS212_CITATION with citn_origin='SEA')
- Geographic coverage assessment via applicant country data
- Temporal distribution validation ensuring consistent data across years
- Citation direction validation (forward vs backward logic verification)
- Data consistency checks between application and family-level analyses

### Business Value Indicators
- Actionable insights for patent strategy and competitive intelligence
- Novel patterns discovery capability demonstrating advanced analytics
- Professional presentation quality suitable for stakeholder meetings
- Cost-effectiveness demonstration vs. commercial patent analysis tools
- Reproducibility and customization potential for other technology domains

## 9. Future Extensions & Modularity

### Extensibility Features
- Template approach for easy adaptation to other technology domains
- Modular SQL query structure for different search strategies
- Configurable parameters for timeframes, geographic regions, and technology codes
- Integration capabilities with external data sources and APIs

### Advanced Analytics Preparation
- Machine learning ready datasets with proper feature engineering
- Natural language processing preparation for patent text analysis
- Semantic analysis foundation for technology convergence studies
- Time-series forecasting capabilities for trend prediction
- Network analysis preparation for innovation ecosystem mapping

This comprehensive approach ensures both immediate practical value for PATLIB professionals and a solid foundation for advanced patent intelligence applications.