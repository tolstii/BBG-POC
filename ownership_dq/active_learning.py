"""
Active Learning Feedback Loop

STRATEGIC PURPOSE:
The core challenge in data quality is balancing automation with human expertise.
Pure ML solutions often fail because:
1. Models can't understand business context (is this change due to rebalancing or error?)
2. Data stewards lose trust if they can't influence the system
3. Edge cases require human judgment

ACTIVE LEARNING SOLVES THIS:
- Presents uncertain predictions to data stewards for review
- Incorporates feedback to improve model over time
- Builds trust by showing the system "learns" from corrections
- Focuses human effort on high-value, high-uncertainty cases

POC LIMITATION:
Currently simulates feedback with ground truth labels. Production would:
- Build web UI for data steward review workflow
- Track feedback metrics (time to review, agreement rate)
- Integrate with case management system
- Add approval workflow for model retraining

PRODUCTION CONSIDERATIONS:
- Need incentive structure for data stewards to provide feedback
- Track and report model improvement to build organizational trust
- Consider feedback quality scoring (some stewards more reliable than others)
- Add audit trail for regulatory compliance
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import json
from datetime import datetime


class ActiveLearningLoop:
    """Active learning system with human feedback"""
    
    def __init__(self):
        self.feedback_history = []
        self.model_versions = []
        self.current_version = 1
        
    def identify_uncertain_predictions(self, df, threshold=0.6):
        """Identify records with uncertain predictions for human review"""
        print("\n🤔 Identifying uncertain predictions...")
        
        # Records where confidence is between 40-60% (most uncertain)
        uncertain = df[
            (df['anomaly_confidence'] >= (threshold - 0.2) * 100) & 
            (df['anomaly_confidence'] <= (threshold + 0.2) * 100)
        ].copy()
        
        # Prioritize by business impact (high market value)
        uncertain['review_priority'] = (
            uncertain['market_value'] / uncertain['market_value'].max() * 100
        )
        
        uncertain = uncertain.sort_values('review_priority', ascending=False)
        
        print(f"   Found {len(uncertain)} uncertain predictions")
        print(f"   Confidence range: {uncertain['anomaly_confidence'].min():.1f}% - {uncertain['anomaly_confidence'].max():.1f}%")
        
        return uncertain
    
    def collect_feedback(self, record: pd.Series, human_label: str, comments: str = "") -> Dict:
        """Collect human feedback on a prediction"""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'record_id': record['record_id'],
            'entity': record.get('entity_name_raw', 'Unknown'),
            'security': record.get('security', 'Unknown'),
            'model_prediction': int(record['hybrid_anomaly']),
            'model_confidence': float(record['anomaly_confidence']),
            'human_label': human_label,  # 'anomaly' or 'normal'
            'agreement': (
                (record['hybrid_anomaly'] == 1 and human_label == 'anomaly') or
                (record['hybrid_anomaly'] == 0 and human_label == 'normal')
            ),
            'comments': comments,
            'model_version': self.current_version
        }
        
        self.feedback_history.append(feedback)
        return feedback
    
    def simulate_feedback(self, df: pd.DataFrame, n_samples: int = 50) -> pd.DataFrame:
        """Simulate human feedback for POC (using true labels)"""
        print(f"\n💭 Simulating human feedback on {n_samples} samples...")
        
        # Get uncertain predictions
        uncertain = self.identify_uncertain_predictions(df)
        
        # Sample for feedback
        feedback_sample = uncertain.head(n_samples) if len(uncertain) >= n_samples else uncertain
        
        feedback_results = []
        
        for idx, record in feedback_sample.iterrows():
            # Use true label as simulated human feedback
            human_label = record['quality_label']
            
            # Simulate comments for disagreements
            if record['hybrid_anomaly'] == 1 and human_label == 'normal':
                comments = "False positive - legitimate business event"
            elif record['hybrid_anomaly'] == 0 and human_label == 'anomaly':
                comments = "Missed anomaly - subtle data quality issue"
            else:
                comments = "Correct prediction"
            
            feedback = self.collect_feedback(record, human_label, comments)
            feedback_results.append(feedback)
        
        feedback_df = pd.DataFrame(feedback_results)
        
        # Calculate agreement rate
        agreement_rate = feedback_df['agreement'].mean()
        
        print(f"   Agreement rate: {agreement_rate:.1%}")
        print(f"   Disagreements: {(~feedback_df['agreement']).sum()}")
        
        return feedback_df
    
    def retrain_with_feedback(self, df: pd.DataFrame, feedback_df: pd.DataFrame) -> pd.DataFrame:
        """Retrain model incorporating human feedback"""
        print("\n🔄 Retraining with human feedback...")
        
        # Create labeled training set from feedback
        feedback_labeled = feedback_df[['record_id', 'human_label']].copy()
        feedback_labeled['human_label_binary'] = (feedback_labeled['human_label'] == 'anomaly').astype(int)
        
        # Merge with main dataset
        df_updated = df.merge(
            feedback_labeled[['record_id', 'human_label_binary']],
            on='record_id',
            how='left'
        )
        
        # Update quality labels where we have feedback
        df_updated['quality_label_updated'] = df_updated.apply(
            lambda row: 'anomaly' if pd.notna(row.get('human_label_binary')) and row['human_label_binary'] == 1
                       else 'normal' if pd.notna(row.get('human_label_binary')) and row['human_label_binary'] == 0
                       else row['quality_label'],
            axis=1
        )
        
        # Recalculate weights for misclassified examples
        # Give higher importance to records where we were wrong
        df_updated['sample_weight'] = 1.0
        df_updated.loc[
            (df_updated['hybrid_anomaly'] != df_updated.get('human_label_binary', df_updated['hybrid_anomaly'])),
            'sample_weight'
        ] = 2.0  # Double weight for mistakes
        
        self.current_version += 1
        
        print(f"✅ Model retrained (version {self.current_version})")
        print(f"   Weighted {(df_updated['sample_weight'] > 1.0).sum()} examples for correction")
        
        return df_updated
    
    def calculate_improvement(self, before_metrics: Dict, after_metrics: Dict) -> Dict:
        """Calculate improvement after incorporating feedback"""
        improvements = {}
        
        for metric in ['precision', 'recall', 'f1_score', 'false_positive_rate']:
            before_val = before_metrics.get(metric, 0)
            after_val = after_metrics.get(metric, 0)
            
            if metric == 'false_positive_rate':
                # Lower is better for FPR
                improvement = (before_val - after_val) / before_val * 100 if before_val > 0 else 0
            else:
                # Higher is better for other metrics
                improvement = (after_val - before_val) / before_val * 100 if before_val > 0 else 0
            
            improvements[metric] = improvement
        
        return improvements
    
    def generate_feedback_report(self) -> pd.DataFrame:
        """Generate report on feedback collected"""
        if not self.feedback_history:
            return pd.DataFrame()
        
        df_feedback = pd.DataFrame(self.feedback_history)
        
        # Summary statistics
        summary = {
            'total_feedback': len(df_feedback),
            'agreement_rate': df_feedback['agreement'].mean(),
            'false_positives_corrected': ((df_feedback['model_prediction'] == 1) & 
                                          (df_feedback['human_label'] == 'normal')).sum(),
            'false_negatives_corrected': ((df_feedback['model_prediction'] == 0) & 
                                          (df_feedback['human_label'] == 'anomaly')).sum(),
            'avg_confidence': df_feedback['model_confidence'].mean()
        }
        
        return df_feedback, summary
    
    def save_feedback(self, filepath: str):
        """Save feedback history to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_history, f, indent=2)
        print(f"💾 Feedback saved to: {filepath}")


if __name__ == "__main__":
    # Test
    print("Testing active learning...")
    
    # Create sample data
    sample_data = {
        'record_id': [f'REC_{i:06d}' for i in range(100)],
        'entity_name_raw': ['Entity A'] * 100,
        'security': ['AAPL'] * 100,
        'hybrid_anomaly': np.random.binomial(1, 0.2, 100),
        'anomaly_confidence': np.random.uniform(30, 70, 100),
        'market_value': np.random.uniform(1e6, 1e9, 100),
        'quality_label': np.random.choice(['normal', 'anomaly'], 100, p=[0.85, 0.15])
    }
    
    df = pd.DataFrame(sample_data)
    
    al = ActiveLearningLoop()
    feedback_df = al.simulate_feedback(df, n_samples=20)
    
    print(f"\nCollected feedback on {len(feedback_df)} records")
    print(feedback_df[['record_id', 'model_prediction', 'human_label', 'agreement']].head())
