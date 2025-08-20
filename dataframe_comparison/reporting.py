"""HTML report generation for dataframe comparison."""

import json
from typing import Dict, Any, List
from datetime import datetime


class HTMLReportGenerator:
    """Generates comprehensive HTML reports for dataframe comparisons."""
    
    def __init__(self):
        """Initialize report generator with default templates."""
        self.template = self._get_template()
        
    def generate_report(self, results: Dict[str, Any], output_path: str):
        """
        Generate HTML report from comparison results.
        
        Args:
            results: Dictionary containing comparison results
            output_path: Path to save the HTML report
        """
        # Organize data by field
        field_results = self._organize_by_field(results)
        
        html_content = self.template.format(
            title=results.get('title', 'DataFrame Comparison Report'),
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            summary_cards=self._render_summary_cards(results.get('summary_cards', [])),
            field_analyses=self._render_field_analyses(field_results),
            correlation_matrices=self._render_correlation_matrices(results.get('correlation_plots', [])),
            insights=self._render_insights(results.get('key_insights', []))
        )
        
        with open(output_path, 'w') as f:
            f.write(html_content)
            
    def _organize_by_field(self, results: Dict) -> Dict:
        """Organize results by field for grouped display."""
        field_data = {}
        
        # Map test results by field
        for test_result in results.get('test_results', []):
            field_name = test_result['field']
            if field_name not in field_data:
                field_data[field_name] = {'tests': [], 'plot': None}
            field_data[field_name]['tests'] = test_result['tests']
        
        # Map distribution plots by field (assuming plots are in same order as test results)
        for i, plot in enumerate(results.get('distribution_plots', [])):
            if i < len(results.get('test_results', [])):
                field_name = results['test_results'][i]['field']
                if field_name in field_data:
                    field_data[field_name]['plot'] = plot
        
        return field_data
    
    def _render_field_analyses(self, field_results: Dict) -> str:
        """Render field-by-field analysis with plot and tests grouped."""
        if not field_results:
            return "<p>No field analyses available.</p>"
        
        html = ""
        for field_name, data in field_results.items():
            html += f'<div class="field-analysis">'
            html += f'<h3 class="field-title">{field_name}</h3>'
            
            # Render plot first
            if data['plot']:
                html += f'<div class="plot-container">{data["plot"].to_html(include_plotlyjs=False)}</div>'
            
            # Render test results
            if data['tests']:
                html += '<div class="test-results">'
                html += '<h4>Statistical Tests</h4>'
                for test in data['tests']:
                    significance_badge = '<span class="badge significant">✓ Significant</span>' if test.significant else '<span class="badge not-significant">✗ Not Significant</span>'
                    html += f'''
                    <div class="test-item">
                        <div class="test-header">
                            <strong>{test.test_name}</strong>
                            {significance_badge}
                            <span class="alpha-level">α={test.alpha}</span>
                        </div>
                        <div class="test-description">{test.description}</div>
                        <div class="test-stats">
                            <span class="stat">Statistic: {test.statistic:.4f}</span>
                            <span class="stat">p-value: {test.p_value:.4f}</span>
                        </div>
                        <div class="test-interpretation">{test.interpretation}</div>
                    </div>
                    '''
                html += '</div>'
            
            html += '</div>'
        
        return html
    
    def _render_correlation_matrices(self, correlation_plots: List) -> str:
        """Render correlation matrices separately."""
        if not correlation_plots:
            return ""
        
        html = '<h2>Correlation Matrices</h2>'
        html += '''
        <div class="correlation-explanation">
            <h3>Understanding Correlation Matrices</h3>
            <p><strong>Method:</strong> These matrices show <strong>Pearson correlation coefficients</strong> calculated only for <strong>numeric columns</strong>. 
            Non-numeric columns (text, categorical) are automatically excluded from the correlation analysis.</p>
            
            <p>Pearson correlation measures the linear relationship between pairs of numeric variables and ranges from -1 to +1:</p>
            <ul>
                <li><strong>Strong positive correlations (red, close to 1.0):</strong> Variables that increase together linearly</li>
                <li><strong>Strong negative correlations (blue, close to -1.0):</strong> When one increases, the other decreases linearly</li>
                <li><strong>No correlation (white, close to 0):</strong> No linear relationship between variables</li>
            </ul>
            
            <h4>Why Compare Correlation Matrices?</h4>
            <p>Comparing correlation patterns across datasets reveals:</p>
            <ul>
                <li><strong>Structural differences:</strong> Different relationships between variables suggest different underlying processes</li>
                <li><strong>Data quality issues:</strong> Unexpected correlations may indicate data problems</li>
                <li><strong>Feature redundancy:</strong> Highly correlated features (>0.9) might be redundant</li>
                <li><strong>Model implications:</strong> Different correlation structures may require different modeling approaches</li>
            </ul>
            
            <h4>How to Interpret:</h4>
            <ul>
                <li>Look for <strong>consistent patterns</strong> across datasets - these represent stable relationships</li>
                <li>Identify <strong>divergent patterns</strong> - these indicate dataset-specific behaviors</li>
                <li>Check the <strong>diagonal</strong> - should always be 1.0 (perfect self-correlation)</li>
                <li>Consider <strong>correlation strength</strong>: |r| > 0.7 is strong, 0.3-0.7 is moderate, < 0.3 is weak</li>
            </ul>
            
            <p class="note"><strong>Important Notes:</strong><br>
            • Pearson correlation only captures <em>linear</em> relationships - non-linear relationships may exist but not be detected<br>
            • Only numeric columns are included in the correlation matrix<br>
            • High correlation doesn't imply causation - domain knowledge is essential for interpretation</p>
        </div>
        '''
        
        for i, plot in enumerate(correlation_plots):
            dataset_name = f"Dataset {i+1}" if i < 3 else f"Dataset {i+1}"
            html += f'''
            <div class="correlation-matrix-container">
                <h4>{dataset_name} Correlation Matrix</h4>
                <div class="plot-container">{plot.to_html(include_plotlyjs=False)}</div>
                <p class="correlation-note">Hover over cells to see exact correlation values. Diagonal values are always 1.0 (perfect self-correlation).</p>
            </div>
            '''
        
        return html
    
    def _render_summary_cards(self, cards: List[Dict]) -> str:
        """Render summary cards HTML."""
        if not cards:
            return ""
            
        cards_html = ""
        for card in cards:
            cards_html += f"""
            <div class="summary-card">
                <h3>{card['title']}</h3>
                <div class="card-value">{card['value']}</div>
                <div class="card-description">{card['description']}</div>
            </div>
            """
        return cards_html
        
    def _render_test_results(self, test_results: List[Dict]) -> str:
        """Render statistical test results."""
        if not test_results:
            return "<p>No statistical tests performed.</p>"
            
        html = ""
        for result in test_results:
            html += f"<div class='test-result'><h4>{result['field']}</h4><ul>"
            for test in result['tests']:
                significance_indicator = "✓ Significant" if test.significant else "✗ Not Significant"
                html += f"""
                <li>
                    <strong>{test.test_name}</strong> ({significance_indicator} at α={test.alpha})
                    <br><span style="color: #666; font-size: 0.9em;">{test.description}</span>
                    <br><strong>Results:</strong> statistic={test.statistic:.4f}, p-value={test.p_value:.4f}
                    <br><em>{test.interpretation}</em>
                </li>
                """
            html += "</ul></div>"
        return html
        
    def _render_visualizations(self, results: Dict) -> str:
        """Render plotly visualizations."""
        html = ""
        
        # Distribution plots
        for plot in results.get('distribution_plots', []):
            html += f'<div class="plot-container">{plot.to_html(include_plotlyjs=False)}</div>'
            
        # Correlation plots
        for plot in results.get('correlation_plots', []):
            html += f'<div class="plot-container">{plot.to_html(include_plotlyjs=False)}</div>'
            
        return html
        
    def _render_insights(self, insights: List[str]) -> str:
        """Render key insights."""
        if not insights:
            return ""
            
        html = "<ul>"
        for insight in insights:
            html += f"<li>{insight}</li>"
        html += "</ul>"
        return html
        
    def _get_template(self) -> str:
        """Get HTML template."""
        return """<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .plot-container {{
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .correlation-explanation {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .correlation-explanation h4 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .correlation-explanation h5 {{
            color: #34495e;
            margin-top: 15px;
            margin-bottom: 10px;
        }}
        .correlation-guide {{
            margin-top: 15px;
        }}
        .correlation-guide ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        .correlation-guide li {{
            margin: 5px 0;
            line-height: 1.6;
        }}
        .correlation-matrix-container {{
            margin: 30px 0;
        }}
        .correlation-matrix-container h4 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        .correlation-note {{
            font-style: italic;
            color: #6c757d;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .card-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .card-description {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .field-analysis {{
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin: 25px 0;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .field-title {{
            color: #2c3e50;
            font-size: 1.4em;
            margin-top: 0;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
        .test-results {{
            margin-top: 20px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
        }}
        .test-results h4 {{
            margin-top: 0;
            color: #34495e;
            font-size: 1.1em;
        }}
        .test-item {{
            background: white;
            padding: 12px;
            margin: 12px 0;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }}
        .test-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .badge.significant {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        .badge.not-significant {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        .alpha-level {{
            color: #6c757d;
            font-size: 0.9em;
            margin-left: auto;
        }}
        .test-description {{
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
            margin: 8px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 3px;
        }}
        .test-stats {{
            display: flex;
            gap: 20px;
            margin: 8px 0;
            font-family: 'Courier New', monospace;
        }}
        .test-stats .stat {{
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .test-interpretation {{
            color: #495057;
            font-style: italic;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #dee2e6;
        }}
        .insights {{
            background: #e8f4fd;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .insights ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
        .insights li {{
            margin: 8px 0;
        }}
        .metadata {{
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>Generated on: {generation_time}</p>
        
        <h2>Summary</h2>
        <div class="summary-cards">
            {summary_cards}
        </div>
        
        <h2>Field-by-Field Analysis</h2>
        {field_analyses}
        
        {correlation_matrices}
        
        <h2>Key Insights</h2>
        <div class="insights">
            {insights}
        </div>
    </div>
</body>
</html>"""
