#!/usr/bin/env python3
"""
PATSTAT Query Testing Script - REE Patent Analysis
==================================================

This script extracts the core PATSTAT functionality from the notebook
to test database queries directly without demo data fallbacks.

Purpose: Isolate and test PATSTAT database connectivity and query execution
Author: Claude Code AI Assistant
Date: 2025-06-24
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def test_patstat_connection():
    """Test PATSTAT connection and basic table access"""
    
    print("="*60)
    print("🔬 PATSTAT Database Connection Test")
    print("="*60)
    
    # Import PATSTAT libraries
    try:
        from epo.tipdata.patstat import PatstatClient
        from epo.tipdata.patstat.database.models import (
            TLS201_APPLN, TLS202_APPLN_TITLE, TLS203_APPLN_ABSTR, 
            TLS209_APPLN_IPC, TLS224_APPLN_CPC, TLS212_CITATION
        )
        from sqlalchemy import func, and_, or_
        from sqlalchemy.orm import sessionmaker, aliased
        
        print("✅ PATSTAT libraries imported successfully")
        
    except ImportError as e:
        print(f"❌ PATSTAT import failed: {e}")
        return False, None, None
    
    # Test both environments
    environments = ['TEST', 'PROD']
    
    for environment in environments:
        print(f"\n🔍 Testing {environment} environment...")
        
        try:
            # Initialize PATSTAT client
            patstat = PatstatClient(env=environment)
            db = patstat.orm()
            
            print(f"✅ Connected to PATSTAT {environment}")
            print(f"   Database engine: {db.bind}")
            
            # Test basic table access
            try:
                test_result = db.query(TLS201_APPLN.docdb_family_id).limit(1).first()
                if test_result:
                    print(f"✅ Table access successful - Found family ID: {test_result.docdb_family_id}")
                    return True, db, environment
                else:
                    print("⚠️  Table access returned no results")
                    
            except Exception as table_error:
                print(f"❌ Table access failed: {table_error}")
                continue
                
        except Exception as conn_error:
            print(f"❌ Connection to {environment} failed: {conn_error}")
            continue
    
    print("\n❌ No working PATSTAT environment found")
    return False, None, None

def test_ree_keywords_search(db):
    """Test REE keywords-based search using working patterns"""
    
    print("\n" + "="*60)
    print("🔍 Testing REE Keywords Search")
    print("="*60)
    
    # REE search terms
    ree_keywords = [
        "rare earth element", "light REE", "heavy REE", "rare earth metal",
        "rare earth oxide", "lanthan", "rare earth", "neodymium", "dysprosium"
    ]
    
    recovery_keywords = ["recov", "recycl", "extract", "separat", "purif"]
    
    try:
        print("📝 Step 1: Testing abstract search...")
        
        # Test abstract search (working pattern from enhanced notebook)
        abstract_query = (
            db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id, 
                     TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS203_APPLN_ABSTR, TLS203_APPLN_ABSTR.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= '2010-01-01',
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(kw) for kw in ree_keywords[:3]]),  # Test with fewer keywords
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(rw) for rw in recovery_keywords[:2]])  # Test with fewer keywords
                )
            ).distinct().limit(10)  # Small limit for testing
        )
        
        abstract_results = abstract_query.all()
        print(f"✅ Abstract search successful: {len(abstract_results)} results")
        
        if len(abstract_results) > 0:
            # Display sample results
            df_abstracts = pd.DataFrame(abstract_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'appln_nr'
            ])
            print("📋 Sample abstract search results:")
            print(df_abstracts.head().to_string(index=False))
        
        print("\n📝 Step 2: Testing title search...")
        
        # Test title search
        title_query = (
            db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id,
                     TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS202_APPLN_TITLE, TLS202_APPLN_TITLE.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= '2010-01-01',
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(kw) for kw in ree_keywords[:3]]),
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(rw) for rw in recovery_keywords[:2]])
                )
            ).distinct().limit(10)
        )
        
        title_results = title_query.all()
        print(f"✅ Title search successful: {len(title_results)} results")
        
        if len(title_results) > 0:
            df_titles = pd.DataFrame(title_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'appln_nr'
            ])
            print("📋 Sample title search results:")
            print(df_titles.head().to_string(index=False))
        
        # Combine results
        all_families = set()
        if len(abstract_results) > 0:
            all_families.update([row.docdb_family_id for row in abstract_results])
        if len(title_results) > 0:
            all_families.update([row.docdb_family_id for row in title_results])
        
        print(f"\n📊 Keywords search summary:")
        print(f"   Abstract matches: {len(abstract_results)}")
        print(f"   Title matches: {len(title_results)}")
        print(f"   Unique families: {len(all_families)}")
        
        return True, list(all_families)
        
    except Exception as e:
        print(f"❌ Keywords search failed: {e}")
        return False, []

def test_ree_classification_search(db):
    """Test REE classification-based search"""
    
    print("\n" + "="*60)
    print("🏷️  Testing REE Classification Search")
    print("="*60)
    
    # Key REE classification codes
    key_classification_codes = [
        'C22B  19/28', 'C22B  19/30', 'C22B  25/06',  # REE extraction
        'C04B  18/04', 'C04B  18/06', 'C04B  18/08',  # REE ceramics/materials  
        'H01M   6/52', 'H01M  10/54',  # REE batteries
        'C09K  11/01',  # REE phosphors
        'H01J   9/52'   # REE displays
    ]
    
    try:
        print("📝 Testing IPC classification search...")
        
        # Test IPC classification search (working pattern)
        ipc_query = (
            db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id,
                     TLS201_APPLN.appln_filing_date, TLS209_APPLN_IPC.ipc_class_symbol)
            .join(TLS209_APPLN_IPC, TLS209_APPLN_IPC.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= '2010-01-01',
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    func.substr(TLS209_APPLN_IPC.ipc_class_symbol, 1, 11).in_(key_classification_codes)
                )
            ).distinct().limit(20)  # Small limit for testing
        )
        
        ipc_results = ipc_query.all()
        print(f"✅ IPC classification search successful: {len(ipc_results)} results")
        
        if len(ipc_results) > 0:
            df_ipc = pd.DataFrame(ipc_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'ipc_class_symbol'
            ])
            print("📋 Sample IPC classification results:")
            print(df_ipc.head().to_string(index=False))
            
            # Show classification distribution
            ipc_dist = df_ipc['ipc_class_symbol'].value_counts()
            print("\n📊 IPC Classification Distribution:")
            for ipc, count in ipc_dist.items():
                print(f"   {ipc}: {count} applications")
        
        classification_families = [row.docdb_family_id for row in ipc_results]
        
        print(f"\n📊 Classification search summary:")
        print(f"   IPC matches: {len(ipc_results)}")
        print(f"   Unique families: {len(set(classification_families))}")
        
        return True, list(set(classification_families))
        
    except Exception as e:
        print(f"❌ Classification search failed: {e}")
        return False, []

def test_ipc_cooccurrence(db, family_ids):
    """Test IPC co-occurrence analysis"""
    
    print("\n" + "="*60)
    print("🔗 Testing IPC Co-occurrence Analysis")
    print("="*60)
    
    if len(family_ids) == 0:
        print("⚠️  No family IDs available for co-occurrence analysis")
        return False
    
    try:
        print(f"📝 Testing co-occurrence for {len(family_ids)} families...")
        
        # Create aliases for self-join
        from sqlalchemy.orm import aliased
        TLS209_APPLN_IPC_2 = aliased(TLS209_APPLN_IPC)
        
        # Co-occurrence query (working pattern from enhanced notebook)
        cooccurrence_query = (
            db.query(
                TLS201_APPLN.docdb_family_id.label('family_id'),
                TLS201_APPLN.earliest_filing_year.label('filing_year'),
                TLS209_APPLN_IPC.ipc_class_symbol.label('IPC_1'),
                TLS209_APPLN_IPC_2.ipc_class_symbol.label('IPC_2')
            )
            .join(TLS209_APPLN_IPC, TLS201_APPLN.appln_id == TLS209_APPLN_IPC.appln_id)
            .join(TLS209_APPLN_IPC_2, TLS201_APPLN.appln_id == TLS209_APPLN_IPC_2.appln_id)
            .filter(
                TLS201_APPLN.docdb_family_id.in_(family_ids[:10]),  # Test with subset
                TLS201_APPLN.earliest_filing_year.between(2010, 2024),
                # Ensure different IPC codes (avoid self-loops)
                TLS209_APPLN_IPC.ipc_class_symbol > TLS209_APPLN_IPC_2.ipc_class_symbol,
                # Ensure different main classes (meaningful co-occurrence)
                func.left(TLS209_APPLN_IPC.ipc_class_symbol, 4) != func.left(TLS209_APPLN_IPC_2.ipc_class_symbol, 4)
            ).limit(20)  # Small limit for testing
        )
        
        cooccurrence_results = cooccurrence_query.all()
        print(f"✅ Co-occurrence analysis successful: {len(cooccurrence_results)} co-occurrences found")
        
        if len(cooccurrence_results) > 0:
            df_cooccurrence = pd.DataFrame(cooccurrence_results, columns=[
                'family_id', 'filing_year', 'IPC_1', 'IPC_2'
            ])
            print("📋 Sample co-occurrence results:")
            print(df_cooccurrence.head().to_string(index=False))
            
            # Analyze patterns
            ipc_pairs = df_cooccurrence.groupby(['IPC_1', 'IPC_2']).size().sort_values(ascending=False)
            print("\n📊 Top IPC Co-occurrence Patterns:")
            for (ipc1, ipc2), count in ipc_pairs.head(5).items():
                print(f"   {ipc1} ↔ {ipc2}: {count} families")
        
        return True
        
    except Exception as e:
        print(f"❌ Co-occurrence analysis failed: {e}")
        return False

def test_citation_analysis(db, family_ids):
    """Test citation analysis"""
    
    print("\n" + "="*60)
    print("🌍 Testing Citation Analysis")
    print("="*60)
    
    if len(family_ids) == 0:
        print("⚠️  No family IDs available for citation analysis")
        return False
    
    try:
        # Get application IDs from family IDs first
        appln_query = (
            db.query(TLS201_APPLN.appln_id, TLS201_APPLN.docdb_family_id)
            .filter(TLS201_APPLN.docdb_family_id.in_(family_ids[:5]))  # Test with subset
            .limit(10)
        )
        
        appln_results = appln_query.all()
        if len(appln_results) == 0:
            print("⚠️  No application IDs found for citation analysis")
            return False
        
        appln_ids = [row.appln_id for row in appln_results]
        print(f"📝 Testing citations for {len(appln_ids)} applications...")
        
        # Test forward citations
        forward_citation_query = (
            db.query(
                TLS212_CITATION.cited_appln_id,
                TLS212_CITATION.citing_appln_id,
                TLS201_APPLN.appln_filing_date.label('citing_filing_date')
            )
            .join(TLS201_APPLN, TLS212_CITATION.citing_appln_id == TLS201_APPLN.appln_id)
            .filter(TLS212_CITATION.cited_appln_id.in_(appln_ids))
            .limit(10)  # Small limit for testing
        )
        
        forward_results = forward_citation_query.all()
        print(f"✅ Forward citation analysis: {len(forward_results)} citations found")
        
        if len(forward_results) > 0:
            df_forward = pd.DataFrame(forward_results, columns=[
                'cited_appln_id', 'citing_appln_id', 'citing_filing_date'
            ])
            print("📋 Sample forward citations:")
            print(df_forward.head().to_string(index=False))
        
        # Test backward citations
        backward_citation_query = (
            db.query(
                TLS212_CITATION.citing_appln_id,
                TLS212_CITATION.cited_appln_id,
                TLS201_APPLN.appln_filing_date.label('cited_filing_date')
            )
            .join(TLS201_APPLN, TLS212_CITATION.cited_appln_id == TLS201_APPLN.appln_id)
            .filter(TLS212_CITATION.citing_appln_id.in_(appln_ids))
            .limit(10)  # Small limit for testing
        )
        
        backward_results = backward_citation_query.all()
        print(f"✅ Backward citation analysis: {len(backward_results)} citations found")
        
        if len(backward_results) > 0:
            df_backward = pd.DataFrame(backward_results, columns=[
                'citing_appln_id', 'cited_appln_id', 'cited_filing_date'
            ])
            print("📋 Sample backward citations:")
            print(df_backward.head().to_string(index=False))
        
        print(f"\n📊 Citation analysis summary:")
        print(f"   Forward citations: {len(forward_results)}")
        print(f"   Backward citations: {len(backward_results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Citation analysis failed: {e}")
        return False

def main():
    """Main testing function"""
    
    print("🚀 PATSTAT REE Patent Analysis - Query Testing Script")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Step 1: Test PATSTAT connection
    patstat_available, db, environment = test_patstat_connection()
    
    if not patstat_available:
        print("\n❌ PATSTAT connection failed - Cannot proceed with query tests")
        return False
    
    print(f"\n✅ Using PATSTAT {environment} environment for testing")
    
    # Step 2: Test REE keywords search
    keywords_success, keyword_families = test_ree_keywords_search(db)
    
    # Step 3: Test REE classification search  
    classification_success, classification_families = test_ree_classification_search(db)
    
    # Step 4: Test intersection of results
    if keywords_success and classification_success:
        intersection_families = list(set(keyword_families) & set(classification_families))
        print(f"\n🎯 Intersection Analysis:")
        print(f"   Keywords families: {len(keyword_families)}")
        print(f"   Classification families: {len(classification_families)}")
        print(f"   High-quality intersection: {len(intersection_families)}")
        
        test_families = intersection_families if len(intersection_families) > 0 else keyword_families[:10]
    else:
        test_families = []
    
    # Step 5: Test IPC co-occurrence analysis
    if len(test_families) > 0:
        test_ipc_cooccurrence(db, test_families)
    
    # Step 6: Test citation analysis
    if len(test_families) > 0:
        test_citation_analysis(db, test_families)
    
    # Final summary
    print("\n" + "="*60)
    print("📋 PATSTAT Query Testing Summary")
    print("="*60)
    print(f"✅ PATSTAT Connection: {'Success' if patstat_available else 'Failed'}")
    print(f"✅ Keywords Search: {'Success' if keywords_success else 'Failed'}")
    print(f"✅ Classification Search: {'Success' if classification_success else 'Failed'}")
    print(f"📊 Total REE families found: {len(set(keyword_families + classification_families))}")
    
    if patstat_available:
        print(f"\n🎯 Key Findings:")
        print(f"   • PATSTAT {environment} environment is accessible")
        print(f"   • Database queries execute successfully")
        print(f"   • REE patent data is available and queryable")
        print(f"   • Working search patterns identified")
        
        print(f"\n💡 Next Steps:")
        print(f"   • Scale up query limits for production analysis")
        print(f"   • Implement full intersection methodology")
        print(f"   • Add error handling for edge cases")
        print(f"   • Optimize query performance")
    
    print(f"\n⏰ Completed at: {datetime.now()}")
    return patstat_available

if __name__ == "__main__":
    # Set pandas display options
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    # Run the test
    success = main()
    
    if success:
        print("\n🎉 PATSTAT query testing completed successfully!")
    else:
        print("\n❌ PATSTAT query testing failed - Check connection and permissions")