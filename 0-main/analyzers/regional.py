"""
Regional Analysis Module for REE Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive regional analysis capabilities for patent data,
including competitive intelligence, market dynamics, and strategic positioning analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegionalAnalyzer:
    """
    Comprehensive regional analysis for patent intelligence with strategic insights.
    """
    
    # Regional definitions and economic classifications
    REGIONAL_DEFINITIONS = {
        'East Asia': {
            'countries': ['China', 'Japan', 'South Korea', 'Taiwan', 'Hong Kong'],
            'economic_status': 'Mixed (Developed/Emerging)',
            'key_strengths': ['Manufacturing', 'Electronics', 'Advanced Materials'],
            'ree_relevance': 'Critical - Major REE consumers and processors'
        },
        'North America': {
            'countries': ['United States', 'Canada'],
            'economic_status': 'Developed',
            'key_strengths': ['Technology Innovation', 'Research Infrastructure'],
            'ree_relevance': 'Strategic - Defense and clean energy applications'
        },
        'Europe': {
            'countries': ['Germany', 'France', 'United Kingdom', 'Italy', 'Spain', 
                         'Netherlands', 'Sweden', 'Switzerland', 'Belgium', 'Austria', 
                         'Norway', 'Denmark', 'Finland', 'Portugal', 'Ireland'],
            'economic_status': 'Developed',
            'key_strengths': ['Automotive', 'Renewable Energy', 'Chemical Industry'],
            'ree_relevance': 'Growing - Green transition driving demand'
        },
        'Southeast Asia': {
            'countries': ['Singapore', 'Malaysia', 'Thailand', 'Indonesia', 'Philippines', 'Vietnam'],
            'economic_status': 'Emerging',
            'key_strengths': ['Electronics Manufacturing', 'Raw Materials'],
            'ree_relevance': 'Emerging - Growing electronics sector'
        },
        'Oceania': {
            'countries': ['Australia'],
            'economic_status': 'Developed',
            'key_strengths': ['Mining', 'Raw Materials'],
            'ree_relevance': 'Strategic - Significant REE reserves'
        },
        'Other': {
            'countries': ['India', 'Russia', 'Brazil', 'South Africa'],
            'economic_status': 'Mixed',
            'key_strengths': ['Diverse Industrial Base'],
            'ree_relevance': 'Variable - Some mining potential'
        }
    }
    
    # Market development stages
    MARKET_STAGES = {
        'Pioneer': {'min_years': 0, 'max_years': 3, 'characteristics': 'Early stage, experimental'},
        'Growth': {'min_years': 4, 'max_years': 8, 'characteristics': 'Rapid expansion, increasing activity'},
        'Mature': {'min_years': 9, 'max_years': 15, 'characteristics': 'Established presence, stable growth'},
        'Advanced': {'min_years': 16, 'max_years': 999, 'characteristics': 'Long-term leader, sophisticated strategies'}
    }
    
    def __init__(self):
        """Initialize regional analyzer."""
        self.analyzed_data = None
        self.regional_intelligence = None
        self.competitive_matrix = None
    
    def analyze_regional_dynamics(self, patent_data: pd.DataFrame,
                                region_col: str = 'region',
                                country_col: str = 'country_name', 
                                family_col: str = 'docdb_family_id',
                                year_col: str = 'earliest_filing_year',
                                family_size_col: str = 'docdb_family_size') -> pd.DataFrame:
        """
        Comprehensive regional dynamics analysis with competitive intelligence.
        
        Args:
            patent_data: DataFrame with regional patent data
            region_col: Column name for regions
            country_col: Column name for countries
            family_col: Column name for patent family IDs
            year_col: Column name for filing years
            family_size_col: Column name for family sizes
            
        Returns:
            Enhanced DataFrame with regional intelligence
        """
        logger.debug("🌍 Starting comprehensive regional dynamics analysis...")
        
        df = patent_data.copy()
        
        # Validate required columns
        required_cols = [region_col, country_col, family_col, year_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Calculate regional metrics
        df = self._calculate_regional_metrics(df, region_col, country_col, family_col, year_col)
        
        # Add market development analysis
        df = self._analyze_market_development(df, region_col, year_col)
        
        # Calculate competitive positioning
        df = self._calculate_regional_competitiveness(df, region_col, family_col, family_size_col)
        
        # Add strategic analysis
        df = self._add_strategic_insights(df, region_col, family_size_col)
        
        # Calculate innovation intensity
        df = self._calculate_innovation_intensity(df, region_col, year_col, family_col)
        
        self.analyzed_data = df
        logger.debug(f"✅ Regional analysis complete for {len(df)} records")
        
        return df
    
    def _calculate_regional_metrics(self, df: pd.DataFrame, region_col: str, 
                                  country_col: str, family_col: str, year_col: str) -> pd.DataFrame:
        """Calculate comprehensive regional metrics."""
        logger.debug("📊 Calculating regional metrics...")
        
        # Regional summary statistics
        regional_stats = df.groupby(region_col).agg({
            family_col: 'nunique',
            country_col: 'nunique',
            year_col: ['min', 'max', 'count']
        }).round(2)
        
        regional_stats.columns = ['unique_families', 'active_countries', 'first_year', 'latest_year', 'total_records']
        
        # Calculate market share
        total_families = regional_stats['unique_families'].sum()
        regional_stats['market_share_pct'] = (regional_stats['unique_families'] / total_families * 100).round(2)
        
        # Calculate activity span
        regional_stats['activity_span'] = regional_stats['latest_year'] - regional_stats['first_year'] + 1
        
        # Average annual activity
        regional_stats['avg_annual_activity'] = (regional_stats['unique_families'] / regional_stats['activity_span']).round(1)
        
        # Merge back to main dataframe
        df = df.merge(
            regional_stats.add_suffix('_regional'),
            left_on=region_col,
            right_index=True,
            how='left'
        )
        
        return df
    
    def _analyze_market_development(self, df: pd.DataFrame, region_col: str, year_col: str) -> pd.DataFrame:
        """Analyze market development stages by region."""
        logger.debug("📈 Analyzing market development stages...")
        
        # Calculate market maturity based on activity span
        def assign_market_stage(activity_span: int) -> str:
            for stage, criteria in self.MARKET_STAGES.items():
                if criteria['min_years'] <= activity_span <= criteria['max_years']:
                    return stage
            return 'Advanced'
        
        df['market_stage'] = df['activity_span_regional'].apply(assign_market_stage)
        
        # Add development characteristics
        stage_characteristics = {stage: info['characteristics'] for stage, info in self.MARKET_STAGES.items()}
        df['stage_characteristics'] = df['market_stage'].map(stage_characteristics)
        
        # Calculate market momentum (recent vs historical activity)
        current_year = datetime.now().year
        recent_threshold = current_year - 3
        
        def calculate_momentum(group):
            recent_activity = len(group[group[year_col] >= recent_threshold])
            total_activity = len(group)
            return recent_activity / total_activity if total_activity > 0 else 0
        
        momentum_by_region = df.groupby(region_col).apply(calculate_momentum)
        df['regional_momentum'] = df[region_col].map(momentum_by_region)
        
        # Classify momentum
        df['momentum_classification'] = pd.cut(
            df['regional_momentum'],
            bins=[0, 0.2, 0.4, 0.6, 1.0],
            labels=['Declining', 'Stable', 'Growing', 'Accelerating']
        )
        
        return df
    
    def _calculate_regional_competitiveness(self, df: pd.DataFrame, region_col: str, 
                                          family_col: str, family_size_col: str) -> pd.DataFrame:
        """Calculate regional competitive positioning."""
        logger.debug("🏆 Calculating regional competitiveness...")
        
        # Competitive tier based on market share
        market_share_tiers = {
            'Market Leader': (15, float('inf')),
            'Major Player': (5, 15),
            'Active Participant': (1, 5),
            'Niche Player': (0, 1)
        }
        
        def assign_competitive_tier(market_share: float) -> str:
            for tier, (min_share, max_share) in market_share_tiers.items():
                if min_share <= market_share < max_share:
                    return tier
            return 'Niche Player'
        
        df['competitive_tier'] = df['market_share_pct_regional'].apply(assign_competitive_tier)
        
        # Strategic filing intensity (if family size data available)
        if family_size_col in df.columns:
            regional_strategy = df.groupby(region_col)[family_size_col].agg(['mean', 'median', 'std']).round(2)
            regional_strategy.columns = ['avg_family_size', 'median_family_size', 'family_size_variance']
            
            # Strategic classification based on family size patterns
            def classify_filing_strategy(avg_size: float, variance: float) -> str:
                if avg_size >= 10:
                    return 'Global Strategy'
                elif avg_size >= 5:
                    return 'Regional Strategy'
                elif variance > avg_size:
                    return 'Mixed Strategy'
                else:
                    return 'Domestic Focus'
            
            regional_strategy['regional_filing_strategy'] = regional_strategy.apply(
                lambda row: classify_filing_strategy(row['avg_family_size'], row['family_size_variance']), 
                axis=1
            )
            
            df = df.merge(
                regional_strategy,
                left_on=region_col,
                right_index=True,
                how='left'
            )
        
        return df
    
    def _add_strategic_insights(self, df: pd.DataFrame, region_col: str, family_size_col: str) -> pd.DataFrame:
        """Add strategic insights and intelligence."""
        logger.debug("💡 Adding strategic insights...")
        
        # Regional strengths from predefined knowledge
        region_strengths = {region: info['key_strengths'] for region, info in self.REGIONAL_DEFINITIONS.items()}
        df['regional_strengths'] = df[region_col].map(region_strengths)
        
        # REE relevance assessment
        ree_relevance = {region: info['ree_relevance'] for region, info in self.REGIONAL_DEFINITIONS.items()}
        df['ree_relevance'] = df[region_col].map(ree_relevance)
        
        # Economic development level
        economic_status = {region: info['economic_status'] for region, info in self.REGIONAL_DEFINITIONS.items()}
        df['economic_status'] = df[region_col].map(economic_status)
        
        # Strategic priority calculation
        def calculate_strategic_priority(row):
            score = 0
            
            # Market share weight
            if row['market_share_pct_regional'] >= 15:
                score += 4
            elif row['market_share_pct_regional'] >= 5:
                score += 3
            elif row['market_share_pct_regional'] >= 1:
                score += 2
            else:
                score += 1
            
            # Activity span weight
            if row['activity_span_regional'] >= 15:
                score += 3
            elif row['activity_span_regional'] >= 10:
                score += 2
            else:
                score += 1
            
            # Momentum weight
            if row['regional_momentum'] >= 0.6:
                score += 2
            elif row['regional_momentum'] >= 0.4:
                score += 1
            
            return score
        
        df['strategic_priority_score'] = df.apply(calculate_strategic_priority, axis=1)
        
        # Strategic priority classification
        df['strategic_priority'] = pd.cut(
            df['strategic_priority_score'],
            bins=[0, 4, 6, 8, 10],
            labels=['Monitor', 'Watch', 'Priority', 'Critical']
        )
        
        return df
    
    def _calculate_innovation_intensity(self, df: pd.DataFrame, region_col: str, 
                                      year_col: str, family_col: str) -> pd.DataFrame:
        """Calculate innovation intensity metrics."""
        logger.debug("🔬 Calculating innovation intensity...")
        
        # Innovation density (patents per year per active country)
        innovation_metrics = df.groupby(region_col).apply(
            lambda group: pd.Series({
                'innovation_density': group[family_col].nunique() / (group['active_countries_regional'].iloc[0] * group['activity_span_regional'].iloc[0]),
                'innovation_consistency': group.groupby(year_col)[family_col].nunique().std() / group.groupby(year_col)[family_col].nunique().mean() if len(group.groupby(year_col)) > 1 else 0,
                'innovation_acceleration': self._calculate_acceleration(group, year_col, family_col)
            })
        ).round(3)
        
        df = df.merge(
            innovation_metrics,
            left_on=region_col,
            right_index=True,
            how='left'
        )
        
        # Innovation intensity classification
        df['innovation_intensity'] = pd.cut(
            df['innovation_density'],
            bins=[0, 0.1, 0.5, 1.0, float('inf')],
            labels=['Low', 'Moderate', 'High', 'Very High']
        )
        
        return df
    
    def _calculate_acceleration(self, group: pd.DataFrame, year_col: str, family_col: str) -> float:
        """Calculate innovation acceleration for a regional group."""
        yearly_counts = group.groupby(year_col)[family_col].nunique().sort_index()
        
        if len(yearly_counts) < 3:
            return 0.0
        
        # Simple acceleration: compare first and last third of timeline
        split_point = len(yearly_counts) // 3
        early_avg = yearly_counts.iloc[:split_point].mean()
        late_avg = yearly_counts.iloc[-split_point:].mean()
        
        return (late_avg - early_avg) / early_avg if early_avg > 0 else 0.0
    
    def generate_regional_intelligence_report(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive regional intelligence report.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with regional intelligence insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_regional_dynamics first.")
        
        logger.debug("📋 Generating regional intelligence report...")
        
        # Regional overview
        regional_overview = df.groupby('region').agg({
            'unique_families_regional': 'first',
            'market_share_pct_regional': 'first',
            'active_countries_regional': 'first',
            'activity_span_regional': 'first',
            'regional_momentum': 'first',
            'strategic_priority_score': 'first'
        }).round(2)
        
        regional_overview = regional_overview.sort_values('market_share_pct_regional', ascending=False)
        
        # Market development analysis
        stage_distribution = df.drop_duplicates('region')['market_stage'].value_counts().to_dict()
        momentum_distribution = df.drop_duplicates('region')['momentum_classification'].value_counts().to_dict()
        
        # Competitive landscape
        competitive_tiers = df.drop_duplicates('region')['competitive_tier'].value_counts().to_dict()
        strategic_priorities = df.drop_duplicates('region')['strategic_priority'].value_counts().to_dict()
        
        # Innovation analysis
        innovation_analysis = df.drop_duplicates('region').groupby('innovation_intensity').agg({
            'region': 'count',
            'unique_families_regional': 'sum'
        }).rename(columns={'region': 'region_count', 'unique_families_regional': 'total_families'})
        
        # Regional profiles
        regional_profiles = {}
        for region in df['region'].unique():
            region_data = df[df['region'] == region].iloc[0]
            
            regional_profiles[region] = {
                'market_position': {
                    'market_share': float(region_data['market_share_pct_regional']),
                    'competitive_tier': region_data['competitive_tier'],
                    'strategic_priority': region_data['strategic_priority']
                },
                'development_profile': {
                    'market_stage': region_data['market_stage'],
                    'momentum': region_data['momentum_classification'],
                    'activity_span': int(region_data['activity_span_regional'])
                },
                'innovation_profile': {
                    'intensity': region_data['innovation_intensity'],
                    'density': float(region_data['innovation_density']),
                    'consistency': float(region_data['innovation_consistency'])
                },
                'strategic_context': {
                    'economic_status': region_data['economic_status'],
                    'ree_relevance': region_data['ree_relevance'],
                    'key_strengths': region_data['regional_strengths']
                }
            }
        
        intelligence_report = {
            'executive_summary': {
                'total_regions': len(regional_overview),
                'market_leader': regional_overview.index[0] if len(regional_overview) > 0 else 'N/A',
                'leader_share': float(regional_overview.iloc[0]['market_share_pct_regional']) if len(regional_overview) > 0 else 0,
                'emerging_regions': len(df[df['momentum_classification'] == 'Accelerating']['region'].unique()),
                'mature_markets': len(df[df['market_stage'] == 'Advanced']['region'].unique())
            },
            'regional_rankings': regional_overview.to_dict('index'),
            'market_development': {
                'stage_distribution': stage_distribution,
                'momentum_distribution': momentum_distribution
            },
            'competitive_landscape': {
                'competitive_tiers': competitive_tiers,
                'strategic_priorities': strategic_priorities
            },
            'innovation_landscape': innovation_analysis.to_dict('index'),
            'regional_profiles': regional_profiles,
            'strategic_recommendations': self._generate_strategic_recommendations(df)
        }
        
        self.regional_intelligence = intelligence_report
        return intelligence_report
    
    def _generate_strategic_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate strategic recommendations based on regional analysis."""
        recommendations = []
        
        # Market leader analysis
        leader_data = df[df['competitive_tier'] == 'Market Leader']
        if len(leader_data) > 0:
            leader_region = leader_data.iloc[0]['region']
            recommendations.append(f"Monitor {leader_region} market leadership strategies and competitive responses")
        
        # High momentum regions
        accelerating_regions = df[df['momentum_classification'] == 'Accelerating']['region'].unique()
        if len(accelerating_regions) > 0:
            recommendations.append(f"Investigate growth drivers in accelerating regions: {', '.join(accelerating_regions)}")
        
        # Innovation hotspots
        high_innovation = df[df['innovation_intensity'] == 'Very High']['region'].unique()
        if len(high_innovation) > 0:
            recommendations.append(f"Track innovation developments in high-intensity regions: {', '.join(high_innovation)}")
        
        # Strategic priorities
        critical_regions = df[df['strategic_priority'] == 'Critical']['region'].unique()
        if len(critical_regions) > 0:
            recommendations.append(f"Prioritize competitive intelligence for critical regions: {', '.join(critical_regions)}")
        
        # Emerging opportunities
        emerging_regions = df[df['market_stage'] == 'Growth']['region'].unique()
        if len(emerging_regions) > 0:
            recommendations.append(f"Explore partnership opportunities in growth-stage regions: {', '.join(emerging_regions)}")
        
        return recommendations
    
    def create_competitive_matrix(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Create competitive positioning matrix for regional analysis.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            DataFrame with competitive matrix
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_regional_dynamics first.")
        
        logger.debug("📊 Creating competitive matrix...")
        
        # Select key metrics for matrix
        matrix_data = df.drop_duplicates('region')[['region', 'market_share_pct_regional', 
                                                   'regional_momentum', 'innovation_density',
                                                   'strategic_priority_score', 'activity_span_regional']]
        
        matrix_data = matrix_data.set_index('region')
        
        # Normalize metrics for comparison
        normalized_matrix = matrix_data.copy()
        for col in matrix_data.columns:
            max_val = matrix_data[col].max()
            min_val = matrix_data[col].min()
            normalized_matrix[col] = (matrix_data[col] - min_val) / (max_val - min_val) if max_val != min_val else 0
        
        # Add composite scores
        normalized_matrix['market_position_score'] = (
            normalized_matrix['market_share_pct_regional'] * 0.4 +
            normalized_matrix['activity_span_regional'] * 0.3 +
            normalized_matrix['strategic_priority_score'] * 0.3
        )
        
        normalized_matrix['innovation_potential_score'] = (
            normalized_matrix['innovation_density'] * 0.6 +
            normalized_matrix['regional_momentum'] * 0.4
        )
        
        # Quadrant classification
        market_median = normalized_matrix['market_position_score'].median()
        innovation_median = normalized_matrix['innovation_potential_score'].median()
        
        def classify_quadrant(market_score: float, innovation_score: float) -> str:
            if market_score >= market_median and innovation_score >= innovation_median:
                return 'Leaders'
            elif market_score >= market_median and innovation_score < innovation_median:
                return 'Established Players'
            elif market_score < market_median and innovation_score >= innovation_median:
                return 'Emerging Innovators'
            else:
                return 'Followers'
        
        normalized_matrix['competitive_quadrant'] = normalized_matrix.apply(
            lambda row: classify_quadrant(row['market_position_score'], row['innovation_potential_score']), 
            axis=1
        )
        
        self.competitive_matrix = normalized_matrix
        return normalized_matrix
    
    def analyze_regional_convergence(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Analyze convergence patterns between regions.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with convergence analysis
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_regional_dynamics first.")
        
        logger.debug("🔄 Analyzing regional convergence patterns...")
        
        # Technology convergence between regions (if classification data available)
        convergence_analysis = {
            'metric_convergence': {},
            'strategic_alignment': {},
            'collaboration_potential': {}
        }
        
        # Calculate metric convergence
        key_metrics = ['market_share_pct_regional', 'regional_momentum', 'innovation_density']
        
        for metric in key_metrics:
            if metric in df.columns:
                regional_values = df.drop_duplicates('region')[['region', metric]].set_index('region')[metric]
                
                # Calculate coefficient of variation (lower = more convergent)
                cv = regional_values.std() / regional_values.mean() if regional_values.mean() != 0 else 0
                convergence_analysis['metric_convergence'][metric] = {
                    'coefficient_of_variation': float(cv),
                    'convergence_level': 'High' if cv < 0.3 else 'Medium' if cv < 0.7 else 'Low'
                }
        
        # Strategic alignment analysis
        strategy_alignment = df.drop_duplicates('region').groupby('regional_filing_strategy')['region'].apply(list).to_dict() if 'regional_filing_strategy' in df.columns else {}
        convergence_analysis['strategic_alignment'] = strategy_alignment
        
        # Collaboration potential based on complementary strengths
        potential_collaborations = []
        regions = df['region'].unique()
        
        for i, region1 in enumerate(regions):
            for region2 in regions[i+1:]:
                region1_data = df[df['region'] == region1].iloc[0]
                region2_data = df[df['region'] == region2].iloc[0]
                
                # Calculate collaboration score based on complementary metrics
                collab_score = 0
                
                # Complementary market positions
                if abs(region1_data['market_share_pct_regional'] - region2_data['market_share_pct_regional']) > 5:
                    collab_score += 1
                
                # Similar momentum
                if abs(region1_data['regional_momentum'] - region2_data['regional_momentum']) < 0.2:
                    collab_score += 1
                
                # Different competitive tiers
                if region1_data['competitive_tier'] != region2_data['competitive_tier']:
                    collab_score += 1
                
                if collab_score >= 2:
                    potential_collaborations.append({
                        'regions': f"{region1} - {region2}",
                        'collaboration_score': collab_score,
                        'rationale': 'Complementary strengths and similar momentum'
                    })
        
        convergence_analysis['collaboration_potential'] = potential_collaborations
        
        return convergence_analysis

def create_regional_analyzer() -> RegionalAnalyzer:
    """
    Factory function to create configured regional analyzer.
    
    Returns:
        Configured RegionalAnalyzer instance
    """
    return RegionalAnalyzer()

# Example usage and demo functions
def demo_regional_analysis():
    """Demonstrate regional analysis capabilities."""
    logger.debug("🚀 Regional Analysis Demo")
    
    # Create sample data
    np.random.seed(42)
    sample_data = []
    
    regions = ['East Asia', 'North America', 'Europe', 'Southeast Asia', 'Oceania']
    countries_by_region = {
        'East Asia': ['China', 'Japan', 'South Korea'],
        'North America': ['United States', 'Canada'],
        'Europe': ['Germany', 'France', 'United Kingdom'],
        'Southeast Asia': ['Singapore', 'Malaysia'],
        'Oceania': ['Australia']
    }
    
    for i in range(200):
        region = np.random.choice(regions)
        country = np.random.choice(countries_by_region[region])
        family_id = 100000 + i
        filing_year = np.random.randint(2010, 2023)
        family_size = np.random.randint(1, 20)
        
        sample_data.append({
            'region': region,
            'country_name': country,
            'docdb_family_id': family_id,
            'earliest_filing_year': filing_year,
            'docdb_family_size': family_size
        })
    
    df = pd.DataFrame(sample_data)
    
    # Analyze regional dynamics
    analyzer = create_regional_analyzer()
    analyzed_df = analyzer.analyze_regional_dynamics(df)
    
    # Generate insights
    intelligence_report = analyzer.generate_regional_intelligence_report()
    competitive_matrix = analyzer.create_competitive_matrix()
    convergence_analysis = analyzer.analyze_regional_convergence()
    
    logger.debug("✅ Demo analysis complete")
    logger.debug(f"🌍 Market leader: {intelligence_report['executive_summary']['market_leader']}")
    logger.debug(f"📊 Competitive matrix dimensions: {competitive_matrix.shape}")
    
    return analyzer, analyzed_df, intelligence_report

if __name__ == "__main__":
    demo_regional_analysis()