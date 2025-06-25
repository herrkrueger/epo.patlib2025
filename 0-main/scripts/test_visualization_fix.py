#!/usr/bin/env python3
"""
Quick test script to verify visualization configuration fix.
"""

import sys
from pathlib import Path
import pandas as pd

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from config import ConfigurationManager
from visualizations import ProductionDashboardCreator

def test_visualization_fix():
    """Test that visualizations can access configuration properly."""
    print("🎨 Testing Visualization Configuration Fix")
    print("=" * 50)
    
    try:
        # Create configuration manager
        print("⚙️ Creating configuration manager...")
        config = ConfigurationManager()
        print("✅ Configuration manager created")
        
        # Test dashboard creator
        print("📊 Creating dashboard creator...")
        dashboard_creator = ProductionDashboardCreator(config)
        print("✅ Dashboard creator initialized successfully")
        
        # Create mock data for dashboard test
        mock_data = {
            'applicant': pd.DataFrame({'entity': ['Test Corp'], 'count': [10]}),
            'geographic': pd.DataFrame({'country': ['US'], 'count': [5]}),
            'classification': pd.DataFrame({'tech': ['AI'], 'count': [3]}),
            'citation': pd.DataFrame({'year': [2024], 'citations': [8]})
        }
        
        print("📈 Testing dashboard creation...")
        dashboard = dashboard_creator.create_executive_dashboard(
            mock_data,
            title="Test Dashboard"
        )
        print("✅ Dashboard creation successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_visualization_fix()
    if success:
        print("🎉 Visualization layer is working! Ready for notebook.")
    else:
        print("⚠️ Visualization layer needs more fixes.")