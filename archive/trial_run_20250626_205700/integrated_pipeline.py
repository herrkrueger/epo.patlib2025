from database_connection import test_tip_connection
from dataset_builder import build_ree_dataset
from citation_analyzer import analyze_citations_for_ree_dataset
from geographic_enricher import get_comprehensive_geographic_intelligence
from data_validator import comprehensive_validation_and_reporting

def run_complete_ree_analysis(test_mode=True):
    """Complete REE analysis pipeline"""
    
    print("REE PATENT CITATION ANALYSIS PIPELINE")
    print("=" * 50)
    print("EPO PATLIB 2025 - Professional Patent Intelligence")
    print("Technology Focus: Rare Earth Elements (REE)")
    print("Time Period: 2010-2023 (Comprehensive Coverage)")
    print("=" * 50)
    
    # Step 1: Connect to database
    print("\n🔌 STEP 1: DATABASE CONNECTION")
    print("-" * 30)
    db = test_tip_connection()
    if not db:
        print("❌ PIPELINE FAILED: Database connection unsuccessful")
        return None
    
    # Step 2: Build REE dataset
    print("\n🔍 STEP 2: REE DATASET CONSTRUCTION")
    print("-" * 35)
    ree_data = build_ree_dataset(db, test_mode)
    if ree_data.empty:
        print("❌ PIPELINE FAILED: No REE patents found")
        return None
    
    print(f"✅ REE Dataset: {len(ree_data):,} applications found")
    
    # Step 3: Citation analysis
    print("\n📊 STEP 3: CITATION INTELLIGENCE")
    print("-" * 30)
    appln_ids = ree_data['appln_id'].tolist()
    citation_results = analyze_citations_for_ree_dataset(appln_ids, test_mode)
    
    if citation_results:
        forward_count = len(citation_results['forward_citations'])
        backward_count = len(citation_results['backward_citations'])
        print(f"✅ Citation Analysis: {forward_count:,} forward + {backward_count:,} backward citations")
    else:
        print("⚠️ Citation analysis completed with limited results")
        citation_results = {}
    
    # Step 4: Geographic intelligence
    print("\n🌍 STEP 4: GEOGRAPHIC INTELLIGENCE")
    print("-" * 35)
    geographic_results = get_comprehensive_geographic_intelligence(ree_data, test_mode)
    
    if geographic_results:
        enriched_data = geographic_results['enriched_dataset']
        print(f"✅ Geographic Analysis: {len(enriched_data):,} applications enriched")
    else:
        print("⚠️ Geographic analysis completed with limited enrichment")
        geographic_results = {}
        enriched_data = ree_data
    
    # Step 5: Quality validation and business reporting
    print("\n✅ STEP 5: VALIDATION & BUSINESS REPORTING")
    print("-" * 40)
    validation_results = comprehensive_validation_and_reporting(
        enriched_data, 
        citation_results, 
        geographic_results
    )
    
    # Pipeline summary
    print("\n" + "=" * 50)
    print("🎉 PIPELINE EXECUTION COMPLETE")
    print("=" * 50)
    
    total_citations = 0
    if citation_results:
        forward_cit = len(citation_results.get('forward_citations', []))
        backward_cit = len(citation_results.get('backward_citations', []))
        total_citations = forward_cit + backward_cit
    
    print(f"📊 Final Results Summary:")
    print(f"   • REE Patents Analyzed: {len(enriched_data):,}")
    print(f"   • Patent Families: {enriched_data['docdb_family_id'].nunique():,}")
    print(f"   • Total Citations: {total_citations:,}")
    print(f"   • Countries Covered: {enriched_data['appln_auth'].nunique()}")
    print(f"   • Quality Score: {validation_results['quality_assessment']['quality_score']}/100")
    print(f"   • Export Files: {len(validation_results['export_files'])}")
    
    quality_rating = validation_results['quality_assessment']['quality_rating']
    print(f"\n🏆 Analysis Quality: {quality_rating}")
    print(f"💼 Business Value: Ready for executive presentation")
    
    return {
        'ree_dataset': enriched_data,
        'citation_results': citation_results,
        'geographic_results': geographic_results,
        'validation_results': validation_results,
        'pipeline_summary': {
            'total_applications': len(enriched_data),
            'total_families': enriched_data['docdb_family_id'].nunique(),
            'total_citations': total_citations,
            'countries_covered': enriched_data['appln_auth'].nunique(),
            'quality_score': validation_results['quality_assessment']['quality_score'],
            'quality_rating': quality_rating
        }
    }

def run_demo_pipeline():
    """Run demonstration pipeline with test mode enabled"""
    
    print("🎬 DEMO MODE: EPO PATLIB 2025 Live Demonstration")
    print("⏱️  Expected Duration: 90 seconds per major step")
    print("🎯 Target: Professional patent intelligence for REE technology")
    print("")
    
    results = run_complete_ree_analysis(test_mode=True)
    
    if results:
        print("\n🎉 DEMO PIPELINE SUCCESS!")
        print("📈 Ready for live presentation at EPO PATLIB 2025")
        print("💡 Demonstrates: Professional AI-enhanced patent analytics")
        
        # Demo-specific summary
        summary = results['pipeline_summary']
        print(f"\n📊 Demo Metrics (Test Mode):")
        print(f"   • Dataset Size: {summary['total_applications']:,} patents")
        print(f"   • Citation Network: {summary['total_citations']:,} connections") 
        print(f"   • Global Coverage: {summary['countries_covered']} countries")
        print(f"   • Analysis Quality: {summary['quality_rating']}")
        
        print(f"\n🎯 Value Proposition Demonstrated:")
        print(f"   • Professional-grade analytics at fraction of commercial costs")
        print(f"   • Real PATSTAT database connectivity")
        print(f"   • Executive-ready business intelligence")
        print(f"   • Reproducible methodology for any technology domain")
        
        return results
    else:
        print("❌ DEMO PIPELINE FAILED - Troubleshooting required")
        return None

def run_production_pipeline():
    """Run production pipeline with full dataset"""
    
    print("🏭 PRODUCTION MODE: Full-Scale REE Analysis")
    print("⚠️  Warning: This will process the complete dataset")
    print("⏱️  Expected Duration: 10-15 minutes")
    print("")
    
    user_confirmation = input("Continue with production run? (yes/no): ")
    if user_confirmation.lower() != 'yes':
        print("Production run cancelled")
        return None
    
    results = run_complete_ree_analysis(test_mode=False)
    
    if results:
        print("\n🏆 PRODUCTION PIPELINE SUCCESS!")
        print("📊 Full-scale analysis complete with comprehensive results")
        
        # Production-specific metrics
        summary = results['pipeline_summary']
        print(f"\n📈 Production Results:")
        print(f"   • Complete REE Patent Landscape: {summary['total_applications']:,}")
        print(f"   • Full Citation Network: {summary['total_citations']:,}")
        print(f"   • Global Market Coverage: {summary['countries_covered']} countries")
        print(f"   • Professional Quality: {summary['quality_rating']}")
        
        return results
    else:
        print("❌ PRODUCTION PIPELINE FAILED")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == 'demo':
            results = run_demo_pipeline()
        elif mode == 'production':
            results = run_production_pipeline()
        else:
            print("Usage: python integrated_pipeline.py [demo|production]")
    else:
        # Default to demo mode
        print("🚀 Running Demo Pipeline (default)")
        print("💡 For production mode: python integrated_pipeline.py production")
        print("")
        results = run_demo_pipeline()
    
    if results:
        print(f"\n✅ Pipeline executed successfully!")
        print(f"📂 Check export files for business deliverables")
    else:
        print(f"\n❌ Pipeline execution failed")
        print(f"🔧 Check component logs for troubleshooting")