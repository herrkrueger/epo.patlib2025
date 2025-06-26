# Citation Analysis using Direct SQL Queries
import pandas as pd
import numpy as np
from database_connection import test_tip_connection

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
    
    # Forward citations: Find patents that cite our REE patents (2022-2024 timeframe)
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
    AND a.appln_filing_year >= 2022  -- Recent citations for 2023 REE patents
    """
    
    if test_mode:
        forward_query += " LIMIT 5000"
    
    print("Analyzing forward citations for 2023 REE patents...")
    forward_citations = pd.read_sql(forward_query, db.bind)
    print(f"Found {len(forward_citations)} forward citations from 2022-2024")
    
    if forward_citations.empty:
        print("ℹ️  No forward citations found - this is normal for recent 2023 patents")
        print("   Citations typically appear 1-2 years after filing due to publication delays")
    
    return forward_citations

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """
    Find all patents/literature cited by our REE patents (backward citations)
    Uses direct SQL to avoid ORM complications
    """
    
    if not ree_appln_ids:
        print("No REE application IDs provided")
        return pd.DataFrame()
    
    # VERIFIED: Get publication IDs for REE applications using confirmed table relationship
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
    
    # VERIFIED: Family-level forward citations using documented TLS228 table
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
    from dataset_builder import build_ree_dataset
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()[:100]  # Test with first 100
            family_ids = ree_data['docdb_family_id'].dropna().tolist()[:100]
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            family_cit = get_family_level_citations(db, family_ids, test_mode=True)