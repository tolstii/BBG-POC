#!/usr/bin/env python
"""
Installation Verification Script for Ownership DQ POC

Run this script after setup to verify all components are working correctly.
Usage: python verify_installation.py
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_status(check, status, message=""):
    """Print check status"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {check:<40} {message}")
    return status


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    required = (3, 9)
    
    status = version >= required
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_status(
        "Python version",
        status,
        f"v{version_str} {'(OK)' if status else '(Need 3.9+)'}"
    )
    return status


def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Dependencies")
    
    dependencies = [
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("sklearn", "scikit-learn"),
        ("tensorflow", "tensorflow"),
        ("spacy", "spacy"),
        ("networkx", "networkx"),
        ("streamlit", "streamlit"),
        ("plotly", "plotly"),
        ("matplotlib", "matplotlib"),
        ("pytest", "pytest"),
    ]
    
    all_ok = True
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print_status(package_name, True, "Installed")
        except ImportError:
            print_status(package_name, False, "Missing")
            all_ok = False
    
    return all_ok


def check_spacy_model():
    """Check if spaCy model is downloaded"""
    print_header("Checking spaCy Model")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print_status("en_core_web_sm", True, "Downloaded")
        return True
    except OSError:
        print_status("en_core_web_sm", False, "Not downloaded")
        print("\nTo download: python -m spacy download en_core_web_sm")
        return False


def check_project_structure():
    """Check if project structure is correct"""
    print_header("Checking Project Structure")
    
    required_dirs = [
        "ownership_dq",
        "data",
        "reports",
        "visualizations",
        "docs",
        "tests",
    ]
    
    required_files = [
        "README.md",
        "requirements.txt",
        "ownership_dq/__init__.py",
        "ownership_dq/main.py",
        "ownership_dq/dashboard.py",
    ]
    
    all_ok = True
    
    for dir_name in required_dirs:
        exists = Path(dir_name).is_dir()
        print_status(f"Directory: {dir_name}", exists)
        all_ok = all_ok and exists
    
    for file_name in required_files:
        exists = Path(file_name).is_file()
        print_status(f"File: {file_name}", exists)
        all_ok = all_ok and exists
    
    return all_ok


def check_imports():
    """Check if package imports work"""
    print_header("Checking Package Imports")
    
    modules = [
        "ownership_dq.synthetic_generator",
        "ownership_dq.nlp_extractor",
        "ownership_dq.graph_resolver",
        "ownership_dq.hybrid_detector",
        "ownership_dq.active_learning",
        "ownership_dq.dq_profiler",
    ]
    
    all_ok = True
    for module_name in modules:
        try:
            __import__(module_name)
            print_status(module_name, True, "OK")
        except ImportError as e:
            print_status(module_name, False, str(e))
            all_ok = False
    
    return all_ok


def run_quick_test():
    """Run a quick smoke test"""
    print_header("Running Quick Test")
    
    try:
        import pandas as pd
        import numpy as np
        from ownership_dq.hybrid_detector import HybridAnomalyDetector
        
        # Create tiny test dataset
        df = pd.DataFrame({
            'filing_date': pd.date_range('2023-01-01', periods=20),
            'filer_name': ['Filer_A'] * 20,
            'issuer_name': ['Company_X'] * 20,
            'shares': np.random.lognormal(10, 1, 20),
            'market_value': np.random.lognormal(15, 1, 20),
            'percent_portfolio': np.random.uniform(1, 5, 20),
            'label': ['normal'] * 20
        })
        
        # Try detection
        detector = HybridAnomalyDetector()
        result = detector.detect(df)
        
        if len(result) == len(df) and 'anomaly_score' in result.columns:
            print_status("Smoke test", True, "Detection works")
            return True
        else:
            print_status("Smoke test", False, "Unexpected result")
            return False
            
    except Exception as e:
        print_status("Smoke test", False, str(e))
        return False


def main():
    """Main verification function"""
    print("\n" + "=" * 60)
    print("  Ownership Data Quality POC - Installation Verification")
    print("=" * 60)
    
    checks = {
        "Python Version": check_python_version(),
        "Dependencies": check_dependencies(),
        "spaCy Model": check_spacy_model(),
        "Project Structure": check_project_structure(),
        "Package Imports": check_imports(),
        "Quick Test": run_quick_test(),
    }
    
    # Summary
    print_header("Verification Summary")
    passed = sum(checks.values())
    total = len(checks)
    
    for check_name, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check_name}")
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if passed == total:
        print("\n🎉 All checks passed! Your installation is ready.")
        print("\nNext steps:")
        print("  1. Run the pipeline: python -m ownership_dq.main")
        print("  2. Launch dashboard: streamlit run ownership_dq/dashboard.py")
        print("  3. Run tests: pytest tests/ -v")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  • Missing dependencies: pip install -r requirements.txt")
        print("  • Missing spaCy model: python -m spacy download en_core_web_sm")
        print("  • Wrong directory: Make sure you're in the project root")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
