"""
Chart.js visualization integration for LlamaVis.

This module implements basic chart types (line, bar, pie, etc.) using Chart.js,
providing a simple and efficient way to create common visualizations.
"""
from typing import Any, Dict, List, Optional, Union
import json
import uuid

from ..core.visualization import Visualization
from ..core.config import VisualizationConfig, ChartType
from ..core.data import DataProcessor
from ..core.utils import generate_unique_id, safe_json_value, generate_color_scale


class ChartJSVisualization(Visualization):
    """
    Base class for Chart.js visualizations.
    
    This class provides common functionality for visualizations
    implemented using Chart.js.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Chart.js Visualization"
    ):
        """
        Initialize a Chart.js visualization.
        
        Args:
            data: Data to visualize
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.BAR)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def get_library_includes(self) -> List[str]:
        """
        Get the JavaScript libraries required for this visualization.
        
        Returns:
            List of library names to include
        """
        return ["chart.js"]
    
    def preprocess_data(self) -> Dict[str, Any]:
        """
        Preprocess the data for Chart.js visualization.
        
        Returns:
            Preprocessed data ready for visualization
        """
        # Default preprocessing for most Chart.js visualizations
        if self.config.chart_type in [ChartType.PIE, ChartType.DONUT]:
            return DataProcessor.prepare_for_pie(self.data)
        
        # For most other chart types, return in the standard Chart.js format
        # which includes labels and datasets
        if hasattr(self.data, "columns") and hasattr(self.data, "values"):
            # Likely a pandas DataFrame
            df = DataProcessor.to_dataframe(self.data)
            
            # Try to guess the x-axis column (first column) and y-axis column(s) (other columns)
            x_col = df.columns[0]
            y_cols = df.columns[1:].tolist()
            
            return DataProcessor.pivot_for_chart(df, x_col, y_cols[0] if y_cols else None)
        
        # Handle dict-like data
        if isinstance(self.data, dict) and "labels" in self.data and "datasets" in self.data:
            # Already in Chart.js format
            return safe_json_value(self.data)
        
        # Try to convert to a standard format
        return DataProcessor.to_json(self.data)


class LineChart(ChartJSVisualization):
    """
    Line chart visualization using Chart.js.
    
    This class implements line chart visualizations for time series
    or trend data using Chart.js.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Line Chart"
    ):
        """
        Initialize a line chart visualization.
        
        Args:
            data: Data for the line chart
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.LINE)
        else:
            # Ensure chart type is set to LINE
            config.update(chart_type=ChartType.LINE)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the line chart visualization.
        
        Returns:
            JavaScript code as a string
        """
        # Define the Chart.js code for line chart visualization
        js_code = f"""
        // Create a line chart visualization
        (function() {{
            const container = document.getElementById("{self.container_id}");
            
            // Clear previous content
            container.innerHTML = "";
            
            // Add title if specified
            if ("{self.title}") {{
                const titleElement = document.createElement("h3");
                titleElement.className = "vis-title";
                titleElement.style.textAlign = "center";
                titleElement.style.marginBottom = "20px";
                titleElement.style.fontFamily = config.font_family;
                titleElement.style.fontSize = config.title_font_size + "px";
                titleElement.textContent = "{self.title}";
                container.appendChild(titleElement);
            }}
            
            // Create canvas element
            const canvas = document.createElement("canvas");
            canvas.width = {self.width};
            canvas.height = {self.height};
            canvas.style.maxWidth = "100%";
            container.appendChild(canvas);
            
            // Create Chart.js dataset colors if not provided
            const datasets = data.datasets.map((dataset, i) => {{
                const colorIndex = i % config.color_palette.length;
                const baseColor = config.color_palette[colorIndex];
                
                return {{
                    ...dataset,
                    borderColor: dataset.borderColor || baseColor,
                    backgroundColor: dataset.backgroundColor || baseColor + "20", // 20 = 12% opacity
                    borderWidth: dataset.borderWidth || 2,
                    pointRadius: dataset.pointRadius || 3,
                    pointHoverRadius: dataset.pointHoverRadius || 5,
                    fill: dataset.fill !== undefined ? dataset.fill : config.fill || false
                }};
            }});
            
            // Create chart configuration
            const chartConfig = {{
                type: 'line',
                data: {{
                    labels: data.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: config.responsive,
                    maintainAspectRatio: true,
                    animation: {{
                        duration: config.animation ? config.animation_duration : 0
                    }},
                    interaction: {{
                        mode: 'index',
                        intersect: false
                    }},
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: config.show_legend,
                            position: 'top',
                            labels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        tooltip: {{
                            enabled: config.interactive,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {{
                                family: config.font_family,
                                size: config.font_size + 2
                            }},
                            bodyFont: {{
                                family: config.font_family,
                                size: config.font_size
                            }},
                            padding: 10,
                            cornerRadius: 3,
                            displayColors: true
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: config.axis_labels && config.axis_labels.x,
                                text: config.axis_labels ? config.axis_labels.x : '',
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }},
                            grid: {{
                                display: config.show_grid
                            }},
                            ticks: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        y: {{
                            title: {{
                                display: config.axis_labels && config.axis_labels.y,
                                text: config.axis_labels ? config.axis_labels.y : '',
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }},
                            grid: {{
                                display: config.show_grid
                            }},
                            beginAtZero: config.begin_at_zero || false,
                            ticks: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }}
                    }}
                }}
            }};
            
            // Apply smooth curves setting
            if (config.smooth_curves) {{
                chartConfig.options.elements = {{
                    line: {{
                        tension: 0.4
                    }}
                }};
            }}
            
            // Create the chart
            new Chart(canvas, chartConfig);
        }})();
        """
        
        return js_code


class BarChart(ChartJSVisualization):
    """
    Bar chart visualization using Chart.js.
    
    This class implements bar chart visualizations for categorical
    data using Chart.js.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Bar Chart"
    ):
        """
        Initialize a bar chart visualization.
        
        Args:
            data: Data for the bar chart
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.BAR)
        else:
            # Ensure chart type is set to BAR
            config.update(chart_type=ChartType.BAR)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the bar chart visualization.
        
        Returns:
            JavaScript code as a string
        """
        # Define the Chart.js code for bar chart visualization
        js_code = f"""
        // Create a bar chart visualization
        (function() {{
            const container = document.getElementById("{self.container_id}");
            
            // Clear previous content
            container.innerHTML = "";
            
            // Add title if specified
            if ("{self.title}") {{
                const titleElement = document.createElement("h3");
                titleElement.className = "vis-title";
                titleElement.style.textAlign = "center";
                titleElement.style.marginBottom = "20px";
                titleElement.style.fontFamily = config.font_family;
                titleElement.style.fontSize = config.title_font_size + "px";
                titleElement.textContent = "{self.title}";
                container.appendChild(titleElement);
            }}
            
            // Create canvas element
            const canvas = document.createElement("canvas");
            canvas.width = {self.width};
            canvas.height = {self.height};
            canvas.style.maxWidth = "100%";
            container.appendChild(canvas);
            
            // Create Chart.js dataset colors if not provided
            const datasets = data.datasets.map((dataset, i) => {{
                const colorIndex = i % config.color_palette.length;
                const baseColor = config.color_palette[colorIndex];
                
                return {{
                    ...dataset,
                    backgroundColor: dataset.backgroundColor || (
                        Array.isArray(config.color_palette) ? 
                        config.color_palette : 
                        [baseColor]
                    ),
                    borderColor: dataset.borderColor || (
                        Array.isArray(dataset.backgroundColor) ? 
                        dataset.backgroundColor.map(c => c.replace('0.2', '1')) : 
                        baseColor
                    ),
                    borderWidth: dataset.borderWidth || 1
                }};
            }});
            
            // Create chart configuration
            const chartConfig = {{
                type: 'bar',
                data: {{
                    labels: data.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: config.responsive,
                    maintainAspectRatio: true,
                    animation: {{
                        duration: config.animation ? config.animation_duration : 0
                    }},
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: config.show_legend && datasets.length > 1,
                            position: 'top',
                            labels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        tooltip: {{
                            enabled: config.interactive,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {{
                                family: config.font_family,
                                size: config.font_size + 2
                            }},
                            bodyFont: {{
                                family: config.font_family,
                                size: config.font_size
                            }},
                            padding: 10,
                            cornerRadius: 3,
                            displayColors: true
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: config.axis_labels && config.axis_labels.x,
                                text: config.axis_labels ? config.axis_labels.x : '',
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }},
                            grid: {{
                                display: config.show_grid
                            }},
                            ticks: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        y: {{
                            title: {{
                                display: config.axis_labels && config.axis_labels.y,
                                text: config.axis_labels ? config.axis_labels.y : '',
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }},
                            grid: {{
                                display: config.show_grid
                            }},
                            beginAtZero: true,
                            ticks: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }}
                    }}
                }}
            }};
            
            // Check if we should use horizontal bars
            if (config.horizontal) {{
                chartConfig.type = 'horizontalBar';
                // In newer Chart.js versions, horizontal bar is handled differently
                chartConfig.type = 'bar';
                chartConfig.options.indexAxis = 'y';
            }}
            
            // Create the chart
            new Chart(canvas, chartConfig);
        }})();
        """
        
        return js_code


class PieChart(ChartJSVisualization):
    """
    Pie chart visualization using Chart.js.
    
    This class implements pie chart visualizations for showing parts
    of a whole using Chart.js.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 600,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Pie Chart"
    ):
        """
        Initialize a pie chart visualization.
        
        Args:
            data: Data for the pie chart
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.PIE)
        else:
            # Ensure chart type is set to PIE
            config.update(chart_type=ChartType.PIE)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the pie chart visualization.
        
        Returns:
            JavaScript code as a string
        """
        # Define the Chart.js code for pie chart visualization
        js_code = f"""
        // Create a pie chart visualization
        (function() {{
            const container = document.getElementById("{self.container_id}");
            
            // Clear previous content
            container.innerHTML = "";
            
            // Add title if specified
            if ("{self.title}") {{
                const titleElement = document.createElement("h3");
                titleElement.className = "vis-title";
                titleElement.style.textAlign = "center";
                titleElement.style.marginBottom = "20px";
                titleElement.style.fontFamily = config.font_family;
                titleElement.style.fontSize = config.title_font_size + "px";
                titleElement.textContent = "{self.title}";
                container.appendChild(titleElement);
            }}
            
            // Create canvas element
            const canvas = document.createElement("canvas");
            canvas.width = {self.width};
            canvas.height = {self.height};
            canvas.style.maxWidth = "100%";
            container.appendChild(canvas);
            
            // Prepare background colors if not provided
            const backgroundColor = data.datasets[0].backgroundColor || config.color_palette;
            
            // Create chart configuration
            const chartConfig = {{
                type: '{self.config.chart_type.value}',
                data: {{
                    labels: data.labels,
                    datasets: [{{
                        data: data.datasets[0].data,
                        backgroundColor: backgroundColor,
                        borderColor: config.show_grid ? 'white' : backgroundColor.map(color => color),
                        borderWidth: config.show_grid ? 2 : 0
                    }}]
                }},
                options: {{
                    responsive: config.responsive,
                    maintainAspectRatio: true,
                    animation: {{
                        duration: config.animation ? config.animation_duration : 0
                    }},
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: config.show_legend,
                            position: 'right',
                            labels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        tooltip: {{
                            enabled: config.interactive,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {{
                                family: config.font_family,
                                size: config.font_size + 2
                            }},
                            bodyFont: {{
                                family: config.font_family,
                                size: config.font_size
                            }},
                            padding: 10,
                            cornerRadius: 3,
                            displayColors: true
                        }}
                    }}
                }}
            }};
            
            // Create the chart
            new Chart(canvas, chartConfig);
        }})();
        """
        
        return js_code


class DonutChart(PieChart):
    """
    Donut chart visualization using Chart.js.
    
    This class is a specialized version of PieChart that renders
    a donut (ring) chart.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 600,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Donut Chart"
    ):
        """
        Initialize a donut chart visualization.
        
        Args:
            data: Data for the donut chart
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.DONUT)
        else:
            # Ensure chart type is set to DONUT
            config.update(chart_type=ChartType.DONUT)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the donut chart visualization.
        
        Returns:
            JavaScript code as a string
        """
        # Define the Chart.js code for donut chart visualization
        js_code = f"""
        // Create a donut chart visualization
        (function() {{
            const container = document.getElementById("{self.container_id}");
            
            // Clear previous content
            container.innerHTML = "";
            
            // Add title if specified
            if ("{self.title}") {{
                const titleElement = document.createElement("h3");
                titleElement.className = "vis-title";
                titleElement.style.textAlign = "center";
                titleElement.style.marginBottom = "20px";
                titleElement.style.fontFamily = config.font_family;
                titleElement.style.fontSize = config.title_font_size + "px";
                titleElement.textContent = "{self.title}";
                container.appendChild(titleElement);
            }}
            
            // Create canvas element
            const canvas = document.createElement("canvas");
            canvas.width = {self.width};
            canvas.height = {self.height};
            canvas.style.maxWidth = "100%";
            container.appendChild(canvas);
            
            // Prepare background colors if not provided
            const backgroundColor = data.datasets[0].backgroundColor || config.color_palette;
            
            // Create chart configuration
            const chartConfig = {{
                type: 'doughnut',
                data: {{
                    labels: data.labels,
                    datasets: [{{
                        data: data.datasets[0].data,
                        backgroundColor: backgroundColor,
                        borderColor: config.show_grid ? 'white' : backgroundColor.map(color => color),
                        borderWidth: config.show_grid ? 2 : 0
                    }}]
                }},
                options: {{
                    responsive: config.responsive,
                    maintainAspectRatio: true,
                    animation: {{
                        duration: config.animation ? config.animation_duration : 0
                    }},
                    cutout: config.cutout || '70%',
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: config.show_legend,
                            position: 'right',
                            labels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        tooltip: {{
                            enabled: config.interactive,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {{
                                family: config.font_family,
                                size: config.font_size + 2
                            }},
                            bodyFont: {{
                                family: config.font_family,
                                size: config.font_size
                            }},
                            padding: 10,
                            cornerRadius: 3,
                            displayColors: true
                        }}
                    }}
                }}
            }};
            
            // Create the chart
            new Chart(canvas, chartConfig);
        }})();
        """
        
        return js_code


class RadarChart(ChartJSVisualization):
    """
    Radar chart visualization using Chart.js.
    
    This class implements radar chart visualizations for multivariate
    data using Chart.js.
    """
    
    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 600,
        height: int = 400,
        container_id: Optional[str] = None,
        title: str = "Radar Chart"
    ):
        """
        Initialize a radar chart visualization.
        
        Args:
            data: Data for the radar chart
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.RADAR)
        else:
            # Ensure chart type is set to RADAR
            config.update(chart_type=ChartType.RADAR)
        
        super().__init__(data, config, width, height, container_id, title)
    
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the radar chart visualization.
        
        Returns:
            JavaScript code as a string
        """
        # Define the Chart.js code for radar chart visualization
        js_code = f"""
        // Create a radar chart visualization
        (function() {{
            const container = document.getElementById("{self.container_id}");
            
            // Clear previous content
            container.innerHTML = "";
            
            // Add title if specified
            if ("{self.title}") {{
                const titleElement = document.createElement("h3");
                titleElement.className = "vis-title";
                titleElement.style.textAlign = "center";
                titleElement.style.marginBottom = "20px";
                titleElement.style.fontFamily = config.font_family;
                titleElement.style.fontSize = config.title_font_size + "px";
                titleElement.textContent = "{self.title}";
                container.appendChild(titleElement);
            }}
            
            // Create canvas element
            const canvas = document.createElement("canvas");
            canvas.width = {self.width};
            canvas.height = {self.height};
            canvas.style.maxWidth = "100%";
            container.appendChild(canvas);
            
            // Create Chart.js dataset colors if not provided
            const datasets = data.datasets.map((dataset, i) => {{
                const colorIndex = i % config.color_palette.length;
                const baseColor = config.color_palette[colorIndex];
                
                return {{
                    ...dataset,
                    borderColor: dataset.borderColor || baseColor,
                    backgroundColor: dataset.backgroundColor || baseColor + "40", // 40 = 25% opacity
                    borderWidth: dataset.borderWidth || 2,
                    pointBackgroundColor: dataset.pointBackgroundColor || baseColor,
                    pointBorderColor: dataset.pointBorderColor || "#fff",
                    pointHoverBackgroundColor: dataset.pointHoverBackgroundColor || "#fff",
                    pointHoverBorderColor: dataset.pointHoverBorderColor || baseColor,
                    pointRadius: dataset.pointRadius || 3,
                    pointHoverRadius: dataset.pointHoverRadius || 5
                }};
            }});
            
            // Create chart configuration
            const chartConfig = {{
                type: 'radar',
                data: {{
                    labels: data.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: config.responsive,
                    maintainAspectRatio: true,
                    animation: {{
                        duration: config.animation ? config.animation_duration : 0
                    }},
                    plugins: {{
                        title: {{
                            display: false
                        }},
                        legend: {{
                            display: config.show_legend,
                            position: 'top',
                            labels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }}
                        }},
                        tooltip: {{
                            enabled: config.interactive,
                            backgroundColor: 'rgba(0, 0, 0, 0.7)',
                            titleFont: {{
                                family: config.font_family,
                                size: config.font_size + 2
                            }},
                            bodyFont: {{
                                family: config.font_family,
                                size: config.font_size
                            }},
                            padding: 10,
                            cornerRadius: 3,
                            displayColors: true
                        }}
                    }},
                    scales: {{
                        r: {{
                            angleLines: {{
                                display: config.show_grid
                            }},
                            grid: {{
                                circular: true,
                                display: config.show_grid
                            }},
                            pointLabels: {{
                                font: {{
                                    family: config.font_family,
                                    size: config.font_size
                                }}
                            }},
                            beginAtZero: true
                        }}
                    }}
                }}
            }};
            
            // Create the chart
            new Chart(canvas, chartConfig);
        }})();
        """
        
        return js_code 