"""
Data handling module for LlamaVis.

This module provides classes and functions for data validation,
transformation, and preprocessing for different visualization types.
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any, Optional, Tuple, Callable
from abc import ABC, abstractmethod


class DataValidator:
    """
    Validates data for different visualization types.
    
    This class provides methods to check if data is valid for
    specific visualization types and provides informative errors.
    """
    
    @staticmethod
    def validate_for_chart(
        data: Any,
        chart_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate data for chart-based visualizations.
        
        Args:
            data: Data to validate
            chart_type: Type of chart (line, bar, pie, etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if chart_type in ["line", "bar", "radar"]:
            # These charts expect data with labels and datasets
            if not isinstance(data, dict):
                return False, f"Data for {chart_type} chart must be a dictionary"
            
            if "labels" not in data:
                return False, f"Data for {chart_type} chart must have 'labels' key"
            
            if "datasets" not in data:
                return False, f"Data for {chart_type} chart must have 'datasets' key"
            
            if not isinstance(data["labels"], list):
                return False, f"'labels' must be a list"
            
            if not isinstance(data["datasets"], list):
                return False, f"'datasets' must be a list"
            
            for dataset in data["datasets"]:
                if not isinstance(dataset, dict):
                    return False, "Each dataset must be a dictionary"
                
                if "data" not in dataset:
                    return False, "Each dataset must have a 'data' key"
                
                if not isinstance(dataset["data"], list):
                    return False, "Dataset 'data' must be a list"
                
                if len(dataset["data"]) != len(data["labels"]):
                    return False, f"Dataset has {len(dataset['data'])} values but there are {len(data['labels'])} labels"
            
            return True, None
            
        elif chart_type in ["pie", "donut"]:
            # These charts expect simpler data structure
            if not isinstance(data, dict):
                return False, f"Data for {chart_type} chart must be a dictionary"
            
            if "labels" not in data:
                return False, f"Data for {chart_type} chart must have 'labels' key"
            
            if "values" not in data:
                return False, f"Data for {chart_type} chart must have 'values' key"
            
            if not isinstance(data["labels"], list):
                return False, f"'labels' must be a list"
            
            if not isinstance(data["values"], list):
                return False, f"'values' must be a list"
            
            if len(data["values"]) != len(data["labels"]):
                return False, f"There are {len(data['values'])} values but {len(data['labels'])} labels"
            
            return True, None
            
        elif chart_type == "scatter":
            # Scatter plots expect x and y values
            if not isinstance(data, dict):
                return False, "Data for scatter chart must be a dictionary"
            
            if "datasets" not in data:
                return False, "Data for scatter chart must have 'datasets' key"
            
            if not isinstance(data["datasets"], list):
                return False, "'datasets' must be a list"
            
            for dataset in data["datasets"]:
                if not isinstance(dataset, dict):
                    return False, "Each dataset must be a dictionary"
                
                if "data" not in dataset:
                    return False, "Each dataset must have a 'data' key"
                
                if not isinstance(dataset["data"], list):
                    return False, "Dataset 'data' must be a list"
                
                for point in dataset["data"]:
                    if not isinstance(point, dict):
                        return False, "Each data point must be a dictionary"
                    
                    if "x" not in point:
                        return False, "Each data point must have an 'x' value"
                    
                    if "y" not in point:
                        return False, "Each data point must have a 'y' value"
            
            return True, None
            
        return False, f"Unsupported chart type: {chart_type}"
    
    @staticmethod
    def validate_for_network(
        data: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate data for network-based visualizations.
        
        Args:
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Network data must be a dictionary"
        
        if "nodes" not in data:
            return False, "Network data must have a 'nodes' key"
        
        if "edges" not in data:
            return False, "Network data must have an 'edges' key"
        
        if not isinstance(data["nodes"], list):
            return False, "'nodes' must be a list"
        
        if not isinstance(data["edges"], list):
            return False, "'edges' must be a list"
        
        # Check node structure
        for node in data["nodes"]:
            if not isinstance(node, dict):
                return False, "Each node must be a dictionary"
            
            if "id" not in node:
                return False, "Each node must have an 'id' key"
        
        # Check edge structure
        for edge in data["edges"]:
            if not isinstance(edge, dict):
                return False, "Each edge must be a dictionary"
            
            if "source" not in edge:
                return False, "Each edge must have a 'source' key"
            
            if "target" not in edge:
                return False, "Each edge must have a 'target' key"
        
        return True, None
    
    @staticmethod
    def validate_for_3d(
        data: Any,
        vis_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate data for 3D visualizations.
        
        Args:
            data: Data to validate
            vis_type: Type of 3D visualization (scatter3d, surface3d, etc.)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if vis_type == "scatter3d":
            if not isinstance(data, list):
                return False, "Scatter3D data must be a list of points"
            
            for point in data:
                if not isinstance(point, dict):
                    return False, "Each point must be a dictionary"
                
                if "x" not in point or "y" not in point or "z" not in point:
                    return False, "Each point must have x, y, and z coordinates"
            
            return True, None
            
        elif vis_type == "surface3d":
            # Surface data can be a 2D array of heights or a function
            if callable(data):
                # It's a function, which is valid
                return True, None
            
            if isinstance(data, dict) and "values" in data:
                if not isinstance(data["values"], list):
                    return False, "Surface data 'values' must be a list of rows"
                
                # Check that all rows have the same length
                row_lengths = [len(row) for row in data["values"]]
                if len(set(row_lengths)) > 1:
                    return False, "All rows in surface data must have the same length"
                
                return True, None
            
            return False, "Surface3D data must be a function or a dictionary with 'values' key"
            
        elif vis_type == "network3d":
            # Reuse network validation
            return DataValidator.validate_for_network(data)
            
        return False, f"Unsupported 3D visualization type: {vis_type}"


class DataTransformer:
    """
    Transforms data into formats suitable for visualization.
    
    This class provides methods to convert various data formats
    (pandas DataFrames, CSV, JSON, etc.) into the format expected
    by visualization classes.
    """
    
    @staticmethod
    def from_dataframe(
        df: pd.DataFrame,
        x_column: str = None,
        y_columns: Union[str, List[str]] = None,
        chart_type: str = "line"
    ) -> Dict[str, Any]:
        """
        Transform a pandas DataFrame into visualization data format.
        
        Args:
            df: Pandas DataFrame
            x_column: Column to use for x-axis (or labels)
            y_columns: Column(s) to use for y-axis values
            chart_type: Type of chart to prepare data for
            
        Returns:
            Data in the appropriate format for the requested chart type
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        # If x_column is not specified, use the first column
        if x_column is None:
            x_column = df.columns[0]
        
        # If y_columns is not specified, use all columns except x_column
        if y_columns is None:
            y_columns = [c for c in df.columns if c != x_column]
        elif isinstance(y_columns, str):
            y_columns = [y_columns]
        
        if chart_type in ["line", "bar", "radar"]:
            # Format for line, bar, and radar charts
            labels = df[x_column].tolist()
            datasets = []
            
            for col in y_columns:
                datasets.append({
                    "label": col,
                    "data": df[col].tolist()
                })
            
            return {
                "labels": labels,
                "datasets": datasets
            }
            
        elif chart_type in ["pie", "donut"]:
            # Format for pie and donut charts
            # For these, we only use the first y column
            y_col = y_columns[0] if len(y_columns) > 0 else df.columns[1]
            
            return {
                "labels": df[x_column].tolist(),
                "values": df[y_col].tolist()
            }
            
        elif chart_type == "scatter":
            # Format for scatter chart
            datasets = []
            
            for col in y_columns:
                data = []
                for _, row in df.iterrows():
                    data.append({
                        "x": float(row[x_column]),
                        "y": float(row[col])
                    })
                
                datasets.append({
                    "label": col,
                    "data": data
                })
            
            return {
                "datasets": datasets
            }
            
        elif chart_type == "heatmap":
            # Format for heatmap
            # For heatmap, we need x_column, y_column, and value_column
            if len(y_columns) < 2:
                raise ValueError("Heatmap requires at least two y columns (one for categories, one for values)")
            
            y_column = y_columns[0]
            value_column = y_columns[1]
            
            # Create a pivot table
            pivot_data = df.pivot(index=y_column, columns=x_column, values=value_column).fillna(0)
            
            return {
                "x_labels": list(pivot_data.columns),
                "y_labels": list(pivot_data.index),
                "values": pivot_data.values.tolist()
            }
            
        elif chart_type in ["network", "tree"]:
            # For network and tree visualizations, we need specialized data
            raise ValueError(f"DataFrame to {chart_type} conversion requires additional parameters. Use from_dataframe_to_network() instead.")
            
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
    @staticmethod
    def from_dataframe_to_network(
        df: pd.DataFrame,
        source_col: str,
        target_col: str,
        weight_col: Optional[str] = None,
        node_attrs: Optional[Dict[str, str]] = None,
        edge_attrs: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Transform a pandas DataFrame into network data format.
        
        Args:
            df: Pandas DataFrame with network edge data
            source_col: Column with source node IDs
            target_col: Column with target node IDs
            weight_col: Optional column with edge weights
            node_attrs: Mapping of node attribute columns
            edge_attrs: Mapping of edge attribute columns
            
        Returns:
            Network data with nodes and edges
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        # Extract unique nodes
        source_nodes = set(df[source_col])
        target_nodes = set(df[target_col])
        all_nodes = list(source_nodes.union(target_nodes))
        
        # Create node objects
        nodes = []
        for node_id in all_nodes:
            node = {"id": node_id}
            
            # Add node attributes if available
            if node_attrs:
                node_rows = df[df[source_col] == node_id]
                if len(node_rows) > 0:
                    for attr_name, attr_col in node_attrs.items():
                        if attr_col in df.columns:
                            node[attr_name] = node_rows.iloc[0][attr_col]
            
            nodes.append(node)
        
        # Create edge objects
        edges = []
        for _, row in df.iterrows():
            edge = {
                "source": row[source_col],
                "target": row[target_col]
            }
            
            # Add weight if specified
            if weight_col and weight_col in df.columns:
                edge["weight"] = row[weight_col]
            
            # Add edge attributes if available
            if edge_attrs:
                for attr_name, attr_col in edge_attrs.items():
                    if attr_col in df.columns:
                        edge[attr_name] = row[attr_col]
            
            edges.append(edge)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    @staticmethod
    def from_json(
        json_data: Union[str, Dict[str, Any]],
        chart_type: str = None
    ) -> Dict[str, Any]:
        """
        Transform JSON data into visualization data format.
        
        Args:
            json_data: JSON string or dictionary
            chart_type: Optional chart type for validation
            
        Returns:
            Data in the appropriate format
        """
        # Parse JSON if string
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON data")
        else:
            data = json_data
        
        # If chart type is specified, validate data
        if chart_type:
            is_valid, error = DataValidator.validate_for_chart(data, chart_type)
            if not is_valid:
                raise ValueError(f"Invalid data for {chart_type} chart: {error}")
        
        return data
    
    @staticmethod
    def from_csv(
        csv_file: str,
        x_column: str = None,
        y_columns: Union[str, List[str]] = None,
        chart_type: str = "line",
        **pandas_kwargs
    ) -> Dict[str, Any]:
        """
        Transform CSV data into visualization data format.
        
        Args:
            csv_file: Path to CSV file
            x_column: Column to use for x-axis
            y_columns: Column(s) to use for y-axis values
            chart_type: Type of chart to prepare data for
            **pandas_kwargs: Additional arguments for pandas.read_csv
            
        Returns:
            Data in the appropriate format
        """
        df = pd.read_csv(csv_file, **pandas_kwargs)
        return DataTransformer.from_dataframe(
            df, x_column, y_columns, chart_type
        )


class DataProcessor(ABC):
    """
    Abstract base class for visualization-specific data processing.
    
    Subclasses implement specific preprocessing for different
    visualization types.
    """
    
    @abstractmethod
    def process(self, data: Any) -> Any:
        """
        Process data for visualization.
        
        Args:
            data: Input data
            
        Returns:
            Processed data ready for visualization
        """
        pass


class ChartDataProcessor(DataProcessor):
    """Data processor for chart-based visualizations."""
    
    def __init__(self, chart_type: str):
        """
        Initialize with chart type.
        
        Args:
            chart_type: Type of chart
        """
        self.chart_type = chart_type
    
    def process(self, data: Any) -> Any:
        """
        Process data for chart visualization.
        
        Args:
            data: Input data
            
        Returns:
            Processed chart data
        """
        # Validate input data
        is_valid, error = DataValidator.validate_for_chart(data, self.chart_type)
        if not is_valid:
            raise ValueError(f"Invalid data for {self.chart_type} chart: {error}")
        
        # Apply chart-specific processing
        if self.chart_type in ["pie", "donut"]:
            # For pie/donut charts, ensure sum is not zero
            if sum(data["values"]) == 0:
                raise ValueError("Sum of values for pie/donut chart must not be zero")
            
            # Sort pie segments by value if needed
            if len(data.get("sort", "")) > 0 and data.get("sort") == "descending":
                sorted_data = sorted(zip(data["labels"], data["values"]), 
                                    key=lambda x: x[1], reverse=True)
                data["labels"], data["values"] = zip(*sorted_data)
        
        elif self.chart_type in ["line", "bar", "radar"]:
            # Ensure all datasets have colors if not provided
            for dataset in data["datasets"]:
                if "backgroundColor" not in dataset and "borderColor" not in dataset:
                    # This will be handled by the visualization class
                    pass
        
        return data


class NetworkDataProcessor(DataProcessor):
    """Data processor for network-based visualizations."""
    
    def process(self, data: Any) -> Any:
        """
        Process data for network visualization.
        
        Args:
            data: Input data
            
        Returns:
            Processed network data
        """
        # Validate input data
        is_valid, error = DataValidator.validate_for_network(data)
        if not is_valid:
            raise ValueError(f"Invalid network data: {error}")
        
        # Create a lookup for nodes by ID
        node_map = {node["id"]: node for node in data["nodes"]}
        
        # Filter edges to only include those with valid source and target
        valid_edges = []
        for edge in data["edges"]:
            if edge["source"] in node_map and edge["target"] in node_map:
                valid_edges.append(edge)
        
        # Update data with valid edges
        data["edges"] = valid_edges
        
        # Add degree information to nodes
        in_degree = {}
        out_degree = {}
        
        for edge in valid_edges:
            source = edge["source"]
            target = edge["target"]
            
            out_degree[source] = out_degree.get(source, 0) + 1
            in_degree[target] = in_degree.get(target, 0) + 1
        
        for node in data["nodes"]:
            node_id = node["id"]
            node["in_degree"] = in_degree.get(node_id, 0)
            node["out_degree"] = out_degree.get(node_id, 0)
            node["degree"] = node["in_degree"] + node["out_degree"]
        
        return data


class ThreeDDataProcessor(DataProcessor):
    """Data processor for 3D visualizations."""
    
    def __init__(self, vis_type: str):
        """
        Initialize with visualization type.
        
        Args:
            vis_type: Type of 3D visualization
        """
        self.vis_type = vis_type
    
    def process(self, data: Any) -> Any:
        """
        Process data for 3D visualization.
        
        Args:
            data: Input data
            
        Returns:
            Processed 3D data
        """
        # Validate input data
        is_valid, error = DataValidator.validate_for_3d(data, self.vis_type)
        if not is_valid:
            raise ValueError(f"Invalid data for {self.vis_type}: {error}")
        
        if self.vis_type == "scatter3d":
            # For scatter3d, normalize position values if they're too large
            max_val = max(
                max(abs(p["x"]) for p in data),
                max(abs(p["y"]) for p in data),
                max(abs(p["z"]) for p in data)
            )
            
            # If values are very large, normalize to [-100, 100] range
            if max_val > 1000:
                normalize_factor = 100 / max_val
                for point in data:
                    point["x"] *= normalize_factor
                    point["y"] *= normalize_factor
                    point["z"] *= normalize_factor
        
        elif self.vis_type == "surface3d":
            # For surface3d with grid data, ensure equal spacing
            if isinstance(data, dict) and "values" in data:
                values = data["values"]
                
                # Check if x_range and y_range are provided
                if "x_range" not in data:
                    data["x_range"] = [0, len(values[0])]
                if "y_range" not in data:
                    data["y_range"] = [0, len(values)]
        
        return data 