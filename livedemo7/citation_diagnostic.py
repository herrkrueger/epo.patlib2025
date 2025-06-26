"""
Citation Analysis Diagnostic Tool
Investigates why forward citations are not being found
"""

import pandas as pd
from database_connection import test_tip_connection

def diagnose_citation_issues():
    """Diagnose citation data availability and structure"""
    
    print("🔍 CITATION DIAGNOSTIC ANALYSIS")
    print("=" * 50)
    
    db = test_tip_connection()
    if not db:
        print("❌ Database connection failed")
        return
    
    # Step 1: Check TLS212_CITATION table structure and data availability
    print("\n1️⃣ CHECKING TLS212_CITATION TABLE:")
    citation_structure_query = """
    SELECT 
        COUNT(*) as total_citations,
        COUNT(DISTINCT citn_origin) as citation_origins,
        MIN(cited_appln_id) as min_appln_id,
        MAX(cited_appln_id) as max_appln_id
    FROM tls212_citation 
    WHERE cited_appln_id IS NOT NULL
    LIMIT 1
    """
    
    try:
        citation_stats = pd.read_sql(citation_structure_query, db.bind)
        print(f"✅ Total citations in database: {citation_stats.iloc[0]['total_citations']:,}")
        print(f"✅ Citation origins available: {citation_stats.iloc[0]['citation_origins']}")
        print(f"✅ Application ID range: {citation_stats.iloc[0]['min_appln_id']} - {citation_stats.iloc[0]['max_appln_id']}")
    except Exception as e:
        print(f"❌ Citation table check failed: {e}")
        return
    
    # Step 2: Check citation origins
    print("\n2️⃣ CHECKING CITATION ORIGINS:")
    origin_query = """
    SELECT citn_origin, COUNT(*) as count
    FROM tls212_citation
    GROUP BY citn_origin
    ORDER BY count DESC
    """
    
    try:
        origins = pd.read_sql(origin_query, db.bind)
        print("Citation origins found:")
        for _, row in origins.iterrows():
            print(f"   {row['citn_origin']}: {row['count']:,} citations")
    except Exception as e:
        print(f"❌ Citation origins check failed: {e}")
    
    # Step 3: Sample REE patents for testing
    print("\n3️⃣ GETTING SAMPLE REE PATENTS:")
    sample_ree_query = """
    SELECT DISTINCT 
        a.appln_id, a.appln_filing_year, a.appln_auth
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    WHERE LOWER(t.appln_title) LIKE '%rare earth%'
    AND a.appln_filing_year BETWEEN 2010 AND 2020
    ORDER BY a.appln_filing_year DESC
    LIMIT 10
    """
    
    try:
        sample_ree = pd.read_sql(sample_ree_query, db.bind)
        print(f"✅ Found {len(sample_ree)} sample REE patents (2010-2020)")
        if not sample_ree.empty:
            print("Sample REE patents:")
            for _, row in sample_ree.head(3).iterrows():
                print(f"   ID: {row['appln_id']}, Year: {row['appln_filing_year']}, Auth: {row['appln_auth']}")
        
        # Step 4: Test forward citations for these specific patents
        if not sample_ree.empty:
            print("\n4️⃣ TESTING FORWARD CITATIONS FOR SAMPLE PATENTS:")
            test_appln_ids = sample_ree['appln_id'].head(3).tolist()
            
            # Try different forward citation approaches
            
            # Approach 1: Direct citation lookup (current method)
            print("\n📋 Approach 1: Direct application citation lookup")
            direct_query = f"""
            SELECT COUNT(*) as forward_count
            FROM tls212_citation c
            WHERE c.cited_appln_id IN ({','.join(map(str, test_appln_ids))})
            AND c.citn_origin = 'SEA'
            """
            
            try:
                direct_result = pd.read_sql(direct_query, db.bind)
                print(f"   Direct citations found: {direct_result.iloc[0]['forward_count']}")
            except Exception as e:
                print(f"   ❌ Direct approach failed: {e}")
            
            # Approach 2: Via publication IDs
            print("\n📋 Approach 2: Via publication IDs")
            publn_lookup_query = f"""
            SELECT 
                p.appln_id,
                p.pat_publn_id,
                c.cited_pat_publn_id,
                COUNT(*) as citation_count
            FROM tls211_pat_publn p
            LEFT JOIN tls212_citation c ON p.pat_publn_id = c.cited_pat_publn_id
            WHERE p.appln_id IN ({','.join(map(str, test_appln_ids))})
            GROUP BY p.appln_id, p.pat_publn_id, c.cited_pat_publn_id
            HAVING COUNT(*) > 0
            """
            
            try:
                publn_result = pd.read_sql(publn_lookup_query, db.bind)
                print(f"   Publication-based citations found: {len(publn_result)}")
                if not publn_result.empty:
                    print(f"   Total citation instances: {publn_result['citation_count'].sum()}")
            except Exception as e:
                print(f"   ❌ Publication approach failed: {e}")
            
            # Approach 3: Check if publications exist at all
            print("\n📋 Approach 3: Publication existence check")
            publn_exist_query = f"""
            SELECT 
                appln_id,
                COUNT(*) as publication_count
            FROM tls211_pat_publn
            WHERE appln_id IN ({','.join(map(str, test_appln_ids))})
            GROUP BY appln_id
            """
            
            try:
                publn_exist = pd.read_sql(publn_exist_query, db.bind)
                print(f"   Publications found for {len(publn_exist)} applications")
                if not publn_exist.empty:
                    print(f"   Total publications: {publn_exist['publication_count'].sum()}")
                    for _, row in publn_exist.iterrows():
                        print(f"     App {row['appln_id']}: {row['publication_count']} publications")
            except Exception as e:
                print(f"   ❌ Publication existence check failed: {e}")
            
            # Approach 4: Check any citations at all (remove SEA filter)
            print("\n📋 Approach 4: All citation types (no SEA filter)")
            all_citations_query = f"""
            SELECT 
                citn_origin,
                COUNT(*) as count
            FROM tls212_citation c
            WHERE c.cited_appln_id IN ({','.join(map(str, test_appln_ids))})
            GROUP BY citn_origin
            """
            
            try:
                all_citations = pd.read_sql(all_citations_query, db.bind)
                print(f"   All citation types found:")
                for _, row in all_citations.iterrows():
                    print(f"     {row['citn_origin']}: {row['count']} citations")
            except Exception as e:
                print(f"   ❌ All citations check failed: {e}")
                
    except Exception as e:
        print(f"❌ Sample REE patents query failed: {e}")
    
    # Step 5: Recommendations
    print("\n💡 DIAGNOSTIC RECOMMENDATIONS:")
    print("1. Check if 'SEA' (Search Report) citations are the right type")
    print("2. Consider using all citation types (remove citn_origin filter)")
    print("3. Verify citation direction (cited_appln_id vs citing application)")
    print("4. Check if recent patents (2020+) have sufficient citation lag time")
    print("5. Consider using patent family citations (TLS228_DOCDB_FAM_CITN)")

if __name__ == "__main__":
    diagnose_citation_issues()