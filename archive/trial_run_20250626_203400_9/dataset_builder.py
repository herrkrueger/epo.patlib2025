"""
Dataset Builder Component for REE Patent Citation Analysis
Core search functionality with keywords and CPC codes for 2014-2024 timeframe
"""

import pandas as pd
import logging
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# REE-specific search configuration
REE_KEYWORDS = [
    'rare earth element', 'rare earth elements', 'neodymium', 'dysprosium', 
    'yttrium', 'lanthanide', 'rare earth recovery', 'REE recycling',
    'scandium', 'erbium', 'terbium', 'europium', 'gadolinium', 'cerium',
    'lanthanum', 'praseodymium', 'samarium', 'holmium', 'thulium', 'ytterbium', 'lutetium'
]

REE_CPC_CODES = [
    'C22B%',      # Metallurgy & Metal Extraction
    'Y02W30%',    # Waste Management & Recycling  
    'H01F1%',     # Magnets & Magnetic Materials
    'C09K11%',    # Luminescent Materials
    'Y02P10%',    # Clean Production Technologies
    'C01F17%'     # Rare Earth Compounds
]

def build_keyword_search_query(keywords: List[str], year_start: int = 2014, year_end: int = 2024, limit: Optional[int] = None) -> str:
    """
    Build SQL query for keyword-based REE patent search
    """
    # Create keyword conditions for titles and abstracts
    title_conditions = []
    abstract_conditions = []
    
    for keyword in keywords:
        title_conditions.append(f"LOWER(t.appln_title) LIKE '%{keyword.lower()}%'")
        abstract_conditions.append(f"LOWER(ab.appln_abstract) LIKE '%{keyword.lower()}%'")
    
    title_clause = " OR ".join(title_conditions)
    abstract_clause = " OR ".join(abstract_conditions)
    
    query = f"""
    SELECT DISTINCT 
        a.appln_id, 
        a.docdb_family_id, 
        a.appln_filing_year, 
        a.appln_auth,
        t.appln_title, 
        ab.appln_abstract,
        'keyword' as search_type
    FROM tls201_appln a
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE (
        ({title_clause}) OR 
        ({abstract_clause})
    )
    AND a.appln_filing_year BETWEEN {year_start} AND {year_end}
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    return query

def build_classification_search_query(cpc_codes: List[str], year_start: int = 2014, year_end: int = 2024, limit: Optional[int] = None) -> str:
    """
    Build SQL query for CPC classification-based REE patent search
    """
    # Create CPC conditions
    cpc_conditions = []
    for code in cpc_codes:
        cpc_conditions.append(f"cpc.cpc_class_symbol LIKE '{code}'")
    
    cpc_clause = " OR ".join(cpc_conditions)
    
    query = f"""
    SELECT DISTINCT 
        a.appln_id, 
        a.docdb_family_id, 
        a.appln_filing_year, 
        a.appln_auth,
        t.appln_title,
        ab.appln_abstract,
        cpc.cpc_class_symbol,
        'classification' as search_type
    FROM tls201_appln a
    JOIN tls224_appln_cpc cpc ON a.appln_id = cpc.appln_id
    LEFT JOIN tls202_appln_title t ON a.appln_id = t.appln_id
    LEFT JOIN tls203_appln_abstr ab ON a.appln_id = ab.appln_id
    WHERE ({cpc_clause})
    AND a.appln_filing_year BETWEEN {year_start} AND {year_end}
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    return query

def execute_search_query(db, query: str, search_type: str) -> pd.DataFrame:
    """
    Execute search query with error handling and logging
    """
    try:
        logger.info(f"Executing {search_type} search...")
        result = pd.read_sql(query, db.bind)
        
        if not result.empty:
            logger.info(f"✅ {search_type} search: {len(result)} applications found")
            logger.info(f"   Year range: {result['appln_filing_year'].min()}-{result['appln_filing_year'].max()}")
            logger.info(f"   Countries: {result['appln_auth'].nunique()} unique")
            logger.info(f"   Families: {result['docdb_family_id'].nunique()} unique")
        else:
            logger.warning(f"⚠️  {search_type} search: No results found")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ {search_type} search failed: {e}")
        return pd.DataFrame()

def combine_search_results(keyword_results: pd.DataFrame, classification_results: pd.DataFrame) -> pd.DataFrame:
    """
    Combine and deduplicate search results from different strategies
    """
    if keyword_results.empty and classification_results.empty:
        logger.warning("Both search strategies returned empty results")
        return pd.DataFrame()
    
    elif keyword_results.empty:
        logger.info("Using classification results only")
        return classification_results
    
    elif classification_results.empty:
        logger.info("Using keyword results only")
        return keyword_results
    
    else:
        # Combine results
        logger.info("Combining keyword and classification results...")
        
        # Align columns between datasets
        common_cols = ['appln_id', 'docdb_family_id', 'appln_filing_year', 'appln_auth', 'appln_title', 'appln_abstract', 'search_type']
        
        keyword_aligned = keyword_results[common_cols].copy()
        classification_aligned = classification_results[common_cols].copy()
        
        combined_df = pd.concat([keyword_aligned, classification_aligned], ignore_index=True)
        
        # Deduplicate by application ID, keeping first occurrence
        before_dedup = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['appln_id'], keep='first')
        after_dedup = len(combined_df)
        
        logger.info(f"✅ Combined dataset: {after_dedup} unique applications")
        logger.info(f"   Deduplication: {before_dedup - after_dedup} duplicates removed")
        logger.info(f"   Final families: {combined_df['docdb_family_id'].nunique()}")
        
        return combined_df

def add_search_quality_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add quality scoring based on content richness
    """
    if df.empty:
        return df
    
    df = df.copy()
    df['quality_score'] = 0
    
    # Score based on title content
    df.loc[df['appln_title'].notna(), 'quality_score'] += 10
    df.loc[df['appln_title'].str.len() > 50, 'quality_score'] += 5
    
    # Score based on abstract content
    df.loc[df['appln_abstract'].notna(), 'quality_score'] += 20
    df.loc[df['appln_abstract'].str.len() > 200, 'quality_score'] += 10
    
    # Score based on search type
    df.loc[df['search_type'] == 'classification', 'quality_score'] += 15
    
    logger.info(f"Quality scoring complete. Average score: {df['quality_score'].mean():.1f}")
    
    return df

def build_ree_dataset(db, test_mode: bool = True, year_start: int = 2014, year_end: int = 2024) -> pd.DataFrame:
    """
    Build comprehensive REE dataset with combined search strategies
    
    Args:
        db: Database connection
        test_mode: If True, limit results for testing
        year_start: Start year for search
        year_end: End year for search
    
    Returns:
        DataFrame with REE patent applications
    """
    logger.info(f"Building REE dataset for {year_start}-{year_end}...")
    
    # Set limits for test mode
    limit = 1000 if test_mode else None
    
    # Build and execute keyword search
    keyword_query = build_keyword_search_query(REE_KEYWORDS, year_start, year_end, limit)
    keyword_results = execute_search_query(db, keyword_query, "keyword")
    
    # Build and execute classification search
    classification_query = build_classification_search_query(REE_CPC_CODES, year_start, year_end, limit)
    classification_results = execute_search_query(db, classification_query, "classification")
    
    # Combine results
    combined_results = combine_search_results(keyword_results, classification_results)
    
    if not combined_results.empty:
        # Add quality scoring
        final_dataset = add_search_quality_score(combined_results)
        
        # Log final statistics
        logger.info("\n" + "="*40)
        logger.info("DATASET BUILD COMPLETE")
        logger.info("="*40)
        logger.info(f"Total applications: {len(final_dataset):,}")
        logger.info(f"Unique families: {final_dataset['docdb_family_id'].nunique():,}")
        logger.info(f"Countries covered: {final_dataset['appln_auth'].nunique()}")
        logger.info(f"Year range: {final_dataset['appln_filing_year'].min()}-{final_dataset['appln_filing_year'].max()}")
        logger.info(f"Average quality score: {final_dataset['quality_score'].mean():.1f}")
        
        return final_dataset
    
    else:
        logger.error("❌ No REE applications found with current search strategy")
        return pd.DataFrame()

def get_search_coverage_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze search coverage and effectiveness
    """
    if df.empty:
        return {}
    
    analysis = {
        'total_applications': len(df),
        'search_type_distribution': df['search_type'].value_counts().to_dict(),
        'yearly_distribution': df['appln_filing_year'].value_counts().sort_index().to_dict(),
        'country_distribution': df['appln_auth'].value_counts().head(10).to_dict(),
        'quality_score_stats': {
            'mean': df['quality_score'].mean(),
            'median': df['quality_score'].median(),
            'std': df['quality_score'].std()
        }
    }
    
    return analysis

if __name__ == "__main__":
    # Test the dataset builder
    from database_connection import test_tip_connection
    
    logger.info("Testing Dataset Builder...")
    
    # Get database connection
    db = test_tip_connection()
    if not db:
        logger.error("Cannot test dataset builder without database connection")
        exit(1)
    
    # Build test dataset
    test_dataset = build_ree_dataset(db, test_mode=True)
    
    if not test_dataset.empty:
        # Analyze coverage
        coverage = get_search_coverage_analysis(test_dataset)
        
        print("\n" + "="*50)
        print("DATASET BUILDER TEST COMPLETE")
        print("="*50)
        print(f"✅ Dataset size: {coverage['total_applications']} applications")
        print(f"✅ Search strategy coverage: {coverage['search_type_distribution']}")
        print(f"✅ Quality score: {coverage['quality_score_stats']['mean']:.1f} average")
        print("✅ Ready for citation analysis")
    else:
        print("\n" + "="*50)
        print("❌ DATASET BUILDER TEST FAILED")
        print("="*50)