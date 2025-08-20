#!/usr/bin/env python3
"""
DataFrame Comparison Tool - Command Line Interface
Run comparison analysis on multiple datasets with automatic format detection
"""

import argparse
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import webbrowser
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from dataframe_comparison import DataFrameComparison
from dataframe_comparison.data_loader import DataLoader
from dataframe_comparison.schema import FieldMapping, SchemaMapper


def create_synthetic_datasets(n_rows: int = 1000, n_cols: int = 10) -> dict:
    """Generate synthetic datasets for demonstration"""
    print(f"📊 Generating synthetic datasets ({n_rows} rows × {n_cols} columns)...")
    
    np.random.seed(42)
    
    # Create base columns
    datasets = {}
    
    # Dataset 1: Format A
    n1 = n_rows
    df1 = pd.DataFrame({
        'id': range(1, n1 + 1),
        'value': np.random.gamma(2, 2, n1) * 100,
        'quantity': np.random.poisson(3, n1),
        'category': np.random.choice(['A', 'B', 'C', 'D'], n1, p=[0.4, 0.3, 0.2, 0.1]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n1),
        'date': pd.date_range(start='2024-01-01', periods=n1, freq='h')[:n1],
        'score': np.random.uniform(0, 100, n1),
        'rating': np.random.choice([1, 2, 3, 4, 5], n1, p=[0.05, 0.1, 0.2, 0.4, 0.25])
    })
    
    # Add additional columns if requested
    if n_cols > 8:
        for i in range(8, n_cols):
            if i % 3 == 0:
                df1[f'metric_{i}'] = np.random.normal(100, 15, n1)
            elif i % 3 == 1:
                df1[f'feature_{i}'] = np.random.choice([f'F{j}' for j in range(5)], n1)
            else:
                df1[f'value_{i}'] = np.random.exponential(2, n1) * 10
    
    # Dataset 2: Format B (different names, slight variations)
    n2 = int(n_rows * 1.2)
    df2 = pd.DataFrame({
        'identifier': range(1, n2 + 1),
        'amount': np.random.gamma(2.5, 2, n2) * 100,
        'count': np.random.poisson(4, n2),
        'type': np.random.choice(['A', 'B', 'C', 'E'], n2, p=[0.35, 0.35, 0.2, 0.1]),
        'area': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n2),
        'timestamp': pd.date_range(start='2024-01-01', periods=n2, freq='50min')[:n2],
        'points': np.random.uniform(0, 100, n2),
        'stars': np.random.choice([1, 2, 3, 4, 5], n2, p=[0.03, 0.07, 0.15, 0.45, 0.3])
    })
    
    # Add additional columns
    if n_cols > 8:
        for i in range(8, n_cols):
            if i % 3 == 0:
                df2[f'measure_{i}'] = np.random.normal(105, 18, n2)
            elif i % 3 == 1:
                df2[f'attribute_{i}'] = np.random.choice([f'A{j}' for j in range(5)], n2)
            else:
                df2[f'number_{i}'] = np.random.exponential(2.2, n2) * 10
    
    # Dataset 3: Format C (subset with variations)
    n3 = int(n_rows * 0.8)
    df3 = pd.DataFrame({
        'id_num': range(1, n3 + 1),
        'total': np.random.gamma(2.2, 2, n3) * 100,
        'qty': np.random.poisson(3.5, n3),
        'class': np.random.choice(['A', 'B', 'C'], n3, p=[0.5, 0.3, 0.2]),
        'zone': np.random.choice(['North', 'South', 'East', 'West'], n3),
        'date_time': pd.date_range(start='2024-01-01', periods=n3, freq='90min')[:n3],
        'result': np.random.uniform(0, 100, n3),
        'grade': np.random.choice([1, 2, 3, 4, 5], n3, p=[0.02, 0.08, 0.25, 0.4, 0.25])
    })
    
    # Add additional columns
    if n_cols > 8:
        for i in range(8, n_cols):
            if i % 3 == 0:
                df3[f'stat_{i}'] = np.random.normal(95, 12, n3)
            elif i % 3 == 1:
                df3[f'property_{i}'] = np.random.choice([f'P{j}' for j in range(5)], n3)
            else:
                df3[f'amount_{i}'] = np.random.exponential(1.8, n3) * 10
    
    # Add some missing values
    for df in [df1, df2, df3]:
        mask = np.random.random(df.shape) < 0.05  # 5% missing
        df[mask] = np.nan
    
    datasets['Dataset_A'] = df1
    datasets['Dataset_B'] = df2
    datasets['Dataset_C'] = df3
    
    return datasets


def create_schema_mappings(datasets: dict) -> list:
    """Create schema mappings based on dataset columns"""
    # Define common field mappings
    mappings = [
        FieldMapping(
            standard_name='id',
            aliases=['id', 'identifier', 'id_num', 'key', 'index'],
            data_type='identifier'
        ),
        FieldMapping(
            standard_name='value',
            aliases=['value', 'amount', 'total', 'price', 'cost', 'revenue'],
            data_type='numeric'
        ),
        FieldMapping(
            standard_name='quantity',
            aliases=['quantity', 'count', 'qty', 'units', 'items'],
            data_type='numeric'
        ),
        FieldMapping(
            standard_name='category',
            aliases=['category', 'type', 'class', 'kind', 'group'],
            data_type='categorical'
        ),
        FieldMapping(
            standard_name='region',
            aliases=['region', 'area', 'zone', 'territory', 'location'],
            data_type='categorical'
        ),
        FieldMapping(
            standard_name='date',
            aliases=['date', 'timestamp', 'date_time', 'datetime', 'time'],
            data_type='datetime'
        ),
        FieldMapping(
            standard_name='score',
            aliases=['score', 'points', 'result', 'performance'],
            data_type='numeric'
        ),
        FieldMapping(
            standard_name='rating',
            aliases=['rating', 'stars', 'grade', 'rank'],
            data_type='categorical'
        )
    ]
    
    # Add mappings for additional columns
    for i in range(8, 150):  # Support up to 150 columns
        if i % 3 == 0:
            mappings.append(FieldMapping(
                standard_name=f'metric_{i}',
                aliases=[f'metric_{i}', f'measure_{i}', f'stat_{i}'],
                data_type='numeric'
            ))
        elif i % 3 == 1:
            mappings.append(FieldMapping(
                standard_name=f'feature_{i}',
                aliases=[f'feature_{i}', f'attribute_{i}', f'property_{i}'],
                data_type='categorical'
            ))
        else:
            mappings.append(FieldMapping(
                standard_name=f'value_{i}',
                aliases=[f'value_{i}', f'number_{i}', f'amount_{i}'],
                data_type='numeric'
            ))
    
    return mappings


def save_datasets_to_data_folder(datasets: dict, data_dir: Path):
    """Save synthetic datasets to data folder for testing"""
    data_dir.mkdir(exist_ok=True)
    
    for name, df in datasets.items():
        # Save in multiple formats
        df.to_csv(data_dir / f"{name}.csv", index=False)
        df.to_parquet(data_dir / f"{name}.parquet", index=False)
        
    print(f"✅ Saved {len(datasets)} datasets to {data_dir}")


def load_datasets_from_files(file_paths: list) -> dict:
    """Load datasets from file paths"""
    loader = DataLoader(optimize_dtypes=True)
    datasets = {}
    
    for i, file_path in enumerate(file_paths):
        path = Path(file_path)
        if path.exists():
            try:
                # Use file stem as dataset name
                name = path.stem or f"Dataset_{i+1}"
                datasets[name] = loader.load(path)
                print(f"✅ Loaded {name} from {path} ({datasets[name].shape[0]} rows × {datasets[name].shape[1]} cols)")
            except Exception as e:
                print(f"❌ Failed to load {path}: {e}")
        else:
            print(f"⚠️ File not found: {path}")
    
    return datasets


def load_datasets_from_directory(directory: Path) -> dict:
    """Load all datasets from a directory"""
    loader = DataLoader(optimize_dtypes=True)
    datasets = loader.load_from_directory(directory)
    
    if datasets:
        print(f"✅ Loaded {len(datasets)} datasets from {directory}")
        for name, df in datasets.items():
            print(f"   - {name}: {df.shape[0]} rows × {df.shape[1]} cols")
    
    return datasets


def run_comparison(datasets: dict, output_dir: Path, open_browser: bool = True):
    """Run comparison analysis on datasets"""
    print("\n🔍 Running comparison analysis...")
    print("=" * 60)
    
    # Create schema mappings
    mappings = create_schema_mappings(datasets)
    
    # Initialize comparison engine
    comparison_engine = DataFrameComparison(
        schema_config=mappings
    )
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = output_dir / f"comparison_report_{timestamp}.html"
    
    # Run comparison (this also generates the report)
    results = comparison_engine.compare_datasets(
        datasets, 
        output_path=str(report_path),
        title="DataFrame Comparison Report"
    )
    
    # Print summary
    print("\n📊 Comparison Results Summary:")
    print("-" * 60)
    print(f"   ✓ Datasets compared: {len(datasets)}")
    print(f"   ✓ Common fields found: {len(results.get('common_fields', []))}")
    print(f"   ✓ Statistical tests performed: {sum(len(r.get('tests', [])) for r in results.get('test_results', []))}")
    print(f"   ✓ Visualizations generated: {len(results.get('distribution_plots', []))}")
    
    # Print significant findings
    if 'key_insights' in results:
        insights = results['key_insights']
        if 'significant_differences' in insights and insights['significant_differences']:
            print("\n🔔 Significant differences found in:")
            for field in insights['significant_differences']:
                print(f"   • {field}")
    
    print(f"\n✅ Report saved to: {report_path}")
    
    # Open in browser
    if open_browser:
        print("🌐 Opening report in browser...")
        webbrowser.open(f"file://{report_path.absolute()}")
    
    return results, report_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='DataFrame Comparison Tool - Compare multiple datasets and generate detailed reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with synthetic demo data
  python run_analysis.py --demo
  
  # Compare specific files
  python run_analysis.py data/file1.csv data/file2.parquet data/file3.json
  
  # Load all files from a directory
  python run_analysis.py --dir data/
  
  # Generate larger synthetic datasets
  python run_analysis.py --demo --rows 5000 --cols 50
  
  # Save output to specific directory
  python run_analysis.py --demo --output reports/
        """
    )
    
    parser.add_argument('files', nargs='*', help='Data files to compare')
    parser.add_argument('--demo', action='store_true', help='Use synthetic demo data')
    parser.add_argument('--dir', type=str, help='Load all files from directory')
    parser.add_argument('--rows', type=int, default=1000, help='Number of rows for demo data')
    parser.add_argument('--cols', type=int, default=10, help='Number of columns for demo data')
    parser.add_argument('--output', type=str, default='output', help='Output directory for reports')
    parser.add_argument('--save-demo', action='store_true', help='Save demo datasets to data folder')
    parser.add_argument('--no-browser', action='store_true', help='Do not open report in browser')
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "=" * 60)
    print("   DataFrame Comparison Tool")
    print("=" * 60)
    
    # Load or generate datasets
    datasets = {}
    
    if args.demo:
        # Generate synthetic data
        datasets = create_synthetic_datasets(args.rows, args.cols)
        
        # Optionally save to data folder
        if args.save_demo:
            data_dir = Path('data')
            save_datasets_to_data_folder(datasets, data_dir)
    
    elif args.dir:
        # Load from directory
        dir_path = Path(args.dir)
        if dir_path.exists():
            datasets = load_datasets_from_directory(dir_path)
        else:
            print(f"❌ Directory not found: {dir_path}")
            sys.exit(1)
    
    elif args.files:
        # Load specific files
        datasets = load_datasets_from_files(args.files)
    
    else:
        # No input specified, use demo
        print("ℹ️ No input files specified, using demo data...")
        datasets = create_synthetic_datasets(args.rows, args.cols)
    
    # Check if we have datasets
    if not datasets:
        print("❌ No datasets to compare!")
        sys.exit(1)
    
    # Run comparison
    results, report_path = run_comparison(
        datasets, 
        output_dir, 
        open_browser=not args.no_browser
    )
    
    print("\n" + "=" * 60)
    print("   ✅ Analysis Complete!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
