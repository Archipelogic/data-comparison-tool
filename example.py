"""Example usage of the DataFrame Comparison Framework."""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from dataframe_comparison import (
    DataFrameComparison,
    FieldMapping,
    DataType
)


def generate_sample_data():
    """Generate sample datasets for demonstration."""
    np.random.seed(42)
    
    # Dataset 1: Sales data format A
    n1 = 1000
    df1 = pd.DataFrame({
        'product_id': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005'], n1),
        'sale_amount': np.random.gamma(2, 2, n1) * 100,
        'quantity': np.random.poisson(3, n1),
        'customer_type': np.random.choice(['Individual', 'Business', 'Government'], n1, p=[0.6, 0.3, 0.1]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n1),
        'sale_date': pd.date_range(start='2023-01-01', periods=n1, freq='H')[:n1],
        'discount_pct': np.random.uniform(0, 30, n1),
        'rating': np.random.choice([1, 2, 3, 4, 5], n1, p=[0.05, 0.1, 0.2, 0.4, 0.25])
    })
    
    # Dataset 2: Sales data format B (different column names)
    n2 = 1200
    df2 = pd.DataFrame({
        'prod_code': np.random.choice(['P001', 'P002', 'P003', 'P004', 'P005', 'P006'], n2),
        'revenue': np.random.gamma(2.5, 2, n2) * 100,
        'units_sold': np.random.poisson(4, n2),
        'client_category': np.random.choice(['Individual', 'Business', 'Enterprise'], n2, p=[0.5, 0.35, 0.15]),
        'territory': np.random.choice(['North', 'South', 'East', 'West', 'Central'], n2),
        'transaction_date': pd.date_range(start='2023-01-01', periods=n2, freq='50min')[:n2],
        'discount': np.random.uniform(0, 25, n2),
        'satisfaction_score': np.random.choice([1, 2, 3, 4, 5], n2, p=[0.03, 0.07, 0.15, 0.45, 0.3])
    })
    
    # Dataset 3: Sales data format C
    n3 = 800
    df3 = pd.DataFrame({
        'item_id': np.random.choice(['P001', 'P002', 'P003', 'P004'], n3),
        'total_sale': np.random.gamma(2.2, 2, n3) * 100,
        'qty': np.random.poisson(3.5, n3),
        'buyer_type': np.random.choice(['Individual', 'Corporate'], n3, p=[0.65, 0.35]),
        'sales_region': np.random.choice(['North', 'South', 'East', 'West'], n3),
        'order_date': pd.date_range(start='2023-01-01', periods=n3, freq='90min')[:n3],
        'promo_discount': np.random.uniform(0, 35, n3),
        'review_rating': np.random.choice([1, 2, 3, 4, 5], n3, p=[0.02, 0.08, 0.25, 0.4, 0.25])
    })
    
    # Add some missing values randomly
    for df in [df1, df2, df3]:
        mask = np.random.random(df.shape) < 0.05  # 5% missing values
        df[mask] = np.nan
    
    return {
        'Sales_Format_A': df1,
        'Sales_Format_B': df2,
        'Sales_Format_C': df3
    }


def main():
    """Main example demonstrating dataframe comparison."""
    
    print("=" * 80)
    print("DataFrame Comparison Framework - Example")
    print("=" * 80)
    
    # Generate sample datasets
    print("\n1. Generating sample datasets...")
    datasets = generate_sample_data()
    
    # Display dataset summaries
    print("\n2. Dataset Summaries:")
    print("-" * 60)
    for name, df in datasets.items():
        print(f"\n{name}:")
        print(f"  - Shape: {df.shape}")
        print(f"  - Columns: {list(df.columns)}")
        print(f"  - Missing values: {df.isnull().sum().sum()}")
    
    # Define schema mappings for standardization
    schema_config = [
        FieldMapping(
            standard_name="product_id",
            aliases=["prod_code", "item_id", "product_code"],
            data_type=DataType.CATEGORICAL
        ),
        FieldMapping(
            standard_name="sale_amount",
            aliases=["revenue", "total_sale", "sales_amount", "amount"],
            data_type=DataType.NUMERIC
        ),
        FieldMapping(
            standard_name="quantity",
            aliases=["units_sold", "qty", "units", "count"],
            data_type=DataType.NUMERIC
        ),
        FieldMapping(
            standard_name="customer_type",
            aliases=["client_category", "buyer_type", "customer_category"],
            data_type=DataType.CATEGORICAL
        ),
        FieldMapping(
            standard_name="region",
            aliases=["territory", "sales_region", "area", "zone"],
            data_type=DataType.CATEGORICAL
        ),
        FieldMapping(
            standard_name="sale_date",
            aliases=["transaction_date", "order_date", "date"],
            data_type=DataType.DATETIME
        ),
        FieldMapping(
            standard_name="discount",
            aliases=["discount_pct", "promo_discount", "discount_percent"],
            data_type=DataType.NUMERIC
        ),
        FieldMapping(
            standard_name="rating",
            aliases=["satisfaction_score", "review_rating", "score"],
            data_type=DataType.NUMERIC
        )
    ]
    
    # Create output folder if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nCreated output directory: {output_dir}")
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"comparison_report_{timestamp}.html"
    output_path = os.path.join(output_dir, output_filename)
    
    # Initialize comparison engine
    print("\n3. Initializing comparison engine with schema mappings...")
    comparison_engine = DataFrameComparison(schema_config=schema_config)
    
    # Run comparison
    print("\n4. Running dataset comparison...")
    print("   This will:")
    print("   - Standardize column names across datasets")
    print("   - Perform statistical tests on distributions")
    print("   - Generate interactive visualizations")
    print("   - Create comprehensive HTML report")
    
    results = comparison_engine.compare_datasets(
        datasets,
        output_path=output_path,
        title="Sales Data Comparison Analysis"
    )
    
    # Display results summary
    print("\n5. Comparison Results Summary:")
    print("-" * 60)
    print(f"   - Datasets compared: {len(results['datasets'])}")
    print(f"   - Common fields found: {len(results['common_fields'])}")
    print(f"   - Statistical tests performed: {len(results['test_results'])}")
    print(f"   - Distribution plots generated: {len(results['distribution_plots'])}")
    print(f"   - Correlation matrices generated: {len(results['correlation_plots'])}")
    
    # Display p-values for tests that show significant differences
    print("\n6. Statistical Test Results (p-values < 0.05):")
    print("-" * 60)
    
    for test_result in results['test_results']:
        field_name = test_result['field']
        tests = test_result['tests']
        significant_tests = [
            test for test in tests 
            if test.p_value < 0.05 and test.p_value >= 0
        ]
        
        if significant_tests:
            print(f"\n   {field_name}:")
            for test in significant_tests:
                print(f"      - {test.test_name}: p={test.p_value:.4f}")
                print(f"        Description: {test.description}")
                print(f"        Result: {test.interpretation}")
    
    # Key insights
    print("\n7. Key Insights:")
    print("-" * 60)
    for insight in results['key_insights'][:5]:  # Show top 5 insights
        print(f"   - {insight}")
    
    print("\n" + "=" * 80)
    print(f"✅ Analysis complete! Report saved to: {output_path}")
    print("   Open the HTML file in your browser to view interactive visualizations.")
    print("=" * 80)
    
    return results


if __name__ == "__main__":
    main()
