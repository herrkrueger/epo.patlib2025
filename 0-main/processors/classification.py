"""
Classification Analysis Processor for REE Patent Analysis
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes patent classification data (IPC/CPC) to analyze technology domains,
innovation networks, and cross-domain convergence patterns for rare earth elements.
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple, Union, Set
import re
from collections import defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClassificationAnalyzer:
    """
    Comprehensive classification analysis for technology intelligence and innovation networks.
    """
    
    # REE-specific IPC/CPC classification codes
    REE_CLASSIFICATION_CODES = {
        # Extraction and Processing
        'C22B  19/28': 'REE Extraction - Specific Methods',
        'C22B  19/30': 'REE Extraction - Advanced Techniques',
        'C22B  25/06': 'REE Processing - General Methods',
        
        # Ceramics and Materials
        'C04B  18/04': 'REE Ceramics - Basic Applications',
        'C04B  18/06': 'REE Ceramics - Advanced Materials',
        'C04B  18/08': 'REE Ceramics - Specialized Uses',
        
        # Energy Storage and Batteries
        'H01M   6/52': 'REE Batteries - Primary Cells',
        'H01M  10/54': 'REE Batteries - Secondary Cells',
        
        # Optical and Electronic Applications
        'C09K  11/01': 'REE Phosphors - Luminescent Materials',
        'H01J   9/52': 'REE Electronic Devices - Display Technology',
        
        # Recycling and Sustainability
        'Y02W30/52': 'REE Recycling - Waste Management',
        'Y02W30/56': 'REE Recycling - Material Recovery',
        'Y02W30/84': 'REE Recycling - Specialized Techniques'
    }
    
    # Technology domain classification
    TECHNOLOGY_DOMAINS = {
        'C22B': 'Metallurgy & Extraction',
        'C04B': 'Ceramics & Materials',
        'H01M': 'Batteries & Energy Storage',
        'C09K': 'Phosphors & Luminescence',
        'H01J': 'Electronic Devices',
        'Y02W': 'Recycling & Sustainability',
        'G06F': 'Computing & AI',
        'B03C': 'Magnetic Separation',
        'C01F': 'Inorganic Chemistry',
        'H01F': 'Magnetics & Electromagnetics',
        'G01N': 'Measuring & Testing',
        'B09B': 'Solid Waste Disposal'
    }
    
    # Sub-domain classifications for detailed analysis
    SUB_DOMAINS = {
        'C22B': {
            '19': 'Rare Earth Extraction',
            '25': 'General Metal Processing',
            '07': 'Electrolytic Processing'
        },
        'C04B': {
            '18': 'REE Ceramics',
            '35': 'Shaped Articles',
            '38': 'Porous Materials'
        },
        'H01M': {
            '06': 'Primary Batteries',
            '10': 'Secondary Batteries',
            '04': 'Battery Components'
        }
    }
    
    def __init__(self):
        """Initialize classification analyzer."""
        self.analyzed_data = None
        self.network_graph = None
        self.classification_intelligence = None
    
    def analyze_classification_patterns(self, patent_data: pd.DataFrame,
                                      ipc1_col: str = 'IPC_1',
                                      ipc2_col: str = 'IPC_2',
                                      family_col: str = 'family_id',
                                      year_col: str = 'filing_year') -> pd.DataFrame:
        """
        Comprehensive classification analysis including co-occurrence networks.
        
        Args:
            patent_data: DataFrame with patent classification data
            ipc1_col: Column name for first IPC code
            ipc2_col: Column name for second IPC code (for co-occurrence)
            family_col: Column name for patent family IDs
            year_col: Column name for filing years
            
        Returns:
            Enhanced DataFrame with classification intelligence
        """
        logger.info("🏷️ Starting comprehensive classification analysis...")
        
        df = patent_data.copy()
        
        # Validate required columns
        required_cols = [ipc1_col, family_col, year_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Clean and standardize classification codes
        df = self._clean_classification_codes(df, ipc1_col, ipc2_col)
        
        # Add domain classifications
        df = self._add_domain_classifications(df, ipc1_col, ipc2_col)
        
        # Analyze co-occurrence patterns
        df = self._analyze_co_occurrence_patterns(df, ipc1_col, ipc2_col, family_col)
        
        # Add temporal analysis
        df = self._add_temporal_classification_patterns(df, year_col)
        
        # Calculate innovation metrics
        df = self._calculate_innovation_metrics(df, ipc1_col, ipc2_col)
        
        self.analyzed_data = df
        logger.info(f"✅ Classification analysis complete for {len(df)} records")
        
        return df
    
    def _clean_classification_codes(self, df: pd.DataFrame, 
                                  ipc1_col: str, ipc2_col: str) -> pd.DataFrame:
        """Clean and standardize IPC/CPC classification codes."""
        logger.info("🧹 Cleaning classification codes...")
        
        # Standardize IPC codes to 8-character format
        df[ipc1_col] = df[ipc1_col].astype(str).str[:8]
        
        if ipc2_col in df.columns:
            df[ipc2_col] = df[ipc2_col].astype(str).str[:8]
            
            # Remove records where IPC1 and IPC2 are the same
            df = df[df[ipc1_col] != df[ipc2_col]].copy()
        
        # Remove invalid codes
        df = df[df[ipc1_col].str.len() >= 4].copy()
        df = df[df[ipc1_col] != 'nan'].copy()
        
        return df
    
    def _add_domain_classifications(self, df: pd.DataFrame, 
                                  ipc1_col: str, ipc2_col: str) -> pd.DataFrame:
        """Add technology domain classifications."""
        logger.info("🏢 Adding domain classifications...")
        
        # Extract main classes (first 4 characters)
        df['main_class_1'] = df[ipc1_col].str[:4]
        df['domain_1'] = df['main_class_1'].map(self.TECHNOLOGY_DOMAINS).fillna('Other')
        
        if ipc2_col in df.columns:
            df['main_class_2'] = df[ipc2_col].str[:4]
            df['domain_2'] = df['main_class_2'].map(self.TECHNOLOGY_DOMAINS).fillna('Other')
            
            # Identify cross-domain innovations
            df['is_cross_domain'] = df['domain_1'] != df['domain_2']
            df['connection_type'] = df['is_cross_domain'].map({
                True: 'Cross-Domain Innovation',
                False: 'Within-Domain Development'
            })
            
            # Create domain pair for analysis
            df['domain_pair'] = df.apply(
                lambda row: f"{row['domain_1']} ↔ {row['domain_2']}" 
                if row['domain_1'] <= row['domain_2'] 
                else f"{row['domain_2']} ↔ {row['domain_1']}", 
                axis=1
            )
        else:
            df['is_cross_domain'] = False
            df['connection_type'] = 'Single Domain'
        
        # Add sub-domain classifications
        df = self._add_subdomain_classifications(df, ipc1_col, ipc2_col)
        
        return df
    
    def _add_subdomain_classifications(self, df: pd.DataFrame, 
                                     ipc1_col: str, ipc2_col: str) -> pd.DataFrame:
        """Add detailed sub-domain classifications."""
        def get_subdomain(ipc_code: str) -> str:
            if len(ipc_code) < 8:
                return 'Unknown'
            
            main_class = ipc_code[:4]
            subclass = ipc_code[4:6].strip()
            
            if main_class in self.SUB_DOMAINS and subclass in self.SUB_DOMAINS[main_class]:
                return self.SUB_DOMAINS[main_class][subclass]
            
            return f"{main_class} - Other"
        
        df['subdomain_1'] = df[ipc1_col].apply(get_subdomain)
        
        if ipc2_col in df.columns:
            df['subdomain_2'] = df[ipc2_col].apply(get_subdomain)
        
        return df
    
    def _analyze_co_occurrence_patterns(self, df: pd.DataFrame, 
                                      ipc1_col: str, ipc2_col: str, 
                                      family_col: str) -> pd.DataFrame:
        """Analyze IPC co-occurrence patterns for network analysis."""
        logger.info("🕸️ Analyzing co-occurrence patterns...")
        
        if ipc2_col not in df.columns:
            logger.warning("⚠️ No second IPC column available for co-occurrence analysis")
            return df
        
        # Calculate co-occurrence frequencies
        cooccurrence_counts = df.groupby([ipc1_col, ipc2_col]).agg({
            family_col: 'nunique',
            'filing_year': 'count'
        }).rename(columns={
            family_col: 'unique_families',
            'filing_year': 'total_occurrences'
        }).reset_index()
        
        # Merge co-occurrence data back
        df = df.merge(
            cooccurrence_counts.add_suffix('_cooccur'),
            left_on=[ipc1_col, ipc2_col],
            right_on=[f'{ipc1_col}_cooccur', f'{ipc2_col}_cooccur'],
            how='left'
        )
        
        # Calculate co-occurrence strength
        max_occurrences = cooccurrence_counts['total_occurrences'].max()
        df['cooccurrence_strength'] = df['total_occurrences_cooccur'] / max_occurrences
        
        # Classify connection strength
        df['connection_strength'] = pd.cut(
            df['cooccurrence_strength'],
            bins=[0, 0.1, 0.3, 0.6, 1.0],
            labels=['Weak', 'Moderate', 'Strong', 'Very Strong']
        )
        
        return df
    
    def _add_temporal_classification_patterns(self, df: pd.DataFrame, year_col: str) -> pd.DataFrame:
        """Add temporal patterns to classification analysis."""
        logger.info("📅 Adding temporal patterns...")
        
        # Time period classification
        df['innovation_period'] = pd.cut(
            df[year_col],
            bins=[2009, 2014, 2018, 2022, float('inf')],
            labels=['Early (2010-2014)', 'Growth (2015-2018)', 'Recent (2019-2022)', 'Latest (2023+)']
        )
        
        # Calculate domain evolution
        domain_evolution = df.groupby(['domain_1', 'innovation_period']).size().reset_index(name='patent_count')
        
        # Add trend indicators
        for domain in df['domain_1'].unique():
            domain_data = domain_evolution[domain_evolution['domain_1'] == domain]
            if len(domain_data) > 1:
                trend = 'Growing' if domain_data['patent_count'].iloc[-1] > domain_data['patent_count'].iloc[0] else 'Stable'
            else:
                trend = 'Emerging'
            
            df.loc[df['domain_1'] == domain, 'domain_trend'] = trend
        
        return df
    
    def _calculate_innovation_metrics(self, df: pd.DataFrame, 
                                    ipc1_col: str, ipc2_col: str) -> pd.DataFrame:
        """Calculate innovation and convergence metrics."""
        logger.info("💡 Calculating innovation metrics...")
        
        # Calculate domain diversity
        domain_counts = df['domain_1'].value_counts()
        total_domains = len(domain_counts)
        
        df['domain_diversity_score'] = df['domain_1'].apply(
            lambda x: 1 - (domain_counts[x] / len(df))
        )
        
        # Innovation complexity based on cross-domain connections
        if 'is_cross_domain' in df.columns:
            df['innovation_complexity'] = df['is_cross_domain'].map({
                True: 'High (Cross-Domain)',
                False: 'Low (Single Domain)'
            })
        
        # Calculate technology convergence index
        if ipc2_col in df.columns:
            convergence_patterns = df.groupby('domain_pair').size()
            max_convergence = convergence_patterns.max() if len(convergence_patterns) > 0 else 1
            
            df['convergence_index'] = df['domain_pair'].apply(
                lambda x: convergence_patterns.get(x, 0) / max_convergence
            )
        
        return df
    
    def build_classification_network(self, df: Optional[pd.DataFrame] = None,
                                   min_cooccurrence: int = 2) -> nx.Graph:
        """
        Build network graph of IPC classification co-occurrences.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            min_cooccurrence: Minimum co-occurrence threshold for edges
            
        Returns:
            NetworkX graph with classification network
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_classification_patterns first.")
        
        logger.info("🕸️ Building classification network...")
        
        # Filter strong connections
        strong_connections = df[df['total_occurrences_cooccur'] >= min_cooccurrence].copy()
        
        # Create NetworkX graph
        G = nx.Graph()
        
        for _, row in strong_connections.iterrows():
            G.add_edge(
                row['IPC_1'], 
                row['IPC_2'], 
                weight=row['total_occurrences_cooccur'],
                strength=row['cooccurrence_strength'],
                domain_1=row['domain_1'],
                domain_2=row['domain_2'],
                is_cross_domain=row['is_cross_domain']
            )
        
        # Calculate network metrics
        node_degrees = dict(G.degree())
        node_centrality = nx.betweenness_centrality(G)
        node_clustering = nx.clustering(G)
        
        # Add node attributes
        for node in G.nodes():
            G.nodes[node]['degree'] = node_degrees.get(node, 0)
            G.nodes[node]['centrality'] = node_centrality.get(node, 0)
            G.nodes[node]['clustering'] = node_clustering.get(node, 0)
            
            # Add domain information
            if node in df['IPC_1'].values:
                domain = df[df['IPC_1'] == node]['domain_1'].iloc[0]
                G.nodes[node]['domain'] = domain
        
        self.network_graph = G
        logger.info(f"✅ Network built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        return G
    
    def generate_classification_intelligence(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate comprehensive classification intelligence summary.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            
        Returns:
            Dictionary with classification intelligence insights
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_classification_patterns first.")
        
        logger.info("📋 Generating classification intelligence...")
        
        # Domain analysis
        domain_analysis = df.groupby('domain_1').agg({
            'family_id': 'nunique',
            'filing_year': ['min', 'max', 'count']
        }).round(2)
        
        domain_analysis.columns = ['unique_families', 'first_year', 'latest_year', 'total_records']
        domain_analysis = domain_analysis.sort_values('unique_families', ascending=False)
        
        # Cross-domain innovation analysis
        cross_domain_stats = {}
        if 'is_cross_domain' in df.columns:
            cross_domain_stats = {
                'cross_domain_innovations': int(df['is_cross_domain'].sum()),
                'cross_domain_percentage': float(df['is_cross_domain'].mean() * 100),
                'top_domain_pairs': df['domain_pair'].value_counts().head(10).to_dict()
            }
        
        # Technology convergence analysis
        convergence_analysis = {}
        if 'convergence_index' in df.columns:
            convergence_analysis = {
                'avg_convergence_index': float(df['convergence_index'].mean()),
                'high_convergence_threshold': float(df['convergence_index'].quantile(0.75)),
                'emerging_convergences': len(df[df['convergence_index'] > df['convergence_index'].quantile(0.9)])
            }
        
        # Network analysis (if network exists)
        network_stats = {}
        if self.network_graph:
            network_stats = {
                'total_nodes': self.network_graph.number_of_nodes(),
                'total_edges': self.network_graph.number_of_edges(),
                'network_density': float(nx.density(self.network_graph)),
                'avg_clustering': float(nx.average_clustering(self.network_graph)),
                'connected_components': nx.number_connected_components(self.network_graph)
            }
        
        intelligence = {
            'overview': {
                'total_domains': df['domain_1'].nunique(),
                'total_classifications': df['IPC_1'].nunique(),
                'dominant_domain': domain_analysis.index[0] if len(domain_analysis) > 0 else 'N/A',
                'innovation_complexity': df['innovation_complexity'].value_counts().to_dict() if 'innovation_complexity' in df.columns else {}
            },
            'domain_rankings': domain_analysis.head(10).to_dict('index'),
            'cross_domain_innovation': cross_domain_stats,
            'technology_convergence': convergence_analysis,
            'network_intelligence': network_stats,
            'temporal_patterns': df['innovation_period'].value_counts().to_dict() if 'innovation_period' in df.columns else {},
            'ree_specific_insights': self._analyze_ree_specific_patterns(df)
        }
        
        self.classification_intelligence = intelligence
        return intelligence
    
    def _analyze_ree_specific_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze REE-specific classification patterns."""
        ree_patterns = {}
        
        # Check for REE-specific codes
        ree_codes = list(self.REE_CLASSIFICATION_CODES.keys())
        ree_data = df[df['IPC_1'].str[:11].isin(ree_codes)]
        
        if len(ree_data) > 0:
            ree_patterns = {
                'ree_specific_records': len(ree_data),
                'ree_percentage': float(len(ree_data) / len(df) * 100),
                'ree_domain_distribution': ree_data['domain_1'].value_counts().to_dict(),
                'top_ree_classifications': ree_data['IPC_1'].value_counts().head(5).to_dict()
            }
        
        return ree_patterns
    
    def get_innovation_hotspots(self, df: Optional[pd.DataFrame] = None, top_n: int = 10) -> Dict:
        """
        Identify innovation hotspots based on classification patterns.
        
        Args:
            df: DataFrame to analyze (uses self.analyzed_data if None)
            top_n: Number of top hotspots to return
            
        Returns:
            Dictionary with innovation hotspot analysis
        """
        if df is None:
            df = self.analyzed_data
        
        if df is None:
            raise ValueError("No analyzed data available. Run analyze_classification_patterns first.")
        
        # Domain-based hotspots
        domain_hotspots = df.groupby('domain_1').agg({
            'family_id': 'nunique',
            'is_cross_domain': 'sum' if 'is_cross_domain' in df.columns else 'count',
            'convergence_index': 'mean' if 'convergence_index' in df.columns else 'count'
        }).round(2)
        
        domain_hotspots.columns = ['unique_families', 'cross_domain_innovations', 'avg_convergence']
        
        # Calculate hotspot score
        domain_hotspots['hotspot_score'] = (
            domain_hotspots['unique_families'] * 0.4 +
            domain_hotspots['cross_domain_innovations'] * 0.4 +
            domain_hotspots['avg_convergence'] * 100 * 0.2
        )
        
        domain_hotspots = domain_hotspots.sort_values('hotspot_score', ascending=False)
        
        # Classification-level hotspots
        classification_hotspots = df.groupby('IPC_1').agg({
            'family_id': 'nunique',
            'total_occurrences_cooccur': 'mean' if 'total_occurrences_cooccur' in df.columns else 'count'
        }).round(2)
        
        classification_hotspots.columns = ['unique_families', 'avg_cooccurrence']
        classification_hotspots = classification_hotspots.sort_values('unique_families', ascending=False)
        
        return {
            'domain_hotspots': domain_hotspots.head(top_n).to_dict('index'),
            'classification_hotspots': classification_hotspots.head(top_n).to_dict('index'),
            'cross_domain_hotspots': df['domain_pair'].value_counts().head(top_n).to_dict() if 'domain_pair' in df.columns else {}
        }

class ClassificationDataProcessor:
    """
    Data processor for cleaning and preparing classification data from PATSTAT.
    """
    
    def __init__(self):
        """Initialize classification data processor."""
        self.processed_data = None
    
    def process_patstat_classification_data(self, raw_data: List[Tuple]) -> pd.DataFrame:
        """
        Process raw PATSTAT classification query results.
        
        Args:
            raw_data: Raw query results from PATSTAT IPC co-occurrence analysis
            
        Returns:
            Processed DataFrame ready for classification analysis
        """
        logger.info(f"📊 Processing {len(raw_data)} raw classification records...")
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data, columns=[
            'family_id', 'filing_year', 'IPC_1', 'IPC_2'
        ])
        
        # Data cleaning
        df = self._clean_classification_data(df)
        df = self._validate_classification_data(df)
        df = self._standardize_ipc_codes(df)
        
        logger.info(f"✅ Processed to {len(df)} clean classification records")
        self.processed_data = df
        
        return df
    
    def _clean_classification_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean classification-specific data."""
        logger.info("🧹 Cleaning classification data...")
        
        # Remove null IPC codes
        df = df[df['IPC_1'].notna()].copy()
        df = df[df['IPC_2'].notna()].copy()
        
        # Convert to string and clean
        df['IPC_1'] = df['IPC_1'].astype(str).str.strip()
        df['IPC_2'] = df['IPC_2'].astype(str).str.strip()
        
        # Remove empty strings
        df = df[df['IPC_1'] != ''].copy()
        df = df[df['IPC_2'] != ''].copy()
        
        return df
    
    def _validate_classification_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate classification data quality."""
        logger.info("🔍 Validating classification data...")
        
        initial_count = len(df)
        
        # Validate filing years
        current_year = datetime.now().year
        df = df[df['filing_year'].between(1980, current_year)].copy()
        
        # Remove self-loops (IPC_1 == IPC_2)
        df = df[df['IPC_1'] != df['IPC_2']].copy()
        
        # Ensure IPC codes have minimum length
        df = df[df['IPC_1'].str.len() >= 4].copy()
        df = df[df['IPC_2'].str.len() >= 4].copy()
        
        removed_count = initial_count - len(df)
        if removed_count > 0:
            logger.info(f"📊 Removed {removed_count} invalid records")
        
        return df
    
    def _standardize_ipc_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize IPC codes to consistent format."""
        logger.info("🏷️ Standardizing IPC codes...")
        
        # Ensure consistent ordering (smaller code first for consistent analysis)
        def order_ipc_codes(row):
            if row['IPC_1'] > row['IPC_2']:
                return pd.Series([row['IPC_2'], row['IPC_1']])
            return pd.Series([row['IPC_1'], row['IPC_2']])
        
        df[['IPC_1', 'IPC_2']] = df.apply(order_ipc_codes, axis=1)
        
        # Truncate to 8 characters for consistency
        df['IPC_1'] = df['IPC_1'].str[:8]
        df['IPC_2'] = df['IPC_2'].str[:8]
        
        return df

def create_classification_analyzer() -> ClassificationAnalyzer:
    """
    Factory function to create configured classification analyzer.
    
    Returns:
        Configured ClassificationAnalyzer instance
    """
    return ClassificationAnalyzer()

def create_classification_processor() -> ClassificationDataProcessor:
    """
    Factory function to create configured classification data processor.
    
    Returns:
        Configured ClassificationDataProcessor instance
    """
    return ClassificationDataProcessor()

# Example usage and demo functions
def demo_classification_analysis():
    """Demonstrate classification analysis capabilities."""
    logger.info("🚀 Classification Analysis Demo")
    
    # Create sample data
    np.random.seed(42)
    sample_data = []
    
    ipc_codes = ['C22B19/28', 'C04B18/04', 'H01M10/54', 'C09K11/01', 'H01J09/52']
    
    for i in range(50):
        family_id = 100000 + i
        filing_year = np.random.randint(2010, 2023)
        ipc1 = np.random.choice(ipc_codes)
        ipc2 = np.random.choice(ipc_codes)
        
        # Ensure different IPC codes
        while ipc2 == ipc1:
            ipc2 = np.random.choice(ipc_codes)
        
        sample_data.append((family_id, filing_year, ipc1, ipc2))
    
    # Process data
    processor = create_classification_processor()
    df = processor.process_patstat_classification_data(sample_data)
    
    # Analyze classifications
    analyzer = create_classification_analyzer()
    analyzed_df = analyzer.analyze_classification_patterns(df)
    
    # Build network
    network = analyzer.build_classification_network(analyzed_df)
    
    # Generate insights
    intelligence = analyzer.generate_classification_intelligence()
    hotspots = analyzer.get_innovation_hotspots()
    
    logger.info("✅ Demo analysis complete")
    logger.info(f"🏷️ Dominant domain: {intelligence['overview']['dominant_domain']}")
    logger.info(f"🕸️ Network nodes: {network.number_of_nodes()}")
    
    return analyzer, analyzed_df, intelligence

if __name__ == "__main__":
    demo_classification_analysis()