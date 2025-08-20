"""Visualization module for dataframe comparison."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional
from .schema import DataType


class VisualizationEngine:
    """Creates interactive visualizations for data comparison."""
    
    def __init__(self):
        """Initialize visualization engine with default settings."""
        self.color_palette = [
            '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#d35400'
        ]
        
    def create_distribution_overlay(self, 
                                  data_dict: Dict[str, np.ndarray],
                                  field_name: str,
                                  data_type: DataType) -> go.Figure:
        """
        Create overlay distribution plot for comparing datasets.
        
        Args:
            data_dict: Dictionary mapping dataset names to arrays
            field_name: Name of the field being compared
            data_type: Type of data (numeric or categorical)
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        for idx, (name, data) in enumerate(data_dict.items()):
            color = self.color_palette[idx % len(self.color_palette)]
            
            # Convert to proper format for Plotly
            if isinstance(data, pd.Series):
                data_values = data.values.tolist()
            elif hasattr(data, 'values'):
                data_values = data.values.tolist()
            elif isinstance(data, np.ndarray):
                data_values = data.tolist()
            else:
                data_values = list(data)
                
            if data_type == DataType.NUMERIC:
                # Create histogram for numeric data
                fig.add_trace(go.Histogram(
                    x=data_values,
                    name=name,
                    opacity=0.7,
                    marker_color=color,
                    nbinsx=30
                ))
            else:
                # Create bar chart for categorical data
                value_counts = pd.Series(data_values).value_counts().head(20)
                fig.add_trace(go.Bar(
                    x=value_counts.index.tolist(),
                    y=value_counts.values.tolist(),
                    name=name,
                    marker_color=color,
                    opacity=0.7
                ))
                
        # Update layout
        fig.update_layout(
            title=f"Distribution Comparison: {field_name}",
            barmode='overlay' if data_type == DataType.NUMERIC else 'group',
            xaxis_title=field_name,
            yaxis_title="Frequency",
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            height=400
        )
        
        return fig
        
    def create_correlation_heatmap(self, df: pd.DataFrame, title: str) -> go.Figure:
        """
        Create correlation heatmap for numeric fields.
        
        Args:
            df: DataFrame with numeric columns
            title: Title for the heatmap
            
        Returns:
            Plotly figure object
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            # Return empty figure if not enough numeric columns
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough numeric columns for correlation",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
            
        corr_matrix = df[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values.tolist(),
            x=corr_matrix.columns.tolist(),
            y=corr_matrix.columns.tolist(),
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2).tolist(),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="",
            yaxis_title="",
            height=500,
            template='plotly_white'
        )
        
        return fig
        
    def create_missing_data_heatmap(self, datasets: Dict[str, pd.DataFrame]) -> go.Figure:
        """
        Create heatmap showing missing data patterns across datasets.
        
        Args:
            datasets: Dictionary mapping dataset names to DataFrames
            
        Returns:
            Plotly figure object
        """
        # Calculate missing percentages
        missing_data = []
        columns = set()
        
        for name, df in datasets.items():
            missing_pct = (df.isnull().sum() / len(df) * 100).round(1)
            missing_data.append(missing_pct)
            columns.update(df.columns)
            
        columns = sorted(list(columns))
        
        # Create matrix
        matrix = []
        dataset_names = []
        
        for name, missing_pct in zip(datasets.keys(), missing_data):
            row = [missing_pct.get(col, 100) for col in columns]
            matrix.append(row)
            dataset_names.append(name)
            
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=columns,
            y=dataset_names,
            colorscale='YlOrRd',
            text=np.array(matrix).round(1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            colorbar=dict(title="Missing %")
        ))
        
        fig.update_layout(
            title="Missing Data Patterns",
            xaxis_title="Fields",
            yaxis_title="Datasets",
            height=300 + len(datasets) * 30,
            template='plotly_white'
        )
        
        return fig
