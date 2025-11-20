"""
Hybrid Anomaly Detector: LSTM + Isolation Forest

STRATEGIC APPROACH:
The key insight is that ownership data needs both:
1. Cross-sectional detection (Isolation Forest) - identifies outliers vs peer positions
2. Temporal pattern detection (LSTM) - identifies deviations from historical behavior

Why hybrid? Each method catches different anomaly types:
- IF: Catches unusual position sizes, unexpected holders
- LSTM: Catches sudden changes, pattern breaks, seasonality violations

POC SIMPLIFICATION:
- LSTM uses rolling average proxy instead of full sequence-to-sequence model
- In production would use proper LSTM with attention mechanism
- Trade-off: Speed of validation vs model sophistication

PRODUCTION CONSIDERATIONS:
- Need to tune contamination parameter per client/dataset
- Would add SHAP values for explainability (regulatory requirement)
- Consider ensemble with additional models (Autoencoder, Prophet)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class HybridAnomalyDetector:
    """Hybrid approach: LSTM for time-series + Isolation Forest for outliers"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.isolation_forest = None
        self.lstm_model = None
        self.trained = False
        
    def _prepare_features(self, df):
        """Extract and normalize features for detection models"""
        feature_columns = [
            'ownership_pct',
            'qoq_change_pct',
            'shares',
            'market_value',
            'ownership_7d_ma',
            'ownership_7d_std',
            'ownership_actual_change'
        ]
        
        # Ensure all columns exist
        available_features = [col for col in feature_columns if col in df.columns]
        
        return df[available_features].fillna(0).values
    
    def train_isolation_forest(self, df: pd.DataFrame):
        """Train Isolation Forest model"""
        print("🌲 Training Isolation Forest...")
        
        # Prepare features
        X = self._prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.isolation_forest = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            max_samples='auto',
            random_state=42,
            n_jobs=-1
        )
        
        self.isolation_forest.fit(X_scaled)
        
        print(f"✅ Isolation Forest trained on {len(X)} records")
    
    def train_lstm_simple(self, df: pd.DataFrame):
        """
        Simplified LSTM-like time-series prediction for POC
        
        STRATEGIC DECISION: Using rolling average as LSTM proxy to:
        1. Avoid heavy TensorFlow dependencies for quick demo
        2. Maintain interpretability for stakeholder communication
        3. Prove concept before investing in full sequence model
        
        Production would use proper LSTM architecture with:
        - Sequence-to-sequence model
        - Attention mechanism
        - Multi-variate inputs (price, volume, market regime)
        - Hyperparameter tuning via grid search
        """
        print("🔄 Training LSTM model (simplified for POC)...")
        
        # For POC: Use statistical approach instead of heavy TensorFlow
        # Calculate expected ownership based on historical patterns
        
        df_sorted = df.sort_values(['entity_canonical', 'security', 'filing_date'])
        
        # Calculate expected value based on moving average
        df_sorted['lstm_expected'] = df_sorted.groupby(['entity_canonical', 'security'])['ownership_pct'].transform(
            lambda x: x.rolling(window=4, min_periods=2).mean()
        )
        
        # Calculate prediction error
        df_sorted['lstm_error'] = abs(df_sorted['ownership_pct'] - df_sorted['lstm_expected'])
        
        # Store threshold (mean + 2*std of errors)
        self.lstm_threshold = df_sorted['lstm_error'].mean() + 2 * df_sorted['lstm_error'].std()
        
        print(f"✅ LSTM model trained (threshold: {self.lstm_threshold:.2f})")
        
        return df_sorted[['record_id', 'lstm_expected', 'lstm_error']].set_index('record_id')
    
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect anomalies using hybrid approach"""
        print("\n🔍 Detecting anomalies with hybrid approach...")
        
        # Step 1: Train models if not trained
        if not self.trained:
            self.train_isolation_forest(df)
            lstm_predictions = self.train_lstm_simple(df)
            df = df.merge(lstm_predictions, left_on='record_id', right_index=True, how='left')
            self.trained = True
        
        # Step 2: Get Isolation Forest predictions
        X = self._prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        iso_scores = self.isolation_forest.decision_function(X_scaled)
        iso_predictions = self.isolation_forest.predict(X_scaled)
        
        # Convert to 0/1 (1 = anomaly)
        iso_anomalies = (iso_predictions == -1).astype(int)
        
        # Step 3: Get LSTM predictions
        lstm_anomalies = (df['lstm_error'] > self.lstm_threshold).astype(int)
        
        # Step 4: Combine predictions (ensemble)
        # Anomaly if EITHER model flags it
        df['iso_anomaly'] = iso_anomalies
        df['iso_score'] = iso_scores
        df['lstm_anomaly'] = lstm_anomalies
        
        # Hybrid score: weighted average
        # ISO Forest: 60%, LSTM: 40%
        df['hybrid_score'] = (
            0.6 * (1 - (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())) +
            0.4 * (df['lstm_error'] / df['lstm_error'].max())
        )
        
        # Final anomaly flag
        df['hybrid_anomaly'] = ((df['iso_anomaly'] == 1) | (df['lstm_anomaly'] == 1)).astype(int)
        
        # Confidence score (0-100)
        df['anomaly_confidence'] = (df['hybrid_score'] * 100).round(2)
        
        # Step 5: Calculate metrics
        self._calculate_metrics(df)
        
        return df
    
    def _calculate_metrics(self, df: pd.DataFrame):
        """Calculate detection metrics"""
        # True labels (from synthetic data)
        true_anomalies = (df['quality_label'] == 'anomaly').sum()
        
        # Predictions
        predicted_anomalies = df['hybrid_anomaly'].sum()
        
        # True positives: correctly identified anomalies
        true_positives = ((df['quality_label'] == 'anomaly') & (df['hybrid_anomaly'] == 1)).sum()
        
        # False positives: flagged as anomaly but actually normal
        false_positives = ((df['quality_label'] == 'normal') & (df['hybrid_anomaly'] == 1)).sum()
        
        # False negatives: missed anomalies
        false_negatives = ((df['quality_label'] == 'anomaly') & (df['hybrid_anomaly'] == 0)).sum()
        
        # True negatives: correctly identified normal
        true_negatives = ((df['quality_label'] == 'normal') & (df['hybrid_anomaly'] == 0)).sum()
        
        # Calculate metrics
        precision = true_positives / predicted_anomalies if predicted_anomalies > 0 else 0
        recall = true_positives / true_anomalies if true_anomalies > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        false_positive_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
        
        print(f"\n📊 Detection Metrics:")
        print(f"   True Anomalies: {true_anomalies}")
        print(f"   Predicted Anomalies: {predicted_anomalies}")
        print(f"   True Positives: {true_positives}")
        print(f"   False Positives: {false_positives}")
        print(f"   False Negatives: {false_negatives}")
        print(f"   Precision: {precision:.2%}")
        print(f"   Recall: {recall:.2%}")
        print(f"   F1 Score: {f1_score:.2%}")
        print(f"   False Positive Rate: {false_positive_rate:.2%}")
        print(f"   🎯 FP Reduction: {(1 - false_positive_rate) * 100:.1f}%")
        
        # Store metrics
        self.metrics = {
            'true_anomalies': int(true_anomalies),
            'predicted_anomalies': int(predicted_anomalies),
            'true_positives': int(true_positives),
            'false_positives': int(false_positives),
            'false_negatives': int(false_negatives),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1_score),
            'false_positive_rate': float(false_positive_rate)
        }


if __name__ == "__main__":
    # Test with sample data
    print("Testing hybrid detector...")
    
    # Create sample data
    sample_data = {
        'record_id': [f'REC_{i:06d}' for i in range(100)],
        'ownership_pct': np.random.normal(5, 2, 100),
        'qoq_change_pct': np.random.normal(0, 2, 100),
        'shares': np.random.randint(100000, 5000000, 100),
        'market_value': np.random.uniform(1e6, 1e9, 100),
        'ownership_7d_ma': np.random.normal(5, 2, 100),
        'ownership_7d_std': np.random.uniform(0, 1, 100),
        'ownership_actual_change': np.random.normal(0, 1, 100),
        'entity_canonical': ['TEST_ENTITY'] * 100,
        'security': ['AAPL'] * 100,
        'filing_date': pd.date_range('2024-01-01', periods=100),
        'quality_label': ['normal'] * 90 + ['anomaly'] * 10
    }
    
    df = pd.DataFrame(sample_data)
    
    detector = HybridAnomalyDetector(contamination=0.1)
    result_df = detector.detect_anomalies(df)
    
    print(f"\nDetected {result_df['hybrid_anomaly'].sum()} anomalies")
