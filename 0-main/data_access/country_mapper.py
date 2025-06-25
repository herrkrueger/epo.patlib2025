"""
Geographic Country Mapper for Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive country mapping using PATSTAT TLS801_COUNTRY table
and Python libraries for strategic patent analysis regional groupings.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Set
from pathlib import Path
import yaml

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports for enhanced mapping
try:
    import pycountry
    import pycountry_convert as pc
    HAS_PYCOUNTRY = True
except ImportError:
    logger.warning("⚠️ pycountry not available. Install with: pip install pycountry pycountry-convert")
    HAS_PYCOUNTRY = False

class PatentCountryMapper:
    """
    Comprehensive country mapper for patent analysis using PATSTAT data and enhanced libraries.
    """
    
    def __init__(self, patstat_client=None, config_path: Optional[str] = None):
        """
        Initialize country mapper with optional PATSTAT integration.
        
        Args:
            patstat_client: Optional PATSTAT client for TLS801_COUNTRY access
            config_path: Path to geographic configuration file
        """
        self.patstat_client = patstat_client
        self.country_cache = {}
        self.regional_groups = {}
        self.config = {}
        
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "geographic_config.yaml"
        
        self._load_config(config_path)
        self._build_mapping()
    
    def _load_config(self, config_path: Path):
        """Load geographic configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.debug(f"✅ Loaded geographic configuration from {config_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load geographic config: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self):
        """Get minimal default configuration if file loading fails."""
        return {
            'regional_groups': {
                'ip5_offices': {'members': ['US', 'EP', 'JP', 'KR', 'CN']},
                'major_economies': {'members': ['US', 'CN', 'JP', 'DE', 'GB', 'FR']}
            },
            'unknown_values': {
                'country_code': 'XX',
                'country_name': 'Unknown',
                'continent': 'Unknown'
            }
        }
    
    def _build_mapping(self):
        """Build comprehensive country mapping from multiple sources."""
        logger.debug("🗺️ Building comprehensive country mapping...")
        
        # First, try to load from PATSTAT TLS801_COUNTRY table
        if self.patstat_client:
            self._load_from_patstat()
        
        # Enhance with pycountry if available
        if HAS_PYCOUNTRY:
            self._enhance_with_pycountry()
        
        # Add strategic regional groupings
        self._add_regional_groupings()
        
        logger.debug(f"✅ Country mapping built with {len(self.country_cache)} countries")
    
    def _load_from_patstat(self):
        """Load country data from PATSTAT TLS801_COUNTRY table."""
        try:
            logger.debug("📊 Loading country data from PATSTAT TLS801_COUNTRY...")
            
            query = self.config.get('patstat_integration', {}).get('query_template', """
                SELECT 
                    CTRY_CODE as country_code,
                    ST3_NAME as country_name,
                    CONTINENT as continent,
                    EU_MEMBER as is_eu_member,
                    EPO_MEMBER as is_epo_member,
                    OECD_MEMBER as is_oecd_member
                FROM TLS801_COUNTRY
                WHERE CTRY_CODE IS NOT NULL
                ORDER BY CTRY_CODE
            """)
            
            # Execute query using PATSTAT client
            if hasattr(self.patstat_client, 'execute_query'):
                result = self.patstat_client.execute_query(query)
            elif hasattr(self.patstat_client, 'db') and hasattr(self.patstat_client.db, 'query'):
                # Use DB session for query (patstat_client.db is the SQLAlchemy session)
                session = self.patstat_client.db
                try:
                    from epo.tipdata.patstat.database.models import TLS801_COUNTRY
                    
                    # Query using ORM
                    orm_result = session.query(
                        TLS801_COUNTRY.ctry_code.label('country_code'),
                        TLS801_COUNTRY.st3_name.label('country_name'),
                        TLS801_COUNTRY.continent,
                        TLS801_COUNTRY.eu_member.label('is_eu_member'),
                        TLS801_COUNTRY.epo_member.label('is_epo_member'),
                        TLS801_COUNTRY.oecd_member.label('is_oecd_member')
                    ).filter(
                        TLS801_COUNTRY.ctry_code.isnot(None)
                    ).order_by(TLS801_COUNTRY.ctry_code)
                    
                    # Convert to DataFrame
                    result = pd.read_sql(orm_result.statement, session.bind)
                    
                except ImportError:
                    # Fallback to raw SQL if ORM models not available
                    result = pd.read_sql(query, session.bind)
            else:
                # Fallback - no compatible query method found
                raise AttributeError("PatstatClient doesn't have a compatible query method")
            
            # Process results
            for _, row in result.iterrows():
                code = row['country_code'].strip() if pd.notna(row['country_code']) else 'XX'
                
                self.country_cache[code] = {
                    'name': row.get('country_name', 'Unknown'),
                    'continent': row.get('continent', 'Unknown'),
                    'is_eu_member': bool(row.get('is_eu_member', False)),
                    'is_epo_member': bool(row.get('is_epo_member', False)),
                    'is_oecd_member': bool(row.get('is_oecd_member', False)),
                    'source': 'PATSTAT_TLS801',
                    'regional_groups': []
                }
            
            logger.debug(f"✅ Loaded {len(self.country_cache)} countries from PATSTAT")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load from PATSTAT: {e}")
            logger.debug("📖 Falling back to pycountry mapping...")
    
    def _enhance_with_pycountry(self):
        """Enhance mapping with pycountry data for missing countries."""
        if not HAS_PYCOUNTRY:
            return
        
        logger.debug("🌍 Enhancing with pycountry data...")
        
        for country in pycountry.countries:
            code = country.alpha_2
            
            # Skip if already loaded from PATSTAT
            if code in self.country_cache:
                # Just add missing fields
                if 'alpha_3' not in self.country_cache[code]:
                    self.country_cache[code]['alpha_3'] = country.alpha_3
                    self.country_cache[code]['numeric'] = country.numeric
                continue
            
            # Get continent
            try:
                continent_code = pc.country_alpha2_to_continent_code(code)
                continent_name = pc.convert_continent_code_to_continent_name(continent_code)
            except:
                continent_name = "Unknown"
            
            # Add new country
            self.country_cache[code] = {
                'name': country.name,
                'official_name': getattr(country, 'official_name', country.name),
                'alpha_3': country.alpha_3,
                'numeric': country.numeric,
                'continent': continent_name,
                'source': 'pycountry',
                'regional_groups': [],
                'is_eu_member': False,
                'is_epo_member': False,
                'is_oecd_member': False
            }
        
        logger.debug(f"✅ Enhanced mapping with pycountry data")
    
    def _add_regional_groupings(self):
        """Add strategic regional groupings for patent analysis."""
        logger.debug("🏛️ Adding strategic regional groupings...")
        
        regional_groups = self.config.get('regional_groups', {})
        
        for group_name, group_config in regional_groups.items():
            members = group_config.get('members', [])
            
            for country_code in members:
                if country_code in self.country_cache:
                    self.country_cache[country_code]['regional_groups'].append(group_name)
        
        # Store group definitions for reference
        self.regional_groups = regional_groups
        
        logger.debug(f"✅ Added {len(regional_groups)} regional groupings")
    
    def get_country_info(self, code: str) -> Dict:
        """
        Get comprehensive country information.
        
        Args:
            code: ISO 2-letter country code
            
        Returns:
            Dictionary with country information
        """
        if not code or pd.isna(code):
            code = self.config.get('unknown_values', {}).get('country_code', 'XX')
        
        code = str(code).strip().upper()
        
        return self.country_cache.get(code, {
            'name': self.config.get('unknown_values', {}).get('country_name', 'Unknown'),
            'continent': self.config.get('unknown_values', {}).get('continent', 'Unknown'),
            'regional_groups': [],
            'source': 'default',
            'is_eu_member': False,
            'is_epo_member': False,
            'is_oecd_member': False
        })
    
    def get_countries_in_group(self, group_name: str) -> List[str]:
        """
        Get list of country codes in a specific regional group.
        
        Args:
            group_name: Name of regional group
            
        Returns:
            List of country codes
        """
        return self.regional_groups.get(group_name, {}).get('members', [])
    
    def get_country_groups(self, code: str) -> List[str]:
        """
        Get all regional groups for a country.
        
        Args:
            code: ISO 2-letter country code
            
        Returns:
            List of group names
        """
        country_info = self.get_country_info(code)
        return country_info.get('regional_groups', [])
    
    def is_in_group(self, code: str, group_name: str) -> bool:
        """
        Check if country is in specific regional group.
        
        Args:
            code: ISO 2-letter country code
            group_name: Name of regional group
            
        Returns:
            True if country is in group
        """
        return group_name in self.get_country_groups(code)
    
    def create_mapping_dataframe(self) -> pd.DataFrame:
        """
        Create comprehensive pandas DataFrame with all country mappings.
        
        Returns:
            DataFrame with country information and regional groupings
        """
        data = []
        
        for code, info in self.country_cache.items():
            row = {
                'country_code': code,
                'country_name': info.get('name', 'Unknown'),
                'continent': info.get('continent', 'Unknown'),
                'alpha_3': info.get('alpha_3', ''),
                'source': info.get('source', 'unknown'),
                'is_eu_member': info.get('is_eu_member', False),
                'is_epo_member': info.get('is_epo_member', False),
                'is_oecd_member': info.get('is_oecd_member', False)
            }
            
            # Add regional group memberships as boolean columns
            for group_name in self.regional_groups.keys():
                row[f'is_{group_name}'] = group_name in info.get('regional_groups', [])
            
            # Add comma-separated list of all groups
            row['regional_groups'] = ','.join(info.get('regional_groups', []))
            
            data.append(row)
        
        df = pd.DataFrame(data).sort_values('country_code')
        logger.debug(f"📊 Created mapping DataFrame with {len(df)} countries and {len(df.columns)} columns")
        
        return df
    
    def enhance_patent_data(self, patent_df: pd.DataFrame, 
                          country_col: str = 'country_code') -> pd.DataFrame:
        """
        Enhance patent DataFrame with comprehensive geographic information.
        
        Args:
            patent_df: DataFrame with patent data
            country_col: Column name containing country codes
            
        Returns:
            Enhanced DataFrame with geographic information
        """
        logger.debug(f"🔧 Enhancing patent data with geographic information...")
        
        enhanced_data = []
        
        for _, row in patent_df.iterrows():
            country_code = row.get(country_col, 'XX')
            geo_info = self.get_country_info(country_code)
            
            enhanced_data.append({
                'country_name': geo_info['name'],
                'continent': geo_info['continent'],
                'is_ip5_office': self.is_in_group(country_code, 'ip5_offices'),
                'is_epo_member': geo_info.get('is_epo_member', False),
                'is_eu_member': geo_info.get('is_eu_member', False),
                'is_major_economy': self.is_in_group(country_code, 'major_economies'),
                'is_emerging_market': self.is_in_group(country_code, 'emerging_markets'),
                'regional_groups_count': len(geo_info.get('regional_groups', [])),
                'data_source': geo_info.get('source', 'unknown')
            })
        
        enhanced_df = pd.DataFrame(enhanced_data)
        result = pd.concat([patent_df, enhanced_df], axis=1)
        
        logger.debug(f"✅ Enhanced {len(result)} patent records with geographic data")
        return result
    
    def get_regional_summary(self) -> Dict:
        """
        Get summary of all regional groupings and their members.
        
        Returns:
            Dictionary with regional group summaries
        """
        summary = {}
        
        for group_name, group_config in self.regional_groups.items():
            members = group_config.get('members', [])
            
            summary[group_name] = {
                'name': group_config.get('name', group_name),
                'description': group_config.get('description', ''),
                'member_count': len(members),
                'members': members
            }
        
        return summary

# Factory function for easy instantiation
def create_country_mapper(patstat_client=None, config_path: Optional[str] = None) -> PatentCountryMapper:
    """
    Create configured country mapper instance.
    
    Args:
        patstat_client: Optional PATSTAT client for database access
        config_path: Optional path to configuration file
        
    Returns:
        Configured PatentCountryMapper instance
    """
    return PatentCountryMapper(patstat_client, config_path)

# Quick mapping function for simple use cases
def get_enhanced_country_mapping() -> pd.DataFrame:
    """
    Get enhanced country mapping DataFrame without PATSTAT client.
    
    Returns:
        DataFrame with comprehensive country mappings
    """
    mapper = create_country_mapper()
    return mapper.create_mapping_dataframe()