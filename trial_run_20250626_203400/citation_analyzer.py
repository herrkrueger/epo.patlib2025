"""
Citation Analyzer Component for REE Patent Citation Analysis
Citation intelligence with proper publication linkage for comprehensive analysis
"""

import pandas as pd
import logging
from typing import List, Optional, Dict, Any, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Citation origin types for comprehensive coverage
CITATION_ORIGINS = [
    'SEA',  # Search Report
    'APP',  # Applicant
    'ISR',  # International Search Report
    'EXA',  # Examiner
    'OPP',  # Opposition
    'SUP',  # Supplementary
    'PIL',  # PIL (Post-Issue Literature)
    'CIT',  # Citation
    'NPL',  # Non-Patent Literature
    'XPN',  # Extended Patent Network
    'Unknown'  # Unspecified origins
]

def get_publications_for_applications(db, appln_ids: List[int]) -> pd.DataFrame:
    """
    Get publication IDs for REE applications - critical for citation linkage
    """
    if not appln_ids:
        return pd.DataFrame()
    
    appln_ids_str = ','.join(map(str, appln_ids))
    
    publications_query = f"""
    SELECT 
        p.appln_id as ree_appln_id, 
        p.pat_publn_id as ree_publn_id,
        p.publn_auth,
        p.publn_kind,
        p.publn_date
    FROM tls211_pat_publn p
    WHERE p.appln_id IN ({appln_ids_str})
    AND p.pat_publn_id > 0
    """
    
    try:
        publications = pd.read_sql(publications_query, db.bind)
        logger.info(f"✅ Found {len(publications)} publications for {len(appln_ids)} applications")
        return publications
        
    except Exception as e:
        logger.error(f"❌ Publications query failed: {e}")
        return pd.DataFrame()

def get_forward_citations(db, ree_appln_ids: List[int], test_mode: bool = True) -> pd.DataFrame:
    """
    Find forward citations using proper publication linkage
    Critical insight: Citations link via publication IDs, not application IDs
    """
    if not ree_appln_ids:
        return pd.DataFrame()
    
    logger.info(f"🔍 Analyzing forward citations for {len(ree_appln_ids)} REE applications...")
    
    # Step 1: Get publication IDs for REE applications
    ree_publications = get_publications_for_applications(db, ree_appln_ids)
    
    if ree_publications.empty:
        logger.warning("No publications found for REE applications")
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['ree_publn_id']))
    
    # Step 2: Find forward citations via publication linkage
    forward_query = f"""
    SELECT 
        c.pat_publn_id as citing_publn_id,
        c.cited_pat_publn_id as cited_ree_publn_id,
        c.citn_origin,
        p_citing.appln_id as citing_appln_id,
        p_citing.publn_auth as citing_country,
        p_citing.publn_date as citing_date,
        a_citing.appln_filing_year as citing_year,
        a_citing.appln_auth as citing_office,
        ree_pub.ree_appln_id as cited_ree_appln_id
    FROM tls212_citation c
    JOIN tls211_pat_publn p_citing ON c.pat_publn_id = p_citing.pat_publn_id
    JOIN tls201_appln a_citing ON p_citing.appln_id = a_citing.appln_id
    JOIN (
        SELECT appln_id as ree_appln_id, pat_publn_id as ree_publn_id 
        FROM tls211_pat_publn 
        WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    ) ree_pub ON c.cited_pat_publn_id = ree_pub.ree_publn_id
    WHERE c.cited_pat_publn_id IN ({publn_ids_str})
    AND a_citing.appln_filing_year BETWEEN 2010 AND 2024
    AND c.citn_origin IS NOT NULL
    """
    
    if test_mode:
        forward_query += " LIMIT 2000"
    
    try:
        forward_citations = pd.read_sql(forward_query, db.bind)
        
        if not forward_citations.empty:
            logger.info(f"✅ Found {len(forward_citations)} forward citations")
            
            # Analyze citation patterns
            origin_counts = forward_citations['citn_origin'].value_counts()
            logger.info(f"Citation origins: {dict(origin_counts.head(5))}")
            
            year_range = f"{forward_citations['citing_year'].min()}-{forward_citations['citing_year'].max()}"
            logger.info(f"Citation years: {year_range}")
            
            countries = forward_citations['citing_country'].nunique()
            logger.info(f"Citing countries: {countries}")
            
        else:
            logger.warning("No forward citations found")
        
        return forward_citations
        
    except Exception as e:
        logger.error(f"❌ Forward citations query failed: {e}")
        return pd.DataFrame()

def get_backward_citations(db, ree_appln_ids: List[int], test_mode: bool = True) -> pd.DataFrame:
    """
    Find backward citations for prior art analysis
    """
    if not ree_appln_ids:
        return pd.DataFrame()
    
    logger.info(f"🔍 Analyzing backward citations for {len(ree_appln_ids)} REE applications...")
    
    # Get publication IDs for our REE patents
    ree_publications = get_publications_for_applications(db, ree_appln_ids)
    
    if ree_publications.empty:
        logger.warning("No publications found for backward citation analysis")
        return pd.DataFrame()
    
    publn_ids_str = ','.join(map(str, ree_publications['ree_publn_id']))
    
    # Find backward citations (what our REE patents cite)
    backward_query = f"""
    SELECT 
        c.pat_publn_id as ree_citing_publn_id,
        c.cited_pat_publn_id,
        c.cited_appln_id,
        c.citn_origin,
        p_cited.publn_auth as cited_country,
        p_cited.publn_date as cited_date,
        a_cited.appln_filing_year as cited_year,
        a_cited.appln_auth as cited_office,
        ree_pub.ree_appln_id as ree_appln_id
    FROM tls212_citation c
    LEFT JOIN tls211_pat_publn p_cited ON c.cited_pat_publn_id = p_cited.pat_publn_id
    LEFT JOIN tls201_appln a_cited ON c.cited_appln_id = a_cited.appln_id
    JOIN (
        SELECT appln_id as ree_appln_id, pat_publn_id as ree_publn_id 
        FROM tls211_pat_publn 
        WHERE appln_id IN ({','.join(map(str, ree_appln_ids))})
    ) ree_pub ON c.pat_publn_id = ree_pub.ree_publn_id
    WHERE c.pat_publn_id IN ({publn_ids_str})
    AND (a_cited.appln_filing_year >= 2000 OR a_cited.appln_filing_year IS NULL)
    AND c.citn_origin IS NOT NULL
    """
    
    if test_mode:
        backward_query += " LIMIT 2000"
    
    try:
        backward_citations = pd.read_sql(backward_query, db.bind)
        
        if not backward_citations.empty:
            logger.info(f"✅ Found {len(backward_citations)} backward citations")
            
            # Analyze backward citation patterns
            origin_counts = backward_citations['citn_origin'].value_counts()
            logger.info(f"Backward citation origins: {dict(origin_counts.head(5))}")
            
            cited_countries = backward_citations['cited_country'].value_counts().head(5)
            logger.info(f"Most cited countries: {dict(cited_countries)}")
            
        else:
            logger.warning("No backward citations found")
        
        return backward_citations
        
    except Exception as e:
        logger.error(f"❌ Backward citations query failed: {e}")
        return pd.DataFrame()

def calculate_citation_metrics(forward_citations: pd.DataFrame, backward_citations: pd.DataFrame, ree_dataset: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive citation impact metrics
    """
    metrics = {}
    
    if not ree_dataset.empty:
        total_ree_patents = len(ree_dataset)
        metrics['total_ree_patents'] = total_ree_patents
    else:
        return metrics
    
    # Forward citation metrics
    if not forward_citations.empty:
        metrics['total_forward_citations'] = len(forward_citations)
        metrics['cited_ree_patents'] = forward_citations['cited_ree_appln_id'].nunique()
        metrics['average_citations_per_patent'] = len(forward_citations) / total_ree_patents
        metrics['citation_coverage'] = metrics['cited_ree_patents'] / total_ree_patents
        
        # Most cited REE patents
        top_cited = forward_citations['cited_ree_appln_id'].value_counts().head(10)
        metrics['top_cited_patents'] = dict(top_cited)
        
        # Citation timing analysis
        if 'citing_year' in forward_citations.columns:
            citation_years = forward_citations['citing_year'].dropna()
            if not citation_years.empty:
                metrics['citation_year_range'] = f"{citation_years.min()}-{citation_years.max()}"
    
    # Backward citation metrics
    if not backward_citations.empty:
        metrics['total_backward_citations'] = len(backward_citations)
        metrics['citing_ree_patents'] = backward_citations['ree_appln_id'].nunique()
        metrics['average_backward_citations_per_patent'] = len(backward_citations) / total_ree_patents
        
        # Prior art analysis
        if 'cited_year' in backward_citations.columns:
            cited_years = backward_citations['cited_year'].dropna()
            if not cited_years.empty:
                metrics['prior_art_year_range'] = f"{cited_years.min()}-{cited_years.max()}"
    
    # Calculate citation intensity score (0-100)
    citation_score = calculate_citation_intensity_score(metrics)
    metrics['citation_intensity_score'] = citation_score
    
    return metrics

def calculate_citation_intensity_score(metrics: Dict[str, Any]) -> int:
    """
    Calculate citation intensity score for business assessment
    """
    score = 0
    
    # Forward citation volume (40 points max)
    forward_cit = metrics.get('total_forward_citations', 0)
    if forward_cit >= 1000: score += 40
    elif forward_cit >= 500: score += 30
    elif forward_cit >= 200: score += 20
    elif forward_cit >= 100: score += 15
    elif forward_cit >= 50: score += 10
    
    # Citation coverage (30 points max)
    coverage = metrics.get('citation_coverage', 0)
    if coverage >= 0.5: score += 30
    elif coverage >= 0.3: score += 25
    elif coverage >= 0.2: score += 20
    elif coverage >= 0.1: score += 15
    elif coverage >= 0.05: score += 10
    
    # Average citations per patent (20 points max)
    avg_cit = metrics.get('average_citations_per_patent', 0)
    if avg_cit >= 5: score += 20
    elif avg_cit >= 3: score += 15
    elif avg_cit >= 2: score += 12
    elif avg_cit >= 1: score += 8
    elif avg_cit >= 0.5: score += 5
    
    # Backward citation richness (10 points max)
    backward_cit = metrics.get('total_backward_citations', 0)
    if backward_cit >= 500: score += 10
    elif backward_cit >= 200: score += 8
    elif backward_cit >= 100: score += 6
    elif backward_cit >= 50: score += 4
    elif backward_cit >= 20: score += 2
    
    return min(score, 100)

def analyze_citation_networks(forward_citations: pd.DataFrame, backward_citations: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze citation network patterns and technology flow
    """
    network_analysis = {}
    
    if not forward_citations.empty:
        # Citing countries analysis
        citing_countries = forward_citations['citing_country'].value_counts()
        network_analysis['top_citing_countries'] = dict(citing_countries.head(10))
        
        # Citation origins analysis
        citation_origins = forward_citations['citn_origin'].value_counts()
        network_analysis['citation_origin_distribution'] = dict(citation_origins)
        
        # Technology transfer patterns
        if 'citing_office' in forward_citations.columns:
            citing_offices = forward_citations['citing_office'].value_counts()
            network_analysis['top_citing_offices'] = dict(citing_offices.head(10))
    
    if not backward_citations.empty:
        # Prior art sources
        cited_countries = backward_citations['cited_country'].value_counts()
        network_analysis['top_prior_art_countries'] = dict(cited_countries.head(10))
    
    return network_analysis

def perform_complete_citation_analysis(db, ree_appln_ids: List[int], ree_dataset: pd.DataFrame, test_mode: bool = True) -> Dict[str, Any]:
    """
    Perform comprehensive citation analysis pipeline
    """
    logger.info("🔍 STARTING COMPREHENSIVE CITATION ANALYSIS")
    logger.info("=" * 50)
    
    # Get forward citations
    forward_citations = get_forward_citations(db, ree_appln_ids, test_mode)
    
    # Get backward citations  
    backward_citations = get_backward_citations(db, ree_appln_ids, test_mode)
    
    # Calculate metrics
    citation_metrics = calculate_citation_metrics(forward_citations, backward_citations, ree_dataset)
    
    # Analyze networks
    network_analysis = analyze_citation_networks(forward_citations, backward_citations)
    
    # Compile results
    analysis_results = {
        'forward_citations': forward_citations,
        'backward_citations': backward_citations,
        'citation_metrics': citation_metrics,
        'network_analysis': network_analysis
    }
    
    # Log summary
    logger.info("CITATION ANALYSIS COMPLETE")
    logger.info("=" * 50)
    if citation_metrics:
        logger.info(f"Forward citations: {citation_metrics.get('total_forward_citations', 0):,}")
        logger.info(f"Backward citations: {citation_metrics.get('total_backward_citations', 0):,}")
        logger.info(f"Citation intensity score: {citation_metrics.get('citation_intensity_score', 0)}/100")
        logger.info(f"Citation coverage: {citation_metrics.get('citation_coverage', 0):.1%}")
    
    return analysis_results

if __name__ == "__main__":
    # Test the citation analyzer
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    
    logger.info("Testing Citation Analyzer...")
    
    # Get database connection
    db = test_tip_connection()
    if not db:
        logger.error("Cannot test citation analyzer without database connection")
        exit(1)
    
    # Build test dataset
    ree_data = build_ree_dataset(db, test_mode=True)
    if ree_data.empty:
        logger.error("Cannot test citation analyzer without REE dataset")
        exit(1)
    
    # Test citation analysis
    appln_ids = ree_data['appln_id'].tolist()[:100]  # Test with first 100 applications
    citation_results = perform_complete_citation_analysis(db, appln_ids, ree_data, test_mode=True)
    
    print("\n" + "="*60)
    print("CITATION ANALYZER TEST COMPLETE")
    print("="*60)
    
    if citation_results['citation_metrics']:
        metrics = citation_results['citation_metrics']
        print(f"✅ Forward citations: {metrics.get('total_forward_citations', 0):,}")
        print(f"✅ Backward citations: {metrics.get('total_backward_citations', 0):,}")
        print(f"✅ Citation intensity: {metrics.get('citation_intensity_score', 0)}/100")
        print("✅ Ready for geographic analysis")
    else:
        print("❌ Citation analysis returned no results")