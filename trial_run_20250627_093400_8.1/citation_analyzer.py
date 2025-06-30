import pandas as pd
from database_connection import get_patstat_connection

def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """Find forward citations via correct publication linkage"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Step 1: Get publication IDs for REE applications
    ree_publications_query = f"""
    SELECT appln_id as ree_appln_id, pat_publn_id as ree_publn_id
    FROM tls211_pat_publn
    WHERE appln_id IN ({appln_ids_str})
    """
    
    print("🔍 Getting publication IDs for REE applications...")
    ree_publications = pd.read_sql(ree_publications_query, db.bind)
    
    if ree_publications.empty:
        print("❌ No publications found for forward citations")
        return pd.DataFrame()
    
    print(f"Found {len(ree_publications)} publications for {len(ree_appln_ids)} applications")
    
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
    AND a_citing.appln_filing_year >= 2010
    """
    
    if test_mode:
        forward_query += " LIMIT 2000"
    
    print("🔍 Analyzing forward citations...")
    forward_citations = pd.read_sql(forward_query, db.bind)
    
    if not forward_citations.empty:
        print(f"✅ Found {len(forward_citations)} forward citations")
        origin_counts = forward_citations['citn_origin'].value_counts()
        print(f"Citation Origins: {origin_counts.to_dict()}")
        
        # Citation analysis
        citing_countries = forward_citations['citing_country'].value_counts()
        print(f"Top Citing Countries: {citing_countries.head(5).to_dict()}")
        
        citing_years = forward_citations['citing_year'].value_counts().sort_index()
        print(f"Citation Years: {citing_years.tail(5).to_dict()}")
    else:
        print("❌ No forward citations found")
    
    return forward_citations

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """Find backward citations via publication linkage"""
    
    if not ree_appln_ids:
        return pd.DataFrame()
    
    # Get publication IDs for our REE patents
    publn_query = f"""
    SELECT pat_publn_id, appln_id FROM tls211_pat_publn
    WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    """
    
    print("🔍 Getting publication IDs for backward citation analysis...")
    ree_publications = pd.read_sql(publn_query, db.bind)
    
    if ree_publications.empty:
        print("❌ No publications found for backward citations")
        return pd.DataFrame()
    
    print(f"Found {len(ree_publications)} publications for backward citation analysis")
    
    publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
    
    # Backward citations
    backward_query = f"""
    SELECT 
        c.pat_publn_id as ree_citing_publn_id,
        c.cited_pat_publn_id,
        c.cited_appln_id,
        c.citn_origin,
        p_cited.publn_auth as cited_country,
        p_cited.publn_date as cited_publn_date,
        a_cited.appln_filing_year as cited_year,
        ree_pub.appln_id as ree_appln_id
    FROM tls212_citation c
    JOIN ({publn_query}) ree_pub ON c.pat_publn_id = ree_pub.pat_publn_id
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    LEFT JOIN tls201_appln a_cited ON c.cited_appln_id = a_cited.appln_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND (a_cited.appln_filing_year >= 2000 OR a_cited.appln_filing_year IS NULL)
    """
    
    if test_mode:
        backward_query += " LIMIT 2000"
    
    print("🔍 Analyzing backward citations...")
    backward_citations = pd.read_sql(backward_query, db.bind)
    
    if not backward_citations.empty:
        print(f"✅ Found {len(backward_citations)} backward citations")
        cited_years = backward_citations['cited_year'].dropna()
        if not cited_years.empty:
            print(f"Prior Art Range: {cited_years.min()}-{cited_years.max()}")
        
        # Citation origin analysis
        origin_counts = backward_citations['citn_origin'].value_counts()
        print(f"Citation Origins: {origin_counts.to_dict()}")
        
        # Technology heritage analysis
        cited_countries = backward_citations['cited_country'].value_counts()
        print(f"Cited Countries: {cited_countries.head(5).to_dict()}")
    else:
        print("❌ No backward citations found")
    
    return backward_citations

def analyze_citation_patterns(forward_cit_df, backward_cit_df):
    """Analyze citation patterns for insights"""
    
    citation_analysis = {}
    
    if not forward_cit_df.empty:
        citation_analysis['forward_citations'] = {
            'total_count': len(forward_cit_df),
            'unique_citing_patents': forward_cit_df['citing_appln_id'].nunique(),
            'citing_countries': forward_cit_df['citing_country'].nunique(),
            'citation_origins': forward_cit_df['citn_origin'].value_counts().to_dict()
        }
    
    if not backward_cit_df.empty:
        citation_analysis['backward_citations'] = {
            'total_count': len(backward_cit_df),
            'unique_cited_patents': backward_cit_df['cited_appln_id'].nunique(),
            'cited_countries': backward_cit_df['cited_country'].nunique(),
            'citation_origins': backward_cit_df['citn_origin'].value_counts().to_dict()
        }
    
    # Citation network metrics
    if not forward_cit_df.empty and not backward_cit_df.empty:
        citation_analysis['network_metrics'] = {
            'forward_backward_ratio': len(forward_cit_df) / len(backward_cit_df),
            'innovation_impact_score': len(forward_cit_df) * 0.7 + len(backward_cit_df) * 0.3
        }
    
    return citation_analysis

def get_citation_origins_reference():
    """Reference for citation origins in PATSTAT"""
    return {
        'SEA': 'Search Report',              # Official examiner citations
        'APP': 'Applicant',                 # Self-reported citations
        'ISR': 'International Search',      # PCT official citations
        'PRS': 'Prior Art Search',          # Systematic research
        'EXA': 'Examiner',                  # Direct examiner citations
        'FOP': 'Office Proceedings',        # Official proceedings
        'OPP': 'Opposition',                # Opposition citations
        'TPO': 'Third Party Observation',   # External input
        'APL': 'Appeal',                    # Appeal proceedings
        'SUP': 'Supplementary',             # Additional information
        'CH2': 'Chapter 2'                  # PCT Chapter 2
    }

def analyze_citations_for_ree_dataset(ree_appln_ids, test_mode=True):
    """Complete citation analysis for REE dataset"""
    
    print("REE CITATION ANALYSIS")
    print("=" * 40)
    
    db = get_patstat_connection()
    if not db:
        print("❌ Database connection failed")
        return None
    
    # Forward citations
    print("\n📈 FORWARD CITATION ANALYSIS")
    print("-" * 30)
    forward_cit = get_forward_citations(db, ree_appln_ids, test_mode)
    
    # Backward citations  
    print("\n📉 BACKWARD CITATION ANALYSIS")
    print("-" * 30)
    backward_cit = get_backward_citations(db, ree_appln_ids, test_mode)
    
    # Pattern analysis
    print("\n📊 CITATION PATTERN ANALYSIS")
    print("-" * 30)
    patterns = analyze_citation_patterns(forward_cit, backward_cit)
    
    for category, metrics in patterns.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
    
    return {
        'forward_citations': forward_cit,
        'backward_citations': backward_cit,
        'citation_patterns': patterns,
        'citation_origins_reference': get_citation_origins_reference()
    }

if __name__ == "__main__":
    print("Testing Citation Analyzer...")
    
    # Test with sample application IDs
    test_appln_ids = [123456, 234567, 345678]  # Replace with real IDs from dataset
    
    results = analyze_citations_for_ree_dataset(test_appln_ids, test_mode=True)
    
    if results:
        print("\n✅ Citation analysis complete!")
        print(f"Forward citations: {len(results['forward_citations'])}")
        print(f"Backward citations: {len(results['backward_citations'])}")
    else:
        print("❌ Citation analysis failed")