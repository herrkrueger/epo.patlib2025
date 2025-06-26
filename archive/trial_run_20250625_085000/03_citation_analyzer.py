# 3.1 Citation Analysis using Direct SQL Queries
import pandas as pd
from datetime import datetime

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
        a.docdb_family_id as citing_family_id,
        cat.citn_categ as citation_category
    FROM tls212_citation c
    JOIN tls211_pat_publn p ON c.pat_publn_id = p.pat_publn_id
    JOIN tls201_appln a ON p.appln_id = a.appln_id
    LEFT JOIN tls215_citn_categ cat ON c.pat_publn_id = cat.pat_publn_id 
        AND c.cited_pat_publn_id = cat.cited_pat_publn_id
    WHERE c.cited_appln_id IN ({appln_ids_str})
    AND c.citn_origin = 'SEA'
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
        p_cited.publn_auth as cited_country,
        a_cited.appln_filing_year as cited_year,
        cat.citn_categ as citation_category
    FROM tls212_citation c
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    LEFT JOIN tls201_appln a_cited ON p_cited.appln_id = a_cited.appln_id
    LEFT JOIN tls215_citn_categ cat ON c.pat_publn_id = cat.pat_publn_id 
        AND c.cited_pat_publn_id = cat.cited_pat_publn_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND c.citn_origin = 'SEA'
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
    ORDER BY citation_count DESC
    """
    
    if test_mode:
        family_query += " LIMIT 3000"
    
    print("Analyzing family-level citations...")
    family_citations = pd.read_sql(family_query, db.bind)
    print(f"Found {len(family_citations)} family citation relationships")
    
    return family_citations

def analyze_citation_patterns(forward_citations_df, backward_citations_df):
    """
    Analyze citation patterns for insights
    """
    
    print(f"\n{'='*50}")
    print("CITATION PATTERN ANALYSIS")
    print(f"{'='*50}")
    
    insights = {}
    
    if not forward_citations_df.empty:
        # Forward citation analysis
        insights['forward_citations_total'] = len(forward_citations_df)
        insights['unique_citing_patents'] = forward_citations_df['citing_publn_id'].nunique()
        insights['unique_cited_ree_patents'] = forward_citations_df['cited_ree_appln_id'].nunique()
        
        # Top citing countries
        if 'citing_country' in forward_citations_df.columns:
            top_citing_countries = forward_citations_df['citing_country'].value_counts().head(5)
            insights['top_citing_countries'] = top_citing_countries.to_dict()
            print(f"Top citing countries: {list(top_citing_countries.index)}")
        
        # Citation categories
        if 'citation_category' in forward_citations_df.columns:
            citation_categories = forward_citations_df['citation_category'].value_counts()
            insights['citation_categories'] = citation_categories.to_dict()
            print(f"Citation categories: {citation_categories.to_dict()}")
    
    if not backward_citations_df.empty:
        # Backward citation analysis
        insights['backward_citations_total'] = len(backward_citations_df)
        insights['unique_cited_patents'] = backward_citations_df['cited_pat_publn_id'].nunique()
        
        # Top cited countries
        if 'cited_country' in backward_citations_df.columns:
            top_cited_countries = backward_citations_df['cited_country'].value_counts().head(5)
            insights['top_cited_countries'] = top_cited_countries.to_dict()
            print(f"Top cited countries: {list(top_cited_countries.index)}")
    
    print(f"Forward citations: {insights.get('forward_citations_total', 0)}")
    print(f"Backward citations: {insights.get('backward_citations_total', 0)}")
    print(f"{'='*50}")
    
    return insights

if __name__ == "__main__":
    # Test citation analysis with sample data
    print("Testing citation analysis...")
    from database_connection import get_database_connection
    from ree_dataset_builder import build_ree_dataset
    
    db = get_database_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:100]  # Test with first 100
            family_ids = ree_data['docdb_family_id'].dropna().tolist()[:100]
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            family_cit = get_family_level_citations(db, family_ids, test_mode=True)
            
            insights = analyze_citation_patterns(forward_cit, backward_cit)