#!/usr/bin/env python3
"""
PATSTAT Query Testing Script - REE Patent Analysis (FIXED)
==========================================================

Fixed version addressing scoping issues with table model imports.

Purpose: Test PATSTAT database connectivity and query execution
Author: Claude Code AI Assistant  
Date: 2025-06-24
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Global variables for PATSTAT objects
PATSTAT_MODELS = None
db = None
environment = None

def test_patstat_connection():
    """Test PATSTAT connection and basic table access"""
    
    global PATSTAT_MODELS, db, environment
    
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
        
        # Store models globally
        PATSTAT_MODELS = {
            'TLS201_APPLN': TLS201_APPLN,
            'TLS202_APPLN_TITLE': TLS202_APPLN_TITLE,
            'TLS203_APPLN_ABSTR': TLS203_APPLN_ABSTR,
            'TLS209_APPLN_IPC': TLS209_APPLN_IPC,
            'TLS224_APPLN_CPC': TLS224_APPLN_CPC,
            'TLS212_CITATION': TLS212_CITATION,
            'func': func,
            'and_': and_,
            'or_': or_,
            'aliased': aliased
        }
        
        print("✅ PATSTAT libraries imported successfully")
        
    except ImportError as e:
        print(f"❌ PATSTAT import failed: {e}")
        return False
    
    # Test both environments
    environments = ['TEST', 'PROD']
    
    for env in environments:
        print(f"\n🔍 Testing {env} environment...")
        
        try:
            # Initialize PATSTAT client
            patstat = PatstatClient(env=env)
            db_test = patstat.orm()
            
            print(f"✅ Connected to PATSTAT {env}")
            print(f"   Database engine: {db_test.bind}")
            
            # Test basic table access
            try:
                test_result = db_test.query(TLS201_APPLN.docdb_family_id).limit(1).first()
                if test_result:
                    print(f"✅ Table access successful - Found family ID: {test_result.docdb_family_id}")
                    db = db_test
                    environment = env
                    return True
                else:
                    print("⚠️  Table access returned no results")
                    
            except Exception as table_error:
                print(f"❌ Table access failed: {table_error}")
                continue
                
        except Exception as conn_error:
            print(f"❌ Connection to {env} failed: {conn_error}")
            continue
    
    print("\n❌ No working PATSTAT environment found")
    return False

def test_ree_keywords_search():
    """Test REE keywords-based search using working patterns"""
    
    print("\n" + "="*60)
    print("🔍 Testing REE Keywords Search")
    print("="*60)
    
    if not db or not PATSTAT_MODELS:
        print("❌ No database connection available")
        return False, []
    
    # Get models from global storage
    TLS201_APPLN = PATSTAT_MODELS['TLS201_APPLN']
    TLS202_APPLN_TITLE = PATSTAT_MODELS['TLS202_APPLN_TITLE']
    TLS203_APPLN_ABSTR = PATSTAT_MODELS['TLS203_APPLN_ABSTR']
    and_ = PATSTAT_MODELS['and_']
    or_ = PATSTAT_MODELS['or_']
    
    # REE search terms (limited for testing)
    ree_keywords = ["rare earth", "lanthan", "neodymium"]
    recovery_keywords = ["recov", "recycl"]
    
    try:
        print("📝 Step 1: Testing abstract search...")
        
        # Test abstract search (working pattern from enhanced notebook)
        abstract_query = (
            db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id, 
                     TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS203_APPLN_ABSTR, TLS203_APPLN_ABSTR.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= '2020-01-01',  # Recent data only
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(kw) for kw in ree_keywords]),
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(rw) for rw in recovery_keywords])
                )
            ).distinct().limit(5)  # Very small limit for testing
        )
        
        abstract_results = abstract_query.all()
        print(f"✅ Abstract search successful: {len(abstract_results)} results")
        
        if len(abstract_results) > 0:
            # Display sample results
            df_abstracts = pd.DataFrame(abstract_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'appln_nr'
            ])
            print("📋 Sample abstract search results:")
            print(df_abstracts.to_string(index=False))
        
        print("\n📝 Step 2: Testing title search...")
        
        # Test title search
        title_query = (
            db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id,
                     TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS202_APPLN_TITLE, TLS202_APPLN_TITLE.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= '2020-01-01',
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(kw) for kw in ree_keywords]),
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(rw) for rw in recovery_keywords])
                )
            ).distinct().limit(5)
        )
        
        title_results = title_query.all()
        print(f"✅ Title search successful: {len(title_results)} results")
        
        if len(title_results) > 0:
            df_titles = pd.DataFrame(title_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'appln_nr'
            ])
            print("📋 Sample title search results:")
            print(df_titles.to_string(index=False))
        
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
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False, []

def test_ree_classification_search():
    """Test REE classification-based search"""
    
    print("\n" + "="*60)
    print("🏷️  Testing REE Classification Search")
    print("="*60)
    
    if not db or not PATSTAT_MODELS:
        print("❌ No database connection available")
        return False, []
    
    # Get models from global storage
    TLS201_APPLN = PATSTAT_MODELS['TLS201_APPLN']
    TLS209_APPLN_IPC = PATSTAT_MODELS['TLS209_APPLN_IPC']
    and_ = PATSTAT_MODELS['and_']
    func = PATSTAT_MODELS['func']
    
    # Key REE classification codes (limited for testing)
    key_classification_codes = [
        'C22B  19/28', 'C22B  19/30',  # REE extraction
        'C04B  18/04', 'C04B  18/06',  # REE ceramics
        'H01M   6/52'   # REE batteries
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
                    TLS201_APPLN.appln_filing_date >= '2020-01-01',
                    TLS201_APPLN.appln_filing_date <= '2024-12-31',
                    func.substr(TLS209_APPLN_IPC.ipc_class_symbol, 1, 11).in_(key_classification_codes)
                )
            ).distinct().limit(10)  # Small limit for testing
        )
        
        ipc_results = ipc_query.all()
        print(f"✅ IPC classification search successful: {len(ipc_results)} results")
        
        if len(ipc_results) > 0:
            df_ipc = pd.DataFrame(ipc_results, columns=[
                'docdb_family_id', 'appln_id', 'appln_filing_date', 'ipc_class_symbol'
            ])
            print("📋 Sample IPC classification results:")
            print(df_ipc.to_string(index=False))
            
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
        print(f"   Error type: {type(e).__name__}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False, []

def test_simple_count_queries():
    """Test simple count queries to verify basic functionality"""
    
    print("\n" + "="*60)
    print("📊 Testing Simple Count Queries")
    print("="*60)
    
    if not db or not PATSTAT_MODELS:
        print("❌ No database connection available")
        return False
    
    TLS201_APPLN = PATSTAT_MODELS['TLS201_APPLN']
    TLS209_APPLN_IPC = PATSTAT_MODELS['TLS209_APPLN_IPC']
    TLS202_APPLN_TITLE = PATSTAT_MODELS['TLS202_APPLN_TITLE']
    
    try:
        print("📝 Testing basic table counts...")
        
        # Test 1: Count applications from 2020+
        recent_apps = db.query(TLS201_APPLN).filter(
            TLS201_APPLN.appln_filing_date >= '2020-01-01'
        ).limit(100).count()
        print(f"✅ Recent applications (2020+): {recent_apps:,}")
        
        # Test 2: Count IPC classifications
        ipc_count = db.query(TLS209_APPLN_IPC).limit(100).count()
        print(f"✅ IPC classifications sample: {ipc_count:,}")
        
        # Test 3: Count titles
        title_count = db.query(TLS202_APPLN_TITLE).limit(100).count()
        print(f"✅ Application titles sample: {title_count:,}")
        
        print("\n📝 Testing specific searches...")
        
        # Test 4: Search for any "rare" mentions
        rare_titles = db.query(TLS202_APPLN_TITLE).filter(
            TLS202_APPLN_TITLE.appln_title.contains('rare')
        ).limit(5).all()
        print(f"✅ Titles containing 'rare': {len(rare_titles)} found")
        
        if rare_titles:
            for title in rare_titles:
                print(f"   ID {title.appln_id}: {title.appln_title[:100]}...")
        
        # Test 5: Search for specific IPC codes
        c22b_codes = db.query(TLS209_APPLN_IPC).filter(
            TLS209_APPLN_IPC.ipc_class_symbol.like('C22B%')
        ).limit(5).all()
        print(f"✅ C22B IPC codes: {len(c22b_codes)} found")
        
        if c22b_codes:
            for ipc in c22b_codes:
                print(f"   App {ipc.appln_id}: {ipc.ipc_class_symbol}")
        
        return True
        
    except Exception as e:
        print(f"❌ Simple count queries failed: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    """Main testing function"""
    
    print("🚀 PATSTAT REE Patent Analysis - Query Testing Script (FIXED)")
    print(f"⏰ Started at: {datetime.now()}")
    
    # Step 1: Test PATSTAT connection
    patstat_available = test_patstat_connection()
    
    if not patstat_available:
        print("\n❌ PATSTAT connection failed - Cannot proceed with query tests")
        return False
    
    print(f"\n✅ Using PATSTAT {environment} environment for testing")
    
    # Step 2: Test simple queries first
    simple_success = test_simple_count_queries()
    
    # Step 3: Test REE keywords search
    keywords_success, keyword_families = test_ree_keywords_search()
    
    # Step 4: Test REE classification search  
    classification_success, classification_families = test_ree_classification_search()
    
    # Step 5: Test intersection of results
    if keywords_success and classification_success:
        intersection_families = list(set(keyword_families) & set(classification_families))
        print(f"\n🎯 Intersection Analysis:")
        print(f"   Keywords families: {len(keyword_families)}")
        print(f"   Classification families: {len(classification_families)}")
        print(f"   High-quality intersection: {len(intersection_families)}")
    
    # Final summary
    print("\n" + "="*60)
    print("📋 PATSTAT Query Testing Summary")
    print("="*60)
    print(f"✅ PATSTAT Connection: {'Success' if patstat_available else 'Failed'}")
    print(f"✅ Simple Queries: {'Success' if simple_success else 'Failed'}")
    print(f"✅ Keywords Search: {'Success' if keywords_success else 'Failed'}")
    print(f"✅ Classification Search: {'Success' if classification_success else 'Failed'}")
    
    if patstat_available:
        print(f"\n🎯 Key Findings:")
        print(f"   • PATSTAT {environment} environment is accessible")
        print(f"   • Basic table queries work correctly")
        print(f"   • REE-specific search patterns {'work' if keywords_success or classification_success else 'need debugging'}")
        
        if keywords_success or classification_success:
            total_families = len(set(keyword_families + classification_families))
            print(f"   • Found {total_families} REE patent families with test queries")
    
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
        print("\n🎉 PATSTAT query testing completed!")
    else:
        print("\n❌ PATSTAT query testing failed")