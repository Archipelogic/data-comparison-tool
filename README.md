# DataFrame Comparison Tool

A powerful Python tool for comparing multiple datasets with automatic schema mapping, statistical analysis, and interactive visualization. The tool automatically detects data formats, performs comprehensive statistical tests, and generates detailed HTML reports with actionable insights.

## Features

### 🔍 Smart Schema Mapping
- Automatic field matching across different naming conventions
- Intelligent type detection and mapping
- Handles multiple dataset schemas seamlessly
- Customizable field mappings for your specific data

### 📊 Statistical Analysis
- **Distribution Tests**: Kolmogorov-Smirnov, Anderson-Darling
- **Group Comparisons**: Kruskal-Wallis, Chi-square
- **Correlation Analysis**: Pearson correlation for numeric columns only
- **Detailed Interpretations**: Practical explanations of test results

### 📈 Visualizations
- Interactive distribution plots with 0.5 opacity for better overlay visibility
- Correlation heatmaps with color-coded strength indicators
- Missing data patterns visualization
- All visualizations are interactive (powered by Plotly)

### 📁 Multi-Format Support
- CSV, TSV
- JSON, JSONL (including nested structures)
- Parquet
- Excel (XLSX, XLS)
- Automatic format detection

### 📝 Comprehensive Reporting
- Beautiful HTML reports with all findings
- Statistical test results with interpretations
- Key insights and recommendations
- Automatic browser opening for immediate viewing

## Quick Start for New Projects

### Step 1: Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dataframe-comparison-tool.git
cd dataframe-comparison-tool

# Option A: Automated setup (Recommended)
./setup_and_run.sh

# Option B: Manual setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
mkdir -p data output
```

### Step 2: Place Your Data

Put your datasets in the `data/` folder. Supported formats:
- CSV/TSV files
- JSON/JSONL files
- Parquet files
- Excel files (XLSX/XLS)

### Step 3: Run the Comparison

```bash
# Compare all files in data/ directory
python3 run_analysis.py --dir data/

# Compare specific files
python3 run_analysis.py data/file1.csv data/file2.json data/file3.parquet

# Test with demo data first
python3 run_analysis.py --demo
```

## Customization Guide

### 1. Loading Data from Different Sources

**Location:** `run_analysis.py` (lines 65-85)

```python
# Current implementation loads all files from a directory
if args.dir:
    loader = DataLoader()
    datasets = loader.load_directory(args.dir)

# To customize for specific data sources, modify:
def load_custom_data():
    import pandas as pd
    loader = DataLoader()
    datasets = {}
    
    # Load from local data folder
    datasets['Sales_Data'] = loader.load_file('data/sales.csv')
    datasets['Customer_Data'] = loader.load_file('data/customers.parquet')
    datasets['Product_Data'] = loader.load_file('data/products.json')
    
    # Load from S3 (using pandas directly)
    datasets['S3_Data'] = pd.read_csv('s3://my-bucket/path/to/file.csv')
    datasets['S3_Parquet'] = pd.read_parquet('s3://my-bucket/path/to/file.parquet')
    
    # Note: For S3 access, ensure AWS credentials are configured
    # via AWS CLI, environment variables, or IAM roles
    
    return datasets
```

### 2. Selecting Specific Columns for Comparison

**Location:** `run_analysis.py` (lines 231-245)

```python
# Current implementation uses all columns
# To select specific columns, modify the schema config generation:

def create_custom_schema():
    # Define which columns to compare
    columns_to_compare = ['price', 'quantity', 'category', 'date']
    
    # Create schema mappings for these columns
    schema_config = []
    for col in columns_to_compare:
        schema_config.append(FieldMapping(
            standard_name=col,
            data_type=DataType.NUMERIC if col in ['price', 'quantity'] else DataType.CATEGORICAL,
            aliases=[col, col.lower(), col.upper()],
            description=f"Comparing {col} field"
        ))
    return schema_config

# Then use it in the comparison:
schema_config = create_custom_schema()
comparator = DataFrameComparison(schema_config)
```

### 3. Configuring Schema Standardization

**Location:** `dataframe_comparison/schema.py` (lines 10-38)

```python
# Define custom field mappings for your data
from dataframe_comparison.schema import FieldMapping, DataType

# Example: Map different column names to standard names
custom_mappings = [
    FieldMapping(
        standard_name="customer_id",
        data_type=DataType.CATEGORICAL,
        aliases=["cust_id", "customerId", "client_id", "user_id"],
        description="Unique customer identifier"
    ),
    FieldMapping(
        standard_name="revenue",
        data_type=DataType.NUMERIC,
        aliases=["sales", "income", "total_sales", "amount"],
        description="Revenue/sales amount"
    ),
    FieldMapping(
        standard_name="purchase_date",
        data_type=DataType.DATETIME,
        aliases=["date", "order_date", "transaction_date", "created_at"],
        description="Date of purchase"
    )
]

# Use in comparison
from dataframe_comparison import DataFrameComparison
comparator = DataFrameComparison(custom_mappings)
```

### 4. Complete Custom Implementation Example

**Create a new file:** `custom_analysis.py`

```python
import pandas as pd
from dataframe_comparison import DataFrameComparison
from dataframe_comparison.schema import FieldMapping, DataType
from dataframe_comparison.data_loader import DataLoader

def run_custom_analysis():
    # Step 1: Load your specific data
    loader = DataLoader()
    datasets = {}
    
    # Load from local files
    datasets['Q1_Sales'] = pd.read_csv('data/q1_sales.csv')
    datasets['Q2_Sales'] = pd.read_excel('data/q2_sales.xlsx')
    datasets['Q3_Sales'] = loader.load_file('data/q3_sales.json')
    
    # Or load from S3
    # datasets['S3_Sales'] = pd.read_csv('s3://my-bucket/sales/q4_sales.csv')
    
    # Step 2: Select only columns you want to compare
    columns_to_keep = ['product_id', 'sales_amount', 'quantity', 'region']
    for name in datasets:
        datasets[name] = datasets[name][columns_to_keep]
    
    # Step 3: Define standardization mappings
    schema_config = [
        FieldMapping(
            standard_name="product_id",
            data_type=DataType.CATEGORICAL,
            aliases=["product_id", "sku", "item_id"],
            description="Product identifier"
        ),
        FieldMapping(
            standard_name="sales_amount",
            data_type=DataType.NUMERIC,
            aliases=["sales_amount", "revenue", "total"],
            description="Sales amount in dollars"
        ),
        FieldMapping(
            standard_name="quantity",
            data_type=DataType.NUMERIC,
            aliases=["quantity", "qty", "units_sold"],
            description="Number of units sold"
        ),
        FieldMapping(
            standard_name="region",
            data_type=DataType.CATEGORICAL,
            aliases=["region", "area", "territory"],
            description="Sales region"
        )
    ]
    
    # Step 4: Run comparison
    comparator = DataFrameComparison(schema_config)
    comparator.compare_datasets(
        datasets,
        title="Quarterly Sales Comparison"
    )
    
    print("✅ Report generated in output/ folder")

if __name__ == "__main__":
    run_custom_analysis()
```

## Command Line Usage

```bash
# Quick demo
python3 run_analysis.py --demo

# Compare your data files
python3 run_analysis.py --dir data/

# Compare specific files
python3 run_analysis.py file1.csv file2.json file3.parquet

# Large demo dataset
python3 run_analysis.py --demo --rows 5000 --cols 50

# Save demo data for testing
python3 run_analysis.py --demo --save-demo

# Disable browser auto-open
python3 run_analysis.py --demo --no-open
```

## Python API

```python
import pandas as pd
from dataframe_comparison import DataFrameComparison
from dataframe_comparison.data_loader import DataLoader
from dataframe_comparison.schema import FieldMapping, DataType

# Load datasets
loader = DataLoader()
datasets = {
    'dataset1': loader.load_file('data/file1.csv'),
    'dataset2': loader.load_file('data/file2.parquet'),
    'dataset3': pd.read_csv('s3://my-bucket/file3.csv')  # Load from S3
}

# Define schema mappings (optional - uses auto-detection if not provided)
schema_config = [
    FieldMapping(
        standard_name="amount",
        data_type=DataType.NUMERIC,
        aliases=["amount", "total", "value"],
        description="Transaction amount"
    )
]

# Run comparison
comparator = DataFrameComparison(schema_config)
comparator.compare_datasets(
    datasets,
    title="My Data Comparison"
)
```

## Project Structure

```
data-comparison-tool/
├── dataframe_comparison/       # Main package
│   ├── __init__.py
│   ├── core.py                # Core comparison logic
│   ├── data_loader.py         # Multi-format data loader
│   ├── schema.py              # Schema mapping
│   ├── statistics.py          # Statistical tests
│   ├── visualization.py       # Plot generation
│   └── reporting.py           # HTML report generation
├── data/                      # Input data directory
├── output/                    # Generated reports
├── run_analysis.py           # CLI interface
├── setup_and_run.sh          # Setup and run script
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## Example Output

The tool generates comprehensive HTML reports including:

1. **Dataset Overview**
   - Shape and size comparison
   - Missing data analysis
   - Data type distribution

2. **Statistical Test Results**
   - Test statistics and p-values
   - Practical interpretations
   - Recommendations for data handling

3. **Distribution Analysis**
   - Visual comparisons across datasets
   - Interactive plots for exploration
   - Outlier detection

4. **Correlation Analysis**
   - Side-by-side correlation matrices
   - Pattern identification
   - Feature relationship insights

5. **Key Insights**
   - Automated finding detection
   - Significant differences highlighted
   - Actionable recommendations

## Statistical Tests Explained

### Kolmogorov-Smirnov Test
Tests if numeric distributions are similar. Low p-values indicate different distributions.

### Anderson-Darling Test
More sensitive than KS test, especially for tail differences. Useful for quality control.

### Kruskal-Wallis Test
Non-parametric test for comparing medians across groups. Robust to outliers.

### Chi-Square Test
Tests independence between categorical variables. Identifies association patterns.

## Dependencies

- **Core**: pandas, numpy, scipy, plotly, jinja2
- **Data Formats**: openpyxl (Excel), pyarrow (Parquet)
- **S3 Support**: s3fs (install with `pip install s3fs` for S3 access)
- **Python**: 3.8 or higher

## Configuration

The tool uses sensible defaults but can be customized:

```python
# In run_analysis.py or your script
comparison = DataFrameComparison(
    alpha=0.05,                    # Significance level
    correlation_threshold=0.7,      # High correlation threshold
    missing_threshold=0.1,          # Missing data warning threshold
    n_bins=50                       # Histogram bins
)
```

## Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **Permission denied on setup_and_run.sh**
   ```bash
   chmod +x setup_and_run.sh
   ```

3. **Report doesn't open automatically**
   - Check if running in SSH/remote environment
   - Use `--no-browser` flag and manually open the HTML file

4. **Memory issues with large datasets**
   - Use the data loader's optimization features
   - Process datasets in chunks
   - Consider using Parquet format for better compression

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

### Development Setup

```bash
# Install development dependencies
pip install pytest black flake8

# Run tests
pytest tests/

# Format code
black dataframe_comparison/

# Check code style
flake8 dataframe_comparison/
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with pandas, numpy, scipy, and plotly
- Inspired by the need for better data comparison tools
- Enhanced with practical statistical interpretations

## Contact

For questions or support, please open an issue on GitHub.
