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
    
    def generate_all_visualizations(self, df: pd.DataFrame, dq_profile: Dict):
        """Generate all visualization charts"""
        print("\n📊 Generating visualizations...")
        
        viz_dir = f"{self.output_dir}/visualizations"
        
        # Use data_quality_dimensions instead of dimensions
        profile_for_viz = {
            'dimensions': dq_profile.get('data_quality_dimensions', dq_profile.get('dimensions', {}))
        }
        profile_for_viz.update(dq_profile)
        
        self.create_dimension_radar_chart(profile_for_viz, f"{viz_dir}/dq_dimensions_radar.png")
        self.create_anomaly_distribution(df, f"{viz_dir}/anomaly_distribution.png")
        self.create_time_series_view(df, f"{viz_dir}/ownership_trends.png")
        self.create_entity_resolution_graph(df, f"{viz_dir}/entity_resolution.png")
        self.create_confusion_matrix(df, f"{viz_dir}/confusion_matrix.png")
        
        print(f"✅ All visualizations saved to: {viz_dir}")


if __name__ == "__main__":
    print("Visualization module ready")
