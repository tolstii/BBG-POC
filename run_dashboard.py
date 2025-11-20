#!/usr/bin/env python
"""
Wrapper script to run the Streamlit dashboard

This script can be run from the project root:
    python run_dashboard.py

Or use streamlit directly:
    streamlit run ownership_dq/dashboard.py
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Run the Streamlit dashboard"""
    dashboard_path = Path(__file__).parent / "ownership_dq" / "dashboard.py"
    
    if not dashboard_path.exists():
        print("❌ Error: dashboard.py not found")
        print(f"Expected location: {dashboard_path}")
        sys.exit(1)
    
    print("🚀 Launching Ownership DQ Dashboard...")
    print(f"📂 Dashboard: {dashboard_path}")
    print()
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(dashboard_path)
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")
    except Exception as e:
        print(f"\n❌ Error running dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
