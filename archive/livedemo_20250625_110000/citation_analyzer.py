import pandas as pd
from database_connection import test_tip_connection
from dataset_builder import build_ree_dataset

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
    else:
        print(f"Found {len(forward_citations)} forward citations")
    
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
        print("ℹ️  No publications found for REE applications")
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
    
    backward_citations = pd.read_sql(backward_query, db.bind)
    
    if backward_citations.empty:
        print("ℹ️  No backward citations found")
    else:
        print(f"Found {len(backward_citations)} backward citations")
    
    return backward_citations

if __name__ == "__main__":
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            print(f"Citation analysis complete: {len(forward_cit)} forward, {len(backward_cit)} backward")