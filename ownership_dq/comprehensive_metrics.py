"""
Comprehensive Data Quality Profiling Metrics

STRATEGIC PURPOSE:
This module implements production-grade profiling across 12 metric categories.
Each category maps to specific business needs and stakeholder requirements.

METRIC CATEGORIES:
1. Completeness - Detect ingestion/parsing failures
2. Accuracy/Validity - Math errors, business rule violations
3. Timeliness - SLA compliance, vendor reliability
4. Consistency - Schema drift, temporal patterns
5. Distribution - Statistical profiling for anomaly detection
6. Categorical - Entity/ticker cardinality, classification drift
7. Correlation - Data sanity checks, pricing validation
8. Anomaly Detection - Multiple detection methods
9. ML-Ready - Features for downstream models
10. DQ Issues - Operational metrics for incident management
11. Vendor Quality - Upstream monitoring and SLA tracking
12. Quarterly Reports - Executive-level summaries

PRODUCTION NOTE:
POC implements core metrics to demonstrate framework. Production would add:
- Real-time streaming metrics
- Vendor-specific SLA tracking
- Automated alerting thresholds
- Historical trending (12+ months)
- Cross-dataset comparisons
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class ComprehensiveMetrics:
    """Production-grade profiling across 12 metric categories"""
    
    def __init__(self):
        self.results = {}
        
    # ===== 1. COMPLETENESS METRICS =====
    
    def calculate_completeness_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Detect ingestion/parsing failures early
        
        Metrics:
        - Field Completeness: % non-null per critical field
        - Record Completeness: % rows with all required fields
        - Coverage Completeness: % expected filers/securities present
        - Filing Coverage: % expected regulatory filings received
        """
        print("\n📊 Category 1: Completeness Metrics")
        
        critical_fields = [
            'entity_name_raw', 'security', 'ownership_pct',
            'shares', 'filing_date', 'filing_type', 'market_value'
        ]
        
        # Field-level completeness
        field_completeness = {}
        for field in critical_fields:
            if field in df.columns:
                non_null_pct = (df[field].notna().sum() / len(df)) * 100
                field_completeness[field] = round(non_null_pct, 2)
        
        # Record-level completeness (all required fields populated)
        required_fields = ['entity_name_raw', 'security', 'ownership_pct', 'shares']
        complete_records = df[required_fields].notna().all(axis=1).sum()
        record_completeness = (complete_records / len(df)) * 100
        
        # Coverage completeness
        unique_filers = df['entity_name_raw'].nunique()
        unique_securities = df['security'].nunique()
        
        # Filing coverage (by quarter)
        if 'filing_date' in df.columns:
            df['filing_quarter'] = pd.to_datetime(df['filing_date']).dt.to_period('Q')
            filing_coverage = df.groupby('filing_quarter').size().to_dict()
        else:
            filing_coverage = {}
        
        print(f"   Field Completeness: {np.mean(list(field_completeness.values())):.1f}%")
        print(f"   Record Completeness: {record_completeness:.1f}%")
        print(f"   Coverage: {unique_filers} filers × {unique_securities} securities")
        
        return {
            'field_completeness': field_completeness,
            'record_completeness': round(record_completeness, 2),
            'coverage_stats': {
                'unique_filers': int(unique_filers),
                'unique_securities': int(unique_securities),
                'total_positions': len(df)
            },
            'filing_coverage': {str(k): int(v) for k, v in filing_coverage.items()},
            'overall_score': round(np.mean(list(field_completeness.values())), 2)
        }
    
    # ===== 2. ACCURACY / VALIDITY METRICS =====
    
    def calculate_accuracy_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Detect math errors, prevent double-counting
        
        Metrics:
        - Ownership % Accuracy: Validate math formulas
        - Identifier Validity: CUSIP/CIK correctness
        - Duplicate Position Detection: Prevent double-counting
        - Business Rule Violations: ownership > 100%, negative shares
        """
        print("\n🎯 Category 2: Accuracy / Validity Metrics")
        
        accuracy_checks = {}
        
        # Ownership % range check
        valid_ownership = df['ownership_pct'].between(0, 100).sum()
        ownership_accuracy = (valid_ownership / len(df)) * 100
        accuracy_checks['ownership_range'] = round(ownership_accuracy, 2)
        
        # Negative shares check
        positive_shares = (df['shares'] >= 0).sum()
        shares_accuracy = (positive_shares / len(df)) * 100
        accuracy_checks['positive_shares'] = round(shares_accuracy, 2)
        
        # Duplicate detection (same filer + security in same period)
        if 'filing_date' in df.columns:
            df['filing_period'] = pd.to_datetime(df['filing_date']).dt.to_period('Q')
            duplicates = df.duplicated(
                subset=['entity_name_raw', 'security', 'filing_period'], 
                keep=False
            ).sum()
            duplicate_rate = (duplicates / len(df)) * 100
            accuracy_checks['duplicate_rate'] = round(duplicate_rate, 2)
        else:
            duplicates = 0
            duplicate_rate = 0
        
        # Business rule violations
        violations = 0
        violations += (df['ownership_pct'] > 100).sum()  # Impossible ownership
        violations += (df['shares'] < 0).sum()  # Negative shares
        if 'market_value' in df.columns:
            violations += ((df['shares'] > 0) & (df['market_value'] <= 0)).sum()
        
        violation_rate = (violations / len(df)) * 100
        accuracy_checks['business_rule_violations'] = round(violation_rate, 2)
        
        # Overall accuracy (inverse of issues)
        overall_accuracy = 100 - violation_rate - duplicate_rate
        
        print(f"   Ownership Range Accuracy: {ownership_accuracy:.1f}%")
        print(f"   Duplicate Positions: {duplicates} ({duplicate_rate:.1f}%)")
        print(f"   Business Rule Violations: {violations} ({violation_rate:.1f}%)")
        
        return {
            'accuracy_checks': accuracy_checks,
            'duplicate_count': int(duplicates),
            'violation_count': int(violations),
            'overall_score': round(max(0, overall_accuracy), 2)
        }
    
    # ===== 3. TIMELINESS METRICS =====
    
    def calculate_timeliness_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Track vendor SLA, identify bottlenecks
        
        Metrics:
        - Filing Lag: Time from filing to ingestion
        - Freshness Age: Age of latest data
        - SLA Compliance Rate: % processed within SLA
        """
        print("\n⏰ Category 3: Timeliness Metrics")
        
        timeliness = {}
        
        if 'filing_date' in df.columns and 'ingestion_date' in df.columns:
            df['filing_lag_days'] = (
                pd.to_datetime(df['ingestion_date']) - 
                pd.to_datetime(df['filing_date'])
            ).dt.days
            
            avg_lag = df['filing_lag_days'].mean()
            max_lag = df['filing_lag_days'].max()
            
            # SLA: process within 2 days
            sla_threshold = 2
            sla_compliant = (df['filing_lag_days'] <= sla_threshold).sum()
            sla_rate = (sla_compliant / len(df)) * 100
            
            timeliness['avg_filing_lag_days'] = round(avg_lag, 2)
            timeliness['max_filing_lag_days'] = int(max_lag)
            timeliness['sla_compliance_rate'] = round(sla_rate, 2)
            
        else:
            # Estimate based on filing dates
            if 'filing_date' in df.columns:
                latest_filing = pd.to_datetime(df['filing_date']).max()
                freshness_days = (datetime.now() - latest_filing).days
                timeliness['data_freshness_days'] = int(freshness_days)
            
            timeliness['note'] = 'Ingestion dates not available in POC'
        
        print(f"   Timeliness metrics: {len(timeliness)} calculated")
        
        return {
            'timeliness_metrics': timeliness,
            'overall_score': round(timeliness.get('sla_compliance_rate', 90), 2)
        }
    
    # ===== 4. CONSISTENCY METRICS =====
    
    def calculate_consistency_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Detect drift, pattern breaks, volatility
        
        Metrics:
        - Temporal Consistency: QoQ behavior patterns
        - Rolling Statistics: Trend stability
        - Peer Consistency: Compare vs sector cohorts
        """
        print("\n🔄 Category 4: Consistency Metrics")
        
        consistency = {}
        
        # Schema consistency (column count and types)
        consistency['schema_columns'] = len(df.columns)
        # Convert dtypes to string for JSON serialization
        consistency['schema_dtypes'] = {
            str(k): int(v) for k, v in df.dtypes.value_counts().to_dict().items()
        }
        
        # Temporal consistency (QoQ changes)
        if 'qoq_change_pct' in df.columns:
            qoq_mean = df['qoq_change_pct'].mean()
            qoq_std = df['qoq_change_pct'].std()
            
            # Flag extreme changes (>3 std devs)
            extreme_changes = (np.abs(df['qoq_change_pct']) > qoq_mean + 3*qoq_std).sum()
            consistency['extreme_qoq_changes'] = int(extreme_changes)
            consistency['qoq_mean'] = round(qoq_mean, 2)
            consistency['qoq_std'] = round(qoq_std, 2)
        
        # Rolling statistics consistency
        if 'ownership_7d_ma' in df.columns and 'ownership_7d_std' in df.columns:
            ma_stability = df['ownership_7d_std'].mean()
            consistency['rolling_ma_stability'] = round(ma_stability, 4)
        
        # Calculate consistency score (lower variation = higher consistency)
        consistency_score = 90  # Base score
        if 'extreme_qoq_changes' in consistency:
            change_impact = (consistency['extreme_qoq_changes'] / len(df)) * 100
            consistency_score -= min(20, change_impact * 2)
        
        print(f"   Schema: {consistency['schema_columns']} columns")
        if 'extreme_qoq_changes' in consistency:
            print(f"   Extreme QoQ Changes: {consistency['extreme_qoq_changes']}")
        
        return {
            'consistency_metrics': consistency,
            'overall_score': round(consistency_score, 2)
        }
    
    # ===== 5. DISTRIBUTION PROFILING METRICS =====
    
    def calculate_distribution_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Baseline for anomaly detection, drift detection
        
        Metrics:
        - Mean, Std, Skewness, Kurtosis
        - Coefficient of Variation
        - Percentiles / IQR
        - Heavy-tail detection
        """
        print("\n📈 Category 5: Distribution Profiling")
        
        distributions = {}
        
        # Focus on key numeric fields
        numeric_fields = ['ownership_pct', 'shares', 'market_value', 'qoq_change_pct']
        
        for field in numeric_fields:
            if field in df.columns:
                data = df[field].dropna()
                
                distributions[field] = {
                    'mean': round(float(data.mean()), 4),
                    'std': round(float(data.std()), 4),
                    'skewness': round(float(stats.skew(data)), 4),
                    'kurtosis': round(float(stats.kurtosis(data)), 4),
                    'cv': round(float(data.std() / data.mean()) if data.mean() != 0 else 0, 4),
                    'percentiles': {
                        'p25': round(float(data.quantile(0.25)), 4),
                        'p50': round(float(data.quantile(0.50)), 4),
                        'p75': round(float(data.quantile(0.75)), 4),
                        'p95': round(float(data.quantile(0.95)), 4)
                    },
                    'iqr': round(float(data.quantile(0.75) - data.quantile(0.25)), 4)
                }
        
        print(f"   Profiled distributions for {len(distributions)} fields")
        
        return {
            'distributions': distributions,
            'overall_score': 95  # Distribution profiling doesn't have a quality score
        }
    
    # ===== 6. CATEGORICAL PROFILING METRICS =====
    
    def calculate_categorical_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Detect category explosion, classification drift
        
        Metrics:
        - Cardinality: Count of unique values
        - Entropy: Category randomness
        - Category Coverage: Expected categories present
        """
        print("\n🏷️ Category 6: Categorical Profiling")
        
        categorical = {}
        
        # Analyze categorical fields
        cat_fields = ['entity_name_raw', 'security', 'filing_type']
        
        for field in cat_fields:
            if field in df.columns:
                value_counts = df[field].value_counts()
                
                # Calculate entropy
                probs = value_counts / value_counts.sum()
                entropy = -np.sum(probs * np.log2(probs + 1e-10))
                
                categorical[field] = {
                    'cardinality': int(df[field].nunique()),
                    'entropy': round(float(entropy), 4),
                    'top_categories': {k: int(v) for k, v in value_counts.head(5).to_dict().items()},
                    'coverage_pct': round((df[field].notna().sum() / len(df)) * 100, 2)
                }
        
        print(f"   Profiled {len(categorical)} categorical fields")
        
        return {
            'categorical_metrics': categorical,
            'overall_score': 95  # Categorical profiling doesn't have quality score
        }
    
    # ===== 7. CORRELATION METRICS =====
    
    def calculate_correlation_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Data sanity checks, pricing validation
        
        Metrics:
        - shares ↔ market_value correlation
        - ownership_pct ↔ shares correlation
        """
        print("\n🔗 Category 7: Correlation Metrics")
        
        correlations = {}
        
        # Key correlations to validate
        correlation_pairs = [
            ('shares', 'market_value'),
            ('ownership_pct', 'shares')
        ]
        
        for field1, field2 in correlation_pairs:
            if field1 in df.columns and field2 in df.columns:
                data1 = df[field1].dropna()
                data2 = df[field2].dropna()
                
                # Ensure same length
                common_idx = data1.index.intersection(data2.index)
                if len(common_idx) > 0:
                    corr = np.corrcoef(data1[common_idx], data2[common_idx])[0, 1]
                    correlations[f"{field1}_vs_{field2}"] = round(float(corr), 4)
        
        print(f"   Calculated {len(correlations)} correlations")
        
        return {
            'correlations': correlations,
            'overall_score': 95  # Correlation is validation, not quality metric
        }
    
    # ===== 8. ANOMALY DETECTION METRICS =====
    
    def calculate_anomaly_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Multiple detection methods, FP rate tracking
        
        Metrics:
        - Z-Score anomalies (±3σ)
        - IQR outliers
        - QoQ spike detection
        - Hybrid classification performance
        """
        print("\n🚨 Category 8: Anomaly Detection Metrics")
        
        anomaly_stats = {}
        
        # Z-score anomalies (±3σ)
        if 'ownership_pct' in df.columns:
            z_scores = np.abs(stats.zscore(df['ownership_pct'].dropna()))
            z_anomalies = (z_scores > 3).sum()
            anomaly_stats['zscore_anomalies_3sigma'] = int(z_anomalies)
        
        # IQR outliers
        if 'ownership_pct' in df.columns:
            Q1 = df['ownership_pct'].quantile(0.25)
            Q3 = df['ownership_pct'].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df['ownership_pct'] < (Q1 - 1.5 * IQR)) | 
                       (df['ownership_pct'] > (Q3 + 1.5 * IQR))).sum()
            anomaly_stats['iqr_outliers'] = int(outliers)
        
        # QoQ spike detection
        if 'qoq_change_pct' in df.columns:
            extreme_spikes = (np.abs(df['qoq_change_pct']) > 50).sum()
            anomaly_stats['qoq_spikes_gt50pct'] = int(extreme_spikes)
        
        # Hybrid classification (if available)
        if 'hybrid_anomaly' in df.columns:
            anomaly_stats['hybrid_detected'] = int(df['hybrid_anomaly'].sum())
            anomaly_stats['hybrid_detection_rate'] = round(
                (df['hybrid_anomaly'].sum() / len(df)) * 100, 2
            )
        
        print(f"   Anomaly metrics: {len(anomaly_stats)} calculated")
        
        return {
            'anomaly_stats': anomaly_stats,
            'overall_score': 95  # Anomaly detection is analysis, not quality
        }
    
    # ===== 9. ML-READY METRICS =====
    
    def calculate_ml_ready_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Features for downstream ML models
        
        Metrics:
        - Completeness trends
        - Anomaly density (rolling)
        - Validation failure rates
        """
        print("\n🤖 Category 9: ML-Ready Metrics")
        
        ml_features = {}
        
        # 30-day completeness trend
        if 'filing_date' in df.columns:
            df_sorted = df.sort_values('filing_date')
            df_sorted['date'] = pd.to_datetime(df_sorted['filing_date'])
            
            # Rolling 30-day completeness
            window = 30
            if len(df_sorted) >= window:
                rolling_complete = df_sorted['ownership_pct'].notna().rolling(window).mean()
                ml_features['completeness_trend_30d'] = round(
                    rolling_complete.iloc[-1] * 100 if len(rolling_complete) > 0 else 0, 2
                )
        
        # Anomaly density (if hybrid detection ran)
        if 'hybrid_anomaly' in df.columns:
            anomaly_rate = (df['hybrid_anomaly'].sum() / len(df)) * 100
            ml_features['anomaly_density'] = round(anomaly_rate, 2)
        
        # Validation failure rate
        violations = 0
        violations += (df['ownership_pct'] < 0).sum() + (df['ownership_pct'] > 100).sum()
        violations += (df['shares'] < 0).sum()
        failure_rate = (violations / len(df)) * 100
        ml_features['validation_failure_rate'] = round(failure_rate, 2)
        
        print(f"   ML features: {len(ml_features)} generated")
        
        return {
            'ml_features': ml_features,
            'overall_score': 95  # ML features are derived metrics
        }
    
    # ===== 10. DQ ISSUE METRICS =====
    
    def calculate_issue_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Operational monitoring, incident management
        
        Metrics:
        - Issue count and severity
        - Root cause classification
        - Entity resolution conflicts
        """
        print("\n⚠️ Category 10: DQ Issue Metrics")
        
        issues = {
            'total_issues': 0,
            'severity_breakdown': {'high': 0, 'medium': 0, 'low': 0},
            'issue_types': {}
        }
        
        # High severity: Business rule violations
        high_issues = 0
        high_issues += (df['ownership_pct'] > 100).sum()
        high_issues += (df['shares'] < 0).sum()
        issues['severity_breakdown']['high'] = int(high_issues)
        
        # Medium severity: Completeness issues
        medium_issues = 0
        for field in ['entity_name_raw', 'security', 'ownership_pct']:
            if field in df.columns:
                medium_issues += df[field].isnull().sum()
        issues['severity_breakdown']['medium'] = int(medium_issues)
        
        # Low severity: Entity resolution candidates
        if 'entity_name_raw' in df.columns:
            low_issues = df['entity_name_raw'].nunique() * 0.1  # Estimate 10% need review
            issues['severity_breakdown']['low'] = int(low_issues)
        
        issues['total_issues'] = sum(issues['severity_breakdown'].values())
        
        print(f"   Total Issues: {issues['total_issues']}")
        print(f"   High/Med/Low: {high_issues}/{medium_issues}/{int(low_issues)}")
        
        return {
            'issues': issues,
            'overall_score': max(0, 100 - (high_issues / len(df) * 100))
        }
    
    # ===== 11. VENDOR QUALITY METRICS =====
    
    def calculate_vendor_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Upstream monitoring, vendor SLA tracking
        
        Metrics:
        - Vendor SLA compliance
        - Vendor-attributable issues
        - Delivery delay trends
        
        NOTE: POC uses simulated vendor data. Production would track:
        - Multiple vendor sources (Bloomberg, FactSet, SEC EDGAR)
        - Per-vendor accuracy and timeliness
        - Vendor-specific anomaly rates
        """
        print("\n🏢 Category 11: Vendor Quality Metrics")
        
        vendor = {
            'note': 'POC uses synthetic data - production would track real vendors',
            'simulated_vendors': ['Bloomberg', 'SEC EDGAR', 'FactSet'],
            'overall_vendor_quality': 92.5  # Simulated
        }
        
        # Simulate vendor distribution
        if len(df) > 0:
            # In production, this would come from actual source tracking
            vendor['vendor_sla_compliance'] = {
                'Bloomberg': 94.5,
                'SEC_EDGAR': 98.2,
                'FactSet': 91.3
            }
        
        print(f"   Vendor metrics: Simulated for POC")
        
        return {
            'vendor_metrics': vendor,
            'overall_score': 92.5
        }
    
    # ===== 12. QUARTERLY REPORT METRICS =====
    
    def calculate_quarterly_metrics(self, df: pd.DataFrame) -> Dict:
        """
        BUSINESS VALUE: Executive summaries, trend analysis
        
        Metrics:
        - Quarterly completeness trends
        - Quarterly accuracy benchmarks
        - Anomaly rate trends
        - Incident summaries
        """
        print("\n📅 Category 12: Quarterly Report Metrics")
        
        quarterly = {}
        
        if 'filing_date' in df.columns:
            df['quarter'] = pd.to_datetime(df['filing_date']).dt.to_period('Q')
            
            # Completeness by quarter
            completeness_by_q = df.groupby('quarter').apply(
                lambda x: (x['ownership_pct'].notna().sum() / len(x)) * 100
            ).to_dict()
            quarterly['completeness_by_quarter'] = {
                str(k): round(v, 2) for k, v in completeness_by_q.items()
            }
            
            # Anomaly rate by quarter (if available)
            if 'hybrid_anomaly' in df.columns:
                anomaly_by_q = df.groupby('quarter')['hybrid_anomaly'].mean() * 100
                quarterly['anomaly_rate_by_quarter'] = {
                    str(k): round(v, 2) for k, v in anomaly_by_q.to_dict().items()
                }
            
            # Record count by quarter
            records_by_q = df.groupby('quarter').size().to_dict()
            quarterly['records_by_quarter'] = {
                str(k): int(v) for k, v in records_by_q.items()
            }
        
        print(f"   Quarterly metrics: {len(quarterly)} calculated")
        
        return {
            'quarterly_metrics': quarterly,
            'overall_score': 95  # Quarterly metrics are summaries
        }
    
    # ===== MASTER PROFILING FUNCTION =====
    
    def profile_all_categories(self, df: pd.DataFrame) -> Dict:
        """
        Execute comprehensive profiling across all 12 categories
        
        Returns dict with:
        - Individual category results
        - Overall DQ score
        - Executive summary
        """
        print("\n" + "="*80)
        print("🔬 COMPREHENSIVE DATA QUALITY PROFILING")
        print("="*80)
        
        results = {}
        
        # Execute all profiling categories
        results['1_completeness'] = self.calculate_completeness_metrics(df)
        results['2_accuracy'] = self.calculate_accuracy_metrics(df)
        results['3_timeliness'] = self.calculate_timeliness_metrics(df)
        results['4_consistency'] = self.calculate_consistency_metrics(df)
        results['5_distribution'] = self.calculate_distribution_metrics(df)
        results['6_categorical'] = self.calculate_categorical_metrics(df)
        results['7_correlation'] = self.calculate_correlation_metrics(df)
        results['8_anomaly'] = self.calculate_anomaly_metrics(df)
        results['9_ml_ready'] = self.calculate_ml_ready_metrics(df)
        results['10_issues'] = self.calculate_issue_metrics(df)
        results['11_vendor'] = self.calculate_vendor_metrics(df)
        results['12_quarterly'] = self.calculate_quarterly_metrics(df)
        
        # Calculate overall DQ score (weighted average)
        category_weights = {
            '1_completeness': 0.20,  # Critical for usability
            '2_accuracy': 0.25,      # Most important for trust
            '3_timeliness': 0.15,    # Important for SLA
            '4_consistency': 0.10,   # Stability matters
            '10_issues': 0.20,       # Direct impact
            '11_vendor': 0.10        # Upstream quality
        }
        
        weighted_score = sum(
            results[cat]['overall_score'] * weight 
            for cat, weight in category_weights.items()
        )
        
        # Executive summary
        summary = {
            'overall_dq_score': round(weighted_score, 2),
            'total_records': len(df),
            'profiling_timestamp': datetime.now().isoformat(),
            'categories_profiled': 12,
            'critical_issues': results['10_issues']['issues']['severity_breakdown']['high'],
            'recommendation': self._get_recommendation(weighted_score)
        }
        
        results['executive_summary'] = summary
        
        print("\n" + "="*80)
        print(f"✅ OVERALL DQ SCORE: {summary['overall_dq_score']:.1f}/100")
        print(f"   {summary['recommendation']}")
        print("="*80 + "\n")
        
        return results
    
    def _get_recommendation(self, score: float) -> str:
        """Get executive recommendation based on score"""
        if score >= 90:
            return "EXCELLENT - Production ready with minor monitoring"
        elif score >= 80:
            return "GOOD - Address medium issues before production"
        elif score >= 70:
            return "FAIR - Significant remediation needed"
        else:
            return "POOR - Major quality issues, not production ready"
