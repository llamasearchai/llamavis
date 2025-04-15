"""
Utility functions for LlamaVis.

This module provides helper functions for working with colors,
manipulating strings, and other common tasks needed by the visualization
library.
"""

import colorsys
import math
import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


def generate_color_scale(
    base_color: str,
    steps: int = 5,
    lighten: bool = True,
    saturation_adjust: float = 0.0,
) -> List[str]:
    """
    Generate a scale of colors from a base color.

    Args:
        base_color: Hex color code to use as base (e.g., "#FF5733")
        steps: Number of colors to generate
        lighten: Whether to lighten (True) or darken (False) the color
        saturation_adjust: Amount to adjust saturation (-1.0 to 1.0)

    Returns:
        List of hex color codes in the scale
    """
    # Convert hex to RGB
    base_color = base_color.lstrip("#")
    r, g, b = tuple(int(base_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert RGB to HSV
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    # Adjust saturation
    s = max(0, min(1, s + saturation_adjust))

    colors = []
    if lighten:
        # Create scale by varying value (brightness)
        for i in range(steps):
            # Calculate new value, keeping within 0-1 range
            new_v = min(1.0, v + (1.0 - v) * (i / (steps - 1)))
            # Convert back to RGB
            r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, new_v)
            # Convert to hex
            hex_color = f"#{int(r_new*255):02x}{int(g_new*255):02x}{int(b_new*255):02x}"
            colors.append(hex_color)
    else:
        # Create scale by darkening
        for i in range(steps):
            # Calculate new value, keeping within 0-1 range
            new_v = max(0.0, v * (1 - (i / (steps - 1))))
            # Convert back to RGB
            r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, new_v)
            # Convert to hex
            hex_color = f"#{int(r_new*255):02x}{int(g_new*255):02x}{int(b_new*255):02x}"
            colors.append(hex_color)

    return colors


def generate_contrasting_colors(
    count: int, base_hue: Optional[float] = None
) -> List[str]:
    """
    Generate visually distinct colors for categories.

    Args:
        count: Number of colors to generate
        base_hue: Starting hue value (0-1) or None for random

    Returns:
        List of hex color codes
    """
    if base_hue is None:
        base_hue = random.random()

    colors = []
    for i in range(count):
        # Use golden ratio to space hues evenly
        h = (base_hue + i * 0.618033988749895) % 1
        # Use high saturation and value for distinction
        s = 0.7 + random.random() * 0.3  # 0.7-1.0
        v = 0.85 + random.random() * 0.15  # 0.85-1.0

        # Convert to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Convert to hex
        hex_color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        colors.append(hex_color)

    return colors


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#ff0000' or '#f00')

    Returns:
        Tuple of (red, green, blue) values (0-255)

    Examples:
        >>> hex_to_rgb('#ff0000')
        (255, 0, 0)
        >>> hex_to_rgb('#f00')
        (255, 0, 0)
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex color string.

    Args:
        rgb: Tuple of (red, green, blue) values (0-255)

    Returns:
        Hex color string (e.g., '#ff0000')

    Examples:
        >>> rgb_to_hex((255, 0, 0))
        '#ff0000'
    """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """
    Convert hex color to rgba CSS string.

    Args:
        hex_color: Hex color string
        alpha: Alpha value (0.0-1.0)

    Returns:
        rgba CSS string (e.g., 'rgba(255, 0, 0, 0.5)')

    Examples:
        >>> hex_to_rgba('#ff0000', 0.5)
        'rgba(255, 0, 0, 0.5)'
    """
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r}, {g}, {b}, {alpha})"


def camel_to_snake(name: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        name: camelCase string

    Returns:
        snake_case string
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        name: snake_case string

    Returns:
        camelCase string
    """
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def truncate_string(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length, adding a suffix if truncated.

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def format_number(value: Union[int, float], precision: int = 2) -> str:
    """
    Format a number with appropriate suffixes for thousands, millions, etc.

    Args:
        value: Number to format
        precision: Decimal precision

    Returns:
        Formatted string
    """
    if abs(value) < 1000:
        return (
            f"{value:.{precision}f}".rstrip("0").rstrip(".")
            if "." in f"{value:.{precision}f}"
            else f"{value}"
        )

    for suffix in ["", "K", "M", "B", "T"]:
        if abs(value) < 1000:
            return f"{value:.{precision}f}".rstrip("0").rstrip(".") + suffix
        value /= 1000

    return f"{value:.{precision}f}".rstrip("0").rstrip(".") + "Q"


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format a datetime object as a string.

    Args:
        date: Datetime object
        format_str: String format (strftime format)

    Returns:
        Formatted date string
    """
    return date.strftime(format_str)


def is_dark_color(hex_color: str) -> bool:
    """
    Determine if a color is dark (for calculating contrasting text color).

    Args:
        hex_color: Hex color code (e.g., "#FF5733")

    Returns:
        True if the color is dark, False otherwise
    """
    r, g, b = hex_to_rgb(hex_color)
    # Calculate luminance using the formula for relative luminance in sRGB space
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5


def get_contrasting_text_color(background_color: str) -> str:
    """
    Get a contrasting text color (black or white) for a background color.

    Args:
        background_color: Hex color code for the background

    Returns:
        "#ffffff" for dark backgrounds, "#000000" for light backgrounds
    """
    return "#ffffff" if is_dark_color(background_color) else "#000000"


def interpolate_colors(color1: str, color2: str, steps: int) -> List[str]:
    """
    Generate a list of hex colors by interpolating between two colors.

    Args:
        color1: Starting hex color
        color2: Ending hex color
        steps: Number of colors to generate (including start and end)

    Returns:
        List of hex color strings

    Examples:
        >>> interpolate_colors('#ff0000', '#0000ff', 3)
        ['#ff0000', '#7f007f', '#0000ff']
    """
    if steps < 2:
        return [color1]

    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    # Convert to HSV for better interpolation
    hsv1 = colorsys.rgb_to_hsv(rgb1[0] / 255, rgb1[1] / 255, rgb1[2] / 255)
    hsv2 = colorsys.rgb_to_hsv(rgb2[0] / 255, rgb2[1] / 255, rgb2[2] / 255)

    # Adjust hue for shortest path
    if abs(hsv2[0] - hsv1[0]) > 0.5:
        if hsv1[0] > hsv2[0]:
            hsv2 = (hsv2[0] + 1, hsv2[1], hsv2[2])
        else:
            hsv1 = (hsv1[0] + 1, hsv1[1], hsv1[2])

    result = []
    for i in range(steps):
        # Linear interpolation
        t = i / (steps - 1)
        h = (hsv1[0] * (1 - t) + hsv2[0] * t) % 1
        s = hsv1[1] * (1 - t) + hsv2[1] * t
        v = hsv1[2] * (1 - t) + hsv2[2] * t

        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        # Convert to hex
        result.append(rgb_to_hex((int(r * 255), int(g * 255), int(b * 255))))

    return result


def normalize_data_for_display(
    values: List[Union[int, float]], min_size: float = 5.0, max_size: float = 50.0
) -> List[float]:
    """
    Normalize numeric values for display (e.g., for bubble chart point sizes).

    Args:
        values: List of numeric values
        min_size: Minimum size in the output range
        max_size: Maximum size in the output range

    Returns:
        List of normalized values
    """
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)

    if max_val == min_val:
        return [min_size + (max_size - min_size) / 2] * len(values)

    # Apply a square root scale to emphasize differences in smaller values
    normalized = []
    for v in values:
        # Normalize to 0-1 range
        norm = (v - min_val) / (max_val - min_val)
        # Apply square root scale and map to size range
        size = min_size + (max_size - min_size) * math.sqrt(norm)
        normalized.append(size)

    return normalized


def parse_css_size(size: str) -> Tuple[float, str]:
    """
    Parse a CSS size value into a number and unit.

    Args:
        size: CSS size string (e.g., "100px", "50%")

    Returns:
        Tuple of (numeric_value, unit)
    """
    match = re.match(r"^(\d+(?:\.\d+)?)([a-zA-Z%]*)$", size)
    if match:
        value = float(match.group(1))
        unit = match.group(2) or "px"  # Default to px if no unit
        return value, unit

    # Default fallback
    return 0, "px"


def safe_json_value(value: Any) -> Any:
    """
    Convert a value to a JSON-safe representation.

    Args:
        value: Any Python value

    Returns:
        JSON-safe representation of the value
    """
    if isinstance(value, (int, float, bool, str, type(None))):
        return value
    elif isinstance(value, (list, tuple)):
        return [safe_json_value(item) for item in value]
    elif isinstance(value, dict):
        return {str(k): safe_json_value(v) for k, v in value.items()}
    elif hasattr(value, "isoformat"):  # datetime, date, etc.
        return value.isoformat()
    else:
        return str(value)  # Fallback


def generate_unique_id(prefix: str = "llamavis") -> str:
    """
    Generate a unique ID for DOM elements.

    Args:
        prefix: Prefix for the ID

    Returns:
        Unique ID string
    """
    timestamp = int(datetime.now().timestamp() * 1000)
    random_part = random.randint(100000, 999999)
    return f"{prefix}_{timestamp}_{random_part}"


def generate_color_scale(
    n_colors: int,
    scheme: str = "spectrum",
    start_color: Optional[str] = None,
    end_color: Optional[str] = None,
) -> List[str]:
    """
    Generate a color scale with the specified number of colors.

    Args:
        n_colors: Number of colors to generate
        scheme: Color scheme to use
            - 'spectrum': Full spectrum of colors
            - 'rainbow': Rainbow colors
            - 'warm': Warm colors (reds, oranges, yellows)
            - 'cool': Cool colors (blues, greens, purples)
            - 'gradient': Gradient between start_color and end_color
        start_color: Starting color for 'gradient' scheme
        end_color: Ending color for 'gradient' scheme

    Returns:
        List of hex color strings
    """
    if n_colors < 1:
        return []

    if scheme == "gradient" and (start_color and end_color):
        return interpolate_colors(start_color, end_color, n_colors)

    # Preset color schemes
    schemes = {
        "spectrum": [
            "#ff0000",
            "#ff7f00",
            "#ffff00",
            "#00ff00",
            "#0000ff",
            "#4b0082",
            "#9400d3",
        ],
        "rainbow": [
            "#ff0000",
            "#ff7f00",
            "#ffff00",
            "#00ff00",
            "#00ffff",
            "#0000ff",
            "#8b00ff",
        ],
        "warm": ["#ff0000", "#ff4500", "#ff8c00", "#ffa500", "#ffd700", "#ffff00"],
        "cool": ["#0000ff", "#4169e1", "#00bfff", "#00ffff", "#00fa9a", "#00ff00"],
        "grayscale": ["#000000", "#333333", "#666666", "#999999", "#cccccc", "#ffffff"],
        "llamasearch": [
            "#5ba0d0",
            "#8ecae6",
            "#219ebc",
            "#023047",
            "#ffb703",
            "#fd9e02",
            "#fb8500",
        ],
    }

    # Default to spectrum if scheme not found
    base_colors = schemes.get(scheme, schemes["spectrum"])

    if n_colors <= len(base_colors):
        # Return a subset of the base colors
        return base_colors[:n_colors]

    # For more colors than in the base palette, interpolate
    result = []
    segments = len(base_colors) - 1
    colors_per_segment = n_colors // segments
    remainder = n_colors % segments

    for i in range(segments):
        segment_colors = colors_per_segment
        if i < remainder:
            segment_colors += 1

        if segment_colors == 1:
            result.append(base_colors[i])
        else:
            result.extend(
                interpolate_colors(base_colors[i], base_colors[i + 1], segment_colors)[
                    :-1
                ]
            )  # Exclude the last color to avoid duplication

    # Add the last base color
    result.append(base_colors[-1])

    return result[:n_colors]  # Ensure we return exactly n_colors


def generate_contrasting_colors(
    n_colors: int, seed: Optional[int] = None, min_distance: float = 0.25
) -> List[str]:
    """
    Generate n visually distinct colors with good contrast.

    Args:
        n_colors: Number of colors to generate
        seed: Random seed for reproducibility
        min_distance: Minimum distance between colors in HSV space

    Returns:
        List of hex color strings
    """
    if seed is not None:
        random.seed(seed)

    result = []
    max_attempts = 100

    # Golden ratio conjugate for even distribution
    golden_ratio_conjugate = 0.618033988749895

    h = random.random()  # Random starting hue

    for _ in range(n_colors):
        # Use golden ratio to pick evenly distributed colors
        h = (h + golden_ratio_conjugate) % 1.0

        # Fixed saturation and value for good visibility
        s = 0.65 + random.random() * 0.3  # 0.65-0.95
        v = 0.65 + random.random() * 0.3  # 0.65-0.95

        # Check distance from existing colors
        attempts = 0
        while attempts < max_attempts:
            # Check distance from existing colors
            too_close = False
            for existing_color in result:
                rgb = hex_to_rgb(existing_color)
                h_existing, s_existing, v_existing = colorsys.rgb_to_hsv(
                    rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
                )

                # Calculate distance in HSV space
                h_dist = min(abs(h - h_existing), 1 - abs(h - h_existing))
                s_dist = abs(s - s_existing)
                v_dist = abs(v - v_existing)

                if (
                    h_dist < min_distance
                    and s_dist < min_distance
                    and v_dist < min_distance
                ):
                    too_close = True
                    break

            if not too_close or attempts == max_attempts - 1:
                break

            # Adjust the hue and try again
            h = (h + 0.1) % 1.0
            s = 0.65 + random.random() * 0.3
            v = 0.65 + random.random() * 0.3
            attempts += 1

        # Convert to RGB and then to hex
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        hex_color = rgb_to_hex((int(r * 255), int(g * 255), int(b * 255)))
        result.append(hex_color)

    return result


def normalize_data(
    data: List[Union[int, float]],
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    out_min: float = 0.0,
    out_max: float = 1.0,
) -> List[float]:
    """
    Normalize a list of numeric values to a specified range.

    Args:
        data: List of numeric values to normalize
        min_val: Minimum value for normalization (default: min of data)
        max_val: Maximum value for normalization (default: max of data)
        out_min: Minimum value of output range
        out_max: Maximum value of output range

    Returns:
        List of normalized values
    """
    if not data:
        return []

    min_val = min_val if min_val is not None else min(data)
    max_val = max_val if max_val is not None else max(data)

    # Avoid division by zero
    if max_val == min_val:
        return [out_min for _ in data]

    return [
        out_min + (out_max - out_min) * (x - min_val) / (max_val - min_val)
        for x in data
    ]


def pivot_data_for_heatmap(
    data: List[Dict[str, Any]], x_key: str, y_key: str, value_key: str
) -> Dict[str, Any]:
    """
    Pivot data for heatmap visualization.

    Args:
        data: List of dictionaries with data points
        x_key: Key for x-axis values
        y_key: Key for y-axis values
        value_key: Key for cell values

    Returns:
        Dictionary with:
            - x_labels: List of unique x values
            - y_labels: List of unique y values
            - values: 2D array of values
    """
    # Extract unique x and y values
    x_values = list(sorted(set(item[x_key] for item in data)))
    y_values = list(sorted(set(item[y_key] for item in data)))

    # Initialize values array with zeros
    values = [[0 for _ in range(len(x_values))] for _ in range(len(y_values))]

    # Create lookup dictionaries for indices
    x_indices = {x: i for i, x in enumerate(x_values)}
    y_indices = {y: i for i, y in enumerate(y_values)}

    # Fill in the values
    for item in data:
        x_idx = x_indices[item[x_key]]
        y_idx = y_indices[item[y_key]]
        values[y_idx][x_idx] = item[value_key]

    return {"x_labels": x_values, "y_labels": y_values, "values": values}


def prepare_network_data(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    node_id_key: str = "id",
    source_key: str = "source",
    target_key: str = "target",
) -> Dict[str, Any]:
    """
    Prepare data for network visualizations.

    Args:
        nodes: List of node dictionaries
        edges: List of edge dictionaries
        node_id_key: Key for node ID in node dictionaries
        source_key: Key for source node ID in edge dictionaries
        target_key: Key for target node ID in edge dictionaries

    Returns:
        Dictionary with normalized data structure for network visualization
    """
    # Create normalized nodes list with consistent structure
    normalized_nodes = []
    node_indices = {}

    for i, node in enumerate(nodes):
        node_id = node[node_id_key]
        node_indices[node_id] = i

        normalized_node = {"id": node_id, "index": i}

        # Add all other properties from original node
        for key, value in node.items():
            if key != node_id_key:
                normalized_node[key] = value

        normalized_nodes.append(normalized_node)

    # Create normalized edges list
    normalized_edges = []

    for edge in edges:
        source_id = edge[source_key]
        target_id = edge[target_key]

        # Skip edges with missing nodes
        if source_id not in node_indices or target_id not in node_indices:
            continue

        normalized_edge = {
            "source": source_id,
            "source_index": node_indices[source_id],
            "target": target_id,
            "target_index": node_indices[target_id],
        }

        # Add all other properties from original edge
        for key, value in edge.items():
            if key not in [source_key, target_key]:
                normalized_edge[key] = value

        normalized_edges.append(normalized_edge)

    return {"nodes": normalized_nodes, "edges": normalized_edges}
