"""
Simplified data loader with automatic format detection for multiple file types
"""

import os
import json
import pandas as pd
from typing import Union, Optional, List, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Data loader with automatic format detection
    
    Features:
    - Auto-detects file format (CSV, TSV, JSON, JSONL, Parquet, Excel)
    - Handles nested JSON structures
    - Schema inference and validation
    - Automatic type optimization
    """
    
    SUPPORTED_FORMATS = {'.csv', '.tsv', '.json', '.jsonl', '.parquet', '.xlsx', '.xls'}
    
    def __init__(self, optimize_dtypes: bool = True):
        """
        Initialize DataLoader
        
        Args:
            optimize_dtypes: Automatically optimize data types for memory efficiency
        """
        self.optimize_dtypes = optimize_dtypes
        self.logger = logger
        
    def load(self, 
             file_path: Union[str, Path],
             optimize_dtypes: Optional[bool] = None,
             **kwargs) -> pd.DataFrame:
        """
        Load data from file with automatic format detection
        
        Args:
            file_path: Path to the file
            optimize_dtypes: Optimize data types for memory efficiency
            **kwargs: Additional arguments for read functions
            
        Returns:
            DataFrame
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect format
        file_format = self._detect_format(file_path)
        
        # Load data
        df = self._load_file(file_path, file_format, **kwargs)
        
        # Optimize dtypes if enabled
        if optimize_dtypes if optimize_dtypes is not None else self.optimize_dtypes:
            df = self._optimize_dtypes(df)
            
        return df
    
    def load_multiple(self, 
                     file_paths: List[Union[str, Path]],
                     names: Optional[List[str]] = None,
                     **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files
        
        Args:
            file_paths: List of file paths
            names: Optional names for the datasets
            **kwargs: Additional arguments for read functions
            
        Returns:
            Dictionary mapping names to DataFrames
        """
        datasets = {}
        
        if names is None:
            names = [Path(fp).stem for fp in file_paths]
        
        for name, file_path in zip(names, file_paths):
            try:
                datasets[name] = self.load(file_path, **kwargs)
                logger.info(f"Successfully loaded: {name} from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
                
        return datasets
    
    def load_from_directory(self, 
                          directory: Union[str, Path],
                          pattern: str = "*",
                          **kwargs) -> Dict[str, pd.DataFrame]:
        """
        Load all matching files from a directory
        
        Args:
            directory: Directory path
            pattern: File pattern (e.g., "*.csv")
            **kwargs: Additional arguments for read functions
            
        Returns:
            Dictionary mapping file names to DataFrames
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all matching files
        files = list(directory.glob(pattern))
        
        # Filter for supported formats
        supported_files = [f for f in files if f.suffix.lower() in self.SUPPORTED_FORMATS]
        
        if not supported_files:
            logger.warning(f"No supported files found in {directory} matching pattern {pattern}")
            return {}
        
        return self.load_multiple(supported_files, **kwargs)
        
    def _detect_format(self, file_path: Path) -> str:
        """Detect file format from extension"""
        suffix = file_path.suffix.lower()
        
        if suffix not in self.SUPPORTED_FORMATS:
            # Try to detect from content
            with open(file_path, 'rb') as f:
                header = f.read(100)
                if b'PAR1' in header:
                    return '.parquet'
                elif b',' in header or b'\t' in header:
                    return '.csv'
                elif header.startswith(b'{') or header.startswith(b'['):
                    return '.json'
            
            raise ValueError(f"Unsupported format: {suffix}")
        
        return suffix
    
    def _load_file(self, file_path: Path, file_format: str, **kwargs) -> pd.DataFrame:
        """Load data based on file format"""
        
        if file_format == '.csv':
            return pd.read_csv(file_path, **kwargs)
        elif file_format == '.tsv':
            return pd.read_csv(file_path, sep='\t', **kwargs)
        elif file_format == '.parquet':
            return pd.read_parquet(file_path, **kwargs)
        elif file_format == '.json':
            # Try regular JSON first
            try:
                return pd.read_json(file_path, **kwargs)
            except (ValueError, json.JSONDecodeError):
                # Try as nested JSON
                return self._load_nested_json(file_path)
        elif file_format == '.jsonl':
            return pd.read_json(file_path, lines=True, **kwargs)
        elif file_format in ['.xlsx', '.xls']:
            return pd.read_excel(file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
    
    def _load_nested_json(self, file_path: Path) -> pd.DataFrame:
        """Load and flatten nested JSON"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Helper function to flatten nested structures
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    if len(v) > 0 and isinstance(v[0], dict):
                        # List of dicts - create numbered entries
                        for i, item in enumerate(v[:10]):  # Limit to first 10 items
                            items.extend(flatten_dict(item, f"{new_key}_{i}", sep=sep).items())
                    else:
                        items.append((new_key, str(v)))
                else:
                    items.append((new_key, v))
            return dict(items)
        
        # Handle different JSON structures
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            data = [{'value': data}]
        
        # Flatten each record
        flattened_records = []
        for record in data:
            if isinstance(record, dict):
                flat_record = flatten_dict(record)
            else:
                flat_record = {'value': record}
            flattened_records.append(flat_record)
        
        return pd.DataFrame(flattened_records)
    
    def _optimize_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for memory efficiency"""
        
        for col in df.columns:
            col_type = df[col].dtype
            
            # Skip if already optimized or is datetime
            if col_type == 'category' or 'datetime' in str(col_type):
                continue
            
            # Optimize numeric types
            if col_type != 'object':
                try:
                    # Try to downcast numeric types
                    if 'int' in str(col_type):
                        df[col] = pd.to_numeric(df[col], downcast='integer')
                    elif 'float' in str(col_type):
                        df[col] = pd.to_numeric(df[col], downcast='float')
                except:
                    pass
            
            # Convert low-cardinality strings to category
            elif col_type == 'object':
                try:
                    num_unique = df[col].nunique()
                    num_total = len(df[col])
                    if num_total > 0 and num_unique / num_total < 0.5:
                        df[col] = df[col].astype('category')
                except:
                    pass
        
        return df
    
    def get_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get DataFrame information"""
        return {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'null_counts': df.isnull().sum().to_dict()
        }
    
    def save(self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to file"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.csv':
            df.to_csv(file_path, index=False, **kwargs)
        elif suffix == '.parquet':
            df.to_parquet(file_path, index=False, **kwargs)
        elif suffix == '.json':
            df.to_json(file_path, **kwargs)
        elif suffix in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported format for saving: {suffix}")
