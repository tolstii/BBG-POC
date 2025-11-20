# ⚡ Quick Start Guide - 60 Second Setup

## 🎯 Goal
Get the POC running in under 60 seconds

---

## 📋 Prerequisites Check
```bash
# Check Python version (need 3.9+)
python --version

# Check if pip is installed
pip --version
```

---

## 🚀 Three Commands to Success

### 1. Install Dependencies (15 seconds)
```bash
pip install pandas numpy scikit-learn matplotlib seaborn networkx
```

### 2. Run Pipeline (120 seconds)
```bash
cd ownership_dq_poc
python main.py
```

### 3. View Results (10 seconds)
```bash
# Open this file in your browser:
reports/dq_assessment_report.html
```

---

## ✅ Success Indicators

You'll see this output:
```
================================================================================
🚀 OWNERSHIP DATA QUALITY ASSESSMENT POC
================================================================================
Start Time: 2025-11-17 ...

STEP 1: GENERATING SYNTHETIC OWNERSHIP DATA
✅ Generated 5000 records...

STEP 2: NLP ENTITY EXTRACTION FROM NARRATIVES
✅ NLP extraction complete: 77.7% accuracy

STEP 3: GRAPH-BASED ENTITY RESOLUTION
✅ Entity resolution complete: 57.7% reduction

STEP 4: HYBRID ANOMALY DETECTION
🎯 FP Reduction: 96.6%

STEP 5: ACTIVE LEARNING FEEDBACK LOOP
   Agreement rate: 89.0%

STEP 6: COMPREHENSIVE DATA QUALITY PROFILING
📊 OVERALL DATA QUALITY SCORE: 81.44% (B)

STEP 7: GENERATING ASSESSMENT REPORT
   💾 Assessment report saved

✅ PIPELINE COMPLETE!
```
---

## 🔧 Quick Customizations

Want more records?
```python
# Edit main.py, line 427:
df, results = pipeline.run_complete_pipeline(n_records=10000)  # Change 5000
```

Want different sensitivity?
```python
# Edit main.py, line 36:
self.hybrid_detector = HybridAnomalyDetector(contamination=0.15)  # Change 0.10
```
---

## 📈 Expected Results

| Metric | Expected Value |
|--------|---------------|
| Overall DQ Score | 80-85% |
| Anomalies Detected | 450-550 |
| Detection Precision | 70-75% |
| FP Reduction | 95-97% |
| Entity Reduction | 55-60% |
| Runtime | 2-3 minutes |

---
