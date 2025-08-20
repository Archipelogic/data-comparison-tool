"""DataFrame Comparison Framework

A flexible framework for comparing multiple dataframes with statistical testing,
visualization, and comprehensive reporting.
"""

from .core import DataFrameComparison
from .schema import FieldMapping, DataType, SchemaMapper
from .statistics import StatisticalTester
from .visualization import VisualizationEngine
from .reporting import HTMLReportGenerator

__version__ = "1.0.0"

__all__ = [
    "DataFrameComparison",
    "FieldMapping",
    "DataType",
    "SchemaMapper",
    "StatisticalTester",
    "VisualizationEngine",
    "HTMLReportGenerator"
]
