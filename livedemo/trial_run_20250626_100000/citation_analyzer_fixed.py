import pandas as pd

def get_forward_citations_fixed(db, ree_appln_ids, test_mode=True):
    """Find patents citing our REE patents - CORRECTED VERSION"""
    
    if not ree_appln_ids:
        print("⚠️ No application IDs provided for forward citation analysis")
        return pd.DataFrame()
    
    print(f"🔍 Analyzing forward citations for {len(ree_appln_ids)} REE applications...")
    
    # CORRECTED APPROACH: Citations work via publications, not directly via applications
    # Step 1: Get publication IDs for our REE applications
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Get all publications for our REE applications
    ree_publications_query = f"""
    SELECT 
        appln_id as ree_appln_id,
        pat_publn_id as ree_publn_id,
        publn_auth,
        publn_kind
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
            ree_pub.ree_appln_id
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
        
        # Add citation origin filter (try both SEA and APP)
        if test_mode:
            forward_query += " AND c.citn_origin IN ('SEA', 'APP') LIMIT 2000"
        else:
            forward_query += " AND c.citn_origin IN ('SEA', 'APP')"
        
        forward_citations = pd.read_sql(forward_query, db.bind)
        
        if forward_citations.empty:
            # Try without citation origin filter
            print("ℹ️  No citations with SEA/APP origin, trying all citation types...")
            
            forward_query_all = f"""
            SELECT 
                c.pat_publn_id as citing_publn_id,
                c.cited_pat_publn_id as cited_ree_publn_id,
                p_citing.appln_id as citing_appln_id,
                p_citing.publn_auth as citing_country,
                a_citing.appln_filing_year as citing_year,
                c.citn_origin,
                ree_pub.ree_appln_id
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
                forward_query_all += " LIMIT 2000"
            
            forward_citations = pd.read_sql(forward_query_all, db.bind)
        
        if forward_citations.empty:
            print("ℹ️  No forward citations found")
        else:
            print(f"✅ Found {len(forward_citations)} forward citations")
            
            # Show citation origin breakdown
            if 'citn_origin' in forward_citations.columns:
                origin_counts = forward_citations['citn_origin'].value_counts()
                print(f"   Citation origins: {origin_counts.to_dict()}")
            
            # Show temporal distribution
            if 'citing_year' in forward_citations.columns:
                year_counts = forward_citations['citing_year'].value_counts().sort_index()
                print(f"   Citing years: {year_counts.head().to_dict()}")
        
        return forward_citations
        
    except Exception as e:
        print(f"⚠️ Forward citation query failed: {e}")
        return pd.DataFrame()

def test_fixed_forward_citations():
    """Test the fixed forward citation function"""
    
    from database_connection import test_tip_connection
    
    print("🧪 TESTING FIXED FORWARD CITATION FUNCTION")
    print("=" * 50)
    
    db = test_tip_connection()
    if not db:
        return
    
    # Get some sample REE applications from earlier years (more likely to have citations)
    sample_query = """
    SELECT DISTINCT a.appln_id
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    WHERE LOWER(t.appln_title) LIKE '%rare earth%'
    AND a.appln_filing_year BETWEEN 2010 AND 2018
    LIMIT 20
    """
    
    try:
        sample_apps = pd.read_sql(sample_query, db.bind)
        print(f"📋 Testing with {len(sample_apps)} sample REE applications (2010-2018)")
        
        if not sample_apps.empty:
            test_appln_ids = sample_apps['appln_id'].tolist()
            
            # Test fixed function
            forward_cit = get_forward_citations_fixed(db, test_appln_ids, test_mode=True)
            
            print(f"\n📊 RESULTS:")
            print(f"   Forward citations found: {len(forward_cit)}")
            
            if not forward_cit.empty:
                print(f"   Sample citations:")
                for i, row in forward_cit.head(3).iterrows():
                    print(f"     REE App {row['ree_appln_id']} cited by App {row['citing_appln_id']} ({row['citing_year']}) via {row['citn_origin']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_fixed_forward_citations()