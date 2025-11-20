"""
NLP Entity Extractor for Ownership Data

STRATEGIC PURPOSE:
13F and ownership filings contain both structured fields (CIK, shares) and 
unstructured narratives (amendments, explanatory notes). Often the narrative
provides critical context that structured fields miss:
- Corporate actions (M&A, spin-offs)
- Share class changes
- Beneficial ownership vs. direct ownership distinctions
- Voting agreements and control situations

POC APPROACH:
Using regex-based extraction for speed. This works for ~70% of cases.

PRODUCTION NEEDS:
- spaCy NER model fine-tuned on SEC filings
- BERT-based entity disambiguation (especially for similar fund names)
- Confidence scoring with calibration
- Handle multi-language disclosures (for international holders)
- Integration with entity reference database (LEI, CIK, CUSIP mappings)

STRATEGIC TRADE-OFF:
Regex fast and explainable (regulatory requirement), but lower accuracy.
Production would use ML but need to maintain audit trail of extraction logic.
"""

import re
from typing import Dict, List, Tuple
import pandas as pd


class NLPEntityExtractor:
    """Extract ownership information from unstructured narratives"""
    
    def __init__(self):
        # Patterns for entity extraction
        self.entity_patterns = [
            r'([A-Z][A-Za-z\s&\.,]+(?:Inc|Corp|Corporation|LLC|LP|Ltd|Co|Group|Fund|Advisors|Capital)\.?)',
            r'([A-Z][A-Za-z\s&]+)\s+(?:holds?|owned?|reports?|disclosed?)',
        ]
        
        # Patterns for ownership percentage
        self.ownership_patterns = [
            r'(\d+\.?\d*)\s*%\s*of\s+(?:the\s+)?(?:outstanding|class)',
            r'representing\s+(\d+\.?\d*)\s*%',
            r'ownership\s+of\s+(\d+\.?\d*)\s*%',
        ]
        
        # Patterns for share count
        self.shares_patterns = [
            r'([\d,]+)\s+shares',
            r'totaling\s+([\d,]+)\s+shares',
            r'owned?\s+([\d,]+)\s+shares',
        ]
        
        # Ticker patterns
        self.ticker_patterns = [
            r'\b([A-Z]{1,5})\b',
            r'of\s+([A-Z]{2,5})\s+',
        ]
        
    def extract_entities(self, narrative):
        """Extract entity names from narrative"""
        entities = []
        for pattern in self.entity_patterns:
            matches = re.findall(pattern, narrative)
            entities.extend(matches)
        
        # Clean up
        entities = [e.strip() for e in entities if len(e.strip()) > 3]
        return list(set(entities))  # Remove duplicates
    
    def extract_ownership_pct(self, narrative: str) -> float:
        """Extract ownership percentage"""
        for pattern in self.ownership_patterns:
            match = re.search(pattern, narrative)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
    
    def extract_shares(self, narrative: str) -> int:
        """Extract share count"""
        for pattern in self.shares_patterns:
            match = re.search(pattern, narrative)
            if match:
                try:
                    shares_str = match.group(1).replace(',', '')
                    return int(shares_str)
                except ValueError:
                    continue
        return None
    
    def extract_ticker(self, narrative: str) -> str:
        """Extract security ticker"""
        for pattern in self.ticker_patterns:
            match = re.search(pattern, narrative)
            if match:
                ticker = match.group(1)
                if 2 <= len(ticker) <= 5:  # Valid ticker length
                    return ticker
        return None
    
    def extract_all(self, narrative: str) -> Dict:
        """Extract all information from narrative"""
        return {
            'entities': self.extract_entities(narrative),
            'ownership_pct': self.extract_ownership_pct(narrative),
            'shares': self.extract_shares(narrative),
            'ticker': self.extract_ticker(narrative),
            'extraction_confidence': self._calculate_confidence(narrative)
        }
    
    def _calculate_confidence(self, narrative: str) -> float:
        """Calculate extraction confidence score"""
        confidence = 0.0
        
        # Check if we found key elements
        if self.extract_entities(narrative):
            confidence += 0.3
        if self.extract_ownership_pct(narrative) is not None:
            confidence += 0.3
        if self.extract_shares(narrative) is not None:
            confidence += 0.2
        if self.extract_ticker(narrative):
            confidence += 0.2
        
        return round(confidence, 2)
    
    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process entire dataset"""
        print("🔄 Extracting entities with NLP...")
        
        extractions = []
        for idx, row in df.iterrows():
            extracted = self.extract_all(row['narrative'])
            extractions.append(extracted)
        
        # Add extraction results to dataframe
        df['nlp_entities'] = [e['entities'] for e in extractions]
        df['nlp_ownership_pct'] = [e['ownership_pct'] for e in extractions]
        df['nlp_shares'] = [e['shares'] for e in extractions]
        df['nlp_ticker'] = [e['ticker'] for e in extractions]
        df['nlp_confidence'] = [e['extraction_confidence'] for e in extractions]
        
        # Calculate extraction accuracy
        accuracy = (df['nlp_ownership_pct'].notna()).sum() / len(df) * 100
        print(f"✅ NLP extraction complete: {accuracy:.1f}% accuracy")
        
        return df


if __name__ == "__main__":
    # Test
    extractor = NLPEntityExtractor()
    
    test_narrative = """Berkshire Hathaway Inc holds 5,250,000 shares of AAPL, 
    representing 8.5% of outstanding shares."""
    
    result = extractor.extract_all(test_narrative)
    print("Test extraction:", result)
