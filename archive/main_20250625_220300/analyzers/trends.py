"""
Trends Analysis Module for REE Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module provides comprehensive trend analysis capabilities including
temporal patterns, market dynamics, and predictive analytics for patent intelligence.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import logging
from datetime import datetime, timedelta
from scipy import stats
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrendsAnalyzer:
    """
    Comprehensive trends analysis for patent intelligence with predictive capabilities.
    """
    
    # Market event timeline for correlation analysis
    MARKET_EVENTS = {
        2010: "REE Crisis Begins - Export restrictions",
        2011: "Price Peak - Neodymium reaches $500/kg", 
        2012: "WTO Dispute - Trade tensions escalate",
        2014: "Market Stabilization - Prices normalize",
        2015: "Paris Agreement - Climate focus increases",
        2016: "Alternative Sources - Diversification efforts",
        2017: "EV Market Acceleration - Tesla growth",
        2018: "Trade War Begins - US-China tensions",
        2019: "Green Deal Announced - EU strategy",
        2020: "COVID Supply Disruption - Global impacts",
        2021: "Clean Energy Boom - Massive investments",
        2022: "Inflation & Supply Chain - Economic pressures",
        2023: "AI Revolution - New demand patterns"
    }
    
    # Technology lifecycle stages
    LIFECYCLE_STAGES = {
        'Emergence': {'duration_years': 3, 'growth_pattern': 'Exponential'},
        'Growth': {'duration_years': 5, 'growth_pattern': 'High Linear'},
        'Maturity': {'duration_years': 8, 'growth_pattern': 'Moderate Linear'},
        'Decline': {'duration_years': 5, 'growth_pattern': 'Negative'}
    }
    
    def __init__(self):
        """Initialize trends analyzer."""
        self.analyzed_data = None
        self.trend_models = {}
        self.predictions = {}
        self.correlation_analysis = {}
    
    def analyze_temporal_trends(self, patent_data: pd.DataFrame,
                              year_col: str = 'filing_year',
                              family_col: str = 'family_id',
                              tech_col: str = 'ree_technology_area',
                              region_col: str = 'region',
                              applicant_col: str = 'applicant_name') -> pd.DataFrame:
        """
        Comprehensive temporal trends analysis with market correlation.
        
        Args:
            patent_data: DataFrame with patent temporal data
            year_col: Column name for filing years
            family_col: Column name for patent family IDs
            tech_col: Column name for technology areas
            region_col: Column name for regions
            applicant_col: Column name for applicants
            
        Returns:
            Enhanced DataFrame with trend intelligence
        """
        logger.debug("📈 Starting comprehensive temporal trends analysis...")
        
        df = patent_data.copy()
        
        # Validate required columns
        required_cols = [year_col, family_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Calculate basic temporal metrics
        df = self._calculate_temporal_metrics(df, year_col, family_col)
        
        # Analyze filing patterns
        df = self._analyze_filing_patterns(df, year_col, family_col, tech_col)
        
        # Add market event correlation
        df = self._add_market_event_correlation(df, year_col)
        
        # Calculate trend indicators
        df = self._calculate_trend_indicators(df, year_col, family_col, tech_col, region_col)
        
        # Analyze cyclical patterns
        df = self._analyze_cyclical_patterns(df, year_col, family_col)
        
        # Generate trend forecasts
        self._generate_trend_forecasts(df, year_col, family_col, tech_col)
        
        self.analyzed_data = df
        logger.debug(f"✅ Trends analysis complete for {len(df)} records")
        
        return df
    
    def _calculate_temporal_metrics(self, df: pd.DataFrame, year_col: str, family_col: str) -> pd.DataFrame:
        """Calculate basic temporal metrics."""
        logger.debug("📊 Calculating temporal metrics...")
        
        # Annual activity summary
        annual_activity = df.groupby(year_col).agg({
            family_col: 'nunique',
            year_col: 'count'
        }).rename(columns={
            family_col: 'unique_families',
            year_col: 'total_records'
        })
        
        # Calculate year-over-year growth
        annual_activity['yoy_growth'] = annual_activity['unique_families'].pct_change() * 100
        annual_activity['yoy_growth_3yr'] = annual_activity['unique_families'].rolling(3).apply(
            lambda x: ((x.iloc[-1] / x.iloc[0]) ** (1/2) - 1) * 100 if x.iloc[0] > 0 else 0
        )
        
        # Calculate cumulative metrics
        annual_activity['cumulative_families'] = annual_activity['unique_families'].cumsum()
        annual_activity['market_penetration'] = (
            annual_activity['cumulative_families'] / annual_activity['cumulative_families'].max() * 100
        )
        
        # Activity intensity (patents per active year)
        min_year = df[year_col].min()
        max_year = df[year_col].max()
        annual_activity['activity_intensity'] = (
            annual_activity['unique_families'] / (max_year - min_year + 1)
        ).round(2)
        
        # Merge temporal metrics back to main dataframe
        df = df.merge(
            annual_activity.add_suffix('_annual'),
            left_on=year_col,
            right_index=True,
            how='left'
        )
        
        return df
    
    def _analyze_filing_patterns(self, df: pd.DataFrame, year_col: str, 
                               family_col: str, tech_col: str) -> pd.DataFrame:
        """Analyze filing patterns and seasonality."""
        logger.debug("🔍 Analyzing filing patterns...")
        
        # Technology-specific temporal patterns
        if tech_col in df.columns:
            tech_patterns = df.groupby([tech_col, year_col]).agg({
                family_col: 'nunique'
            }).reset_index()
            
            tech_patterns.columns = ['technology', 'year', 'families']
            
            # Calculate technology trend direction
            def calculate_tech_trend(group):
                if len(group) < 3:
                    return 'Insufficient Data'
                
                # Linear regression to determine trend
                x = group['year'].values
                y = group['families'].values
                
                slope, _, r_value, _, _ = stats.linregress(x, y)
                
                if r_value**2 < 0.3:  # Low R-squared
                    return 'Volatile'
                elif slope > 0.5:
                    return 'Strong Growth'
                elif slope > 0:
                    return 'Moderate Growth'
                elif slope > -0.5:
                    return 'Stable/Decline'
                else:
                    return 'Strong Decline'
            
            tech_trends = tech_patterns.groupby('technology').apply(calculate_tech_trend).to_dict()
            df['technology_trend'] = df[tech_col].map(tech_trends) if tech_col in df.columns else 'Unknown'
        
        # Filing velocity (rate of change)
        df['filing_velocity'] = df.groupby(tech_col if tech_col in df.columns else 'dummy')[
            'unique_families_annual'
        ].diff().fillna(0)
        
        # Filing momentum (acceleration)
        df['filing_momentum'] = df.groupby(tech_col if tech_col in df.columns else 'dummy')[
            'filing_velocity'
        ].diff().fillna(0)
        
        return df
    
    def _add_market_event_correlation(self, df: pd.DataFrame, year_col: str) -> pd.DataFrame:
        """Add market event correlation analysis."""
        logger.debug("📰 Adding market event correlation...")
        
        # Map market events to years
        df['market_event'] = df[year_col].map(self.MARKET_EVENTS)
        df['has_market_event'] = df['market_event'].notna()
        
        # Calculate pre/post event activity changes
        def calculate_event_impact(year: int) -> Dict[str, float]:
            """Calculate impact of market events on filing activity."""
            if year not in self.MARKET_EVENTS:
                return {'pre_event_avg': 0, 'post_event_avg': 0, 'event_impact': 0}
            
            # Get activity 2 years before and after
            pre_years = [year-2, year-1]
            post_years = [year+1, year+2]
            
            pre_activity = df[df[year_col].isin(pre_years)]['unique_families_annual'].mean()
            post_activity = df[df[year_col].isin(post_years)]['unique_families_annual'].mean()
            
            impact = ((post_activity - pre_activity) / pre_activity * 100) if pre_activity > 0 else 0
            
            return {
                'pre_event_avg': pre_activity,
                'post_event_avg': post_activity,
                'event_impact': impact
            }
        
        # Calculate event impacts for all market event years
        event_impacts = {}
        for event_year in self.MARKET_EVENTS.keys():
            if event_year in df[year_col].values:
                event_impacts[event_year] = calculate_event_impact(event_year)
        
        # Add event impact to dataframe
        def get_event_impact(year: int) -> float:
            return event_impacts.get(year, {}).get('event_impact', 0)
        
        df['market_event_impact'] = df[year_col].apply(get_event_impact)
        
        # Classify market responsiveness
        df['market_responsiveness'] = pd.cut(
            df['market_event_impact'].abs(),
            bins=[0, 10, 25, 50, float('inf')],
            labels=['Low', 'Moderate', 'High', 'Very High']
        )
        
        return df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame, year_col: str, 
                                  family_col: str, tech_col: str, region_col: str) -> pd.DataFrame:
        """Calculate comprehensive trend indicators."""
        logger.debug("📊 Calculating trend indicators...")
        
        # Technology maturity indicators
        if tech_col in df.columns:
            tech_maturity = df.groupby(tech_col).agg({
                year_col: ['min', 'max', 'count'],
                family_col: 'nunique'
            })
            
            tech_maturity.columns = ['first_year', 'latest_year', 'total_records', 'unique_families']
            tech_maturity['technology_age'] = datetime.now().year - tech_maturity['first_year']
            tech_maturity['activity_span'] = tech_maturity['latest_year'] - tech_maturity['first_year'] + 1
            
            # Technology lifecycle classification
            def classify_lifecycle_stage(row):
                age = row['technology_age']
                activity_span = row['activity_span']
                recent_activity = len(df[
                    (df[tech_col] == row.name) & 
                    (df[year_col] >= datetime.now().year - 3)
                ])
                
                if age <= 3:
                    return 'Emergence'
                elif age <= 8 and recent_activity > 0:
                    return 'Growth'
                elif recent_activity > 0:
                    return 'Maturity'
                else:
                    return 'Decline'
            
            tech_maturity['lifecycle_stage'] = tech_maturity.apply(classify_lifecycle_stage, axis=1)
            
            # Merge maturity indicators
            df = df.merge(
                tech_maturity[['technology_age', 'lifecycle_stage']].add_suffix('_tech'),
                left_on=tech_col,
                right_index=True,
                how='left'
            )
        
        # Regional trend indicators
        if region_col in df.columns:
            regional_trends = df.groupby([region_col, year_col]).agg({
                family_col: 'nunique'
            }).reset_index()
            
            regional_trends.columns = ['region', 'year', 'families']
            
            # Calculate regional momentum
            def calculate_regional_momentum(group):
                if len(group) < 3:
                    return 0
                
                recent_avg = group.tail(3)['families'].mean()
                historical_avg = group.head(len(group)//2)['families'].mean()
                
                return ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
            
            regional_momentum = regional_trends.groupby('region').apply(calculate_regional_momentum).to_dict()
            df['regional_momentum'] = df[region_col].map(regional_momentum) if region_col in df.columns else 0
        
        # Innovation intensity trends
        df['innovation_intensity'] = df.groupby(year_col)['unique_families_annual'].transform(
            lambda x: (x - x.mean()) / x.std() if x.std() > 0 else 0
        )
        
        return df
    
    def _analyze_cyclical_patterns(self, df: pd.DataFrame, year_col: str, family_col: str) -> pd.DataFrame:
        """Analyze cyclical and seasonal patterns."""
        logger.debug("🔄 Analyzing cyclical patterns...")
        
        # Multi-year cycles analysis
        annual_data = df.groupby(year_col)[family_col].nunique().reset_index()
        annual_data.columns = ['year', 'families']
        
        if len(annual_data) >= 6:  # Need minimum data for cycle analysis
            # Simple cycle detection using moving averages
            annual_data['ma_3yr'] = annual_data['families'].rolling(3, center=True).mean()
            annual_data['ma_5yr'] = annual_data['families'].rolling(5, center=True).mean()
            
            # Cycle deviation
            annual_data['cycle_deviation'] = (
                (annual_data['families'] - annual_data['ma_3yr']) / annual_data['ma_3yr'] * 100
            ).fillna(0)
            
            # Cycle classification
            def classify_cycle_phase(deviation: float) -> str:
                if deviation > 15:
                    return 'Peak'
                elif deviation > 5:
                    return 'Expansion'
                elif deviation > -5:
                    return 'Stable'
                elif deviation > -15:
                    return 'Contraction'
                else:
                    return 'Trough'
            
            annual_data['cycle_phase'] = annual_data['cycle_deviation'].apply(classify_cycle_phase)
            
            # Merge cycle data
            df = df.merge(
                annual_data[['year', 'cycle_phase', 'cycle_deviation']],
                left_on=year_col,
                right_on='year',
                how='left'
            )
        else:
            df['cycle_phase'] = 'Insufficient Data'
            df['cycle_deviation'] = 0
        
        return df
    
    def _generate_trend_forecasts(self, df: pd.DataFrame, year_col: str, 
                                family_col: str, tech_col: str):
        """Generate trend forecasts using statistical models."""
        logger.debug("🔮 Generating trend forecasts...")
        
        current_year = datetime.now().year
        forecast_years = 3  # Forecast 3 years ahead
        
        # Overall market forecast
        annual_families = df.groupby(year_col)[family_col].nunique().reset_index()
        annual_families.columns = ['year', 'families']
        
        if len(annual_families) >= 5:  # Need minimum data for forecasting
            # Simple linear trend forecast
            x = annual_families['year'].values
            y = annual_families['families'].values
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Generate forecasts
            forecast_years_list = list(range(current_year + 1, current_year + forecast_years + 1))
            forecasts = [slope * year + intercept for year in forecast_years_list]
            
            self.predictions['overall_market'] = {
                'forecast_years': forecast_years_list,
                'forecasted_families': forecasts,
                'confidence': r_value**2,
                'trend_direction': 'Growth' if slope > 0 else 'Decline',
                'annual_growth_rate': slope / annual_families['families'].mean() * 100 if annual_families['families'].mean() > 0 else 0
            }
        
        # Technology-specific forecasts
        if tech_col in df.columns:
            tech_forecasts = {}
            
            for tech in df[tech_col].unique():
                tech_data = df[df[tech_col] == tech].groupby(year_col)[family_col].nunique().reset_index()
                tech_data.columns = ['year', 'families']
                
                if len(tech_data) >= 3:
                    x = tech_data['year'].values
                    y = tech_data['families'].values
                    
                    if len(x) > 1 and np.var(x) > 0:  # Need variance for regression
                        slope, intercept, r_value, _, _ = stats.linregress(x, y)
                        
                        tech_forecasts[tech] = {
                            'trend_slope': slope,
                            'forecast_confidence': r_value**2,
                            'predicted_2024': slope * 2024 + intercept if slope * 2024 + intercept > 0 else 0,
                            'maturity_assessment': self._assess_technology_maturity(tech_data)
                        }
            
            self.predictions['technology_specific'] = tech_forecasts
    
    def _assess_technology_maturity(self, tech_data: pd.DataFrame) -> str:
        """Assess technology maturity based on growth patterns."""
        if len(tech_data) < 3:
            return 'Insufficient Data'
        
        recent_growth = tech_data.tail(3)['families'].mean()
        early_growth = tech_data.head(3)['families'].mean()
        
        if recent_growth > early_growth * 2:
            return 'Accelerating'
        elif recent_growth > early_growth * 1.2:
            return 'Growing'
        elif recent_growth > early_growth * 0.8:
            return 'Mature'
        else:
            return 'Declining'
    
    def generate_trends_intelligence_report(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive trends intelligence report.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with trends intelligence insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_temporal_trends first.")
        
        logger.debug("📋 Generating trends intelligence report...")
        
        current_year = datetime.now().year
        
        # Overall market trends
        latest_year_data = df[df['filing_year'] == df['filing_year'].max()]
        market_overview = {
            'current_year_families': int(latest_year_data['unique_families_annual'].iloc[0]) if len(latest_year_data) > 0 else 0,
            'yoy_growth': float(latest_year_data['yoy_growth_annual'].iloc[0]) if len(latest_year_data) > 0 else 0,
            'market_momentum': self._classify_market_momentum(df),
            'dominant_trend': df['technology_trend'].mode().iloc[0] if 'technology_trend' in df.columns and len(df['technology_trend'].mode()) > 0 else 'Unknown'
        }
        
        # Technology lifecycle analysis
        if 'lifecycle_stage_tech' in df.columns:
            lifecycle_distribution = df.drop_duplicates('ree_technology_area')['lifecycle_stage_tech'].value_counts().to_dict()
        else:
            lifecycle_distribution = {}
        
        # Market event impact analysis
        event_impact_summary = {}
        if 'market_event_impact' in df.columns:
            significant_events = df[df['market_event_impact'].abs() > 10]
            if len(significant_events) > 0:
                event_impact_summary = {
                    'high_impact_events': significant_events[['filing_year', 'market_event', 'market_event_impact']].drop_duplicates().to_dict('records'),
                    'avg_event_impact': float(significant_events['market_event_impact'].mean()),
                    'market_responsiveness_distribution': df['market_responsiveness'].value_counts().to_dict()
                }
        
        # Cyclical patterns
        cycle_analysis = {}
        if 'cycle_phase' in df.columns:
            current_cycle_data = df[df['filing_year'] == df['filing_year'].max()]
            if len(current_cycle_data) > 0:
                cycle_analysis = {
                    'current_cycle_phase': current_cycle_data['cycle_phase'].iloc[0],
                    'cycle_deviation': float(current_cycle_data['cycle_deviation'].iloc[0]) if 'cycle_deviation' in current_cycle_data.columns else 0,
                    'historical_cycle_distribution': df['cycle_phase'].value_counts().to_dict()
                }
        
        # Technology-specific trends
        if 'ree_technology_area' in df.columns:
            tech_trends = df.groupby('ree_technology_area').agg({
                'technology_trend': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown',
                'filing_velocity': 'mean',
                'filing_momentum': 'mean',
                'technology_age_tech': 'first'
            }).round(2).to_dict('index')
        else:
            tech_trends = {}
        
        # Regional momentum analysis
        if 'regional_momentum' in df.columns:
            regional_trends = df.drop_duplicates('region').set_index('region')['regional_momentum'].to_dict()
        else:
            regional_trends = {}
        
        # Forecasting insights
        forecast_summary = {}
        if self.predictions:
            if 'overall_market' in self.predictions:
                market_forecast = self.predictions['overall_market']
                forecast_summary['market_forecast'] = {
                    'predicted_growth_direction': market_forecast['trend_direction'],
                    'annual_growth_rate': float(market_forecast['annual_growth_rate']),
                    'forecast_confidence': float(market_forecast['confidence']),
                    'next_year_prediction': int(market_forecast['forecasted_families'][0]) if market_forecast['forecasted_families'] else 'N/A'
                }
            
            if 'technology_specific' in self.predictions:
                tech_forecasts = self.predictions['technology_specific']
                high_potential_techs = {
                    tech: data for tech, data in tech_forecasts.items() 
                    if data['trend_slope'] > 0 and data['forecast_confidence'] > 0.5
                }
                forecast_summary['high_potential_technologies'] = high_potential_techs
        
        # Strategic insights and recommendations
        strategic_insights = self._generate_strategic_insights(df)
        
        trends_report = {
            'executive_summary': market_overview,
            'technology_lifecycle': lifecycle_distribution,
            'market_events_impact': event_impact_summary,
            'cyclical_patterns': cycle_analysis,
            'technology_trends': tech_trends,
            'regional_momentum': regional_trends,
            'forecasting_insights': forecast_summary,
            'strategic_insights': strategic_insights,
            'trend_recommendations': self._generate_trend_recommendations(df)
        }
        
        return trends_report
    
    def _classify_market_momentum(self, df: pd.DataFrame) -> str:
        """Classify overall market momentum."""
        if 'yoy_growth_annual' not in df.columns:
            return 'Unknown'
        
        recent_growth = df[df['filing_year'] >= df['filing_year'].max() - 2]['yoy_growth_annual'].mean()
        
        if recent_growth > 15:
            return 'Strong Growth'
        elif recent_growth > 5:
            return 'Moderate Growth'
        elif recent_growth > -5:
            return 'Stable'
        else:
            return 'Declining'
    
    def _generate_strategic_insights(self, df: pd.DataFrame) -> Dict:
        """Generate strategic insights from trend analysis."""
        insights = {
            'emerging_opportunities': [],
            'market_risks': [],
            'technology_shifts': [],
            'competitive_dynamics': []
        }
        
        # Emerging opportunities
        if 'lifecycle_stage_tech' in df.columns:
            emerging_techs = df[df['lifecycle_stage_tech'] == 'Emergence']['ree_technology_area'].unique()
            if len(emerging_techs) > 0:
                insights['emerging_opportunities'].append(f"Emerging technologies: {', '.join(emerging_techs)}")
        
        # Market risks
        if 'market_responsiveness' in df.columns:
            high_volatile = df[df['market_responsiveness'] == 'Very High']['ree_technology_area'].unique()
            if len(high_volatile) > 0:
                insights['market_risks'].append(f"High market volatility in: {', '.join(high_volatile)}")
        
        # Technology shifts
        if 'technology_trend' in df.columns:
            declining_techs = df[df['technology_trend'] == 'Strong Decline']['ree_technology_area'].unique()
            growing_techs = df[df['technology_trend'] == 'Strong Growth']['ree_technology_area'].unique()
            
            if len(declining_techs) > 0:
                insights['technology_shifts'].append(f"Declining technologies: {', '.join(declining_techs)}")
            if len(growing_techs) > 0:
                insights['technology_shifts'].append(f"Growing technologies: {', '.join(growing_techs)}")
        
        return insights
    
    def _generate_trend_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate trend-based strategic recommendations."""
        recommendations = []
        
        # Market momentum recommendations
        momentum = self._classify_market_momentum(df)
        if momentum == 'Strong Growth':
            recommendations.append("Consider scaling patent filing activities to capture growth opportunities")
        elif momentum == 'Declining':
            recommendations.append("Focus on high-value technologies and optimize patent portfolio")
        
        # Technology lifecycle recommendations
        if 'lifecycle_stage_tech' in df.columns:
            emerging_count = len(df[df['lifecycle_stage_tech'] == 'Emergence']['ree_technology_area'].unique())
            if emerging_count > 0:
                recommendations.append(f"Monitor {emerging_count} emerging technology areas for early investment opportunities")
        
        # Event responsiveness recommendations
        if 'market_responsiveness' in df.columns:
            high_responsive = len(df[df['market_responsiveness'] == 'Very High'])
            if high_responsive > 0:
                recommendations.append("Develop market event monitoring systems for high-volatility technologies")
        
        # Forecasting recommendations
        if self.predictions and 'overall_market' in self.predictions:
            forecast = self.predictions['overall_market']
            if forecast['trend_direction'] == 'Growth' and forecast['confidence'] > 0.7:
                recommendations.append("Market forecast indicates growth - consider expanding patent activities")
        
        return recommendations
    
    def analyze_innovation_cycles(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Analyze innovation cycles and technological waves.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with innovation cycle analysis
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_temporal_trends first.")
        
        logger.debug("🌊 Analyzing innovation cycles...")
        
        cycles_analysis = {
            'technology_waves': {},
            'innovation_intensity_cycles': {},
            'market_driven_cycles': {}
        }
        
        # Technology waves analysis
        if 'ree_technology_area' in df.columns:
            for tech_area in df['ree_technology_area'].unique():
                tech_data = df[df['ree_technology_area'] == tech_area]
                annual_activity = tech_data.groupby('filing_year')['family_id'].nunique()
                
                if len(annual_activity) >= 5:
                    # Identify peaks and troughs
                    peaks = []
                    troughs = []
                    
                    for i in range(1, len(annual_activity) - 1):
                        if (annual_activity.iloc[i] > annual_activity.iloc[i-1] and 
                            annual_activity.iloc[i] > annual_activity.iloc[i+1]):
                            peaks.append((annual_activity.index[i], annual_activity.iloc[i]))
                        elif (annual_activity.iloc[i] < annual_activity.iloc[i-1] and 
                              annual_activity.iloc[i] < annual_activity.iloc[i+1]):
                            troughs.append((annual_activity.index[i], annual_activity.iloc[i]))
                    
                    cycles_analysis['technology_waves'][tech_area] = {
                        'peaks': peaks,
                        'troughs': troughs,
                        'average_cycle_length': self._calculate_average_cycle_length(peaks),
                        'current_phase': self._determine_current_phase(annual_activity, peaks, troughs)
                    }
        
        return cycles_analysis
    
    def _calculate_average_cycle_length(self, peaks: List[Tuple]) -> float:
        """Calculate average length between peaks."""
        if len(peaks) < 2:
            return 0
        
        cycle_lengths = [peaks[i][0] - peaks[i-1][0] for i in range(1, len(peaks))]
        return sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 0
    
    def _determine_current_phase(self, annual_activity: pd.Series, 
                               peaks: List[Tuple], troughs: List[Tuple]) -> str:
        """Determine current phase of innovation cycle."""
        if len(annual_activity) < 3:
            return 'Insufficient Data'
        
        recent_trend = annual_activity.tail(3)
        if recent_trend.is_monotonic_increasing:
            return 'Growth Phase'
        elif recent_trend.is_monotonic_decreasing:
            return 'Decline Phase'
        else:
            return 'Transition Phase'

def create_trends_analyzer() -> TrendsAnalyzer:
    """
    Factory function to create configured trends analyzer.
    
    Returns:
        Configured TrendsAnalyzer instance
    """
    return TrendsAnalyzer()

# Example usage and demo functions
def demo_trends_analysis():
    """Demonstrate trends analysis capabilities."""
    logger.debug("🚀 Trends Analysis Demo")
    
    # Create sample data with temporal patterns
    np.random.seed(42)
    sample_data = []
    
    tech_areas = ['Extraction & Processing', 'Advanced Materials', 'Energy Storage', 'Optical & Electronics']
    regions = ['East Asia', 'North America', 'Europe']
    
    # Generate data with trends
    for year in range(2010, 2024):
        for tech in tech_areas:
            for region in regions:
                # Add growth trend with some randomness
                base_activity = 10 + (year - 2010) * 2
                tech_multiplier = {'Extraction & Processing': 1.2, 'Advanced Materials': 1.0, 
                                 'Energy Storage': 1.5, 'Optical & Electronics': 0.8}[tech]
                
                activity = int(base_activity * tech_multiplier * (1 + np.random.normal(0, 0.2)))
                
                for i in range(max(1, activity)):
                    sample_data.append({
                        'family_id': len(sample_data) + 100000,
                        'filing_year': year,
                        'ree_technology_area': tech,
                        'region': region,
                        'applicant_name': f'Company_{np.random.randint(1, 20)}'
                    })
    
    df = pd.DataFrame(sample_data)
    
    # Analyze trends
    analyzer = create_trends_analyzer()
    analyzed_df = analyzer.analyze_temporal_trends(df)
    
    # Generate intelligence
    trends_report = analyzer.generate_trends_intelligence_report()
    cycles_analysis = analyzer.analyze_innovation_cycles()
    
    logger.debug("✅ Demo analysis complete")
    logger.debug(f"📈 Market momentum: {trends_report['executive_summary']['market_momentum']}")
    logger.debug(f"🔮 Forecasting insights available: {bool(trends_report['forecasting_insights'])}")
    
    return analyzer, analyzed_df, trends_report

if __name__ == "__main__":
    demo_trends_analysis()