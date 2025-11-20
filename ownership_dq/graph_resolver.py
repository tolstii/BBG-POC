"""
Graph-Based Entity Resolution

BUSINESS PROBLEM:
Same entity appears in ownership data with dozens of variations:
- "BlackRock Inc." vs "BLACKROCK INC" vs "BlackRock Fund Advisors"
- "JP Morgan Chase & Co" vs "JPMorgan Chase & Co." vs "JPM Chase"
- Typos, punctuation differences, legal entity structure changes

This causes:
- Position aggregation errors (understating actual ownership)
- False anomalies when "new" entity is actually a known holder
- Compliance issues (missing 13D/13G disclosure thresholds)

GRAPH APPROACH RATIONALE:
Traditional fuzzy matching treats each pair independently. Graph approach:
- Finds transitive relationships (A similar to B, B similar to C → cluster ABC)
- Scales better for large entity universe (thousands of holders)
- Visual representation helps data stewards understand resolution logic

POC SIMPLIFICATION:
Using basic string similarity (SequenceMatcher). Production needs:
- Graph Neural Networks (GNN) or transformer-based matching
- Bloomberg/FactSet LEI/CIK reference data integration
- Multi-attribute matching (CIK + name + address)
- Historical resolution audit trail (who approved mapping, when)

PRODUCTION INSIGHT:
~30% of entity resolution errors come from corporate actions (M&A, spin-offs, 
name changes). Need event-driven updates to reference data.
"""

import pandas as pd
import networkx as nx
from difflib import SequenceMatcher
from typing import Dict, List, Tuple
import re


class GraphEntityResolver:
    """Resolve entity name variations using graph-based matching"""
    
    def __init__(self, similarity_threshold: float = 0.80):
        self.similarity_threshold = similarity_threshold
        self.graph = nx.Graph()
        self.canonical_map = {}
        
    def _normalize_name(self, name: str) -> str:
        """Normalize entity name for comparison"""
        # Convert to lowercase
        name = name.lower()
        
        # Remove common suffixes
        suffixes = ['inc', 'incorporated', 'corp', 'corporation', 'llc', 'lp', 'ltd', 'co', 'company']
        for suffix in suffixes:
            name = re.sub(rf'\b{suffix}\.?\b', '', name)
        
        # Remove punctuation
        name = re.sub(r'[.,&\-]', ' ', name)
        
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        return name.strip()
    
    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two entity names"""
        norm1 = self._normalize_name(name1)
        norm2 = self._normalize_name(name2)
        
        # Use SequenceMatcher for fuzzy matching
        ratio = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Bonus for exact substring matches
        if norm1 in norm2 or norm2 in norm1:
            ratio = min(1.0, ratio + 0.1)
        
        return ratio
    
    def build_entity_graph(self, entity_names: List[str], canonical_entities: List[str] = None):
        """Build graph connecting similar entity names"""
        print("🕸️ Building entity resolution graph...")
        
        # Add all entities as nodes
        for name in entity_names:
            self.graph.add_node(name, normalized=self._normalize_name(name))
        
        # Add edges between similar entities
        entities_list = list(entity_names)
        edge_count = 0
        
        for i, name1 in enumerate(entities_list):
            for name2 in entities_list[i+1:]:
                similarity = self._calculate_similarity(name1, name2)
                
                if similarity >= self.similarity_threshold:
                    self.graph.add_edge(name1, name2, weight=similarity)
                    edge_count += 1
        
        print(f"   Nodes: {self.graph.number_of_nodes()}")
        print(f"   Edges: {edge_count}")
        
        # Find connected components (entity clusters)
        self._identify_canonical_entities()
        
    def _identify_canonical_entities(self):
        """Identify canonical form for each entity cluster"""
        components = list(nx.connected_components(self.graph))
        
        print(f"   Found {len(components)} unique entities")
        
        for component in components:
            # Choose the most common or shortest name as canonical
            names = list(component)
            
            # Prefer official-looking names (with Inc, Corp, etc.)
            official_names = [n for n in names if any(suffix in n.lower() 
                            for suffix in ['inc', 'corp', 'corporation'])]
            
            if official_names:
                canonical = min(official_names, key=len)  # Shortest official name
            else:
                canonical = min(names, key=len)  # Shortest name
            
            # Map all variations to canonical
            for name in names:
                self.canonical_map[name] = canonical
    
    def resolve_entity(self, entity_name: str) -> str:
        """Resolve entity name to canonical form"""
        # Direct lookup
        if entity_name in self.canonical_map:
            return self.canonical_map[entity_name]
        
        # Find best match in existing entities
        best_match = None
        best_score = 0.0
        
        for canonical in set(self.canonical_map.values()):
            score = self._calculate_similarity(entity_name, canonical)
            if score > best_score and score >= self.similarity_threshold:
                best_score = score
                best_match = canonical
        
        return best_match if best_match else entity_name
    
    def process_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process dataset and resolve all entities"""
        # Get all unique entity names
        unique_entities = df['entity_name_raw'].unique().tolist()
        
        # Build graph
        self.build_entity_graph(unique_entities)
        
        # Resolve entities
        df['entity_resolved'] = df['entity_name_raw'].apply(self.resolve_entity)
        
        # Calculate resolution stats
        original_count = df['entity_name_raw'].nunique()
        resolved_count = df['entity_resolved'].nunique()
        reduction_pct = (1 - resolved_count / original_count) * 100
        
        print(f"✅ Entity resolution complete:")
        print(f"   Original entities: {original_count}")
        print(f"   Resolved entities: {resolved_count}")
        print(f"   Reduction: {reduction_pct:.1f}%")
        
        return df
    
    def get_resolution_report(self) -> pd.DataFrame:
        """Generate entity resolution report"""
        report_data = []
        
        for original, canonical in self.canonical_map.items():
            if original != canonical:
                report_data.append({
                    'original_name': original,
                    'canonical_name': canonical,
                    'similarity': self._calculate_similarity(original, canonical)
                })
        
        return pd.DataFrame(report_data).sort_values('canonical_name')


if __name__ == "__main__":
    # Test
    resolver = GraphEntityResolver(similarity_threshold=0.80)
    
    test_names = [
        "Berkshire Hathaway Inc",
        "BERKSHIRE HATHAWAY INC.",
        "Berkshire Hathaway",
        "Vanguard Group Inc",
        "The Vanguard Group, Inc."
    ]
    
    resolver.build_entity_graph(test_names)
    
    for name in test_names:
        resolved = resolver.resolve_entity(name)
        print(f"{name} → {resolved}")
