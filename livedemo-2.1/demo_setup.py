#!/usr/bin/env python3
"""
Patent Analysis Demo Setup Script
Prepares the environment for live notebook enhancement demonstration
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def create_demo_structure():
    """Create the standardized demo file structure"""
    
    base_dir = Path("patent_demo")
    dirs = [
        "data",
        "notebooks", 
        "templates",
        "outputs",
        "config"
    ]
    
    # Create directories
    for dir_name in dirs:
        (base_dir / dir_name).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {base_dir / dir_name}")
    
    return base_dir

def install_required_packages():
    """Install packages needed for the demo"""
    
    packages = [
        "pandas",
        "matplotlib", 
        "plotly",
        "requests",
        "jupyter",
        "seaborn",
        "wordcloud",
        "networkx",
        "folium",
        "openpyxl"
    ]
    
    print("Installing required packages...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")

def create_sample_data():
    """Create sample patent data for offline demonstration"""
    
    sample_patents = [
        {
            "publication_number": "EP3234567A1",
            "title": "Machine Learning Method for Patent Classification",
            "abstract": "A novel approach to automatically classify patents using deep learning...",
            "applicant": "Tech Corp International",
            "inventor": "Dr. Anna Schmidt; Prof. Jan Mueller",
            "ipc_class": "G06N 20/00",
            "cpc_class": "G06N20/00",
            "filing_date": "2023-03-15",
            "publication_date": "2024-09-18",
            "priority_date": "2022-03-15",
            "citations_forward": 12,
            "citations_backward": 45,
            "family_size": 5,
            "countries": ["EP", "US", "JP", "CN", "KR"],
            "legal_status": "Granted"
        },
        {
            "publication_number": "EP3345678A1", 
            "title": "Blockchain-based Patent Protection System",
            "abstract": "System and method for protecting intellectual property using blockchain...",
            "applicant": "Innovation Labs GmbH",
            "inventor": "Michael Weber; Sarah Johnson",
            "ipc_class": "G06F 21/60",
            "cpc_class": "G06F21/602",
            "filing_date": "2023-06-20",
            "publication_date": "2024-12-25",
            "priority_date": "2022-06-20", 
            "citations_forward": 8,
            "citations_backward": 32,
            "family_size": 3,
            "countries": ["EP", "US", "CN"],
            "legal_status": "Pending"
        },
        # Add more sample patents...
    ]
    
    # Save sample data
    data_file = Path("patent_demo/data/sample_patents.json")
    with open(data_file, 'w') as f:
        json.dump(sample_patents, f, indent=2)
    
    print(f"✓ Created sample data: {data_file}")

def create_config_files():
    """Create configuration files for the demo"""
    
    config = {
        "epo_ops": {
            "base_url": "https://ops.epo.org/3.2/rest-services",
            "consumer_key": "YOUR_KEY_HERE",
            "consumer_secret": "YOUR_SECRET_HERE"
        },
        "demo_settings": {
            "default_search_limit": 100,
            "visualization_theme": "professional",
            "output_format": "pdf",
            "cache_results": True
        },
        "patlib_contacts": {
            "germany": "https://www.dpma.de/english/services/patent_information/patlib/index.html",
            "europe": "https://www.epo.org/en/searching-for-patents/helpful-resources/support/patlib"
        }
    }
    
    config_file = Path("patent_demo/config/demo_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created config file: {config_file}")

def create_templates():
    """Create code templates for live enhancement"""
    
    templates = {
        "api_call": '''
def enhanced_epo_search(query, filters=None):
    """Enhanced EPO API search with error handling"""
    import requests
    import time
    
    headers = {"Accept": "application/json"}
    params = {"q": query}
    
    if filters:
        params.update(filters)
    
    try:
        response = requests.get(EPO_OPS_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API Error: {e}")
        return None
''',
        
        "visualization": '''
def create_patent_landscape_plot(df):
    """Create interactive patent landscape visualization"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    fig = px.scatter(df, 
                     x='filing_date', 
                     y='citations_forward',
                     size='family_size',
                     color='applicant',
                     hover_data=['title', 'ipc_class'])
    
    fig.update_layout(title="Patent Landscape Analysis",
                      xaxis_title="Filing Date",
                      yaxis_title="Forward Citations")
    
    return fig
''',

        "report_generator": '''
def generate_executive_report(analysis_results):
    """Generate professional executive summary"""
    from datetime import datetime
    
    report = f"""
    PATENT LANDSCAPE ANALYSIS REPORT
    Generated: {datetime.now().strftime('%Y-%m-%d')}
    
    EXECUTIVE SUMMARY
    ================
    Total Patents Analyzed: {len(analysis_results)}
    Key Technology Areas: {', '.join(analysis_results['top_ipc_classes'])}
    Leading Companies: {', '.join(analysis_results['top_applicants'])}
    
    STRATEGIC RECOMMENDATIONS
    ========================
    1. Technology Opportunities: {analysis_results['white_spaces']}
    2. Competitive Threats: {analysis_results['competitor_activity']}
    3. Filing Strategy: {analysis_results['filing_recommendations']}
    """
    
    return report
'''
    }
    
    templates_dir = Path("patent_demo/templates")
    for name, code in templates.items():
        template_file = templates_dir / f"{name}_template.py"
        with open(template_file, 'w') as f:
            f.write(code)
        print(f"✓ Created template: {template_file}")

def main():
    """Main setup function"""
    print("🚀 Setting up Patent Analysis Demo Environment")
    print("=" * 50)
    
    # Create directory structure
    base_dir = create_demo_structure()
    
    # Install packages
    install_required_packages()
    
    # Create sample data
    create_sample_data()
    
    # Create config files
    create_config_files()
    
    # Create templates
    create_templates()
    
    print("\n" + "=" * 50)
    print("✅ Demo environment setup complete!")
    print(f"📁 Base directory: {base_dir.absolute()}")
    print("\nNext steps:")
    print("1. Copy the base notebook to the notebooks/ directory")
    print("2. Copy CLAUDE.md to the base directory") 
    print("3. Test the setup by running jupyter notebook")
    print("4. Practice the live enhancement flow")
    print("\n🎯 Ready for your PATLIB presentation!")

if __name__ == "__main__":
    main()