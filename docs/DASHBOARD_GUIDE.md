# 📊 Bloomberg Terminal Dashboard Guide

## 🎨 Authentic Bloomberg Terminal Design

This interactive dashboard uses the **authentic Bloomberg terminal color scheme**:
- **Black Background** (#000000) - Classic terminal look
- **Orange Headers** (#FF8C00) - Bloomberg signature color
- **Green for Positive** (#00FF00) - Good metrics
- **Red for Negative** (#FF0000) - Issues/alerts
- **Blue Highlights** (#00BFFF) - Important info
- **Yellow Warnings** (#FFFF00) - Caution items
- **Courier New Font** - Monospace terminal aesthetic

---

## 🚀 Quick Start

### 1. Install Streamlit
```bash
pip install streamlit plotly
```

### 2. Run the Dashboard
```bash
cd ownership_dq_poc
streamlit run dashboard.py
```

### 3. View in Browser
The dashboard will automatically open at: `http://localhost:8501`

---

## 📺 Dashboard Pages

### 1. 📊 Executive Dashboard
**What You See:**
- Overall DQ Score gauge (Bloomberg-style)
- Key metrics: Anomalies, Precision, FP Reduction
- DQ Dimensions bar chart
- Scenario distribution pie chart
- Real-time system status

**Best For:**
- Quick overview
- Executive presentations

### 2. 🎯 Anomaly Detection
**What You See:**
- Detection performance metrics
- Confidence distribution histogram
- Model comparison (ISO Forest vs LSTM vs Hybrid)
- Confusion matrix heatmap

**Best For:**
- Technical deep-dives
- Explaining hybrid approach
- Model performance analysis

### 3. 📈 DQ Dimensions
**What You See:**
- 6 interactive gauges (one per dimension)
- Detailed breakdowns per dimension
- Check-level results
- Status indicators

**Best For:**
- DAMA framework demonstration
- Comprehensive DQ assessment
- Compliance reporting

### 4. 🕸️ Entity Resolution
**What You See:**
- Before/After entity counts
- Reduction rate metrics
- Full entity mapping table
- Variation groupings

**Best For:**
- Explaining graph-based resolution
- Showing deduplication effectiveness
- Name standardization demos

### 5. 💾 Raw Data
**What You See:**
- Filterable data explorer
- Scenario filters
- Entity filters
- Anomaly status filters
- CSV download capability

**Best For:**
- Data exploration
- Finding specific records
- Exporting subsets
- Ad-hoc analysis

---

## 🎨 Visual Features

### Bloomberg Color Coding
```
🟢 Green (>90%)  = Excellent performance
🟡 Yellow (75-90%) = Good, needs monitoring
🔴 Red (<75%)    = Needs attention
🟠 Orange        = Bloomberg signature (headers, highlights)
```

### Interactive Elements
- **Hover** over charts for detailed tooltips
- **Click** legend items to toggle visibility
- **Zoom** on charts with mouse selection
- **Pan** on charts with click-drag
- **Download** filtered data as CSV

### Real-Time Updates
- System status shows current timestamp
- Record counts update with filters
- All metrics calculated dynamically

---

## 🎯 Key Features

### Bloomberg Aesthetic
✅ Black background  
✅ Orange/amber headers  
✅ Monospace font (Courier New)  
✅ Color-coded metrics  
✅ Terminal-style layout  

### Interactive Analysis
✅ Multi-page navigation  
✅ Dynamic filtering  
✅ Hover tooltips  
✅ Zoom/pan charts  
✅ CSV export  

### Professional Polish
✅ Real-time status  
✅ Formatted metrics  
✅ Responsive layout  
✅ Clean styling  
✅ Error handling  

---

## 🔧 Customization

### Change Color Scheme
Edit the `BLOOMBERG_COLORS` dictionary in `dashboard.py`:
```python
BLOOMBERG_COLORS = {
    'background': '#000000',      # Change to your color
    'primary_orange': '#FF8C00',  # Bloomberg signature
    'positive_green': '#00FF00',  # Success color
    ...
}
```

### Add New Page
1. Create function: `def show_my_page(df, report):`
2. Add to navigation: `page = st.sidebar.radio(...)`
3. Add routing: `elif page == "My Page": show_my_page(df, report)`

### Modify Charts
All charts use Plotly - full customization available:
```python
fig.update_layout(
    title="My Custom Title",
    font=dict(size=16, color="#FFFFFF"),
    ...
)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: streamlit"
```bash
pip install streamlit plotly
```

### "File not found: data/..."
Run the main pipeline first:
```bash
python main.py
```

### Dashboard won't load
Check you're in the correct directory:
```bash
cd ownership_dq_poc
streamlit run dashboard.py
```

### Port already in use
Stop other Streamlit apps or use different port:
```bash
streamlit run dashboard.py --server.port 8502
```

### Colors look wrong
Some browsers cache CSS. Hard refresh:
- **Windows/Linux:** Ctrl + Shift + R
- **Mac:** Cmd + Shift + R

---

## 📊 Dashboard Statistics

- **5 Interactive Pages**
- **15+ Charts and Visualizations**
- **Real-time Filtering**
- **Bloomberg Color Scheme**
- **Mobile Responsive**
- **CSV Export**
- **Hover Tooltips**
- **Professional Grade**

---
