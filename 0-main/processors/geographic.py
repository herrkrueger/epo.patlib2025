"""
Geographic Analysis Processor for REE Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes patent geographic data to generate strategic insights,
competitive landscape analysis, and international filing pattern intelligence.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeographicAnalyzer:
    """
    Comprehensive geographic analysis for patent intelligence with strategic insights.
    """
    
    # Country code to name mapping
    COUNTRY_MAPPING = {
        'CN': 'China', 'US': 'United States', 'JP': 'Japan', 'KR': 'South Korea',
        'DE': 'Germany', 'FR': 'France', 'GB': 'United Kingdom', 'CA': 'Canada',
        'AU': 'Australia', 'IN': 'India', 'RU': 'Russia', 'BR': 'Brazil',
        'IT': 'Italy', 'ES': 'Spain', 'NL': 'Netherlands', 'SE': 'Sweden',
        'CH': 'Switzerland', 'BE': 'Belgium', 'AT': 'Austria', 'NO': 'Norway',
        'DK': 'Denmark', 'FI': 'Finland', 'PT': 'Portugal', 'IE': 'Ireland',
        'TW': 'Taiwan', 'SG': 'Singapore', 'HK': 'Hong Kong', 'MY': 'Malaysia',
        'TH': 'Thailand', 'ID': 'Indonesia', 'PH': 'Philippines', 'VN': 'Vietnam',
        'UNKNOWN': 'Unknown/Missing', '': 'Unknown/Missing'
    }
    
    # ISO country codes for choropleth mapping
    ISO_MAPPING = {
        'China': 'CHN', 'United States': 'USA', 'Japan': 'JPN', 'South Korea': 'KOR',
        'Germany': 'DEU', 'France': 'FRA', 'United Kingdom': 'GBR', 'Canada': 'CAN',
        'Australia': 'AUS', 'India': 'IND', 'Russia': 'RUS', 'Brazil': 'BRA',
        'Italy': 'ITA', 'Spain': 'ESP', 'Netherlands': 'NLD', 'Sweden': 'SWE',
        'Switzerland': 'CHE', 'Belgium': 'BEL', 'Austria': 'AUT', 'Norway': 'NOR',
        'Denmark': 'DNK', 'Finland': 'FIN', 'Portugal': 'PRT', 'Ireland': 'IRL',
        'Taiwan': 'TWN', 'Singapore': 'SGP', 'Hong Kong': 'HKG', 'Malaysia': 'MYS',
        'Thailand': 'THA', 'Indonesia': 'IDN', 'Philippines': 'PHL', 'Vietnam': 'VNM'
    }
    
    # Regional groupings for strategic analysis
    REGIONAL_GROUPS = {
        'East Asia': ['China', 'Japan', 'South Korea', 'Taiwan', 'Hong Kong'],
        'North America': ['United States', 'Canada'],
        'Europe': ['Germany', 'France', 'United Kingdom', 'Italy', 'Spain', 'Netherlands', 
                  'Sweden', 'Switzerland', 'Belgium', 'Austria', 'Norway', 'Denmark', 
                  'Finland', 'Portugal', 'Ireland'],
        'Southeast Asia': ['Singapore', 'Malaysia', 'Thailand', 'Indonesia', 'Philippines', 'Vietnam'],
        'Oceania': ['Australia'],
        'Other': ['India', 'Russia', 'Brazil']
    }
    
    def __init__(self):
        """Initialize geographic analyzer."""
        self.analyzed_data = None
        self.geographic_intelligence = None
    
    def analyze_geographic_patterns(self, patent_data: pd.DataFrame,
                                  country_col: str = 'country_code',
                                  family_col: str = 'docdb_family_id',
                                  family_size_col: str = 'docdb_family_size',
                                  year_col: str = 'earliest_filing_year') -> pd.DataFrame:
        """
        Comprehensive geographic analysis of patent filing patterns.
        
        Args:
            patent_data: DataFrame with patent geographic data
            country_col: Column name for country codes
            family_col: Column name for patent family IDs
            family_size_col: Column name for family sizes
            year_col: Column name for filing years
            
        Returns:
            Enhanced DataFrame with geographic intelligence
        """
        logger.info("🌍 Starting comprehensive geographic analysis...")
        
        df = patent_data.copy()
        
        # Validate required columns
        required_cols = [country_col, family_col, year_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean and standardize geographic data
        df = self._clean_geographic_data(df, country_col)
        
        # Add geographic metadata
        df = self._add_geographic_metadata(df, country_col)
        
        # Calculate strategic filing patterns
        df = self._analyze_filing_strategies(df, family_size_col)
        
        # Add temporal analysis
        df = self._add_temporal_patterns(df, year_col)
        
        # Calculate competitive positioning
        df = self._calculate_geographic_competitiveness(df, family_col)
        
        self.analyzed_data = df
        logger.info(f"✅ Geographic analysis complete for {len(df)} records")
        
        return df
    
    def _clean_geographic_data(self, df: pd.DataFrame, country_col: str) -> pd.DataFrame:
        """Clean and standardize geographic data."""
        logger.info("🧹 Cleaning geographic data...")
        
        # Handle missing values
        df[country_col] = df[country_col].fillna('UNKNOWN')
        df[country_col] = df[country_col].replace('', 'UNKNOWN')
        
        # Standardize country codes
        df[country_col] = df[country_col].str.upper().str.strip()
        
        # Map to country names
        df['country_name'] = df[country_col].map(self.COUNTRY_MAPPING).fillna(df[country_col])
        
        # Add ISO codes for mapping
        df['iso_country_code'] = df['country_name'].map(self.ISO_MAPPING)
        
        return df
    
    def _add_geographic_metadata(self, df: pd.DataFrame, country_col: str) -> pd.DataFrame:
        """Add geographic metadata and regional groupings."""
        logger.info("🗺️ Adding geographic metadata...")
        
        # Add regional groupings
        def assign_region(country_name: str) -> str:
            for region, countries in self.REGIONAL_GROUPS.items():
                if country_name in countries:
                    return region
            return 'Other'
        
        df['region'] = df['country_name'].apply(assign_region)
        
        # Economic development classification
        developed_countries = [
            'United States', 'Japan', 'Germany', 'France', 'United Kingdom',
            'Canada', 'Australia', 'Italy', 'Spain', 'Netherlands', 'Sweden',
            'Switzerland', 'Belgium', 'Austria', 'Norway', 'Denmark', 'Finland'
        ]
        
        emerging_markets = [
            'China', 'South Korea', 'Taiwan', 'Singapore', 'Hong Kong'
        ]
        
        def classify_economy(country_name: str) -> str:
            if country_name in developed_countries:
                return 'Developed'
            elif country_name in emerging_markets:
                return 'Emerging'
            else:
                return 'Developing'
        
        df['economy_type'] = df['country_name'].apply(classify_economy)
        
        return df
    
    def _analyze_filing_strategies(self, df: pd.DataFrame, family_size_col: str) -> pd.DataFrame:
        """Analyze strategic filing patterns based on family sizes."""
        logger.info("🎯 Analyzing filing strategies...")
        
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
        logger.info("📅 Adding temporal patterns...")
        
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
        logger.info("🏆 Calculating geographic competitiveness...")
        
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
        
        logger.info("📋 Generating geographic intelligence summary...")
        
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
        
        logger.info("📈 Analyzing filing evolution over time...")
        
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
        logger.info(f"📊 Processing {len(raw_data)} raw geographic records...")
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data, columns=[
            'docdb_family_id', 'docdb_family_size', 'earliest_filing_year',
            'country_code', 'applicant_name', 'applt_seq_nr'
        ])
        
        # Data cleaning
        df = self._clean_geographic_fields(df)
        df = self._validate_data_quality(df)
        df = self._remove_duplicates(df)
        
        logger.info(f"✅ Processed to {len(df)} clean geographic records")
        self.processed_data = df
        
        return df
    
    def _clean_geographic_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean geographic-specific fields."""
        logger.info("🧹 Cleaning geographic fields...")
        
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
        logger.info("🔍 Validating data quality...")
        
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
            logger.info(f"📊 Removed {removed_count} invalid records")
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records."""
        logger.info("🔍 Removing duplicates...")
        
        # Remove exact duplicates
        initial_count = len(df)
        df = df.drop_duplicates().copy()
        
        # Remove duplicates based on family_id and country (keep first occurrence)
        df = df.drop_duplicates(subset=['docdb_family_id', 'country_code']).copy()
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"📊 Removed {removed_count} duplicate records")
        
        return df

def create_geographic_analyzer() -> GeographicAnalyzer:
    """
    Factory function to create configured geographic analyzer.
    
    Returns:
        Configured GeographicAnalyzer instance
    """
    return GeographicAnalyzer()

def create_geographic_processor() -> GeographicDataProcessor:
    """
    Factory function to create configured geographic data processor.
    
    Returns:
        Configured GeographicDataProcessor instance
    """
    return GeographicDataProcessor()

# Example usage and demo functions
def demo_geographic_analysis():
    """Demonstrate geographic analysis capabilities."""
    logger.info("🚀 Geographic Analysis Demo")
    
    # Create sample data
    np.random.seed(42)
    sample_data = []
    
    countries = ['CN', 'US', 'JP', 'DE', 'KR', 'FR', 'GB', 'CA']
    applicants = ['UNIV TECH', 'CORP INC', 'INST SCI', 'LAB RES']
    
    for i in range(100):
        family_id = 100000 + i
        family_size = np.random.randint(1, 20)
        filing_year = np.random.randint(2010, 2023)
        country = np.random.choice(countries)
        applicant = f"{np.random.choice(applicants)} {i}"
        
        sample_data.append((family_id, family_size, filing_year, country, applicant, 1))
    
    # Process data
    processor = create_geographic_processor()
    df = processor.process_patstat_geographic_data(sample_data)
    
    # Analyze geographic patterns
    analyzer = create_geographic_analyzer()
    analyzed_df = analyzer.analyze_geographic_patterns(df)
    
    # Generate insights
    summary = analyzer.generate_geographic_summary()
    landscape = analyzer.get_competitive_landscape_by_region()
    evolution = analyzer.analyze_filing_evolution()
    
    logger.info("✅ Demo analysis complete")
    logger.info(f"🌍 Dominant country: {summary['overview']['dominant_country']}")
    logger.info(f"🏆 Total countries analyzed: {summary['overview']['total_countries']}")
    
    return analyzer, analyzed_df, summary

if __name__ == "__main__":
    demo_geographic_analysis()