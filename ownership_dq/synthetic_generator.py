"""
Synthetic Ownership Data Generator

STRATEGIC PURPOSE:
Generate realistic ownership data with controlled quality scenarios to validate
detection framework. Critical for testing because:
1. Real data has privacy/legal constraints
2. Need known ground truth to measure detection accuracy
3. Can simulate rare edge cases (M&A, index reconstitution)

DATA QUALITY SCENARIOS:
- False Positives: Legitimate patterns that look suspicious (70%+ one-day changes from index adds)
- False Negatives: Errors that look normal (gradual drift in reported positions)
- True Anomalies: Actual data quality issues (duplicate filings, wrong CIK mapping)
- Outliers: Statistical edge cases (activist investors, concentrated positions)
- Normal patterns: Typical institutional rebalancing behavior

REALISM CONSIDERATIONS:
- Based on 13F filing frequency and patterns
- Entity name variations reflect real-world data messiness
- Ownership distributions follow power law (few large holders, many small)
- Corporate actions and index changes create temporal complexity

POC NOTE: Uses simplified synthetic approach. Production would analyze
historical data distributions and use generative models (GANs/VAEs).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import Dict, List

class OwnershipDataGenerator:
    """Generate realistic ownership data with quality scenarios"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        # Entity name variations for graph network testing
        self.entity_variations = {
            "BERKSHIRE_HATHAWAY": [
                "Berkshire Hathaway Inc",
                "BERKSHIRE HATHAWAY INC.",
                "Berkshire Hathaway",
                "BRK.A Holdings",
                "Warren Buffett - Berkshire",
                "Berkshire Hathway Inc"  # Intentional typo
            ],
            "VANGUARD": [
                "Vanguard Group Inc",
                "The Vanguard Group, Inc.",
                "Vanguard Group",
                "Vanguard Funds",
                "VANGUARD GROUP INC"
            ],
            "BLACKROCK": [
                "BlackRock Inc.",
                "BlackRock, Inc",
                "BlackRock Fund Advisors",
                "BLACKROCK INC",
                "Black Rock Inc"
            ],
            "STATE_STREET": [
                "State Street Corporation",
                "State Street Corp",
                "STATE STREET CORP",
                "State St. Corp",
                "StateStreet Corporation"
            ],
            "JPMORGAN": [
                "JPMorgan Chase & Co",
                "JP Morgan Chase & Co.",
                "JPMORGAN CHASE & CO",
                "JPM Chase",
                "J.P. Morgan"
            ]
        }
        
        self.securities = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "JPM", "V", "WMT",
            "UNH", "MA", "HD", "PG", "DIS"
        ]
        
        self.filing_types = ["13F", "13D", "13G", "Form 4", "Schedule 13G/A"]
        
    def generate_complete_dataset(
        self,
        n_records: int = 5000,
        start_date: str = "2021-01-01",
        end_date: str = "2024-12-31"
    ) -> pd.DataFrame:
        """Generate complete ownership dataset with all scenarios"""
        
        print("🔄 Generating ownership data with quality scenarios...")
        
        records = []
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Scenario distribution
        scenario_weights = {
            "normal": 0.70,           # 70% normal data
            "true_anomaly": 0.10,     # 10% real anomalies
            "false_positive": 0.08,   # 8% false positives (looks wrong, is right)
            "false_negative": 0.07,   # 7% false negatives (looks right, is wrong)
            "outlier": 0.05           # 5% statistical outliers
        }
        
        for i in range(n_records):
            # Select scenario
            scenario = np.random.choice(
                list(scenario_weights.keys()),
                p=list(scenario_weights.values())
            )
            
            # Generate base record
            entity_key = random.choice(list(self.entity_variations.keys()))
            entity_name = random.choice(self.entity_variations[entity_key])
            security = random.choice(self.securities)
            filing_date = start + timedelta(days=random.randint(0, (end - start).days))
            filing_type = random.choice(self.filing_types)
            
            # Generate scenario-specific data
            record = self._generate_scenario_record(
                scenario, entity_key, entity_name, security, filing_date, filing_type, i
            )
            
            records.append(record)
        
        df = pd.DataFrame(records)
        
        # Add time-series features for LSTM
        df = self._add_time_series_features(df)
        
        print(f"✅ Generated {len(df)} records across {len(df['filing_date'].unique())} dates")
        print(f"   📊 Scenario distribution:")
        for scenario, count in df['scenario_type'].value_counts().items():
            print(f"      - {scenario}: {count} ({count/len(df)*100:.1f}%)")
        
        return df
    
    def _generate_scenario_record(
        self,
        scenario: str,
        entity_key: str,
        entity_name: str,
        security: str,
        filing_date: datetime,
        filing_type: str,
        record_id: int
    ) -> Dict:
        """Generate record based on scenario type"""
        
        base_record = {
            "record_id": f"REC_{record_id:06d}",
            "entity_canonical": entity_key,
            "entity_name_raw": entity_name,
            "security": security,
            "filing_date": filing_date,
            "filing_type": filing_type,
            "scenario_type": scenario,
        }
        
        if scenario == "normal":
            return self._normal_record(base_record)
        elif scenario == "true_anomaly":
            return self._true_anomaly_record(base_record)
        elif scenario == "false_positive":
            return self._false_positive_record(base_record)
        elif scenario == "false_negative":
            return self._false_negative_record(base_record)
        else:  # outlier
            return self._outlier_record(base_record)
    
    def _normal_record(self, base: Dict) -> Dict:
        """Normal ownership pattern with realistic ranges by entity type"""
        
        # Realistic ownership ranges based on entity type
        entity_ranges = {
            "BERKSHIRE_HATHAWAY": (3.0, 10.0),
            "VANGUARD": (4.0, 8.0),
            "BLACKROCK": (3.5, 7.5),
            "STATE_STREET": (2.5, 6.5),
            "JPMORGAN": (2.0, 5.5)
        }
        
        ownership_range = entity_ranges.get(base['entity_canonical'], (0.5, 8.0))
        ownership_pct = np.random.uniform(*ownership_range)
        
        # Calculate shares based on realistic ownership
        total_shares_outstanding = np.random.uniform(1e9, 5e9)  # 1B to 5B shares
        shares = int(ownership_pct / 100 * total_shares_outstanding)
        
        # Stock price varies by security
        stock_price = np.random.uniform(150, 300)
        market_value = shares * stock_price
        
        # Add narrative (for NLP extraction)
        narrative = self._generate_narrative(
            base['entity_name_raw'],
            base['security'],
            ownership_pct,
            shares,
            "normal"
        )
        
        base.update({
            "ownership_pct": round(ownership_pct, 2),
            "shares": shares,
            "market_value": round(market_value, 2),
            "qoq_change_pct": round(np.random.uniform(-2, 2), 2),
            "float_pct": round(ownership_pct / 100 * 95, 2),
            "narrative": narrative,
            "quality_label": "normal",
            "needs_review": False
        })
        return base
    
    def _true_anomaly_record(self, base: Dict) -> Dict:
        """Real data quality issue"""
        anomaly_types = [
            "impossible_ownership",  # >100%
            "negative_shares",
            "massive_jump",
            "data_corruption"
        ]
        
        anomaly_type = random.choice(anomaly_types)
        
        if anomaly_type == "impossible_ownership":
            ownership_pct = np.random.uniform(105, 250)  # Impossible!
            shares = int(np.random.uniform(10000000, 50000000))
            qoq_change = np.random.uniform(50, 100)
        elif anomaly_type == "negative_shares":
            ownership_pct = -np.random.uniform(1, 10)
            shares = -int(np.random.uniform(100000, 1000000))
            qoq_change = -np.random.uniform(80, 100)
        elif anomaly_type == "massive_jump":
            ownership_pct = np.random.uniform(25, 45)
            shares = int(np.random.uniform(5000000, 20000000))
            qoq_change = np.random.uniform(2000, 5000)  # 2000%+ jump!
        else:  # data_corruption
            ownership_pct = 99999.99
            shares = 0
            qoq_change = 0
        
        market_value = shares * np.random.uniform(150, 300) if shares > 0 else 0
        
        narrative = f"ERROR: Invalid data for {base['security']}"
        
        base.update({
            "ownership_pct": round(ownership_pct, 2),
            "shares": shares,
            "market_value": round(market_value, 2),
            "qoq_change_pct": round(qoq_change, 2),
            "float_pct": round(ownership_pct / 100 * 95, 2) if ownership_pct > 0 else 0,
            "narrative": narrative,
            "quality_label": "anomaly",
            "anomaly_type": anomaly_type,
            "needs_review": True
        })
        return base
    
    def _false_positive_record(self, base: Dict) -> Dict:
        """Looks wrong but is actually correct - large but legitimate changes"""
        
        # Realistic base ownership that experiences large change
        base_ownership = np.random.uniform(4.0, 8.0)
        ownership_pct = base_ownership * np.random.uniform(1.4, 1.8)  # 40-80% increase
        
        # Calculate shares based on ownership
        total_shares_outstanding = np.random.uniform(1e9, 5e9)
        shares = int(ownership_pct / 100 * total_shares_outstanding)
        
        # Large but legitimate quarterly change
        qoq_change = (ownership_pct - base_ownership) / base_ownership * 100
        
        stock_price = np.random.uniform(150, 300)
        market_value = shares * stock_price
        
        reasons = [
            "Quarterly index rebalancing",
            "Stock split adjustment (2-for-1)",
            "Merger completion",
            "Index inclusion (S&P 500 addition)"
        ]
        reason = random.choice(reasons)
        
        narrative = f"{base['entity_name_raw']} increased holdings in {base['security']} " \
                   f"by {qoq_change:.1f}% due to {reason}. " \
                   f"Current position: {shares:,} shares ({ownership_pct:.2f}% of outstanding)."
        
        base.update({
            "ownership_pct": round(ownership_pct, 2),
            "shares": shares,
            "market_value": round(market_value, 2),
            "qoq_change_pct": round(qoq_change, 2),
            "float_pct": round(ownership_pct / 100 * 95, 2),
            "narrative": narrative,
            "quality_label": "normal",  # Actually correct!
            "false_positive_reason": reason,
            "needs_review": False
        })
        return base
    
    def _false_negative_record(self, base: Dict) -> Dict:
        """Looks right but is actually wrong"""
        ownership_pct = np.random.uniform(2.0, 6.0)
        shares = int(np.random.uniform(500000, 2000000))
        qoq_change = np.random.uniform(-3, 3)
        market_value = shares * np.random.uniform(150, 300)
        
        error_types = ["wrong_entity", "stale_data", "duplicate", "wrong_security"]
        error_type = random.choice(error_types)
        
        narrative = f"{base['entity_name_raw']} holds {shares:,} shares of {base['security']}."
        
        base.update({
            "ownership_pct": round(ownership_pct, 2),
            "shares": shares,
            "market_value": round(market_value, 2),
            "qoq_change_pct": round(qoq_change, 2),
            "float_pct": round(ownership_pct / 100 * 95, 2),
            "narrative": narrative,
            "quality_label": "anomaly",  # Actually wrong!
            "false_negative_type": error_type,
            "needs_review": True
        })
        return base
    
    def _outlier_record(self, base: Dict) -> Dict:
        """Statistical outlier but legitimate"""
        ownership_pct = np.random.uniform(15, 25)
        shares = int(np.random.uniform(10000000, 30000000))
        qoq_change = np.random.uniform(15, 25)
        market_value = shares * np.random.uniform(150, 300)
        
        contexts = ["Activist investment", "Strategic acquisition", "Insider accumulation"]
        context = random.choice(contexts)
        
        narrative = f"{base['entity_name_raw']} disclosed {ownership_pct:.1f}% stake in " \
                   f"{base['security']} as part of {context}."
        
        base.update({
            "ownership_pct": round(ownership_pct, 2),
            "shares": shares,
            "market_value": round(market_value, 2),
            "qoq_change_pct": round(qoq_change, 2),
            "float_pct": round(ownership_pct / 100 * 95, 2),
            "narrative": narrative,
            "quality_label": "normal",  # Legitimate outlier
            "outlier_context": context,
            "needs_review": False
        })
        return base
    
    def _generate_narrative(self, entity: str, security: str, 
                          ownership_pct: float, shares: int, scenario: str) -> str:
        """Generate realistic narrative for NLP extraction"""
        templates = [
            f"{entity} holds {shares:,} shares of {security}, representing {ownership_pct:.2f}% of outstanding shares.",
            f"As of the reporting date, {entity} beneficially owned {shares:,} shares ({ownership_pct:.2f}% of the class) of {security}.",
            f"{entity} reports ownership of {ownership_pct:.2f}% of {security} common stock, totaling {shares:,} shares."
        ]
        return random.choice(templates)
    
    def _add_time_series_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add features needed for LSTM model"""
        df = df.sort_values(['entity_canonical', 'security', 'filing_date'])
        
        # Rolling statistics
        df['ownership_7d_ma'] = df.groupby(['entity_canonical', 'security'])['ownership_pct'].transform(
            lambda x: x.rolling(window=3, min_periods=1).mean()
        )
        
        df['ownership_7d_std'] = df.groupby(['entity_canonical', 'security'])['ownership_pct'].transform(
            lambda x: x.rolling(window=3, min_periods=1).std()
        )
        
        # Previous quarter value
        df['ownership_prev_quarter'] = df.groupby(['entity_canonical', 'security'])['ownership_pct'].shift(1)
        df['ownership_actual_change'] = df['ownership_pct'] - df['ownership_prev_quarter']
        
        # Fill NaN
        df['ownership_7d_std'].fillna(0, inplace=True)
        df['ownership_prev_quarter'].fillna(df['ownership_pct'], inplace=True)
        df['ownership_actual_change'].fillna(0, inplace=True)
        
        return df


if __name__ == "__main__":
    generator = OwnershipDataGenerator(seed=42)
    df = generator.generate_complete_dataset(n_records=5000)
    df.to_csv("/home/claude/ownership_dq_poc/data/ownership_complete.csv", index=False)
    print("\n✅ Synthetic data generation complete!")
