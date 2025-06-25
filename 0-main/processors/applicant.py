"""
Applicant Analysis Processor for REE Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes patent applicant data to generate market intelligence,
competitive analysis, and strategic insights for rare earth elements patents.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import re
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApplicantAnalyzer:
    """
    Comprehensive applicant analysis for patent intelligence with market insights.
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
    
    def __init__(self):
        """Initialize applicant analyzer."""
        self.analyzed_data = None
        self.market_intelligence = None
    
    def analyze_applicants(self, patent_data: pd.DataFrame, 
                          applicant_col: str = 'Applicant',
                          family_col: str = 'Patent_Families',
                          min_year_col: str = 'First_Year',
                          max_year_col: str = 'Latest_Year') -> pd.DataFrame:
        """
        Comprehensive applicant analysis with market intelligence.
        
        Args:
            patent_data: DataFrame with applicant patent data
            applicant_col: Column name for applicant names
            family_col: Column name for patent family counts
            min_year_col: Column name for first filing year
            max_year_col: Column name for latest filing year
            
        Returns:
            Enhanced DataFrame with market intelligence metrics
        """
        logger.info("🔍 Starting comprehensive applicant analysis...")
        
        df = patent_data.copy()
        
        # Validate required columns
        required_cols = [applicant_col, family_col, min_year_col, max_year_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Calculate market intelligence metrics
        df = self._calculate_market_metrics(df, applicant_col, family_col, min_year_col, max_year_col)
        
        # Add geographic intelligence
        df = self._add_geographic_intelligence(df, applicant_col)
        
        # Add organization type classification
        df = self._classify_organization_types(df, applicant_col)
        
        # Calculate competitive positioning
        df = self._calculate_competitive_positioning(df, family_col)
        
        # Add strategic insights
        df = self._add_strategic_insights(df, family_col, min_year_col, max_year_col)
        
        self.analyzed_data = df
        logger.info(f"✅ Analysis complete for {len(df)} applicants")
        
        return df
    
    def _calculate_market_metrics(self, df: pd.DataFrame, applicant_col: str, 
                                 family_col: str, min_year_col: str, max_year_col: str) -> pd.DataFrame:
        """Calculate market share and activity metrics."""
        logger.info("📊 Calculating market metrics...")
        
        # Market share calculation
        total_families = df[family_col].sum()
        df['Market_Share_Pct'] = (df[family_col] / total_families * 100).round(2)
        
        # Activity span and intensity
        df['Activity_Span'] = df[max_year_col] - df[min_year_col] + 1
        df['Avg_Annual_Activity'] = (df[family_col] / df['Activity_Span']).round(1)
        
        # Portfolio classification
        df['Portfolio_Size'] = pd.cut(
            df[family_col], 
            bins=[0, 5, 20, 50, float('inf')],
            labels=['Emerging', 'Active', 'Major', 'Dominant']
        )
        
        # Calculate relative market position
        df['Market_Rank'] = df[family_col].rank(method='dense', ascending=False).astype(int)
        
        return df
    
    def _add_geographic_intelligence(self, df: pd.DataFrame, applicant_col: str) -> pd.DataFrame:
        """Add geographic intelligence based on applicant names."""
        logger.info("🌍 Adding geographic intelligence...")
        
        def identify_country(applicant_name: str) -> str:
            """Identify likely country based on applicant name patterns."""
            if pd.isna(applicant_name):
                return 'UNKNOWN'
            
            name_upper = str(applicant_name).upper()
            
            for country, patterns in self.GEOGRAPHIC_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, name_upper):
                        return country
            return 'OTHER'
        
        df['Likely_Country'] = df[applicant_col].apply(identify_country)
        
        # Calculate geographic market share
        country_stats = df.groupby('Likely_Country').agg({
            'Patent_Families': 'sum',
            'Market_Share_Pct': 'sum',
            applicant_col: 'count'
        }).rename(columns={applicant_col: 'Applicant_Count'})
        
        df = df.merge(
            country_stats.add_suffix('_Country_Total'),
            left_on='Likely_Country',
            right_index=True,
            how='left'
        )
        
        return df
    
    def _classify_organization_types(self, df: pd.DataFrame, applicant_col: str) -> pd.DataFrame:
        """Classify organizations by type (University, Corporation, etc.)."""
        logger.info("🏢 Classifying organization types...")
        
        def classify_organization(applicant_name: str) -> str:
            """Classify organization type based on name patterns."""
            if pd.isna(applicant_name):
                return 'Unknown'
            
            name_upper = str(applicant_name).upper()
            
            for org_type, patterns in self.ORG_TYPE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, name_upper):
                        return org_type
            return 'Other'
        
        df['Organization_Type'] = df[applicant_col].apply(classify_organization)
        
        return df
    
    def _calculate_competitive_positioning(self, df: pd.DataFrame, family_col: str) -> pd.DataFrame:
        """Calculate competitive positioning metrics."""
        logger.info("🎯 Calculating competitive positioning...")
        
        # Competitive tier classification
        q1 = df[family_col].quantile(0.75)
        q2 = df[family_col].quantile(0.5)
        q3 = df[family_col].quantile(0.25)
        
        def assign_tier(patents: int) -> str:
            if patents >= q1:
                return 'Tier 1 (Leaders)'
            elif patents >= q2:
                return 'Tier 2 (Challengers)'
            elif patents >= q3:
                return 'Tier 3 (Followers)'
            else:
                return 'Tier 4 (Niche)'
        
        df['Competitive_Tier'] = df[family_col].apply(assign_tier)
        
        # Market concentration analysis
        cumulative_share = df.sort_values(family_col, ascending=False)['Market_Share_Pct'].cumsum()
        
        # Find HHI-style concentration
        hhi = (df['Market_Share_Pct'] ** 2).sum()
        df['Market_Concentration_HHI'] = hhi
        
        return df
    
    def _add_strategic_insights(self, df: pd.DataFrame, family_col: str, 
                              min_year_col: str, max_year_col: str) -> pd.DataFrame:
        """Add strategic insights and trend indicators."""
        logger.info("💡 Adding strategic insights...")
        
        # Innovation consistency (low variance in activity indicates consistency)
        df['Innovation_Consistency'] = df['Activity_Span'].apply(
            lambda span: 'Consistent' if span > 5 else 'Sporadic'
        )
        
        # Strategic positioning based on multiple factors
        def calculate_strategic_score(row):
            score = 0
            # Portfolio size weight
            if row[family_col] > 50:
                score += 4
            elif row[family_col] > 20:
                score += 3
            elif row[family_col] > 5:
                score += 2
            else:
                score += 1
            
            # Activity span weight
            if row['Activity_Span'] > 10:
                score += 2
            elif row['Activity_Span'] > 5:
                score += 1
            
            # Consistency weight
            if row['Avg_Annual_Activity'] > 5:
                score += 1
            
            return score
        
        df['Strategic_Score'] = df.apply(calculate_strategic_score, axis=1)
        
        # Strategic category
        def assign_strategic_category(score: int) -> str:
            if score >= 6:
                return 'Strategic Leader'
            elif score >= 4:
                return 'Key Player'
            elif score >= 2:
                return 'Active Participant'
            else:
                return 'Emerging Player'
        
        df['Strategic_Category'] = df['Strategic_Score'].apply(assign_strategic_category)
        
        return df
    
    def generate_market_intelligence_summary(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive market intelligence summary.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with market intelligence insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_applicants first.")
        
        logger.info("📋 Generating market intelligence summary...")
        
        total_families = df['Patent_Families'].sum()
        top_applicant = df.iloc[0] if len(df) > 0 else None
        
        summary = {
            'market_overview': {
                'total_patent_families': int(total_families),
                'total_applicants': len(df),
                'market_leader': top_applicant['Applicant'] if top_applicant is not None else 'N/A',
                'leader_market_share': float(top_applicant['Market_Share_Pct']) if top_applicant is not None else 0,
                'top_10_concentration': float(df.head(10)['Market_Share_Pct'].sum()),
                'hhi_concentration': float(df['Market_Concentration_HHI'].iloc[0]) if len(df) > 0 else 0
            },
            'geographic_distribution': df['Likely_Country'].value_counts().head(10).to_dict(),
            'organization_types': df['Organization_Type'].value_counts().to_dict(),
            'competitive_tiers': df['Competitive_Tier'].value_counts().to_dict(),
            'strategic_categories': df['Strategic_Category'].value_counts().to_dict(),
            'activity_insights': {
                'avg_portfolio_size': float(df['Patent_Families'].mean()),
                'avg_activity_span': float(df['Activity_Span'].mean()),
                'consistent_innovators': len(df[df['Innovation_Consistency'] == 'Consistent']),
                'strategic_leaders': len(df[df['Strategic_Category'] == 'Strategic Leader'])
            },
            'key_metrics': {
                'major_players': len(df[df['Patent_Families'] > 5]),
                'emerging_players': len(df[df['Portfolio_Size'] == 'Emerging']),
                'sustained_rd': len(df[df['Activity_Span'] > 10]),
                'high_intensity': len(df[df['Avg_Annual_Activity'] > 5])
            }
        }
        
        self.market_intelligence = summary
        return summary
    
    def get_top_applicants(self, df: Optional[pd.DataFrame] = None, 
                          top_n: int = 20, 
                          min_patents: int = 1) -> pd.DataFrame:
        """
        Get top applicants with filtering options.
        
        Args:
            df: DataFrame to filter (uses self.analyzed_data if None)
            top_n: Number of top applicants to return
            min_patents: Minimum number of patents required
            
        Returns:
            Filtered DataFrame with top applicants
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_applicants first.")
        
        filtered_df = df[df['Patent_Families'] >= min_patents].copy()
        return filtered_df.head(top_n)
    
    def get_competitive_landscape(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Get competitive landscape analysis.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with competitive landscape insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_applicants first.")
        
        # Leaders, challengers, followers analysis
        tier_analysis = {}
        for tier in df['Competitive_Tier'].unique():
            tier_data = df[df['Competitive_Tier'] == tier]
            tier_analysis[tier] = {
                'count': len(tier_data),
                'total_patents': int(tier_data['Patent_Families'].sum()),
                'market_share': float(tier_data['Market_Share_Pct'].sum()),
                'avg_patents': float(tier_data['Patent_Families'].mean()),
                'top_players': tier_data.head(3)['Applicant'].tolist()
            }
        
        # Geographic competition
        geo_competition = {}
        for country in df['Likely_Country'].value_counts().head(5).index:
            country_data = df[df['Likely_Country'] == country]
            geo_competition[country] = {
                'applicants': len(country_data),
                'total_patents': int(country_data['Patent_Families'].sum()),
                'market_share': float(country_data['Market_Share_Pct'].sum()),
                'top_player': country_data.iloc[0]['Applicant'] if len(country_data) > 0 else 'N/A'
            }
        
        return {
            'tier_analysis': tier_analysis,
            'geographic_competition': geo_competition,
            'market_concentration': {
                'hhi': float(df['Market_Concentration_HHI'].iloc[0]) if len(df) > 0 else 0,
                'top_5_share': float(df.head(5)['Market_Share_Pct'].sum()),
                'top_10_share': float(df.head(10)['Market_Share_Pct'].sum())
            }
        }

class ApplicantDataProcessor:
    """
    Data processor for cleaning and preparing applicant data from various sources.
    """
    
    def __init__(self):
        """Initialize data processor."""
        self.processed_data = None
    
    def process_patstat_applicant_data(self, raw_data: List[Tuple]) -> pd.DataFrame:
        """
        Process raw PATSTAT applicant query results.
        
        Args:
            raw_data: Raw query results from PATSTAT
            
        Returns:
            Processed DataFrame ready for analysis
        """
        logger.info(f"📊 Processing {len(raw_data)} raw applicant records...")
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data, columns=[
            'Applicant', 'Patent_Families', 'First_Year', 'Latest_Year'
        ])
        
        # Data cleaning
        df = self._clean_applicant_names(df)
        df = self._validate_years(df)
        df = self._remove_duplicates(df)
        
        # Sort by patent families descending
        df = df.sort_values('Patent_Families', ascending=False).reset_index(drop=True)
        
        logger.info(f"✅ Processed to {len(df)} clean applicant records")
        self.processed_data = df
        
        return df
    
    def _clean_applicant_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize applicant names."""
        logger.info("🧹 Cleaning applicant names...")
        
        # Remove empty or null names
        df = df[df['Applicant'].notna()].copy()
        df = df[df['Applicant'].str.strip() != ''].copy()
        
        # Standardize names
        df['Applicant'] = df['Applicant'].str.strip()
        df['Applicant'] = df['Applicant'].str.upper()
        
        # Remove excessive whitespace
        df['Applicant'] = df['Applicant'].str.replace(r'\s+', ' ', regex=True)
        
        return df
    
    def _validate_years(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean year data."""
        logger.info("📅 Validating year data...")
        
        current_year = datetime.now().year
        
        # Remove records with invalid years
        df = df[df['First_Year'].between(1980, current_year)].copy()
        df = df[df['Latest_Year'].between(1980, current_year)].copy()
        
        # Ensure First_Year <= Latest_Year
        df = df[df['First_Year'] <= df['Latest_Year']].copy()
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate applicants and merge similar entries."""
        logger.info("🔍 Removing duplicates...")
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['Applicant']).copy()
        
        # Group by applicant and aggregate (in case of processing errors)
        df_grouped = df.groupby('Applicant').agg({
            'Patent_Families': 'sum',
            'First_Year': 'min',
            'Latest_Year': 'max'
        }).reset_index()
        
        return df_grouped

def create_applicant_analyzer() -> ApplicantAnalyzer:
    """
    Factory function to create configured applicant analyzer.
    
    Returns:
        Configured ApplicantAnalyzer instance
    """
    return ApplicantAnalyzer()

def create_applicant_processor() -> ApplicantDataProcessor:
    """
    Factory function to create configured applicant data processor.
    
    Returns:
        Configured ApplicantDataProcessor instance
    """
    return ApplicantDataProcessor()

# Example usage and demo functions
def demo_applicant_analysis():
    """Demonstrate applicant analysis capabilities."""
    logger.info("🚀 Applicant Analysis Demo")
    
    # Create sample data
    np.random.seed(42)
    sample_data = []
    
    companies = [
        'JIANGXI UNIVERSITY OF SCIENCE AND TECHNOLOGY',
        'HITACHI METALS',
        'CHINESE ACADEMY OF SCIENCES',
        'SONY CORPORATION',
        'SIEMENS AG',
        'MASSACHUSETTS INSTITUTE OF TECHNOLOGY',
        'UNIVERSITY OF CALIFORNIA'
    ]
    
    for i, company in enumerate(companies):
        patents = np.random.randint(5, 60)
        first_year = np.random.randint(2010, 2018)
        latest_year = np.random.randint(first_year, 2023)
        
        sample_data.append((company, patents, first_year, latest_year))
    
    # Process data
    processor = create_applicant_processor()
    df = processor.process_patstat_applicant_data(sample_data)
    
    # Analyze applicants
    analyzer = create_applicant_analyzer()
    analyzed_df = analyzer.analyze_applicants(df)
    
    # Generate insights
    summary = analyzer.generate_market_intelligence_summary()
    landscape = analyzer.get_competitive_landscape()
    
    logger.info("✅ Demo analysis complete")
    logger.info(f"📊 Market leader: {summary['market_overview']['market_leader']}")
    logger.info(f"🌍 Geographic distribution: {list(summary['geographic_distribution'].keys())[:3]}")
    
    return analyzer, analyzed_df, summary

if __name__ == "__main__":
    demo_applicant_analysis()