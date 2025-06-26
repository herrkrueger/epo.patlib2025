# 4.1 Geographic Data Enhancement using Direct SQL
import pandas as pd
from datetime import datetime

def enrich_with_geographic_data(db, ree_df):
    """
    Add country codes and geographic information
    Uses direct SQL queries to avoid ORM complications
    """
    
    if ree_df.empty:
        print("No REE data provided for geographic enrichment")
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    # Get geographic data through person-application links
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.iso_alpha3,
        c.st3_name as country_name,
        pa.applt_seq_nr,
        pa.invt_seq_nr
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    """
    
    print("Enriching with geographic data...")
    geo_data = pd.read_sql(geo_query, db.bind)
    
    if not geo_data.empty:
        # Merge with REE data
        enriched_df = ree_df.merge(
            geo_data, 
            on='appln_id', 
            how='left'
        )
        print(f"Geographic enrichment: {len(geo_data)} geographic records added")
        return enriched_df
    else:
        print("No geographic data found")
        return ree_df

def analyze_country_citations(forward_citations_df, backward_citations_df):
    """
    Analyze citation flows between countries
    Uses direct DataFrame operations
    """
    
    print(f"\n{'='*40}")
    print("COUNTRY CITATION ANALYSIS")
    print(f"{'='*40}")
    
    citation_flows = pd.DataFrame()
    top_citing = pd.Series()
    
    if not forward_citations_df.empty:
        # Top citing countries
        if 'citing_country' in forward_citations_df.columns:
            top_citing = forward_citations_df['citing_country'].value_counts().head(10)
            print(f"Top citing countries: {top_citing.to_dict()}")
        
        # Citation flows analysis
        if 'citing_country' in forward_citations_df.columns:
            citation_flows = forward_citations_df.groupby('citing_country').agg({
                'citing_publn_id': 'nunique',
                'cited_ree_appln_id': 'nunique'
            }).reset_index()
            
            citation_flows.columns = ['country', 'citing_patents', 'cited_ree_patents']
            citation_flows = citation_flows.sort_values('citing_patents', ascending=False)
            
            print(f"Citation flows identified: {len(citation_flows)} countries")
            print("Top citation flows:")
            print(citation_flows.head())
    
    print(f"{'='*40}")
    return citation_flows, top_citing

def create_country_summary(enriched_ree_df):
    """Create summary statistics by country"""
    
    if 'country_name' not in enriched_ree_df.columns:
        print("No country data available for summary")
        return pd.DataFrame()
    
    country_summary = enriched_ree_df.groupby('country_name').agg({
        'appln_id': 'count',
        'docdb_family_id': 'nunique',
        'appln_filing_year': ['min', 'max', 'mean']
    }).round(2)
    
    country_summary.columns = ['total_applications', 'unique_families', 'first_year', 'last_year', 'avg_year']
    country_summary = country_summary.sort_values('total_applications', ascending=False)
    
    print(f"\n{'='*50}")
    print("COUNTRY SUMMARY (Top 10)")
    print(f"{'='*50}")
    print(country_summary.head(10))
    print(f"{'='*50}")
    
    return country_summary

def analyze_geographic_trends(enriched_ree_df):
    """
    Analyze geographic trends over time
    """
    
    if 'country_name' not in enriched_ree_df.columns or 'appln_filing_year' not in enriched_ree_df.columns:
        print("Missing required columns for geographic trend analysis")
        return pd.DataFrame()
    
    # Year-over-year trends by country
    yearly_trends = enriched_ree_df.groupby(['appln_filing_year', 'country_name']).agg({
        'appln_id': 'count'
    }).reset_index()
    
    yearly_trends.columns = ['year', 'country', 'patent_count']
    
    # Get top countries for trend analysis
    top_countries = enriched_ree_df['country_name'].value_counts().head(5).index.tolist()
    yearly_trends_top = yearly_trends[yearly_trends['country'].isin(top_countries)]
    
    print(f"\nGeographic trends for top {len(top_countries)} countries:")
    print(yearly_trends_top.head(10))
    
    return yearly_trends_top

def get_country_coordinates():
    """
    Get basic country coordinates for visualization
    Returns dictionary with country names and their coordinates
    """
    
    country_coords = {
        'United States': {'lat': 39.8283, 'lon': -98.5795},
        'China': {'lat': 35.8617, 'lon': 104.1954},
        'Japan': {'lat': 36.2048, 'lon': 138.2529},
        'Germany': {'lat': 51.1657, 'lon': 10.4515},
        'South Korea': {'lat': 35.9078, 'lon': 127.7669},
        'United Kingdom': {'lat': 55.3781, 'lon': -3.4360},
        'France': {'lat': 46.6034, 'lon': 1.8883},
        'Canada': {'lat': 56.1304, 'lon': -106.3468},
        'Australia': {'lat': -25.2744, 'lon': 133.7751},
        'India': {'lat': 20.5937, 'lon': 78.9629},
        'Brazil': {'lat': -14.2350, 'lon': -51.9253},
        'Russia': {'lat': 61.5240, 'lon': 105.3188},
        'Italy': {'lat': 41.8719, 'lon': 12.5674},
        'Netherlands': {'lat': 52.1326, 'lon': 5.2913},
        'Sweden': {'lat': 60.1282, 'lon': 18.6435},
        'Switzerland': {'lat': 46.8182, 'lon': 8.2275},
        'Belgium': {'lat': 50.5039, 'lon': 4.4699},
        'Spain': {'lat': 40.4637, 'lon': -3.7492},
        'Austria': {'lat': 47.5162, 'lon': 14.5501},
        'Denmark': {'lat': 56.2639, 'lon': 9.5018}
    }
    
    return country_coords

if __name__ == "__main__":
    # Test geographic analysis
    print("Testing geographic enrichment...")
    from database_connection import get_database_connection
    from ree_dataset_builder import build_ree_dataset
    
    db = get_database_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            enriched_data = enrich_with_geographic_data(db, ree_data)
            country_summary = create_country_summary(enriched_data)
            geographic_trends = analyze_geographic_trends(enriched_data)
            coords = get_country_coordinates()
            print(f"Country coordinates available for {len(coords)} countries")