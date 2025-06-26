"""
Cache Manager for Patent Analysis Data
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides intelligent caching for PATSTAT queries and EPO OPS API calls
to improve performance and reduce API usage during development and demos.
"""

import os
import json
import pickle
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatentDataCache:
    """
    Intelligent cache manager for patent analysis data with automatic expiration
    and data integrity checks.
    """
    
    def __init__(self, cache_dir: str = "./cache", default_ttl: int = 3600):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds (1 hour default)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        
        # Create subdirectories for different data types
        self.patstat_cache_dir = self.cache_dir / "patstat"
        self.ops_cache_dir = self.cache_dir / "epo_ops"
        self.analysis_cache_dir = self.cache_dir / "analysis"
        
        for cache_subdir in [self.patstat_cache_dir, self.ops_cache_dir, self.analysis_cache_dir]:
            cache_subdir.mkdir(exist_ok=True)
        
        logger.debug(f"✅ Cache manager initialized: {self.cache_dir}")
    
    def _generate_cache_key(self, data: Union[str, Dict, List]) -> str:
        """
        Generate a unique cache key from input data.
        
        Args:
            data: Input data to generate key from
            
        Returns:
            SHA256 hash as cache key
        """
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True)
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_type: str, cache_key: str) -> Path:
        """
        Get full path for cache file.
        
        Args:
            cache_type: Type of cache ('patstat', 'epo_ops', 'analysis')
            cache_key: Unique cache key
            
        Returns:
            Path to cache file
        """
        cache_subdir = {
            'patstat': self.patstat_cache_dir,
            'epo_ops': self.ops_cache_dir,
            'analysis': self.analysis_cache_dir
        }.get(cache_type, self.cache_dir)
        
        return cache_subdir / f"{cache_key}.pkl"
    
    def _is_cache_valid(self, cache_path: Path, ttl: int) -> bool:
        """
        Check if cache file is still valid based on TTL.
        
        Args:
            cache_path: Path to cache file
            ttl: Time-to-live in seconds
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False
        
        file_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        return file_age < ttl
    
    def get(self, cache_type: str, cache_key_data: Union[str, Dict, List], 
            ttl: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve data from cache if available and valid.
        
        Args:
            cache_type: Type of cache ('patstat', 'epo_ops', 'analysis')
            cache_key_data: Data to generate cache key from
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            Cached data or None if not available/expired
        """
        cache_key = self._generate_cache_key(cache_key_data)
        cache_path = self._get_cache_path(cache_type, cache_key)
        ttl = ttl or self.default_ttl
        
        if self._is_cache_valid(cache_path, ttl):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                
                logger.debug(f"📦 Cache hit: {cache_type}/{cache_key[:8]}...")
                return cached_data
                
            except Exception as e:
                logger.warning(f"⚠️ Cache read error: {e}")
                # Remove corrupted cache file
                cache_path.unlink(missing_ok=True)
        
        logger.debug(f"📭 Cache miss: {cache_type}/{cache_key[:8]}...")
        return None
    
    def set(self, cache_type: str, cache_key_data: Union[str, Dict, List], 
            data: Any, metadata: Optional[Dict] = None) -> bool:
        """
        Store data in cache with metadata.
        
        Args:
            cache_type: Type of cache ('patstat', 'epo_ops', 'analysis')
            cache_key_data: Data to generate cache key from
            data: Data to cache
            metadata: Optional metadata to store with data
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(cache_key_data)
            cache_path = self._get_cache_path(cache_type, cache_key)
            
            cache_entry = {
                'data': data,
                'metadata': metadata or {},
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_entry, f)
            
            logger.debug(f"💾 Cached: {cache_type}/{cache_key[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache write error: {e}")
            return False
    
    def invalidate(self, cache_type: str, cache_key_data: Union[str, Dict, List]) -> bool:
        """
        Invalidate specific cache entry.
        
        Args:
            cache_type: Type of cache
            cache_key_data: Data to generate cache key from
            
        Returns:
            True if invalidated, False if not found
        """
        cache_key = self._generate_cache_key(cache_key_data)
        cache_path = self._get_cache_path(cache_type, cache_key)
        
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"🗑️ Invalidated cache: {cache_type}/{cache_key[:8]}...")
            return True
        
        return False
    
    def clear_cache(self, cache_type: Optional[str] = None, older_than: Optional[int] = None):
        """
        Clear cache entries.
        
        Args:
            cache_type: Specific cache type to clear (clears all if None)
            older_than: Only clear entries older than this many seconds
        """
        if cache_type:
            cache_dirs = [getattr(self, f"{cache_type}_cache_dir")]
        else:
            cache_dirs = [self.patstat_cache_dir, self.ops_cache_dir, self.analysis_cache_dir]
        
        cleared_count = 0
        current_time = datetime.now().timestamp()
        
        for cache_dir in cache_dirs:
            for cache_file in cache_dir.glob("*.pkl"):
                if older_than:
                    file_age = current_time - cache_file.stat().st_mtime
                    if file_age < older_than:
                        continue
                
                cache_file.unlink()
                cleared_count += 1
        
        logger.debug(f"🧹 Cleared {cleared_count} cache entries")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics and health information.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'cache_dir': str(self.cache_dir),
            'total_size_mb': 0,
            'cache_types': {}
        }
        
        for cache_type, cache_dir in [
            ('patstat', self.patstat_cache_dir),
            ('epo_ops', self.ops_cache_dir),
            ('analysis', self.analysis_cache_dir)
        ]:
            cache_files = list(cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            stats['cache_types'][cache_type] = {
                'file_count': len(cache_files),
                'size_mb': total_size / (1024 * 1024),
                'oldest_file': None,
                'newest_file': None
            }
            
            if cache_files:
                file_times = [f.stat().st_mtime for f in cache_files]
                stats['cache_types'][cache_type]['oldest_file'] = datetime.fromtimestamp(min(file_times)).isoformat()
                stats['cache_types'][cache_type]['newest_file'] = datetime.fromtimestamp(max(file_times)).isoformat()
            
            stats['total_size_mb'] += stats['cache_types'][cache_type]['size_mb']
        
        return stats

class PatstatQueryCache:
    """
    Specialized cache for PATSTAT queries with query optimization.
    """
    
    def __init__(self, cache_manager: PatentDataCache):
        """
        Initialize PATSTAT query cache.
        
        Args:
            cache_manager: Parent cache manager instance
        """
        self.cache_manager = cache_manager
        self.cache_type = 'patstat'
        
        # Default TTL for different query types
        self.query_ttls = {
            'search': 3600,      # 1 hour for search results
            'details': 86400,    # 24 hours for patent details
            'citations': 43200,  # 12 hours for citation data
            'families': 86400    # 24 hours for family data
        }
    
    def cache_search_results(self, search_params: Dict, results: pd.DataFrame) -> bool:
        """
        Cache PATSTAT search results.
        
        Args:
            search_params: Search parameters used for the query
            results: Search results DataFrame
            
        Returns:
            True if successfully cached
        """
        cache_key_data = {
            'query_type': 'search',
            'params': search_params,
            'timestamp': datetime.now().date().isoformat()  # Cache per day
        }
        
        metadata = {
            'query_type': 'search',
            'result_count': len(results),
            'unique_families': results['docdb_family_id'].nunique() if 'docdb_family_id' in results.columns else 0,
            'search_params': search_params
        }
        
        return self.cache_manager.set(
            self.cache_type, 
            cache_key_data, 
            results, 
            metadata
        )
    
    def get_cached_search_results(self, search_params: Dict) -> Optional[pd.DataFrame]:
        """
        Retrieve cached PATSTAT search results.
        
        Args:
            search_params: Search parameters
            
        Returns:
            Cached DataFrame or None
        """
        cache_key_data = {
            'query_type': 'search',
            'params': search_params,
            'timestamp': datetime.now().date().isoformat()
        }
        
        cached_entry = self.cache_manager.get(
            self.cache_type, 
            cache_key_data, 
            ttl=self.query_ttls['search']
        )
        
        if cached_entry and 'data' in cached_entry:
            return cached_entry['data']
        
        return None

class EPSOPSCache:
    """
    Specialized cache for EPO OPS API calls with rate limiting awareness.
    """
    
    def __init__(self, cache_manager: PatentDataCache):
        """
        Initialize EPO OPS cache.
        
        Args:
            cache_manager: Parent cache manager instance
        """
        self.cache_manager = cache_manager
        self.cache_type = 'epo_ops'
        
        # EPO OPS data has longer TTL since it's more stable
        self.api_ttls = {
            'patent_details': 604800,  # 1 week
            'patent_family': 604800,   # 1 week
            'citations': 86400,        # 1 day
            'search_results': 3600     # 1 hour
        }
    
    def cache_patent_details(self, patent_number: str, details: Dict) -> bool:
        """
        Cache patent details from EPO OPS.
        
        Args:
            patent_number: Patent number
            details: Patent details from API
            
        Returns:
            True if successfully cached
        """
        cache_key_data = {
            'api_type': 'patent_details',
            'patent_number': patent_number
        }
        
        metadata = {
            'patent_number': patent_number,
            'cached_sections': list(details.keys()) if isinstance(details, dict) else [],
            'api_type': 'patent_details'
        }
        
        return self.cache_manager.set(
            self.cache_type,
            cache_key_data,
            details,
            metadata
        )
    
    def get_cached_patent_details(self, patent_number: str) -> Optional[Dict]:
        """
        Retrieve cached patent details.
        
        Args:
            patent_number: Patent number
            
        Returns:
            Cached patent details or None
        """
        cache_key_data = {
            'api_type': 'patent_details',
            'patent_number': patent_number
        }
        
        cached_entry = self.cache_manager.get(
            self.cache_type,
            cache_key_data,
            ttl=self.api_ttls['patent_details']
        )
        
        if cached_entry and 'data' in cached_entry:
            return cached_entry['data']
        
        return None

class AnalysisCache:
    """
    Cache for processed analysis results and visualizations.
    """
    
    def __init__(self, cache_manager: PatentDataCache):
        """
        Initialize analysis cache.
        
        Args:
            cache_manager: Parent cache manager instance
        """
        self.cache_manager = cache_manager
        self.cache_type = 'analysis'
        
        # Analysis results can be cached longer
        self.analysis_ttls = {
            'geographic_analysis': 7200,    # 2 hours
            'technology_analysis': 7200,    # 2 hours
            'trend_analysis': 3600,         # 1 hour
            'visualization_data': 1800      # 30 minutes
        }
    
    def cache_analysis_result(self, analysis_type: str, params: Dict, 
                            result: Any, visualization_data: Optional[Dict] = None) -> bool:
        """
        Cache analysis results.
        
        Args:
            analysis_type: Type of analysis performed
            params: Analysis parameters
            result: Analysis result
            visualization_data: Optional visualization data
            
        Returns:
            True if successfully cached
        """
        cache_key_data = {
            'analysis_type': analysis_type,
            'params': params
        }
        
        cache_data = {
            'result': result,
            'visualization_data': visualization_data
        }
        
        metadata = {
            'analysis_type': analysis_type,
            'params': params,
            'has_visualization': visualization_data is not None
        }
        
        return self.cache_manager.set(
            self.cache_type,
            cache_key_data,
            cache_data,
            metadata
        )
    
    def get_cached_analysis(self, analysis_type: str, params: Dict) -> Optional[Dict]:
        """
        Retrieve cached analysis results.
        
        Args:
            analysis_type: Type of analysis
            params: Analysis parameters
            
        Returns:
            Cached analysis data or None
        """
        cache_key_data = {
            'analysis_type': analysis_type,
            'params': params
        }
        
        cached_entry = self.cache_manager.get(
            self.cache_type,
            cache_key_data,
            ttl=self.analysis_ttls.get(analysis_type, 3600)
        )
        
        if cached_entry and 'data' in cached_entry:
            return cached_entry['data']
        
        return None

def create_cache_manager(cache_dir: str = "./cache") -> PatentDataCache:
    """
    Factory function to create a configured cache manager.
    
    Args:
        cache_dir: Directory for cache storage
        
    Returns:
        Configured PatentDataCache instance
    """
    return PatentDataCache(cache_dir)

def create_specialized_caches(cache_manager: PatentDataCache) -> Dict[str, Any]:
    """
    Create specialized cache instances.
    
    Args:
        cache_manager: Main cache manager
        
    Returns:
        Dictionary with specialized cache instances
    """
    return {
        'patstat': PatstatQueryCache(cache_manager),
        'epo_ops': EPSOPSCache(cache_manager),
        'analysis': AnalysisCache(cache_manager)
    }

