"""Core module for dataframe comparison framework."""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from .schema import DataType, FieldMapping, SchemaMapper
from .statistics import StatisticalTester
from .visualization import VisualizationEngine
from .reporting import HTMLReportGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFrameComparison:
    """Main class for comparing multiple dataframes."""
    
    def __init__(self, schema_config: Optional[List[FieldMapping]] = None):
        """
        Initialize dataframe comparison engine.
        
        Args:
            schema_config: Optional list of FieldMapping objects for column standardization
        """
        self.schema_config = schema_config or []
        self.schema_dict = {fm.standard_name: fm for fm in self.schema_config}
        
        self.schema_mapper = SchemaMapper(self.schema_config)
        self.statistical_tester = StatisticalTester()
        self.visualization_engine = VisualizationEngine()
        self.report_generator = HTMLReportGenerator()
        
    def compare_datasets(self,
                        datasets: Dict[str, pd.DataFrame],
                        output_path: str = "comparison_report.html",
                        title: str = None) -> Dict[str, Any]:
        """
        Compare multiple datasets and generate report.
        
        Args:
            datasets: Dictionary mapping dataset names to DataFrames
            output_path: Path to save the HTML report
            title: Optional title for the report
            
        Returns:
            Dictionary containing comparison results
        """
        if not datasets:
            raise ValueError("No datasets provided for comparison")
            
        if title is None:
            title = f"Comparison of {len(datasets)} Datasets"
            
        logger.info(f"Starting comparison of {len(datasets)} datasets")
        
        # Standardize datasets using schema mapper
        standardized_datasets = {}
        for name, df in datasets.items():
            logger.info(f"Standardizing dataset: {name}")
            standardized_df = self.schema_mapper.standardize_dataframe(df)
            # If no columns were renamed, use original dataframe
            if set(standardized_df.columns) == set(df.columns):
                standardized_datasets[name] = df
            else:
                standardized_datasets[name] = standardized_df
            
        # Identify common fields across all datasets
        common_fields = self._identify_common_fields(standardized_datasets)
        logger.info(f"Found {len(common_fields)} common fields for comparison")
        
        # Initialize results
        results = {
            'title': title,
            'datasets': standardized_datasets,
            'common_fields': common_fields,
            'summary_cards': [],
            'key_insights': [],
            'test_results': [],
            'distribution_plots': [],
            'correlation_plots': []
        }
        
        # Generate summary statistics
        results['summary_cards'] = self._generate_summary_cards(standardized_datasets, common_fields)
        
        # Perform statistical tests and generate visualizations
        # Compare each common field
        for field in common_fields:
            # Infer data type from first dataset
            data_type = self._infer_data_type(
                standardized_datasets[list(standardized_datasets.keys())[0]][field]
            )
            logger.debug(f"Field '{field}' detected as {data_type}")
            
            if data_type == DataType.NUMERIC:
                # Statistical tests for numeric data
                field_data = [df[field].dropna() for df in standardized_datasets.values()]
                if all(len(d) > 0 for d in field_data):
                    test_results = self.statistical_tester.compare_numeric_distributions(*field_data)
                    results['test_results'].append({
                        'field': field,
                        'tests': test_results
                    })
                    
                    # Generate distribution plot
                    field_data_dict = {name: df[field].dropna() for name, df in standardized_datasets.items()}
                    plot = self.visualization_engine.create_distribution_overlay(
                        field_data_dict,
                        field,
                        DataType.NUMERIC
                    )
                    results['distribution_plots'].append(plot)
                    
            elif data_type == DataType.CATEGORICAL:
                # Statistical tests for categorical data
                field_data = [df[field].dropna() for df in standardized_datasets.values()]
                if all(len(d) > 0 for d in field_data):
                    test_results = self.statistical_tester.compare_categorical_distributions(*field_data)
                    results['test_results'].append({
                        'field': field,
                        'tests': test_results
                    })
                    
                    # Generate distribution plot
                    field_data_dict = {name: df[field].dropna() for name, df in standardized_datasets.items()}
                    plot = self.visualization_engine.create_distribution_overlay(
                        field_data_dict,
                        field,
                        DataType.CATEGORICAL
                    )
                    results['distribution_plots'].append(plot)
                    
        # Generate correlation heatmaps
        for name, df in standardized_datasets.items():
            corr_plot = self.visualization_engine.create_correlation_heatmap(
                df,
                f"Correlation Matrix: {name}"
            )
            results['correlation_plots'].append(corr_plot)
            
        # Generate key insights
        results['key_insights'] = self._generate_insights(results)
        
        # Generate HTML report
        self.report_generator.generate_report(results, output_path)
        logger.info(f"Report saved to {output_path}")
        
        return results
        
    def _identify_common_fields(self, datasets: Dict[str, pd.DataFrame]) -> List[str]:
        """Identify fields present in all datasets."""
        if not datasets:
            return []
            
        common_fields = set(list(datasets.values())[0].columns)
        for df in datasets.values():
            common_fields &= set(df.columns)
        return sorted(list(common_fields))
        
    def _infer_data_type(self, series: pd.Series) -> DataType:
        """Infer data type from pandas series."""
        if pd.api.types.is_numeric_dtype(series):
            return DataType.NUMERIC
        elif pd.api.types.is_datetime64_any_dtype(series):
            return DataType.DATETIME
        else:
            # Check if categorical (limited unique values)
            unique_ratio = len(series.dropna().unique()) / len(series.dropna())
            if unique_ratio < 0.05:  # Less than 5% unique values
                return DataType.CATEGORICAL
            else:
                return DataType.TEXT
                
    def _generate_summary_cards(self, datasets: Dict[str, pd.DataFrame], 
                               common_fields: List[str]) -> List[Dict]:
        """Generate summary cards for report."""
        cards = []
        
        # Total records card
        total_records = sum(len(df) for df in datasets.values())
        cards.append({
            'title': 'Total Records',
            'value': f'{total_records:,}',
            'description': f'Across {len(datasets)} datasets'
        })
        
        # Common fields card
        cards.append({
            'title': 'Common Fields',
            'value': str(len(common_fields)),
            'description': 'Fields present in all datasets'
        })
        
        # Average missing data card
        total_missing = sum(df.isnull().sum().sum() for df in datasets.values())
        total_cells = sum(df.size for df in datasets.values())
        missing_pct = (total_missing / total_cells * 100) if total_cells > 0 else 0
        cards.append({
            'title': 'Missing Data',
            'value': f'{missing_pct:.1f}%',
            'description': 'Average across all datasets'
        })
        
        # Dataset sizes card
        sizes = [len(df) for df in datasets.values()]
        cards.append({
            'title': 'Dataset Range',
            'value': f'{min(sizes):,} - {max(sizes):,}',
            'description': 'Min to max records'
        })
        
        return cards
        
    def _generate_insights(self, results: Dict) -> List[str]:
        """Generate key insights from comparison results."""
        insights = []
        
        # Significant test results
        significant_fields = []
        for test_result in results['test_results']:
            field = test_result['field']
            for test in test_result['tests']:
                if hasattr(test, 'p_value') and test.p_value < 0.05 and test.p_value >= 0:
                    significant_fields.append(field)
                    break
                    
        if significant_fields:
            insights.append(f"Statistical tests revealed significant differences in: {', '.join(set(significant_fields))}")
            
        # Dataset size variations
        datasets = results['datasets']
        if datasets:
            sizes = {name: len(df) for name, df in datasets.items()}
            max_size = max(sizes.values())
            min_size = min(sizes.values())
            if max_size > min_size * 2:
                insights.append(f"Large size variation detected: {min(sizes, key=sizes.get)} ({min_size:,} records) vs {max(sizes, key=sizes.get)} ({max_size:,} records)")
                
        # Common fields coverage
        common_fields = results['common_fields']
        if datasets and common_fields:
            total_fields = set()
            for df in datasets.values():
                total_fields.update(df.columns)
            coverage = len(common_fields) / len(total_fields) * 100
            insights.append(f"Common field coverage: {coverage:.1f}% ({len(common_fields)} out of {len(total_fields)} total unique fields)")
            
        return insights
