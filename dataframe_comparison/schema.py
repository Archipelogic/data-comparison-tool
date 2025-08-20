"""Schema mapping and field configuration for dataframe comparison."""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DataType(Enum):
    """Data type enumeration for field classification."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class FieldMapping:
    """Defines mapping between different field name variations."""
    standard_name: str
    aliases: List[str]
    data_type: DataType = DataType.UNKNOWN
    description: Optional[str] = None


class SchemaMapper:
    """Maps varied column names to standardized names for comparison."""
    
    def __init__(self, config: Optional[List[FieldMapping]] = None):
        """
        Initialize schema mapper with field mappings.
        
        Args:
            config: List of FieldMapping objects defining standard names and aliases
        """
        self.config = config or []
        self._build_mapping_dict()
        
    def _build_mapping_dict(self):
        """Build internal mapping dictionaries for efficient lookup."""
        self.mapping_dict = {}
        self.standard_fields = {}
        
        for mapping in self.config:
            self.standard_fields[mapping.standard_name] = mapping
            for alias in mapping.aliases:
                self.mapping_dict[alias.lower()] = mapping.standard_name
                
    def standardize_dataframe(self, df):
        """
        Standardize dataframe column names based on mappings.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with standardized column names
        """
        import pandas as pd
        
        df_copy = df.copy()
        rename_map = {}
        
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in self.mapping_dict:
                rename_map[col] = self.mapping_dict[col_lower]
            else:
                # Try fuzzy matching for close matches
                best_match = self._find_best_match(col_lower)
                if best_match:
                    rename_map[col] = best_match
                    
        if rename_map:
            df_copy = df_copy.rename(columns=rename_map)
            
        return df_copy
        
    def _find_best_match(self, column_name: str, threshold: float = 0.8) -> Optional[str]:
        """Find best matching standard field using fuzzy matching."""
        from difflib import SequenceMatcher
        
        best_score = 0
        best_match = None
        
        for standard_name in self.standard_fields:
            score = SequenceMatcher(None, column_name, standard_name.lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = standard_name
                
        # Also check aliases
        for alias, standard_name in self.mapping_dict.items():
            score = SequenceMatcher(None, column_name, alias).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = standard_name
                
        if best_match:
            import logging
            logging.info(f"Fuzzy matched '{column_name}' to '{best_match}'")
            
        return best_match
