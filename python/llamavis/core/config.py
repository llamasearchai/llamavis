"""
Configuration classes for LlamaVis visualizations.

This module defines configuration options and enumerations for
controlling visualization appearance, behavior and interactions.
"""

import json
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union


class ThemeType(Enum):
    """Enumeration of supported visualization themes."""

    LIGHT = "light"
    DARK = "dark"
    COLORBLIND = "colorblind"
    MONOCHROME = "monochrome"
    PASTEL = "pastel"
    VIBRANT = "vibrant"
    CORPORATE = "corporate"
    SCIENTIFIC = "scientific"


class ChartType(Enum):
    """Enumeration of supported chart types."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    RADAR = "radar"
    NETWORK = "network"
    TREE = "tree"
    TREEMAP = "treemap"
    HEATMAP = "heatmap"
    SCATTER3D = "scatter3d"
    NETWORK3D = "network3d"
    SURFACE3D = "surface3d"


class Interaction(Enum):
    """Enumeration of supported interaction types."""

    HOVER = "hover"
    CLICK = "click"
    ZOOM = "zoom"
    PAN = "pan"
    ROTATE = "rotate"
    SELECT = "select"
    DRAG = "drag"


# Default color palettes
COLOR_PALETTES = {
    "llamasearch": ["#6E44FF", "#B892FF", "#FFC2E2", "#FF90B3", "#EF7A85"],
    "categorical": [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ],
    "sequential": [
        "#f7fbff",
        "#deebf7",
        "#c6dbef",
        "#9ecae1",
        "#6baed6",
        "#4292c6",
        "#2171b5",
        "#08519c",
        "#08306b",
    ],
    "diverging": [
        "#d73027",
        "#f46d43",
        "#fdae61",
        "#fee090",
        "#ffffbf",
        "#e0f3f8",
        "#abd9e9",
        "#74add1",
        "#4575b4",
    ],
}


class VisualizationConfig:
    """Base configuration class for all visualizations."""

    def __init__(
        self,
        chart_type: Union[ChartType, str],
        theme: Union[ThemeType, str] = ThemeType.LIGHT,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        show_legend: bool = True,
        legend_position: str = "top",
        colors: Optional[List[str]] = None,
        animation_duration: int = 500,
        tooltip_enabled: bool = True,
        enable_interactions: List[Union[Interaction, str]] = None,
        axis_labels: Dict[str, str] = None,
        grid_lines: bool = True,
        background_color: Optional[str] = None,
        font_family: str = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
        responsive: bool = True,
        maintain_aspect_ratio: bool = True,
        custom_options: Dict[str, Any] = None,
    ):
        """
        Initialize visualization configuration.

        Args:
            chart_type: Type of chart to render
            theme: Color theme to apply
            title: Main chart title
            subtitle: Secondary chart title
            show_legend: Whether to show the legend
            legend_position: Position of the legend (top, bottom, left, right)
            colors: List of colors to use (overrides theme colors)
            animation_duration: Duration of animations in milliseconds
            tooltip_enabled: Whether to show tooltips on hover
            enable_interactions: List of enabled interactions
            axis_labels: Dict mapping axis names to labels
            grid_lines: Whether to show grid lines
            background_color: Background color of the chart
            font_family: Font family for text elements
            responsive: Whether the chart should resize with its container
            maintain_aspect_ratio: Whether to maintain the aspect ratio when resizing
            custom_options: Dict of library-specific options
        """
        # Convert string chart_type to enum if needed
        if isinstance(chart_type, str):
            try:
                self.chart_type = ChartType(chart_type)
            except ValueError:
                raise ValueError(f"Unsupported chart type: {chart_type}")
        else:
            self.chart_type = chart_type

        # Convert string theme to enum if needed
        if isinstance(theme, str):
            try:
                self.theme = ThemeType(theme)
            except ValueError:
                raise ValueError(f"Unsupported theme: {theme}")
        else:
            self.theme = theme

        self.title = title
        self.subtitle = subtitle
        self.show_legend = show_legend
        self.legend_position = legend_position
        self.colors = colors
        self.animation_duration = animation_duration
        self.tooltip_enabled = tooltip_enabled

        # Process interactions
        self.enable_interactions = []
        if enable_interactions:
            for interaction in enable_interactions:
                if isinstance(interaction, str):
                    try:
                        self.enable_interactions.append(Interaction(interaction))
                    except ValueError:
                        raise ValueError(f"Unsupported interaction: {interaction}")
                else:
                    self.enable_interactions.append(interaction)

        self.axis_labels = axis_labels or {}
        self.grid_lines = grid_lines
        self.background_color = background_color
        self.font_family = font_family
        self.responsive = responsive
        self.maintain_aspect_ratio = maintain_aspect_ratio
        self.custom_options = custom_options or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        return {
            "chart_type": self.chart_type.value,
            "theme": self.theme.value,
            "title": self.title,
            "subtitle": self.subtitle,
            "show_legend": self.show_legend,
            "legend_position": self.legend_position,
            "colors": self.colors,
            "animation_duration": self.animation_duration,
            "tooltip_enabled": self.tooltip_enabled,
            "enable_interactions": [i.value for i in self.enable_interactions],
            "axis_labels": self.axis_labels,
            "grid_lines": self.grid_lines,
            "background_color": self.background_color,
            "font_family": self.font_family,
            "responsive": self.responsive,
            "maintain_aspect_ratio": self.maintain_aspect_ratio,
            "custom_options": self.custom_options,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "VisualizationConfig":
        """Create a configuration from a dictionary."""
        # Extract and handle enums
        chart_type = config_dict.pop("chart_type")
        theme = config_dict.pop("theme", ThemeType.LIGHT.value)

        # Handle interactions
        interactions_vals = config_dict.pop("enable_interactions", [])
        enable_interactions = [Interaction(i) for i in interactions_vals]

        # Create instance with remaining options
        config_dict["enable_interactions"] = enable_interactions
        return cls(chart_type=chart_type, theme=theme, **config_dict)

    def update(self, **kwargs) -> "VisualizationConfig":
        """Update configuration with new values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"VisualizationConfig has no attribute '{key}'")
        return self


class ChartJSConfig(VisualizationConfig):
    """Configuration specific to Chart.js visualizations."""

    def __init__(
        self,
        chart_type: Union[ChartType, str],
        stacked: bool = False,
        fill: bool = False,
        tension: float = 0.4,
        point_radius: int = 3,
        border_width: int = 1,
        **kwargs,
    ):
        """
        Initialize Chart.js specific configuration.

        Args:
            chart_type: Type of chart to render
            stacked: Whether to stack data series
            fill: Whether to fill area under lines
            tension: Line tension for curved lines
            point_radius: Radius of data points
            border_width: Width of borders in pixels
            **kwargs: Additional base configuration options
        """
        super().__init__(chart_type=chart_type, **kwargs)
        self.stacked = stacked
        self.fill = fill
        self.tension = tension
        self.point_radius = point_radius
        self.border_width = border_width

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        config_dict = super().to_dict()
        config_dict.update(
            {
                "stacked": self.stacked,
                "fill": self.fill,
                "tension": self.tension,
                "point_radius": self.point_radius,
                "border_width": self.border_width,
            }
        )
        return config_dict


class D3Config(VisualizationConfig):
    """Configuration specific to D3.js visualizations."""

    def __init__(
        self,
        chart_type: Union[ChartType, str],
        force_strength: float = 0.1,
        link_distance: int = 30,
        charge_strength: int = -30,
        node_size: Union[int, str] = 5,
        link_width: int = 1,
        transition_duration: int = 750,
        **kwargs,
    ):
        """
        Initialize D3.js specific configuration.

        Args:
            chart_type: Type of chart to render
            force_strength: Strength parameter for force-directed layouts
            link_distance: Target distance between linked nodes
            charge_strength: Charge strength for node repulsion/attraction
            node_size: Size of nodes (or attribute name for dynamic sizing)
            link_width: Width of links in pixels
            transition_duration: Duration of transitions in milliseconds
            **kwargs: Additional base configuration options
        """
        super().__init__(chart_type=chart_type, **kwargs)
        self.force_strength = force_strength
        self.link_distance = link_distance
        self.charge_strength = charge_strength
        self.node_size = node_size
        self.link_width = link_width
        self.transition_duration = transition_duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        config_dict = super().to_dict()
        config_dict.update(
            {
                "force_strength": self.force_strength,
                "link_distance": self.link_distance,
                "charge_strength": self.charge_strength,
                "node_size": self.node_size,
                "link_width": self.link_width,
                "transition_duration": self.transition_duration,
            }
        )
        return config_dict


class ThreeJSConfig(VisualizationConfig):
    """Configuration specific to Three.js visualizations."""

    def __init__(
        self,
        chart_type: Union[ChartType, str],
        camera_position: Dict[str, float] = None,
        point_size: float = 0.1,
        wireframe: bool = False,
        ambient_light_intensity: float = 0.5,
        directional_light_intensity: float = 0.8,
        shadow_enabled: bool = True,
        background_opacity: float = 1.0,
        auto_rotate: bool = False,
        fog_enabled: bool = False,
        fog_color: str = "#f0f0f0",
        fog_density: float = 0.005,
        **kwargs,
    ):
        """
        Initialize Three.js specific configuration.

        Args:
            chart_type: Type of chart to render
            camera_position: Dict with x, y, z coordinates for camera
            point_size: Size of points in 3D scatter plots
            wireframe: Whether to render surfaces as wireframes
            ambient_light_intensity: Intensity of ambient light
            directional_light_intensity: Intensity of directional light
            shadow_enabled: Whether to render shadows
            background_opacity: Opacity of background (0.0-1.0)
            auto_rotate: Whether to auto-rotate the scene
            fog_enabled: Whether to enable fog effect
            fog_color: Color of fog
            fog_density: Density of fog
            **kwargs: Additional base configuration options
        """
        super().__init__(chart_type=chart_type, **kwargs)
        self.camera_position = camera_position or {"x": 5, "y": 5, "z": 5}
        self.point_size = point_size
        self.wireframe = wireframe
        self.ambient_light_intensity = ambient_light_intensity
        self.directional_light_intensity = directional_light_intensity
        self.shadow_enabled = shadow_enabled
        self.background_opacity = background_opacity
        self.auto_rotate = auto_rotate
        self.fog_enabled = fog_enabled
        self.fog_color = fog_color
        self.fog_density = fog_density

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dictionary."""
        config_dict = super().to_dict()
        config_dict.update(
            {
                "camera_position": self.camera_position,
                "point_size": self.point_size,
                "wireframe": self.wireframe,
                "ambient_light_intensity": self.ambient_light_intensity,
                "directional_light_intensity": self.directional_light_intensity,
                "shadow_enabled": self.shadow_enabled,
                "background_opacity": self.background_opacity,
                "auto_rotate": self.auto_rotate,
                "fog_enabled": self.fog_enabled,
                "fog_color": self.fog_color,
                "fog_density": self.fog_density,
            }
        )
        return config_dict


class VisualizationConfig:
    """
    Configuration settings for visualizations.

    This class provides a centralized way to configure visualization options,
    with type safety and sensible defaults.
    """

    def __init__(
        self,
        theme: Union[str, ThemeType] = ThemeType.LIGHT,
        chart_type: Union[str, ChartType] = ChartType.BAR,
        color_palette: Union[str, List[str]] = "llamasearch",
        show_legend: bool = True,
        show_axes: bool = True,
        show_grid: bool = True,
        interactive: bool = True,
        interactions: List[Union[str, Interaction]] = None,
        animation: bool = True,
        animation_duration: int = 1000,
        background_color: Optional[str] = None,
        axis_labels: Dict[str, str] = None,
        font_size: int = 12,
        font_family: str = "Arial, sans-serif",
        title_font_size: int = 18,
        responsive: bool = True,
        smooth_curves: bool = True,
        tooltip_format: Optional[str] = None,
        margin: Dict[str, int] = None,
        **additional_options,
    ):
        """
        Initialize visualization configuration.

        Args:
            theme: Theme for the visualization
            chart_type: Type of chart to create
            color_palette: Name of palette or list of color codes
            show_legend: Whether to show a legend
            show_axes: Whether to show axes
            show_grid: Whether to show grid lines
            interactive: Whether the visualization is interactive
            interactions: List of enabled interaction types
            animation: Whether to animate transitions
            animation_duration: Duration of animations in milliseconds
            background_color: Background color (default based on theme)
            axis_labels: Dictionary mapping axis names to labels
            font_size: Base font size for text elements
            font_family: Font family for text elements
            title_font_size: Font size for titles
            responsive: Whether the visualization should resize
            smooth_curves: Whether to smooth curves in line charts
            tooltip_format: Format string for tooltips
            margin: Margins around the visualization
            **additional_options: Additional library-specific options
        """
        # Convert string enums to enum types
        self.theme = ThemeType(theme) if isinstance(theme, str) else theme
        self.chart_type = (
            ChartType(chart_type) if isinstance(chart_type, str) else chart_type
        )

        # Handle color palette
        if isinstance(color_palette, str):
            self.color_palette = COLOR_PALETTES.get(
                color_palette, COLOR_PALETTES["llamasearch"]
            )
        else:
            self.color_palette = color_palette

        # Basic display options
        self.show_legend = show_legend
        self.show_axes = show_axes
        self.show_grid = show_grid

        # Interactivity options
        self.interactive = interactive
        self.interactions = interactions or [
            Interaction.HOVER,
            Interaction.CLICK,
            Interaction.ZOOM,
        ]
        if isinstance(self.interactions[0], str):
            self.interactions = [Interaction(i) for i in self.interactions]

        # Animation options
        self.animation = animation
        self.animation_duration = animation_duration

        # Visual styling
        self.background_color = background_color or (
            "#ffffff"
            if self.theme == ThemeType.LIGHT
            else (
                "#1a1a1a" if self.theme == ThemeType.DARK else "#f6f6f9"
            )  # LlamaSearch light background
        )
        self.axis_labels = axis_labels or {"x": "X-Axis", "y": "Y-Axis", "z": "Z-Axis"}
        self.font_size = font_size
        self.font_family = font_family
        self.title_font_size = title_font_size

        # Layout options
        self.responsive = responsive
        self.smooth_curves = smooth_curves
        self.tooltip_format = tooltip_format
        self.margin = margin or {"top": 40, "right": 20, "bottom": 50, "left": 60}

        # Additional library-specific options
        self.additional_options = additional_options

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.

        Returns:
            Dictionary representation of the configuration
        """
        return {
            "theme": self.theme.value if isinstance(self.theme, Enum) else self.theme,
            "chart_type": (
                self.chart_type.value
                if isinstance(self.chart_type, Enum)
                else self.chart_type
            ),
            "color_palette": self.color_palette,
            "show_legend": self.show_legend,
            "show_axes": self.show_axes,
            "show_grid": self.show_grid,
            "interactive": self.interactive,
            "interactions": [
                i.value if isinstance(i, Enum) else i for i in self.interactions
            ],
            "animation": self.animation,
            "animation_duration": self.animation_duration,
            "background_color": self.background_color,
            "axis_labels": self.axis_labels,
            "font_size": self.font_size,
            "font_family": self.font_family,
            "title_font_size": self.title_font_size,
            "responsive": self.responsive,
            "smooth_curves": self.smooth_curves,
            "tooltip_format": self.tooltip_format,
            "margin": self.margin,
            **self.additional_options,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "VisualizationConfig":
        """
        Create a configuration object from a dictionary.

        Args:
            config_dict: Dictionary with configuration values

        Returns:
            New VisualizationConfig instance
        """
        # Extract additional options that aren't part of the standard parameters
        standard_params = {
            "theme",
            "chart_type",
            "color_palette",
            "show_legend",
            "show_axes",
            "show_grid",
            "interactive",
            "interactions",
            "animation",
            "animation_duration",
            "background_color",
            "axis_labels",
            "font_size",
            "font_family",
            "title_font_size",
            "responsive",
            "smooth_curves",
            "tooltip_format",
            "margin",
        }

        additional_options = {
            k: v for k, v in config_dict.items() if k not in standard_params
        }
        standard_config = {k: v for k, v in config_dict.items() if k in standard_params}

        return cls(**standard_config, **additional_options)

    def to_json(self) -> str:
        """
        Convert configuration to a JSON string.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "VisualizationConfig":
        """
        Create a configuration object from a JSON string.

        Args:
            json_str: JSON string with configuration values

        Returns:
            New VisualizationConfig instance
        """
        config_dict = json.loads(json_str)
        return cls.from_dict(config_dict)

    def update(self, **kwargs) -> "VisualizationConfig":
        """
        Update configuration with new values.

        Args:
            **kwargs: New configuration values

        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.additional_options[key] = value

        return self

    def __repr__(self) -> str:
        """String representation of the configuration."""
        theme = self.theme.value if isinstance(self.theme, Enum) else self.theme
        chart_type = (
            self.chart_type.value
            if isinstance(self.chart_type, Enum)
            else self.chart_type
        )
        return f"VisualizationConfig(theme='{theme}', chart_type='{chart_type}')"
