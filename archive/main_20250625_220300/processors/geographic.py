"""
Geographic Analysis Processor for Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes search results from PatentSearchProcessor to analyze geographic patterns,
competitive landscapes, and international filing strategies. Works with PATSTAT data to 
extract geographic intelligence.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime

# Import PATSTAT client and models for geographic data enrichment
try:
    from epo.tipdata.patstat import PatstatClient
    from epo.tipdata.patstat.database.models import (
        TLS201_APPLN, TLS207_PERS_APPLN, TLS206_PERSON, TLS801_COUNTRY
    )
    from sqlalchemy import func, and_, or_, distinct
    PATSTAT_AVAILABLE = True
except ImportError:
    PATSTAT_AVAILABLE = False
    logging.warning("PATSTAT integration not available")

# Import geographic mappers from data_access
try:
    from data_access.country_mapper import create_country_mapper
    from data_access.nuts_mapper import create_nuts_mapper
    GEOGRAPHIC_MAPPERS_AVAILABLE = True
except ImportError:
    GEOGRAPHIC_MAPPERS_AVAILABLE = False
    logging.warning("Geographic mappers not available, using basic mapping")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeographicAnalyzer:
    """
    Geographic analyzer that works with PatentSearchProcessor results.
    
    Takes patent family search results and enriches them with geographic data from PATSTAT,
    then performs comprehensive geographic intelligence analysis.
    """
    
    # Basic country mapping fallback
    BASIC_COUNTRY_MAPPING = {
        'US': {'name': 'United States', 'continent': 'North America', 'region': 'North America'},
        'CN': {'name': 'China', 'continent': 'Asia', 'region': 'Asia Pacific'},
        'JP': {'name': 'Japan', 'continent': 'Asia', 'region': 'Asia Pacific'},
        'DE': {'name': 'Germany', 'continent': 'Europe', 'region': 'Europe'},
        'GB': {'name': 'United Kingdom', 'continent': 'Europe', 'region': 'Europe'},
        'FR': {'name': 'France', 'continent': 'Europe', 'region': 'Europe'},
        'KR': {'name': 'South Korea', 'continent': 'Asia', 'region': 'Asia Pacific'},
        'CA': {'name': 'Canada', 'continent': 'North America', 'region': 'North America'},
        'IT': {'name': 'Italy', 'continent': 'Europe', 'region': 'Europe'},
        'NL': {'name': 'Netherlands', 'continent': 'Europe', 'region': 'Europe'},
        'CH': {'name': 'Switzerland', 'continent': 'Europe', 'region': 'Europe'},
        'SE': {'name': 'Sweden', 'continent': 'Europe', 'region': 'Europe'},
        'AU': {'name': 'Australia', 'continent': 'Oceania', 'region': 'Asia Pacific'},
        'IN': {'name': 'India', 'continent': 'Asia', 'region': 'Asia Pacific'}
    }
    
    def __init__(self, patstat_client: Optional[object] = None):
        """
        Initialize geographic analyzer with NUTS and country mapping capabilities.
        
        Args:
            patstat_client: PATSTAT client instance for data enrichment
        """
        self.patstat_client = patstat_client
        self.session = None
        self.analyzed_data = None
        self.geographic_data = None
        self.geographic_intelligence = None
        self.country_mapper = None
        self.nuts_mapper = None
        
        # Initialize geographic mappers if available
        if GEOGRAPHIC_MAPPERS_AVAILABLE:
            try:
                self.country_mapper = create_country_mapper(patstat_client)
                self.nuts_mapper = create_nuts_mapper(patstat_client)
                logger.debug("✅ Enhanced country and NUTS mappers initialized")
            except Exception as e:
                logger.warning(f"⚠️ Geographic mappers failed, using basic mapping: {e}")
        
        # Initialize PATSTAT connection
        if PATSTAT_AVAILABLE and self.patstat_client is None:
            try:
                self.patstat_client = PatstatClient(environment='PROD')
                logger.debug("✅ Connected to PATSTAT for geographic data enrichment")
            except Exception as e:
                logger.error(f"❌ Failed to connect to PATSTAT: {e}")
                self.patstat_client = None
        
        if self.patstat_client:
            try:
                # Use the db session from our PatstatClient (preferred method)
                if hasattr(self.patstat_client, 'db') and self.patstat_client.db is not None:
                    self.session = self.patstat_client.db
                    # Get models and SQL functions from our client
                    if hasattr(self.patstat_client, 'models'):
                        self.models = self.patstat_client.models
                    if hasattr(self.patstat_client, 'sql_funcs'):
                        self.sql_funcs = self.patstat_client.sql_funcs
                    logger.debug("✅ PATSTAT session initialized for geographic analysis")
                elif hasattr(self.patstat_client, 'orm') and callable(self.patstat_client.orm):
                    # Fallback to EPO PatstatClient orm method
                    self.session = self.patstat_client.orm()
                    logger.debug("✅ PATSTAT session initialized for geographic analysis (via orm)")
                else:
                    logger.error("❌ No valid PATSTAT session method found")
                    self.session = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize PATSTAT session: {e}")
    
    def analyze_search_results(self, search_results: pd.DataFrame, 
                             analyze_applicants: bool = True,
                             analyze_inventors: bool = False,
                             nuts_level: int = 3) -> pd.DataFrame:
        """
        Analyze patent search results to extract geographic intelligence.
        
        Args:
            search_results: DataFrame from PatentSearchProcessor with columns:
                           ['docdb_family_id', 'quality_score', 'match_type', 'earliest_filing_year', etc.]
            analyze_applicants: Include applicant geographic analysis
            analyze_inventors: Include inventor geographic analysis  
            nuts_level: NUTS hierarchy level for regional analysis (1-3)
                           
        Returns:
            Enhanced DataFrame with geographic intelligence
        """
        logger.debug(f"🌍 Starting geographic analysis of {len(search_results)} patent families...")
        
        if search_results.empty:
            logger.warning("⚠️ No search results to analyze")
            return pd.DataFrame()
        
        # Step 1: Enrich search results with geographic data from PATSTAT
        logger.debug("📊 Step 1: Enriching with geographic data from PATSTAT...")
        logger.debug(f"   Analysis scope: Applicants={analyze_applicants}, Inventors={analyze_inventors}, NUTS Level={nuts_level}")
        geographic_data = self._enrich_with_geographic_data(search_results, analyze_applicants, analyze_inventors, nuts_level)
        
        if geographic_data.empty:
            logger.warning("⚠️ No geographic data found for the search results")
            return pd.DataFrame()
        
        # Step 2: Analyze geographic patterns and distributions
        logger.debug("🗺️ Step 2: Analyzing geographic patterns and distributions...")
        pattern_analysis = self._analyze_geographic_patterns(geographic_data)
        
        # Step 3: Calculate competitive landscapes by region
        logger.debug("🏆 Step 3: Calculating competitive landscapes by region...")
        competitive_analysis = self._analyze_competitive_landscapes(pattern_analysis)
        
        # Step 4: Generate geographic intelligence insights
        logger.debug("🎯 Step 4: Generating geographic intelligence insights...")
        intelligence_analysis = self._generate_geographic_intelligence(competitive_analysis)
        
        self.analyzed_data = intelligence_analysis
        self.geographic_data = geographic_data
        
        logger.debug(f"✅ Geographic analysis complete: {len(intelligence_analysis)} geographic patterns analyzed")
        
        return intelligence_analysis
    
    def _enrich_with_geographic_data(self, search_results: pd.DataFrame,
                                   analyze_applicants: bool = True,
                                   analyze_inventors: bool = False, 
                                   nuts_level: int = 3) -> pd.DataFrame:
        """
        Enrich search results with geographic data from PATSTAT including NUTS codes.
        
        Uses TLS207_PERS_APPLN and TLS206_PERSON tables to get geographic information
        for both applicants and inventors with NUTS regional data support.
        
        Args:
            search_results: Patent family search results
            analyze_applicants: Include applicant data (applt_seq_nr > 0)
            analyze_inventors: Include inventor data (invt_seq_nr > 0)
            nuts_level: Target NUTS level for regional analysis
        """
        if not self.session:
            logger.error("❌ No PATSTAT session available for geographic enrichment")
            return pd.DataFrame()
        
        family_ids = search_results['docdb_family_id'].tolist()
        logger.debug(f"   Enriching {len(family_ids)} families with geographic data...")
        
        # Build role filter conditions
        role_conditions = []
        if analyze_applicants:
            role_conditions.append(TLS207_PERS_APPLN.applt_seq_nr > 0)
        if analyze_inventors:
            role_conditions.append(TLS207_PERS_APPLN.invt_seq_nr > 0)
        
        if not role_conditions:
            logger.error("❌ Must analyze applicants, inventors, or both")
            return pd.DataFrame()
        
        try:
            # Query geographic data including NUTS codes
            geographic_query = self.session.query(
                TLS201_APPLN.docdb_family_id,
                TLS201_APPLN.appln_id,
                TLS201_APPLN.earliest_filing_year,
                TLS207_PERS_APPLN.person_id,
                TLS207_PERS_APPLN.applt_seq_nr,
                TLS207_PERS_APPLN.invt_seq_nr,
                TLS206_PERSON.person_name,
                TLS206_PERSON.person_address,
                TLS206_PERSON.person_ctry_code,
                TLS206_PERSON.nuts.label('nuts_code'),
                TLS206_PERSON.nuts_level
            ).select_from(TLS201_APPLN)\
            .join(TLS207_PERS_APPLN, TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id)\
            .join(TLS206_PERSON, TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id)\
            .filter(
                and_(
                    TLS201_APPLN.docdb_family_id.in_(family_ids),
                    role_conditions[0] if len(role_conditions) == 1 else or_(*role_conditions)
                )
            )
            
            result = geographic_query.all()
            
            if not result:
                logger.warning("⚠️ No geographic data found in PATSTAT for these families")
                return pd.DataFrame()
            
            # Convert to DataFrame with NUTS data
            geographic_df = pd.DataFrame(result, columns=[
                'docdb_family_id', 'appln_id', 'earliest_filing_year', 'person_id',
                'applt_seq_nr', 'invt_seq_nr', 'person_name', 'person_address', 
                'person_ctry_code', 'nuts_code', 'nuts_level'
            ])
            
            # Add role identification
            geographic_df['is_applicant'] = geographic_df['applt_seq_nr'] > 0
            geographic_df['is_inventor'] = geographic_df['invt_seq_nr'] > 0
            geographic_df['person_role'] = geographic_df.apply(
                lambda row: 'Applicant' if row['is_applicant'] and not row['is_inventor']
                           else 'Inventor' if row['is_inventor'] and not row['is_applicant']
                           else 'Both' if row['is_applicant'] and row['is_inventor']
                           else 'Unknown', axis=1
            )
            
            # Merge with original search results to preserve quality scores
            enriched_data = search_results.merge(
                geographic_df,
                on='docdb_family_id',
                how='inner',
                suffixes=('', '_patstat')  # Keep original column names
            )
            
            # Fix duplicate column names - prefer search results version
            if 'appln_id_patstat' in enriched_data.columns:
                enriched_data = enriched_data.drop('appln_id_patstat', axis=1)
            if 'earliest_filing_year_patstat' in enriched_data.columns:
                enriched_data = enriched_data.drop('earliest_filing_year_patstat', axis=1)
            
            # Clean and standardize geographic data with NUTS support
            enriched_data = self._clean_geographic_data_with_nuts(enriched_data, nuts_level)
            
            logger.debug(f"   ✅ Enriched {len(enriched_data)} geographic relationships")
            logger.debug(f"   🗺️ Covering {enriched_data['docdb_family_id'].nunique()} families")
            logger.debug(f"   🌍 Found {enriched_data['person_ctry_code'].nunique()} unique countries")
            if 'nuts_code' in enriched_data.columns:
                nuts_coverage = enriched_data['nuts_code'].notna().sum()
                logger.debug(f"   🇪🇺 NUTS coverage: {nuts_coverage}/{len(enriched_data)} ({nuts_coverage/len(enriched_data)*100:.1f}%)")
            logger.debug(f"   👥 Role distribution: {enriched_data['person_role'].value_counts().to_dict()}")
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"❌ Failed to enrich with geographic data: {e}")
            logger.warning("⚠️ Falling back to basic geographic mapping from search results")
            
            # Fallback: use basic country mapping from search results if available
            fallback_data = search_results.copy()
            
            # Add basic geographic columns that processors expect
            fallback_data['person_ctry_code'] = 'XX'  # Unknown country
            fallback_data['geographic_level'] = 'country'
            fallback_data['primary_region'] = 'Unknown'
            fallback_data['geographic_quality'] = 0.1  # Low quality fallback
            fallback_data['family_country_count'] = 1
            
            return fallback_data
    
    def _clean_geographic_data_with_nuts(self, df: pd.DataFrame, nuts_level: int = 3) -> pd.DataFrame:
        """Clean geographic data from PATSTAT with NUTS support."""
        logger.debug(f"🧹 Cleaning PATSTAT geographic data with NUTS level {nuts_level} support...")
        
        # Clean country codes
        df['person_ctry_code'] = df['person_ctry_code'].fillna('XX')
        df['person_ctry_code'] = df['person_ctry_code'].str.upper().str.strip()
        df['person_ctry_code'] = df['person_ctry_code'].replace(['', 'NULL', 'NONE'], 'XX')
        
        # Clean NUTS codes
        df['nuts_code'] = df['nuts_code'].astype(str).str.strip()
        df['nuts_code'] = df['nuts_code'].replace(['nan', 'None', 'NULL', ''], None)
        df['nuts_level'] = df['nuts_level'].fillna(9)  # Level 9 = no NUTS assigned
        
        # Handle NUTS data quality issues
        df['has_nuts'] = df['nuts_code'].notna() & (df['nuts_level'] != 9)
        df['nuts_coverage'] = df['has_nuts'].apply(lambda x: 'NUTS Available' if x else 'Country Only')
        
        # Add enhanced geographic information using mappers
        enhanced_geo_data = []
        for _, row in df.iterrows():
            ctry_code = row['person_ctry_code']
            nuts_code = row['nuts_code']
            
            # Get country information
            country_info = self._get_country_info(ctry_code)
            
            # Get NUTS information if available
            nuts_info = self._get_nuts_info(nuts_code) if pd.notna(nuts_code) else {}
            
            # Determine primary geographic level based on target nuts_level
            if row['has_nuts'] and nuts_code:
                # Use NUTS mapper to get appropriate level
                if self.nuts_mapper:
                    hierarchy = self.nuts_mapper.get_nuts_hierarchy(nuts_code)
                    target_nuts = self._get_target_nuts_from_hierarchy(hierarchy, nuts_level)
                    region_name = self.nuts_mapper.get_nuts_name(target_nuts) if target_nuts else country_info['name']
                    geographic_level = f'NUTS{nuts_level}'
                    primary_region = target_nuts or ctry_code
                else:
                    region_name = nuts_info.get('nuts_label', country_info['name'])
                    geographic_level = f'NUTS{row["nuts_level"]}'
                    primary_region = nuts_code
            else:
                # Fallback to country level
                region_name = country_info['name']
                geographic_level = 'Country'
                primary_region = ctry_code
            
            enhanced_geo_data.append({
                'country_name': country_info['name'],
                'continent': country_info.get('continent', 'Unknown'),
                'region': country_info.get('region', 'Other'),
                'nuts_region_name': region_name,
                'geographic_level': geographic_level,
                'primary_region': primary_region,
                'is_major_economy': ctry_code in ['US', 'CN', 'JP', 'DE', 'GB', 'FR', 'IT', 'CA', 'KR'],
                'is_ip5_office': ctry_code in ['US', 'CN', 'JP', 'EP', 'KR'],
                'is_emerging_market': ctry_code in ['CN', 'IN', 'BR', 'RU', 'MX', 'TR', 'ID', 'SA'],
                'is_eu_nuts': row['has_nuts']
            })
        
        enhanced_geo_df = pd.DataFrame(enhanced_geo_data)
        df = pd.concat([df, enhanced_geo_df], axis=1)
        
        # Handle family size information
        family_size_data = df.groupby('docdb_family_id').agg({
            'person_ctry_code': 'nunique'
        }).rename(columns={'person_ctry_code': 'family_country_count'}).reset_index()
        
        df = df.merge(family_size_data, on='docdb_family_id', how='left')
        
        # Add filing strategy classification
        df['filing_strategy'] = pd.cut(
            df['family_country_count'],
            bins=[0, 1, 3, 8, float('inf')],
            labels=['Domestic', 'Regional', 'Global', 'Premium Global']
        )
        
        return df
    
    def _get_country_info(self, country_code: str) -> Dict[str, str]:
        """Get country information using enhanced mapper or fallback."""
        if self.country_mapper:
            try:
                return self.country_mapper.get_country_info(country_code)
            except:
                pass
        
        # Fallback to basic mapping
        return self.BASIC_COUNTRY_MAPPING.get(country_code, {
            'name': country_code,
            'continent': 'Unknown',
            'region': 'Other'
        })
    
    def _get_nuts_info(self, nuts_code: str) -> Dict[str, str]:
        """Get NUTS information using NUTS mapper or fallback."""
        if self.nuts_mapper and nuts_code:
            try:
                return self.nuts_mapper.get_nuts_info(nuts_code)
            except:
                pass
        
        # Fallback for NUTS data
        return {
            'nuts_code': nuts_code or 'Unknown',
            'nuts_label': 'Unknown Region',
            'nuts_level': 9
        }
    
    def _get_target_nuts_from_hierarchy(self, hierarchy: List[str], target_level: int) -> Optional[str]:
        """Extract NUTS code at target level from hierarchy."""
        if not hierarchy or target_level < 0:
            return None
        
        # NUTS levels: 0=Country (2 chars), 1=3 chars, 2=4 chars, 3=5 chars
        target_length = 2 + target_level if target_level > 0 else 2
        
        for code in hierarchy:
            if len(code) == target_length:
                return code
        
        # Return deepest available if target not found
        return hierarchy[-1] if hierarchy else None
    
    def _analyze_geographic_patterns(self, geographic_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze geographic patterns and distributions.
        """
        logger.debug("🗺️ Analyzing geographic patterns...")
        
        # Check available year columns
        year_col = None
        for col in ['earliest_filing_year_x', 'earliest_filing_year_y', 'earliest_filing_year']:
            if col in geographic_data.columns:
                year_col = col
                break
        
        if year_col is None:
            logger.error("❌ No filing year column found for geographic analysis")
            return pd.DataFrame()
        
        logger.debug(f"   Using year column: {year_col}")
        
        # Aggregate by country
        agg_dict = {
            'docdb_family_id': 'nunique',
            'appln_id': 'nunique',
            'family_country_count': 'mean',
            year_col: ['min', 'max', 'mean']
        }
        
        # Add optional columns if they exist
        if 'quality_score' in geographic_data.columns:
            agg_dict['quality_score'] = 'mean'
        
        # Group by primary region (NUTS level or country)
        # Use nuts_region_name for more granular analysis when NUTS available
        primary_grouping_col = 'nuts_region_name'
        if primary_grouping_col not in geographic_data.columns:
            primary_grouping_col = 'country_name'
        
        region_analysis = geographic_data.groupby([primary_grouping_col, 'geographic_level']).agg(agg_dict).reset_index()
        
        # Flatten column names
        flattened_columns = []
        for col in region_analysis.columns:
            if isinstance(col, tuple):
                if col[1] == '':
                    flattened_columns.append(col[0])
                elif col[1] == 'min':
                    flattened_columns.append('first_filing_year')
                elif col[1] == 'max':
                    flattened_columns.append('latest_filing_year')
                elif col[1] == 'mean' and col[0] == year_col:
                    flattened_columns.append('avg_filing_year')
                else:
                    flattened_columns.append(f"{col[0]}_{col[1]}")
            else:
                flattened_columns.append(col)
        
        region_analysis.columns = flattened_columns
        
        # Map column names
        column_mapping = {
            'docdb_family_id_nunique': 'patent_families',
            'appln_id_nunique': 'total_applications',
            'family_country_count_mean': 'avg_internationalization',
            'quality_score_mean': 'avg_search_quality'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in region_analysis.columns:
                region_analysis = region_analysis.rename(columns={old_name: new_name})
        
        # Add missing columns with defaults
        if 'avg_search_quality' not in region_analysis.columns:
            region_analysis['avg_search_quality'] = 2.0
        
        # Calculate geographic metrics
        total_families = region_analysis['patent_families'].sum()
        region_analysis['market_share_pct'] = (region_analysis['patent_families'] / total_families * 100).round(2)
        region_analysis['activity_span'] = region_analysis['latest_filing_year'] - region_analysis['first_filing_year'] + 1
        
        # Add region information from original data
        region_info_cols = ['nuts_region_name', 'country_name', 'region', 'continent', 'geographic_level']
        available_cols = [col for col in region_info_cols if col in geographic_data.columns]
        
        if len(available_cols) > 1:
            region_map = geographic_data[available_cols].drop_duplicates()
            merge_col = primary_grouping_col
            if merge_col in region_map.columns:
                region_analysis = region_analysis.merge(region_map, on=[merge_col, 'geographic_level'], how='left')
        
        # Sort by patent families
        region_analysis = region_analysis.sort_values('patent_families', ascending=False).reset_index(drop=True)
        region_analysis['regional_rank'] = range(1, len(region_analysis) + 1)
        
        # Add NUTS-specific analysis
        if 'geographic_level' in region_analysis.columns:
            nuts_summary = region_analysis['geographic_level'].value_counts()
            logger.debug(f"   🇪🇺 Geographic level distribution: {nuts_summary.to_dict()}")
        
        logger.debug(f"   ✅ Analyzed geographic patterns for {len(region_analysis)} regions")
        if len(region_analysis) > 0:
            top_region = region_analysis.iloc[0]
            logger.debug(f"   🏆 Top region: {top_region[primary_grouping_col]} ({top_region['patent_families']} families, {top_region['geographic_level']})")
        
        return region_analysis
    
    def analyze_inventor_geography(self, search_results: pd.DataFrame, nuts_level: int = 3) -> pd.DataFrame:
        """
        Specialized analysis for inventor geographic patterns.
        
        Args:
            search_results: Patent family search results
            nuts_level: NUTS level for regional analysis
            
        Returns:
            DataFrame with inventor-specific geographic analysis
        """
        logger.debug("👨‍🔬 Starting inventor-specific geographic analysis...")
        
        # Run geographic analysis focused on inventors
        inventor_data = self.analyze_search_results(
            search_results, 
            analyze_applicants=False, 
            analyze_inventors=True, 
            nuts_level=nuts_level
        )
        
        if inventor_data.empty:
            logger.warning("⚠️ No inventor geographic data found")
            return pd.DataFrame()
        
        # Add inventor-specific insights
        inventor_data['innovation_geography'] = inventor_data.apply(
            lambda row: f"{row.get('nuts_region_name', row.get('country_name', 'Unknown'))} "
                       f"({row.get('geographic_level', 'Country')})", axis=1
        )
        
        # Calculate innovation density metrics
        if 'patent_families' in inventor_data.columns:
            inventor_data['innovation_density_score'] = inventor_data['patent_families'] / inventor_data['patent_families'].max()
        
        logger.debug(f"✅ Inventor geographic analysis complete: {len(inventor_data)} innovation regions")
        
        return inventor_data
    
    def analyze_applicant_geography(self, search_results: pd.DataFrame, nuts_level: int = 3) -> pd.DataFrame:
        """
        Specialized analysis for applicant geographic patterns.
        
        Args:
            search_results: Patent family search results
            nuts_level: NUTS level for regional analysis
            
        Returns:
            DataFrame with applicant-specific geographic analysis
        """
        logger.debug("🏢 Starting applicant-specific geographic analysis...")
        
        # Run geographic analysis focused on applicants
        applicant_data = self.analyze_search_results(
            search_results, 
            analyze_applicants=True, 
            analyze_inventors=False, 
            nuts_level=nuts_level
        )
        
        if applicant_data.empty:
            logger.warning("⚠️ No applicant geographic data found")
            return pd.DataFrame()
        
        # Add applicant-specific insights
        applicant_data['filing_geography'] = applicant_data.apply(
            lambda row: f"{row.get('nuts_region_name', row.get('country_name', 'Unknown'))} "
                       f"({row.get('geographic_level', 'Country')})", axis=1
        )
        
        # Calculate market presence metrics
        if 'patent_families' in applicant_data.columns:
            applicant_data['market_presence_score'] = applicant_data['patent_families'] / applicant_data['patent_families'].max()
        
        logger.debug(f"✅ Applicant geographic analysis complete: {len(applicant_data)} market regions")
        
        return applicant_data
    
    def compare_innovation_vs_filing_geography(self, search_results: pd.DataFrame, nuts_level: int = 3) -> Dict:
        """
        Compare innovation geography (inventors) vs filing geography (applicants).
        
        Args:
            search_results: Patent family search results
            nuts_level: NUTS level for regional analysis
            
        Returns:
            Dictionary with comparative analysis
        """
        logger.debug("🔬🏢 Comparing innovation vs filing geography...")
        
        # Get both analyses
        inventor_data = self.analyze_inventor_geography(search_results, nuts_level)
        applicant_data = self.analyze_applicant_geography(search_results, nuts_level)
        
        if inventor_data.empty or applicant_data.empty:
            logger.warning("⚠️ Insufficient data for geographic comparison")
            return {}
        
        # Extract region names for comparison
        inventor_regions = set(inventor_data.get('nuts_region_name', inventor_data.get('country_name', [])))
        applicant_regions = set(applicant_data.get('nuts_region_name', applicant_data.get('country_name', [])))
        
        # Calculate overlap and differences
        common_regions = inventor_regions.intersection(applicant_regions)
        innovation_only = inventor_regions - applicant_regions
        filing_only = applicant_regions - inventor_regions
        
        comparison = {
            'overview': {
                'innovation_regions': len(inventor_regions),
                'filing_regions': len(applicant_regions),
                'common_regions': len(common_regions),
                'innovation_only_regions': len(innovation_only),
                'filing_only_regions': len(filing_only),
                'geographic_overlap_pct': len(common_regions) / max(len(inventor_regions), 1) * 100
            },
            'regional_analysis': {
                'common_regions': list(common_regions),
                'innovation_hotspots': list(innovation_only),
                'filing_centers': list(filing_only)
            },
            'top_innovation_regions': inventor_data.head(5)[['nuts_region_name', 'patent_families', 'geographic_level']].to_dict('records') if len(inventor_data) > 0 else [],
            'top_filing_regions': applicant_data.head(5)[['nuts_region_name', 'patent_families', 'geographic_level']].to_dict('records') if len(applicant_data) > 0 else []
        }
        
        logger.debug(f"✅ Geographic comparison complete: {comparison['overview']['geographic_overlap_pct']:.1f}% overlap")
        
        return comparison
    
    def _analyze_competitive_landscapes(self, pattern_analysis: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze competitive landscapes by region and country.
        """
        logger.debug("🏆 Analyzing competitive landscapes...")
        
        # Add competitive tier classification
        pattern_analysis['competitive_tier'] = pd.cut(
            pattern_analysis['market_share_pct'],
            bins=[0, 1, 5, 15, float('inf')],
            labels=['Niche Player', 'Active Participant', 'Major Player', 'Market Leader']
        )
        
        # Add international strategy classification
        pattern_analysis['international_strategy'] = pd.cut(
            pattern_analysis['avg_internationalization'],
            bins=[0, 2, 5, 10, float('inf')],
            labels=['Domestic Focus', 'Regional Strategy', 'Global Strategy', 'Premium Global']
        )
        
        # Calculate innovation density (families per year of activity)
        pattern_analysis['innovation_density'] = (
            pattern_analysis['patent_families'] / pattern_analysis['activity_span']
        ).round(2)
        
        return pattern_analysis
    
    def _generate_geographic_intelligence(self, competitive_analysis: pd.DataFrame) -> pd.DataFrame:
        """
        Generate comprehensive geographic intelligence insights.
        """
        logger.debug("🎯 Generating geographic intelligence insights...")
        
        # Enhance competitive analysis with strategic insights
        enhanced_analysis = competitive_analysis.copy()
        
        # Calculate global reach index
        max_families = enhanced_analysis['patent_families'].max() if not enhanced_analysis.empty else 1
        enhanced_analysis['global_reach_index'] = (
            (enhanced_analysis['patent_families'] / max_families) * 0.4 +
            (enhanced_analysis['avg_internationalization'] / 10) * 0.3 +
            enhanced_analysis['avg_search_quality'] / 3 * 0.3
        ).round(3)
        
        # Strategic importance scoring
        def calculate_strategic_importance(row):
            score = 0
            # Market share weight
            if row['market_share_pct'] > 20:
                score += 4
            elif row['market_share_pct'] > 10:
                score += 3
            elif row['market_share_pct'] > 5:
                score += 2
            elif row['market_share_pct'] > 1:
                score += 1
            
            # Innovation density weight
            if row['innovation_density'] > 5:
                score += 2
            elif row['innovation_density'] > 2:
                score += 1
            
            # International reach weight
            if row['avg_internationalization'] > 8:
                score += 2
            elif row['avg_internationalization'] > 4:
                score += 1
            
            return score
        
        enhanced_analysis['strategic_importance_score'] = enhanced_analysis.apply(calculate_strategic_importance, axis=1)
        
        # Strategic category
        def assign_strategic_category(score: int) -> str:
            if score >= 7:
                return 'Global Powerhouse'
            elif score >= 5:
                return 'Regional Leader'
            elif score >= 3:
                return 'Active Market'
            else:
                return 'Emerging Market'
        
        enhanced_analysis['strategic_category'] = enhanced_analysis['strategic_importance_score'].apply(assign_strategic_category)
        
        # Market maturity assessment
        def assess_market_maturity(row):
            if row['activity_span'] > 10 and row['patent_families'] > 20:
                return 'Mature'
            elif row['activity_span'] > 5:
                return 'Developing'
            else:
                return 'Emerging'
        
        enhanced_analysis['market_maturity'] = enhanced_analysis.apply(assess_market_maturity, axis=1)
        
        return enhanced_analysis
    
    def _clean_geographic_data(self, df: pd.DataFrame, country_col: str) -> pd.DataFrame:
        """Clean and standardize geographic data using enhanced country mapping."""
        logger.debug("🧹 Cleaning geographic data with enhanced mapping...")
        
        # Handle missing values
        df[country_col] = df[country_col].fillna('XX')
        df[country_col] = df[country_col].replace('', 'XX')
        
        # Standardize country codes
        df[country_col] = df[country_col].str.upper().str.strip()
        
        # Use enhanced country mapping
        enhanced_data = []
        for _, row in df.iterrows():
            country_info = self.country_mapper.get_country_info(row[country_col])
            enhanced_data.append({
                'country_name': country_info['name'],
                'iso_country_code': country_info.get('alpha_3', ''),
                'continent': country_info['continent'],
                'is_eu_member': country_info.get('is_eu_member', False),
                'is_epo_member': country_info.get('is_epo_member', False),
                'is_oecd_member': country_info.get('is_oecd_member', False),
                'regional_groups': country_info.get('regional_groups', []),
                'data_source': country_info.get('source', 'unknown')
            })
        
        enhanced_df = pd.DataFrame(enhanced_data)
        df = pd.concat([df, enhanced_df], axis=1)
        
        return df
    
    def _add_geographic_metadata(self, df: pd.DataFrame, country_col: str) -> pd.DataFrame:
        """Add enhanced geographic metadata using configuration-driven approach."""
        logger.debug("🗺️ Adding enhanced geographic metadata...")
        
        # Regional groupings are already added by the country mapper
        # Add primary region based on regional groups
        def get_primary_region(regional_groups_list: List[str]) -> str:
            """Get primary region from list of regional groups."""
            if not regional_groups_list:
                return 'Other'
            
            # Priority mapping for primary region assignment
            region_priority = {
                'europe': 'Europe',
                'north_america': 'North America', 
                'asia_pacific': 'Asia Pacific',
                'ip5_offices': 'Major Patent Offices',
                'major_economies': 'Major Economies'
            }
            
            # Return first matching priority region
            for region in regional_groups_list:
                if region in region_priority:
                    return region_priority[region]
            
            # Default to first group if no priority match
            return regional_groups_list[0].replace('_', ' ').title()
        
        df['region'] = df['regional_groups'].apply(
            lambda x: get_primary_region(x) if isinstance(x, list) else 'Other'
        )
        
        # Enhanced economic classification using country mapper groups
        def classify_economy_enhanced(country_code: str) -> str:
            """Enhanced economy classification using country mapper."""
            if self.country_mapper.is_in_group(country_code, 'developed'):
                return 'Developed'
            elif self.country_mapper.is_in_group(country_code, 'emerging'):
                return 'Emerging'
            else:
                return 'Developing'
        
        df['economy_type'] = df[country_col].apply(classify_economy_enhanced)
        
        # Add strategic classifications
        df['is_ip5_office'] = df[country_col].apply(
            lambda x: self.country_mapper.is_in_group(x, 'ip5_offices')
        )
        df['is_major_economy'] = df[country_col].apply(
            lambda x: self.country_mapper.is_in_group(x, 'major_economies')
        )
        df['is_emerging_market'] = df[country_col].apply(
            lambda x: self.country_mapper.is_in_group(x, 'emerging_markets')
        )
        
        return df
    
    def _analyze_filing_strategies(self, df: pd.DataFrame, family_size_col: str) -> pd.DataFrame:
        """Analyze strategic filing patterns based on family sizes."""
        logger.debug("🎯 Analyzing filing strategies...")
        
        if family_size_col in df.columns:
            # Strategic classification based on family size
            df['filing_strategy'] = pd.cut(
                df[family_size_col],
                bins=[0, 2, 5, 10, float('inf')],
                labels=['Domestic Focus', 'Regional Strategy', 'Global Strategy', 'Premium Global']
            )
            
            # Calculate strategic intensity
            df['strategic_intensity'] = df[family_size_col].apply(
                lambda x: 'High' if x >= 10 else 'Medium' if x >= 5 else 'Low'
            )
        else:
            logger.warning(f"⚠️ {family_size_col} column not found, skipping family size analysis")
            df['filing_strategy'] = 'Unknown'
            df['strategic_intensity'] = 'Unknown'
        
        return df
    
    def _add_temporal_patterns(self, df: pd.DataFrame, year_col: str) -> pd.DataFrame:
        """Add temporal analysis patterns."""
        logger.debug("📅 Adding temporal patterns...")
        
        # Time period classification
        df['filing_period'] = pd.cut(
            df[year_col],
            bins=[2009, 2014, 2018, 2022, float('inf')],
            labels=['Early (2010-2014)', 'Growth (2015-2018)', 'Recent (2019-2022)', 'Latest (2023+)']
        )
        
        # Decade classification
        df['filing_decade'] = pd.cut(
            df[year_col],
            bins=[2009, 2019, float('inf')],
            labels=['2010s', '2020s+']
        )
        
        return df
    
    def _calculate_geographic_competitiveness(self, df: pd.DataFrame, 
                                           family_col: str) -> pd.DataFrame:
        """Calculate geographic competitiveness metrics."""
        logger.debug("🏆 Calculating geographic competitiveness...")
        
        # Calculate country-level metrics
        country_metrics = df.groupby('country_name').agg({
            family_col: 'nunique',
            'country_name': 'count'
        }).rename(columns={
            family_col: 'unique_families',
            'country_name': 'total_records'
        })
        
        # Add market share calculations
        total_families = country_metrics['unique_families'].sum()
        country_metrics['market_share_pct'] = (
            country_metrics['unique_families'] / total_families * 100
        ).round(2)
        
        # Competitive tier classification
        country_metrics['competitive_tier'] = pd.cut(
            country_metrics['market_share_pct'],
            bins=[0, 1, 5, 15, float('inf')],
            labels=['Niche Player', 'Active Participant', 'Major Player', 'Market Leader']
        )
        
        # Merge back to main dataframe
        df = df.merge(
            country_metrics.add_suffix('_country'),
            left_on='country_name',
            right_index=True,
            how='left'
        )
        
        return df
    
    def generate_geographic_intelligence_summary(self) -> Dict:
        """
        Generate comprehensive geographic intelligence summary.
        
        Returns:
            Dictionary with geographic intelligence insights
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        df = self.analyzed_data
        logger.debug("📋 Generating geographic intelligence summary...")
        
        total_families = df['patent_families'].sum()
        top_country = df.iloc[0] if len(df) > 0 else None
        
        summary = {
            'geographic_overview': {
                'total_patent_families': int(total_families),
                'total_countries': len(df),
                'total_regions': df['region'].nunique(),
                'dominant_country': top_country['country_name'] if top_country is not None else 'N/A',
                'dominant_country_share': float(top_country['market_share_pct']) if top_country is not None else 0,
                'avg_internationalization': float(df['avg_internationalization'].mean()),
                'top_region': df.groupby('region')['patent_families'].sum().idxmax() if not df.empty else 'N/A'
            },
            'country_distribution': df[['country_name', 'patent_families', 'market_share_pct']].head(10).to_dict('records'),
            'regional_distribution': df.groupby('region')['patent_families'].sum().to_dict(),
            'competitive_tiers': df['competitive_tier'].value_counts().to_dict(),
            'strategic_categories': df['strategic_category'].value_counts().to_dict(),
            'market_maturity': df['market_maturity'].value_counts().to_dict(),
            'filing_strategies': df['international_strategy'].value_counts().to_dict(),
            'geographic_metrics': {
                'avg_global_reach': float(df['global_reach_index'].mean()),
                'innovation_density_avg': float(df['innovation_density'].mean()),
                'powerhouse_countries': len(df[df['strategic_category'] == 'Global Powerhouse']),
                'mature_markets': len(df[df['market_maturity'] == 'Mature']),
                'market_concentration_hhi': self._calculate_hhi_simple(df['market_share_pct'])
            },
            'temporal_insights': {
                'earliest_activity': int(df['first_filing_year'].min()) if not df.empty else None,
                'latest_activity': int(df['latest_filing_year'].max()) if not df.empty else None,
                'avg_activity_span': float(df['activity_span'].mean()),
                'most_sustained_country': df.loc[df['activity_span'].idxmax(), 'country_name'] if not df.empty else 'N/A'
            }
        }
        
        self.geographic_intelligence = summary
        return summary
    
    def _calculate_hhi_simple(self, market_shares: pd.Series) -> float:
        """Calculate simple HHI for market concentration."""
        return float((market_shares ** 2).sum())
    
    def get_top_countries(self, top_n: int = 10, min_families: int = 1) -> pd.DataFrame:
        """
        Get top countries with filtering options.
        
        Args:
            top_n: Number of top countries to return
            min_families: Minimum number of patent families required
            
        Returns:
            Filtered DataFrame with top countries
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        filtered_df = self.analyzed_data[self.analyzed_data['patent_families'] >= min_families].copy()
        return filtered_df.head(top_n)
    
    def get_geographic_hotspots(self, top_n: int = 5) -> pd.DataFrame:
        """
        Get geographic hotspots based on multiple criteria.
        
        Args:
            top_n: Number of hotspots to return
            
        Returns:
            DataFrame with geographic hotspots
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        # Sort by global reach index and strategic importance
        hotspots = self.analyzed_data.sort_values(
            ['global_reach_index', 'strategic_importance_score'], 
            ascending=False
        ).head(top_n)
        
        return hotspots[['country_name', 'patent_families', 'market_share_pct', 'global_reach_index', 'strategic_category', 'market_maturity']]

    # Legacy method for backward compatibility (deprecated)
    def generate_geographic_summary(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive geographic intelligence summary.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with geographic intelligence insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_geographic_patterns first.")
        
        logger.debug("📋 Generating geographic intelligence summary...")
        
        # Country-level summary
        country_summary = df.groupby('country_name').agg({
            'docdb_family_id': 'nunique',
            'docdb_family_size': 'mean' if 'docdb_family_size' in df.columns else 'count',
            'earliest_filing_year': ['min', 'max']
        }).round(2)
        
        country_summary.columns = ['unique_families', 'avg_family_size', 'first_year', 'latest_year']
        country_summary = country_summary.sort_values('unique_families', ascending=False)
        
        # Regional analysis
        regional_summary = df.groupby('region').agg({
            'docdb_family_id': 'nunique',
            'country_name': 'nunique'
        }).rename(columns={
            'docdb_family_id': 'total_families',
            'country_name': 'active_countries'
        })
        
        # Strategic analysis
        filing_strategy_analysis = df['filing_strategy'].value_counts().to_dict() if 'filing_strategy' in df.columns else {}
        period_analysis = df['filing_period'].value_counts().to_dict() if 'filing_period' in df.columns else {}
        
        summary = {
            'overview': {
                'total_countries': df['country_name'].nunique(),
                'total_regions': df['region'].nunique(),
                'total_unique_families': df['docdb_family_id'].nunique(),
                'dominant_country': country_summary.index[0] if len(country_summary) > 0 else 'N/A',
                'dominant_region': regional_summary.sort_values('total_families', ascending=False).index[0] if len(regional_summary) > 0 else 'N/A'
            },
            'country_rankings': country_summary.head(10).to_dict('index'),
            'regional_distribution': regional_summary.to_dict('index'),
            'filing_strategies': filing_strategy_analysis,
            'temporal_patterns': period_analysis,
            'market_concentration': {
                'top_3_countries_share': float(country_summary.head(3)['unique_families'].sum() / country_summary['unique_families'].sum() * 100),
                'top_5_countries_share': float(country_summary.head(5)['unique_families'].sum() / country_summary['unique_families'].sum() * 100),
                'herfindahl_index': self._calculate_hhi(country_summary['unique_families'])
            }
        }
        
        self.geographic_intelligence = summary
        return summary
    
    def _calculate_hhi(self, market_shares: pd.Series) -> float:
        """Calculate Herfindahl-Hirschman Index for market concentration."""
        total = market_shares.sum()
        percentages = (market_shares / total) * 100
        hhi = (percentages ** 2).sum()
        return float(hhi)
    
    def get_competitive_landscape_by_region(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Get competitive landscape analysis by region.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with regional competitive analysis
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_geographic_patterns first.")
        
        regional_landscape = {}
        
        for region in df['region'].unique():
            region_data = df[df['region'] == region]
            
            country_performance = region_data.groupby('country_name').agg({
                'docdb_family_id': 'nunique',
                'docdb_family_size': 'mean' if 'docdb_family_size' in df.columns else 'count'
            }).round(2)
            
            country_performance.columns = ['unique_families', 'avg_family_size']
            country_performance = country_performance.sort_values('unique_families', ascending=False)
            
            regional_landscape[region] = {
                'total_countries': len(country_performance),
                'total_families': int(country_performance['unique_families'].sum()),
                'leading_country': country_performance.index[0] if len(country_performance) > 0 else 'N/A',
                'leader_families': int(country_performance.iloc[0]['unique_families']) if len(country_performance) > 0 else 0,
                'country_rankings': country_performance.head(5).to_dict('index'),
                'regional_concentration': float(country_performance.iloc[0]['unique_families'] / country_performance['unique_families'].sum() * 100) if len(country_performance) > 0 else 0
            }
        
        return regional_landscape
    
    def analyze_filing_evolution(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Analyze the evolution of filing patterns over time by geography.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            DataFrame with temporal evolution analysis
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_geographic_patterns first.")
        
        logger.debug("📈 Analyzing filing evolution over time...")
        
        # Group by country and year
        evolution_analysis = df.groupby(['country_name', 'earliest_filing_year']).agg({
            'docdb_family_id': 'nunique',
            'docdb_family_size': 'mean' if 'docdb_family_size' in df.columns else 'count'
        }).reset_index()
        
        evolution_analysis.columns = ['country_name', 'filing_year', 'families_count', 'avg_family_size']
        
        # Calculate year-over-year growth
        evolution_analysis = evolution_analysis.sort_values(['country_name', 'filing_year'])
        evolution_analysis['families_growth'] = evolution_analysis.groupby('country_name')['families_count'].pct_change()
        
        # Calculate cumulative totals
        evolution_analysis['cumulative_families'] = evolution_analysis.groupby('country_name')['families_count'].cumsum()
        
        # Add trend classification
        def classify_trend(growth_rate):
            if pd.isna(growth_rate):
                return 'Initial'
            elif growth_rate > 0.5:
                return 'High Growth'
            elif growth_rate > 0.1:
                return 'Moderate Growth'
            elif growth_rate > -0.1:
                return 'Stable'
            else:
                return 'Declining'
        
        evolution_analysis['trend_classification'] = evolution_analysis['families_growth'].apply(classify_trend)
        
        return evolution_analysis

class GeographicDataProcessor:
    """
    Data processor for cleaning and preparing geographic patent data.
    """
    
    def __init__(self):
        """Initialize geographic data processor."""
        self.processed_data = None
    
    def process_patstat_geographic_data(self, raw_data: List[Tuple]) -> pd.DataFrame:
        """
        Process raw PATSTAT geographic query results.
        
        Args:
            raw_data: Raw query results from PATSTAT
            
        Returns:
            Processed DataFrame ready for geographic analysis
        """
        logger.debug(f"📊 Processing {len(raw_data)} raw geographic records...")
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data, columns=[
            'docdb_family_id', 'docdb_family_size', 'earliest_filing_year',
            'country_code', 'applicant_name', 'applt_seq_nr'
        ])
        
        # Data cleaning
        df = self._clean_geographic_fields(df)
        df = self._validate_data_quality(df)
        df = self._remove_duplicates(df)
        
        logger.debug(f"✅ Processed to {len(df)} clean geographic records")
        self.processed_data = df
        
        return df
    
    def _clean_geographic_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean geographic-specific fields."""
        logger.debug("🧹 Cleaning geographic fields...")
        
        # Clean country codes
        df['country_code'] = df['country_code'].astype(str).str.upper().str.strip()
        df['country_code'] = df['country_code'].replace(['NAN', 'NONE', 'NULL'], 'UNKNOWN')
        
        # Clean applicant names
        df['applicant_name'] = df['applicant_name'].astype(str).str.strip()
        
        # Ensure numeric fields are proper types
        df['docdb_family_size'] = pd.to_numeric(df['docdb_family_size'], errors='coerce')
        df['earliest_filing_year'] = pd.to_numeric(df['earliest_filing_year'], errors='coerce')
        df['applt_seq_nr'] = pd.to_numeric(df['applt_seq_nr'], errors='coerce')
        
        return df
    
    def _validate_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data quality and remove invalid records."""
        logger.debug("🔍 Validating data quality...")
        
        initial_count = len(df)
        
        # Remove records with invalid years
        current_year = datetime.now().year
        df = df[df['earliest_filing_year'].between(1980, current_year)].copy()
        
        # Remove records with invalid family sizes
        df = df[df['docdb_family_size'] > 0].copy()
        
        # Keep only primary applicants (seq_nr = 1) for cleaner analysis
        df = df[df['applt_seq_nr'] == 1].copy()
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.debug(f"📊 Removed {removed_count} invalid records")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        logger.debug("🔍 Removing duplicates...")
        
        # Remove exact duplicates
        initial_count = len(df)
        df = df.drop_duplicates().copy()
        
        # Remove duplicates based on family_id and country (keep first occurrence)
        df = df.drop_duplicates(subset=['docdb_family_id', 'country_code']).copy()
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.debug(f"📊 Removed {removed_count} duplicate records")
        
        return df

def create_geographic_analyzer(patstat_client: Optional[object] = None) -> GeographicAnalyzer:
    """
    Factory function to create configured geographic analyzer.
    
    Args:
        patstat_client: Optional PATSTAT client for enhanced country mapping
    
    Returns:
        Configured GeographicAnalyzer instance with enhanced geographic intelligence
    """
    return GeographicAnalyzer(patstat_client)

def create_geographic_processor() -> GeographicDataProcessor:
    """
    Factory function to create configured geographic data processor.
    
    Returns:
        Configured GeographicDataProcessor instance
    """
    return GeographicDataProcessor()

