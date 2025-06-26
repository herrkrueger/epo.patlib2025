"""
Patent Search Processor for Patent Intelligence Platform
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides the foundational patent search capabilities for finding 
patent families using configured keywords and technology areas. It serves as 
the core data source for all downstream enhancement processors.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Set
from datetime import datetime
import logging
import yaml
import os
from pathlib import Path

# Import PATSTAT client and models based on the working notebook patterns
try:
    from epo.tipdata.patstat import PatstatClient
    from epo.tipdata.patstat.database.models import (
        TLS201_APPLN, TLS202_APPLN_TITLE, TLS203_APPLN_ABSTR,
        TLS209_APPLN_IPC, TLS224_APPLN_CPC
    )
    from sqlalchemy import func, and_, or_, distinct
    PATSTAT_AVAILABLE = True
except ImportError:
    PATSTAT_AVAILABLE = False
    logging.warning("PATSTAT integration not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatentSearchProcessor:
    """
    Core patent search processor that finds patent families using keywords and technology areas.
    
    This processor serves as the foundation of the analysis pipeline, implementing the proven
    search patterns from the EPO PATLIB 2025 live demo code.
    """
    
    def __init__(self, patstat_client: Optional[object] = None, config_path: Optional[str] = None):
        """
        Initialize patent search processor.
        
        Args:
            patstat_client: PATSTAT client instance (if None, creates new one)
            config_path: Path to search patterns configuration
        """
        self.patstat_client = patstat_client
        self.session = None
        self.config = self._load_configuration(config_path)
        self.search_results = {}
        self.quality_metrics = {}
        
        # Initialize PATSTAT connection
        if PATSTAT_AVAILABLE and self.patstat_client is None:
            try:
                self.patstat_client = PatstatClient(env='PROD')  # Proven working environment
                logger.debug("✅ Connected to PATSTAT PROD environment")
            except Exception as e:
                logger.error(f"❌ Failed to connect to PATSTAT: {e}")
                self.patstat_client = None
        
        if self.patstat_client:
            try:
                self.session = self.patstat_client.orm()
                logger.debug("✅ PATSTAT session initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize PATSTAT session: {e}")
    
    def _load_configuration(self, config_path: Optional[str] = None) -> Dict:
        """Load search patterns configuration."""
        if config_path is None:
            # Default to config directory relative to this file
            config_dir = Path(__file__).parent.parent / 'config'
            config_path = config_dir / 'search_patterns_config.yaml'
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.debug(f"✅ Loaded search configuration from {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration if file loading fails."""
        return {
            'global_settings': {
                'date_ranges': {
                    'default_start': '2010-01-01',
                    'default_end': '2024-12-31'
                }
            },
            'keywords': {
                'primary': ['rare earth', 'lanthanide'],
                'secondary': ['extraction', 'separation'],
                'focus': ['magnet', 'phosphor']
            },
            'cpc_classifications': {
                'technology_areas': {
                    'rare_earth_elements': {
                        'codes': ['C22B19/28', 'C22B19/30', 'C22B25/06'],
                        'description': 'Rare Earth Elements processing'
                    }
                }
            }
        }
    
    def search_patent_families(self, 
                              keywords: Optional[List[str]] = None,
                              technology_areas: Optional[List[str]] = None,
                              date_range: Optional[Tuple[str, str]] = None,
                              quality_mode: str = 'intersection',
                              max_results: Optional[int] = None) -> pd.DataFrame:
        """
        Search for patent families using configured keywords and technology areas.
        
        Args:
            keywords: List of keywords to search (if None, uses config)
            technology_areas: List of technology area symbols (if None, uses config) 
            date_range: Tuple of (start_date, end_date) in 'YYYY-MM-DD' format
            quality_mode: 'intersection', 'keyword_only', 'classification_only', or 'comprehensive'
            max_results: Maximum number of results to return
            
        Returns:
            DataFrame with patent families and quality scores
        """
        logger.debug("🔍 Starting patent family search...")
        
        if not self.session:
            logger.error("❌ No PATSTAT session available")
            return pd.DataFrame()
        
        # Use configuration defaults if not provided
        if date_range is None:
            start_date = self.config['global_settings']['date_ranges']['default_start']
            end_date = self.config['global_settings']['date_ranges']['default_end']
            date_range = (start_date, end_date)
        
        if keywords is None:
            keywords = self._get_all_configured_keywords()
        
        if technology_areas is None:
            technology_areas = list(self.config['cpc_classifications']['technology_areas'].keys())
        
        logger.debug(f"📊 Search parameters:")
        logger.debug(f"   Keywords: {len(keywords)} terms")
        logger.debug(f"   Technology areas: {technology_areas}")
        logger.debug(f"   Date range: {date_range[0]} to {date_range[1]}")
        logger.debug(f"   Quality mode: {quality_mode}")
        
        # Execute searches based on quality mode
        results = []
        
        if quality_mode in ['intersection', 'comprehensive', 'keyword_only']:
            keyword_families = self._search_by_keywords(keywords, date_range, max_results)
            if not keyword_families.empty:
                results.append(keyword_families)
        
        if quality_mode in ['intersection', 'comprehensive', 'classification_only']:
            classification_families = self._search_by_technology_areas(technology_areas, date_range, max_results)
            if not classification_families.empty:
                results.append(classification_families)
        
        if not results:
            logger.warning("⚠️ No search results found")
            return pd.DataFrame()
        
        # Combine and score results based on quality mode
        combined_results = self._combine_search_results(results, quality_mode)
        
        # Apply result limits
        if max_results and len(combined_results) > max_results:
            combined_results = combined_results.head(max_results)
            logger.debug(f"📊 Limited results to {max_results} families")
        
        # Store results for potential enhancement
        self.search_results = {
            'families': combined_results,
            'search_params': {
                'keywords': keywords,
                'technology_areas': technology_areas, 
                'date_range': date_range,
                'quality_mode': quality_mode
            }
        }
        
        logger.debug(f"✅ Search completed: {len(combined_results)} patent families found")
        
        return combined_results
    
    def _get_all_configured_keywords(self) -> List[str]:
        """Get all keywords from configuration."""
        all_keywords = []
        keyword_config = self.config.get('keywords', {})
        
        for category in ['primary', 'secondary', 'focus']:
            keywords = keyword_config.get(category, [])
            all_keywords.extend(keywords)
        
        return list(set(all_keywords))  # Remove duplicates
    
    def _search_by_keywords(self, keywords: List[str], date_range: Tuple[str, str], max_results: Optional[int]) -> pd.DataFrame:
        """
        Search patent families using keyword matching in titles and abstracts.
        
        Implements the proven pattern from the EPO PATLIB 2025 demo code.
        """
        logger.debug(f"🔍 Searching by keywords: {len(keywords)} terms")
        
        # Build keyword search conditions (case-insensitive)
        keyword_conditions = []
        for keyword in keywords:
            keyword_conditions.extend([
                func.lower(TLS202_APPLN_TITLE.appln_title).contains(keyword.lower()),
                func.lower(TLS203_APPLN_ABSTR.appln_abstract).contains(keyword.lower())
            ])
        
        if not keyword_conditions:
            return pd.DataFrame()
        
        # Execute query using proven pattern from demo notebook
        try:
            query = self.session.query(
                distinct(TLS201_APPLN.docdb_family_id).label('docdb_family_id'),
                func.count(distinct(TLS201_APPLN.appln_id)).label('family_size'),
                func.min(TLS201_APPLN.earliest_filing_year).label('earliest_filing_year'),
                func.max(TLS201_APPLN.earliest_filing_year).label('latest_filing_year')
            ).select_from(TLS201_APPLN)\
            .join(TLS202_APPLN_TITLE, TLS201_APPLN.appln_id == TLS202_APPLN_TITLE.appln_id, isouter=True)\
            .join(TLS203_APPLN_ABSTR, TLS201_APPLN.appln_id == TLS203_APPLN_ABSTR.appln_id, isouter=True)\
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= date_range[0],
                    TLS201_APPLN.appln_filing_date <= date_range[1],
                    TLS201_APPLN.docdb_family_id.isnot(None),
                    or_(*keyword_conditions)
                )
            ).group_by(TLS201_APPLN.docdb_family_id)
            
            if max_results:
                query = query.limit(max_results)
            
            result = query.all()
            
            if result:
                keyword_families = pd.DataFrame(result, columns=[
                    'docdb_family_id', 'family_size', 'earliest_filing_year', 'latest_filing_year'
                ])
                keyword_families['search_method'] = 'keyword'
                keyword_families['match_score'] = 2  # Keyword match
                
                logger.debug(f"✅ Found {len(keyword_families)} families using keyword matching")
                return keyword_families
            else:
                logger.warning("⚠️ No keyword matches found")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Keyword search failed: {e}")
            return pd.DataFrame()
    
    def _search_by_technology_areas(self, technology_areas: List[str], date_range: Tuple[str, str], max_results: Optional[int]) -> pd.DataFrame:
        """
        Search patent families using CPC/IPC classification codes.
        
        Implements the proven pattern from the EPO PATLIB 2025 demo code.
        """
        logger.debug(f"🔍 Searching by technology areas: {technology_areas}")
        
        # Get all CPC codes for the specified technology areas
        all_cpc_codes = []
        tech_config = self.config['cpc_classifications']['technology_areas']
        
        for area in technology_areas:
            if area in tech_config:
                codes = tech_config[area]['codes']
                all_cpc_codes.extend(codes)
        
        if not all_cpc_codes:
            logger.warning("⚠️ No CPC codes found for specified technology areas")
            return pd.DataFrame()
        
        logger.debug(f"   Using {len(all_cpc_codes)} CPC codes")
        
        try:
            # CPC-based search using the proven pattern with exact format matching
            cpc_query = self.session.query(
                distinct(TLS201_APPLN.docdb_family_id).label('docdb_family_id'),
                func.count(distinct(TLS201_APPLN.appln_id)).label('family_size'),
                func.min(TLS201_APPLN.earliest_filing_year).label('earliest_filing_year'),
                func.max(TLS201_APPLN.earliest_filing_year).label('latest_filing_year')
            ).select_from(TLS201_APPLN)\
            .join(TLS224_APPLN_CPC, TLS224_APPLN_CPC.appln_id == TLS201_APPLN.appln_id)\
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= date_range[0],
                    TLS201_APPLN.appln_filing_date <= date_range[1],
                    TLS201_APPLN.docdb_family_id.isnot(None),
                    func.substr(TLS224_APPLN_CPC.cpc_class_symbol, 1, 11).in_(all_cpc_codes)
                )
            ).group_by(TLS201_APPLN.docdb_family_id)
            
            if max_results:
                cpc_query = cpc_query.limit(max_results)
            
            cpc_result = cpc_query.all()
            
            # IPC-based search (subset of CPC codes without Y-codes)
            ipc_codes = [code for code in all_cpc_codes if not code.startswith('Y')]
            
            ipc_families = set()
            if ipc_codes:
                ipc_query = self.session.query(
                    distinct(TLS201_APPLN.docdb_family_id).label('docdb_family_id')
                ).select_from(TLS201_APPLN)\
                .join(TLS209_APPLN_IPC, TLS201_APPLN.appln_id == TLS209_APPLN_IPC.appln_id)\
                .filter(
                    and_(
                        TLS201_APPLN.appln_filing_date >= date_range[0],
                        TLS201_APPLN.appln_filing_date <= date_range[1],
                        TLS201_APPLN.docdb_family_id.isnot(None),
                        func.substr(TLS209_APPLN_IPC.ipc_class_symbol, 1, 11).in_(ipc_codes)
                    )
                )
                
                ipc_result = ipc_query.all()
                ipc_families = set([row[0] for row in ipc_result])
                logger.debug(f"   Found {len(ipc_families)} families using IPC codes")
            
            # Combine CPC and IPC results
            if cpc_result:
                cpc_families_df = pd.DataFrame(cpc_result, columns=[
                    'docdb_family_id', 'family_size', 'earliest_filing_year', 'latest_filing_year'
                ])
                
                # Add IPC matches to the dataset
                cpc_families_df['has_ipc_match'] = cpc_families_df['docdb_family_id'].isin(ipc_families)
                cpc_families_df['search_method'] = 'classification'
                cpc_families_df['match_score'] = 1  # Classification match
                
                logger.debug(f"✅ Found {len(cpc_families_df)} families using CPC codes")
                logger.debug(f"   {cpc_families_df['has_ipc_match'].sum()} also have IPC matches")
                
                return cpc_families_df
            else:
                logger.warning("⚠️ No classification matches found")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Classification search failed: {e}")
            return pd.DataFrame()
    
    def _combine_search_results(self, results: List[pd.DataFrame], quality_mode: str) -> pd.DataFrame:
        """
        Combine search results based on quality mode.
        
        Implements the intersection approach proven in the EPO PATLIB 2025 demo.
        """
        logger.debug(f"🎯 Combining search results using {quality_mode} mode...")
        
        if not results:
            return pd.DataFrame()
        
        if len(results) == 1:
            combined = results[0].copy()
            combined['quality_score'] = combined['match_score'] 
            combined['match_type'] = combined['search_method'] + '_only'
            return combined
        
        # Two search result sets (keywords and classifications)
        keyword_df = None
        classification_df = None
        
        for df in results:
            if 'search_method' in df.columns:
                if df['search_method'].iloc[0] == 'keyword':
                    keyword_df = df
                elif df['search_method'].iloc[0] == 'classification':
                    classification_df = df
        
        combined_families = []
        
        if keyword_df is not None and classification_df is not None:
            # Find intersections and unique sets
            keyword_ids = set(keyword_df['docdb_family_id'])
            classification_ids = set(classification_df['docdb_family_id'])
            
            # High-quality intersection
            intersection_ids = keyword_ids.intersection(classification_ids)
            keyword_only_ids = keyword_ids - classification_ids
            classification_only_ids = classification_ids - keyword_ids
            
            logger.debug(f"   Keyword families: {len(keyword_ids):,}")
            logger.debug(f"   Classification families: {len(classification_ids):,}")
            logger.debug(f"   HIGH-QUALITY intersection: {len(intersection_ids):,}")
            logger.debug(f"   Keyword-only: {len(keyword_only_ids):,}")
            logger.debug(f"   Classification-only: {len(classification_only_ids):,}")
            
            # Create combined dataset based on quality mode
            if quality_mode == 'intersection':
                # Only high-quality intersection
                for family_id in intersection_ids:
                    family_data = self._merge_family_data(family_id, keyword_df, classification_df)
                    family_data.update({
                        'quality_score': 3,
                        'match_type': 'intersection'
                    })
                    combined_families.append(family_data)
            
            elif quality_mode == 'comprehensive':
                # All families with different quality scores
                for family_id in intersection_ids:
                    family_data = self._merge_family_data(family_id, keyword_df, classification_df)
                    family_data.update({
                        'quality_score': 3,
                        'match_type': 'intersection'
                    })
                    combined_families.append(family_data)
                
                for family_id in keyword_only_ids:
                    family_data = keyword_df[keyword_df['docdb_family_id'] == family_id].iloc[0].to_dict()
                    family_data.update({
                        'quality_score': 2,
                        'match_type': 'keyword_only'
                    })
                    combined_families.append(family_data)
                
                for family_id in classification_only_ids:
                    family_data = classification_df[classification_df['docdb_family_id'] == family_id].iloc[0].to_dict()
                    family_data.update({
                        'quality_score': 1,
                        'match_type': 'classification_only'
                    })
                    combined_families.append(family_data)
            
            elif quality_mode == 'keyword_only':
                for family_id in keyword_ids:
                    family_data = keyword_df[keyword_df['docdb_family_id'] == family_id].iloc[0].to_dict()
                    family_data.update({
                        'quality_score': 2 if family_id in intersection_ids else 1,
                        'match_type': 'intersection' if family_id in intersection_ids else 'keyword_only'
                    })
                    combined_families.append(family_data)
            
            elif quality_mode == 'classification_only':
                for family_id in classification_ids:
                    family_data = classification_df[classification_df['docdb_family_id'] == family_id].iloc[0].to_dict()
                    family_data.update({
                        'quality_score': 2 if family_id in intersection_ids else 1,
                        'match_type': 'intersection' if family_id in intersection_ids else 'classification_only'
                    })
                    combined_families.append(family_data)
        
        elif keyword_df is not None:
            # Only keyword results
            for _, row in keyword_df.iterrows():
                family_data = row.to_dict()
                family_data.update({
                    'quality_score': 2,
                    'match_type': 'keyword_only'
                })
                combined_families.append(family_data)
        
        elif classification_df is not None:
            # Only classification results
            for _, row in classification_df.iterrows():
                family_data = row.to_dict()
                family_data.update({
                    'quality_score': 1,
                    'match_type': 'classification_only'
                })
                combined_families.append(family_data)
        
        if combined_families:
            combined_df = pd.DataFrame(combined_families)
            
            # Sort by quality score (highest first) and then by earliest filing year
            combined_df = combined_df.sort_values(
                ['quality_score', 'earliest_filing_year'], 
                ascending=[False, True]
            ).reset_index(drop=True)
            
            # Store quality metrics
            self.quality_metrics = {
                'total_families': len(combined_df),
                'quality_distribution': combined_df['match_type'].value_counts().to_dict(),
                'average_quality_score': combined_df['quality_score'].mean(),
                'high_quality_families': len(combined_df[combined_df['quality_score'] >= 3])
            }
            
            logger.debug(f"✅ Combined {len(combined_df)} families with quality scores")
            return combined_df
        
        return pd.DataFrame()
    
    def _merge_family_data(self, family_id: int, keyword_df: pd.DataFrame, classification_df: pd.DataFrame) -> Dict:
        """Merge data from keyword and classification searches for a family."""
        keyword_data = keyword_df[keyword_df['docdb_family_id'] == family_id]
        classification_data = classification_df[classification_df['docdb_family_id'] == family_id]
        
        merged = {'docdb_family_id': family_id}
        
        if not keyword_data.empty:
            merged.update(keyword_data.iloc[0].to_dict())
        
        if not classification_data.empty:
            classification_row = classification_data.iloc[0].to_dict()
            # Merge non-conflicting fields
            for key, value in classification_row.items():
                if key not in merged or key == 'search_method':
                    merged[key] = value
                elif key == 'family_size':
                    # Use maximum family size
                    merged[key] = max(merged.get(key, 0), value)
        
        merged['search_method'] = 'combined'
        return merged
    
    def get_search_summary(self) -> Dict:
        """
        Get summary of the last search operation.
        
        Returns:
            Dictionary with search metrics and quality information
        """
        if not self.search_results:
            return {'status': 'No search performed yet'}
        
        families = self.search_results['families']
        params = self.search_results['search_params']
        
        summary = {
            'search_summary': {
                'total_families_found': len(families),
                'search_parameters': params,
                'quality_metrics': self.quality_metrics,
                'date_range_coverage': {
                    'earliest_year': int(families['earliest_filing_year'].min()) if not families.empty else None,
                    'latest_year': int(families['latest_filing_year'].max()) if not families.empty else None
                }
            }
        }
        
        if not families.empty:
            summary['top_families'] = families.head(10)[['docdb_family_id', 'quality_score', 'match_type']].to_dict('records')
        
        return summary
    
    def export_search_results(self, filename: Optional[str] = None) -> str:
        """
        Export search results to CSV file.
        
        Args:
            filename: Output filename (if None, generates timestamped name)
            
        Returns:
            Path to exported file
        """
        if not self.search_results or self.search_results['families'].empty:
            raise ValueError("No search results available to export")
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'patent_search_results_{timestamp}.csv'
        
        families = self.search_results['families']
        families.to_csv(filename, index=False)
        
        logger.debug(f"✅ Exported {len(families)} search results to {filename}")
        return filename


def create_patent_search_processor(patstat_client: Optional[object] = None) -> PatentSearchProcessor:
    """
    Factory function to create configured patent search processor.
    
    Args:
        patstat_client: Optional PATSTAT client instance
        
    Returns:
        Configured PatentSearchProcessor instance
    """
    return PatentSearchProcessor(patstat_client=patstat_client)