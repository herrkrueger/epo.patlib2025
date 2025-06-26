"""
Applicant Analysis Processor for Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes search results from PatentSearchProcessor to analyze applicant patterns,
competitive landscapes, and market intelligence. Works with PATSTAT data to extract applicant information.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import re
from datetime import datetime
import logging

# Import PATSTAT client and models for applicant data enrichment
try:
    from epo.tipdata.patstat import PatstatClient
    from epo.tipdata.patstat.database.models import (
        TLS201_APPLN, TLS207_PERS_APPLN, TLS206_PERSON
    )
    from sqlalchemy import func, and_, distinct
    PATSTAT_AVAILABLE = True
except ImportError:
    PATSTAT_AVAILABLE = False
    logging.warning("PATSTAT integration not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicantAnalyzer:
    """
    Applicant analyzer that works with PatentSearchProcessor results.
    
    Takes patent family search results and enriches them with applicant data from PATSTAT,
    then performs comprehensive market intelligence analysis.
    """
    
    # Geographic patterns for company identification
    GEOGRAPHIC_PATTERNS = {
        'CN': [r'\bCHINA\b', r'\bCHINESE\b', r'UNIVERSITY.*CHINA', r'ACADEMY.*SCIENCES'],
        'US': [r'\bUSA\b', r'\bUS\s', r'\bAMERICA\b', r'CORPORATION\b', r'\bINC\b'],
        'JP': [r'\bJAPAN\b', r'\bJAPANESE\b', r'KABUSHIKI', r'KAISHA', r'HITACHI', r'SONY'],
        'DE': [r'\bGERMAN\b', r'\bGERMANY\b', r'\bGMBH\b', r'SIEMENS', r'BASF'],
        'KR': [r'\bKOREA\b', r'\bKOREAN\b', r'SAMSUNG', r'LG\s'],
        'FR': [r'\bFRANCE\b', r'\bFRENCH\b', r'\bSA\b'],
        'GB': [r'\bBRITISH\b', r'\bUK\b', r'\bLTD\b', r'UNIVERSITY.*OXFORD|CAMBRIDGE'],
        'CA': [r'\bCANADA\b', r'\bCANADIAN\b'],
        'AU': [r'\bAUSTRALIA\b', r'\bAUSTRALIAN\b'],
        'NL': [r'\bNETHERLANDS\b', r'\bDUTCH\b', r'\bBV\b', r'\bNV\b']
    }
    
    # Organization type patterns
    ORG_TYPE_PATTERNS = {
        'University': [r'UNIVERSITY', r'INSTITUTE.*TECHNOLOGY', r'COLLEGE'],
        'Research Institute': [r'RESEARCH.*INSTITUTE', r'ACADEMY.*SCIENCES', r'LABORATORY'],
        'Corporation': [r'CORPORATION', r'CORP\b', r'INC\b', r'LTD\b', r'GMBH', r'SA\b'],
        'Government': [r'MINISTRY', r'DEPARTMENT', r'GOVERNMENT', r'NATIONAL.*LABORATORY']
    }
    
    # Strategic scoring criteria
    STRATEGIC_CRITERIA = {
        'portfolio_size_weights': {'Emerging': 1, 'Active': 2, 'Major': 3, 'Dominant': 4},
        'market_share_thresholds': {'low': 1.0, 'medium': 5.0, 'high': 15.0},
        'activity_intensity_thresholds': {'low': 2.0, 'medium': 5.0, 'high': 10.0}
    }
    
    def __init__(self, patstat_client: Optional[object] = None):
        """
        Initialize applicant analyzer.
        
        Args:
            patstat_client: PATSTAT client instance for data enrichment
        """
        self.patstat_client = patstat_client
        self.session = None
        self.analyzed_data = None
        self.applicant_data = None
        self.market_intelligence = None
        
        # Initialize PATSTAT connection
        if PATSTAT_AVAILABLE and self.patstat_client is None:
            try:
                self.patstat_client = PatstatClient(environment='PROD')
                logger.debug("✅ Connected to PATSTAT for applicant data enrichment")
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
                    logger.debug("✅ PATSTAT session initialized for applicant analysis")
                elif hasattr(self.patstat_client, 'orm') and callable(self.patstat_client.orm):
                    # Fallback to EPO PatstatClient orm method
                    self.session = self.patstat_client.orm()
                    logger.debug("✅ PATSTAT session initialized for applicant analysis (via orm)")
                else:
                    logger.error("❌ No valid PATSTAT session method found")
                    self.session = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize PATSTAT session: {e}")
        
    def analyze_search_results(self, search_results: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze patent search results to extract applicant intelligence.
        
        Args:
            search_results: DataFrame from PatentSearchProcessor with columns:
                           ['docdb_family_id', 'quality_score', 'match_type', 'earliest_filing_year', etc.]
                           
        Returns:
            Enhanced DataFrame with applicant intelligence
        """
        logger.debug(f"👥 Starting applicant analysis of {len(search_results)} patent families...")
        
        if search_results.empty:
            logger.warning("⚠️ Empty search results provided")
            return pd.DataFrame()
        
        # Step 1: Enrich with applicant data from PATSTAT
        applicant_data = self._enrich_with_applicant_data(search_results)
        
        # Step 2: Aggregate by applicant
        aggregated_data = self._aggregate_by_applicant(applicant_data)
        
        # Step 3: Calculate market intelligence
        enhanced_data = self._calculate_market_intelligence(aggregated_data)
        
        # Step 4: Add strategic insights
        final_data = self._add_strategic_insights(enhanced_data)
        
        self.analyzed_data = final_data
        logger.debug(f"✅ Applicant analysis completed: {len(final_data)} applicants analyzed")
        
        return final_data
    
    def _enrich_with_applicant_data(self, search_results: pd.DataFrame) -> pd.DataFrame:
        """Enrich search results with applicant data from PATSTAT."""
        logger.debug("🔍 Enriching with applicant data from PATSTAT...")
        
        if not self.session:
            logger.warning("⚠️ No PATSTAT session available, using mock data")
            return self._create_mock_applicant_data(search_results)
        
        try:
            # Get applicant data for the family IDs
            family_ids = search_results['docdb_family_id'].tolist()
            
            # Query PATSTAT for applicant information
            applicant_query = self.session.query(
                TLS201_APPLN.docdb_family_id,
                TLS206_PERSON.person_name,
                TLS206_PERSON.person_ctry_code,
                TLS207_PERS_APPLN.applt_seq_nr,
                TLS201_APPLN.appln_filing_date,
                TLS201_APPLN.appln_id
            ).join(
                TLS207_PERS_APPLN, TLS201_APPLN.appln_id == TLS207_PERS_APPLN.appln_id
            ).join(
                TLS206_PERSON, TLS207_PERS_APPLN.person_id == TLS206_PERSON.person_id
            ).filter(
                and_(
                    TLS201_APPLN.docdb_family_id.in_(family_ids),
                    TLS207_PERS_APPLN.applt_seq_nr > 0  # Only applicants, not inventors
                )
            )
            
            applicant_df = pd.read_sql(applicant_query.statement, self.session.bind)
            
            if applicant_df.empty:
                logger.warning("⚠️ No applicant data found in PATSTAT, using mock data")
                return self._create_mock_applicant_data(search_results)
            
            logger.debug(f"✅ Retrieved applicant data for {len(applicant_df)} records")
            
            # Merge with search results
            enriched_data = search_results.merge(
                applicant_df, 
                on='docdb_family_id', 
                how='left'
            )
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"❌ Failed to enrich with PATSTAT applicant data: {e}")
            return self._create_mock_applicant_data(search_results)
    
    def _create_mock_applicant_data(self, search_results: pd.DataFrame) -> pd.DataFrame:
        """Create mock applicant data for testing when PATSTAT is not available."""
        logger.debug("📝 Creating mock applicant data for testing...")
        
        # Mock applicant names based on technology patterns
        mock_applicants = [
            'TOYOTA MOTOR CORP', 'UNIVERSITY OF CALIFORNIA', 'MITSUBISHI MATERIALS CORP',
            'CHINA RARE EARTH HOLDINGS', 'BASF SE', 'SIEMENS AG', 'SAMSUNG SDI CO LTD',
            'PANASONIC CORP', 'GENERAL ELECTRIC CO', 'TSINGHUA UNIVERSITY',
            'MIT', 'STANFORD UNIVERSITY', 'HITACHI LTD', 'SUMITOMO CORP',
            'LYNAS CORP', 'UMICORE SA', 'VAC MAGNETICS CORP'
        ]
        
        mock_countries = ['JP', 'US', 'CN', 'DE', 'KR', 'FR', 'GB', 'AU', 'BE']
        
        # Create mock data
        mock_data = search_results.copy()
        np.random.seed(42)  # For reproducible results
        
        mock_data['person_name'] = np.random.choice(mock_applicants, len(mock_data))
        mock_data['person_ctry_code'] = np.random.choice(mock_countries, len(mock_data))
        mock_data['applt_seq_nr'] = 1  # Primary applicant
        mock_data['appln_filing_date'] = pd.to_datetime('2020-01-01') + pd.to_timedelta(
            np.random.randint(0, 1460, len(mock_data)), unit='D'
        )
        mock_data['appln_id'] = range(100000, 100000 + len(mock_data))
        
        return mock_data
    
    def _aggregate_by_applicant(self, applicant_data: pd.DataFrame) -> pd.DataFrame:
        """Aggregate data by applicant to calculate metrics."""
        logger.debug("📊 Aggregating data by applicant...")
        
        if applicant_data.empty:
            return pd.DataFrame()
        
        # Handle potential column naming issues from merge
        year_col = None
        for col in ['earliest_filing_year_x', 'earliest_filing_year_y', 'earliest_filing_year']:
            if col in applicant_data.columns:
                year_col = col
                break
        
        if year_col is None:
            # Extract year from filing date if available
            if 'appln_filing_date' in applicant_data.columns:
                applicant_data['filing_year'] = pd.to_datetime(applicant_data['appln_filing_date']).dt.year
                year_col = 'filing_year'
            else:
                logger.warning("⚠️ No year column found, using default")
                applicant_data['filing_year'] = 2020
                year_col = 'filing_year'
        
        # Aggregate by applicant
        agg_dict = {
            'docdb_family_id': 'count',
            'quality_score': 'mean',
            year_col: ['min', 'max'],
            'person_ctry_code': 'first'
        }
        
        # Add family_size if available
        if 'family_size' in applicant_data.columns:
            agg_dict['family_size'] = 'sum'
        
        aggregated = applicant_data.groupby('person_name').agg(agg_dict)
        
        # Flatten column names
        if isinstance(aggregated.columns, pd.MultiIndex):
            aggregated.columns = ['_'.join(col).strip() if col[1] else col[0] for col in aggregated.columns]
        
        # Reset index and rename columns
        aggregated = aggregated.reset_index()
        aggregated = aggregated.rename(columns={
            'person_name': 'applicant_name',
            'docdb_family_id_count': 'patent_families',
            'quality_score_mean': 'avg_quality_score',
            'person_ctry_code_first': 'country_code'
        })
        
        # Handle year columns dynamically
        for old_col, new_col in [('min', 'first_filing_year'), ('max', 'latest_filing_year')]:
            year_col_name = None
            for col in aggregated.columns:
                if old_col in col and year_col.split('_')[0] in col:
                    year_col_name = col
                    break
            if year_col_name:
                aggregated = aggregated.rename(columns={year_col_name: new_col})
        
        # Ensure we have the expected columns
        if 'first_filing_year' not in aggregated.columns:
            aggregated['first_filing_year'] = 2020
        if 'latest_filing_year' not in aggregated.columns:
            aggregated['latest_filing_year'] = 2020
        
        return aggregated
    
    def _calculate_market_intelligence(self, aggregated_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate market intelligence metrics."""
        logger.debug("🧠 Calculating market intelligence...")
        
        if aggregated_data.empty:
            return pd.DataFrame()
        
        df = aggregated_data.copy()
        
        # Calculate market share
        total_families = df['patent_families'].sum()
        df['market_share_pct'] = (df['patent_families'] / total_families * 100).round(2)
        
        # Calculate activity metrics
        df['activity_span'] = df['latest_filing_year'] - df['first_filing_year'] + 1
        df['activity_span'] = df['activity_span'].clip(lower=1)  # Minimum 1 year
        df['avg_annual_activity'] = (df['patent_families'] / df['activity_span']).round(1)
        
        # Portfolio size classification
        df['portfolio_size'] = pd.cut(
            df['patent_families'], 
            bins=[0, 5, 20, 50, float('inf')],
            labels=['Emerging', 'Active', 'Major', 'Dominant']
        )
        
        # Market ranking
        df['market_rank'] = df['patent_families'].rank(method='dense', ascending=False).astype(int)
        
        # Geographic intelligence
        df = self._add_geographic_intelligence(df)
        
        # Organization type classification
        df = self._classify_organization_types(df)
        
        return df
    
    def _add_geographic_intelligence(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add geographic intelligence based on applicant names and country codes."""
        logger.debug("🌍 Adding geographic intelligence...")
        
        def identify_country_from_name(applicant_name: str, country_code: str) -> str:
            """Identify likely country based on applicant name patterns."""
            # First try the country code if available
            if pd.notna(country_code) and country_code != '':
                return country_code
            
            if pd.isna(applicant_name):
                return 'UNKNOWN'
            
            name_upper = str(applicant_name).upper()
            
            for country, patterns in self.GEOGRAPHIC_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, name_upper):
                        return country
            return 'OTHER'
        
        df['likely_country'] = df.apply(
            lambda x: identify_country_from_name(x['applicant_name'], x.get('country_code', '')), 
            axis=1
        )
        
        return df
    
    def _classify_organization_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify organization types based on name patterns."""
        logger.debug("🏢 Classifying organization types...")
        
        def classify_org_type(applicant_name: str) -> str:
            """Classify organization type based on name patterns."""
            if pd.isna(applicant_name):
                return 'Unknown'
            
            name_upper = str(applicant_name).upper()
            
            for org_type, patterns in self.ORG_TYPE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, name_upper):
                        return org_type
            return 'Other'
        
        df['organization_type'] = df['applicant_name'].apply(classify_org_type)
        
        return df
    
    def _add_strategic_insights(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add strategic insights and scoring."""
        logger.debug("⚡ Adding strategic insights...")
        
        if df.empty:
            return df
        
        # Strategic scoring based on multiple factors
        df['strategic_score'] = 0
        
        # Portfolio size component (0-40 points)
        portfolio_weights = self.STRATEGIC_CRITERIA['portfolio_size_weights']
        df['portfolio_score'] = df['portfolio_size'].map(portfolio_weights).fillna(1).astype(float) * 10
        df['strategic_score'] += df['portfolio_score']
        
        # Market share component (0-30 points)
        thresholds = self.STRATEGIC_CRITERIA['market_share_thresholds']
        df['market_share_score'] = pd.cut(
            df['market_share_pct'],
            bins=[0, thresholds['low'], thresholds['medium'], thresholds['high'], float('inf')],
            labels=[5, 10, 20, 30]
        ).astype(float).fillna(5)
        df['strategic_score'] += df['market_share_score']
        
        # Activity intensity component (0-20 points)
        activity_thresholds = self.STRATEGIC_CRITERIA['activity_intensity_thresholds']
        df['activity_score'] = pd.cut(
            df['avg_annual_activity'],
            bins=[0, activity_thresholds['low'], activity_thresholds['medium'], activity_thresholds['high'], float('inf')],
            labels=[5, 10, 15, 20]
        ).astype(float).fillna(5)
        df['strategic_score'] += df['activity_score']
        
        # Quality component (0-10 points)
        df['quality_score'] = (df['avg_quality_score'] / 3 * 10).round(1)
        df['strategic_score'] += df['quality_score']
        
        # Strategic category
        df['strategic_category'] = pd.cut(
            df['strategic_score'],
            bins=[0, 30, 60, 80, 100],
            labels=['Emerging', 'Active', 'Strategic', 'Dominant']
        )
        
        # Competitive threat assessment
        df['competitive_threat'] = 'Low'
        df.loc[(df['market_share_pct'] > 5) & (df['avg_annual_activity'] > 3), 'competitive_threat'] = 'Medium'
        df.loc[(df['market_share_pct'] > 10) & (df['avg_annual_activity'] > 5), 'competitive_threat'] = 'High'
        df.loc[df['market_rank'] <= 3, 'competitive_threat'] = 'Critical'
        
        return df
    
    def get_applicant_summary(self) -> Dict[str, any]:
        """Generate summary of applicant analysis results."""
        if self.analyzed_data is None or self.analyzed_data.empty:
            return {
                'status': 'No analysis completed',
                'total_applicants': 0,
                'total_families': 0
            }
        
        df = self.analyzed_data
        
        return {
            'status': 'Analysis completed',
            'total_applicants': len(df),
            'total_families': df['patent_families'].sum(),
            'avg_families_per_applicant': df['patent_families'].mean().round(1),
            'top_applicants': df.nlargest(5, 'patent_families')[['applicant_name', 'patent_families']].to_dict('records'),
            'country_distribution': df['likely_country'].value_counts().head().to_dict(),
            'organization_types': df['organization_type'].value_counts().to_dict(),
            'strategic_categories': df['strategic_category'].value_counts().to_dict(),
            'competitive_threats': df['competitive_threat'].value_counts().to_dict()
        }
    
    def export_applicant_analysis(self, filename: str = None) -> str:
        """Export applicant analysis results."""
        if self.analyzed_data is None or self.analyzed_data.empty:
            raise ValueError("No analysis data available. Run analyze_search_results() first.")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"applicant_analysis_{timestamp}.xlsx"
        
        # Export to Excel with multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main analysis data
            self.analyzed_data.to_excel(writer, sheet_name='Applicant_Analysis', index=False)
            
            # Summary statistics
            summary_df = pd.DataFrame([self.get_applicant_summary()])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Top applicants by various metrics
            top_by_families = self.analyzed_data.nlargest(20, 'patent_families')
            top_by_families.to_excel(writer, sheet_name='Top_By_Families', index=False)
            
            top_by_strategic = self.analyzed_data.nlargest(20, 'strategic_score')
            top_by_strategic.to_excel(writer, sheet_name='Top_Strategic', index=False)
        
        logger.debug(f"✅ Applicant analysis exported to {filename}")
        return filename

def create_applicant_analyzer(patstat_client: Optional[object] = None) -> ApplicantAnalyzer:
    """
    Factory function to create an ApplicantAnalyzer instance.
    
    Args:
        patstat_client: Optional PATSTAT client instance
        
    Returns:
        Configured ApplicantAnalyzer instance
    """
    return ApplicantAnalyzer(patstat_client=patstat_client)