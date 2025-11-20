"""
Detection Methods for Comparison Analysis
Implements Z-Score, IQR, Moving Average, LSTM, Isolation Forest
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class TraditionalDetectors:
    """Traditional statistical anomaly detection methods"""
    
    @staticmethod
    def z_score_detection(series, threshold=3):
        """Detect anomalies using Z-score method"""
        mean = series.mean()
        std = series.std()
        z_scores = np.abs((series - mean) / std)
        anomalies = z_scores > threshold
        return anomalies, z_scores
    
    @staticmethod
    def iqr_detection(series, multiplier=1.5):
        """Detect anomalies using IQR method"""
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        anomalies = (series < lower_bound) | (series > upper_bound)
        return anomalies, lower_bound, upper_bound
    
    @staticmethod
    def moving_average_detection(series, window=5, threshold=2):
        """Detect anomalies using moving average method"""
        ma = series.rolling(window=window, min_periods=1).mean()
        ma_std = series.rolling(window=window, min_periods=1).std()
        
        # Calculate deviation from moving average
        deviation = np.abs(series - ma)
        threshold_band = threshold * ma_std
        
        anomalies = deviation > threshold_band
        return anomalies, ma, threshold_band


class MLDetectors:
    """Machine learning-based anomaly detection methods"""
    
    def __init__(self):
        self.iso_forest = None
        self.scaler = StandardScaler()
        self.lstm_threshold = None
    
    def isolation_forest_detection(self, data, contamination=0.1):
        """Detect anomalies using Isolation Forest"""
        # Prepare features
        features = data[['ownership_pct', 'qoq_change_pct', 'shares', 'market_value']].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Fit Isolation Forest
        self.iso_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        
        predictions = self.iso_forest.fit_predict(X_scaled)
        scores = self.iso_forest.decision_function(X_scaled)
        
        # Convert to boolean (1 = anomaly, -1 = normal -> True/False)
        anomalies = predictions == -1
        
        return anomalies, scores
    
    def lstm_detection(self, series, window=4):
        """Simplified LSTM-like detection using rolling statistics"""
        # Calculate expected value based on historical patterns
        expected = series.rolling(window=window, min_periods=2).mean()
        
        # Calculate prediction error
        error = np.abs(series - expected)
        
        # Set threshold (mean + 2*std of errors)
        threshold = error.mean() + 2 * error.std()
        self.lstm_threshold = threshold
        
        anomalies = error > threshold
        
        return anomalies, error, threshold


def compare_all_methods(df, entity, security):
    """
    Compare all detection methods on a specific entity-security pair
    Returns results for visualization
    """
    # Filter data for specific entity-security
    mask = (df['entity_canonical'] == entity) & (df['security'] == security)
    data = df[mask].sort_values('filing_date').copy()
    
    if len(data) < 10:
        return None  # Not enough data points
    
    series = data['ownership_pct']
    
    # Initialize detectors
    trad = TraditionalDetectors()
    ml = MLDetectors()
    
    # Traditional methods
    z_anomalies, z_scores = trad.z_score_detection(series)
    iqr_anomalies, iqr_lower, iqr_upper = trad.iqr_detection(series)
    ma_anomalies, ma, ma_threshold = trad.moving_average_detection(series)
    
    # ML methods
    iso_anomalies, iso_scores = ml.isolation_forest_detection(data)
    lstm_anomalies, lstm_error, lstm_threshold = ml.lstm_detection(series)
    
    # Combine results
    results = {
        'data': data,
        'series': series,
        'traditional': {
            'z_score': {
                'anomalies': z_anomalies.values,
                'scores': z_scores.values,
                'method': 'Z-Score (±3σ)'
            },
            'iqr': {
                'anomalies': iqr_anomalies.values,
                'lower': iqr_lower,
                'upper': iqr_upper,
                'method': 'IQR (1.5×IQR)'
            },
            'moving_avg': {
                'anomalies': ma_anomalies.values,
                'ma': ma.values,
                'threshold': ma_threshold.values,
                'method': 'Moving Avg (±2σ)'
            }
        },
        'ml': {
            'isolation_forest': {
                'anomalies': iso_anomalies,
                'scores': iso_scores,
                'method': 'Isolation Forest'
            },
            'lstm': {
                'anomalies': lstm_anomalies.values,
                'error': lstm_error.values,
                'threshold': lstm_threshold,
                'method': 'LSTM (Simplified)'
            }
        },
        'hybrid': {
            'anomalies': data['hybrid_anomaly'].values,
            'confidence': data['anomaly_confidence'].values,
            'method': 'Hybrid Ensemble'
        },
        'ground_truth': {
            'anomalies': (data['quality_label'] == 'anomaly').values,
            'labels': data['quality_label'].values
        }
    }
    
    return results


def calculate_method_metrics(anomalies, ground_truth):
    """Calculate precision, recall, F1 for a detection method"""
    true_positives = np.sum(anomalies & ground_truth)
    false_positives = np.sum(anomalies & ~ground_truth)
    false_negatives = np.sum(~anomalies & ground_truth)
    true_negatives = np.sum(~anomalies & ~ground_truth)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    fp_rate = false_positives / (false_positives + true_negatives) if (false_positives + true_negatives) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'fp_rate': fp_rate,
        'true_positives': int(true_positives),
        'false_positives': int(false_positives),
        'false_negatives': int(false_negatives),
        'true_negatives': int(true_negatives)
    }
