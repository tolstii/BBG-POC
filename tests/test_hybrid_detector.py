"""
Unit tests for Hybrid Anomaly Detector

This demonstrates testing approach for the ownership DQ POC.
Run with: pytest tests/test_hybrid_detector.py
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ownership_dq.hybrid_detector import HybridAnomalyDetector


class TestHybridAnomalyDetector:
    """Test suite for HybridAnomalyDetector"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample ownership data for testing"""
        np.random.seed(42)
        
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        filers = ['Filer_A', 'Filer_B', 'Filer_C'] * 34  # 102 records, take first 100
        issuers = ['Company_X', 'Company_Y', 'Company_Z'] * 34
        
        df = pd.DataFrame({
            'filing_date': dates,
            'filer_name': filers[:100],
            'issuer_name': issuers[:100],
            'shares': np.random.lognormal(10, 2, 100),
            'market_value': np.random.lognormal(15, 2, 100),
            'percent_portfolio': np.random.uniform(0.1, 5.0, 100),
            'label': ['normal'] * 95 + ['anomaly'] * 5  # 5% anomalies
        })
        
        return df
    
    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return HybridAnomalyDetector()
    
    def test_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert hasattr(detector, 'contamination')
        assert 0 < detector.contamination < 1
    
    def test_detect_with_valid_data(self, detector, sample_data):
        """Test detection runs successfully with valid data"""
        result = detector.detect(sample_data)
        
        # Check result structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_data)
        assert 'anomaly_score' in result.columns
        assert 'is_anomaly' in result.columns
        
    def test_anomaly_scores_range(self, detector, sample_data):
        """Test anomaly scores are in valid range"""
        result = detector.detect(sample_data)
        
        # Scores should be between -1 and 1 for Isolation Forest
        assert result['anomaly_score'].min() >= -1
        assert result['anomaly_score'].max() <= 1
        
    def test_anomaly_detection_logic(self, detector, sample_data):
        """Test that anomalies are correctly flagged"""
        result = detector.detect(sample_data)
        
        # Should detect some anomalies
        num_anomalies = result['is_anomaly'].sum()
        assert num_anomalies > 0
        assert num_anomalies < len(result)  # Not everything is anomaly
        
    def test_empty_dataframe(self, detector):
        """Test handling of empty dataframe"""
        empty_df = pd.DataFrame()
        
        with pytest.raises((ValueError, KeyError)):
            detector.detect(empty_df)
            
    def test_missing_required_columns(self, detector):
        """Test handling of missing required columns"""
        invalid_df = pd.DataFrame({
            'filing_date': pd.date_range('2023-01-01', periods=10),
            'shares': np.random.rand(10)
            # Missing other required columns
        })
        
        with pytest.raises((KeyError, ValueError)):
            detector.detect(invalid_df)
            
    def test_reproducibility(self, detector, sample_data):
        """Test that detection is reproducible"""
        result1 = detector.detect(sample_data.copy())
        result2 = detector.detect(sample_data.copy())
        
        # Results should be identical (if random seed is set)
        pd.testing.assert_frame_equal(
            result1[['is_anomaly']], 
            result2[['is_anomaly']]
        )
    
    def test_extreme_values(self, detector):
        """Test handling of extreme values"""
        extreme_df = pd.DataFrame({
            'filing_date': pd.date_range('2023-01-01', periods=10),
            'filer_name': ['Filer_A'] * 10,
            'issuer_name': ['Company_X'] * 10,
            'shares': [1, 2, 3, 4, 5, 1000000, 7, 8, 9, 10],  # One extreme value
            'market_value': [100] * 10,
            'percent_portfolio': [1.0] * 10,
            'label': ['normal'] * 10
        })
        
        result = detector.detect(extreme_df)
        
        # Extreme value should be flagged
        assert result.loc[5, 'is_anomaly'] == True
        

class TestDetectorMetrics:
    """Test metric calculation"""
    
    def test_precision_calculation(self):
        """Test precision metric calculation"""
        predictions = pd.Series([True, True, False, False, True])
        actual = pd.Series([True, False, False, True, True])
        
        # True Positives: 2, False Positives: 1
        # Precision = TP / (TP + FP) = 2 / 3 = 0.667
        tp = ((predictions == True) & (actual == True)).sum()
        fp = ((predictions == True) & (actual == False)).sum()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        assert 0.6 < precision < 0.7
        
    def test_recall_calculation(self):
        """Test recall metric calculation"""
        predictions = pd.Series([True, True, False, False, True])
        actual = pd.Series([True, False, False, True, True])
        
        # True Positives: 2, False Negatives: 1
        # Recall = TP / (TP + FN) = 2 / 3 = 0.667
        tp = ((predictions == True) & (actual == True)).sum()
        fn = ((predictions == False) & (actual == True)).sum()
        
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        assert 0.6 < recall < 0.7


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
