"""
NUTS Geographic Mapper for Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive NUTS (Nomenclature of Territorial Units for Statistics)
mapping using PATSTAT TLS904_NUTS and TLS206_PERSON tables for hierarchical geographic 
patent analysis across EU regions.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Set, Tuple
from pathlib import Path
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NUTSMapper:
    """
    Comprehensive NUTS mapper for hierarchical geographic patent analysis using PATSTAT data.
    
    Handles EU's 5-level hierarchical coding system:
    - Level 0: Country (DE)
    - Level 1: Major regions (DE1) 
    - Level 2: Basic regions (DE11)
    - Level 3: Small regions (DE111)
    - Level 4: OECD enhanced data
    - Level 9: No NUTS code assigned
    """
    
    def __init__(self, patstat_client=None, local_csv_path: Optional[str] = None):
        """
        Initialize NUTS mapper with PATSTAT integration and local fallback.
        
        Args:
            patstat_client: Optional PATSTAT client for TLS904_NUTS access
            local_csv_path: Path to local NUTS mapping CSV file
        """
        self.patstat_client = patstat_client
        self.nuts_cache = {}
        self.hierarchy_cache = {}
        self.country_regions_cache = {}
        
        # Set local CSV path
        if local_csv_path is None:
            local_csv_path = Path(__file__).parent / "mappings" / "nuts_mapping.csv"
        self.local_csv_path = local_csv_path
        
        self._build_nuts_mapping()
    
    def _build_nuts_mapping(self):
        """Build comprehensive NUTS mapping from PATSTAT and local sources."""
        logger.debug("🗺️ Building NUTS geographic mapping...")
        
        # First, try to load from PATSTAT TLS904_NUTS
        if self.patstat_client:
            self._load_from_patstat()
        
        # Enhance/fallback with local CSV data
        self._load_from_local_csv()
        
        # Build hierarchy and country caches
        self._build_hierarchy_cache()
        self._build_country_cache()
        
        logger.debug(f"✅ NUTS mapping built with {len(self.nuts_cache)} regions")
    
    def _load_from_patstat(self):
        """Load NUTS data from PATSTAT TLS904_NUTS table."""
        try:
            logger.debug("📊 Loading NUTS data from PATSTAT TLS904_NUTS...")
            
            query = """
                SELECT 
                    NUTS as nuts_code,
                    NUTS_LEVEL as nuts_level,
                    NUTS_LABEL as nuts_label
                FROM TLS904_NUTS
                WHERE NUTS IS NOT NULL
                ORDER BY NUTS, NUTS_LEVEL
            """
            
            # Execute query using PATSTAT client
            if hasattr(self.patstat_client, 'execute_query'):
                result = self.patstat_client.execute_query(query)
            elif hasattr(self.patstat_client, 'db') and hasattr(self.patstat_client.db, 'query'):
                # Use DB session for query
                session = self.patstat_client.db
                try:
                    from epo.tipdata.patstat.database.models import TLS904_NUTS
                    
                    # Query using ORM
                    orm_result = session.query(
                        TLS904_NUTS.nuts.label('nuts_code'),
                        TLS904_NUTS.nuts_level.label('nuts_level'),
                        TLS904_NUTS.nuts_label.label('nuts_label')
                    ).filter(
                        TLS904_NUTS.nuts.isnot(None)
                    ).order_by(TLS904_NUTS.nuts, TLS904_NUTS.nuts_level)
                    
                    # Convert to DataFrame
                    result = pd.read_sql(orm_result.statement, session.bind)
                    
                except ImportError:
                    # Fallback to raw SQL if ORM models not available
                    result = pd.read_sql(query, session.bind)
            else:
                raise AttributeError("PatstatClient doesn't have a compatible query method")
            
            # Process results
            for _, row in result.iterrows():
                nuts_code = str(row['nuts_code']).strip()
                nuts_level = int(row['nuts_level']) if pd.notna(row['nuts_level']) else 9
                nuts_label = str(row['nuts_label']).strip() if pd.notna(row['nuts_label']) else 'Unknown'
                
                self.nuts_cache[nuts_code] = {
                    'nuts_code': nuts_code,
                    'nuts_level': nuts_level,
                    'nuts_label': nuts_label,
                    'source': 'PATSTAT_TLS904'
                }
            
            logger.debug(f"✅ Loaded {len(self.nuts_cache)} NUTS regions from PATSTAT")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load from PATSTAT: {e}")
            logger.debug("📖 Falling back to local CSV mapping...")
    
    def _load_from_local_csv(self):
        """Load NUTS data from local CSV file."""
        try:
            logger.debug(f"📁 Loading NUTS data from local CSV: {self.local_csv_path}")
            
            if not Path(self.local_csv_path).exists():
                logger.warning(f"⚠️ Local CSV file not found: {self.local_csv_path}")
                return
            
            # Read CSV with UTF-8 encoding to handle special characters
            df = pd.read_csv(self.local_csv_path, encoding='utf-8-sig')
            
            # Expected columns: NUTS_ID, LEVEL, NAME_LATIN
            required_cols = ['NUTS_ID', 'LEVEL', 'NAME_LATIN']
            if not all(col in df.columns for col in required_cols):
                logger.warning(f"⚠️ Local CSV missing required columns: {required_cols}")
                return
            
            # Process CSV data
            added_count = 0
            for _, row in df.iterrows():
                nuts_code = str(row['NUTS_ID']).strip()
                nuts_level = int(row['LEVEL']) if pd.notna(row['LEVEL']) else 9
                nuts_label = str(row['NAME_LATIN']).strip() if pd.notna(row['NAME_LATIN']) else 'Unknown'
                
                # Skip if already loaded from PATSTAT (PATSTAT takes priority)
                if nuts_code in self.nuts_cache and self.nuts_cache[nuts_code]['source'] == 'PATSTAT_TLS904':
                    continue
                
                self.nuts_cache[nuts_code] = {
                    'nuts_code': nuts_code,
                    'nuts_level': nuts_level,
                    'nuts_label': nuts_label,
                    'source': 'local_csv'
                }
                added_count += 1
            
            logger.debug(f"✅ Added {added_count} NUTS regions from local CSV")
            
        except Exception as e:
            logger.error(f"❌ Failed to load from local CSV: {e}")
    
    def _build_hierarchy_cache(self):
        """Build hierarchy relationships for efficient navigation."""
        logger.debug("🏗️ Building NUTS hierarchy cache...")
        
        for nuts_code in self.nuts_cache.keys():
            hierarchy = self._extract_hierarchy(nuts_code)
            self.hierarchy_cache[nuts_code] = hierarchy
        
        logger.debug(f"✅ Built hierarchy cache for {len(self.hierarchy_cache)} regions")
    
    def _build_country_cache(self):
        """Build country-to-regions mapping for efficient lookups."""
        logger.debug("🌍 Building country regions cache...")
        
        for nuts_code, nuts_info in self.nuts_cache.items():
            country_code = self._extract_country_code(nuts_code)
            nuts_level = nuts_info['nuts_level']
            
            if country_code not in self.country_regions_cache:
                self.country_regions_cache[country_code] = {}
            
            if nuts_level not in self.country_regions_cache[country_code]:
                self.country_regions_cache[country_code][nuts_level] = []
            
            self.country_regions_cache[country_code][nuts_level].append(nuts_code)
        
        logger.debug(f"✅ Built country cache for {len(self.country_regions_cache)} countries")
    
    def _extract_hierarchy(self, nuts_code: str) -> List[str]:
        """
        Extract NUTS hierarchy from code.
        
        Args:
            nuts_code: NUTS code (e.g., "DE111")
            
        Returns:
            List of codes from country to specific region ["DE", "DE1", "DE11", "DE111"]
        """
        if not nuts_code or len(nuts_code) < 2:
            return []
        
        hierarchy = []
        
        # Country level (first 2 characters)
        country = nuts_code[:2]
        hierarchy.append(country)
        
        # Add intermediate levels
        for i in range(3, min(len(nuts_code) + 1, 6)):  # Max 5 characters for NUTS
            level_code = nuts_code[:i]
            hierarchy.append(level_code)
        
        return hierarchy
    
    def _extract_country_code(self, nuts_code: str) -> str:
        """Extract country code from NUTS code."""
        if not nuts_code or len(nuts_code) < 2:
            return 'XX'
        return nuts_code[:2].upper()
    
    def _validate_nuts_format(self, nuts_code: str) -> bool:
        """Validate NUTS code format (2-5 ASCII characters)."""
        if not nuts_code:
            return False
        
        # NUTS codes are 2-5 ASCII characters, alphanumeric
        pattern = r'^[A-Z]{2}[A-Z0-9]{0,3}$'
        return bool(re.match(pattern, nuts_code.upper()))
    
    def get_nuts_info(self, nuts_code: str) -> Dict:
        """
        Get comprehensive NUTS information.
        
        Args:
            nuts_code: NUTS code to look up
            
        Returns:
            Dictionary with NUTS information
        """
        if not nuts_code or pd.isna(nuts_code):
            return {
                'nuts_code': 'UNKNOWN',
                'nuts_level': 9,
                'nuts_label': 'Unknown Region',
                'country_code': 'XX',
                'is_valid': False,
                'source': 'default'
            }
        
        nuts_code = str(nuts_code).strip().upper()
        
        # Check cache first
        if nuts_code in self.nuts_cache:
            info = self.nuts_cache[nuts_code].copy()
            info['country_code'] = self._extract_country_code(nuts_code)
            info['is_valid'] = True
            return info
        
        # If not found, return basic info with validation
        return {
            'nuts_code': nuts_code,
            'nuts_level': 9,  # Unknown level
            'nuts_label': 'Unknown Region',
            'country_code': self._extract_country_code(nuts_code),
            'is_valid': self._validate_nuts_format(nuts_code),
            'source': 'inferred'
        }
    
    def get_nuts_hierarchy(self, nuts_code: str) -> List[str]:
        """
        Get NUTS hierarchy from country to specific region.
        
        Args:
            nuts_code: NUTS code (e.g., "DE111")
            
        Returns:
            List of NUTS codes in hierarchy ["DE", "DE1", "DE11", "DE111"]
        """
        if not nuts_code:
            return []
        
        nuts_code = str(nuts_code).strip().upper()
        
        # Use cached hierarchy if available
        if nuts_code in self.hierarchy_cache:
            return self.hierarchy_cache[nuts_code]
        
        # Generate hierarchy on-the-fly
        return self._extract_hierarchy(nuts_code)
    
    def get_nuts_name(self, nuts_code: str) -> str:
        """
        Get official NUTS region name.
        
        Args:
            nuts_code: NUTS code
            
        Returns:
            Official region name or 'Unknown Region'
        """
        info = self.get_nuts_info(nuts_code)
        return info.get('nuts_label', 'Unknown Region')
    
    def nuts_to_country(self, nuts_code: str) -> str:
        """
        Extract country code from NUTS code.
        
        Args:
            nuts_code: NUTS code
            
        Returns:
            2-letter country code
        """
        return self._extract_country_code(nuts_code)
    
    def get_country_regions(self, country_code: str, nuts_level: int = 3) -> List[str]:
        """
        Get all NUTS regions within country at specified level.
        
        Args:
            country_code: 2-letter country code
            nuts_level: NUTS level (0-4, 9)
            
        Returns:
            List of NUTS codes at specified level
        """
        country_code = str(country_code).strip().upper()
        
        if country_code in self.country_regions_cache:
            return self.country_regions_cache[country_code].get(nuts_level, [])
        
        # Fallback: filter all regions
        regions = []
        for nuts_code, info in self.nuts_cache.items():
            if (self._extract_country_code(nuts_code) == country_code and 
                info['nuts_level'] == nuts_level):
                regions.append(nuts_code)
        
        return sorted(regions)
    
    def validate_nuts_code(self, nuts_code: str) -> bool:
        """
        Check if NUTS code exists in mapping.
        
        Args:
            nuts_code: NUTS code to validate
            
        Returns:
            True if code exists and is valid
        """
        if not nuts_code:
            return False
        
        nuts_code = str(nuts_code).strip().upper()
        return nuts_code in self.nuts_cache
    
    def get_parent_region(self, nuts_code: str) -> Optional[str]:
        """
        Get parent region in NUTS hierarchy.
        
        Args:
            nuts_code: NUTS code
            
        Returns:
            Parent NUTS code or None if at country level
        """
        if not nuts_code or len(nuts_code) <= 2:
            return None
        
        # Parent is the code with one less character
        parent_code = nuts_code[:-1]
        
        # Validate parent exists
        if self.validate_nuts_code(parent_code):
            return parent_code
        
        # If exact parent doesn't exist, try the hierarchy
        hierarchy = self.get_nuts_hierarchy(nuts_code)
        if len(hierarchy) > 1:
            return hierarchy[-2]  # Second to last in hierarchy
        
        return None
    
    def get_child_regions(self, nuts_code: str) -> List[str]:
        """
        Get child regions in NUTS hierarchy.
        
        Args:
            nuts_code: Parent NUTS code
            
        Returns:
            List of child NUTS codes
        """
        if not nuts_code:
            return []
        
        nuts_code = str(nuts_code).strip().upper()
        children = []
        
        # Find all codes that start with this code and are one level deeper
        target_level = len(nuts_code) + 1
        
        for code in self.nuts_cache.keys():
            if (code.startswith(nuts_code) and 
                len(code) == target_level and 
                code != nuts_code):
                children.append(code)
        
        return sorted(children)
    
    def aggregate_by_nuts_level(self, patent_df: pd.DataFrame, 
                               nuts_col: str = 'nuts_code', 
                               target_level: int = 2) -> pd.DataFrame:
        """
        Aggregate patent data by NUTS level.
        
        Args:
            patent_df: DataFrame with patent data
            nuts_col: Column containing NUTS codes
            target_level: Target NUTS level for aggregation
            
        Returns:
            Aggregated DataFrame by NUTS regions
        """
        logger.debug(f"📊 Aggregating patent data by NUTS level {target_level}...")
        
        # Create mapping to target level
        level_mapping = {}
        
        for _, row in patent_df.iterrows():
            original_nuts = row.get(nuts_col, '')
            if not original_nuts:
                continue
            
            # Get hierarchy and find appropriate level
            hierarchy = self.get_nuts_hierarchy(original_nuts)
            
            # Find the code at target level
            target_nuts = None
            for nuts_code in hierarchy:
                nuts_info = self.get_nuts_info(nuts_code)
                if nuts_info['nuts_level'] == target_level:
                    target_nuts = nuts_code
                    break
            
            # If no exact level match, use closest available
            if not target_nuts and hierarchy:
                # Use the deepest available level that's <= target_level
                for nuts_code in reversed(hierarchy):
                    nuts_info = self.get_nuts_info(nuts_code)
                    if nuts_info['nuts_level'] <= target_level:
                        target_nuts = nuts_code
                        break
            
            if target_nuts:
                level_mapping[original_nuts] = target_nuts
        
        # Add target NUTS column
        patent_df_copy = patent_df.copy()
        patent_df_copy[f'nuts_level_{target_level}'] = patent_df_copy[nuts_col].map(level_mapping)
        
        # Aggregate by target NUTS level
        agg_columns = [col for col in patent_df_copy.columns 
                      if col not in [nuts_col, f'nuts_level_{target_level}']]
        
        # Define aggregation rules
        agg_rules = {}
        for col in agg_columns:
            if patent_df_copy[col].dtype in ['int64', 'float64']:
                agg_rules[col] = 'sum'
            else:
                agg_rules[col] = 'count'
        
        # Perform aggregation
        result = patent_df_copy.groupby(f'nuts_level_{target_level}').agg(agg_rules).reset_index()
        
        # Add NUTS metadata
        result['nuts_level'] = target_level
        result['nuts_name'] = result[f'nuts_level_{target_level}'].apply(self.get_nuts_name)
        result['country_code'] = result[f'nuts_level_{target_level}'].apply(self.nuts_to_country)
        
        logger.debug(f"✅ Aggregated to {len(result)} NUTS level {target_level} regions")
        return result
    
    def enhance_patent_data(self, patent_df: pd.DataFrame, 
                          nuts_col: str = 'nuts_code') -> pd.DataFrame:
        """
        Enhance patent DataFrame with comprehensive NUTS information.
        
        Args:
            patent_df: DataFrame with patent data
            nuts_col: Column name containing NUTS codes
            
        Returns:
            Enhanced DataFrame with NUTS metadata
        """
        logger.debug(f"🔧 Enhancing patent data with NUTS information...")
        
        enhanced_data = []
        
        for _, row in patent_df.iterrows():
            nuts_code = row.get(nuts_col, '')
            nuts_info = self.get_nuts_info(nuts_code)
            hierarchy = self.get_nuts_hierarchy(nuts_code)
            
            enhanced_data.append({
                'nuts_label': nuts_info['nuts_label'],
                'nuts_level': nuts_info['nuts_level'],
                'country_code': nuts_info['country_code'],
                'is_valid_nuts': nuts_info['is_valid'],
                'nuts_source': nuts_info['source'],
                'hierarchy_depth': len(hierarchy),
                'parent_region': self.get_parent_region(nuts_code),
                'is_missing_nuts': nuts_info['nuts_level'] == 9
            })
        
        enhanced_df = pd.DataFrame(enhanced_data)
        result = pd.concat([patent_df, enhanced_df], axis=1)
        
        logger.debug(f"✅ Enhanced {len(result)} patent records with NUTS data")
        return result
    
    def get_nuts_summary(self) -> Dict:
        """
        Get comprehensive summary of NUTS mapping.
        
        Returns:
            Dictionary with mapping statistics
        """
        summary = {
            'total_regions': len(self.nuts_cache),
            'countries': len(self.country_regions_cache),
            'data_sources': {},
            'level_distribution': {},
            'coverage_stats': {}
        }
        
        # Count by data source
        for nuts_info in self.nuts_cache.values():
            source = nuts_info['source']
            summary['data_sources'][source] = summary['data_sources'].get(source, 0) + 1
        
        # Count by NUTS level
        for nuts_info in self.nuts_cache.values():
            level = nuts_info['nuts_level']
            summary['level_distribution'][level] = summary['level_distribution'].get(level, 0) + 1
        
        # Coverage statistics
        summary['coverage_stats'] = {
            'valid_format_codes': sum(1 for code in self.nuts_cache.keys() 
                                    if self._validate_nuts_format(code)),
            'missing_data_level': summary['level_distribution'].get(9, 0),
            'oecd_enhanced': summary['level_distribution'].get(4, 0)
        }
        
        return summary
    
    def create_nuts_dataframe(self) -> pd.DataFrame:
        """
        Create comprehensive pandas DataFrame with all NUTS mappings.
        
        Returns:
            DataFrame with NUTS information
        """
        data = []
        
        for nuts_code, nuts_info in self.nuts_cache.items():
            hierarchy = self.get_nuts_hierarchy(nuts_code)
            
            row = {
                'nuts_code': nuts_code,
                'nuts_level': nuts_info['nuts_level'],
                'nuts_label': nuts_info['nuts_label'],
                'country_code': self._extract_country_code(nuts_code),
                'source': nuts_info['source'],
                'hierarchy_depth': len(hierarchy),
                'parent_region': self.get_parent_region(nuts_code),
                'child_count': len(self.get_child_regions(nuts_code)),
                'is_valid_format': self._validate_nuts_format(nuts_code),
                'hierarchy_path': ' → '.join(hierarchy)
            }
            
            data.append(row)
        
        df = pd.DataFrame(data).sort_values(['country_code', 'nuts_level', 'nuts_code'])
        logger.debug(f"📊 Created NUTS DataFrame with {len(df)} regions")
        
        return df

# Factory function for easy instantiation
def create_nuts_mapper(patstat_client=None, local_csv_path: Optional[str] = None) -> NUTSMapper:
    """
    Create configured NUTS mapper instance.
    
    Args:
        patstat_client: Optional PATSTAT client for database access
        local_csv_path: Optional path to local CSV file
        
    Returns:
        Configured NUTSMapper instance
    """
    return NUTSMapper(patstat_client, local_csv_path)

# Quick mapping function for simple use cases
def get_enhanced_nuts_mapping() -> pd.DataFrame:
    """
    Get enhanced NUTS mapping DataFrame without PATSTAT client.
    
    Returns:
        DataFrame with comprehensive NUTS mappings
    """
    mapper = create_nuts_mapper()
    return mapper.create_nuts_dataframe()