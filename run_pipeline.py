#!/usr/bin/env python
"""
Wrapper script to run the full DQ pipeline

This script can be run from the project root:
    python run_pipeline.py

Or use the module directly:
    python -m ownership_dq.main
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the full ownership DQ pipeline"""
    print("=" * 60)
    print("  Ownership Data Quality Assessment Pipeline")
    print("=" * 60)
    print()
    print("🚀 Starting pipeline...")
    print()
    print("This will:")
    print("  1. Generate synthetic ownership data")
    print("  2. Extract entities using NLP")
    print("  3. Resolve entities with graph-based approach")
    print("  4. Detect anomalies using hybrid ML")
    print("  5. Simulate active learning feedback")
    print("  6. Generate DQ assessment report")
    print()
    print("⏱️  Estimated time: 2-3 minutes")
    print()
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "ownership_dq.main"
        ])
        
        print()
        print("=" * 60)
        print("  ✅ Pipeline Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  • View reports in: reports/")
        print("  • View data in: data/")
        print("  • View charts in: visualizations/")
        print("  • Launch dashboard: python run_dashboard.py")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
