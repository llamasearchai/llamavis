"""
Three.js visualization integration for LlamaVis.

This module implements 3D visualizations using Three.js, providing
capabilities for 3D scatter plots, surfaces, and network visualizations.
"""

import json
import math
import uuid
from typing import Any, Dict, List, Optional, Union

from ..core.config import ChartType, VisualizationConfig
from ..core.data import DataProcessor
from ..core.utils import generate_unique_id, safe_json_value
from ..core.visualization import Visualization


class ThreeJSVisualization(Visualization):
    """
    Base class for Three.js visualizations.

    This class provides common functionality for visualizations
    implemented using Three.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "Three.js Visualization",
    ):
        """
        Initialize a Three.js visualization.

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
            config = VisualizationConfig(chart_type=ChartType.SCATTER)

        super().__init__(data, config, width, height, container_id, title)

    def get_library_includes(self) -> List[str]:
        """
        Get the JavaScript libraries required for this visualization.

        Returns:
            List of library names to include
        """
        libs = ["three"]

        # Add orbit controls for interactive visualizations
        if self.config.interactive:
            libs.append("three-orbit-controls")

        # Add other necessary Three.js extensions
        if self.config.chart_type == ChartType.NETWORK:
            libs.append("three-css2d")

        return libs

    def preprocess_data(self) -> Dict[str, Any]:
        """
        Preprocess the data for Three.js visualization.

        Returns:
            Preprocessed data ready for visualization
        """
        # Default preprocessing for most Three.js visualizations
        if self.config.chart_type == ChartType.NETWORK:
            return DataProcessor.prepare_for_network(self.data)

        # For standard 3D scatter or surface plots, just return as JSON
        return DataProcessor.to_json(self.data)


class Scatter3D(ThreeJSVisualization):
    """
    3D scatter plot visualization using Three.js.

    This class implements 3D scatter plot visualizations for multivariate
    data using Three.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "3D Scatter Plot",
    ):
        """
        Initialize a 3D scatter plot visualization.

        Args:
            data: Data for the 3D scatter plot (must have x, y, z columns)
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.SCATTER)
        else:
            # Ensure chart type is set to SCATTER
            config.update(chart_type=ChartType.SCATTER)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the 3D scatter plot visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the Three.js code for 3D scatter plot visualization
        js_code = f"""
        // Create a 3D scatter plot visualization
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
            
            // Create scene, camera, and renderer
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(config.background_color);
            
            const camera = new THREE.PerspectiveCamera(75, {self.width} / {self.height}, 0.1, 1000);
            camera.position.z = 5;
            camera.position.y = 2;
            camera.position.x = 2;
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize({self.width}, {self.height});
            container.appendChild(renderer.domElement);
            
            // Create orbit controls for interaction
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.enableZoom = true;
            
            // Create axis helpers
            if (config.show_axes) {{
                const axesHelper = new THREE.AxesHelper(5);
                scene.add(axesHelper);
                
                // Add axis labels if specified
                if (config.axis_labels) {{
                    // Create labels (simplified - in a real implementation, these would be
                    // proper CSS2D labels with proper positioning)
                    const axisLabels = [
                        {{ position: new THREE.Vector3(5.2, 0, 0), text: config.axis_labels.x || "X" }},
                        {{ position: new THREE.Vector3(0, 5.2, 0), text: config.axis_labels.y || "Y" }},
                        {{ position: new THREE.Vector3(0, 0, 5.2), text: config.axis_labels.z || "Z" }}
                    ];
                    
                    // In a real implementation, this would use CSS2DRenderer for proper labels
                }}
            }}
            
            // Create grid if specified
            if (config.show_grid) {{
                const gridHelper = new THREE.GridHelper(10, 10);
                gridHelper.rotation.x = Math.PI / 2;
                scene.add(gridHelper);
            }}
            
            // Process data points
            const points = data.map(point => ({{
                x: point.x || 0,
                y: point.y || 0,
                z: point.z || 0,
                color: point.color,
                size: point.size || 1,
                group: point.group,
                label: point.label
            }}));
            
            // Determine min/max for scaling
            let xMin = Infinity, xMax = -Infinity;
            let yMin = Infinity, yMax = -Infinity;
            let zMin = Infinity, zMax = -Infinity;
            
            points.forEach(point => {{
                xMin = Math.min(xMin, point.x);
                xMax = Math.max(xMax, point.x);
                yMin = Math.min(yMin, point.y);
                yMax = Math.max(yMax, point.y);
                zMin = Math.min(zMin, point.z);
                zMax = Math.max(zMax, point.z);
            }});
            
            // Scale function to map data coordinates to scene coordinates
            const scale = (value, min, max, targetMin = -4, targetMax = 4) => {{
                if (min === max) return (targetMin + targetMax) / 2;
                return targetMin + (value - min) * (targetMax - targetMin) / (max - min);
            }};
            
            // Group points by group for color assignment
            const groups = new Map();
            points.forEach(point => {{
                const group = point.group || "default";
                if (!groups.has(group)) {{
                    groups.set(group, []);
                }}
                groups.get(group).push(point);
            }});
            
            // Create geometries and materials for each group
            groups.forEach((groupPoints, groupName) => {{
                const positions = new Float32Array(groupPoints.length * 3);
                const sizes = new Float32Array(groupPoints.length);
                
                groupPoints.forEach((point, i) => {{
                    positions[i * 3] = scale(point.x, xMin, xMax);
                    positions[i * 3 + 1] = scale(point.y, yMin, yMax);
                    positions[i * 3 + 2] = scale(point.z, zMin, zMax);
                    sizes[i] = point.size * 5; // Scale up for visibility
                }});
                
                const geometry = new THREE.BufferGeometry();
                geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
                
                // Determine color for this group
                let color;
                if (groupName === "default") {{
                    color = config.color_palette[0];
                }} else {{
                    const groupIndex = [...groups.keys()].indexOf(groupName);
                    color = config.color_palette[groupIndex % config.color_palette.length];
                }}
                
                // Create material
                const material = new THREE.PointsMaterial({{
                    color: color,
                    size: 0.1,
                    sizeAttenuation: true,
                    transparent: true,
                    opacity: 0.8
                }});
                
                // Create point cloud
                const pointCloud = new THREE.Points(geometry, material);
                scene.add(pointCloud);
            }});
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                
                // Update controls
                if (config.animation) {{
                    controls.update();
                }}
                
                // Render scene
                renderer.render(scene, camera);
            }}
            
            // Handle window resize
            if (config.responsive) {{
                window.addEventListener('resize', () => {{
                    const width = container.clientWidth;
                    camera.aspect = width / {self.height};
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, {self.height});
                }});
            }}
            
            // Start animation loop
            animate();
        }})();
        """

        return js_code


class Network3D(ThreeJSVisualization):
    """
    3D network graph visualization using Three.js.

    This class implements 3D network/graph visualizations using Three.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "3D Network Graph",
    ):
        """
        Initialize a 3D network graph visualization.

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
        Generate JavaScript code for the 3D network graph visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the Three.js code for 3D network graph visualization
        js_code = f"""
        // Create a 3D network graph visualization
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
            
            // Create scene, camera, and renderer
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(config.background_color);
            
            const camera = new THREE.PerspectiveCamera(75, {self.width} / {self.height}, 0.1, 1000);
            camera.position.z = 15;
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize({self.width}, {self.height});
            container.appendChild(renderer.domElement);
            
            // Initialize CSS2D renderer for labels if needed
            let labelRenderer;
            if (config.show_labels) {{
                labelRenderer = new THREE.CSS2DRenderer();
                labelRenderer.setSize({self.width}, {self.height});
                labelRenderer.domElement.style.position = 'absolute';
                labelRenderer.domElement.style.top = '0';
                labelRenderer.domElement.style.pointerEvents = 'none';
                container.appendChild(labelRenderer.domElement);
            }}
            
            // Create orbit controls for interaction
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.enableZoom = true;
            
            // Extract nodes and links from data
            const nodes = data.nodes;
            const links = data.links;
            
            // Create a map of nodes for easy lookup
            const nodeMap = new Map();
            nodes.forEach(node => {{
                nodeMap.set(node.id, {{
                    ...node,
                    position: new THREE.Vector3(
                        (Math.random() - 0.5) * 10,
                        (Math.random() - 0.5) * 10,
                        (Math.random() - 0.5) * 10
                    )
                }});
            }});
            
            // Create materials for nodes and links
            const nodeMaterial = new THREE.MeshLambertMaterial({{
                color: config.color_palette[0]
            }});
            
            const linkMaterial = new THREE.LineBasicMaterial({{
                color: 0x999999,
                opacity: 0.6,
                transparent: true
            }});
            
            // Add nodes to the scene
            const nodeGroup = new THREE.Group();
            scene.add(nodeGroup);
            
            // Add a small sphere for each node
            for (const [id, node] of nodeMap.entries()) {{
                const nodeRadius = node.size || 0.5;
                const geometry = new THREE.SphereGeometry(nodeRadius, 16, 16);
                
                // Determine color for this node
                let nodeMat = nodeMaterial.clone();
                if (node.group) {{
                    const groupIndex = [...new Set(nodes.map(n => n.group))].indexOf(node.group);
                    nodeMat.color.set(config.color_palette[groupIndex % config.color_palette.length]);
                }}
                
                const mesh = new THREE.Mesh(geometry, nodeMat);
                mesh.position.copy(node.position);
                mesh.userData = {{ id, ...node }};
                nodeGroup.add(mesh);
                node.mesh = mesh;
                
                // Add label if configured
                if (config.show_labels) {{
                    const labelDiv = document.createElement('div');
                    labelDiv.className = 'node-label';
                    labelDiv.textContent = node.label || id;
                    labelDiv.style.color = '#ffffff';
                    labelDiv.style.fontSize = config.font_size + 'px';
                    labelDiv.style.fontFamily = config.font_family;
                    labelDiv.style.padding = '2px';
                    labelDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.6)';
                    labelDiv.style.borderRadius = '2px';
                    
                    const label = new THREE.CSS2DObject(labelDiv);
                    label.position.copy(node.position);
                    label.position.y += nodeRadius + 0.5;
                    mesh.add(label);
                }}
            }}
            
            // Add links to the scene
            const linkGroup = new THREE.Group();
            scene.add(linkGroup);
            
            for (const link of links) {{
                const sourceNode = nodeMap.get(link.source);
                const targetNode = nodeMap.get(link.target);
                
                if (sourceNode && targetNode) {{
                    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                        sourceNode.position,
                        targetNode.position
                    ]);
                    
                    // Create line with appropriate width
                    const lineWidth = link.value || 1;
                    const lineMat = linkMaterial.clone();
                    lineMat.linewidth = lineWidth;
                    
                    const line = new THREE.Line(lineGeometry, lineMat);
                    line.userData = {{ ...link }};
                    linkGroup.add(line);
                    
                    // Store reference to line for updates
                    link.line = line;
                }}
            }}
            
            // Add lights to the scene
            const ambientLight = new THREE.AmbientLight(0xcccccc, 0.5);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.7);
            directionalLight.position.set(1, 1, 1).normalize();
            scene.add(directionalLight);
            
            // Simple force simulation for layout
            if (config.animation) {{
                // Apply forces to nodes
                function applyForces() {{
                    const repulsionForce = 1;
                    const attractionForce = 0.05;
                    const centeringForce = 0.05;
                    
                    // Apply centering force
                    for (const [id, node] of nodeMap.entries()) {{
                        const dist = node.position.length();
                        const force = dist * centeringForce;
                        const dir = node.position.clone().normalize().multiplyScalar(-force);
                        node.position.add(dir);
                    }}
                    
                    // Apply node-node repulsion
                    for (const [id1, node1] of nodeMap.entries()) {{
                        for (const [id2, node2] of nodeMap.entries()) {{
                            if (id1 === id2) continue;
                            
                            const diff = node1.position.clone().sub(node2.position);
                            const dist = diff.length();
                            
                            if (dist > 0 && dist < 6) {{
                                const force = repulsionForce / (dist * dist);
                                const dir = diff.normalize().multiplyScalar(force);
                                node1.position.add(dir);
                                node2.position.sub(dir);
                            }}
                        }}
                    }}
                    
                    // Apply link attraction
                    for (const link of links) {{
                        const sourceNode = nodeMap.get(link.source);
                        const targetNode = nodeMap.get(link.target);
                        
                        if (sourceNode && targetNode) {{
                            const diff = sourceNode.position.clone().sub(targetNode.position);
                            const dist = diff.length();
                            const force = dist * attractionForce;
                            const dir = diff.normalize().multiplyScalar(force);
                            
                            sourceNode.position.sub(dir);
                            targetNode.position.add(dir);
                        }}
                    }}
                }}
                
                // Update positions of nodes and links
                function updatePositions() {{
                    // Update node positions
                    for (const [id, node] of nodeMap.entries()) {{
                        if (node.mesh) {{
                            node.mesh.position.copy(node.position);
                        }}
                    }}
                    
                    // Update link positions
                    for (const link of links) {{
                        if (link.line) {{
                            const sourceNode = nodeMap.get(link.source);
                            const targetNode = nodeMap.get(link.target);
                            
                            if (sourceNode && targetNode) {{
                                const positions = new Float32Array([
                                    sourceNode.position.x, sourceNode.position.y, sourceNode.position.z,
                                    targetNode.position.x, targetNode.position.y, targetNode.position.z
                                ]);
                                
                                link.line.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                                link.line.geometry.attributes.position.needsUpdate = true;
                            }}
                        }}
                    }}
                }}
                
                // Apply initial forces immediately
                for (let i = 0; i < 100; i++) {{
                    applyForces();
                }}
                updatePositions();
            }}
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                
                // Update controls
                controls.update();
                
                // Apply forces if animation is enabled
                if (config.animation) {{
                    applyForces();
                    updatePositions();
                }}
                
                // Render scene
                renderer.render(scene, camera);
                
                // Render labels if enabled
                if (config.show_labels && labelRenderer) {{
                    labelRenderer.render(scene, camera);
                }}
            }}
            
            // Handle window resize
            if (config.responsive) {{
                window.addEventListener('resize', () => {{
                    const width = container.clientWidth;
                    camera.aspect = width / {self.height};
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, {self.height});
                    
                    if (labelRenderer) {{
                        labelRenderer.setSize(width, {self.height});
                    }}
                }});
            }}
            
            // Start animation loop
            animate();
        }})();
        """

        return js_code


class Surface3D(ThreeJSVisualization):
    """
    3D surface plot visualization using Three.js.

    This class implements 3D surface plot visualizations for 2D data
    using Three.js.
    """

    def __init__(
        self,
        data: Any,
        config: Optional[VisualizationConfig] = None,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "3D Surface Plot",
    ):
        """
        Initialize a 3D surface plot visualization.

        Args:
            data: Data for the 3D surface plot (must be a 2D array or a function)
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        # Create default config if none provided
        if config is None:
            config = VisualizationConfig(chart_type=ChartType.SURFACE)
        else:
            # Ensure chart type is set to SURFACE
            config.update(chart_type=ChartType.SURFACE)

        super().__init__(data, config, width, height, container_id, title)

    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the 3D surface plot visualization.

        Returns:
            JavaScript code as a string
        """
        # Define the Three.js code for 3D surface plot visualization
        js_code = f"""
        // Create a 3D surface plot visualization
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
            
            // Create scene, camera, and renderer
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(config.background_color);
            
            const camera = new THREE.PerspectiveCamera(75, {self.width} / {self.height}, 0.1, 1000);
            camera.position.z = 10;
            camera.position.y = 5;
            camera.position.x = 5;
            
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize({self.width}, {self.height});
            container.appendChild(renderer.domElement);
            
            // Create orbit controls for interaction
            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.25;
            controls.enableZoom = true;
            
            // Create axis helpers
            if (config.show_axes) {{
                const axesHelper = new THREE.AxesHelper(5);
                scene.add(axesHelper);
            }}
            
            // Create grid if specified
            if (config.show_grid) {{
                const gridHelper = new THREE.GridHelper(10, 10);
                scene.add(gridHelper);
            }}
            
            // Extract data and create surface
            let surfaceData;
            if (typeof data === 'function') {{
                // Function-based data
                surfaceData = [];
                const resolution = 50;
                const xRange = [-5, 5];
                const zRange = [-5, 5];
                
                for (let i = 0; i < resolution; i++) {{
                    const x = xRange[0] + i * (xRange[1] - xRange[0]) / (resolution - 1);
                    surfaceData[i] = [];
                    
                    for (let j = 0; j < resolution; j++) {{
                        const z = zRange[0] + j * (zRange[1] - zRange[0]) / (resolution - 1);
                        const y = data(x, z);
                        surfaceData[i][j] = y;
                    }}
                }}
            }} else if (Array.isArray(data) && Array.isArray(data[0])) {{
                // 2D array data
                surfaceData = data;
            }} else {{
                // Default to simple function if input data is not usable
                surfaceData = [];
                const resolution = 50;
                const xRange = [-5, 5];
                const zRange = [-5, 5];
                
                for (let i = 0; i < resolution; i++) {{
                    const x = xRange[0] + i * (xRange[1] - xRange[0]) / (resolution - 1);
                    surfaceData[i] = [];
                    
                    for (let j = 0; j < resolution; j++) {{
                        const z = zRange[0] + j * (zRange[1] - zRange[0]) / (resolution - 1);
                        const y = Math.sin(Math.sqrt(x*x + z*z) * 0.5);
                        surfaceData[i][j] = y;
                    }}
                }}
            }}
            
            // Determine surface dimensions
            const width = surfaceData.length;
            const depth = surfaceData[0].length;
            
            // Find min/max heights for scaling
            let minHeight = Infinity;
            let maxHeight = -Infinity;
            
            for (let i = 0; i < width; i++) {{
                for (let j = 0; j < depth; j++) {{
                    minHeight = Math.min(minHeight, surfaceData[i][j]);
                    maxHeight = Math.max(maxHeight, surfaceData[i][j]);
                }}
            }}
            
            // Create surface geometry
            const geometry = new THREE.PlaneGeometry(10, 10, width - 1, depth - 1);
            
            // Update vertices based on data
            const positions = geometry.attributes.position.array;
            
            for (let i = 0; i < width; i++) {{
                for (let j = 0; j < depth; j++) {{
                    const index = (i * depth + j) * 3;
                    positions[index + 1] = (surfaceData[i][j] - minHeight) / (maxHeight - minHeight) * 5;
                }}
            }}
            
            geometry.attributes.position.needsUpdate = true;
            geometry.computeVertexNormals();
            
            // Create color gradient based on height
            const colors = new Float32Array(width * depth * 3);
            
            for (let i = 0; i < width; i++) {{
                for (let j = 0; j < depth; j++) {{
                    const index = (i * depth + j) * 3;
                    
                    // Normalize height to 0-1 range
                    const heightRatio = (surfaceData[i][j] - minHeight) / (maxHeight - minHeight);
                    
                    // Get color from palette (simple interpolation between two colors)
                    const colorIndex = Math.min(
                        Math.floor(heightRatio * config.color_palette.length),
                        config.color_palette.length - 1
                    );
                    
                    // Parse hex color
                    const hex = config.color_palette[colorIndex].replace('#', '');
                    const r = parseInt(hex.substring(0, 2), 16) / 255;
                    const g = parseInt(hex.substring(2, 4), 16) / 255;
                    const b = parseInt(hex.substring(4, 6), 16) / 255;
                    
                    colors[index] = r;
                    colors[index + 1] = g;
                    colors[index + 2] = b;
                }}
            }}
            
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            
            // Create material
            const material = new THREE.MeshPhongMaterial({{
                vertexColors: true,
                side: THREE.DoubleSide,
                flatShading: false,
                shininess: 30
            }});
            
            // Create mesh
            const surface = new THREE.Mesh(geometry, material);
            scene.add(surface);
            
            // Rotate to a more natural orientation
            surface.rotation.x = -Math.PI / 2;
            
            // Add lights to the scene
            const ambientLight = new THREE.AmbientLight(0xcccccc, 0.5);
            scene.add(ambientLight);
            
            const directionalLight = new THREE.DirectionalLight(0xffffff, 0.7);
            directionalLight.position.set(1, 1, 1).normalize();
            scene.add(directionalLight);
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                
                // Update controls
                controls.update();
                
                // Optional: add animation effect
                if (config.animation) {{
                    // Subtle wave animation as an example
                    const time = Date.now() * 0.001;
                    
                    for (let i = 0; i < width; i++) {{
                        for (let j = 0; j < depth; j++) {{
                            const index = (i * depth + j) * 3;
                            const originalHeight = (surfaceData[i][j] - minHeight) / (maxHeight - minHeight) * 5;
                            const waveEffect = Math.sin(i * 0.5 + time) * Math.cos(j * 0.5 + time) * 0.1;
                            positions[index + 1] = originalHeight + waveEffect;
                        }}
                    }}
                    
                    geometry.attributes.position.needsUpdate = true;
                    geometry.computeVertexNormals();
                }}
                
                // Render scene
                renderer.render(scene, camera);
            }}
            
            // Handle window resize
            if (config.responsive) {{
                window.addEventListener('resize', () => {{
                    const width = container.clientWidth;
                    camera.aspect = width / {self.height};
                    camera.updateProjectionMatrix();
                    renderer.setSize(width, {self.height});
                }});
            }}
            
            // Start animation loop
            animate();
        }})();
        """

        return js_code
