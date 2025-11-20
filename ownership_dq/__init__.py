"""
Ownership Data Quality Assessment POC

A comprehensive data quality framework combining:
- NLP entity extraction
- Graph-based entity resolution
- Hybrid anomaly detection (Isolation Forest + time-series logic)
- Active learning loop with human feedback
- Complete DAMA dimension profiling
- Interactive Bloomberg-style dashboard

Author: Vladimir Volkov
"""

__version__ = "1.0.0"
__author__ = "Vladimir Volkov"

from .synthetic_generator import OwnershipDataGenerator
from .nlp_extractor import NLPEntityExtractor
from .graph_resolver import GraphEntityResolver
from .hybrid_detector import HybridAnomalyDetector
from .active_learning import ActiveLearningLoop
from .dq_profiler import DataQualityProfiler

__all__ = [
    "OwnershipDataGenerator",
    "NLPEntityExtractor",
    "GraphEntityResolver",
    "HybridAnomalyDetector",
    "ActiveLearningLoop",
    "DataQualityProfiler",
]
