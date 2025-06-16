"""
EPO PATLIB 2025 Demo Safety Utilities
Enhanced error handling and fallback data for live demonstrations
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

class DemoSafetyManager:
    """
    Manages fallback data and error handling for live demos
    """
    
    def __init__(self):
        self.fallback_data = self._create_fallback_data()
        self.connection_status = {'patstat': False, 'demo_mode': False}
        
    def _create_fallback_data(self):
        """Create realistic fallback data for each notebook"""
        
        # Notebook 1: REE Ranking Applicants fallback
        applicants_data = {
            'Applicant': [
                'JIANGXI UNIVERSITY OF SCIENCE AND TECHNOLOGY',
                'CHINESE ACADEMY OF SCIENCES', 
                'BAOTOU IRON & STEEL (GROUP) COMPANY',
                'BAOTOU RESEARCH INSTITUTE OF RARE EARTHS',
                'NORTHEASTERN UNIVERSITY',
                'TOYOTA MOTOR CORPORATION',
                'SUMITOMO ELECTRIC INDUSTRIES',
                'SIEMENS AG',
                'GENERAL ELECTRIC COMPANY',
                'UNIVERSITY OF CALIFORNIA'
            ],
            'Patent_Families': [179, 103, 68, 51, 47, 35, 28, 22, 19, 15],
            'First_Year': [2010, 2011, 2012, 2010, 2013, 2014, 2011, 2012, 2013, 2015],
            'Latest_Year': [2022, 2022, 2021, 2020, 2022, 2021, 2020, 2019, 2021, 2022]
        }
        
        # Notebook 2: Geographic Family Size fallback
        geographic_data = {
            'country_name': ['China', 'United States', 'Japan', 'South Korea', 'Germany'] * 3,
            'filing_year': [2015, 2015, 2015, 2015, 2015, 2018, 2018, 2018, 2018, 2018, 2021, 2021, 2021, 2021, 2021],
            'avg_family_size': [2.8, 4.2, 6.1, 3.9, 5.2, 3.1, 4.8, 6.8, 4.3, 5.9, 3.5, 5.2, 7.2, 4.8, 6.4],
            'unique_families': [850, 320, 180, 95, 75, 920, 380, 210, 120, 85, 1050, 420, 240, 140, 95]
        }
        
        # Notebook 3: Technology Network fallback
        network_data = {
            'IPC_1': ['C22B  19', 'C04B  18', 'H01M  10', 'C09K  11', 'C22B  25'],
            'IPC_2': ['C04B  18', 'H01M  10', 'C09K  11', 'H01J   9', 'C04B  18'],
            'total_co_occurrences': [15, 12, 8, 6, 5],
            'domain_1': ['Metallurgy & Extraction', 'Ceramics & Materials', 'Batteries & Energy Storage', 'Phosphors & Luminescence', 'Metallurgy & Extraction'],
            'domain_2': ['Ceramics & Materials', 'Batteries & Energy Storage', 'Phosphors & Luminescence', 'Electronic Devices', 'Ceramics & Materials']
        }
        
        return {
            'applicants': pd.DataFrame(applicants_data),
            'geographic': pd.DataFrame(geographic_data),
            'network': pd.DataFrame(network_data)
        }
    
    def check_patstat_connection(self):
        """Test PATSTAT connection with graceful fallback"""
        try:
            from epo.tipdata.patstat import PatstatClient
            patstat = PatstatClient(env='PROD')
            db = patstat.orm()
            # Test query
            test_query = db.execute("SELECT 1 as test").fetchone()
            self.connection_status['patstat'] = True
            return True, "PATSTAT connection successful"
        except Exception as e:
            self.connection_status['patstat'] = False
            self.connection_status['demo_mode'] = True
            return False, f"PATSTAT unavailable: {str(e)[:100]}..."
    
    def safe_query_execution(self, query_func, fallback_key, description="query"):
        """
        Execute query with automatic fallback to demo data
        """
        try:
            if self.connection_status['patstat']:
                result = query_func()
                print(f"✅ {description} executed successfully")
                return result, True
            else:
                raise Exception("PATSTAT not available")
        except Exception as e:
            print(f"⚠️ {description} failed: {str(e)[:50]}...")
            print(f"🔄 Using fallback demo data for {fallback_key}")
            return self.fallback_data[fallback_key], False
    
    def create_demo_notification(self, is_live_data=True):
        """Create notification about data source"""
        if is_live_data:
            return "🔴 LIVE DATA from PATSTAT"
        else:
            return "🟡 DEMO DATA (PATSTAT unavailable)"
    
    def safe_visualization(self, viz_func, title_prefix=""):
        """Create visualization with error handling"""
        try:
            fig = viz_func()
            if not self.connection_status['patstat']:
                # Add demo mode indicator
                fig.add_annotation(
                    text="⚠️ DEMO MODE - Sample Data",
                    xref="paper", yref="paper",
                    x=1, y=1, xanchor="right", yanchor="top",
                    bgcolor="yellow", bordercolor="red",
                    font=dict(size=12, color="red")
                )
            return fig
        except Exception as e:
            # Create error visualization
            fig = go.Figure()
            fig.add_annotation(
                text=f"Visualization Error: {str(e)[:50]}...<br>Please check data and try again",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor="center", yanchor="middle",
                font=dict(size=14, color="red")
            )
            fig.update_layout(title=f"{title_prefix} - Error Recovery")
            return fig


class LiveDemoEnhancements:
    """
    Live coding enhancements that can be added during demo
    """
    
    @staticmethod
    def add_market_share_analysis(df):
        """Quick enhancement: Add market share calculations"""
        df = df.copy()
        df['Market_Share_Pct'] = (df['Patent_Families'] / df['Patent_Families'].sum() * 100).round(2)
        df['Portfolio_Size'] = pd.cut(df['Patent_Families'], 
                                     bins=[0, 5, 20, 50, float('inf')],
                                     labels=['Emerging', 'Active', 'Major', 'Dominant'])
        return df
    
    @staticmethod
    def add_geographic_intelligence(df):
        """Quick enhancement: Add geographic insights"""
        df = df.copy()
        df['filing_strategy'] = pd.cut(
            df['avg_family_size'],
            bins=[0, 2, 5, 10, float('inf')],
            labels=['Domestic Focus', 'Regional Strategy', 'Global Strategy', 'Premium Global']
        )
        return df
    
    @staticmethod
    def add_network_metrics(connections_df):
        """Quick enhancement: Add network analysis metrics"""
        df = connections_df.copy()
        df['is_cross_domain'] = df['domain_1'] != df['domain_2']
        df['connection_strength'] = pd.cut(
            df['total_co_occurrences'],
            bins=[0, 3, 7, 15, float('inf')],
            labels=['Weak', 'Moderate', 'Strong', 'Very Strong']
        )
        return df
    
    @staticmethod
    def create_executive_summary(data_dict):
        """Generate executive summary for any dataset"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        summary = {
            'analysis_timestamp': timestamp,
            'data_quality': 'Live PATSTAT data' if data_dict.get('is_live', False) else 'Demo data',
            'key_insights': [],
            'strategic_recommendations': []
        }
        
        # Add dataset-specific insights
        if 'applicants' in data_dict:
            df = data_dict['applicants']
            summary['key_insights'].extend([
                f"Market leader: {df.iloc[0]['Applicant']} with {df.iloc[0]['Patent_Families']} families",
                f"Top 5 players control {df.head(5)['Patent_Families'].sum()} total families",
                f"Geographic focus: Strong Asian presence in top rankings"
            ])
        
        return summary


def demo_error_handler(func):
    """Decorator for safe demo execution"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"⚠️ Demo error in {func.__name__}: {str(e)[:50]}...")
            print("🔄 Continuing with fallback approach...")
            return None
    return wrapper


# Pre-built recovery functions
def create_connection_test_cell():
    """Generate code for testing PATSTAT connection"""
    return '''
# 🧪 PATSTAT CONNECTION TEST
safety_manager = DemoSafetyManager()
is_connected, message = safety_manager.check_patstat_connection()

print(f"Connection Status: {message}")
if is_connected:
    print("🔴 LIVE DEMO MODE - Using real PATSTAT data")
else:
    print("🟡 DEMO MODE - Using prepared sample data")
    print("   (Perfect for showing Claude Code capabilities!)")
'''

def create_fallback_data_showcase():
    """Generate code to showcase fallback data"""
    return '''
# 📊 DEMO DATA SHOWCASE
print("Sample of available demo data:")
for key, df in safety_manager.fallback_data.items():
    print(f"\\n{key.upper()} DATA:")
    print(df.head())
    print(f"Shape: {df.shape}")
'''

# Export safety utilities
__all__ = [
    'DemoSafetyManager', 
    'LiveDemoEnhancements', 
    'demo_error_handler',
    'create_connection_test_cell',
    'create_fallback_data_showcase'
]