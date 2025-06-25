"""
Classification Analysis Processor for Patent Intelligence
Enhanced from EPO PATLIB 2025 Live Demo Code

This module processes search results from PatentSearchProcessor to analyze technology domains,
innovation networks, and cross-domain convergence patterns. Works with PATSTAT data to 
extract and analyze IPC/CPC classification information.
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Optional, Tuple, Union, Set
import re
from collections import defaultdict, Counter
from datetime import datetime
import logging

# Import PATSTAT client and models for classification data enrichment
try:
    from epo.tipdata.patstat import PatstatClient
    from epo.tipdata.patstat.database.models import (
        TLS201_APPLN, TLS209_APPLN_IPC, TLS224_APPLN_CPC
    )
    from sqlalchemy import func, and_, distinct
    PATSTAT_AVAILABLE = True
except ImportError:
    PATSTAT_AVAILABLE = False
    logging.warning("PATSTAT integration not available")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClassificationAnalyzer:
    """
    Classification analyzer that works with PatentSearchProcessor results.
    
    Takes patent family search results and enriches them with classification data from PATSTAT,
    then performs comprehensive technology intelligence analysis.
    """
    
    # Core technology domains based on CPC first 4 characters
    TECHNOLOGY_DOMAINS = {
        'A01': 'Agriculture & Food',
        'A43': 'Footwear & Textiles',
        'A61': 'Medical Technology',
        'B01': 'Physical/Chemical Processes',
        'B03': 'Separation & Sorting',
        'B22': 'Casting & Metallurgy',
        'B29': 'Plastics & Materials',
        'C01': 'Inorganic Chemistry',
        'C04': 'Ceramics & Glass',
        'C07': 'Organic Chemistry',
        'C08': 'Polymers',
        'C09': 'Dyes & Coatings',
        'C10': 'Petroleum & Fuels',
        'C22': 'Metallurgy',
        'C25': 'Electrochemistry',
        'D01': 'Textiles & Fibers',
        'D21': 'Paper & Cellulose',
        'F01': 'Engines & Motors',
        'F02': 'Combustion Engines',
        'F16': 'Engineering Elements',
        'F24': 'Heating & Cooling',
        'G01': 'Measuring & Testing',
        'G02': 'Optics',
        'G06': 'Computing & Calculation',
        'G21': 'Nuclear Technology',
        'H01': 'Basic Electric Elements',
        'H02': 'Power Generation & Distribution',
        'H03': 'Electronic Circuits',
        'H04': 'Communication Technology',
        'H05': 'Electric Techniques',
        'Y02': 'Climate Change Mitigation',
        'Y04': 'Smart Grids'
    }
    
    # REE-specific classification mapping
    REE_CLASSIFICATION_FOCUS = {
        'C22B': 'REE Extraction & Processing',
        'C04B': 'REE Ceramics & Materials',
        'H01M': 'REE Batteries & Energy Storage',
        'C09K': 'REE Phosphors & Luminescence',
        'H01J': 'REE Electronic Devices',
        'H01F': 'REE Magnetics & Motors',
        'Y02W': 'REE Recycling & Sustainability',
        'Y02E': 'REE Clean Energy Applications'
    }
    
    def __init__(self, patstat_client: Optional[object] = None):
        """
        Initialize classification analyzer.
        
        Args:
            patstat_client: PATSTAT client instance for data enrichment
        """
        self.patstat_client = patstat_client
        self.session = None
        self.analyzed_data = None
        self.classification_data = None
        self.network_graph = None
        self.classification_intelligence = None
        
        # Initialize PATSTAT connection
        if PATSTAT_AVAILABLE and self.patstat_client is None:
            try:
                self.patstat_client = PatstatClient(environment='PROD')
                logger.debug("✅ Connected to PATSTAT for classification data enrichment")
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
                    logger.debug("✅ PATSTAT session initialized for classification analysis")
                elif hasattr(self.patstat_client, 'orm') and callable(self.patstat_client.orm):
                    # Fallback to EPO PatstatClient orm method
                    self.session = self.patstat_client.orm()
                    logger.debug("✅ PATSTAT session initialized for classification analysis (via orm)")
                else:
                    logger.error("❌ No valid PATSTAT session method found")
                    self.session = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize PATSTAT session: {e}")
    
    def analyze_search_results(self, search_results: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze patent search results to extract classification intelligence.
        
        Args:
            search_results: DataFrame from PatentSearchProcessor with columns:
                           ['docdb_family_id', 'quality_score', 'match_type', 'earliest_filing_year', etc.]
                           
        Returns:
            Enhanced DataFrame with classification intelligence
        """
        logger.debug(f"🏷️ Starting classification analysis of {len(search_results)} patent families...")
        
        if search_results.empty:
            logger.warning("⚠️ No search results to analyze")
            return pd.DataFrame()
        
        # Step 1: Enrich search results with classification data from PATSTAT
        logger.debug("📊 Step 1: Enriching with classification data from PATSTAT...")
        classification_data = self._enrich_with_classification_data(search_results)
        
        if classification_data.empty:
            logger.warning("⚠️ No classification data found for the search results")
            return pd.DataFrame()
        
        # Step 2: Analyze classification patterns and domains
        logger.debug("🔍 Step 2: Analyzing classification patterns and domains...")
        pattern_analysis = self._analyze_classification_patterns(classification_data)
        
        # Step 3: Build technology networks and co-occurrence
        logger.debug("🕸️ Step 3: Building technology networks and co-occurrence patterns...")
        network_analysis = self._build_technology_networks(classification_data)
        
        # Step 4: Generate technology intelligence insights
        logger.debug("🎯 Step 4: Generating technology intelligence insights...")
        intelligence_analysis = self._generate_technology_intelligence(pattern_analysis, network_analysis)
        
        self.analyzed_data = intelligence_analysis
        self.classification_data = classification_data
        
        logger.debug(f"✅ Classification analysis complete: {len(intelligence_analysis)} technology patterns analyzed")
        
        return intelligence_analysis
    
    def _enrich_with_classification_data(self, search_results: pd.DataFrame) -> pd.DataFrame:
        """
        Enrich search results with classification data from PATSTAT.
        
        Uses TLS209_APPLN_IPC and TLS224_APPLN_CPC tables to get classification information.
        """
        if not self.session:
            logger.error("❌ No PATSTAT session available for classification enrichment")
            return pd.DataFrame()
        
        family_ids = search_results['docdb_family_id'].tolist()
        logger.debug(f"   Enriching {len(family_ids)} families with classification data...")
        
        try:
            # Get IPC classifications
            logger.debug("   📋 Querying IPC classifications...")
            ipc_query = self.session.query(
                TLS201_APPLN.docdb_family_id,
                TLS201_APPLN.appln_id,
                TLS201_APPLN.earliest_filing_year,
                TLS209_APPLN_IPC.ipc_class_symbol,
                TLS209_APPLN_IPC.ipc_class_level,
                TLS209_APPLN_IPC.ipc_version,
                TLS209_APPLN_IPC.ipc_value,
                TLS209_APPLN_IPC.ipc_position,
                TLS209_APPLN_IPC.ipc_gener_auth
            ).select_from(TLS201_APPLN)\
            .join(TLS209_APPLN_IPC, TLS201_APPLN.appln_id == TLS209_APPLN_IPC.appln_id)\
            .filter(TLS201_APPLN.docdb_family_id.in_(family_ids))
            
            ipc_result = ipc_query.all()
            
            # Get CPC classifications  
            logger.debug("   📋 Querying CPC classifications...")
            cpc_query = self.session.query(
                TLS201_APPLN.docdb_family_id,
                TLS201_APPLN.appln_id,
                TLS201_APPLN.earliest_filing_year,
                TLS224_APPLN_CPC.cpc_class_symbol
            ).select_from(TLS201_APPLN)\
            .join(TLS224_APPLN_CPC, TLS201_APPLN.appln_id == TLS224_APPLN_CPC.appln_id)\
            .filter(TLS201_APPLN.docdb_family_id.in_(family_ids))
            
            cpc_result = cpc_query.all()
            
            # Convert to DataFrames
            classification_records = []
            
            # Process IPC records
            for record in ipc_result:
                classification_records.append({
                    'docdb_family_id': record[0],
                    'appln_id': record[1],
                    'earliest_filing_year': record[2],
                    'classification_symbol': record[3],
                    'classification_type': 'IPC',
                    'classification_level': record[4],
                    'classification_version': record[5],
                    'classification_value': record[6],
                    'classification_position': record[7],
                    'classification_authority': record[8]
                })
            
            # Process CPC records
            for record in cpc_result:
                classification_records.append({
                    'docdb_family_id': record[0],
                    'appln_id': record[1],
                    'earliest_filing_year': record[2],
                    'classification_symbol': record[3],
                    'classification_type': 'CPC',
                    'classification_level': None,
                    'classification_version': None,
                    'classification_value': None,
                    'classification_position': None,
                    'classification_authority': None
                })
            
            if not classification_records:
                logger.warning("⚠️ No classification data found in PATSTAT for these families")
                return pd.DataFrame()
            
            classification_df = pd.DataFrame(classification_records)
            
            # Merge with original search results to preserve quality scores
            enriched_data = search_results.merge(
                classification_df,
                on='docdb_family_id',
                how='inner',
                suffixes=('', '_patstat')  # Keep original column names
            )
            
            # Fix duplicate column names - prefer search results version
            if 'appln_id_patstat' in enriched_data.columns:
                enriched_data = enriched_data.drop('appln_id_patstat', axis=1)
            if 'earliest_filing_year_patstat' in enriched_data.columns:
                enriched_data = enriched_data.drop('earliest_filing_year_patstat', axis=1)
            
            # Clean and standardize classification codes
            enriched_data = self._clean_classification_data(enriched_data)
            
            logger.debug(f"   ✅ Enriched {len(enriched_data)} classification relationships")
            logger.debug(f"   📊 IPC classifications: {len([r for r in classification_records if r['classification_type'] == 'IPC'])}")
            logger.debug(f"   📊 CPC classifications: {len([r for r in classification_records if r['classification_type'] == 'CPC'])}")
            logger.debug(f"   🏢 Covering {enriched_data['docdb_family_id'].nunique()} families")
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"❌ Failed to enrich with classification data: {e}")
            logger.warning("⚠️ Falling back to basic classification mapping from search results")
            
            # Fallback: use basic classification mapping from search results if available
            fallback_data = search_results.copy()
            
            # Add basic classification columns that processors expect
            fallback_data['cpc_class_symbol'] = 'G06F'  # Generic computing class
            fallback_data['technology_domain'] = 'Computing'
            fallback_data['classification_quality'] = 0.1  # Low quality fallback
            fallback_data['class_depth'] = 1
            
            return fallback_data
    
    def _clean_classification_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize classification data."""
        logger.debug("🧹 Cleaning classification data...")
        
        # Remove empty or null classifications
        df = df[df['classification_symbol'].notna()].copy()
        df = df[df['classification_symbol'].str.strip() != ''].copy()
        
        # Standardize classification symbols
        df['classification_symbol_clean'] = df['classification_symbol'].str.strip().str.upper()
        
        # Extract main class (first 4 characters for technology domain)
        df['main_class'] = df['classification_symbol_clean'].str[:4]
        
        # Extract subclass (first 7 characters)
        df['subclass'] = df['classification_symbol_clean'].str[:7]
        
        # Add technology domain mapping
        df['technology_domain'] = df['main_class'].map(self.TECHNOLOGY_DOMAINS).fillna('Other')
        
        # Add REE-specific focus area
        df['ree_focus_area'] = df['main_class'].map(self.REE_CLASSIFICATION_FOCUS).fillna('General Technology')
        
        return df
    
    def _analyze_classification_patterns(self, classification_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze classification patterns and technology distributions.
        """
        logger.debug("🔍 Analyzing classification patterns...")
        
        # Check available columns and find the correct year column
        year_col = None
        for col in ['earliest_filing_year_x', 'earliest_filing_year_y', 'earliest_filing_year']:
            if col in classification_data.columns:
                year_col = col
                break
        
        if year_col is None:
            logger.error("❌ No filing year column found for classification analysis")
            return pd.DataFrame()
        
        logger.debug(f"   Using year column: {year_col}")
        
        # Check if quality_score exists before aggregating
        agg_dict = {
            'docdb_family_id': 'nunique',
            'appln_id': 'nunique',
            'classification_symbol_clean': 'nunique',
            year_col: ['min', 'max', 'mean']
        }
        
        # Add quality_score only if it exists
        if 'quality_score' in classification_data.columns:
            agg_dict['quality_score'] = 'mean'
        
        # Aggregate by technology domain
        domain_analysis = classification_data.groupby('technology_domain').agg(agg_dict).reset_index()
        
        # Flatten column names properly
        flattened_columns = []
        for col in domain_analysis.columns:
            if isinstance(col, tuple):
                if col[1] == '':  # Single level column
                    flattened_columns.append(col[0])
                elif col[1] == 'min':
                    flattened_columns.append('first_filing_year')
                elif col[1] == 'max':
                    flattened_columns.append('latest_filing_year')
                elif col[1] == 'mean' and col[0] == year_col:
                    flattened_columns.append('avg_filing_year')
                else:
                    flattened_columns.append(f"{col[0]}_{col[1]}")
            else:
                flattened_columns.append(col)
        
        domain_analysis.columns = flattened_columns
        
        # Map aggregated column names to expected names
        column_mapping = {
            'docdb_family_id_nunique': 'patent_families',
            'appln_id_nunique': 'total_applications',
            'classification_symbol_clean_nunique': 'unique_classifications',
            'quality_score_mean': 'avg_quality_score'
        }
        
        # Apply column name mapping
        for old_name, new_name in column_mapping.items():
            if old_name in domain_analysis.columns:
                domain_analysis = domain_analysis.rename(columns={old_name: new_name})
        
        # Add missing avg_quality_score if not present
        if 'avg_quality_score' not in domain_analysis.columns:
            domain_analysis['avg_quality_score'] = 2.0
        
        # Calculate domain metrics
        total_families = domain_analysis['patent_families'].sum()
        domain_analysis['domain_share_pct'] = (domain_analysis['patent_families'] / total_families * 100).round(2)
        domain_analysis['avg_classifications_per_family'] = (domain_analysis['unique_classifications'] / domain_analysis['patent_families']).round(1)
        
        # Activity span
        domain_analysis['activity_span'] = domain_analysis['latest_filing_year'] - domain_analysis['first_filing_year'] + 1
        
        # Sort by patent families
        domain_analysis = domain_analysis.sort_values('patent_families', ascending=False).reset_index(drop=True)
        
        # Add ranking
        domain_analysis['domain_rank'] = range(1, len(domain_analysis) + 1)
        
        logger.debug(f"   ✅ Analyzed {len(domain_analysis)} technology domains")
        logger.debug(f"   🏆 Top domain: {domain_analysis.iloc[0]['technology_domain']} ({domain_analysis.iloc[0]['patent_families']} families)")
        
        return domain_analysis
    
    def _build_technology_networks(self, classification_data: pd.DataFrame) -> Dict:
        """
        Build technology networks and analyze co-occurrence patterns.
        """
        logger.debug("🕸️ Building technology networks...")
        
        # Create co-occurrence matrix at family level
        family_classifications = classification_data.groupby('docdb_family_id')['main_class'].apply(list).reset_index()
        
        # Build co-occurrence network
        G = nx.Graph()
        co_occurrence_counts = defaultdict(int)
        
        for _, row in family_classifications.iterrows():
            classes = list(set(row['main_class']))  # Remove duplicates within family
            if len(classes) > 1:
                # Add all pairs of classifications in this family
                for i, class1 in enumerate(classes):
                    for class2 in classes[i+1:]:
                        pair = tuple(sorted([class1, class2]))
                        co_occurrence_counts[pair] += 1
                        
                        # Add to network
                        if co_occurrence_counts[pair] >= 2:  # Minimum threshold
                            G.add_edge(class1, class2, weight=co_occurrence_counts[pair])
        
        # Calculate network metrics
        network_metrics = {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'network_density': nx.density(G) if G.number_of_nodes() > 1 else 0,
            'average_clustering': nx.average_clustering(G) if G.number_of_nodes() > 2 else 0
        }
        
        # Find most connected technology areas
        if G.number_of_nodes() > 0:
            centrality = nx.degree_centrality(G)
            betweenness = nx.betweenness_centrality(G)
            
            # Top connected nodes
            top_connected = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:5]
            top_bridges = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:5]
        else:
            top_connected = []
            top_bridges = []
        
        # Analyze co-occurrence patterns
        top_cooccurrences = sorted(co_occurrence_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        self.network_graph = G  # Store for visualization
        
        network_analysis = {
            'network_metrics': network_metrics,
            'top_connected_technologies': top_connected,
            'top_bridge_technologies': top_bridges,
            'top_cooccurrences': top_cooccurrences,
            'cooccurrence_matrix': dict(co_occurrence_counts)
        }
        
        logger.debug(f"   ✅ Built network with {network_metrics['total_nodes']} nodes and {network_metrics['total_edges']} edges")
        logger.debug(f"   📊 Network density: {network_metrics['network_density']:.3f}")
        
        return network_analysis
    
    def _generate_technology_intelligence(self, pattern_analysis: pd.DataFrame, 
                                        network_analysis: Dict) -> pd.DataFrame:
        """
        Generate comprehensive technology intelligence insights.
        """
        logger.debug("🎯 Generating technology intelligence insights...")
        
        # Enhance pattern analysis with network insights
        enhanced_analysis = pattern_analysis.copy()
        
        # Add network centrality measures
        if network_analysis['top_connected_technologies']:
            centrality_dict = dict(network_analysis['top_connected_technologies'])
            enhanced_analysis['network_centrality'] = enhanced_analysis['technology_domain'].apply(
                lambda x: centrality_dict.get(x[:4], 0)  # Map domain to main class
            )
        else:
            enhanced_analysis['network_centrality'] = 0
        
        # Calculate innovation intensity
        enhanced_analysis['innovation_intensity'] = (
            enhanced_analysis['unique_classifications'] * enhanced_analysis['avg_quality_score'] / 
            enhanced_analysis['activity_span']
        ).round(2)
        
        # Technology maturity assessment
        def assess_technology_maturity(row):
            if row['activity_span'] > 10 and row['patent_families'] > 5:
                return 'Mature'
            elif row['activity_span'] > 5:
                return 'Developing'
            else:
                return 'Emerging'
        
        enhanced_analysis['technology_maturity'] = enhanced_analysis.apply(assess_technology_maturity, axis=1)
        
        # Strategic importance scoring
        def calculate_strategic_score(row):
            score = 0
            # Volume weight
            if row['patent_families'] > 10:
                score += 3
            elif row['patent_families'] > 5:
                score += 2
            elif row['patent_families'] > 1:
                score += 1
            
            # Quality weight
            if row['avg_quality_score'] > 2.5:
                score += 2
            elif row['avg_quality_score'] > 2.0:
                score += 1
            
            # Network importance weight
            if row['network_centrality'] > 0.1:
                score += 2
            elif row['network_centrality'] > 0.05:
                score += 1
            
            return score
        
        enhanced_analysis['strategic_score'] = enhanced_analysis.apply(calculate_strategic_score, axis=1)
        
        # Strategic category
        def assign_strategic_category(score: int) -> str:
            if score >= 6:
                return 'Core Technology'
            elif score >= 4:
                return 'Important Technology'
            elif score >= 2:
                return 'Supporting Technology'
            else:
                return 'Niche Technology'
        
        enhanced_analysis['strategic_category'] = enhanced_analysis['strategic_score'].apply(assign_strategic_category)
        
        return enhanced_analysis
    
    def generate_classification_intelligence_summary(self) -> Dict:
        """
        Generate comprehensive classification intelligence summary.
        
        Returns:
            Dictionary with classification intelligence insights
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        df = self.analyzed_data
        logger.debug("📋 Generating classification intelligence summary...")
        
        total_families = df['patent_families'].sum()
        top_domain = df.iloc[0] if len(df) > 0 else None
        
        summary = {
            'technology_overview': {
                'total_patent_families': int(total_families),
                'total_technology_domains': len(df),
                'dominant_technology': top_domain['technology_domain'] if top_domain is not None else 'N/A',
                'dominant_domain_share': float(top_domain['domain_share_pct']) if top_domain is not None else 0,
                'total_classifications': int(df['unique_classifications'].sum()),
                'avg_classifications_per_domain': float(df['unique_classifications'].mean())
            },
            'domain_distribution': df[['technology_domain', 'patent_families', 'domain_share_pct']].head(10).to_dict('records'),
            'maturity_analysis': df['technology_maturity'].value_counts().to_dict(),
            'strategic_categories': df['strategic_category'].value_counts().to_dict(),
            'innovation_metrics': {
                'avg_innovation_intensity': float(df['innovation_intensity'].mean()),
                'most_innovative_domain': df.loc[df['innovation_intensity'].idxmax(), 'technology_domain'] if not df.empty else 'N/A',
                'core_technologies': len(df[df['strategic_category'] == 'Core Technology']),
                'emerging_technologies': len(df[df['technology_maturity'] == 'Emerging'])
            },
            'temporal_insights': {
                'earliest_activity': int(df['first_filing_year'].min()) if not df.empty else None,
                'latest_activity': int(df['latest_filing_year'].max()) if not df.empty else None,
                'avg_activity_span': float(df['activity_span'].mean()),
                'most_sustained_domain': df.loc[df['activity_span'].idxmax(), 'technology_domain'] if not df.empty else 'N/A'
            }
        }
        
        # Add network insights if available
        if hasattr(self, 'network_graph') and self.network_graph:
            network_metrics = {
                'network_nodes': self.network_graph.number_of_nodes(),
                'network_edges': self.network_graph.number_of_edges(),
                'network_density': nx.density(self.network_graph),
                'most_connected_technology': max(nx.degree_centrality(self.network_graph).items(), key=lambda x: x[1])[0] if self.network_graph.number_of_nodes() > 0 else 'N/A'
            }
            summary['network_analysis'] = network_metrics
        
        self.classification_intelligence = summary
        return summary
    
    def get_top_technologies(self, top_n: int = 10, min_families: int = 1) -> pd.DataFrame:
        """
        Get top technology domains with filtering options.
        
        Args:
            top_n: Number of top domains to return
            min_families: Minimum number of patent families required
            
        Returns:
            Filtered DataFrame with top technology domains
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        filtered_df = self.analyzed_data[self.analyzed_data['patent_families'] >= min_families].copy()
        return filtered_df.head(top_n)
    
    def get_innovation_hotspots(self, top_n: int = 5) -> pd.DataFrame:
        """
        Get innovation hotspots based on multiple criteria.
        
        Args:
            top_n: Number of hotspots to return
            
        Returns:
            DataFrame with innovation hotspots
        """
        if self.analyzed_data is None:
            raise ValueError("No analyzed data available. Run analyze_search_results first.")
        
        # Sort by innovation intensity and strategic score
        hotspots = self.analyzed_data.sort_values(
            ['innovation_intensity', 'strategic_score'], 
            ascending=False
        ).head(top_n)
        
        return hotspots[['technology_domain', 'patent_families', 'innovation_intensity', 'strategic_category', 'technology_maturity']]
    
    def build_classification_network(self, min_cooccurrence: int = 2) -> nx.Graph:
        """
        Build and return the classification co-occurrence network.
        
        Args:
            min_cooccurrence: Minimum co-occurrence threshold for edges
            
        Returns:
            NetworkX graph of technology relationships
        """
        if self.network_graph is None:
            logger.warning("⚠️ No network graph available. Run analyze_search_results first.")
            return nx.Graph()
        
        # Filter edges by minimum co-occurrence
        filtered_graph = nx.Graph()
        for u, v, data in self.network_graph.edges(data=True):
            if data['weight'] >= min_cooccurrence:
                filtered_graph.add_edge(u, v, **data)
        
        return filtered_graph

    # Legacy methods for backward compatibility (deprecated)
    def _clean_classification_codes(self, df: pd.DataFrame, 
                                  ipc1_col: str, ipc2_col: str) -> pd.DataFrame:
        """Clean and standardize IPC/CPC classification codes."""
        logger.debug("🧹 Cleaning classification codes...")
        
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
        logger.debug("🏢 Adding domain classifications...")
        
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
        logger.debug("🕸️ Analyzing co-occurrence patterns...")
        
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
        logger.debug("📅 Adding temporal patterns...")
        
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
        logger.debug("💡 Calculating innovation metrics...")
        
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
        
        logger.debug("🕸️ Building classification network...")
        
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
        logger.debug(f"✅ Network built with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
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
        
        logger.debug("📋 Generating classification intelligence...")
        
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
            'technology_specific_insights': self._analyze_technology_specific_patterns(df)
        }
        
        self.classification_intelligence = intelligence
        return intelligence
    
    def _analyze_technology_specific_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze technology-specific classification patterns."""
        tech_patterns = {}
        
        # Check for technology-specific codes
        tech_codes = list(self.TECHNOLOGY_CLASSIFICATION_CODES.keys())
        tech_data = df[df['IPC_1'].str[:11].isin(tech_codes)]
        
        if len(tech_data) > 0:
            tech_patterns = {
                'technology_specific_records': len(tech_data),
                'technology_percentage': float(len(tech_data) / len(df) * 100),
                'technology_domain_distribution': tech_data['domain_1'].value_counts().to_dict(),
                'top_technology_classifications': tech_data['IPC_1'].value_counts().head(5).to_dict()
            }
        
        return tech_patterns
    
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
        logger.debug(f"📊 Processing {len(raw_data)} raw classification records...")
        
        # Convert to DataFrame
        df = pd.DataFrame(raw_data, columns=[
            'family_id', 'filing_year', 'IPC_1', 'IPC_2'
        ])
        
        # Data cleaning
        df = self._clean_classification_data(df)
        df = self._validate_classification_data(df)
        df = self._standardize_ipc_codes(df)
        
        logger.debug(f"✅ Processed to {len(df)} clean classification records")
        self.processed_data = df
        
        return df
    
    def _clean_classification_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean classification-specific data."""
        logger.debug("🧹 Cleaning classification data...")
        
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
        logger.debug("🔍 Validating classification data...")
        
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
            logger.debug(f"📊 Removed {removed_count} invalid records")
        
        return df
    
    def _standardize_ipc_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize IPC codes to consistent format."""
        logger.debug("🏷️ Standardizing IPC codes...")
        
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

def create_classification_analyzer(patstat_client: Optional[object] = None) -> ClassificationAnalyzer:
    """
    Factory function to create configured classification analyzer.
    
    Args:
        patstat_client: Optional PATSTAT client instance
        
    Returns:
        Configured ClassificationAnalyzer instance
    """
    return ClassificationAnalyzer(patstat_client=patstat_client)

def create_classification_processor() -> ClassificationDataProcessor:
    """
    Factory function to create configured classification data processor.
    
    Returns:
        Configured ClassificationDataProcessor instance
    """
    return ClassificationDataProcessor()

