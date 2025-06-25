"""
PATSTAT Database Client for Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides robust PATSTAT connectivity with proven working patterns
for technology-agnostic patent analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Union
import warnings
import logging
import weakref
import threading
import atexit
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global registry for EPO PatstatClient instances to prevent garbage collection issues
_patstat_client_registry = weakref.WeakSet()

def _safe_close_epo_client(client):
    """Safely close EPO PatstatClient with comprehensive error handling."""
    try:
        if client is None:
            return
            
        # Check if client has close_session method and is callable
        if hasattr(client, 'close_session') and callable(client.close_session):
            # Additional checks to prevent the garbage collection exception
            if hasattr(client, '_session'):
                session = getattr(client, '_session', None)
                if session is not None and hasattr(session, '_connection_record'):
                    # Check if the connection is still active before closing
                    try:
                        connection_record = getattr(session, '_connection_record', None)
                        if connection_record is not None:
                            client.close_session()
                            logger.debug("🔒 EPO PATSTAT client session closed safely")
                        else:
                            logger.debug("🔒 EPO PATSTAT client session already closed")
                    except Exception:
                        logger.debug("🔒 EPO PATSTAT client session already closed (connection check failed)")
                else:
                    logger.debug("🔒 EPO PATSTAT client session already closed")
            else:
                logger.debug("🔒 EPO PATSTAT client session already closed")
        
        # Nullify internal references to prevent garbage collection issues
        for attr in ['_session', 'session', '_engine', 'engine']:
            if hasattr(client, attr):
                setattr(client, attr, None)
        
        # Disable the destructor to prevent garbage collection exceptions
        if hasattr(client, '__del__'):
            client.__del__ = lambda: None
            
    except Exception as e:
        logger.warning(f"⚠️ Safe EPO client close warning: {e}")

def _register_epo_client(client):
    """Register EPO PatstatClient for safe cleanup."""
    if client is not None:
        _patstat_client_registry.add(client)

def _cleanup_all_epo_clients():
    """Clean up all registered EPO PatstatClient instances."""
    clients_to_cleanup = list(_patstat_client_registry)
    for client in clients_to_cleanup:
        _safe_close_epo_client(client)

# Register cleanup function to run at exit
atexit.register(_cleanup_all_epo_clients)

# Monkey-patch EPO PatstatClient to prevent garbage collection exceptions
def _patch_epo_patstat_client():
    """Monkey-patch EPO PatstatClient destructor to prevent exceptions."""
    try:
        from epo.tipdata.patstat import PatstatClient as EPOPatstatClient
        
        # Store original destructor
        original_del = EPOPatstatClient.__del__
        
        def safe_del(self):
            """Safe destructor that prevents garbage collection exceptions."""
            try:
                # Check if the session is still valid before calling original destructor
                if hasattr(self, '_session') and self._session is not None:
                    # Try to check session state before calling original destructor
                    try:
                        if hasattr(self._session, '_connection_record'):
                            connection_record = getattr(self._session, '_connection_record', None)
                            if connection_record is not None:
                                original_del(self)
                            else:
                                # Session is already closed, just clean up
                                self._session = None
                        else:
                            # No connection record, session is invalid
                            self._session = None
                    except Exception:
                        # Any error means session is invalid, just clean up
                        self._session = None
                else:
                    # No session or already None, nothing to clean up
                    pass
            except Exception:
                # Silently ignore all destructor errors during garbage collection
                pass
        
        # Replace destructor
        EPOPatstatClient.__del__ = safe_del
        logger.debug("✅ EPO PatstatClient destructor patched for safe cleanup")
        
    except ImportError:
        # EPO library not available, no patching needed
        pass
    except Exception as e:
        logger.warning(f"⚠️ Could not patch EPO PatstatClient destructor: {e}")

# Apply the patch
_patch_epo_patstat_client()

class PatstatConnectionManager:
    """
    Thread-safe connection manager for PATSTAT with proper lifecycle management
    and garbage collection protection.
    """
    
    def __init__(self, environment: str = 'PROD'):
        """
        Initialize connection manager.
        
        Args:
            environment: 'PROD' (full dataset) or 'TEST' (limited access)
        """
        self.environment = environment
        self.patstat_client = None
        self.db_session = None
        self.models = {}
        self.sql_funcs = {}
        self.is_connected = False
        self.is_closed = False
        self._lock = threading.Lock()
        self._weak_refs = set()
        
        # Initialize connection
        self._establish_connection()
    
    def _establish_connection(self):
        """Establish PATSTAT connection with comprehensive error handling."""
        try:
            # Check if we're in TIP environment
            try:
                from config import get_database_config
            except ImportError:
                # Fallback for relative import
                import sys
                from pathlib import Path
                config_path = Path(__file__).parent.parent / 'config'
                sys.path.insert(0, str(config_path.parent))
                from config import get_database_config
            
            tip_config = get_database_config('patstat.environments.tip_environment', {})
            
            if tip_config.get('enabled', True) and tip_config.get('use_patstat_client_module', True):
                # Use TIP environment PatstatClient module
                from epo.tipdata.patstat import PatstatClient as EPOPatstatClient
                from epo.tipdata.patstat.database.models import (
                    TLS201_APPLN, TLS202_APPLN_TITLE, TLS203_APPLN_ABSTR, 
                    TLS209_APPLN_IPC, TLS224_APPLN_CPC, TLS212_CITATION,
                    TLS228_DOCDB_FAM_CITN, TLS215_CITN_CATEG, TLS214_NPL_PUBLN,
                    TLS211_PAT_PUBLN, TLS227_PERS_PUBLN, TLS207_PERS_APPLN, TLS206_PERSON
                )
                from sqlalchemy import func, and_, or_
                from sqlalchemy.orm import sessionmaker, aliased
                
                logger.debug("✅ PATSTAT libraries imported successfully")
                
                # Store models and SQL functions
                self.models = {
                    'TLS201_APPLN': TLS201_APPLN,
                    'TLS202_APPLN_TITLE': TLS202_APPLN_TITLE,
                    'TLS203_APPLN_ABSTR': TLS203_APPLN_ABSTR,
                    'TLS209_APPLN_IPC': TLS209_APPLN_IPC,
                    'TLS224_APPLN_CPC': TLS224_APPLN_CPC,
                    'TLS212_CITATION': TLS212_CITATION,
                    'TLS228_DOCDB_FAM_CITN': TLS228_DOCDB_FAM_CITN,
                    'TLS215_CITN_CATEG': TLS215_CITN_CATEG,
                    'TLS214_NPL_PUBLN': TLS214_NPL_PUBLN,
                    'TLS211_PAT_PUBLN': TLS211_PAT_PUBLN,
                    'TLS227_PERS_PUBLN': TLS227_PERS_PUBLN,
                    'TLS207_PERS_APPLN': TLS207_PERS_APPLN,
                    'TLS206_PERSON': TLS206_PERSON
                }
                self.sql_funcs = {'func': func, 'and_': and_, 'or_': or_}
                
                # Initialize PATSTAT client with connection state tracking
                logger.debug(f"Connecting to PATSTAT {self.environment} environment...")
                
                with self._lock:
                    self.patstat_client = EPOPatstatClient(env=self.environment)
                    # Register the EPO client for safe cleanup
                    _register_epo_client(self.patstat_client)
                    
                    self.db_session = self.patstat_client.orm()
                    
                    # Test connection
                    test_result = self.db_session.query(TLS201_APPLN.docdb_family_id).limit(1).first()
                    self.is_connected = True
                    
                logger.debug(f"✅ Connected to PATSTAT {self.environment} environment")
                logger.debug(f"Database engine: {self.db_session.bind}")
                logger.debug("✅ Table access test successful")
                
            else:
                logger.warning("TIP environment not available")
                self.is_connected = False
                
        except Exception as e:
            logger.error(f"❌ PATSTAT connection failed: {e}")
            self.is_connected = False
    
    def get_session(self):
        """Get database session with connection validation."""
        with self._lock:
            if self.is_closed:
                raise RuntimeError("Connection manager has been closed")
            if not self.is_connected or self.db_session is None:
                raise RuntimeError("PATSTAT connection not available")
            return self.db_session
    
    def get_models(self):
        """Get PATSTAT table models."""
        return self.models.copy()
    
    def get_sql_functions(self):
        """Get SQL function helpers."""
        return self.sql_funcs.copy()
    
    def add_weak_reference(self, obj):
        """Add weak reference to track dependent objects."""
        try:
            weak_ref = weakref.ref(obj, self._cleanup_weak_ref)
            self._weak_refs.add(weak_ref)
        except TypeError:
            # Object doesn't support weak references
            pass
    
    def _cleanup_weak_ref(self, weak_ref):
        """Clean up weak reference."""
        self._weak_refs.discard(weak_ref)
    
    def close(self):
        """Close connection with comprehensive cleanup."""
        with self._lock:
            if self.is_closed:
                return
            
            try:
                # Close database session first
                if hasattr(self, 'db_session') and self.db_session is not None:
                    try:
                        # Check if session is still valid before closing
                        if hasattr(self.db_session, 'close') and callable(self.db_session.close):
                            self.db_session.close()
                            logger.debug("🔒 Database session closed")
                    except Exception as e:
                        logger.warning(f"⚠️ Database session close warning: {e}")
                
                # Close PATSTAT client using safe close function
                if hasattr(self, 'patstat_client') and self.patstat_client is not None:
                    _safe_close_epo_client(self.patstat_client)
                    self.patstat_client = None
                
                # Mark as closed
                self.is_closed = True
                self.is_connected = False
                
                # Clear references
                self.db_session = None
                self.patstat_client = None
                self._weak_refs.clear()
                
            except Exception as e:
                logger.warning(f"⚠️ Connection manager cleanup error: {e}")
                # Ensure we're marked as closed even if cleanup fails
                self.is_closed = True
                self.is_connected = False
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with guaranteed cleanup."""
        self.close()
    
    def __del__(self):
        """Destructor with safe cleanup."""
        try:
            if not self.is_closed:
                self.close()
        except:
            # Silently ignore errors during garbage collection
            pass

class PatstatClient:
    """
    Production-ready PATSTAT client with comprehensive error handling
    and proven working patterns for patent analysis.
    """
    
    def __init__(self, environment: str = 'PROD'):
        """
        Initialize PATSTAT client with environment configuration.
        
        Args:
            environment: 'PROD' (full dataset) or 'TEST' (limited access)
        """
        self.environment = environment
        self.patstat_available = False
        self.patstat_connected = False
        self.connection_manager = None
        self.db = None
        self.models = {}
        self._cleanup_done = False
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize PATSTAT connection using connection manager."""
        try:
            # Create connection manager
            self.connection_manager = PatstatConnectionManager(self.environment)
            
            if self.connection_manager.is_connected:
                # Get references from connection manager
                self.db = self.connection_manager.get_session()
                self.models = self.connection_manager.get_models()
                self.sql_funcs = self.connection_manager.get_sql_functions()
                
                # Register this client with connection manager for tracking
                self.connection_manager.add_weak_reference(self)
                
                self.patstat_available = True
                self.patstat_connected = True
                
            else:
                # External environment - use alternative BigQuery connection
                logger.warning("TIP environment not available, using external BigQuery connection")
                self._initialize_external_connection()
                return
                
        except Exception as e:
            logger.error(f"❌ PATSTAT setup failed: {e}")
            self.patstat_available = False
            self.patstat_connected = False
    
    def _initialize_external_connection(self):
        """Initialize external BigQuery connection for non-TIP environments."""
        try:
            from google.cloud import bigquery
            try:
                from config import get_database_config
            except ImportError:
                import sys
                from pathlib import Path
                config_path = Path(__file__).parent.parent / 'config'
                sys.path.insert(0, str(config_path.parent))
                from config import get_database_config
            import os
            
            external_config = get_database_config('patstat.environments.external_environment', {})
            
            if external_config.get('authentication') == 'service_account':
                service_account_path = external_config.get('service_account_path')
                if service_account_path and service_account_path.startswith('${ENV:'):
                    env_var = service_account_path[6:-1]  # Remove ${ENV: and }
                    service_account_path = os.getenv(env_var)
                
                if service_account_path:
                    self.client = bigquery.Client.from_service_account_json(service_account_path)
                else:
                    self.client = bigquery.Client()  # Use default credentials
            else:
                self.client = bigquery.Client()
            
            # Test connection
            query = "SELECT 1 as test"
            self.client.query(query).result()
            
            self.patstat_available = True
            self.patstat_connected = True
            logger.debug("✅ External BigQuery connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to establish external BigQuery connection: {e}")
            self.patstat_available = False
            self.patstat_connected = False
    
    
    def is_connected(self) -> bool:
        """Check if PATSTAT is connected and ready."""
        return self.patstat_connected
    
    def get_connection_status(self) -> Dict[str, bool]:
        """Get detailed connection status."""
        return {
            'patstat_available': self.patstat_available,
            'patstat_connected': self.patstat_connected,
            'environment': self.environment
        }
    
    def close(self):
        """Clean up resources using connection manager."""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return
            
        try:
            # Use connection manager for cleanup
            if hasattr(self, 'connection_manager') and self.connection_manager is not None:
                self.connection_manager.close()
                logger.debug("🔒 Connection manager closed")
            
            # Clear references
            self.db = None
            self.models = {}
            self.sql_funcs = {}
            self.connection_manager = None
            
            # Mark cleanup as done
            self._cleanup_done = True
            self.patstat_connected = False
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error (non-critical): {e}")
            if hasattr(self, '_cleanup_done'):
                self._cleanup_done = True
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with guaranteed cleanup."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure cleanup on garbage collection."""
        try:
            self.close()
        except:
            # Silently ignore errors during garbage collection
            pass

class PatentSearcher:
    """
    Technology-agnostic patent searcher with configurable search parameters.
    Uses centralized configuration for all search parameters.
    """
    
    def __init__(self, patstat_client: PatstatClient):
        """
        Initialize patent searcher.
        
        Args:
            patstat_client: Connected PATSTAT client instance
        """
        self.client = patstat_client
        self.models = patstat_client.models if hasattr(patstat_client, 'models') else {}
        self.sql_funcs = patstat_client.sql_funcs if hasattr(patstat_client, 'sql_funcs') else {}
        
        # Load centralized search configuration with error handling
        try:
            from config import get_patent_search_config
        except ImportError:
            # Fallback for relative import
            import sys
            from pathlib import Path
            config_path = Path(__file__).parent.parent / 'config'
            sys.path.insert(0, str(config_path.parent))
            from config import get_patent_search_config
        
        try:
            self.search_config = get_patent_search_config()
            logger.debug("✅ Search configuration loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load search configuration: {e}")
            # Cannot proceed without configuration
            raise RuntimeError("Search configuration is required for patent searcher functionality") from e
        
        # Extract search parameters from configuration
        keywords_config = self.search_config.get('keywords', {})
        self.search_keywords = keywords_config.get('primary', []) + keywords_config.get('specific_elements', [])
        self.recovery_keywords = keywords_config.get('recovery', [])
        
        # Extract classification codes from the correct YAML structure
        cpc_classifications = self.search_config.get('cpc_classifications', {})
        technology_areas = cpc_classifications.get('technology_areas', {})
        
        # Flatten all CPC codes from technology areas
        self.cpc_codes = []
        for area_name, area_config in technology_areas.items():
            if isinstance(area_config, dict) and 'codes' in area_config:
                category_codes = area_config['codes']
                if isinstance(category_codes, list):
                    self.cpc_codes.extend(category_codes)
        
        # No IPC codes in current configuration (CPC-only approach)
        self.ipc_codes = []
        
        # Load search strategies
        self.search_strategies = self.search_config.get('search_strategies', {})
        self.quality_thresholds = self.search_config.get('quality_thresholds', {})
        
        # Store technology areas for selective searching
        self.technology_areas = technology_areas
    
    def get_available_technology_areas(self) -> list:
        """Get list of available technology areas from configuration."""
        return list(self.technology_areas.keys())
    
    def get_cpc_codes_for_technology(self, technology_area: str) -> list:
        """Get CPC codes for a specific technology area."""
        area_config = self.technology_areas.get(technology_area, {})
        return area_config.get('codes', [])
    
    def execute_technology_specific_search(self, 
                                         technology_areas: list,
                                         start_date: str = '2010-01-01',
                                         end_date: str = '2024-12-31',
                                         focused_search: bool = True) -> pd.DataFrame:
        """
        Execute search for specific technology areas only.
        
        Args:
            technology_areas: List of technology area names to search
            start_date: Search start date (YYYY-MM-DD)
            end_date: Search end date (YYYY-MM-DD)
            focused_search: Use focused keywords for better performance
            
        Returns:
            DataFrame with patent search results
        """
        if not self.client.is_connected():
            logger.error("PATSTAT not connected - cannot execute search")
            raise RuntimeError("PATSTAT connection is required for patent search")
        
        # Get CPC codes for selected technology areas
        selected_cpc_codes = []
        for area in technology_areas:
            area_codes = self.get_cpc_codes_for_technology(area)
            selected_cpc_codes.extend(area_codes)
        
        if not selected_cpc_codes:
            logger.warning(f"No CPC codes found for technology areas: {technology_areas}")
            return pd.DataFrame(columns=['appln_id', 'appln_nr', 'appln_filing_date', 'docdb_family_id', 'earliest_filing_year', 'search_method', 'quality_score', 'filing_year'])
        
        logger.debug(f"🔬 Technology-specific search: {technology_areas}")
        logger.debug(f"📊 Using {len(selected_cpc_codes)} CPC codes from selected areas")
        
        # Temporarily override the instance CPC codes for this search
        original_cpc_codes = self.cpc_codes
        self.cpc_codes = selected_cpc_codes
        
        try:
            # Execute search with selected CPC codes
            result = self.execute_comprehensive_search(start_date, end_date, focused_search)
            return result
        finally:
            # Restore original CPC codes
            self.cpc_codes = original_cpc_codes
    
    def execute_comprehensive_search(self, 
                                   start_date: str = '2010-01-01',
                                   end_date: str = '2024-12-31',
                                   focused_search: bool = True) -> pd.DataFrame:
        """
        Execute comprehensive patent search using proven patterns.
        
        Args:
            start_date: Search start date (YYYY-MM-DD)
            end_date: Search end date (YYYY-MM-DD)
            focused_search: Use focused keywords for better performance
            
        Returns:
            DataFrame with patent search results
        """
        if not self.client.is_connected():
            logger.error("PATSTAT not connected - cannot execute search")
            raise RuntimeError("PATSTAT connection is required for patent search")
        
        try:
            logger.debug("🔍 Executing Real PATSTAT Patent Search - FULL DATASET...")
            
            # Use focused keywords for better performance
            if focused_search:
                keywords_config = self.search_config.get('keywords', {})
                search_keywords = keywords_config.get('focus', [])
                recovery_keywords = keywords_config.get('secondary', [])
            else:
                search_keywords = self.search_keywords
                recovery_keywords = self.recovery_keywords
            
            # Step 1: Abstract keyword search
            abstract_results = self._search_abstracts(search_keywords, recovery_keywords, start_date, end_date)
            
            # Step 2: Title keyword search  
            title_results = self._search_titles(search_keywords, recovery_keywords, start_date, end_date)
            
            # Step 3: Classification search
            classification_results = self._search_classifications(start_date, end_date)
            
            # Combine and analyze results
            return self._combine_search_results(abstract_results, title_results, classification_results)
            
        except Exception as e:
            logger.error(f"❌ Real PATSTAT search failed: {e}")
            raise RuntimeError(f"Patent search failed: {e}") from e
    
    def _search_abstracts(self, primary_keywords: List[str], secondary_keywords: List[str], 
                         start_date: str, end_date: str) -> List:
        """Search patent abstracts for configured keywords."""
        logger.debug("📝 Step 1: Abstract keyword search...")
        
        TLS201_APPLN = self.models['TLS201_APPLN']
        TLS203_APPLN_ABSTR = self.models['TLS203_APPLN_ABSTR']
        and_ = self.sql_funcs['and_']
        or_ = self.sql_funcs['or_']
        
        query = (
            self.client.db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id, 
                                TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS203_APPLN_ABSTR, TLS203_APPLN_ABSTR.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= start_date,
                    TLS201_APPLN.appln_filing_date <= end_date,
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(kw) for kw in primary_keywords]),
                    or_(*[TLS203_APPLN_ABSTR.appln_abstract.contains(rw) for rw in secondary_keywords])
                )
            ).distinct()
        )
        
        results = query.all()
        logger.debug(f"✅ Keywords search: {len(results):,} applications found")
        return results
    
    def _search_titles(self, primary_keywords: List[str], secondary_keywords: List[str],
                      start_date: str, end_date: str) -> List:
        """Search patent titles for configured keywords.""" 
        logger.debug("📝 Step 2: Title keyword search...")
        
        TLS201_APPLN = self.models['TLS201_APPLN']
        TLS202_APPLN_TITLE = self.models['TLS202_APPLN_TITLE']
        and_ = self.sql_funcs['and_']
        or_ = self.sql_funcs['or_']
        
        query = (
            self.client.db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id,
                                TLS201_APPLN.appln_filing_date, TLS201_APPLN.appln_nr)
            .join(TLS202_APPLN_TITLE, TLS202_APPLN_TITLE.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= start_date,
                    TLS201_APPLN.appln_filing_date <= end_date,
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(kw) for kw in primary_keywords]),
                    or_(*[TLS202_APPLN_TITLE.appln_title.contains(rw) for rw in secondary_keywords])
                )
            ).distinct()
        )
        
        results = query.all()
        logger.debug(f"✅ Title search: {len(results):,} applications found")
        return results
    
    def _search_classifications(self, start_date: str, end_date: str) -> List:
        """Search patent classifications for configured codes."""
        logger.debug("📝 Step 3: Classification search...")
        
        TLS201_APPLN = self.models['TLS201_APPLN']
        TLS224_APPLN_CPC = self.models['TLS224_APPLN_CPC']
        and_ = self.sql_funcs['and_']
        func = self.sql_funcs['func']
        
        # Use instance CPC codes (supports technology-specific search)
        focused_codes = self.cpc_codes[:10] if self.cpc_codes else []  # Take first 10 for performance
        
        # Configuration is required - no fallback
        if not focused_codes:
            raise RuntimeError("No classification codes found in configuration")
        
        query = (
            self.client.db.query(TLS201_APPLN.docdb_family_id, TLS201_APPLN.appln_id,
                                TLS201_APPLN.appln_filing_date, TLS224_APPLN_CPC.cpc_class_symbol)
            .join(TLS224_APPLN_CPC, TLS224_APPLN_CPC.appln_id == TLS201_APPLN.appln_id)
            .filter(
                and_(
                    TLS201_APPLN.appln_filing_date >= start_date,
                    TLS201_APPLN.appln_filing_date <= end_date,
                    func.substr(TLS224_APPLN_CPC.cpc_class_symbol, 1, 11).in_(focused_codes)
                )
            ).distinct()
        )
        
        results = query.all()
        logger.debug(f"✅ Classification search: {len(results):,} applications found")
        return results
    
    def _combine_search_results(self, abstract_results: List, title_results: List, 
                               classification_results: List) -> pd.DataFrame:
        """Combine search results and calculate quality scores."""
        # Extract family IDs
        abstract_families = [row.docdb_family_id for row in abstract_results]
        title_families = [row.docdb_family_id for row in title_results]
        classification_families = [row.docdb_family_id for row in classification_results]
        
        # Combine results
        all_keyword_families = list(set(abstract_families + title_families))
        all_families = list(set(all_keyword_families + classification_families))
        intersection_families = list(set(all_keyword_families) & set(classification_families))
        
        logger.debug(f"\n📊 SEARCH RESULTS SUMMARY:")
        logger.debug(f"   Keywords families: {len(all_keyword_families):,}")
        logger.debug(f"   Classification families: {len(set(classification_families)):,}")
        logger.debug(f"   Total unique families: {len(all_families):,}")
        logger.debug(f"   🎯 High-quality intersection: {len(intersection_families):,}")
        
        if len(all_families) == 0:
            logger.warning("No results found in search")
            return pd.DataFrame(columns=['appln_id', 'appln_nr', 'appln_filing_date', 'docdb_family_id', 'earliest_filing_year', 'search_method', 'quality_score', 'filing_year'])
        
        # Build final dataset
        TLS201_APPLN = self.models['TLS201_APPLN']
        
        final_query = (
            self.client.db.query(TLS201_APPLN.appln_id, TLS201_APPLN.appln_nr, 
                                TLS201_APPLN.appln_filing_date, TLS201_APPLN.docdb_family_id,
                                TLS201_APPLN.earliest_filing_year)
            .filter(TLS201_APPLN.docdb_family_id.in_(all_families))
            .distinct()
        )
        
        final_results = final_query.all()
        df_result = pd.DataFrame(final_results, columns=[
            'appln_id', 'appln_nr', 'appln_filing_date', 'docdb_family_id', 'earliest_filing_year'
        ])
        
        # Add quality indicators
        df_result['search_method'] = 'Real PATSTAT (Full Keywords + Classification)'
        df_result['quality_score'] = df_result['docdb_family_id'].apply(
            lambda x: 1.0 if x in intersection_families else 
                     0.9 if x in all_keyword_families else 0.8
        )
        df_result['filing_year'] = pd.to_datetime(df_result['appln_filing_date']).dt.year
        
        logger.debug("✅ Real PATSTAT search successful!")
        logger.debug(f"📈 Found {len(df_result):,} patent applications")
        logger.debug(f"📊 Covering {df_result['docdb_family_id'].nunique():,} unique families")
        logger.debug(f"🏆 Average quality score: {df_result['quality_score'].mean():.2f}")
        
        return df_result
    
    def close(self):
        """Clean up resources by delegating to client."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

class CitationAnalyzer:
    """
    Advanced citation analysis using PATSTAT citation tables.
    Based on proven patterns from EPO PATLIB 2025 implementation.
    """
    
    def __init__(self, patstat_client: PatstatClient):
        """
        Initialize citation analyzer.
        
        Args:
            patstat_client: Connected PATSTAT client instance
        """
        self.client = patstat_client
        self.models = patstat_client.models if hasattr(patstat_client, 'models') else {}
        self.sql_funcs = patstat_client.sql_funcs if hasattr(patstat_client, 'sql_funcs') else {}
        
        # Validate required tables
        required_tables = ['TLS228_DOCDB_FAM_CITN', 'TLS201_APPLN', 'TLS212_CITATION']
        missing_tables = [table for table in required_tables if table not in self.models]
        
        if missing_tables:
            raise RuntimeError(f"Citation analysis requires tables: {missing_tables}")
        
        logger.debug("✅ Citation analyzer initialized with PATSTAT tables")
    
    def get_forward_citations(self, family_ids: List[int], include_metadata: bool = True) -> pd.DataFrame:
        """
        Extract families citing the specified families (forward citations).
        Based on proven working pattern from notebook implementation.
        
        Args:
            family_ids: List of DOCDB family IDs to analyze
            include_metadata: Include additional citation metadata
            
        Returns:
            DataFrame with forward citation relationships
        """
        if not self.client.is_connected():
            raise RuntimeError("PATSTAT connection is required for citation analysis")
        
        logger.debug(f"🔍 Analyzing forward citations for {len(family_ids)} families...")
        
        TLS228_DOCDB_FAM_CITN = self.models['TLS228_DOCDB_FAM_CITN']
        
        # Forward citations query - families appear in cited_docdb_family_id field
        query = self.client.db.query(
            TLS228_DOCDB_FAM_CITN.cited_docdb_family_id.label('cited_family_id'),
            TLS228_DOCDB_FAM_CITN.docdb_family_id.label('citing_family_id')
        ).filter(
            TLS228_DOCDB_FAM_CITN.cited_docdb_family_id.in_(family_ids)
        )
        
        # Execute query
        forward_citations_data = query.all()
        
        if not forward_citations_data:
            logger.warning("⚠️ No forward citations found")
            return pd.DataFrame(columns=['cited_family_id', 'citing_family_id'])
        
        # Convert to DataFrame
        forward_citations_df = pd.DataFrame(forward_citations_data, columns=[
            'cited_family_id', 'citing_family_id'
        ])
        
        # Add metadata if requested
        if include_metadata:
            forward_citations_df = self._enrich_citation_metadata(
                forward_citations_df, 'forward'
            )
        
        logger.debug(f"✅ Found {len(forward_citations_df)} forward citation relationships")
        logger.debug(f"   {forward_citations_df['citing_family_id'].nunique()} unique citing families")
        logger.debug(f"   {forward_citations_df['cited_family_id'].nunique()} cited families")
        
        return forward_citations_df
    
    def get_backward_citations(self, family_ids: List[int], include_metadata: bool = True) -> pd.DataFrame:
        """
        Extract families cited by the specified families (backward citations).
        Based on proven working pattern from notebook implementation.
        
        Args:
            family_ids: List of DOCDB family IDs to analyze
            include_metadata: Include additional citation metadata
            
        Returns:
            DataFrame with backward citation relationships
        """
        if not self.client.is_connected():
            raise RuntimeError("PATSTAT connection is required for citation analysis")
        
        logger.debug(f"🔍 Analyzing backward citations from {len(family_ids)} families...")
        
        TLS228_DOCDB_FAM_CITN = self.models['TLS228_DOCDB_FAM_CITN']
        
        # Backward citations query - families appear in docdb_family_id field
        query = self.client.db.query(
            TLS228_DOCDB_FAM_CITN.docdb_family_id.label('citing_family_id'),
            TLS228_DOCDB_FAM_CITN.cited_docdb_family_id.label('cited_family_id')
        ).filter(
            TLS228_DOCDB_FAM_CITN.docdb_family_id.in_(family_ids)
        )
        
        # Execute query
        backward_citations_data = query.all()
        
        if not backward_citations_data:
            logger.warning("⚠️ No backward citations found")
            return pd.DataFrame(columns=['citing_family_id', 'cited_family_id'])
        
        # Convert to DataFrame
        backward_citations_df = pd.DataFrame(backward_citations_data, columns=[
            'citing_family_id', 'cited_family_id'
        ])
        
        # Add metadata if requested
        if include_metadata:
            backward_citations_df = self._enrich_citation_metadata(
                backward_citations_df, 'backward'
            )
        
        logger.debug(f"✅ Found {len(backward_citations_df)} backward citation relationships")
        logger.debug(f"   {backward_citations_df['citing_family_id'].nunique()} families citing prior art")
        logger.debug(f"   {backward_citations_df['cited_family_id'].nunique()} unique cited families")
        
        return backward_citations_df
    
    def get_comprehensive_citation_analysis(self, family_ids: List[int]) -> Dict[str, Union[pd.DataFrame, Dict]]:
        """
        Perform comprehensive citation analysis including forward, backward, and network metrics.
        
        Args:
            family_ids: List of DOCDB family IDs to analyze
            
        Returns:
            Dictionary containing citation DataFrames and analysis metrics
        """
        logger.debug(f"📊 Performing comprehensive citation analysis for {len(family_ids)} families...")
        
        # Get forward and backward citations
        forward_citations = self.get_forward_citations(family_ids, include_metadata=True)
        backward_citations = self.get_backward_citations(family_ids, include_metadata=True)
        
        # Calculate network metrics
        network_metrics = self._calculate_network_metrics(forward_citations, backward_citations, family_ids)
        
        # Most cited families
        most_cited = self._get_most_cited_families(forward_citations) if not forward_citations.empty else {}
        
        # Most citing families (from original set)
        most_citing = self._get_most_citing_families(backward_citations) if not backward_citations.empty else {}
        
        # Citation quality analysis
        quality_metrics = self._analyze_citation_quality(forward_citations, backward_citations)
        
        results = {
            'forward_citations': forward_citations,
            'backward_citations': backward_citations,
            'network_metrics': network_metrics,
            'most_cited_families': most_cited,
            'most_citing_families': most_citing,
            'quality_metrics': quality_metrics,
            'summary': {
                'total_families_analyzed': len(family_ids),
                'forward_citation_count': len(forward_citations),
                'backward_citation_count': len(backward_citations),
                'total_citation_relationships': len(forward_citations) + len(backward_citations),
                'analysis_timestamp': datetime.now().isoformat()
            }
        }
        
        logger.debug("✅ Comprehensive citation analysis completed")
        return results
    
    def _enrich_citation_metadata(self, citation_df: pd.DataFrame, citation_type: str) -> pd.DataFrame:
        """
        Enrich citation data with additional metadata from PATSTAT tables.
        
        Args:
            citation_df: DataFrame with citation relationships
            citation_type: 'forward' or 'backward'
            
        Returns:
            Enriched DataFrame with metadata
        """
        if citation_df.empty:
            return citation_df
        
        try:
            TLS201_APPLN = self.models['TLS201_APPLN']
            
            # Get basic application data for cited families
            if citation_type == 'forward':
                family_ids = citation_df['cited_family_id'].unique()
                id_column = 'cited_family_id'
            else:
                family_ids = citation_df['cited_family_id'].unique()
                id_column = 'cited_family_id'
            
            # Query for metadata
            metadata_query = self.client.db.query(
                TLS201_APPLN.docdb_family_id,
                TLS201_APPLN.earliest_filing_year,
                TLS201_APPLN.earliest_publn_year
            ).filter(
                TLS201_APPLN.docdb_family_id.in_(family_ids)
            ).distinct()
            
            metadata_df = pd.DataFrame(
                metadata_query.all(),
                columns=['docdb_family_id', 'earliest_filing_year', 'earliest_publn_year']
            )
            
            # Merge metadata
            enriched_df = citation_df.merge(
                metadata_df, 
                left_on=id_column, 
                right_on='docdb_family_id', 
                how='left'
            ).drop('docdb_family_id', axis=1)
            
            return enriched_df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not enrich citation metadata: {e}")
            return citation_df
    
    def _calculate_network_metrics(self, forward_citations: pd.DataFrame, 
                                 backward_citations: pd.DataFrame, original_families: List[int]) -> Dict:
        """Calculate citation network metrics."""
        metrics = {
            'forward_metrics': {},
            'backward_metrics': {},
            'network_overview': {}
        }
        
        if not forward_citations.empty:
            metrics['forward_metrics'] = {
                'total_forward_citations': len(forward_citations),
                'unique_citing_families': forward_citations['citing_family_id'].nunique(),
                'unique_cited_families': forward_citations['cited_family_id'].nunique(),
                'avg_citations_per_family': len(forward_citations) / forward_citations['cited_family_id'].nunique() if not forward_citations.empty else 0
            }
        
        if not backward_citations.empty:
            metrics['backward_metrics'] = {
                'total_backward_citations': len(backward_citations),
                'unique_citing_families': backward_citations['citing_family_id'].nunique(),
                'unique_cited_families': backward_citations['cited_family_id'].nunique(),
                'avg_references_per_family': len(backward_citations) / backward_citations['citing_family_id'].nunique() if not backward_citations.empty else 0
            }
        
        total_forward = len(forward_citations)
        total_backward = len(backward_citations)
        
        metrics['network_overview'] = {
            'total_families_analyzed': len(original_families),
            'total_citation_relationships': total_forward + total_backward,
            'citation_ratio': total_forward / total_backward if total_backward > 0 else 0,
            'network_density': (total_forward + total_backward) / len(original_families) if original_families else 0
        }
        
        return metrics
    
    def _get_most_cited_families(self, forward_citations: pd.DataFrame, top_n: int = 10) -> Dict[int, int]:
        """Get most cited families from forward citations."""
        if forward_citations.empty:
            return {}
        
        most_cited = forward_citations.groupby('cited_family_id').size().sort_values(ascending=False).head(top_n)
        return most_cited.to_dict()
    
    def _get_most_citing_families(self, backward_citations: pd.DataFrame, top_n: int = 10) -> Dict[int, int]:
        """Get families that cite the most prior art."""
        if backward_citations.empty:
            return {}
        
        most_citing = backward_citations.groupby('citing_family_id').size().sort_values(ascending=False).head(top_n)
        return most_citing.to_dict()
    
    def _analyze_citation_quality(self, forward_citations: pd.DataFrame, 
                                backward_citations: pd.DataFrame) -> Dict:
        """Analyze citation quality metrics."""
        quality_metrics = {
            'forward_quality': {},
            'backward_quality': {},
            'overall_quality': {}
        }
        
        # Basic quality indicators based on citation patterns
        if not forward_citations.empty:
            citing_distribution = forward_citations['citing_family_id'].value_counts()
            quality_metrics['forward_quality'] = {
                'high_impact_families': (citing_distribution >= 5).sum(),  # Families cited 5+ times
                'medium_impact_families': ((citing_distribution >= 2) & (citing_distribution < 5)).sum(),
                'low_impact_families': (citing_distribution == 1).sum(),
                'avg_citations_per_family': citing_distribution.mean(),
                'max_citations_single_family': citing_distribution.max()
            }
        
        if not backward_citations.empty:
            cited_distribution = backward_citations['citing_family_id'].value_counts()
            quality_metrics['backward_quality'] = {
                'highly_referencing_families': (cited_distribution >= 10).sum(),  # Families citing 10+ prior art
                'medium_referencing_families': ((cited_distribution >= 5) & (cited_distribution < 10)).sum(),
                'low_referencing_families': (cited_distribution < 5).sum(),
                'avg_references_per_family': cited_distribution.mean(),
                'max_references_single_family': cited_distribution.max()
            }
        
        # Overall quality assessment
        total_forward = len(forward_citations)
        total_backward = len(backward_citations)
        
        if total_forward > 0 or total_backward > 0:
            quality_metrics['overall_quality'] = {
                'citation_activity_level': 'high' if (total_forward + total_backward) > 100 else 'medium' if (total_forward + total_backward) > 50 else 'low',
                'innovation_impact_ratio': total_forward / total_backward if total_backward > 0 else 0,
                'technology_maturity': 'emerging' if total_forward / total_backward > 1 else 'established' if total_backward > 0 else 'unknown'
            }
        
        return quality_metrics
    
    def close(self):
        """Clean up resources by delegating to client."""
        if hasattr(self, 'client') and self.client:
            self.client.close()

