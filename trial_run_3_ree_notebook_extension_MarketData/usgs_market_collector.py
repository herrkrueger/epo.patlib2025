"""
USGS Market Data Collector - REE Market Intelligence Extension
Source: USGS Mineral Commodity Summaries integration
Built for EPO TIP Platform / PATLIB 2025 demonstration
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import logging

class USGSMarketDataCollector:
    """
    USGS Mineral Commodity Summaries integration
    Handles REE market data, price trends, and supply analysis
    """
    
    def __init__(self, data_file_path: str = "usgs_market_data/ree_market_data.json"):
        self.data_file = Path(data_file_path)
        self.ree_commodities = [
            'rare_earths', 'neodymium', 'dysprosium', 'yttrium',
            'cerium', 'lanthanum', 'terbium', 'europium'
        ]
        self.market_data = None
        self.logger = logging.getLogger(__name__)
    
    def load_market_data(self) -> Dict:
        """Load USGS market data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                self.market_data = json.load(f)
            self.logger.info(f"Loaded USGS market data from {self.data_file}")
            return self.market_data
        except FileNotFoundError:
            self.logger.error(f"Market data file not found: {self.data_file}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in market data: {e}")
            raise
    
    def get_price_trends(self, element: str = 'neodymium') -> pd.DataFrame:
        """Extract price trend data for specific REE element"""
        if not self.market_data:
            self.load_market_data()
        
        price_key = f"{element}_price_index"
        if price_key in self.market_data.get('price_trends', {}):
            price_data = self.market_data['price_trends'][price_key]
            df = pd.DataFrame(list(price_data.items()), columns=['year', 'price_index'])
            df['year'] = pd.to_numeric(df['year'])
            df = df.sort_values('year')
            return df
        else:
            self.logger.warning(f"No price data found for {element}")
            return pd.DataFrame()
    
    def get_import_dependency_data(self) -> Dict[str, float]:
        """Get US import dependency percentages by REE"""
        if not self.market_data:
            self.load_market_data()
        
        return self.market_data.get('import_dependency', {})
    
    def get_global_production_data(self) -> pd.DataFrame:
        """Get global production data by country and year"""
        if not self.market_data:
            self.load_market_data()
        
        production_data = self.market_data.get('global_production', {})
        
        records = []
        for country, yearly_data in production_data.items():
            for year, production in yearly_data.items():
                records.append({
                    'country': country,
                    'year': int(year),
                    'production_tons': production
                })
        
        df = pd.DataFrame(records)
        return df.sort_values(['year', 'country'])
    
    def calculate_supply_concentration(self) -> Dict[str, float]:
        """Calculate market concentration metrics (China dominance)"""
        production_df = self.get_global_production_data()
        if production_df.empty:
            return {}
        
        # Get latest year data
        latest_year = production_df['year'].max()
        latest_data = production_df[production_df['year'] == latest_year]
        
        total_production = latest_data['production_tons'].sum()
        
        concentration_metrics = {}
        for country in latest_data['country'].unique():
            country_production = latest_data[latest_data['country'] == country]['production_tons'].sum()
            concentration_metrics[country] = (country_production / total_production) * 100
        
        return concentration_metrics
    
    def identify_price_shock_periods(self, threshold: float = 50.0) -> List[Dict]:
        """Identify periods of significant price volatility"""
        price_df = self.get_price_trends('neodymium')
        if price_df.empty:
            return []
        
        price_df['price_change'] = price_df['price_index'].pct_change() * 100
        
        shock_periods = []
        for idx, row in price_df.iterrows():
            if abs(row['price_change']) > threshold:
                shock_periods.append({
                    'year': row['year'],
                    'price_index': row['price_index'],
                    'price_change_percent': row['price_change'],
                    'shock_type': 'spike' if row['price_change'] > 0 else 'crash'
                })
        
        return shock_periods
    
    def get_market_events_timeline(self) -> List[Dict]:
        """Get key market disruption events for correlation analysis"""
        if not self.market_data:
            self.load_market_data()
        
        events_data = self.market_data.get('market_events', {})
        timeline = []
        
        for year_str, event_description in events_data.items():
            timeline.append({
                'year': int(year_str),
                'event': event_description,
                'description': event_description
            })
        
        return sorted(timeline, key=lambda x: x['year'])

# Testing function
def test_usgs_collector():
    """Test USGS market data collector functionality"""
    collector = USGSMarketDataCollector()
    
    # Test data loading
    market_data = collector.load_market_data()
    assert market_data is not None, "Failed to load market data"
    print("✅ Market data loaded successfully")
    
    # Test price trends
    price_df = collector.get_price_trends('neodymium')
    assert not price_df.empty, "Failed to get price trends"
    print(f"✅ Price trends: {len(price_df)} years of data")
    
    # Test import dependency
    import_data = collector.get_import_dependency_data()
    assert import_data, "Failed to get import dependency data"
    print(f"✅ Import dependency data: {len(import_data)} elements")
    
    # Test production data
    production_df = collector.get_global_production_data()
    assert not production_df.empty, "Failed to get production data"
    print(f"✅ Production data: {len(production_df)} records")
    
    # Test concentration metrics
    concentration = collector.calculate_supply_concentration()
    assert concentration, "Failed to calculate concentration metrics"
    print(f"✅ Supply concentration: {len(concentration)} countries")
    
    # Test price shock detection
    shocks = collector.identify_price_shock_periods()
    print(f"✅ Price shocks identified: {len(shocks)} periods")
    
    # Test market events timeline
    events = collector.get_market_events_timeline()
    print(f"✅ Market events timeline: {len(events)} events")
    
    print("\n🎯 All USGS market data tests passed!")
    return True

if __name__ == "__main__":
    test_usgs_collector()