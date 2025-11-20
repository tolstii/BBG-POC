"""
Visualization Module for DQ Assessment
Creates charts and visualizations for the assessment report
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from typing import Dict
import numpy as np


class DQVisualizer:
    """Generate visualizations for DQ assessment"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        
    def create_dimension_radar_chart(self, dq_profile: Dict, save_path: str):
        """Create radar chart for DQ dimensions"""
        dimensions = list(dq_profile['dimensions'].keys())
        scores = [dq_profile['dimensions'][d]['overall_score'] for d in dimensions]
        
        # Create radar chart
        angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
        scores += scores[:1]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, scores, 'o-', linewidth=2, label='Current Score')
        ax.fill(angles, scores, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([d.title() for d in dimensions])
        ax.set_ylim(0, 100)
        ax.set_title('Data Quality Dimensions', size=16, pad=20)
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Radar chart saved: {save_path}")
    
    def create_anomaly_distribution(self, df: pd.DataFrame, save_path: str):
        """Create distribution of anomaly scores"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Subplot 1: Anomaly confidence distribution
        axes[0, 0].hist(df['anomaly_confidence'], bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(df['anomaly_confidence'].median(), color='red', 
                          linestyle='--', label=f'Median: {df["anomaly_confidence"].median():.1f}')
        axes[0, 0].set_xlabel('Anomaly Confidence Score')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Anomaly Confidence Distribution')
        axes[0, 0].legend()
        
        # Subplot 2: Scenario type breakdown
        scenario_counts = df['scenario_type'].value_counts()
        axes[0, 1].bar(range(len(scenario_counts)), scenario_counts.values)
        axes[0, 1].set_xticks(range(len(scenario_counts)))
        axes[0, 1].set_xticklabels([s.replace('_', '\n') for s in scenario_counts.index], 
                                   rotation=0, ha='center')
        axes[0, 1].set_ylabel('Count')
        axes[0, 1].set_title('Scenario Type Distribution')
        
        # Subplot 3: ISO Forest vs LSTM comparison
        anomaly_comparison = pd.DataFrame({
            'ISO Forest': [df['iso_anomaly'].sum(), (~df['iso_anomaly'].astype(bool)).sum()],
            'LSTM': [df['lstm_anomaly'].sum(), (~df['lstm_anomaly'].astype(bool)).sum()],
            'Hybrid': [df['hybrid_anomaly'].sum(), (~df['hybrid_anomaly'].astype(bool)).sum()]
        }, index=['Anomalies', 'Normal'])
        
        anomaly_comparison.plot(kind='bar', ax=axes[1, 0])
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('Model Comparison: Anomaly Detection')
        axes[1, 0].legend(title='Model')
        axes[1, 0].set_xticklabels(axes[1, 0].get_xticklabels(), rotation=0)
        
        # Subplot 4: Ownership percentage by scenario
        df.boxplot(column='ownership_pct', by='scenario_type', ax=axes[1, 1])
        axes[1, 1].set_xlabel('Scenario Type')
        axes[1, 1].set_ylabel('Ownership %')
        axes[1, 1].set_title('Ownership Distribution by Scenario')
        plt.suptitle('')  # Remove default title
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Anomaly distribution saved: {save_path}")
    
    def create_time_series_view(self, df: pd.DataFrame, save_path: str):
        """Create time-series visualization of ownership changes"""
        df_sorted = df.sort_values('filing_date')
        
        # Sample a few entities for clarity
        top_entities = df['entity_canonical'].value_counts().head(3).index
        df_sample = df_sorted[df_sorted['entity_canonical'].isin(top_entities)]
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for entity in top_entities:
            entity_data = df_sample[df_sample['entity_canonical'] == entity]
            ax.plot(entity_data['filing_date'], entity_data['ownership_pct'], 
                   marker='o', label=entity, alpha=0.7)
        
        ax.set_xlabel('Filing Date')
        ax.set_ylabel('Ownership %')
        ax.set_title('Ownership Trends Over Time (Top 3 Entities)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Time series chart saved: {save_path}")
    
    def create_entity_resolution_graph(self, df: pd.DataFrame, save_path: str):
        """Visualize entity resolution effectiveness"""
        resolution_stats = pd.DataFrame({
            'Entity Names': [
                df['entity_name_raw'].nunique(),
                df['entity_resolved'].nunique()
            ]
        }, index=['Before Resolution', 'After Resolution'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.bar(resolution_stats.index, resolution_stats['Entity Names'], 
                     color=['#e74c3c', '#27ae60'])
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=14, fontweight='bold')
        
        reduction_pct = (1 - resolution_stats.loc['After Resolution', 'Entity Names'] / 
                        resolution_stats.loc['Before Resolution', 'Entity Names']) * 100
        
        ax.set_ylabel('Number of Unique Entities', fontsize=12)
        ax.set_title(f'Entity Resolution Impact\n({reduction_pct:.1f}% reduction)', 
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, resolution_stats['Entity Names'].max() * 1.2)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Entity resolution chart saved: {save_path}")
    
    def create_confusion_matrix(self, df: pd.DataFrame, save_path: str):
        """Create confusion matrix for anomaly detection"""
        from sklearn.metrics import confusion_matrix
        
        # True labels vs predictions
        true_labels = (df['quality_label'] == 'anomaly').astype(int)
        predictions = df['hybrid_anomaly']
        
        cm = confusion_matrix(true_labels, predictions)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                   xticklabels=['Normal', 'Anomaly'],
                   yticklabels=['Normal', 'Anomaly'])
        
        ax.set_xlabel('Predicted Label', fontsize=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_title('Confusion Matrix: Anomaly Detection', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Confusion matrix saved: {save_path}")
    
    def create_timeliness_analysis(self, df: pd.DataFrame, save_path: str):
        """Create comprehensive timeliness analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Timeliness Analysis', fontsize=16, fontweight='bold')
        
        # Check required columns
        has_delay = 'filing_delay_days' in df.columns
        has_report_date = 'report_date' in df.columns
        has_holder_type = 'holder_type' in df.columns
        
        # 1. Filing delay distribution
        ax1 = axes[0, 0]
        if has_delay:
            df['filing_delay_days'].hist(bins=60, ax=ax1, color='teal', alpha=0.7, edgecolor='black')
            ax1.axvline(45, color='red', linestyle='--', linewidth=2, label='Regulatory Threshold (45 days)')
            ax1.set_xlabel('Filing Delay (Days)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Filing Delay Distribution\n(Report date to Filing date)')
            ax1.legend()
        else:
            ax1.text(0.5, 0.5, 'Filing delay data not available\n(POC uses simplified schema)', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('Filing Delay Distribution')
            ax1.axis('off')
        
        # 2. Filing volume over time
        ax2 = axes[0, 1]
        if has_report_date:
            quarterly_counts = df.groupby(df['report_date'].dt.to_period('Q')).size()
            quarterly_counts.plot(kind='line', ax=ax2, marker='o', color='darkblue', linewidth=2)
            ax2.set_xlabel('Quarter')
            ax2.set_ylabel('Number of Filings')
            ax2.set_title('Filing Volume Over Time\n(Quarterly Trend)')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        elif 'filing_date' in df.columns:
            # Use filing_date as proxy
            quarterly_counts = df.groupby(pd.to_datetime(df['filing_date']).dt.to_period('Q')).size()
            quarterly_counts.plot(kind='line', ax=ax2, marker='o', color='darkblue', linewidth=2)
            ax2.set_xlabel('Quarter')
            ax2.set_ylabel('Number of Records')
            ax2.set_title('Data Volume Over Time\n(Quarterly Trend)')
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax2.text(0.5, 0.5, 'Temporal data not available', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Filing Volume Over Time')
            ax2.axis('off')
        
        # 3. Filing timeliness by holder type
        ax3 = axes[1, 0]
        if has_delay and has_holder_type:
            holder_delays = df.groupby('holder_type')['filing_delay_days'].mean().sort_values()
            holder_delays.plot(kind='barh', ax=ax3, color='skyblue', edgecolor='black')
            ax3.axvline(45, color='red', linestyle='--', alpha=0.7, label='45-day threshold')
            ax3.set_xlabel('Average Filing Delay (Days)')
            ax3.set_title('Filing Timeliness by Holder Type')
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, 'Holder type timeliness not available\n(POC uses simplified schema)', 
                    ha='center', va='center', transform=ax3.transAxes, fontsize=12)
            ax3.set_title('Filing Timeliness by Holder Type')
            ax3.axis('off')
        
        # 4. Data growth over time
        ax4 = axes[1, 1]
        if has_report_date:
            df_sorted = df.sort_values('report_date')
            df_sorted['cumulative_records'] = range(1, len(df_sorted) + 1)
            ax4.plot(df_sorted['report_date'], df_sorted['cumulative_records'], 
                    color='green', linewidth=2)
            ax4.set_xlabel('Report Date')
            ax4.set_ylabel('Cumulative Records')
            ax4.set_title('Data Growth Over Time')
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        elif 'filing_date' in df.columns:
            df_sorted = df.sort_values('filing_date')
            df_sorted['cumulative_records'] = range(1, len(df_sorted) + 1)
            ax4.plot(pd.to_datetime(df_sorted['filing_date']), df_sorted['cumulative_records'], 
                    color='green', linewidth=2)
            ax4.set_xlabel('Filing Date')
            ax4.set_ylabel('Cumulative Records')
            ax4.set_title('Data Growth Over Time')
            ax4.grid(True, alpha=0.3)
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax4.text(0.5, 0.5, 'Temporal data not available', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Data Growth Over Time')
            ax4.axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Timeliness analysis saved: {save_path}")
    
    def create_entity_analysis(self, df: pd.DataFrame, save_path: str):
        """Create entity distribution and holder analysis"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Entity Analysis', fontsize=16, fontweight='bold')
        
        # Check required columns
        has_holder = 'holder_name' in df.columns
        has_holder_type = 'holder_type' in df.columns
        has_ownership = 'ownership_pct' in df.columns
        
        # Use fallback columns if needed
        holder_col = 'holder_name' if has_holder else ('entity_resolved' if 'entity_resolved' in df.columns else 'entity_canonical')
        type_col = 'holder_type' if has_holder_type else 'filing_type'
        
        # 1. Top holders by total ownership
        ax1 = axes[0]
        if has_ownership:
            top_holders = df.groupby(holder_col)['ownership_pct'].sum().nlargest(15)
            top_holders.plot(kind='barh', ax=ax1, color='steelblue', edgecolor='black')
            ax1.set_xlabel('Total Ownership %')
            ax1.set_title('Top 15 Holders by Aggregate Ownership')
            ax1.invert_yaxis()
        else:
            # Just show count
            top_holders = df[holder_col].value_counts().head(15)
            top_holders.plot(kind='barh', ax=ax1, color='steelblue', edgecolor='black')
            ax1.set_xlabel('Position Count')
            ax1.set_title('Top 15 Most Active Entities')
            ax1.invert_yaxis()
        
        # 2. Holder type distribution
        ax2 = axes[1]
        if type_col in df.columns:
            holder_type_dist = df[type_col].value_counts()
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
            ax2.pie(holder_type_dist.values, labels=holder_type_dist.index, autopct='%1.1f%%',
                   startangle=90, colors=colors[:len(holder_type_dist)], textprops={'fontsize': 10})
            title = 'Distribution by Holder Type' if has_holder_type else 'Distribution by Filing Type'
            ax2.set_title(title)
        else:
            ax2.text(0.5, 0.5, 'Type distribution not available', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Holder Type Distribution')
            ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Entity analysis saved: {save_path}")
    
    def create_trend_analysis(self, df: pd.DataFrame, save_path: str):
        """Create comprehensive ownership trend analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Ownership Trend Analysis', fontsize=16, fontweight='bold')
        
        # Check required columns
        has_report_date = 'report_date' in df.columns
        has_holder_type = 'holder_type' in df.columns
        has_ownership = 'ownership_pct' in df.columns
        has_market_value = 'market_value' in df.columns
        has_security_name = 'security_name' in df.columns
        has_ownership_change = 'ownership_change' in df.columns
        
        # Use fallbacks
        date_col = 'report_date' if has_report_date else 'filing_date'
        security_col = 'security_name' if has_security_name else 'security'
        
        # 1. Ownership concentration over time
        ax1 = axes[0, 0]
        if has_ownership and date_col in df.columns:
            quarterly_avg = df.groupby(pd.to_datetime(df[date_col]).dt.to_period('Q'))['ownership_pct'].agg(['mean', 'median'])
            quarterly_avg['mean'].plot(ax=ax1, marker='o', label='Mean', linewidth=2)
            quarterly_avg['median'].plot(ax=ax1, marker='s', label='Median', linewidth=2)
            ax1.set_xlabel('Quarter')
            ax1.set_ylabel('Ownership %')
            ax1.set_title('Average Ownership Percentage Trends')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax1.text(0.5, 0.5, 'Temporal ownership data not available\n(POC uses simplified schema)', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('Ownership Percentage Trends')
            ax1.axis('off')
        
        # 2. Market value trends by holder type
        ax2 = axes[0, 1]
        if has_market_value and has_holder_type and date_col in df.columns:
            for holder_type in df['holder_type'].unique():
                holder_df = df[df['holder_type'] == holder_type]
                quarterly_value = holder_df.groupby(pd.to_datetime(holder_df[date_col]).dt.to_period('Q'))['market_value'].sum()
                quarterly_value.plot(ax=ax2, marker='o', label=holder_type, linewidth=2)
            ax2.set_xlabel('Quarter')
            ax2.set_ylabel('Total Market Value')
            ax2.set_title('Market Value by Holder Type')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax2.text(0.5, 0.5, 'Market value trends not available\n(POC uses simplified schema)', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Market Value by Holder Type')
            ax2.axis('off')
        
        # 3. Security concentration
        ax3 = axes[1, 0]
        if has_market_value:
            top_securities = df.groupby(security_col)['market_value'].sum().nlargest(10)
            top_securities.plot(kind='barh', ax=ax3, color='coral', edgecolor='black')
            ax3.set_xlabel('Total Market Value')
            ax3.set_title('Top 10 Securities by Market Value')
            ax3.invert_yaxis()
        else:
            # Just show count
            top_securities = df[security_col].value_counts().head(10)
            top_securities.plot(kind='barh', ax=ax3, color='coral', edgecolor='black')
            ax3.set_xlabel('Position Count')
            ax3.set_title('Top 10 Most Held Securities')
            ax3.invert_yaxis()
        
        # 4. Ownership change volatility
        ax4 = axes[1, 1]
        if has_ownership_change:
            change_volatility = df.groupby(security_col)['ownership_change'].std().nlargest(10)
            change_volatility.plot(kind='barh', ax=ax4, color='purple', edgecolor='black')
            ax4.set_xlabel('Std Dev of Ownership Change')
            ax4.set_title('Top 10 Most Volatile Securities')
            ax4.invert_yaxis()
        elif 'qoq_change_pct' in df.columns:
            # Use QoQ change as proxy
            change_volatility = df.groupby(security_col)['qoq_change_pct'].std().nlargest(10)
            change_volatility.plot(kind='barh', ax=ax4, color='purple', edgecolor='black')
            ax4.set_xlabel('Std Dev of QoQ Change %')
            ax4.set_title('Top 10 Most Volatile Securities')
            ax4.invert_yaxis()
        else:
            ax4.text(0.5, 0.5, 'Volatility data not available\n(POC uses simplified schema)', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Most Volatile Securities')
            ax4.axis('off')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Trend analysis saved: {save_path}")
    
    
    def generate_all_visualizations(self, df: pd.DataFrame, dq_profile: Dict):
        """Generate all visualization charts"""
        print("\n📊 Generating visualizations...")
        
        # Use output_dir directly (already points to visualizations/)
        viz_dir = self.output_dir
        
        # Use data_quality_dimensions instead of dimensions
        profile_for_viz = {
            'dimensions': dq_profile.get('data_quality_dimensions', dq_profile.get('dimensions', {}))
        }
        profile_for_viz.update(dq_profile)
        
        # Original visualizations
        self.create_dimension_radar_chart(profile_for_viz, f"{viz_dir}/dq_dimensions_radar.png")
        self.create_anomaly_distribution(df, f"{viz_dir}/anomaly_distribution.png")
        self.create_time_series_view(df, f"{viz_dir}/ownership_trends.png")
        self.create_entity_resolution_graph(df, f"{viz_dir}/entity_resolution.png")
        self.create_confusion_matrix(df, f"{viz_dir}/confusion_matrix.png")
        
        # New business intelligence visualizations
        self.create_timeliness_analysis(df, f"{viz_dir}/timeliness_analysis.png")
        self.create_entity_analysis(df, f"{viz_dir}/entity_analysis.png")
        self.create_trend_analysis(df, f"{viz_dir}/trend_analysis.png")
        
        print(f"✅ All visualizations saved to: {viz_dir}")


if __name__ == "__main__":
    print("Visualization module ready")
