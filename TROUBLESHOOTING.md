# Troubleshooting Guide

## Common Issues and Solutions

### 1. Dashboard Import Error

**Error:**
```
ImportError: attempted relative import with no known parent package
```

**Cause:** Streamlit has issues with relative imports when running scripts directly.

**Solution (Fixed in v1.0.1):**
The dashboard now includes both relative and absolute import fallbacks. Use one of these methods:

```bash
# Method 1: Use wrapper script (recommended)
python run_dashboard.py

# Method 2: Run from project root
streamlit run ownership_dq/dashboard.py

# Method 3: Use Python module syntax (if that fails)
python -m streamlit run ownership_dq/dashboard.py
```

**If still having issues:**
- Ensure you're in the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (need 3.9+)

---

### 2. Data Not Found Error

**Error:**
```
⚠️ Could not find data file. Please run the pipeline first
```

**Cause:** Dashboard can't locate the generated data files.

**Solution:**
1. Run the pipeline first to generate data:
   ```bash
   python run_pipeline.py
   # or
   python -m ownership_dq.main
   ```

2. Verify data was created:
   ```bash
   ls data/
   # Should see: 05_feedback_incorporated.csv and others
   ```

3. If files exist but dashboard still can't find them, ensure you're running from the project root directory.

---

### 3. Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'ownership_dq'
```

**Cause:** Python can't find the package.

**Solution:**
1. Ensure you're in the project root directory
2. Check Python path:
   ```bash
   pwd  # Should show: .../ownership-dq-poc
   ```

3. If running from a different directory, add to PYTHONPATH:
   ```bash
   export PYTHONPATH="/path/to/ownership-dq-poc:$PYTHONPATH"
   # On Windows:
   set PYTHONPATH=C:\path\to\ownership-dq-poc;%PYTHONPATH%
   ```

---

### 4. spaCy Model Not Found

**Error:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Cause:** spaCy language model not downloaded.

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

**Verify installation:**
```bash
python -c "import spacy; spacy.load('en_core_web_sm'); print('✅ Model loaded')"
```

---

### 5. TensorFlow/LSTM Warnings

**Warning:**
```
Your CPU supports instructions that this TensorFlow binary was not compiled to use
```

**Cause:** TensorFlow is running on CPU without optimizations.

**Solution (optional):**
This is just a warning and won't affect functionality. To suppress:
```bash
export TF_CPP_MIN_LOG_LEVEL=2  # Linux/Mac
# On Windows:
set TF_CPP_MIN_LOG_LEVEL=2
```

Or install TensorFlow GPU version if you have a compatible GPU.

---

### 6. Streamlit Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Cause:** Port 8501 (default Streamlit port) is already in use.

**Solution:**
```bash
# Use a different port
streamlit run ownership_dq/dashboard.py --server.port 8502

# Or stop the existing Streamlit process
# Linux/Mac:
lsof -i :8501
kill <PID>

# Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

---

### 7. Virtual Environment Issues

**Problem:** Changes not taking effect or wrong package versions.

**Solution:**
1. Activate virtual environment:
   ```bash
   # Linux/Mac
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

2. Verify you're in the venv:
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   # Should point to venv/bin/python or venv\Scripts\python
   ```

3. Reinstall dependencies:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

### 8. Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Cause:** Script not executable or directory not writable.

**Solution:**
```bash
# Make scripts executable (Linux/Mac)
chmod +x setup.sh
chmod +x run_dashboard.py
chmod +x run_pipeline.py

# Check directory permissions
ls -la
# Ensure you own the directory

# On Windows, run as administrator if needed
```

---

### 9. Memory Errors

**Error:**
```
MemoryError: Unable to allocate array
```

**Cause:** Insufficient memory for processing.

**Solution:**
1. Close other applications
2. Reduce dataset size in synthetic_generator.py:
   ```python
   # Change these parameters:
   num_filers = 25  # default: 50
   num_issuers = 50  # default: 100
   ```

3. Increase Python memory limit (advanced):
   ```bash
   export PYTHONMALLOC=malloc
   ```

---

### 10. Visualization Issues

**Problem:** Charts not displaying or showing errors.

**Solution:**
1. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```

2. Update plotly:
   ```bash
   pip install --upgrade plotly
   ```

3. Check browser console for JavaScript errors (F12)

4. Try a different browser (Chrome/Firefox recommended)

---

## Platform-Specific Issues

### Windows

**Issue:** Path separators causing errors

**Solution:**
The code uses `pathlib.Path` which handles this automatically. If you see errors with backslashes, ensure you're using the latest code version.

**Issue:** PowerShell execution policy

**Solution:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### macOS

**Issue:** SSL certificate errors when downloading spaCy model

**Solution:**
```bash
/Applications/Python\ 3.x/Install\ Certificates.command
# or
pip install --upgrade certifi
```

### Linux

**Issue:** Missing system libraries for TensorFlow

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev

# CentOS/RHEL
sudo yum install python3-devel
```

---

## Debugging Tips

### 1. Enable Verbose Logging

```bash
# For pipeline
python -m ownership_dq.main --verbose

# For Streamlit
streamlit run ownership_dq/dashboard.py --logger.level=debug
```

### 2. Check Versions

```bash
python --version
pip list | grep -E "(streamlit|pandas|numpy|tensorflow|spacy)"
```

### 3. Test Components Individually

```python
# Test imports
python -c "from ownership_dq.hybrid_detector import HybridAnomalyDetector; print('✅ OK')"

# Test data loading
python -c "import pandas as pd; df = pd.read_csv('data/01_raw_data.csv'); print('✅ OK')"
```

### 4. Use Verification Script

```bash
python verify_installation.py
```

This will check:
- Python version
- All dependencies
- spaCy model
- Project structure
- Package imports
- Run a smoke test

---

## Getting Help

If you're still experiencing issues:

1. **Check the error message carefully** - It often contains the solution
2. **Review the CHANGELOG.md** - Your issue might be a known problem with a fix
3. **Run verify_installation.py** - Diagnoses most common issues
4. **Check GitHub Issues** - Someone may have encountered the same problem
5. **Create a minimal reproduction** - Helps identify the root cause

### Information to Include When Asking for Help

- Python version: `python --version`
- Operating system: Windows/Mac/Linux
- Error message (full traceback)
- What you were trying to do
- What you've already tried
- Output of: `python verify_installation.py`

---

## Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Am I in the project root directory?
- [ ] Is my virtual environment activated?
- [ ] Have I run `pip install -r requirements.txt`?
- [ ] Have I downloaded the spaCy model?
- [ ] Does the data directory exist with files?
- [ ] Have I run the pipeline at least once?
- [ ] Is my Python version 3.9 or higher?
- [ ] Have I tried restarting my terminal/IDE?
- [ ] Have I cleared Streamlit cache?
- [ ] Have I checked for typos in my command?

---

## Known Limitations

1. **Large datasets:** May require 8GB+ RAM for processing
2. **LSTM training:** Can be slow on CPU (5-10 minutes)
3. **Dashboard refresh:** Sometimes needs manual refresh (R in browser)
4. **Path handling:** Works best when run from project root
5. **Windows paths:** Occasionally require forward slashes in config

---

## Performance Optimization

If the pipeline or dashboard is slow:

1. **Reduce dataset size** in `synthetic_generator.py`
2. **Disable LSTM** temporarily (use Isolation Forest only)
3. **Use SSD** for data storage
4. **Close other applications** to free memory
5. **Update packages** to latest versions

---

**Last Updated:** November 19, 2024  
**Version:** 1.0.1 (with Streamlit import fixes)
