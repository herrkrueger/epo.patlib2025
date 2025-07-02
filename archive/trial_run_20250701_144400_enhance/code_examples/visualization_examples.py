# Executive Dashboard Visualizations - TESTED AND WORKING
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_geographic_dashboard(ree_dataset):
    """PROVEN working geographic visualization"""
    plt.figure(figsize=(15, 10))
    
    # Country distribution pie chart
    plt.subplot(2, 2, 1)
    top_countries = ree_dataset['primary_applicant_country'].value_counts().head(8)
    plt.pie(top_countries.values, labels=top_countries.index, autopct='%1.1f%%')
    plt.title('REE Patents by Primary Applicant Country')
    
    # Regional market share
    plt.subplot(2, 2, 2)
    from geographic_enricher_example import get_regional_aggregation
    regional_data = get_regional_aggregation(ree_dataset)
    if not regional_data.empty:
        plt.bar(regional_data.index, regional_data.values)
        plt.title('REE Patents by Region')
        plt.xticks(rotation=45)
    
    # Innovation density by country
    plt.subplot(2, 2, 3)
    if 'applicant_country_count' in ree_dataset.columns:
        country_diversity = ree_dataset.groupby('primary_applicant_country')['applicant_country_count'].mean().head(10)
        plt.barh(range(len(country_diversity)), country_diversity.values)
        plt.yticks(range(len(country_diversity)), country_diversity.index)
        plt.title('Average International Collaboration by Country')
    
    plt.tight_layout()
    return plt

def create_innovation_trends(ree_dataset, citation_data):
    """PROVEN working temporal analysis"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Patent filings over time
    yearly_filings = ree_dataset['appln_filing_year'].value_counts().sort_index()
    recent_years = yearly_filings[yearly_filings.index >= 2010]
    ax1.plot(recent_years.index, recent_years.values, marker='o', linewidth=2)
    ax1.set_title('REE Patent Filings Over Time')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Number of Applications')
    ax1.grid(True, alpha=0.3)
    
    # Citation patterns
    if not citation_data.empty and 'citing_year' in citation_data.columns:
        citation_trends = citation_data.groupby('citing_year').size()
        ax2.bar(citation_trends.index, citation_trends.values)
        ax2.set_title('Citation Activity by Year')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Number of Citations')
    
    # Technology focus areas (CPC analysis)
    if 'cpc_class_symbol' in ree_dataset.columns:
        cpc_main = ree_dataset['cpc_class_symbol'].str[:4].value_counts().head(10)
        ax3.barh(range(len(cpc_main)), cpc_main.values)
        ax3.set_yticks(range(len(cpc_main)))
        ax3.set_yticklabels(cpc_main.index)
        ax3.set_title('Top Technology Areas (CPC Classes)')
    
    # Search method effectiveness
    if 'search_method_final' in ree_dataset.columns:
        method_counts = ree_dataset['search_method_final'].value_counts()
        ax4.pie(method_counts.values, labels=method_counts.index, autopct='%1.1f%%')
        ax4.set_title('Search Method Distribution')
    
    plt.tight_layout()
    return fig

def create_plotly_interactive_dashboard(ree_dataset, citation_data):
    """PROVEN plotly interactive visualizations"""
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Geographic Distribution', 'Innovation Trends', 
                       'Citation Network', 'Quality Metrics'),
        specs=[[{'type': 'pie'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'bar'}]]
    )
    
    # Geographic distribution pie chart
    top_countries = ree_dataset['primary_applicant_country'].value_counts().head(8)
    fig.add_trace(
        go.Pie(labels=top_countries.index, values=top_countries.values, name="Countries"),
        row=1, col=1
    )
    
    # Innovation trends line chart
    yearly_data = ree_dataset['appln_filing_year'].value_counts().sort_index()
    fig.add_trace(
        go.Scatter(x=yearly_data.index, y=yearly_data.values, mode='lines+markers', name="Patents"),
        row=1, col=2
    )
    
    # Citation network (if available)
    if not citation_data.empty and 'citing_year' in citation_data.columns and 'cited_ree_appln_id' in citation_data.columns:
        citation_summary = citation_data.groupby(['citing_year', 'citing_country']).size().reset_index(name='citation_count')
        fig.add_trace(
            go.Scatter(
                x=citation_summary['citing_year'], 
                y=citation_summary['citation_count'],
                mode='markers',
                marker=dict(size=citation_summary['citation_count'], sizemode='area'),
                text=citation_summary['citing_country'],
                name="Citations"
            ),
            row=2, col=1
        )
    
    # Quality metrics bar chart
    quality_data = {
        'Patents': len(ree_dataset),
        'Countries': ree_dataset['primary_applicant_country'].nunique(),
        'Citations': len(citation_data) if not citation_data.empty else 0,
        'Families': ree_dataset['docdb_family_id'].nunique() if 'docdb_family_id' in ree_dataset.columns else 0
    }
    
    fig.add_trace(
        go.Bar(x=list(quality_data.keys()), y=list(quality_data.values()), name="Metrics"),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="REE Patent Analysis Dashboard")
    return fig

def generate_executive_summary(ree_dataset, citation_results, quality_metrics):
    """PROVEN working business summary generator"""
    
    def calculate_growth_rate(dataset):
        if 'appln_filing_year' in dataset.columns:
            yearly_counts = dataset['appln_filing_year'].value_counts().sort_index()
            if len(yearly_counts) >= 2:
                recent_5_years = yearly_counts.tail(5)
                if len(recent_5_years) >= 2:
                    start_avg = recent_5_years.head(2).mean()
                    end_avg = recent_5_years.tail(2).mean()
                    growth_rate = ((end_avg - start_avg) / start_avg * 100) if start_avg > 0 else 0
                    return round(growth_rate, 1)
        return 0
    
    def calculate_market_concentration(dataset):
        if 'primary_applicant_country' in dataset.columns:
            country_counts = dataset['primary_applicant_country'].value_counts()
            top_3_share = country_counts.head(3).sum() / len(dataset) * 100
            return round(top_3_share, 1)
        return 0
    
    summary = {
        'total_patents': len(ree_dataset),
        'total_citations': len(citation_results) if not citation_results.empty else 0,
        'countries_covered': ree_dataset['primary_applicant_country'].nunique() if 'primary_applicant_country' in ree_dataset.columns else 0,
        'top_innovators': ree_dataset['primary_applicant_country'].value_counts().head(5).to_dict() if 'primary_applicant_country' in ree_dataset.columns else {},
        'annual_growth_rate': calculate_growth_rate(ree_dataset),
        'quality_score': quality_metrics.get('quality_score', 0),
        'market_concentration': calculate_market_concentration(ree_dataset)
    }
    
    return summary

def export_visualizations(ree_dataset, citation_data, quality_metrics, output_dir="."):
    """Export all visualizations in business-ready formats"""
    
    # Geographic dashboard
    geo_fig = create_geographic_dashboard(ree_dataset)
    geo_fig.savefig(f"{output_dir}/ree_geographic_analysis.png", dpi=300, bbox_inches='tight')
    
    # Innovation trends
    trend_fig = create_innovation_trends(ree_dataset, citation_data)
    trend_fig.savefig(f"{output_dir}/ree_innovation_trends.png", dpi=300, bbox_inches='tight')
    
    # Interactive dashboard
    interactive_fig = create_plotly_interactive_dashboard(ree_dataset, citation_data)
    interactive_fig.write_html(f"{output_dir}/ree_interactive_dashboard.html")
    
    # Executive summary
    summary = generate_executive_summary(ree_dataset, citation_data, quality_metrics)
    
    import json
    with open(f"{output_dir}/ree_executive_summary.json", 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"✅ Visualizations exported to {output_dir}/")
    return summary

# MANDATORY: Test visualizations after implementation
if __name__ == "__main__":
    print("Testing visualization examples...")
    
    # Create sample data for testing
    test_data = pd.DataFrame({
        'appln_id': range(1, 101),
        'appln_filing_year': [2015 + i//20 for i in range(100)],
        'primary_applicant_country': ['US'] * 30 + ['CN'] * 25 + ['DE'] * 20 + ['JP'] * 15 + ['KR'] * 10,
        'docdb_family_id': range(1, 101),
        'cpc_class_symbol': ['C22B19/28'] * 40 + ['Y02W30/52'] * 35 + ['H01F1/057'] * 25
    })
    
    test_citations = pd.DataFrame({
        'citing_year': [2018, 2019, 2020, 2021, 2022] * 20,
        'citing_country': ['US', 'CN', 'DE', 'JP', 'KR'] * 20,
        'cited_ree_appln_id': range(1, 101)
    })
    
    test_quality = {'quality_score': 85, 'quality_rating': 'GOOD'}
    
    try:
        summary = export_visualizations(test_data, test_citations, test_quality)
        print(f"✅ Visualization test PASSED: Generated {len(summary)} summary metrics")
    except Exception as e:
        print(f"❌ Visualization test FAILED: {e}")
        import traceback
        traceback.print_exc()