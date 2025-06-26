"""
EPO Open Patent Services (OPS) API Client
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides secure EPO OPS API integration for patent data enrichment
and validation against PATSTAT results.
"""

import os
import requests
import json
import pandas as pd
import time
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
import logging
from urllib.parse import quote

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from patlib/.env file
def load_env_file():
    """Load environment variables from the patlib/.env file."""
    try:
        # Look for .env file in patlib directory
        env_file_paths = [
            '/home/jovyan/patlib/.env',  # Full path
            '../../../.env',             # Relative to 0-main
            '../../../../.env'           # Alternative relative path
        ]
        
        for env_file in env_file_paths:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                logger.debug(f"✅ Loaded environment variables from {env_file}")
                return True
        
        logger.warning("⚠️ No .env file found in expected locations")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load .env file: {e}")
        return False

# Load environment variables on module import
load_env_file()

class EPOOPSClient:
    """
    Production-ready EPO Open Patent Services API client with rate limiting
    and comprehensive error handling.
    """
    
    BASE_URL = "https://ops.epo.org/3.2/rest-services"
    AUTH_URL = "https://ops.epo.org/3.2/auth/accesstoken"
    
    def __init__(self, consumer_key: Optional[str] = None, consumer_secret: Optional[str] = None):
        """
        Initialize EPO OPS client with API credentials.
        
        Args:
            consumer_key: EPO OPS consumer key (defaults to ENV:OPS_KEY)
            consumer_secret: EPO OPS consumer secret (defaults to ENV:OPS_SECRET)
        """
        self.consumer_key = consumer_key or os.getenv('OPS_KEY')
        self.consumer_secret = consumer_secret or os.getenv('OPS_SECRET')
        
        # Initialize status attributes
        self.authentication_configured = bool(self.consumer_key and self.consumer_secret)
        self.client_available = self.authentication_configured
        self.authenticated = False
        self.access_token = None
        self.token_expires = None
        self.rate_limit_reset = None
        self.remaining_requests = None
        
        if not self.authentication_configured:
            logger.warning("⚠️ EPO OPS credentials not found. Set OPS_KEY and OPS_SECRET environment variables.")
        else:
            # Rate limiting parameters
            self.last_request_time = None
            self.min_request_interval = 1.0  # Minimum seconds between requests
            
            # Initialize session
            self.session = requests.Session()
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with EPO OPS and obtain access token."""
        try:
            auth_data = {
                'grant_type': 'client_credentials'
            }
            
            response = self.session.post(
                self.AUTH_URL,
                auth=(self.consumer_key, self.consumer_secret),
                data=auth_data
            )
            
            response.raise_for_status()
            auth_result = response.json()
            
            self.access_token = auth_result.get('access_token')
            expires_in = auth_result.get('expires_in', 3600)
            
            # Ensure expires_in is numeric (API might return string)
            try:
                expires_in = int(expires_in)
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Invalid expires_in value: {expires_in}, using default 3600")
                expires_in = 3600
            
            self.token_expires = datetime.now() + timedelta(seconds=expires_in)
            
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            })
            
            self.authenticated = True
            logger.debug("✅ EPO OPS authentication successful")
            
        except Exception as e:
            logger.error(f"❌ EPO OPS authentication failed: {e}")
            self.authenticated = False
    
    def _check_and_refresh_token(self):
        """Check token expiry and refresh if needed."""
        if not self.authenticated:
            return False
            
        if self.token_expires and datetime.now() >= self.token_expires:
            logger.debug("🔄 Refreshing EPO OPS token...")
            self._authenticate()
        
        return self.authenticated
    
    def _rate_limit_wait(self):
        """Implement rate limiting to avoid API throttling."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make authenticated request to EPO OPS API with error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            API response as dictionary or None if failed
        """
        if not self._check_and_refresh_token():
            logger.error("❌ Cannot make request - authentication failed")
            return None
        
        self._rate_limit_wait()
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params)
            
            # Update rate limit info from headers
            self.remaining_requests = response.headers.get('X-RateLimit-Remaining')
            reset_time = response.headers.get('X-RateLimit-Reset')
            if reset_time:
                self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:  # Rate limit exceeded
                logger.warning("⚠️ Rate limit exceeded - waiting...")
                time.sleep(60)  # Wait 1 minute
                return self._make_request(endpoint, params)  # Retry once
            else:
                logger.error(f"❌ HTTP error {response.status_code}: {e}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            return None
    
    def search_patents(self, query: str, range_begin: int = 1, range_end: int = 25) -> Optional[Dict]:
        """
        Search patents using EPO OPS published-data search.
        
        Args:
            query: CQL (Contextual Query Language) search query
            range_begin: Start index for results
            range_end: End index for results
            
        Returns:
            Search results as dictionary
        """
        endpoint = "published-data/search"
        params = {
            'q': query,
            'Range': f'{range_begin}-{range_end}'
        }
        
        logger.debug(f"🔍 Searching patents: {query[:100]}...")
        result = self._make_request(endpoint, params)
        
        if result:
            total_results = result.get('ops:world-patent-data', {}).get('ops:biblio-search', {}).get('@total-result-count', 0)
            logger.debug(f"📊 Found {total_results} results")
        
        return result
    
    def get_patent_details(self, reference_type: str, patent_number: str, 
                          sections: List[str] = None) -> Optional[Dict]:
        """
        Get detailed patent information.
        
        Args:
            reference_type: 'publication', 'application', or 'priority'
            patent_number: Patent number (e.g., 'EP1000000A1')
            sections: Data sections to retrieve ['biblio', 'abstract', 'claims', 'description']
            
        Returns:
            Patent details as dictionary
        """
        if sections is None:
            sections = ['biblio', 'abstract']
        
        sections_str = ','.join(sections)
        endpoint = f"published-data/{reference_type}/{patent_number}/{sections_str}"
        
        logger.debug(f"📄 Fetching patent details: {patent_number}")
        return self._make_request(endpoint)
    
    def get_patent_family(self, reference_type: str, patent_number: str) -> Optional[Dict]:
        """
        Get patent family information.
        
        Args:
            reference_type: 'publication', 'application', or 'priority'  
            patent_number: Patent number
            
        Returns:
            Patent family data as dictionary
        """
        endpoint = f"published-data/{reference_type}/{patent_number}/family"
        
        logger.debug(f"👪 Fetching patent family: {patent_number}")
        return self._make_request(endpoint)
    
    def get_citations(self, reference_type: str, patent_number: str, 
                     citation_type: str = 'all') -> Optional[Dict]:
        """
        Get patent citations.
        
        Args:
            reference_type: 'publication', 'application', or 'priority'
            patent_number: Patent number
            citation_type: 'all', 'applicant', or 'examiner'
            
        Returns:
            Citations data as dictionary
        """
        endpoint = f"published-data/{reference_type}/{patent_number}/citations/{citation_type}"
        
        logger.debug(f"🔗 Fetching citations: {patent_number}")
        return self._make_request(endpoint)
    
    def get_batch_citations(self, patent_numbers: List[str], reference_type: str = 'publication',
                          citation_type: str = 'all', max_patents: int = 100) -> Dict[str, Optional[Dict]]:
        """
        Get citations for multiple patents with rate limiting.
        
        Args:
            patent_numbers: List of patent numbers
            reference_type: 'publication', 'application', or 'priority'
            citation_type: 'all', 'applicant', or 'examiner'
            max_patents: Maximum number of patents to process
            
        Returns:
            Dictionary mapping patent numbers to citation data
        """
        if not self.authenticated:
            logger.error("❌ EPO OPS not authenticated for batch citation requests")
            return {}
        
        # Limit the number of patents to process
        patents_to_process = patent_numbers[:max_patents]
        logger.debug(f"🔗 Fetching citations for {len(patents_to_process)} patents...")
        
        citation_results = {}
        
        for i, patent_number in enumerate(patents_to_process):
            try:
                citations = self.get_citations(reference_type, patent_number, citation_type)
                citation_results[patent_number] = citations
                
                # Rate limiting - extra delay for batch requests
                if i < len(patents_to_process) - 1:  # Don't wait after the last request
                    time.sleep(2)  # 2 seconds between requests for safety
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to get citations for {patent_number}: {e}")
                citation_results[patent_number] = None
        
        logger.debug(f"✅ Completed batch citation fetch: {len(citation_results)} results")
        return citation_results
    
    def analyze_citation_network(self, patent_numbers: List[str], depth: int = 1) -> Dict[str, any]:
        """
        Analyze citation network for a set of patents using EPO OPS.
        
        Args:
            patent_numbers: List of patent numbers to analyze
            depth: Citation depth (1 = direct citations only)
            
        Returns:
            Dictionary with citation network analysis
        """
        if not self.authenticated:
            logger.error("❌ EPO OPS not authenticated for citation network analysis")
            return {}
        
        logger.debug(f"🕸️ Analyzing citation network for {len(patent_numbers)} patents (depth={depth})...")
        
        # Get citations for all patents
        citation_data = self.get_batch_citations(patent_numbers)
        
        # Analyze the citation network
        network_analysis = {
            'source_patents': patent_numbers,
            'citation_data': citation_data,
            'network_metrics': self._calculate_ops_network_metrics(citation_data),
            'most_cited_patents': self._find_most_cited_patents(citation_data),
            'citation_summary': self._summarize_citation_patterns(citation_data)
        }
        
        logger.debug("✅ Citation network analysis completed")
        return network_analysis
    
    def _calculate_ops_network_metrics(self, citation_data: Dict[str, Optional[Dict]]) -> Dict:
        """Calculate network metrics from OPS citation data."""
        metrics = {
            'total_patents_analyzed': len(citation_data),
            'patents_with_citations': 0,
            'total_forward_citations': 0,
            'total_backward_citations': 0,
            'avg_citations_per_patent': 0
        }
        
        citation_counts = []
        
        for patent_num, citations in citation_data.items():
            if citations is None:
                continue
            
            try:
                # Extract citation counts from OPS response structure
                world_data = citations.get('ops:world-patent-data', {})
                citation_info = world_data.get('ops:patent-citations', {})
                
                if citation_info:
                    metrics['patents_with_citations'] += 1
                    
                    # Count different citation types
                    if isinstance(citation_info, dict):
                        # Count forward citations (cited by)
                        cited_by = citation_info.get('ops:patent-citation', [])
                        if not isinstance(cited_by, list):
                            cited_by = [cited_by] if cited_by else []
                        
                        citation_count = len(cited_by)
                        citation_counts.append(citation_count)
                        metrics['total_forward_citations'] += citation_count
                
            except Exception as e:
                logger.debug(f"Error processing citations for {patent_num}: {e}")
        
        if citation_counts:
            metrics['avg_citations_per_patent'] = sum(citation_counts) / len(citation_counts)
        
        return metrics
    
    def _find_most_cited_patents(self, citation_data: Dict[str, Optional[Dict]]) -> List[Dict]:
        """Find most cited patents from OPS citation data."""
        patent_citation_counts = []
        
        for patent_num, citations in citation_data.items():
            if citations is None:
                continue
            
            try:
                world_data = citations.get('ops:world-patent-data', {})
                citation_info = world_data.get('ops:patent-citations', {})
                
                if citation_info:
                    cited_by = citation_info.get('ops:patent-citation', [])
                    if not isinstance(cited_by, list):
                        cited_by = [cited_by] if cited_by else []
                    
                    citation_count = len(cited_by)
                    
                    patent_citation_counts.append({
                        'patent_number': patent_num,
                        'citation_count': citation_count
                    })
                
            except Exception as e:
                logger.debug(f"Error processing {patent_num}: {e}")
        
        # Sort by citation count
        most_cited = sorted(patent_citation_counts, key=lambda x: x['citation_count'], reverse=True)
        return most_cited[:10]  # Top 10
    
    def _summarize_citation_patterns(self, citation_data: Dict[str, Optional[Dict]]) -> Dict:
        """Summarize citation patterns from OPS data."""
        summary = {
            'citation_activity': 'low',
            'most_active_year': None,
            'citation_distribution': {},
            'data_quality': 'good' if citation_data else 'no_data'
        }
        
        # Count successful retrievals
        successful_retrievals = sum(1 for citations in citation_data.values() if citations is not None)
        total_patents = len(citation_data)
        
        if total_patents > 0:
            success_rate = successful_retrievals / total_patents
            if success_rate >= 0.8:
                summary['data_quality'] = 'excellent'
            elif success_rate >= 0.6:
                summary['data_quality'] = 'good'
            elif success_rate >= 0.4:
                summary['data_quality'] = 'fair'
            else:
                summary['data_quality'] = 'poor'
        
        # Analyze citation activity level
        total_citations = sum(1 for citations in citation_data.values() 
                            if citations is not None and 
                            citations.get('ops:world-patent-data', {}).get('ops:patent-citations'))
        
        if total_citations >= len(citation_data) * 0.5:
            summary['citation_activity'] = 'high'
        elif total_citations >= len(citation_data) * 0.2:
            summary['citation_activity'] = 'medium'
        else:
            summary['citation_activity'] = 'low'
        
        return summary

class PatentValidator:
    """
    Generic patent data validator using EPO OPS API to cross-check PATSTAT results.
    Uses centralized configuration for validation keywords and patterns.
    """
    
    def __init__(self, ops_client: EPOOPSClient):
        """
        Initialize validator with EPO OPS client.
        
        Args:
            ops_client: Authenticated EPO OPS client
        """
        self.ops_client = ops_client
        
        # Load validation keywords from centralized config
        try:
            from config import get_patent_search_config
            search_config = get_patent_search_config()
            keywords_config = search_config.get('keywords', {})
            
            # Combine all keyword categories for validation
            self.validation_keywords = []
            for category in ['primary', 'specific_elements', 'recovery', 'validation']:
                self.validation_keywords.extend(keywords_config.get(category, []))
            
            if not self.validation_keywords:
                logger.error("No validation keywords found in configuration")
                raise ValueError("Validation keywords are required but not found in configuration")
                
            logger.debug(f"✅ Loaded {len(self.validation_keywords)} validation keywords from config")
            
        except Exception as e:
            logger.error(f"❌ Failed to load validation keywords from config: {e}")
            raise RuntimeError("Cannot initialize validator without proper configuration") from e
    
    def validate_patent_batch(self, patent_numbers: List[str], 
                            sample_size: int = 10) -> Dict[str, any]:
        """
        Validate a batch of patents against EPO OPS for quality assurance.
        
        Args:
            patent_numbers: List of patent numbers to validate
            sample_size: Number of patents to sample for validation
            
        Returns:
            Validation results dictionary
        """
        if not self.ops_client.authenticated:
            logger.warning("⚠️ EPO OPS not authenticated - skipping validation")
            return {"validated": False, "reason": "Authentication failed"}
        
        # Sample patents for validation
        import random
        sample_patents = random.sample(patent_numbers, min(sample_size, len(patent_numbers)))
        
        validation_results = {
            "total_patents": len(patent_numbers),
            "sample_size": len(sample_patents),
            "validated_patents": [],
            "validation_errors": [],
            "relevance_scores": [],
            "validation_summary": {}
        }
        
        logger.debug(f"🔍 Validating {len(sample_patents)} sample patents...")
        
        for patent_num in sample_patents:
            try:
                # Get patent details
                patent_details = self.ops_client.get_patent_details('publication', patent_num)
                
                if patent_details:
                    relevance_score = self._calculate_relevance(patent_details)
                    validation_results["relevance_scores"].append(relevance_score)
                    validation_results["validated_patents"].append({
                        "patent_number": patent_num,
                        "relevance_score": relevance_score,
                        "validated": True
                    })
                else:
                    validation_results["validation_errors"].append(f"Could not fetch details for {patent_num}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                validation_results["validation_errors"].append(f"Error validating {patent_num}: {e}")
        
        # Calculate validation summary
        if validation_results["relevance_scores"]:
            avg_relevance = sum(validation_results["relevance_scores"]) / len(validation_results["relevance_scores"])
            validation_results["validation_summary"] = {
                "average_relevance_score": avg_relevance,
                "high_relevance_count": sum(1 for score in validation_results["relevance_scores"] if score >= 0.7),
                "validation_success_rate": len(validation_results["validated_patents"]) / len(sample_patents)
            }
        
        logger.debug(f"✅ Validation complete - Average relevance: {validation_results['validation_summary'].get('average_relevance_score', 0):.2f}")
        
        return validation_results
    
    def _calculate_relevance(self, patent_details: Dict) -> float:
        """
        Calculate relevance score based on patent content using configured keywords.
        
        Args:
            patent_details: Patent details from EPO OPS
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        try:
            # Extract text content
            text_content = ""
            
            # Get title
            if 'ops:world-patent-data' in patent_details:
                patent_data = patent_details['ops:world-patent-data']
                if 'ops:biblio-search' in patent_data:
                    biblio_data = patent_data['ops:biblio-search']
                    # Extract title and abstract text
                    text_content += str(biblio_data).lower()
            
            # Count keyword matches
            keyword_matches = 0
            for keyword in self.validation_keywords:
                if keyword.lower() in text_content:
                    keyword_matches += 1
            
            # Calculate relevance score
            max_possible_matches = len(self.validation_keywords)
            relevance_score = min(keyword_matches / max_possible_matches * 2.0, 1.0)  # Scale appropriately
            
            return relevance_score
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {e}")
            return 0.0

def create_search_queries() -> List[str]:
    """
    Create EPO OPS CQL queries for patent search using centralized config.
    
    Returns:
        List of CQL query strings
    """
    try:
        from config import get_epo_ops_query_templates
        
        # Get query templates from centralized config
        query_templates = get_epo_ops_query_templates()
        
        if query_templates:
            base_queries = []
            for template_name, template_config in query_templates.items():
                if isinstance(template_config, dict) and 'template' in template_config:
                    base_queries.append(template_config['template'])
            
            if base_queries:
                logger.debug(f"✅ Loaded {len(base_queries)} query templates from config")
                return base_queries
        
        logger.error("No query templates found in configuration")
        raise ValueError("EPO OPS query templates are required but not found in configuration")
        
    except Exception as e:
        logger.error(f"❌ Failed to load query templates from config: {e}")
        raise RuntimeError("Cannot create search queries without proper configuration") from e

# Market data integration helper functions
def correlate_patent_market_data(patent_df: pd.DataFrame, 
                               market_events: Optional[Dict[int, str]] = None) -> pd.DataFrame:
    """
    Correlate patent filing trends with market events using centralized config.
    
    Args:
        patent_df: DataFrame with patent data including filing dates
        market_events: Dictionary mapping years to market event descriptions (loads from config if None)
        
    Returns:
        Enhanced DataFrame with market correlation data
    """
    # Load market events from config if not provided
    if market_events is None:
        try:
            from config import get_market_data_integration_config
            market_config = get_market_data_integration_config()
            market_events = market_config.get('market_events', {}).get('timeline', {})
            
            # Convert string keys to integers if needed
            if market_events and isinstance(list(market_events.keys())[0], str):
                market_events = {int(k): v for k, v in market_events.items()}
                
            logger.debug(f"✅ Loaded {len(market_events)} market events from config")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load market events from config: {e}")
            logger.warning("Proceeding without market correlation")
            market_events = {}
    if 'filing_year' not in patent_df.columns:
        if 'appln_filing_date' in patent_df.columns:
            patent_df['filing_year'] = pd.to_datetime(patent_df['appln_filing_date']).dt.year
        else:
            logger.warning("⚠️ No filing date information available for market correlation")
            return patent_df
    
    # Add market event information
    patent_df['market_event'] = patent_df['filing_year'].map(market_events)
    
    # Calculate filing trends around market events
    yearly_counts = patent_df.groupby('filing_year').size().reset_index(name='patent_count')
    
    # Add trend indicators
    yearly_counts['market_event'] = yearly_counts['filing_year'].map(market_events)
    yearly_counts['trend_change'] = yearly_counts['patent_count'].pct_change()
    
    logger.debug("📈 Market correlation analysis complete")
    
    return patent_df.merge(yearly_counts[['filing_year', 'trend_change']], on='filing_year', how='left')