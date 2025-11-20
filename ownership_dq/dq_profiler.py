"""
Comprehensive Data Quality Profiler
Assesses all 6 DAMA DQ dimensions with metrics and checks
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta


class DataQualityProfiler:
    """Comprehensive DQ profiling across all DAMA dimensions"""
    
    def __init__(self):
        self.profile_results = {}
        self.dq_checks = {}
        
    def profile_completeness(self, df: pd.DataFrame) -> Dict:
        """Assess completeness dimension"""
        print("\n📊 Profiling Completeness...")
        
        critical_fields = [
            'entity_name_raw', 'security', 'ownership_pct', 
            'shares', 'filing_date', 'filing_type'
        ]
        
        completeness_metrics = {}
        
        for field in critical_fields:
            if field in df.columns:
                null_count = df[field].isnull().sum()
                null_pct = (null_count / len(df)) * 100
                
                completeness_metrics[field] = {
                    'total_records': len(df),
                    'null_count': int(null_count),
                    'null_percentage': round(null_pct, 2),
                    'completeness_score': round(100 - null_pct, 2),
                    'status': 'PASS' if null_pct < 5 else 'WARN' if null_pct < 10 else 'FAIL'
                }
        
        overall_completeness = np.mean([m['completeness_score'] 
                                       for m in completeness_metrics.values()])
        
        print(f"   Overall Completeness: {overall_completeness:.2f}%")
        
        return {
            'dimension': 'Completeness',
            'overall_score': round(overall_completeness, 2),
            'field_metrics': completeness_metrics,
            'critical_issues': [k for k, v in completeness_metrics.items() 
                               if v['status'] == 'FAIL']
        }
    
    def profile_accuracy(self, df: pd.DataFrame) -> Dict:
        """Assess accuracy dimension"""
        print("\n🎯 Profiling Accuracy...")
        
        accuracy_checks = {}
        
        # Check 1: Ownership percentage range (0-100%)
        invalid_ownership = ((df['ownership_pct'] < 0) | 
                            (df['ownership_pct'] > 100)).sum()
        ownership_accuracy = (1 - invalid_ownership / len(df)) * 100
        
        accuracy_checks['ownership_pct_range'] = {
            'check': 'Ownership % in valid range (0-100%)',
            'invalid_count': int(invalid_ownership),
            'accuracy_score': round(ownership_accuracy, 2),
            'status': 'PASS' if ownership_accuracy > 95 else 'FAIL'
        }
        
        # Check 2: Negative shares
        negative_shares = (df['shares'] < 0).sum()
        shares_accuracy = (1 - negative_shares / len(df)) * 100
        
        accuracy_checks['shares_positive'] = {
            'check': 'Share count is positive',
            'invalid_count': int(negative_shares),
            'accuracy_score': round(shares_accuracy, 2),
            'status': 'PASS' if shares_accuracy > 95 else 'FAIL'
        }
        
        # Check 3: Market value consistency
        if 'market_value' in df.columns and 'shares' in df.columns:
            # Market value should be positive when shares > 0
            inconsistent_mv = ((df['shares'] > 0) & (df['market_value'] <= 0)).sum()
            mv_accuracy = (1 - inconsistent_mv / len(df)) * 100
            
            accuracy_checks['market_value_consistency'] = {
                'check': 'Market value consistent with shares',
                'invalid_count': int(inconsistent_mv),
                'accuracy_score': round(mv_accuracy, 2),
                'status': 'PASS' if mv_accuracy > 95 else 'FAIL'
            }
        
        # Check 4: Entity name format
        if 'entity_name_raw' in df.columns:
            invalid_names = df['entity_name_raw'].str.len() < 3
            name_accuracy = (1 - invalid_names.sum() / len(df)) * 100
            
            accuracy_checks['entity_name_format'] = {
                'check': 'Entity name has valid format',
                'invalid_count': int(invalid_names.sum()),
                'accuracy_score': round(name_accuracy, 2),
                'status': 'PASS' if name_accuracy > 98 else 'FAIL'
            }
        
        overall_accuracy = np.mean([c['accuracy_score'] 
                                   for c in accuracy_checks.values()])
        
        print(f"   Overall Accuracy: {overall_accuracy:.2f}%")
        
        return {
            'dimension': 'Accuracy',
            'overall_score': round(overall_accuracy, 2),
            'checks': accuracy_checks,
            'failed_checks': [k for k, v in accuracy_checks.items() 
                            if v['status'] == 'FAIL']
        }
    
    def profile_consistency(self, df: pd.DataFrame) -> Dict:
        """Assess consistency dimension"""
        print("\n🔄 Profiling Consistency...")
        
        consistency_checks = {}
        
        # Check 1: Filing type consistency
        valid_filing_types = ['13F', '13D', '13G', 'Form 4', 'Schedule 13D', 
                             'Schedule 13G', 'Schedule 13G/A']
        
        if 'filing_type' in df.columns:
            invalid_filing_types = ~df['filing_type'].isin(valid_filing_types)
            filing_consistency = (1 - invalid_filing_types.sum() / len(df)) * 100
            
            consistency_checks['filing_type_valid'] = {
                'check': 'Filing type from approved list',
                'valid_types': len(valid_filing_types),
                'invalid_count': int(invalid_filing_types.sum()),
                'consistency_score': round(filing_consistency, 2),
                'status': 'PASS' if filing_consistency > 98 else 'FAIL'
            }
        
        # Check 2: Security ticker format (2-5 uppercase letters)
        if 'security' in df.columns:
            valid_ticker_pattern = df['security'].str.match(r'^[A-Z]{2,5}$', na=False)
            ticker_consistency = (valid_ticker_pattern.sum() / len(df)) * 100
            
            consistency_checks['ticker_format'] = {
                'check': 'Security ticker has valid format',
                'invalid_count': int((~valid_ticker_pattern).sum()),
                'consistency_score': round(ticker_consistency, 2),
                'status': 'PASS' if ticker_consistency > 95 else 'FAIL'
            }
        
        # Check 3: Date format consistency
        if 'filing_date' in df.columns:
            valid_dates = pd.to_datetime(df['filing_date'], errors='coerce').notna()
            date_consistency = (valid_dates.sum() / len(df)) * 100
            
            consistency_checks['date_format'] = {
                'check': 'Filing date has valid format',
                'invalid_count': int((~valid_dates).sum()),
                'consistency_score': round(date_consistency, 2),
                'status': 'PASS' if date_consistency > 99 else 'FAIL'
            }
        
        overall_consistency = np.mean([c['consistency_score'] 
                                      for c in consistency_checks.values()])
        
        print(f"   Overall Consistency: {overall_consistency:.2f}%")
        
        return {
            'dimension': 'Consistency',
            'overall_score': round(overall_consistency, 2),
            'checks': consistency_checks,
            'failed_checks': [k for k, v in consistency_checks.items() 
                            if v['status'] == 'FAIL']
        }
    
    def profile_timeliness(self, df: pd.DataFrame) -> Dict:
        """Assess timeliness dimension"""
        print("\n⏰ Profiling Timeliness...")
        
        timeliness_metrics = {}
        
        if 'filing_date' in df.columns:
            df['filing_date_dt'] = pd.to_datetime(df['filing_date'], errors='coerce')
            current_date = datetime.now()
            
            # Calculate age of filings
            df['filing_age_days'] = (current_date - df['filing_date_dt']).dt.days
            
            # Recent filings (< 90 days)
            recent_count = (df['filing_age_days'] <= 90).sum()
            recent_pct = (recent_count / len(df)) * 100
            
            # Stale filings (> 180 days)
            stale_count = (df['filing_age_days'] > 180).sum()
            stale_pct = (stale_count / len(df)) * 100
            
            timeliness_score = 100 - stale_pct
            
            timeliness_metrics = {
                'total_filings': len(df),
                'recent_filings': int(recent_count),
                'recent_percentage': round(recent_pct, 2),
                'stale_filings': int(stale_count),
                'stale_percentage': round(stale_pct, 2),
                'avg_age_days': round(df['filing_age_days'].mean(), 1),
                'median_age_days': round(df['filing_age_days'].median(), 1),
                'timeliness_score': round(timeliness_score, 2),
                'status': 'PASS' if stale_pct < 10 else 'WARN' if stale_pct < 20 else 'FAIL'
            }
        
        print(f"   Timeliness Score: {timeliness_metrics.get('timeliness_score', 0):.2f}%")
        
        return {
            'dimension': 'Timeliness',
            'overall_score': timeliness_metrics.get('timeliness_score', 0),
            'metrics': timeliness_metrics
        }
    
    def profile_validity(self, df: pd.DataFrame) -> Dict:
        """Assess validity dimension"""
        print("\n✅ Profiling Validity...")
        
        validity_checks = {}
        
        # Check 1: Business rule - Ownership + Float should be reasonable
        if 'ownership_pct' in df.columns and 'float_pct' in df.columns:
            # Float % should generally be less than ownership %
            invalid_float = (df['float_pct'] > df['ownership_pct'] * 1.2).sum()
            float_validity = (1 - invalid_float / len(df)) * 100
            
            validity_checks['float_percentage'] = {
                'check': 'Float % is reasonable vs ownership %',
                'invalid_count': int(invalid_float),
                'validity_score': round(float_validity, 2),
                'status': 'PASS' if float_validity > 90 else 'FAIL'
            }
        
        # Check 2: QoQ change reasonableness
        if 'qoq_change_pct' in df.columns:
            # Changes > 1000% are likely errors
            extreme_changes = (abs(df['qoq_change_pct']) > 1000).sum()
            qoq_validity = (1 - extreme_changes / len(df)) * 100
            
            validity_checks['qoq_change'] = {
                'check': 'QoQ change is within reasonable bounds',
                'extreme_count': int(extreme_changes),
                'validity_score': round(qoq_validity, 2),
                'status': 'PASS' if qoq_validity > 95 else 'FAIL'
            }
        
        # Check 3: Required field combinations
        if all(col in df.columns for col in ['entity_name_raw', 'security', 'filing_date']):
            # These 3 fields should never all be null simultaneously
            missing_key_fields = (df[['entity_name_raw', 'security', 'filing_date']].isnull().all(axis=1)).sum()
            key_validity = (1 - missing_key_fields / len(df)) * 100
            
            validity_checks['key_fields'] = {
                'check': 'Key identification fields present',
                'invalid_count': int(missing_key_fields),
                'validity_score': round(key_validity, 2),
                'status': 'PASS' if key_validity == 100 else 'FAIL'
            }
        
        overall_validity = np.mean([c['validity_score'] 
                                   for c in validity_checks.values()])
        
        print(f"   Overall Validity: {overall_validity:.2f}%")
        
        return {
            'dimension': 'Validity',
            'overall_score': round(overall_validity, 2),
            'checks': validity_checks,
            'failed_checks': [k for k, v in validity_checks.items() 
                            if v['status'] == 'FAIL']
        }
    
    def profile_uniqueness(self, df: pd.DataFrame) -> Dict:
        """Assess uniqueness dimension"""
        print("\n🔑 Profiling Uniqueness...")
        
        uniqueness_metrics = {}
        
        # Check for duplicates on key fields
        key_fields = ['entity_canonical', 'security', 'filing_date']
        
        if all(col in df.columns for col in key_fields):
            duplicates = df.duplicated(subset=key_fields, keep=False).sum()
            duplicate_pct = (duplicates / len(df)) * 100
            uniqueness_score = 100 - duplicate_pct
            
            uniqueness_metrics = {
                'total_records': len(df),
                'duplicate_count': int(duplicates),
                'duplicate_percentage': round(duplicate_pct, 2),
                'unique_combinations': int(df[key_fields].drop_duplicates().shape[0]),
                'uniqueness_score': round(uniqueness_score, 2),
                'status': 'PASS' if duplicate_pct < 1 else 'WARN' if duplicate_pct < 5 else 'FAIL'
            }
        
        print(f"   Uniqueness Score: {uniqueness_metrics.get('uniqueness_score', 0):.2f}%")
        
        return {
            'dimension': 'Uniqueness',
            'overall_score': uniqueness_metrics.get('uniqueness_score', 0),
            'metrics': uniqueness_metrics
        }
    
    def generate_comprehensive_profile(self, df: pd.DataFrame) -> Dict:
        """Generate complete DQ profile across all dimensions"""
        print("\n" + "="*60)
        print("🔍 COMPREHENSIVE DATA QUALITY PROFILING")
        print("="*60)
        
        profile = {
            'profiling_timestamp': datetime.now().isoformat(),
            'dataset_size': len(df),
            'dimensions': {}
        }
        
        # Profile all 6 DAMA dimensions
        profile['dimensions']['completeness'] = self.profile_completeness(df)
        profile['dimensions']['accuracy'] = self.profile_accuracy(df)
        profile['dimensions']['consistency'] = self.profile_consistency(df)
        profile['dimensions']['timeliness'] = self.profile_timeliness(df)
        profile['dimensions']['validity'] = self.profile_validity(df)
        profile['dimensions']['uniqueness'] = self.profile_uniqueness(df)
        
        # Calculate overall DQ score
        dimension_scores = [d['overall_score'] for d in profile['dimensions'].values()]
        overall_dq_score = np.mean(dimension_scores)
        
        profile['overall_dq_score'] = round(overall_dq_score, 2)
        profile['dq_grade'] = self._calculate_grade(overall_dq_score)
        
        print("\n" + "="*60)
        print(f"📊 OVERALL DATA QUALITY SCORE: {overall_dq_score:.2f}% ({profile['dq_grade']})")
        print("="*60)
        
        return profile
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score"""
        if score >= 95:
            return 'A (Excellent)'
        elif score >= 90:
            return 'A- (Very Good)'
        elif score >= 85:
            return 'B+ (Good)'
        elif score >= 80:
            return 'B (Satisfactory)'
        elif score >= 75:
            return 'B- (Fair)'
        elif score >= 70:
            return 'C+ (Needs Improvement)'
        elif score >= 65:
            return 'C (Poor)'
        else:
            return 'F (Critical Issues)'


if __name__ == "__main__":
    print("Testing DQ Profiler...")
    
    # Create sample data
    sample_data = {
        'entity_canonical': ['VANGUARD'] * 50,
        'entity_name_raw': ['Vanguard Group Inc'] * 50,
        'security': ['AAPL'] * 50,
        'filing_date': pd.date_range('2024-01-01', periods=50),
        'filing_type': ['13F'] * 50,
        'ownership_pct': np.random.uniform(1, 10, 50),
        'shares': np.random.randint(100000, 5000000, 50),
        'market_value': np.random.uniform(1e6, 1e9, 50),
        'qoq_change_pct': np.random.uniform(-5, 5, 50),
        'float_pct': np.random.uniform(1, 10, 50)
    }
    
    df = pd.DataFrame(sample_data)
    
    profiler = DataQualityProfiler()
    profile = profiler.generate_comprehensive_profile(df)
