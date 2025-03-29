"""
LlamaVis: Data visualization library for the LlamaSearch.AI ecosystem.

This library integrates multiple JavaScript visualization libraries
(Three.js, D3.js, Chart.js, GSAP, Lottie) to provide a comprehensive
set of visualization tools for Python.
"""

__version__ = "0.1.0"

# Import core components
from .core.visualization import Visualization
from .core.config import VisualizationConfig, ChartType, ThemeType, Interaction
from .core.renderer import Renderer

# Import Chart.js visualizations
from .integrations.chartjs_vis import (
    ChartJSVisualization,
    LineChart,
    BarChart,
    PieChart,
    DonutChart,
    RadarChart,
)

# Import D3 visualizations
from .integrations.d3_vis import (
    D3Visualization,
    NetworkGraph,
    TreeVis,
    TreemapVis,
    HeatmapVis,
)

# Import Three.js visualizations
from .integrations.threejs_vis import (
    ThreeJSVisualization,
    Scatter3D,
    Network3D,
    Surface3D,
)

# Import utility functions
from .core.utils import (
    generate_color_scale,
    generate_contrasting_colors,
    hex_to_rgb,
    rgb_to_hex,
    hex_to_rgba,
    interpolate_colors,
)

# Define what's available for import when using `from llamavis import *`
__all__ = [
    # Version
    "__version__",
    
    # Core classes
    "Visualization",
    "VisualizationConfig",
    "ChartType",
    "ThemeType",
    "Interaction",
    "Renderer",
    
    # Chart.js visualizations
    "ChartJSVisualization",
    "LineChart",
    "BarChart",
    "PieChart", 
    "DonutChart",
    "RadarChart",
    
    # D3 visualizations
    "D3Visualization",
    "NetworkGraph",
    "TreeVis",
    "TreemapVis",
    "HeatmapVis",
    
    # Three.js visualizations
    "ThreeJSVisualization",
    "Scatter3D",
    "Network3D",
    "Surface3D",
    
    # Utility functions
    "generate_color_scale",
    "generate_contrasting_colors",
    "hex_to_rgb",
    "rgb_to_hex",
    "hex_to_rgba",
    "interpolate_colors",
] 