"""
D3.js visualization integration for LlamaVis.

This module implements visualizations using D3.js, providing network graphs,
hierarchical visualizations, and other advanced chart types.
"""

import json
import uuid
from typing import Any, Dict, List, Optional, Union

from ..core.config import ChartType, VisualizationConfig
from ..core.data import DataProcessor
from ..core.utils import generate_unique_id
from ..core.visualization import Visualization


class D3Visualization(Visualization):
    """
    Base class for D3.js visualizations.

    This class provides common functionality for visualizations
    implemented using D3.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 500,
        container_id: Optional[str] = None,
        title: str = "D3.js Visualization",
    ):
        """
        Initialize a D3.js visualization.

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
            config = VisualizationConfig(chart_type=ChartType.NETWORK)

        super().__init__(data, config, width, height, container_id, title)

    def get_library_includes(self) -> List[str]:
        """
        Get the JavaScript libraries required for this visualization.

        Returns:
            List of library names to include
        """
        libs = ["d3"]

        # Add additional libraries based on chart type
        if self.config.chart_type in [ChartType.FORCE_DIRECTED, ChartType.NETWORK]:
            libs.append("d3-force")

        return libs

    def preprocess_data(self) -> Dict[str, Any]:
        """
        Preprocess the data for D3.js visualization.

        Returns:
            Preprocessed data ready for visualization
        """
        # Default preprocessing for most D3 visualizations
        if (
            self.config.chart_type == ChartType.NETWORK
            or self.config.chart_type == ChartType.FORCE_DIRECTED
        ):
            return DataProcessor.prepare_for_network(self.data)
        elif (
            self.config.chart_type == ChartType.TREE
            or self.config.chart_type == ChartType.TREEMAP
        ):
            return DataProcessor.prepare_for_hierarchical(self.data)
        elif self.config.chart_type == ChartType.HEATMAP:
            return DataProcessor.prepare_for_heatmap(self.data)
        else:
            # Default to returning data as is
            return DataProcessor.to_json(self.data)


class NetworkGraph(D3Visualization):
    """
    Network graph visualization using D3.js.

    This class implements network/graph visualizations using D3.js
    force-directed layout algorithm.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 500,
        container_id: Optional[str] = None,
        title: str = "Network Graph",
    ):
        """
        Initialize a network graph visualization.

        Args:
            data: Network data (nodes and links)
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.NETWORK)
        else:
            # Ensure chart type is set to NETWORK
            config.update(chart_type=ChartType.NETWORK)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the network graph visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the D3.js code for force-directed network graph
        js_code = f"""
        // Create a force-directed network graph
        (function() {{
            const width = {self.width};
            const height = {self.height};
            const container = d3.select("#{self.container_id}");
            
            // Clear previous content
            container.html("");
            
            // Add title if specified
            if ("{self.title}") {{
                container.append("h3")
                    .attr("class", "vis-title")
                    .style("text-align", "center")
                    .style("margin-bottom", "20px")
                    .style("font-family", config.font_family)
                    .style("font-size", config.title_font_size + "px")
                    .text("{self.title}");
            }}
            
            // Create SVG element
            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;");
            
            // Extract nodes and links from data
            const nodes = data.nodes;
            const links = data.links;
            
            // Define color scale for nodes
            const colorScale = d3.scaleOrdinal()
                .domain(nodes.map(d => d.group || "default"))
                .range(config.color_palette);
            
            // Create a simulation with forces
            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id))
                .force("charge", d3.forceManyBody().strength(-100))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collide", d3.forceCollide().radius(d => d.radius || 10));
            
            // Create links
            const link = svg.append("g")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .selectAll("line")
                .data(links)
                .join("line")
                .attr("stroke-width", d => Math.sqrt(d.value || 1));
            
            // Create nodes
            const node = svg.append("g")
                .attr("stroke", "#fff")
                .attr("stroke-width", 1.5)
                .selectAll("circle")
                .data(nodes)
                .join("circle")
                .attr("r", d => d.radius || 5)
                .attr("fill", d => colorScale(d.group || "default"))
                .call(drag(simulation));
            
            // Add tooltip for nodes
            if (config.interactive) {{
                node.append("title")
                    .text(d => d.id);
            }}
            
            // Add labels if configured
            if (config.show_labels) {{
                const labels = svg.append("g")
                    .attr("font-family", config.font_family)
                    .attr("font-size", config.font_size)
                    .selectAll("text")
                    .data(nodes)
                    .join("text")
                    .attr("dx", 12)
                    .attr("dy", ".35em")
                    .text(d => d.label || d.id);
                
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                    
                    labels
                        .attr("x", d => d.x)
                        .attr("y", d => d.y);
                }});
            }} else {{
                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                    
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                }});
            }}
            
            // Implement drag functionality
            function drag(simulation) {{
                function dragstarted(event) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    event.subject.fx = event.subject.x;
                    event.subject.fy = event.subject.y;
                }}
                
                function dragged(event) {{
                    event.subject.fx = event.x;
                    event.subject.fy = event.y;
                }}
                
                function dragended(event) {{
                    if (!event.active) simulation.alphaTarget(0);
                    event.subject.fx = null;
                    event.subject.fy = null;
                }}
                
                return d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended);
            }}
            
            // Implement zoom functionality if enabled
            if (config.interactions.includes("zoom")) {{
                const zoom = d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on("zoom", (event) => {{
                        svg.select("g").attr("transform", event.transform);
                    }});
                
                svg.call(zoom);
            }}
        }})();
        """

        return js_code


class TreeVis(D3Visualization):
    """
    Tree visualization using D3.js.

    This class implements hierarchical tree visualizations using D3.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "Hierarchical Tree",
    ):
        """
        Initialize a hierarchical tree visualization.

        Args:
            data: Hierarchical data
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.TREE)
        else:
            # Ensure chart type is set to TREE
            config.update(chart_type=ChartType.TREE)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the tree visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the D3.js code for tree visualization
        js_code = f"""
        // Create a hierarchical tree visualization
        (function() {{
            const width = {self.width};
            const height = {self.height};
            const container = d3.select("#{self.container_id}");
            
            // Clear previous content
            container.html("");
            
            // Add title if specified
            if ("{self.title}") {{
                container.append("h3")
                    .attr("class", "vis-title")
                    .style("text-align", "center")
                    .style("margin-bottom", "20px")
                    .style("font-family", config.font_family)
                    .style("font-size", config.title_font_size + "px")
                    .text("{self.title}");
            }}
            
            // Create SVG element
            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;");
            
            // Create a group for the tree
            const g = svg.append("g")
                .attr("transform", `translate(40, 0)`);
            
            // Create a hierarchical data structure
            const root = d3.hierarchy(data);
            
            // Set the size of the tree layout
            const treeLayout = d3.tree()
                .size([height - 100, width - 160]);
            
            // Compute the tree layout
            treeLayout(root);
            
            // Define color scale for nodes
            const colorScale = d3.scaleOrdinal()
                .domain(root.descendants().map(d => d.depth))
                .range(config.color_palette);
            
            // Create links
            g.selectAll(".link")
                .data(root.links())
                .join("path")
                .attr("class", "link")
                .attr("d", d3.linkHorizontal()
                    .x(d => d.y)
                    .y(d => d.x))
                .attr("fill", "none")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .attr("stroke-width", 1.5);
            
            // Create nodes
            const node = g.selectAll(".node")
                .data(root.descendants())
                .join("g")
                .attr("class", "node")
                .attr("transform", d => `translate(${{d.y}},${{d.x}})`);
            
            // Add circles for nodes
            node.append("circle")
                .attr("r", 5)
                .attr("fill", d => colorScale(d.depth))
                .attr("stroke", "#fff")
                .attr("stroke-width", 1.5);
            
            // Add labels for nodes
            node.append("text")
                .attr("dy", "0.31em")
                .attr("x", d => d.children ? -8 : 8)
                .attr("text-anchor", d => d.children ? "end" : "start")
                .text(d => d.data.name)
                .attr("font-family", config.font_family)
                .attr("font-size", config.font_size + "px")
                .clone(true).lower()
                .attr("stroke", "white")
                .attr("stroke-width", 3);
            
            // Implement zoom functionality if enabled
            if (config.interactions.includes("zoom")) {{
                const zoom = d3.zoom()
                    .scaleExtent([0.1, 3])
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});
                
                svg.call(zoom);
            }}
        }})();
        """

        return js_code


class TreemapVis(D3Visualization):
    """
    Treemap visualization using D3.js.

    This class implements treemap visualizations for hierarchical data
    using D3.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "Treemap",
    ):
        """
        Initialize a treemap visualization.

        Args:
            data: Hierarchical data
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.TREEMAP)
        else:
            # Ensure chart type is set to TREEMAP
            config.update(chart_type=ChartType.TREEMAP)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the treemap visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the D3.js code for treemap visualization
        js_code = f"""
        // Create a treemap visualization
        (function() {{
            const width = {self.width};
            const height = {self.height};
            const container = d3.select("#{self.container_id}");
            
            // Clear previous content
            container.html("");
            
            // Add title if specified
            if ("{self.title}") {{
                container.append("h3")
                    .attr("class", "vis-title")
                    .style("text-align", "center")
                    .style("margin-bottom", "20px")
                    .style("font-family", config.font_family)
                    .style("font-size", config.title_font_size + "px")
                    .text("{self.title}");
            }}
            
            // Create SVG element
            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;");
            
            // Create a group for the treemap
            const g = svg.append("g");
            
            // Create a hierarchical data structure
            const hierarchy = d3.hierarchy(data)
                .sum(d => d.value || 1)
                .sort((a, b) => b.value - a.value);
            
            // Create a treemap layout
            const treemap = d3.treemap()
                .size([width, height - 50])
                .paddingOuter(3)
                .paddingTop(19)
                .paddingInner(1)
                .round(true);
            
            // Compute the treemap layout
            const root = treemap(hierarchy);
            
            // Define color scale
            const colorScale = d3.scaleOrdinal()
                .domain(root.children.map(d => d.data.name))
                .range(config.color_palette);
            
            // Create leaf nodes
            const leaf = g.selectAll("g")
                .data(root.leaves())
                .join("g")
                .attr("transform", d => `translate(${{d.x0}},${{d.y0}})`);
            
            // Create rectangles for leaf nodes
            leaf.append("rect")
                .attr("width", d => d.x1 - d.x0)
                .attr("height", d => d.y1 - d.y0)
                .attr("fill", d => {{
                    while (d.depth > 1) d = d.parent;
                    return colorScale(d.data.name);
                }})
                .attr("fill-opacity", 0.8)
                .attr("stroke", "#fff");
            
            // Add labels for leaf nodes if there's enough space
            leaf.append("text")
                .attr("x", 3)
                .attr("y", "1.1em")
                .text(d => d.data.name)
                .attr("font-family", config.font_family)
                .attr("font-size", config.font_size + "px")
                .attr("fill", "white")
                .each(function(d) {{
                    const t = d3.select(this);
                    const rect = d3.select(this.parentNode).select("rect");
                    const rectWidth = rect.attr("width");
                    const rectHeight = rect.attr("height");
                    
                    // Hide text if it doesn't fit in the rectangle
                    if (this.getComputedTextLength() > rectWidth || 
                        parseInt(rectHeight) < config.font_size * 1.5) {{
                        t.remove();
                    }}
                }});
            
            // Add titles (categories) for parent nodes
            g.selectAll(".parent-label")
                .data(root.descendants().filter(d => d.depth === 1))
                .join("text")
                .attr("class", "parent-label")
                .attr("x", d => d.x0 + 3)
                .attr("y", d => d.y0 + 14)
                .attr("font-family", config.font_family)
                .attr("font-size", (config.font_size + 2) + "px")
                .attr("font-weight", "bold")
                .text(d => d.data.name)
                .attr("fill", "#000");
            
            // Add tooltips for all nodes
            if (config.interactive) {{
                leaf.append("title")
                    .text(d => `${{d.ancestors().reverse().map(d => d.data.name).join("/")}}\nValue: ${{d.value}}`);
            }}
        }})();
        """

        return js_code


class HeatmapVis(D3Visualization):
    """
    Heatmap visualization using D3.js.

    This class implements heatmap visualizations using D3.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "Heatmap",
    ):
        """
        Initialize a heatmap visualization.

        Args:
            data: Data for the heatmap
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.HEATMAP)
        else:
            # Ensure chart type is set to HEATMAP
            config.update(chart_type=ChartType.HEATMAP)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the heatmap visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the D3.js code for heatmap visualization
        js_code = f"""
        // Create a heatmap visualization
        (function() {{
            const width = {self.width};
            const height = {self.height};
            const container = d3.select("#{self.container_id}");
            
            // Clear previous content
            container.html("");
            
            // Add title if specified
            if ("{self.title}") {{
                container.append("h3")
                    .attr("class", "vis-title")
                    .style("text-align", "center")
                    .style("margin-bottom", "20px")
                    .style("font-family", config.font_family)
                    .style("font-size", config.title_font_size + "px")
                    .text("{self.title}");
            }}
            
            // Extract data
            const x_labels = data.x_labels;
            const y_labels = data.y_labels;
            const values = data.values;
            
            // Define margins
            const margin = {{top: 50, right: 50, bottom: 100, left: 100}};
            const innerWidth = width - margin.left - margin.right;
            const innerHeight = height - margin.top - margin.bottom;
            
            // Create SVG element
            const svg = container.append("svg")
                .attr("width", width)
                .attr("height", height)
                .attr("viewBox", [0, 0, width, height])
                .attr("style", "max-width: 100%; height: auto;");
            
            // Create a group for the heatmap
            const g = svg.append("g")
                .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
            
            // Calculate cell size
            const cellWidth = innerWidth / x_labels.length;
            const cellHeight = innerHeight / y_labels.length;
            
            // Find min and max values for color scale
            let minValue = Infinity;
            let maxValue = -Infinity;
            
            for (const row of values) {{
                for (const value of row) {{
                    minValue = Math.min(minValue, value);
                    maxValue = Math.max(maxValue, value);
                }}
            }}
            
            // Define color scale
            let colorScale;
            if (config.color_palette === "sequential") {{
                colorScale = d3.scaleSequential()
                    .domain([minValue, maxValue])
                    .interpolator(d3.interpolateBlues);
            }} else if (config.color_palette === "diverging") {{
                const middle = (minValue + maxValue) / 2;
                colorScale = d3.scaleDiverging()
                    .domain([minValue, middle, maxValue])
                    .interpolator(d3.interpolateRdBu);
            }} else {{
                // Default to custom color palette
                colorScale = d3.scaleSequential()
                    .domain([minValue, maxValue])
                    .interpolator(d3.interpolateRgb(
                        config.color_palette[0] || "#f7fbff", 
                        config.color_palette[config.color_palette.length - 1] || "#08306b"
                    ));
            }}
            
            // Create x scale
            const xScale = d3.scaleBand()
                .domain(x_labels)
                .range([0, innerWidth])
                .padding(0.05);
            
            // Create y scale
            const yScale = d3.scaleBand()
                .domain(y_labels)
                .range([0, innerHeight])
                .padding(0.05);
            
            // Create x axis
            const xAxis = g.append("g")
                .attr("transform", `translate(0,${{innerHeight}})`)
                .call(d3.axisBottom(xScale))
                .call(g => g.select(".domain").remove());
            
            // Rotate x axis labels if needed
            if (x_labels.length > 10) {{
                xAxis.selectAll("text")
                    .attr("transform", "rotate(-45)")
                    .attr("text-anchor", "end")
                    .attr("dx", "-.8em")
                    .attr("dy", ".15em");
            }}
            
            // Create y axis
            g.append("g")
                .call(d3.axisLeft(yScale))
                .call(g => g.select(".domain").remove());
            
            // Create cells
            const cells = g.append("g")
                .selectAll("rect")
                .data(values.flatMap((row, i) => 
                    row.map((value, j) => ({{
                        value,
                        row: i,
                        col: j,
                        x: xScale(x_labels[j]),
                        y: yScale(y_labels[i]),
                        width: xScale.bandwidth(),
                        height: yScale.bandwidth()
                    }}))
                ))
                .join("rect")
                .attr("x", d => d.x)
                .attr("y", d => d.y)
                .attr("width", d => d.width)
                .attr("height", d => d.height)
                .attr("fill", d => colorScale(d.value))
                .attr("stroke", "#fff")
                .attr("stroke-width", 0.5);
            
            // Add tooltips
            if (config.interactive) {{
                cells.append("title")
                    .text(d => `${{y_labels[d.row]}}, ${{x_labels[d.col]}}: ${{d.value}}`);
                
                // Or use mouseover for more complex tooltips
                const tooltip = container.append("div")
                    .attr("class", "tooltip")
                    .style("position", "absolute")
                    .style("visibility", "hidden")
                    .style("background-color", "white")
                    .style("border", "1px solid #ddd")
                    .style("padding", "5px")
                    .style("border-radius", "5px")
                    .style("pointer-events", "none");
                
                cells
                    .on("mouseover", (event, d) => {{
                        tooltip
                            .style("visibility", "visible")
                            .html(`<strong>${{y_labels[d.row]}}, ${{x_labels[d.col]}}</strong><br/>Value: ${{d.value.toFixed(2)}}`);
                    }})
                    .on("mousemove", (event) => {{
                        tooltip
                            .style("top", (event.pageY - 10) + "px")
                            .style("left", (event.pageX + 10) + "px");
                    }})
                    .on("mouseout", () => {{
                        tooltip.style("visibility", "hidden");
                    }});
            }}
            
            // Add color legend
            const legendWidth = innerWidth * 0.6;
            const legendHeight = 20;
            
            const legendX = innerWidth / 2 - legendWidth / 2;
            const legendY = innerHeight + 50;
            
            // Create gradient for legend
            const defs = svg.append("defs");
            
            const gradient = defs.append("linearGradient")
                .attr("id", "color-gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "0%");
            
            if (config.color_palette === "diverging") {{
                gradient.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", colorScale(minValue));
                
                gradient.append("stop")
                    .attr("offset", "50%")
                    .attr("stop-color", colorScale((minValue + maxValue) / 2));
                
                gradient.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", colorScale(maxValue));
            }} else {{
                gradient.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", colorScale(minValue));
                
                gradient.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", colorScale(maxValue));
            }}
            
            // Add rectangle with gradient
            g.append("rect")
                .attr("x", legendX)
                .attr("y", legendY)
                .attr("width", legendWidth)
                .attr("height", legendHeight)
                .style("fill", "url(#color-gradient)");
            
            // Add legend axis
            const legendScale = d3.scaleLinear()
                .domain([minValue, maxValue])
                .range([0, legendWidth]);
            
            g.append("g")
                .attr("transform", `translate(${{legendX}},${{legendY + legendHeight}})`)
                .call(d3.axisBottom(legendScale).ticks(5).tickFormat(d3.format(".1f")));
            
            // Add legend title
            g.append("text")
                .attr("x", legendX + legendWidth / 2)
                .attr("y", legendY - 5)
                .attr("text-anchor", "middle")
                .attr("font-family", config.font_family)
                .attr("font-size", config.font_size + "px")
                .text("Value");
            
            // Add axis labels if provided
            if (config.axis_labels) {{
                // X-axis label
                g.append("text")
                    .attr("x", innerWidth / 2)
                    .attr("y", innerHeight + margin.top + 20)
                    .attr("text-anchor", "middle")
                    .attr("font-family", config.font_family)
                    .attr("font-size", config.font_size + "px")
                    .text(config.axis_labels.x || "X-Axis");
                
                // Y-axis label
                g.append("text")
                    .attr("transform", "rotate(-90)")
                    .attr("x", -innerHeight / 2)
                    .attr("y", -margin.left + 30)
                    .attr("text-anchor", "middle")
                    .attr("font-family", config.font_family)
                    .attr("font-size", config.font_size + "px")
                    .text(config.axis_labels.y || "Y-Axis");
            }}
        }})();
        """

        return js_code
