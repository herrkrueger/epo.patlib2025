"""
Citation Analysis Module for REE Patent Analysis
Forward and backward citations via proper publication linkage
"""

import pandas as pd
import numpy as np
from datetime import datetime
import traceback

def get_forward_citations(db, ree_appln_ids, test_mode=True):
    """
    Find forward citations via correct publication linkage
    
    Args:
        db: Database connection
        ree_appln_ids: List of REE application IDs
        test_mode: If True, limits results for faster testing
    
    Returns:
        DataFrame with forward citation data
    """
    
    if not ree_appln_ids:
        print("❌ No application IDs provided for forward citations")
        return pd.DataFrame()
    
    print(f"🔍 Forward citations for {len(ree_appln_ids)} REE applications...")
    
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    # Step 1: Get publication IDs for REE applications
    ree_publications_query = f"""
    SELECT appln_id as ree_appln_id, pat_publn_id as ree_publn_id
    FROM tls211_pat_publn
    WHERE appln_id IN ({appln_ids_str})
    """
    
    try:
        ree_publications = pd.read_sql(ree_publications_query, db.bind)
        
        if ree_publications.empty:
            print("❌ No publications found for REE applications")
            return pd.DataFrame()
        
        print(f"✅ Found {len(ree_publications)} REE publications")
        
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
            forward_query += " LIMIT 200000"
        
        forward_citations = pd.read_sql(forward_query, db.bind)
        
        if not forward_citations.empty:
            print(f"✅ Found {len(forward_citations)} forward citations")
            
            # Citation origin analysis
            origin_counts = forward_citations['citn_origin'].value_counts()
            print(f"   Citation origins: {origin_counts.to_dict()}")
            
            # Temporal analysis
            year_range = forward_citations['citing_year'].min(), forward_citations['citing_year'].max()
            print(f"   Citation years: {year_range[0]}-{year_range[1]}")
            
            # Geographic analysis
            country_counts = forward_citations['citing_country'].value_counts()
            print(f"   Top citing countries: {country_counts.head(3).to_dict()}")
            
        else:
            print("❌ No forward citations found")
        
        return forward_citations
        
    except Exception as e:
        print(f"❌ Forward citation analysis failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return pd.DataFrame()

def get_backward_citations(db, ree_appln_ids, test_mode=True):
    """
    Find backward citations via publication linkage
    
    Args:
        db: Database connection
        ree_appln_ids: List of REE application IDs
        test_mode: If True, limits results for faster testing
    
    Returns:
        DataFrame with backward citation data
    """
    
    if not ree_appln_ids:
        print("❌ No application IDs provided for backward citations")
        return pd.DataFrame()
    
    print(f"🔍 Backward citations for {len(ree_appln_ids)} REE applications...")
    
    # Get publication IDs for our REE patents
    appln_ids_str = ','.join(map(str, ree_appln_ids))
    
    publn_query = f"""
    SELECT pat_publn_id, appln_id FROM tls211_pat_publn
    WHERE appln_id IN ({appln_ids_str})
    """
    
    try:
        ree_publications = pd.read_sql(publn_query, db.bind)
        
        if ree_publications.empty:
            print("❌ No publications found for REE applications")
            return pd.DataFrame()
        
        publn_ids_str = ','.join(map(str, ree_publications['pat_publn_id']))
        
        # Backward citations query
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
            backward_query += " LIMIT 200000"
        
        backward_citations = pd.read_sql(backward_query, db.bind)
        
        if not backward_citations.empty:
            print(f"✅ Found {len(backward_citations)} backward citations")
            
            # Citation origin analysis
            origin_counts = backward_citations['citn_origin'].value_counts()
            print(f"   Citation origins: {origin_counts.to_dict()}")
            
            # Prior art temporal analysis
            cited_years = backward_citations['cited_year'].dropna()
            if not cited_years.empty:
                year_range = cited_years.min(), cited_years.max()
                print(f"   Prior art range: {year_range[0]}-{year_range[1]}")
            
            # Geographic analysis of cited work
            cited_countries = backward_citations['cited_country'].value_counts()
            print(f"   Top cited countries: {cited_countries.head(3).to_dict()}")
            
        else:
            print("❌ No backward citations found")
        
        return backward_citations
        
    except Exception as e:
        print(f"❌ Backward citation analysis failed: {e}")
        print(f"   Error details: {traceback.format_exc()}")
        return pd.DataFrame()

def analyze_citation_patterns(forward_citations, backward_citations):
    """
    Analyze citation patterns for business intelligence
    
    Args:
        forward_citations: DataFrame with forward citations
        backward_citations: DataFrame with backward citations
    
    Returns:
        Dictionary with citation pattern analysis
    """
    
    print("📊 Analyzing citation patterns...")
    
    analysis = {
        'forward_citation_count': len(forward_citations),
        'backward_citation_count': len(backward_citations),
        'citation_balance': 'N/A',
        'top_citing_countries': [],
        'top_cited_countries': [],
        'citation_origins': {},
        'temporal_patterns': {}
    }
    
    # Citation balance analysis
    if len(forward_citations) > 0 and len(backward_citations) > 0:
        balance_ratio = len(forward_citations) / len(backward_citations)
        if balance_ratio > 1.5:
            analysis['citation_balance'] = 'High impact (more cited than citing)'
        elif balance_ratio < 0.5:
            analysis['citation_balance'] = 'High dependency (more citing than cited)'
        else:
            analysis['citation_balance'] = 'Balanced citation pattern'
    
    # Geographic patterns
    if not forward_citations.empty and 'citing_country' in forward_citations.columns:
        citing_countries = forward_citations['citing_country'].value_counts()
        analysis['top_citing_countries'] = citing_countries.head(5).to_dict()
    
    if not backward_citations.empty and 'cited_country' in backward_citations.columns:
        cited_countries = backward_citations['cited_country'].value_counts()
        analysis['top_cited_countries'] = cited_countries.head(5).to_dict()
    
    # Citation origin patterns
    all_origins = []
    if not forward_citations.empty and 'citn_origin' in forward_citations.columns:
        all_origins.extend(forward_citations['citn_origin'].tolist())
    if not backward_citations.empty and 'citn_origin' in backward_citations.columns:
        all_origins.extend(backward_citations['citn_origin'].tolist())
    
    if all_origins:
        origin_series = pd.Series(all_origins)
        analysis['citation_origins'] = origin_series.value_counts().to_dict()
    
    # Temporal patterns
    if not forward_citations.empty and 'citing_year' in forward_citations.columns:
        citing_years = forward_citations['citing_year'].dropna()
        if not citing_years.empty:
            analysis['temporal_patterns']['forward_years'] = {
                'min': int(citing_years.min()),
                'max': int(citing_years.max()),
                'mean': float(citing_years.mean())
            }
    
    if not backward_citations.empty and 'cited_year' in backward_citations.columns:
        cited_years = backward_citations['cited_year'].dropna()
        if not cited_years.empty:
            analysis['temporal_patterns']['backward_years'] = {
                'min': int(cited_years.min()),
                'max': int(cited_years.max()),
                'mean': float(cited_years.mean())
            }
    
    print(f"✅ Citation pattern analysis complete")
    print(f"   Forward: {analysis['forward_citation_count']}, Backward: {analysis['backward_citation_count']}")
    print(f"   Balance: {analysis['citation_balance']}")
    
    return analysis

def calculate_citation_metrics(ree_dataset, forward_citations, backward_citations):
    """
    Calculate key citation metrics for each REE application
    
    Args:
        ree_dataset: DataFrame with REE applications
        forward_citations: DataFrame with forward citations
        backward_citations: DataFrame with backward citations
    
    Returns:
        DataFrame with citation metrics per application
    """
    
    print("📈 Calculating citation metrics...")
    
    if ree_dataset.empty:
        return pd.DataFrame()
    
    # Initialize metrics dataframe
    metrics_df = ree_dataset[['appln_id', 'appln_filing_year', 'appln_auth']].copy()
    
    # Forward citation metrics
    if not forward_citations.empty and 'cited_ree_appln_id' in forward_citations.columns:
        forward_counts = forward_citations['cited_ree_appln_id'].value_counts()
        metrics_df['forward_citations'] = metrics_df['appln_id'].map(forward_counts).fillna(0)
        
        # Citation velocity (citations per year since filing)
        current_year = datetime.now().year
        metrics_df['years_since_filing'] = current_year - metrics_df['appln_filing_year']
        metrics_df['citation_velocity'] = metrics_df['forward_citations'] / metrics_df['years_since_filing'].clip(lower=1)
    else:
        metrics_df['forward_citations'] = 0
        metrics_df['citation_velocity'] = 0
    
    # Backward citation metrics
    if not backward_citations.empty and 'ree_appln_id' in backward_citations.columns:
        backward_counts = backward_citations['ree_appln_id'].value_counts()
        metrics_df['backward_citations'] = metrics_df['appln_id'].map(backward_counts).fillna(0)
    else:
        metrics_df['backward_citations'] = 0
    
    # Citation impact score (simple weighted metric)
    metrics_df['citation_impact_score'] = (
        metrics_df['forward_citations'] * 2 +  # Forward citations weighted more heavily
        metrics_df['backward_citations'] * 0.5 +  # Backward citations show thoroughness
        metrics_df['citation_velocity'] * 3  # Velocity shows current relevance
    )
    
    # Categorize impact levels
    def categorize_impact(score):
        if score >= 10:
            return 'High Impact'
        elif score >= 5:
            return 'Medium Impact'
        elif score >= 1:
            return 'Low Impact'
        else:
            return 'No Citations'
    
    metrics_df['impact_category'] = metrics_df['citation_impact_score'].apply(categorize_impact)
    
    print(f"✅ Citation metrics calculated for {len(metrics_df)} applications")
    
    # Summary statistics
    impact_distribution = metrics_df['impact_category'].value_counts()
    print(f"   Impact distribution: {impact_distribution.to_dict()}")
    
    if metrics_df['forward_citations'].sum() > 0:
        avg_forward = metrics_df['forward_citations'].mean()
        print(f"   Average forward citations: {avg_forward:.1f}")
    
    return metrics_df

def export_citation_analysis(forward_citations, backward_citations, citation_metrics, output_prefix="ree_citations"):
    """
    Export citation analysis results to CSV files
    
    Args:
        forward_citations: DataFrame with forward citations
        backward_citations: DataFrame with backward citations
        citation_metrics: DataFrame with citation metrics
        output_prefix: Prefix for output filenames
    """
    
    print("💾 Exporting citation analysis results...")
    
    try:
        # Export forward citations
        if not forward_citations.empty:
            forward_file = f"{output_prefix}_forward.csv"
            forward_citations.to_csv(forward_file, index=False)
            print(f"✅ Forward citations: {forward_file}")
        
        # Export backward citations
        if not backward_citations.empty:
            backward_file = f"{output_prefix}_backward.csv"
            backward_citations.to_csv(backward_file, index=False)
            print(f"✅ Backward citations: {backward_file}")
        
        # Export citation metrics
        if not citation_metrics.empty:
            metrics_file = f"{output_prefix}_metrics.csv"
            citation_metrics.to_csv(metrics_file, index=False)
            print(f"✅ Citation metrics: {metrics_file}")
            
        print("✅ Citation analysis export complete")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

if __name__ == "__main__":
    from database_connection import get_database_connection
    from dataset_builder import build_ree_dataset
    
    print("CITATION ANALYZER - STANDALONE TEST")
    print("=" * 50)
    
    # Get database connection
    db = get_database_connection()
    if not db:
        print("❌ Database connection failed")
        exit(1)
    
    # Build small REE dataset for testing
    print("\n📊 Building test dataset...")
    ree_dataset = build_ree_dataset(db, test_mode=True)
    
    if ree_dataset.empty:
        print("❌ No REE dataset available for citation testing")
        exit(1)
    
    # Test citation analysis
    appln_ids = ree_dataset['appln_id'].tolist()[:50]  # Test with first 50 applications
    
    print(f"\n🔍 Testing citation analysis with {len(appln_ids)} applications...")
    
    # Forward citations
    forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
    
    # Backward citations
    backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
    
    # Pattern analysis
    patterns = analyze_citation_patterns(forward_cit, backward_cit)
    
    # Metrics calculation
    metrics = calculate_citation_metrics(ree_dataset.head(50), forward_cit, backward_cit)
    
    # Export results
    export_citation_analysis(forward_cit, backward_cit, metrics, "test_ree_citations")
    
    print("\n🎯 Citation analysis test complete!")
    print(f"   Forward: {len(forward_cit)}, Backward: {len(backward_cit)}")
    print(f"   Metrics: {len(metrics)} applications analyzed")