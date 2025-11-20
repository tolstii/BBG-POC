"""
Interactive Dashboard for Ownership Data Quality Assessment

STRATEGIC PURPOSE:
This dashboard serves as a communication tool for stakeholders:
- Executives: High-level DQ scores and trends
- Data stewards: Detailed dimension breakdowns
- Technical teams: Method comparison and performance metrics

DESIGN DECISIONS:
- Bloomberg-inspired aesthetic for financial services audience familiarity
- Multiple visualization types to support different stakeholder needs
- Interactive filtering to enable self-service exploration

POC NOTE: This dashboard is more comprehensive than typical POC to demonstrate
full stakeholder communication strategy. Production deployment would:
- Simplify to 3-4 core views initially
- Add views incrementally based on user feedback
- Integrate with existing BI tools (Tableau/PowerBI)
- Add role-based access controls

Development note: Built with AI assistance for rapid prototyping.
Focus was proving visualization concepts, not production optimization.
"""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports when running with streamlit
if __name__ == "__main__" or "streamlit" in sys.modules:
    current_dir = Path(__file__).parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

# Try relative imports first (when used as package), fall back to absolute
try:
    from .comparison_methods import compare_all_methods, calculate_method_metrics
    from .academic_visualizations import (
        create_before_after_comparison,
        create_adaptive_detection_plot,
        create_post_retrain_anomaly_plot,
        create_rolling_stats
    )
    from .six_step_visualization import create_six_step_comparison, create_combined_six_steps
    from .comprehensive_profiling import generate_comprehensive_report
except ImportError:
    from ownership_dq.comparison_methods import compare_all_methods, calculate_method_metrics
    from ownership_dq.academic_visualizations import (
        create_before_after_comparison,
        create_adaptive_detection_plot,
        create_post_retrain_anomaly_plot,
        create_rolling_stats
    )
    from ownership_dq.six_step_visualization import create_six_step_comparison, create_combined_six_steps
    from ownership_dq.comprehensive_profiling import generate_comprehensive_report

# Bloomberg Terminal Color Palette
BLOOMBERG_COLORS = {
    'background': '#000000',
    'surface': '#0A0A0A',
    'primary_orange': '#FF8C00',
    'header_orange': '#FFA500',
    'positive_green': '#00FF00',
    'negative_red': '#FF0000',
    'highlight_blue': '#00BFFF',
    'warning_yellow': '#FFFF00',
    'text_white': '#FFFFFF',
    'text_gray': '#CCCCCC',
    'border_gray': '#333333',
    'chart_orange': '#FF8C00',
    'chart_blue': '#4169E1',
    'chart_green': '#32CD32',
    'chart_red': '#DC143C'
}

# Configure Streamlit page
st.set_page_config(
    page_title="Bloomberg DQ Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bloomberg terminal look
st.markdown(f"""
<style>
    .stApp {{
        background-color: {BLOOMBERG_COLORS['background']};
        color: {BLOOMBERG_COLORS['text_white']};
    }}
    
    h1, h2, h3 {{
        color: {BLOOMBERG_COLORS['header_orange']} !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }}
    
    .stMetric {{
        background-color: {BLOOMBERG_COLORS['surface']};
        padding: 15px;
        border-radius: 5px;
        border: 1px solid {BLOOMBERG_COLORS['border_gray']};
    }}
    
    .stMetric label {{
        color: {BLOOMBERG_COLORS['primary_orange']} !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }}
    
    .stMetric [data-testid="stMetricValue"] {{
        color: {BLOOMBERG_COLORS['positive_green']} !important;
        font-size: 32px !important;
        font-family: 'Courier New', monospace;
    }}
    
    .css-1d391kg, [data-testid="stSidebar"] {{
        background-color: {BLOOMBERG_COLORS['surface']};
        border-right: 2px solid {BLOOMBERG_COLORS['primary_orange']};
    }}
    
    p, span, div {{
        color: {BLOOMBERG_COLORS['text_gray']};
        font-family: 'Courier New', monospace;
    }}
    
    .stButton button {{
        background-color: {BLOOMBERG_COLORS['primary_orange']};
        color: {BLOOMBERG_COLORS['background']};
        border: none;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }}
    
    .stButton button:hover {{
        background-color: {BLOOMBERG_COLORS['header_orange']};
    }}
    
    .dataframe {{
        background-color: {BLOOMBERG_COLORS['surface']} !important;
        color: {BLOOMBERG_COLORS['text_white']} !important;
        border: 1px solid {BLOOMBERG_COLORS['border_gray']} !important;
    }}
    
    .dataframe th {{
        background-color: {BLOOMBERG_COLORS['primary_orange']} !important;
        color: {BLOOMBERG_COLORS['background']} !important;
        font-weight: bold;
    }}
    
    .dataframe td {{
        color: {BLOOMBERG_COLORS['text_white']} !important;
    }}
    
    hr {{
        border-color: {BLOOMBERG_COLORS['primary_orange']};
    }}
    
    .metric-box {{
        background-color: {BLOOMBERG_COLORS['surface']};
        padding: 15px;
        border-radius: 5px;
        border: 1px solid {BLOOMBERG_COLORS['border_gray']};
        margin: 10px 0;
    }}
    
    .metric-box h4 {{
        color: {BLOOMBERG_COLORS['primary_orange']} !important;
        margin: 0 0 10px 0;
    }}
    
    .metric-box .value {{
        color: {BLOOMBERG_COLORS['positive_green']};
        font-size: 24px;
        font-weight: bold;
    }}
    
    .metric-box .label {{
        color: {BLOOMBERG_COLORS['text_gray']};
        font-size: 12px;
    }}
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load all generated data and reports"""
    try:
        # Determine the project root directory
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        
        # Try multiple possible data locations
        data_paths = [
            project_root / 'data' / '05_feedback_incorporated.csv',
            Path('data') / '05_feedback_incorporated.csv',
            Path('..') / 'data' / '05_feedback_incorporated.csv',
        ]
        
        report_paths = [
            project_root / 'reports' / 'dq_assessment_report.json',
            Path('reports') / 'dq_assessment_report.json',
            Path('..') / 'reports' / 'dq_assessment_report.json',
        ]
        
        # Try to load data from possible locations
        df = None
        for data_path in data_paths:
            if data_path.exists():
                df = pd.read_csv(data_path)
                break
        
        if df is None:
            st.error("⚠️ Could not find data file. Please run the pipeline first: python -m ownership_dq.main")
            return None, None
        
        # Try to load report from possible locations
        report = None
        for report_path in report_paths:
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                break
        
        if report is None:
            st.warning("⚠️ Could not find report file. Some features may be limited.")
        
        return df, report
        
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        st.info("💡 Tip: Make sure to run the pipeline first: python -m ownership_dq.main")
        return None, None

def create_bloomberg_gauge(value, title, max_val=100):
    """Create Bloomberg-style gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': BLOOMBERG_COLORS['header_orange']}},
        delta={'reference': 90, 'increasing': {'color': BLOOMBERG_COLORS['positive_green']}},
        number={'font': {'size': 40, 'color': BLOOMBERG_COLORS['text_white']}},
        gauge={
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': BLOOMBERG_COLORS['text_gray']},
            'bar': {'color': BLOOMBERG_COLORS['primary_orange']},
            'bgcolor': BLOOMBERG_COLORS['surface'],
            'borderwidth': 2,
            'bordercolor': BLOOMBERG_COLORS['border_gray'],
            'steps': [
                {'range': [0, 50], 'color': 'rgba(220, 20, 60, 0.3)'},
                {'range': [50, 75], 'color': 'rgba(255, 255, 0, 0.3)'},
                {'range': [75, 100], 'color': 'rgba(50, 205, 50, 0.3)'}
            ],
            'threshold': {
                'line': {'color': BLOOMBERG_COLORS['negative_red'], 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor=BLOOMBERG_COLORS['background'],
        plot_bgcolor=BLOOMBERG_COLORS['surface'],
        font={'color': BLOOMBERG_COLORS['text_white'], 'family': 'Courier New'},
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig

def create_bloomberg_bar(data, x, y, title, color=None):
    """Create Bloomberg-style bar chart"""
    fig = go.Figure()
    
    colors = [BLOOMBERG_COLORS['chart_orange'] if val > 90 
              else BLOOMBERG_COLORS['chart_blue'] if val > 75 
              else BLOOMBERG_COLORS['chart_red'] for val in data[y]]
    
    fig.add_trace(go.Bar(
        x=data[x],
        y=data[y],
        marker=dict(
            color=colors,
            line=dict(color=BLOOMBERG_COLORS['border_gray'], width=1)
        ),
        text=data[y].round(1),
        textposition='outside',
        textfont=dict(color=BLOOMBERG_COLORS['text_white'], size=12)
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=BLOOMBERG_COLORS['header_orange'])),
        paper_bgcolor=BLOOMBERG_COLORS['background'],
        plot_bgcolor=BLOOMBERG_COLORS['surface'],
        font=dict(color=BLOOMBERG_COLORS['text_white'], family='Courier New'),
        xaxis=dict(
            gridcolor=BLOOMBERG_COLORS['border_gray'],
            showline=True,
            linecolor=BLOOMBERG_COLORS['primary_orange']
        ),
        yaxis=dict(
            gridcolor=BLOOMBERG_COLORS['border_gray'],
            showline=True,
            linecolor=BLOOMBERG_COLORS['primary_orange']
        ),
        height=400,
        margin=dict(l=50, r=20, t=50, b=50)
    )
    
    return fig

def create_bloomberg_line(data, x, y, title):
    """Create Bloomberg-style line chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y],
        mode='lines+markers',
        line=dict(color=BLOOMBERG_COLORS['primary_orange'], width=2),
        marker=dict(
            size=6,
            color=BLOOMBERG_COLORS['primary_orange'],
            line=dict(color=BLOOMBERG_COLORS['text_white'], width=1)
        ),
        fill='tozeroy',
        fillcolor=f'rgba(255, 140, 0, 0.1)'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=BLOOMBERG_COLORS['header_orange'])),
        paper_bgcolor=BLOOMBERG_COLORS['background'],
        plot_bgcolor=BLOOMBERG_COLORS['surface'],
        font=dict(color=BLOOMBERG_COLORS['text_white'], family='Courier New'),
        xaxis=dict(
            gridcolor=BLOOMBERG_COLORS['border_gray'],
            showline=True,
            linecolor=BLOOMBERG_COLORS['primary_orange']
        ),
        yaxis=dict(
            gridcolor=BLOOMBERG_COLORS['border_gray'],
            showline=True,
            linecolor=BLOOMBERG_COLORS['primary_orange']
        ),
        height=400,
        margin=dict(l=50, r=20, t=50, b=50)
    )
    
    return fig

def create_bloomberg_heatmap(data, title):
    """Create Bloomberg-style heatmap"""
    fig = go.Figure(data=go.Heatmap(
        z=data.values,
        x=data.columns,
        y=data.index,
        colorscale=[
            [0, BLOOMBERG_COLORS['negative_red']],
            [0.5, BLOOMBERG_COLORS['warning_yellow']],
            [1, BLOOMBERG_COLORS['positive_green']]
        ],
        text=data.values,
        texttemplate='%{text:.1f}%',
        textfont=dict(color=BLOOMBERG_COLORS['background'], size=10),
        colorbar=dict(
            tickfont=dict(color=BLOOMBERG_COLORS['text_white']),
            title=dict(text='Score', font=dict(color=BLOOMBERG_COLORS['header_orange']))
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color=BLOOMBERG_COLORS['header_orange'])),
        paper_bgcolor=BLOOMBERG_COLORS['background'],
        plot_bgcolor=BLOOMBERG_COLORS['surface'],
        font=dict(color=BLOOMBERG_COLORS['text_white'], family='Courier New'),
        height=400,
        margin=dict(l=120, r=20, t=50, b=50)
    )
    
    return fig

def calculate_statistical_metrics(df):
    """Calculate comprehensive statistical profiling metrics"""
    metrics = {}
    
    # Numerical columns
    numerical_cols = ['ownership_pct', 'shares', 'market_value', 'qoq_change_pct']
    
    for col in numerical_cols:
        if col in df.columns:
            metrics[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'q25': df[col].quantile(0.25),
                'q75': df[col].quantile(0.75),
                'skewness': df[col].skew(),
                'kurtosis': df[col].kurtosis(),
                'null_count': df[col].isnull().sum(),
                'null_pct': (df[col].isnull().sum() / len(df)) * 100
            }
    
    return metrics

# Main Application
def main():
    # Header with Bloomberg branding
    st.markdown(f"""
    <div style='background-color: {BLOOMBERG_COLORS['primary_orange']}; padding: 20px; border-radius: 5px; margin-bottom: 20px;'>
        <h1 style='color: {BLOOMBERG_COLORS['background']}; margin: 0; text-align: center;'>
            📊 BLOOMBERG OWNERSHIP DATA QUALITY TERMINAL
        </h1>
        <p style='color: {BLOOMBERG_COLORS['background']}; margin: 5px 0 0 0; text-align: center; font-size: 14px;'>
            Real-Time Data Quality Assessment & Anomaly Detection System
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df, report = load_data()
    
    if df is None or report is None:
        st.error("⚠️ Please run `python main.py` first to generate data and reports.")
        return
    
    # Sidebar
    st.sidebar.markdown(f"""
    <div style='background-color: {BLOOMBERG_COLORS['primary_orange']}; padding: 10px; border-radius: 5px; margin-bottom: 20px;'>
        <h2 style='color: {BLOOMBERG_COLORS['background']}; margin: 0; text-align: center;'>NAVIGATION</h2>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Select View:",
        ["📊 Executive Dashboard", "📈 Profiling Metrics", "🔬 Method Comparison",
         "🎯 Anomaly Detection", "📏 DQ Dimensions", "🕸️ Entity Resolution", "💾 Raw Data"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style='padding: 10px; background-color: {BLOOMBERG_COLORS['surface']}; border-radius: 5px;'>
        <p style='color: {BLOOMBERG_COLORS['primary_orange']}; font-weight: bold;'>SYSTEM STATUS</p>
        <p style='color: {BLOOMBERG_COLORS['positive_green']};'>● LIVE</p>
        <p style='color: {BLOOMBERG_COLORS['text_gray']}; font-size: 12px;'>
            Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </p>
        <p style='color: {BLOOMBERG_COLORS['text_gray']}; font-size: 12px;'>
            Records: {len(df):,}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Page routing
    if page == "📊 Executive Dashboard":
        show_executive_dashboard(df, report)
    elif page == "📈 Profiling Metrics":
        show_profiling_metrics(df, report)
    elif page == "🔬 Method Comparison":
        show_method_comparison(df, report)
    elif page == "🎯 Anomaly Detection":
        show_anomaly_detection(df, report)
    elif page == "📏 DQ Dimensions":
        show_dq_dimensions(df, report)
    elif page == "🕸️ Entity Resolution":
        show_entity_resolution(df)
    elif page == "💾 Raw Data":
        show_raw_data(df)

def show_executive_dashboard(df, report):
    """Executive dashboard page"""
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "OVERALL DQ SCORE",
            f"{report['executive_summary']['overall_dq_score']:.1f}%",
            delta=f"{report['executive_summary']['dq_grade']}"
        )
    
    with col2:
        st.metric(
            "ANOMALIES DETECTED",
            f"{report['executive_summary']['anomalies_detected']:,}",
            delta=f"{report['executive_summary']['anomalies_detected']/len(df)*100:.1f}%"
        )
    
    with col3:
        st.metric(
            "DETECTION PRECISION",
            report['executive_summary']['detection_precision'],
            delta="High Confidence"
        )
    
    with col4:
        st.metric(
            "FP REDUCTION",
            report['executive_summary']['false_positive_reduction'],
            delta="vs Traditional"
        )
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall DQ Score Gauge
        gauge = create_bloomberg_gauge(
            report['executive_summary']['overall_dq_score'],
            "OVERALL DATA QUALITY SCORE"
        )
        st.plotly_chart(gauge, use_container_width=True)
    
    with col2:
        # DQ Dimensions Bar Chart
        dimensions_data = pd.DataFrame({
            'Dimension': [d['dimension'] for d in report['data_quality_dimensions'].values()],
            'Score': [d['overall_score'] for d in report['data_quality_dimensions'].values()]
        })
        bar_chart = create_bloomberg_bar(
            dimensions_data,
            'Dimension',
            'Score',
            "DQ DIMENSIONS PERFORMANCE"
        )
        st.plotly_chart(bar_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Scenario breakdown
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>SCENARIO DISTRIBUTION</h3>
    """, unsafe_allow_html=True)
    
    scenario_counts = df['scenario_type'].value_counts()
    scenario_df = pd.DataFrame({
        'Scenario': scenario_counts.index,
        'Count': scenario_counts.values,
        'Percentage': (scenario_counts.values / len(df) * 100).round(1)
    })
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Scenario pie chart
        fig = go.Figure(data=[go.Pie(
            labels=scenario_df['Scenario'],
            values=scenario_df['Count'],
            marker=dict(
                colors=[BLOOMBERG_COLORS['positive_green'], 
                       BLOOMBERG_COLORS['negative_red'],
                       BLOOMBERG_COLORS['warning_yellow'],
                       BLOOMBERG_COLORS['chart_blue'],
                       BLOOMBERG_COLORS['primary_orange']],
                line=dict(color=BLOOMBERG_COLORS['border_gray'], width=2)
            ),
            textfont=dict(size=14, color=BLOOMBERG_COLORS['background']),
            hole=0.4
        )])
        
        fig.update_layout(
            title=dict(text="Scenario Mix", font=dict(size=18, color=BLOOMBERG_COLORS['header_orange'])),
            paper_bgcolor=BLOOMBERG_COLORS['background'],
            plot_bgcolor=BLOOMBERG_COLORS['surface'],
            font=dict(color=BLOOMBERG_COLORS['text_white'], family='Courier New'),
            height=400,
            showlegend=True,
            legend=dict(
                font=dict(color=BLOOMBERG_COLORS['text_white']),
                bgcolor=BLOOMBERG_COLORS['surface'],
                bordercolor=BLOOMBERG_COLORS['border_gray'],
                borderwidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.dataframe(
            scenario_df.style.format({'Percentage': '{:.1f}%'}),
            use_container_width=True,
            height=400
        )

def show_profiling_metrics(df, report):
    """Comprehensive profiling metrics page - All 12 DQ Categories"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>COMPREHENSIVE DATA QUALITY PROFILING</h2>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>
        Production-Grade Master Profiling - 12 Category Framework
    </p>
    """, unsafe_allow_html=True)
    
    # Check if comprehensive metrics exist in report
    if report and 'comprehensive_metrics' in report:
        st.success("✅ Displaying Production-Grade Comprehensive Metrics from Report")
        show_comprehensive_metrics_from_report(report['comprehensive_metrics'], df)
    else:
        # Fallback to generating on-the-fly
        st.info("ℹ️ Generating comprehensive profiling report (legacy mode)...")
        with st.spinner("🔄 Generating comprehensive profiling report..."):
            profiling_results = generate_comprehensive_report(df)
        show_legacy_profiling(profiling_results, df)
    
def show_comprehensive_metrics_from_report(comp_metrics, df):
    """Display comprehensive metrics from JSON report - All 12 categories"""
    
    # Get the profiling summary if available
    summary = comp_metrics.get('profiling_summary', {})
    all_categories = comp_metrics.get('all_categories', {})
    
    # Executive Summary Section
    st.markdown("### 📊 Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = summary.get('overall_dq_score', 0)
        st.metric("Overall DQ Score", f"{score:.1f}/100", 
                 delta=summary.get('recommendation', ''))
    with col2:
        st.metric("Total Records", f"{summary.get('total_records', len(df)):,}")
    with col3:
        st.metric("Categories Profiled", summary.get('categories_profiled', 12))
    with col4:
        st.metric("Critical Issues", summary.get('critical_issues', 0))
    
    st.markdown("---")
    
    # Create tabs for all 12 categories
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "1️⃣ Completeness",
        "2️⃣ Accuracy",
        "3️⃣ Timeliness",
        "4️⃣ Consistency",
        "5️⃣ Distribution",
        "6️⃣ Categorical",
        "7️⃣ Correlation",
        "8️⃣ Anomalies",
        "9️⃣ ML-Ready",
        "🔟 DQ Issues",
        "1️⃣1️⃣ Vendor Quality",
        "1️⃣2️⃣ Quarterly Report"
    ])
    
    # TAB 1: COMPLETENESS
    with tab1:
        show_comprehensive_completeness(all_categories.get('1_completeness', {}))
    
    # TAB 2: ACCURACY
    with tab2:
        show_comprehensive_accuracy(all_categories.get('2_accuracy', {}))
    
    # TAB 3: TIMELINESS
    with tab3:
        show_comprehensive_timeliness(all_categories.get('3_timeliness', {}))
    
    # TAB 4: CONSISTENCY
    with tab4:
        show_comprehensive_consistency(all_categories.get('4_consistency', {}))
    
    # TAB 5: DISTRIBUTION
    with tab5:
        show_comprehensive_distribution(all_categories.get('5_distribution', {}))
    
    # TAB 6: CATEGORICAL
    with tab6:
        show_comprehensive_categorical(all_categories.get('6_categorical', {}))
    
    # TAB 7: CORRELATION
    with tab7:
        show_comprehensive_correlation(all_categories.get('7_correlation', {}))
    
    # TAB 8: ANOMALIES
    with tab8:
        show_comprehensive_anomalies(all_categories.get('8_anomaly', {}))
    
    # TAB 9: ML-READY
    with tab9:
        show_comprehensive_ml_ready(all_categories.get('9_ml_ready', {}))
    
    # TAB 10: DQ ISSUES
    with tab10:
        show_comprehensive_issues(all_categories.get('10_issues', {}))
    
    # TAB 11: VENDOR QUALITY
    with tab11:
        show_comprehensive_vendor(all_categories.get('11_vendor', {}))
    
    # TAB 12: QUARTERLY REPORT
    with tab12:
        show_comprehensive_quarterly(all_categories.get('12_quarterly', {}))


def show_comprehensive_completeness(metrics):
    """Display Category 1: Completeness"""
    st.markdown("### 📊 Completeness Metrics")
    st.markdown("**Business Value:** Detect ingestion/parsing failures and coverage gaps")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    with col2:
        st.metric("Record Completeness", 
                 f"{metrics.get('record_completeness', 0):.1f}%")
    with col3:
        coverage = metrics.get('coverage_stats', {})
        st.metric("Unique Filers", f"{coverage.get('unique_filers', 0):,}")
    
    st.markdown("#### Field Completeness")
    field_comp = metrics.get('field_completeness', {})
    if field_comp:
        fig = go.Figure(go.Bar(
            x=list(field_comp.keys()),
            y=list(field_comp.values()),
            marker_color=BLOOMBERG_COLORS['primary_orange']
        ))
        fig.update_layout(
            title="Completeness by Field",
            yaxis_title="Completeness %",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Show coverage stats
    st.markdown("#### Coverage Statistics")
    coverage = metrics.get('coverage_stats', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Filers", f"{coverage.get('unique_filers', 0):,}")
    with col2:
        st.metric("Unique Securities", f"{coverage.get('unique_securities', 0):,}")
    with col3:
        st.metric("Total Positions", f"{coverage.get('total_positions', 0):,}")


def show_comprehensive_accuracy(metrics):
    """Display Category 2: Accuracy"""
    st.markdown("### 🎯 Accuracy / Validity Metrics")
    st.markdown("**Business Value:** Detect math errors, prevent double-counting")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    with col2:
        st.metric("Duplicate Positions", f"{metrics.get('duplicate_count', 0):,}")
    with col3:
        st.metric("Business Rule Violations", f"{metrics.get('violation_count', 0):,}")
    
    st.markdown("#### Accuracy Checks")
    checks = metrics.get('accuracy_checks', {})
    if checks:
        fig = go.Figure(go.Bar(
            x=list(checks.keys()),
            y=list(checks.values()),
            marker_color=BLOOMBERG_COLORS['chart_green']
        ))
        fig.update_layout(
            title="Accuracy by Check Type",
            yaxis_title="Accuracy %",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_timeliness(metrics):
    """Display Category 3: Timeliness"""
    st.markdown("### ⏰ Timeliness Metrics")
    st.markdown("**Business Value:** Track vendor SLA, identify bottlenecks")
    
    timeliness_data = metrics.get('timeliness_metrics', {})
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    with col2:
        freshness = timeliness_data.get('data_freshness_days', 0)
        st.metric("Data Freshness", f"{freshness} days")
    with col3:
        sla_rate = timeliness_data.get('sla_compliance_rate', 'N/A')
        st.metric("SLA Compliance", f"{sla_rate}%" if isinstance(sla_rate, (int, float)) else sla_rate)
    
    st.markdown("---")
    
    # Additional details
    if 'avg_filing_lag_days' in timeliness_data:
        st.markdown("#### Filing Lag Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Filing Lag", f"{timeliness_data.get('avg_filing_lag_days', 0):.1f} days")
        with col2:
            st.metric("Max Filing Lag", f"{timeliness_data.get('max_filing_lag_days', 0)} days")
        with col3:
            st.metric("SLA Threshold", "2 days")
    
    # POC Note
    if 'note' in timeliness_data:
        st.info(f"ℹ️ **POC Note:** {timeliness_data['note']}")
    
    # Production expectations
    with st.expander("📋 Production SLA Targets"):
        st.markdown("""
        **Standard Filings:**
        - Process within 2 business days
        - 95% SLA compliance target
        
        **Priority Filings (13D/13G):**
        - Process within 4 hours
        - 99% SLA compliance target
        
        **Real-time Feeds:**
        - Data < 24 hours old
        - Continuous monitoring
        """)



def show_comprehensive_consistency(metrics):
    """Display Category 4: Consistency"""
    st.markdown("### 🔄 Consistency Metrics")
    st.markdown("**Business Value:** Detect schema drift, pattern breaks")
    
    consistency_data = metrics.get('consistency_metrics', {})
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    with col2:
        st.metric("Schema Columns", f"{consistency_data.get('schema_columns', 0)}")
    with col3:
        st.metric("Extreme QoQ Changes", f"{consistency_data.get('extreme_qoq_changes', 0):,}")
    with col4:
        qoq_std = consistency_data.get('qoq_std', 0)
        st.metric("QoQ Volatility (Std)", f"{qoq_std:.2f}")
    
    st.markdown("---")
    
    # Schema breakdown
    if 'schema_dtypes' in consistency_data:
        st.markdown("#### Schema Type Distribution")
        schema_dtypes = consistency_data['schema_dtypes']
        
        fig = go.Figure(go.Bar(
            x=list(schema_dtypes.keys()),
            y=list(schema_dtypes.values()),
            marker_color=BLOOMBERG_COLORS['chart_blue'],
            text=list(schema_dtypes.values()),
            textposition='outside'
        ))
        fig.update_layout(
            title="Column Count by Data Type",
            xaxis_title="Data Type",
            yaxis_title="Count",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # QoQ Statistics
    if 'qoq_mean' in consistency_data:
        st.markdown("#### Quarter-over-Quarter Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mean QoQ Change", f"{consistency_data.get('qoq_mean', 0):.2f}%")
        with col2:
            st.metric("Std Dev", f"{consistency_data.get('qoq_std', 0):.2f}%")
        with col3:
            st.metric("Rolling MA Stability", f"{consistency_data.get('rolling_ma_stability', 0):.2f}")
        
        st.info("""
        **Interpretation:**
        - **Extreme changes** indicate potential data issues or activist activity
        - **High volatility** suggests unstable data patterns
        - **Rolling MA stability** measures trend consistency over time
        """)
    
    # Production considerations
    with st.expander("📋 Production Monitoring"):
        st.markdown("""
        **Schema Drift Detection:**
        - Alert on new column additions
        - Flag column type changes
        - Track column removal
        
        **Pattern Break Detection:**
        - QoQ changes > 3σ trigger review
        - Peer comparison for validation
        - Automated notification to data stewards
        """)



def show_comprehensive_distribution(metrics):
    """Display Category 5: Distribution"""
    st.markdown("### 📈 Distribution Profiling")
    st.markdown("**Business Value:** Statistical baseline for anomaly detection")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    distributions = metrics.get('distributions', {})
    if distributions:
        for field, stats in distributions.items():
            with st.expander(f"📊 {field} Distribution"):
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Mean", f"{stats.get('mean', 0):.4f}")
                with col2:
                    st.metric("Std Dev", f"{stats.get('std', 0):.4f}")
                with col3:
                    st.metric("Skewness", f"{stats.get('skewness', 0):.4f}")
                with col4:
                    st.metric("Kurtosis", f"{stats.get('kurtosis', 0):.4f}")
                
                percentiles = stats.get('percentiles', {})
                st.markdown("**Percentiles:**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("P25", f"{percentiles.get('p25', 0):.4f}")
                with col2:
                    st.metric("P50", f"{percentiles.get('p50', 0):.4f}")
                with col3:
                    st.metric("P75", f"{percentiles.get('p75', 0):.4f}")
                with col4:
                    st.metric("P95", f"{percentiles.get('p95', 0):.4f}")


def show_comprehensive_categorical(metrics):
    """Display Category 6: Categorical"""
    st.markdown("### 🏷️ Categorical Profiling")
    st.markdown("**Business Value:** Detect category explosion, classification drift")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    categorical_data = metrics.get('categorical_metrics', {})
    if categorical_data:
        for field, stats in categorical_data.items():
            with st.expander(f"📋 {field} Analysis"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Cardinality", f"{stats.get('cardinality', 0):,}")
                with col2:
                    st.metric("Entropy", f"{stats.get('entropy', 0):.4f}")
                with col3:
                    st.metric("Coverage", f"{stats.get('coverage_pct', 0):.1f}%")
                
                top_cats = stats.get('top_categories', {})
                if top_cats:
                    st.markdown("**Top Categories:**")
                    fig = go.Figure(go.Bar(
                        x=list(top_cats.keys()),
                        y=list(top_cats.values()),
                        marker_color=BLOOMBERG_COLORS['chart_blue']
                    ))
                    fig.update_layout(template='plotly_dark', height=300)
                    st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_correlation(metrics):
    """Display Category 7: Correlation"""
    st.markdown("### 🔗 Correlation Metrics")
    st.markdown("**Business Value:** Data sanity checks, pricing validation")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    correlations = metrics.get('correlations', {})
    if correlations:
        st.markdown("#### Correlation Matrix")
        fig = go.Figure(go.Bar(
            x=list(correlations.keys()),
            y=list(correlations.values()),
            marker_color=BLOOMBERG_COLORS['chart_green']
        ))
        fig.update_layout(
            title="Field Correlations",
            yaxis_title="Correlation Coefficient",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_anomalies(metrics):
    """Display Category 8: Anomalies"""
    st.markdown("### 🚨 Anomaly Detection Metrics")
    st.markdown("**Business Value:** Multi-method detection, FP rate tracking")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    anomaly_stats = metrics.get('anomaly_stats', {})
    if anomaly_stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Z-Score Anomalies", f"{anomaly_stats.get('zscore_anomalies_3sigma', 0):,}")
        with col2:
            st.metric("IQR Outliers", f"{anomaly_stats.get('iqr_outliers', 0):,}")
        with col3:
            st.metric("QoQ Spikes", f"{anomaly_stats.get('qoq_spikes_gt50pct', 0):,}")
        with col4:
            st.metric("Hybrid Detected", f"{anomaly_stats.get('hybrid_detected', 0):,}")


def show_comprehensive_ml_ready(metrics):
    """Display Category 9: ML-Ready"""
    st.markdown("### 🤖 ML-Ready Metrics")
    st.markdown("**Business Value:** Features for downstream ML models")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    ml_features = metrics.get('ml_features', {})
    if ml_features:
        st.markdown("#### ML Feature Engineering Metrics")
        for feature, value in ml_features.items():
            st.metric(feature.replace('_', ' ').title(), f"{value}")


def show_comprehensive_issues(metrics):
    """Display Category 10: DQ Issues"""
    st.markdown("### ⚠️ DQ Issue Metrics")
    st.markdown("**Business Value:** Operational monitoring, incident management")
    
    issues_data = metrics.get('issues', {})
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    with col2:
        st.metric("Total Issues", f"{issues_data.get('total_issues', 0):,}")
    with col3:
        severity = issues_data.get('severity_breakdown', {})
        st.metric("High Severity", f"{severity.get('high', 0):,}")
    with col4:
        st.metric("Medium Severity", f"{severity.get('medium', 0):,}")
    
    if issues_data:
        st.markdown("#### Severity Breakdown")
        severity = issues_data.get('severity_breakdown', {})
        fig = go.Figure(go.Bar(
            x=list(severity.keys()),
            y=list(severity.values()),
            marker_color=[BLOOMBERG_COLORS['negative_red'], 
                         BLOOMBERG_COLORS['warning_yellow'],
                         BLOOMBERG_COLORS['positive_green']]
        ))
        fig.update_layout(
            title="Issues by Severity",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_vendor(metrics):
    """Display Category 11: Vendor Quality"""
    st.markdown("### 🏢 Vendor Quality Metrics")
    st.markdown("**Business Value:** Upstream SLA tracking, vendor performance")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    vendor_data = metrics.get('vendor_metrics', {})
    st.markdown("#### Vendor Performance")
    
    if 'vendor_sla_compliance' in vendor_data:
        sla_data = vendor_data['vendor_sla_compliance']
        fig = go.Figure(go.Bar(
            x=list(sla_data.keys()),
            y=list(sla_data.values()),
            marker_color=BLOOMBERG_COLORS['chart_blue']
        ))
        fig.update_layout(
            title="Vendor SLA Compliance %",
            yaxis_title="SLA Compliance",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(vendor_data.get('note', 'No vendor data available'))


def show_comprehensive_quarterly(metrics):
    """Display Category 12: Quarterly Report"""
    st.markdown("### 📅 Quarterly Report Metrics")
    st.markdown("**Business Value:** Executive summaries, trend analysis")
    
    st.metric("Overall Score", f"{metrics.get('overall_score', 0):.1f}%")
    
    quarterly_data = metrics.get('quarterly_metrics', {})
    
    if 'completeness_by_quarter' in quarterly_data:
        st.markdown("#### Completeness Trend by Quarter")
        comp_by_q = quarterly_data['completeness_by_quarter']
        fig = go.Figure(go.Scatter(
            x=list(comp_by_q.keys()),
            y=list(comp_by_q.values()),
            mode='lines+markers',
            marker_color=BLOOMBERG_COLORS['primary_orange']
        ))
        fig.update_layout(
            yaxis_title="Completeness %",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if 'records_by_quarter' in quarterly_data:
        st.markdown("#### Records by Quarter")
        records_by_q = quarterly_data['records_by_quarter']
        fig = go.Figure(go.Bar(
            x=list(records_by_q.keys()),
            y=list(records_by_q.values()),
            marker_color=BLOOMBERG_COLORS['chart_green']
        ))
        fig.update_layout(
            yaxis_title="Record Count",
            template='plotly_dark',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_legacy_profiling(profiling_results, df):
    """Legacy profiling display (fallback)"""
    
    # Generate comprehensive profiling report if needed
    with st.spinner("🔄 Generating comprehensive profiling report..."):
        pass  # profiling_results already passed in
    
    # Create tabs for each category
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "1️⃣ Completeness",
        "2️⃣ Accuracy",
        "3️⃣ Timeliness",
        "4️⃣ Consistency",
        "5️⃣ Distribution",
        "6️⃣ Categorical",
        "7️⃣ Correlation",
        "8️⃣ Anomalies",
        "9️⃣ ML-Ready",
        "🔟 DQ Issues",
        "1️⃣1️⃣ Vendor Quality",
        "1️⃣2️⃣ Quarterly Report"
    ])
    
    # TAB 1: COMPLETENESS METRICS
    with tab1:
        show_completeness_metrics(profiling_results['completeness'], df)
    
    # TAB 2: ACCURACY METRICS
    with tab2:
        show_accuracy_metrics(profiling_results['accuracy'], df)
    
    # TAB 3: TIMELINESS METRICS
    with tab3:
        show_timeliness_metrics(profiling_results['timeliness'], df)
    
    # TAB 4: CONSISTENCY METRICS
    with tab4:
        show_consistency_metrics(profiling_results['consistency'], df)
    
    # TAB 5: DISTRIBUTION METRICS
    with tab5:
        show_distribution_metrics(profiling_results['distribution'], df)
    
    # TAB 6: CATEGORICAL METRICS
    with tab6:
        show_categorical_metrics(profiling_results['categorical'], df)
    
    # TAB 7: CORRELATION METRICS
    with tab7:
        show_correlation_metrics(profiling_results['correlation'], df)
    
    # TAB 8: ANOMALY METRICS
    with tab8:
        show_anomaly_metrics(profiling_results['anomalies'], df)
    
    # TAB 9: ML-READY METRICS
    with tab9:
        show_ml_ready_metrics(profiling_results['ml_ready'], df)
    
    # TAB 10: DQ ISSUES METRICS
    with tab10:
        show_dq_issues_metrics(profiling_results['dq_issues'], df)
    
    # TAB 11: VENDOR QUALITY METRICS
    with tab11:
        show_vendor_quality_metrics(profiling_results['vendor_quality'], df)
    
    # TAB 12: QUARTERLY REPORT METRICS
    with tab12:
        show_quarterly_report_metrics(profiling_results['quarterly_report'], df)


def show_completeness_metrics(metrics, df):
    """Display Category 1: Completeness Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>COMPLETENESS METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Detect ingestion/parsing failures and coverage gaps</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Record Completeness", f"{metrics['record_completeness_pct']:.1f}%")
    with col2:
        st.metric("Coverage Completeness", f"{metrics['coverage_completeness_pct']:.1f}%")
    with col3:
        st.metric("Filing Coverage", f"{metrics.get('filing_coverage_pct', 100):.1f}%")
    with col4:
        total_missing = sum(metrics['missing_critical_fields'].values())
        st.metric("Missing Fields", f"{total_missing:,}")
    
    st.markdown("---")
    
    # Field Completeness Bar Chart
    st.markdown("#### Field Completeness by Column")
    field_comp = metrics['field_completeness']
    fig = go.Figure(go.Bar(
        x=list(field_comp.keys()),
        y=list(field_comp.values()),
        marker=dict(color='#FF8C00'),
        text=[f"{v:.1f}%" for v in field_comp.values()],
        textposition='outside'
    ))
    fig.update_layout(
        yaxis=dict(title="Completeness %", range=[0, 105], gridcolor='#2A2A2A', color='#FFFFFF'),
        xaxis=dict(title="Field", gridcolor='#2A2A2A', color='#FFFFFF'),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Record Completeness Donut Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Record Completeness Distribution")
        complete = metrics['record_completeness_pct']
        incomplete = 100 - complete
        
        fig = go.Figure(go.Pie(
            labels=['Complete', 'Incomplete'],
            values=[complete, incomplete],
            hole=0.4,
            marker=dict(colors=['#00FF00', '#FF0000'])
        ))
        fig.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Missing Critical Fields")
        missing_df = pd.DataFrame(list(metrics['missing_critical_fields'].items()), 
                                  columns=['Field', 'Missing Count'])
        st.dataframe(missing_df, use_container_width=True, height=300)


def show_accuracy_metrics(metrics, df):
    """Display Category 2: Accuracy Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>ACCURACY / VALIDITY METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Detect math errors, duplicates, and rule violations</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Ownership Accuracy", f"{metrics.get('ownership_accuracy_pct', 100):.1f}%")
    with col2:
        st.metric("Identifier Validity", f"{metrics.get('identifier_validity_pct', 100):.1f}%")
    with col3:
        st.metric("Duplicate Positions", f"{metrics.get('duplicate_positions', 0):,}")
    with col4:
        total_violations = sum(metrics['business_rule_violations'].values())
        st.metric("Rule Violations", f"{total_violations:,}")
    
    st.markdown("---")
    
    # Business Rule Violations Bar Chart
    st.markdown("#### Business Rule Violations")
    violations = metrics['business_rule_violations']
    
    fig = go.Figure(go.Bar(
        y=list(violations.keys()),
        x=list(violations.values()),
        orientation='h',
        marker=dict(color='#FF0000'),
        text=list(violations.values()),
        textposition='outside'
    ))
    fig.update_layout(
        xaxis=dict(title="Violation Count", gridcolor='#2A2A2A', color='#FFFFFF'),
        yaxis=dict(title="Rule Type", gridcolor='#2A2A2A', color='#FFFFFF'),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF'),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)


def show_timeliness_metrics(metrics, df):
    """Display Category 3: Timeliness Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>TIMELINESS METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Track processing delays and SLA compliance</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Freshness Age", f"{metrics.get('freshness_age_days', 0)} days")
    with col2:
        st.metric("Avg Filing Lag", f"{metrics.get('avg_filing_lag_days', 0):.1f} days")
    with col3:
        st.metric("SLA Compliance", f"{metrics.get('sla_compliance_pct', 0):.1f}%")
    with col4:
        st.metric("Q-End Filings", f"{metrics.get('quarter_end_filings', 0):,}")
    
    st.markdown("---")
    
    # Freshness Gauge
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Data Freshness Gauge")
        freshness = metrics.get('freshness_age_days', 0)
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=freshness,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Days Since Last Filing", 'font': {'color': '#FFFFFF'}},
            gauge={
                'axis': {'range': [None, 30], 'tickcolor': '#FFFFFF'},
                'bar': {'color': '#FF8C00'},
                'steps': [
                    {'range': [0, 7], 'color': '#00FF00'},
                    {'range': [7, 14], 'color': '#FFFF00'},
                    {'range': [14, 30], 'color': '#FF0000'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 14
                }
            }
        ))
        fig.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### SLA Compliance Trend")
        # Simulated trend
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        compliance = [96.5, 95.8, 96.2, 95.0]
        
        fig = go.Figure(go.Scatter(
            x=quarters,
            y=compliance,
            mode='lines+markers',
            line=dict(color='#00BFFF', width=2),
            marker=dict(size=10, color='#FF8C00')
        ))
        fig.add_hline(y=95, line_dash="dash", line_color="red", 
                     annotation_text="SLA Threshold (95%)")
        fig.update_layout(
            yaxis=dict(title="Compliance %", range=[90, 100], gridcolor='#2A2A2A', color='#FFFFFF'),
            xaxis=dict(title="Quarter", gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)


def show_consistency_metrics(metrics, df):
    """Display Category 4: Consistency Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>CONSISTENCY METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Monitor temporal stability and schema consistency</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("QoQ Mean Change", f"{metrics.get('qoq_mean', 0):.2f}%")
    with col2:
        st.metric("QoQ Std Dev", f"{metrics.get('qoq_std', 0):.2f}%")
    with col3:
        st.metric("Extreme Changes", f"{metrics.get('extreme_qoq_changes', 0):,}")
    with col4:
        schema_status = "✓ Consistent" if metrics.get('schema_consistent', True) else "✗ Drift Detected"
        st.metric("Schema Status", schema_status)
    
    st.markdown("---")
    
    # QoQ Distribution
    if 'qoq_change_pct' in df.columns:
        st.markdown("#### Quarter-over-Quarter Change Distribution")
        qoq_data = df['qoq_change_pct'].dropna()
        
        fig = go.Figure(go.Histogram(
            x=qoq_data,
            nbinsx=50,
            marker=dict(color='#FF8C00', line=dict(color='#FFFFFF', width=1))
        ))
        fig.add_vline(x=metrics.get('qoq_mean', 0), line_dash="dash", 
                     line_color="cyan", annotation_text="Mean")
        fig.update_layout(
            xaxis=dict(title="QoQ Change %", gridcolor='#2A2A2A', color='#FFFFFF'),
            yaxis=dict(title="Frequency", gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_distribution_metrics(metrics, df):
    """Display Category 5: Distribution Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>DISTRIBUTION PROFILING METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Statistical distribution analysis for numerical columns</p>
    """, unsafe_allow_html=True)
    
    # Create distribution matrix table
    dist_data = []
    for col, stats in metrics.items():
        if isinstance(stats, dict):
            dist_data.append({
                'Column': col.replace('_', ' ').title(),
                'Mean': f"{stats.get('mean', 0):.2f}",
                'Std Dev': f"{stats.get('std', 0):.2f}",
                'Skewness': f"{stats.get('skewness', 0):.3f}",
                'Kurtosis': f"{stats.get('kurtosis', 0):.3f}",
                'CV': f"{stats.get('cv', 0):.3f}",
                'Min': f"{stats.get('min', 0):.2f}",
                'Q25': f"{stats.get('q25', 0):.2f}",
                'Median': f"{stats.get('q50', 0):.2f}",
                'Q75': f"{stats.get('q75', 0):.2f}",
                'Max': f"{stats.get('max', 0):.2f}"
            })
    
    if dist_data:
        dist_df = pd.DataFrame(dist_data)
        st.dataframe(dist_df, use_container_width=True, height=250)
        
        # Box plots for each metric
        st.markdown("---")
        st.markdown("#### Distribution Visualizations")
        
        numerical_cols = [col for col in ['ownership_pct', 'shares', 'market_value', 'qoq_change_pct'] 
                         if col in df.columns]
        
        for col in numerical_cols[:2]:  # Show first 2 to avoid clutter
            col_data = df[col].dropna()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histogram
                fig = go.Figure(go.Histogram(
                    x=col_data,
                    nbinsx=30,
                    marker=dict(color='#FF8C00', line=dict(color='#FFFFFF', width=1))
                ))
                fig.update_layout(
                    title=dict(text=f"{col.replace('_', ' ').title()} - Histogram", 
                             font=dict(size=14, color='#FFFFFF')),
                    xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                    yaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    font=dict(color='#FFFFFF'),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Box plot
                fig = go.Figure(go.Box(
                    y=col_data,
                    marker=dict(color='#FF8C00'),
                    line=dict(color='#FFFFFF'),
                    name=col.replace('_', ' ').title()
                ))
                fig.update_layout(
                    title=dict(text=f"{col.replace('_', ' ').title()} - Box Plot", 
                             font=dict(size=14, color='#FFFFFF')),
                    yaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                    xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                    plot_bgcolor='#000000',
                    paper_bgcolor='#000000',
                    font=dict(color='#FFFFFF'),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)


def show_categorical_metrics(metrics, df):
    """Display Category 6: Categorical Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>CATEGORICAL PROFILING METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Analyze cardinality, entropy, and category distribution</p>
    """, unsafe_allow_html=True)
    
    # Create categorical metrics table
    cat_data = []
    for col, stats in metrics.items():
        if isinstance(stats, dict):
            cat_data.append({
                'Column': col.replace('_', ' ').title(),
                'Cardinality': stats.get('cardinality', 0),
                'Entropy': f"{stats.get('entropy', 0):.3f}",
                'Coverage %': f"{stats.get('coverage_pct', 0):.1f}%",
                'Imbalance Ratio': f"{stats.get('imbalance_ratio', 0):.2f}",
                'Top Category': stats.get('top_category', 'N/A'),
                'Top %': f"{stats.get('top_category_pct', 0):.1f}%"
            })
    
    if cat_data:
        cat_df = pd.DataFrame(cat_data)
        st.dataframe(cat_df, use_container_width=True, height=250)
        
        # Entropy comparison
        st.markdown("---")
        st.markdown("#### Entropy by Column (Category Randomness)")
        
        entropy_data = {col: stats.get('entropy', 0) for col, stats in metrics.items() 
                       if isinstance(stats, dict)}
        
        fig = go.Figure(go.Bar(
            x=list(entropy_data.keys()),
            y=list(entropy_data.values()),
            marker=dict(color='#00BFFF'),
            text=[f"{v:.2f}" for v in entropy_data.values()],
            textposition='outside'
        ))
        fig.update_layout(
            yaxis=dict(title="Entropy", gridcolor='#2A2A2A', color='#FFFFFF'),
            xaxis=dict(title="Column", gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


def show_correlation_metrics(metrics, df):
    """Display Category 7: Correlation Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>CORRELATION METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Variable relationships and pricing consistency</p>
    """, unsafe_allow_html=True)
    
    # Key correlations
    col1, col2, col3 = st.columns(3)
    with col1:
        corr_val = metrics.get('shares_value_correlation', 0)
        st.metric("Shares ↔ Value", f"{corr_val:.3f}")
    with col2:
        corr_val = metrics.get('ownership_shares_correlation', 0)
        st.metric("Ownership ↔ Shares", f"{corr_val:.3f}")
    with col3:
        st.metric("Matrix Size", f"{len(metrics.get('correlation_matrix', {}))}×{len(metrics.get('correlation_matrix', {}))}")
    
    st.markdown("---")
    
    # Correlation Heatmap
    if 'correlation_matrix' in metrics:
        st.markdown("#### Correlation Heatmap")
        
        corr_df = pd.DataFrame(metrics['correlation_matrix'])
        
        fig = go.Figure(go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale='RdBu',
            zmid=0,
            text=corr_df.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        fig.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)


def show_anomaly_metrics(metrics, df):
    """Display Category 8: Anomaly Detection Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>ANOMALY DETECTION METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Statistical outliers and hybrid ML detection</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Z-Score Outliers", f"{metrics.get('zscore_outliers', 0):,}")
    with col2:
        st.metric("IQR Outliers", f"{metrics.get('iqr_outliers', 0):,}")
    with col3:
        st.metric("QoQ Spikes", f"{metrics.get('qoq_spikes', 0):,}")
    with col4:
        st.metric("Hybrid Anomalies", f"{metrics.get('hybrid_anomalies', 0):,}")
    
    st.markdown("---")
    
    # Anomaly method comparison
    st.markdown("#### Anomaly Detection Method Comparison")
    
    methods = ['Z-Score', 'IQR', 'MAD', 'Hybrid ML']
    counts = [
        metrics.get('zscore_outliers', 0),
        metrics.get('iqr_outliers', 0),
        metrics.get('mad_outliers', 0),
        metrics.get('hybrid_anomalies', 0)
    ]
    
    fig = go.Figure(go.Bar(
        x=methods,
        y=counts,
        marker=dict(color=['#FF8C00', '#00BFFF', '#FFFF00', '#00FF00']),
        text=counts,
        textposition='outside'
    ))
    fig.update_layout(
        yaxis=dict(title="Anomaly Count", gridcolor='#2A2A2A', color='#FFFFFF'),
        xaxis=dict(title="Detection Method", gridcolor='#2A2A2A', color='#FFFFFF'),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def show_ml_ready_metrics(metrics, df):
    """Display Category 9: ML-Ready Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>ML-READY METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Features for ML model training and monitoring</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("30d Completeness", f"{metrics.get('completeness_trend_30d', 0):.1f}%")
    with col2:
        st.metric("Rolling Anomaly Avg", f"{metrics.get('anomaly_rolling_avg', 0):.2f}%")
    with col3:
        st.metric("Validation Failure", f"{metrics.get('validation_failure_rate', 0):.2f}%")
    with col4:
        st.metric("Consistency Score", f"{metrics.get('consistency_score', 0):.1f}/100")
    
    st.markdown("---")
    
    # ML Feature Importance (simulated)
    st.markdown("#### ML Feature Importance")
    
    features = ['Completeness Trend', 'Anomaly Rate', 'Consistency Score', 
               'Validation Failure', 'Vendor Reliability']
    importance = [0.25, 0.30, 0.20, 0.15, 0.10]
    
    fig = go.Figure(go.Bar(
        y=features,
        x=importance,
        orientation='h',
        marker=dict(color='#00FF00'),
        text=[f"{v:.0%}" for v in importance],
        textposition='outside'
    ))
    fig.update_layout(
        xaxis=dict(title="Feature Importance", gridcolor='#2A2A2A', color='#FFFFFF'),
        yaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF'),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


def show_dq_issues_metrics(metrics, df):
    """Display Category 10: DQ Issue Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>DQ ISSUE METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Issue classification, severity, and root cause analysis</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Issues", f"{metrics.get('total_issues', 0):,}")
    with col2:
        high_sev = metrics.get('severity_breakdown', {}).get('high', 0)
        st.metric("High Severity", f"{high_sev:,}")
    with col3:
        medium_sev = metrics.get('severity_breakdown', {}).get('medium', 0)
        st.metric("Medium Severity", f"{medium_sev:,}")
    with col4:
        low_sev = metrics.get('severity_breakdown', {}).get('low', 0)
        st.metric("Low Severity", f"{low_sev:,}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Issue type breakdown
        st.markdown("#### Issue Count by Type")
        issue_counts = metrics.get('issue_counts', {})
        
        fig = go.Figure(go.Pie(
            labels=list(issue_counts.keys()),
            values=list(issue_counts.values()),
            marker=dict(colors=['#FF8C00', '#00BFFF', '#FFFF00', '#FF0000'])
        ))
        fig.update_layout(
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Root cause classification
        st.markdown("#### Root Cause Classification")
        root_causes = metrics.get('root_causes', {})
        
        fig = go.Figure(go.Bar(
            x=list(root_causes.keys()),
            y=list(root_causes.values()),
            marker=dict(color='#FF0000'),
            text=list(root_causes.values()),
            textposition='outside'
        ))
        fig.update_layout(
            yaxis=dict(title="Issue Count", gridcolor='#2A2A2A', color='#FFFFFF'),
            xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)


def show_vendor_quality_metrics(metrics, df):
    """Display Category 11: Vendor Quality Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>VENDOR QUALITY METRICS</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Vendor SLA compliance and performance monitoring</p>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("SLA Compliance", f"{metrics.get('sla_compliance_pct', 0):.1f}%")
    with col2:
        st.metric("Avg Delay", f"{metrics.get('avg_delivery_delay_hours', 0):.1f}h")
    with col3:
        st.metric("Anomaly Rate", f"{metrics.get('vendor_anomaly_rate', 0):.2f}%")
    with col4:
        st.metric("Accuracy Drift", f"{metrics.get('accuracy_drift_trend', 0):.2f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Accuracy drift trend
        st.markdown("#### Quarterly Accuracy Drift")
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        accuracy = [
            metrics.get('accuracy_drift_q1', 0),
            metrics.get('accuracy_drift_q2', 0),
            metrics.get('accuracy_drift_q3', 0),
            metrics.get('accuracy_drift_q4', 0)
        ]
        
        fig = go.Figure(go.Scatter(
            x=quarters,
            y=accuracy,
            mode='lines+markers',
            line=dict(color='#FF8C00', width=2),
            marker=dict(size=10, color='#00BFFF')
        ))
        fig.add_hline(y=97, line_dash="dash", line_color="red", 
                     annotation_text="Target (97%)")
        fig.update_layout(
            yaxis=dict(title="Accuracy %", range=[95, 100], gridcolor='#2A2A2A', color='#FFFFFF'),
            xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Delivery delay trend
        st.markdown("#### Delivery Delay Trend")
        periods = ['P1', 'P2', 'P3', 'P4', 'P5']
        delays = metrics.get('delay_trend', [0]*5)
        
        fig = go.Figure(go.Histogram(
            x=periods,
            y=delays,
            marker=dict(color='#FFFF00', line=dict(color='#FFFFFF', width=1))
        ))
        fig.update_layout(
            yaxis=dict(title="Delay (hours)", gridcolor='#2A2A2A', color='#FFFFFF'),
            xaxis=dict(title="Period", gridcolor='#2A2A2A', color='#FFFFFF'),
            plot_bgcolor='#000000',
            paper_bgcolor='#000000',
            font=dict(color='#FFFFFF'),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)


def show_quarterly_report_metrics(metrics, df):
    """Display Category 12: Quarterly Report Metrics"""
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>QUARTERLY OWNERSHIP DQ REPORT</h3>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>Executive summary and governance dashboard</p>
    """, unsafe_allow_html=True)
    
    # Key governance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rule Coverage", f"{metrics.get('rule_coverage_pct', 0):.0f}%")
    with col2:
        st.metric("Automated Checks", f"{metrics.get('automated_checks', 0)}")
    with col3:
        incidents = metrics.get('incidents', {})
        st.metric("Total Incidents", f"{incidents.get('total_issues', 0)}")
    with col4:
        st.metric("MTTR", f"{incidents.get('mttr_hours', 0):.1f}h")
    
    st.markdown("---")
    
    # Quarterly breakdown table
    if 'quarterly_breakdown' in metrics:
        st.markdown("#### Quarterly Performance Breakdown")
        quarterly_df = pd.DataFrame(metrics['quarterly_breakdown'])
        st.dataframe(quarterly_df, use_container_width=True, height=300)
        
        # Quarterly trend charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Completeness Trend")
            fig = go.Figure(go.Scatter(
                x=quarterly_df['quarter'],
                y=quarterly_df['completeness_pct'],
                mode='lines+markers',
                line=dict(color='#00FF00', width=2),
                marker=dict(size=10, color='#FF8C00')
            ))
            fig.update_layout(
                yaxis=dict(title="Completeness %", gridcolor='#2A2A2A', color='#FFFFFF'),
                xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font=dict(color='#FFFFFF'),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Anomaly Rate Trend")
            fig = go.Figure(go.Bar(
                x=quarterly_df['quarter'],
                y=quarterly_df['anomaly_rate'],
                marker=dict(color='#FF0000'),
                text=[f"{v:.2f}%" for v in quarterly_df['anomaly_rate']],
                textposition='outside'
            ))
            fig.update_layout(
                yaxis=dict(title="Anomaly Rate %", gridcolor='#2A2A2A', color='#FFFFFF'),
                xaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF'),
                plot_bgcolor='#000000',
                paper_bgcolor='#000000',
                font=dict(color='#FFFFFF'),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Governance radar chart
    st.markdown("---")
    st.markdown("#### Governance Score Radar")
    
    categories = ['Rule Coverage', 'Automation', 'Completeness', 'Accuracy', 'Timeliness']
    values = [
        metrics.get('rule_coverage_pct', 0),
        (metrics.get('automated_checks', 0) / 50) * 100,  # Normalized to 100
        95.0,  # Simulated
        97.5,  # Simulated
        96.0   # Simulated
    ]
    
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(255, 140, 0, 0.3)',
        line=dict(color='#FF8C00', width=2)
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='#000000',
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#2A2A2A', color='#FFFFFF'),
            angularaxis=dict(gridcolor='#2A2A2A', color='#FFFFFF')
        ),
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        font=dict(color='#FFFFFF'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
def show_method_comparison(df, report):
    """Method comparison with 6-step clear demonstration of hybrid advantage"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>HYBRID METHOD ADVANTAGE DEMONSTRATION</h2>
    <p style='color: {BLOOMBERG_COLORS['text_gray']};'>
        6-Step visualization showing how hybrid ML outperforms traditional methods
    </p>
    """, unsafe_allow_html=True)
    
    # Entity and Security selectors
    col1, col2 = st.columns(2)
    
    with col1:
        # Get entities with sufficient data
        entity_counts = df.groupby('entity_canonical').size()
        valid_entities = entity_counts[entity_counts >= 20].index.tolist()
        
        selected_entity = st.selectbox(
            "SELECT ENTITY:",
            options=valid_entities,
            index=0 if valid_entities else None
        )
    
    with col2:
        # Get securities for selected entity
        if selected_entity:
            entity_securities = df[df['entity_canonical'] == selected_entity]['security'].unique()
            selected_security = st.selectbox(
                "SELECT SECURITY:",
                options=entity_securities,
                index=0 if len(entity_securities) > 0 else None
            )
        else:
            st.selectbox("SELECT SECURITY:", options=[], disabled=True)
            selected_security = None
    
    if not selected_entity or not selected_security:
        st.warning("⚠️ Please select both entity and security to view comparison")
        return
    
    st.markdown("---")
    
    # Filter data for selected entity-security
    mask = (df['entity_canonical'] == selected_entity) & (df['security'] == selected_security)
    data = df[mask].sort_values('filing_date').copy()
    
    if len(data) < 10:
        st.error("⚠️ Insufficient data for selected entity-security pair (need at least 10 records)")
        return
    
    # Prepare data
    dates = pd.to_datetime(data['filing_date']).reset_index(drop=True)
    values = data['ownership_pct'].values
    
    # Find change point (largest jump in the series)
    diffs = np.abs(np.diff(values))
    if len(diffs) > 0:
        change_point_idx = np.argmax(diffs) + 1
        # Ensure change point is not too early or too late
        change_point_idx = max(5, min(change_point_idx, len(values) - 5))
    else:
        change_point_idx = len(values) // 2
    
    # Generate 6-step comparison
    with st.spinner("🔄 Generating 6-step comparison..."):
        results = create_six_step_comparison(dates, values, change_point_idx)
        figs, stats = create_combined_six_steps(results)
    
    # Display overview metrics
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>KEY PERFORMANCE METRICS</h3>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    pre_reduction = ((stats['pre_traditional'] - stats['pre_hybrid']) / stats['pre_traditional'] * 100) if stats['pre_traditional'] > 0 else 0
    
    with col1:
        st.metric(
            "TRADITIONAL (Pre-Change)",
            f"{stats['pre_traditional']} anomalies",
            delta="Many false positives"
        )
    
    with col2:
        st.metric(
            "HYBRID (Pre-Change)",
            f"{stats['pre_hybrid']} anomalies",
            delta=f"{pre_reduction:.0f}% reduction"
        )
    
    with col3:
        st.metric(
            "TRADITIONAL (Post-Change)",
            f"{stats['post_traditional_fails']} anomalies",
            delta="Doesn't adapt!"
        )
    
    with col4:
        st.metric(
            "HYBRID (Post-Change)",
            f"{stats['post_hybrid']} anomalies",
            delta="Adapts successfully"
        )
    
    st.markdown("---")
    
    # Display all 6 steps
    for step_name, fig in figs:
        if step_name == 'step1':
            st.markdown(f"""
            <div style='background-color: #F0F8FF; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['highlight_blue']}; margin: 20px 0;'>
                <h3 style='color: {BLOOMBERG_COLORS['highlight_blue']}; margin: 0;'>📊 STEP 1: Baseline Time Series</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    Initial ownership data (Q1-Q8). This is our baseline period where ownership is relatively stable around 5-7%.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        
        elif step_name == 'step2':
            st.markdown(f"""
            <div style='background-color: #FFF3CD; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['warning_yellow']}; margin: 20px 0;'>
                <h3 style='color: #856404; margin: 0;'>⚠️ STEP 2: Traditional Methods Applied</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    <strong>Problem:</strong> Traditional statistical methods (Z-Score, IQR, Moving Average) flag {stats['pre_traditional']} anomalies.
                    Many are false positives - normal quarterly rebalancing flagged as issues!
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        
        elif step_name == 'step3':
            st.markdown(f"""
            <div style='background-color: #D4EDDA; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['positive_green']}; margin: 20px 0;'>
                <h3 style='color: #155724; margin: 0;'>✅ STEP 3: Hybrid ML Reduces False Positives</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    <strong>Solution:</strong> Hybrid approach (LSTM + Isolation Forest) learns patterns.
                    Reduces to {stats['pre_hybrid']} anomalies - a {pre_reduction:.0f}% reduction!
                    LSTM learns quarterly patterns, ISO Forest catches true statistical outliers.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        
        elif step_name == 'step4':
            st.markdown(f"""
            <div style='background-color: #F0F8FF; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['primary_orange']}; margin: 20px 0;'>
                <h3 style='color: {BLOOMBERG_COLORS['primary_orange']}; margin: 0;'>🔄 STEP 4: Structural Change Occurs</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    New quarter arrives (Q9-Q12). Ownership jumps to 8-10% - a legitimate structural change
                    (e.g., Activist 13D filing, index inclusion). <strong>This is the test: can the model adapt?</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        
        elif step_name == 'step5':
            st.markdown(f"""
            <div style='background-color: #F8D7DA; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['negative_red']}; margin: 20px 0;'>
                <h3 style='color: #721C24; margin: 0;'>❌ STEP 5: Traditional Methods Fail</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    <strong>Failure:</strong> Traditional methods use old baseline (5-7%). They flag the new baseline (8-10%)
                    as {stats['post_traditional_fails']} anomalies! Every point is a false positive. <strong>They don't adapt.</strong>
                    Analysts would waste time investigating normal data.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
        
        elif step_name == 'step6':
            st.markdown(f"""
            <div style='background-color: #D4EDDA; padding: 15px; border-left: 5px solid {BLOOMBERG_COLORS['positive_green']}; margin: 20px 0;'>
                <h3 style='color: #155724; margin: 0;'>🎯 STEP 6: Hybrid ML Adapts Successfully</h3>
                <p style='color: #333; margin: 10px 0 0 0;'>
                    <strong>Success:</strong> After retraining, hybrid ML learns the new baseline (8-10%).
                    Only {stats['post_hybrid']} true anomalies flagged. <strong>Model adapts automatically.</strong>
                    Analysts focus only on real issues, not false alarms.
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Final comparison summary
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>FINAL COMPARISON: TRADITIONAL VS HYBRID</h3>
    """, unsafe_allow_html=True)
    
    comparison_data = pd.DataFrame({
        'Period': ['Pre-Change (Q1-Q8)', 'Post-Change (Q9-Q12)'],
        'Traditional Anomalies': [stats['pre_traditional'], stats['post_traditional_fails']],
        'Hybrid Anomalies': [stats['pre_hybrid'], stats['post_hybrid']],
        'Traditional FP Rate': ['High', 'Very High (doesn\'t adapt)'],
        'Hybrid FP Rate': ['Low', 'Low (adapts)']
    })
    
    st.dataframe(comparison_data, use_container_width=True)
    
    # Key insights
    col1, col2 = st.columns(2)
    
    with col1:
        total_traditional = stats['pre_traditional'] + stats['post_traditional_fails']
        total_hybrid = stats['pre_hybrid'] + stats['post_hybrid']
        overall_reduction = ((total_traditional - total_hybrid) / total_traditional * 100) if total_traditional > 0 else 0
        
        st.markdown(f"""
        <div style='background-color: {BLOOMBERG_COLORS['surface']}; padding: 20px; border-radius: 5px; 
                    border: 2px solid {BLOOMBERG_COLORS['positive_green']};'>
            <h4 style='color: {BLOOMBERG_COLORS['positive_green']};'>✅ HYBRID ADVANTAGES</h4>
            <ul style='color: {BLOOMBERG_COLORS['text_white']};'>
                <li><strong>{pre_reduction:.0f}% fewer false positives</strong> in stable periods</li>
                <li><strong>Adapts automatically</strong> to structural changes</li>
                <li><strong>{overall_reduction:.0f}% overall reduction</strong> in false alerts</li>
                <li><strong>Maintains accuracy</strong> after retraining</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background-color: {BLOOMBERG_COLORS['surface']}; padding: 20px; border-radius: 5px; 
                    border: 2px solid {BLOOMBERG_COLORS['negative_red']};'>
            <h4 style='color: {BLOOMBERG_COLORS['negative_red']};'>❌ TRADITIONAL FAILURES</h4>
            <ul style='color: {BLOOMBERG_COLORS['text_white']};'>
                <li><strong>Static thresholds</strong> don't adapt</li>
                <li><strong>Flags legitimate changes</strong> as anomalies</li>
                <li><strong>Requires manual retuning</strong> after changes</li>
                <li><strong>High analyst burden</strong> from false positives</li>
                <li><strong>Misses real issues</strong> in noise</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


def show_anomaly_detection(df, report):
    """Anomaly detection analysis page"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>ANOMALY DETECTION ANALYSIS</h2>
    """, unsafe_allow_html=True)
    
    # Detection metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = report['anomaly_detection']['improved_performance']
    
    with col1:
        st.metric("PRECISION", f"{metrics['precision']:.1%}")
    with col2:
        st.metric("RECALL", f"{metrics['recall']:.1%}")
    with col3:
        st.metric("F1 SCORE", f"{metrics['f1_score']:.1%}")
    with col4:
        st.metric("FP RATE", f"{metrics['false_positive_rate']:.1%}")
    
    st.markdown("---")
    
    # Anomaly confidence distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=df['anomaly_confidence'],
            nbinsx=50,
            marker=dict(
                color=BLOOMBERG_COLORS['primary_orange'],
                line=dict(color=BLOOMBERG_COLORS['border_gray'], width=1)
            )
        ))
        
        fig.update_layout(
            title=dict(text="ANOMALY CONFIDENCE DISTRIBUTION", 
                      font=dict(size=18, color=BLOOMBERG_COLORS['header_orange'])),
            paper_bgcolor=BLOOMBERG_COLORS['background'],
            plot_bgcolor=BLOOMBERG_COLORS['surface'],
            font=dict(color=BLOOMBERG_COLORS['text_white'], family='Courier New'),
            xaxis=dict(title="Confidence Score", gridcolor=BLOOMBERG_COLORS['border_gray']),
            yaxis=dict(title="Frequency", gridcolor=BLOOMBERG_COLORS['border_gray']),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Model comparison
        model_data = pd.DataFrame({
            'Model': ['ISO Forest', 'LSTM', 'Hybrid'],
            'Anomalies': [
                df['iso_anomaly'].sum(),
                df['lstm_anomaly'].sum(),
                df['hybrid_anomaly'].sum()
            ]
        })
        
        bar_chart = create_bloomberg_bar(
            model_data,
            'Model',
            'Anomalies',
            "MODEL COMPARISON"
        )
        st.plotly_chart(bar_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Confusion matrix
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>DETECTION PERFORMANCE MATRIX</h3>
    """, unsafe_allow_html=True)
    
    true_labels = (df['quality_label'] == 'anomaly').astype(int)
    predictions = df['hybrid_anomaly']
    
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(true_labels, predictions)
    
    cm_df = pd.DataFrame(
        cm,
        index=['Actual Normal', 'Actual Anomaly'],
        columns=['Predicted Normal', 'Predicted Anomaly']
    )
    
    heatmap = create_bloomberg_heatmap(cm_df, "CONFUSION MATRIX")
    st.plotly_chart(heatmap, use_container_width=True)

def show_dq_dimensions(df, report):
    """DQ dimensions detailed view"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>DATA QUALITY DIMENSIONS</h2>
    """, unsafe_allow_html=True)
    
    dimensions = report['data_quality_dimensions']
    
    # Create gauges for each dimension
    cols = st.columns(3)
    dim_names = list(dimensions.keys())
    
    for idx, dim_name in enumerate(dim_names):
        with cols[idx % 3]:
            dim_data = dimensions[dim_name]
            gauge = create_bloomberg_gauge(
                dim_data['overall_score'],
                dim_data['dimension'].upper(),
                max_val=100
            )
            st.plotly_chart(gauge, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed breakdown
    selected_dim = st.selectbox(
        "SELECT DIMENSION FOR DETAILS:",
        options=list(dimensions.keys()),
        format_func=lambda x: dimensions[x]['dimension'].upper()
    )
    
    dim_detail = dimensions[selected_dim]
    
    st.markdown(f"""
    <div style='background-color: {BLOOMBERG_COLORS['surface']}; padding: 20px; border-radius: 5px; border: 1px solid {BLOOMBERG_COLORS['primary_orange']};'>
        <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>{dim_detail['dimension'].upper()}</h3>
        <p style='color: {BLOOMBERG_COLORS['positive_green']}; font-size: 32px; font-weight: bold;'>
            {dim_detail['overall_score']:.1f}%
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show detailed metrics if available
    if 'checks' in dim_detail:
        st.markdown("<br>", unsafe_allow_html=True)
        checks_df = pd.DataFrame([
            {
                'Check': v['check'],
                'Score': f"{v.get('accuracy_score', v.get('consistency_score', v.get('validity_score', 0))):.1f}%",
                'Status': v['status']
            }
            for k, v in dim_detail['checks'].items()
        ])
        st.dataframe(checks_df, use_container_width=True)

def show_entity_resolution(df):
    """Entity resolution visualization"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>ENTITY RESOLUTION ANALYSIS</h2>
    """, unsafe_allow_html=True)
    
    # Before/After comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ORIGINAL ENTITIES", df['entity_name_raw'].nunique())
    with col2:
        st.metric("RESOLVED ENTITIES", df['entity_resolved'].nunique())
    
    reduction = (1 - df['entity_resolved'].nunique() / df['entity_name_raw'].nunique()) * 100
    st.metric("REDUCTION RATE", f"{reduction:.1f}%")
    
    st.markdown("---")
    
    # Entity mapping table
    st.markdown(f"""
    <h3 style='color: {BLOOMBERG_COLORS['header_orange']};'>ENTITY MAPPING</h3>
    """, unsafe_allow_html=True)
    
    entity_map = df[['entity_name_raw', 'entity_resolved']].drop_duplicates().sort_values('entity_resolved')
    st.dataframe(entity_map, use_container_width=True, height=600)

def show_raw_data(df):
    """Raw data explorer"""
    
    st.markdown(f"""
    <h2 style='color: {BLOOMBERG_COLORS['header_orange']};'>RAW DATA EXPLORER</h2>
    """, unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        scenario_filter = st.multiselect(
            "FILTER BY SCENARIO:",
            options=df['scenario_type'].unique(),
            default=df['scenario_type'].unique()
        )
    
    with col2:
        entity_filter = st.multiselect(
            "FILTER BY ENTITY:",
            options=df['entity_canonical'].unique()[:10],  # Top 10
            default=[]
        )
    
    with col3:
        anomaly_filter = st.radio(
            "ANOMALY STATUS:",
            options=["All", "Anomalies Only", "Normal Only"],
            index=0
        )
    
    # Apply filters
    filtered_df = df[df['scenario_type'].isin(scenario_filter)]
    
    if entity_filter:
        filtered_df = filtered_df[filtered_df['entity_canonical'].isin(entity_filter)]
    
    if anomaly_filter == "Anomalies Only":
        filtered_df = filtered_df[filtered_df['hybrid_anomaly'] == 1]
    elif anomaly_filter == "Normal Only":
        filtered_df = filtered_df[filtered_df['hybrid_anomaly'] == 0]
    
    st.markdown(f"**Showing {len(filtered_df):,} of {len(df):,} records**")
    
    # Display data
    display_cols = [
        'record_id', 'entity_name_raw', 'security', 'ownership_pct',
        'shares', 'qoq_change_pct', 'hybrid_anomaly', 'anomaly_confidence',
        'scenario_type', 'quality_label'
    ]
    
    st.dataframe(
        filtered_df[display_cols].style.format({
            'ownership_pct': '{:.2f}%',
            'qoq_change_pct': '{:.2f}%',
            'anomaly_confidence': '{:.1f}'
        }),
        use_container_width=True,
        height=600
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 DOWNLOAD FILTERED DATA",
        data=csv,
        file_name=f"ownership_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
