#!/usr/bin/env python3
"""
Quick test script to verify processor session initialization fix.
"""

import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from data_access import PatstatClient
from processors import ApplicantAnalyzer, GeographicAnalyzer, ClassificationAnalyzer

def test_processor_initialization():
    """Test that all processors can initialize with PatstatClient."""
    print("🧪 Testing Processor Session Initialization Fix")
    print("=" * 50)
    
    # Create PATSTAT client
    print("🔗 Creating PATSTAT client...")
    patstat = PatstatClient(environment='PROD')
    print("✅ PATSTAT client created")
    
    # Test each processor
    processors = [
        ("Applicant", ApplicantAnalyzer),
        ("Geographic", GeographicAnalyzer), 
        ("Classification", ClassificationAnalyzer)
    ]
    
    success_count = 0
    
    for name, ProcessorClass in processors:
        print(f"\n🔬 Testing {name} Analyzer...")
        try:
            processor = ProcessorClass(patstat)
            if hasattr(processor, 'session') and processor.session is not None:
                print(f"✅ {name} analyzer: Session initialized successfully")
                success_count += 1
            else:
                print(f"⚠️ {name} analyzer: Session is None")
        except Exception as e:
            print(f"❌ {name} analyzer failed: {e}")
    
    print(f"\n📊 Results: {success_count}/{len(processors)} processors working")
    
    if success_count == len(processors):
        print("🎉 All processors fixed! Ready for notebook execution.")
    else:
        print("⚠️ Some processors still have issues.")
    
    return success_count == len(processors)

if __name__ == "__main__":
    test_processor_initialization()