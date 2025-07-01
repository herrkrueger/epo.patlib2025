import pandas as pd

def enrich_with_geographic_data(db, ree_df):
    """Add country information using verified table relationships"""
    
    if ree_df.empty:
        print("⚠️ Empty dataset provided for geographic enrichment")
        return ree_df
    
    appln_ids_str = ','.join(map(str, ree_df['appln_id']))
    
    geo_query = f"""
    SELECT DISTINCT
        pa.appln_id,
        p.person_ctry_code,
        c.st3_name as country_name
    FROM tls207_pers_appln pa
    JOIN tls206_person p ON pa.person_id = p.person_id
    JOIN tls801_country c ON p.person_ctry_code = c.ctry_code
    WHERE pa.appln_id IN ({appln_ids_str})
    AND pa.applt_seq_nr > 0
    """
    
    try:
        geo_data = pd.read_sql(geo_query, db.bind)
        
        if not geo_data.empty:
            print(f"Found geographic data for {geo_data['appln_id'].nunique()} applications")
            enriched_df = ree_df.merge(geo_data, on='appln_id', how='left')
            return enriched_df
        else:
            print("ℹ️  No geographic data found - using filing authority as fallback")
            return ree_df
            
    except Exception as e:
        print(f"⚠️ Geographic enrichment failed: {e}")
        print("Using filing authority (appln_auth) as geographic information")
        return ree_df

def analyze_country_citations(forward_citations_df):
    """Analyze citation flows between countries"""
    
    if forward_citations_df.empty:
        print("ℹ️  No forward citations to analyze")
        return pd.Series()
    
    try:
        top_citing = forward_citations_df['citing_country'].value_counts().head(10)
        print(f"Top citing countries: {top_citing.to_dict()}")
        return top_citing
        
    except Exception as e:
        print(f"⚠️ Citation country analysis failed: {e}")
        return pd.Series()

def get_geographic_distribution(ree_df):
    """Analyze geographic distribution of REE patents"""
    
    if ree_df.empty:
        print("⚠️ Empty dataset for geographic distribution analysis")
        return {}
    
    geographic_stats = {}
    
    # Primary distribution by filing authority
    if 'appln_auth' in ree_df.columns:
        auth_distribution = ree_df['appln_auth'].value_counts()
        geographic_stats['filing_authority'] = auth_distribution.head(10).to_dict()
        print(f"Top filing authorities: {dict(list(auth_distribution.head(5).items()))}")
    
    # Secondary distribution by applicant country (if available)
    if 'person_ctry_code' in ree_df.columns:
        country_distribution = ree_df['person_ctry_code'].value_counts()
        geographic_stats['applicant_country'] = country_distribution.head(10).to_dict()
        print(f"Top applicant countries: {dict(list(country_distribution.head(5).items()))}")
    
    # Family distribution
    if 'docdb_family_id' in ree_df.columns:
        family_by_auth = ree_df.groupby('appln_auth')['docdb_family_id'].nunique().sort_values(ascending=False)
        geographic_stats['families_by_authority'] = family_by_auth.head(10).to_dict()
        print(f"Patent families by authority: {dict(list(family_by_auth.head(5).items()))}")
    
    return geographic_stats

def create_citation_network_data(ree_df, forward_citations_df, backward_citations_df):
    """Prepare data for citation network visualization"""
    
    network_data = {
        'nodes': [],
        'edges': []
    }
    
    try:
        # Create nodes from REE patents (by country)
        if not ree_df.empty and 'appln_auth' in ree_df.columns:
            ree_countries = ree_df['appln_auth'].value_counts()
            for country, count in ree_countries.items():
                network_data['nodes'].append({
                    'id': f"REE_{country}",
                    'label': f"{country} (REE: {count})",
                    'type': 'ree_origin',
                    'size': count,
                    'country': country
                })
        
        # Add citing countries as nodes
        if not forward_citations_df.empty and 'citing_country' in forward_citations_df.columns:
            citing_countries = forward_citations_df['citing_country'].value_counts()
            for country, count in citing_countries.items():
                if country and country != 'None':
                    network_data['nodes'].append({
                        'id': f"CITING_{country}",
                        'label': f"{country} (Citations: {count})",
                        'type': 'citing',
                        'size': count,
                        'country': country
                    })
        
        # Create edges for forward citations
        if not forward_citations_df.empty:
            for _, row in forward_citations_df.iterrows():
                if row['citing_country'] and row['citing_country'] != 'None':
                    # Find the REE origin country for this cited application
                    cited_app = ree_df[ree_df['appln_id'] == row['cited_ree_appln_id']]
                    if not cited_app.empty:
                        ree_country = cited_app.iloc[0]['appln_auth']
                        network_data['edges'].append({
                            'source': f"REE_{ree_country}",
                            'target': f"CITING_{row['citing_country']}",
                            'type': 'forward_citation'
                        })
        
        print(f"Created network with {len(network_data['nodes'])} nodes and {len(network_data['edges'])} edges")
        
    except Exception as e:
        print(f"⚠️ Network data creation failed: {e}")
    
    return network_data

if __name__ == "__main__":
    from database_connection import test_tip_connection
    from dataset_builder import build_ree_dataset
    from citation_analyzer import get_forward_citations, get_backward_citations
    
    db = test_tip_connection()
    if db:
        ree_data = build_ree_dataset(db, test_mode=True)
        if not ree_data.empty:
            # Geographic enrichment
            enriched_ree = enrich_with_geographic_data(db, ree_data)
            geo_stats = get_geographic_distribution(enriched_ree)
            
            # Citation analysis
            appln_ids = ree_data['appln_id'].tolist()
            forward_cit = get_forward_citations(db, appln_ids, test_mode=True)
            backward_cit = get_backward_citations(db, appln_ids, test_mode=True)
            
            # Citation country analysis
            top_citing = analyze_country_citations(forward_cit)
            
            # Network data
            network_data = create_citation_network_data(enriched_ree, forward_cit, backward_cit)
            
            print("Geographic analysis completed!")