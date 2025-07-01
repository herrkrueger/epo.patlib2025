import pandas as pd

def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """Find patents citing our REE patents - CORRECTED VERSION"""
    
    if not ree_appln_ids:
        print("⚠️ No application IDs provided for forward citation analysis")
        return pd.DataFrame()
    
    print(f"🔍 Analyzing forward citations for {len(ree_appln_ids)} REE applications...")
    
    # CORRECTED: Citations work via publications, not directly via applications
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Step 1: Get publication IDs for our REE applications
    ree_publications_query = f"""
    SELECT 
        appln_id as ree_appln_id,
        pat_publn_id as ree_publn_id
    FROM tls211_pat_publn
    WHERE appln_id IN ({appln_ids_str})
    """
    
    try:
        ree_publications = pd.read_sql(ree_publications_query, db.bind)
        
        if ree_publications.empty:
            print("ℹ️  No publications found for REE applications")
            return pd.DataFrame()
        
        print(f"📄 Found {len(ree_publications)} publications for REE applications")
        
        # Step 2: Find citations to these publications
        ree_publn_ids = ree_publications['ree_publn_id'].tolist()
        publn_ids_str = ','.join(map(str, ree_publn_ids))
        
        # Forward citations query - find patents that cite our REE publications
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
        JOIN (
            SELECT 
                pat_publn_id as ree_publn_id,
                appln_id as ree_appln_id
            FROM tls211_pat_publn
            WHERE appln_id IN ({appln_ids_str})
        ) ree_pub ON c.cited_pat_publn_id = ree_pub.ree_publn_id
        WHERE c.cited_pat_publn_id IN ({publn_ids_str})
        AND a_citing.appln_filing_year >= 2010
        """
        
        if test_mode:
            forward_query += " LIMIT 2000"
        
        forward_citations = pd.read_sql(forward_query, db.bind)
        
        if forward_citations.empty:
            print("ℹ️  No forward citations found")
        else:
            print(f"✅ Found {len(forward_citations)} forward citations")
            
            # Show citation origin breakdown
            if 'citn_origin' in forward_citations.columns:
                origin_counts = forward_citations['citn_origin'].value_counts()
                print(f"   Citation origins: {origin_counts.to_dict()}")
        
        return forward_citations
        
    except Exception as e:
        print(f"⚠️ Forward citation query failed: {e}")
        return pd.DataFrame()

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """Find patents/literature cited by our REE patents"""
    
    if not ree_appln_ids:
        print("⚠️ No application IDs provided for backward citation analysis")
        return pd.DataFrame()
    
    # Get publication IDs
    publn_query = f"""
    SELECT pat_publn_id FROM tls211_pat_publn
    WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    """
    
    try:
        ree_publications = pd.read_sql(publn_query, db.bind)
        
        if ree_publications.empty:
            print("ℹ️  No publications found for backward citation analysis")
            return pd.DataFrame()
        
        publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
        
        # Backward citations - include citation origin for analysis
        backward_query = f"""
        SELECT 
            c.pat_publn_id as ree_citing_publn_id,
            c.cited_pat_publn_id,
            c.cited_appln_id,
            c.citn_origin,
            p_cited.publn_auth as cited_country
        FROM tls212_citation c
        LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
        WHERE c.pat_publn_id IN ({publn_ids_str})
        """
        
        if test_mode:
            backward_query += " LIMIT 1000"
        
        backward_citations = pd.read_sql(backward_query, db.bind)
        
        if backward_citations.empty:
            print("ℹ️  No backward citations found")
        else:
            print(f"Found {len(backward_citations)} backward citations")
        
        return backward_citations
        
    except Exception as e:
        print(f"⚠️ Backward citation query failed: {e}")
        return pd.DataFrame()

def analyze_citation_patterns(forward_citations_df, backward_citations_df):
    """Analyze citation patterns and trends with comprehensive citation origin analysis"""
    
    analysis_results = {}
    
    # Forward citation analysis
    if not forward_citations_df.empty:
        analysis_results['forward_citing_countries'] = forward_citations_df['citing_country'].value_counts().head(10)
        analysis_results['forward_citing_years'] = forward_citations_df['citing_year'].value_counts().sort_index()
        print(f"Forward citations by country (top 5): {analysis_results['forward_citing_countries'].head().to_dict()}")
        
        # Citation origin analysis for forward citations
        if 'citn_origin' in forward_citations_df.columns:
            analysis_results['forward_citation_origins'] = forward_citations_df['citn_origin'].value_counts()
            print(f"Forward citation origins: {analysis_results['forward_citation_origins'].to_dict()}")
    
    # Backward citation analysis
    if not backward_citations_df.empty:
        analysis_results['backward_cited_countries'] = backward_citations_df['cited_country'].value_counts().head(10)
        print(f"Backward citations by country (top 5): {analysis_results['backward_cited_countries'].head().to_dict()}")
        
        # Citation origin analysis for backward citations
        if 'citn_origin' in backward_citations_df.columns:
            analysis_results['backward_citation_origins'] = backward_citations_df['citn_origin'].value_counts()
            print(f"Backward citation origins: {analysis_results['backward_citation_origins'].to_dict()}")
    
    return analysis_results

if __name__ == "__main__":
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            appln_ids = ree_data['appln_id'].tolist()
            
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            analysis = analyze_citation_patterns(forward_cit, backward_cit)
            print("Citation analysis completed!")