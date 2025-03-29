"""
Renderer module for LlamaVis visualizations.

This module provides a Renderer class that handles generating HTML,
embedding JavaScript libraries, and creating standalone HTML files
from visualizations.
"""

import os
import json
import webbrowser
from typing import Dict, List, Optional, Union, Any


class Renderer:
    """Class for rendering visualizations to HTML and other formats."""
    
    # CDN URLs for common visualization libraries
    CDN_URLS = {
        "chartjs": "https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js",
        "d3": "https://d3js.org/d3.v7.min.js",
        "threejs": "https://cdn.jsdelivr.net/npm/three@0.154.0/build/three.min.js",
        "gsap": "https://cdn.jsdelivr.net/npm/gsap@3.12.2/dist/gsap.min.js",
        "lottie": "https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.0/lottie.min.js",
        "jquery": "https://code.jquery.com/jquery-3.7.0.min.js",
    }
    
    # Additional library modules that may be needed
    ADDITIONAL_MODULES = {
        "threejs_controls": "https://cdn.jsdelivr.net/npm/three@0.154.0/examples/js/controls/OrbitControls.js",
        "d3_force": "https://d3js.org/d3-force.v2.min.js",
        "chartjs_datalabels": "https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js",
    }
    
    @staticmethod
    def render_html(
        js_code: str,
        css_code: str = "",
        libraries: List[str] = None,
        additional_modules: List[str] = None,
        title: str = "LlamaVis Visualization",
        container_id: str = "visualization",
        width: Union[int, str] = "100%",
        height: Union[int, str] = "500px",
        inline_styles: Dict[str, str] = None,
    ) -> str:
        """
        Render a visualization to HTML.
        
        Args:
            js_code: JavaScript code to render the visualization
            css_code: CSS code for styling the visualization
            libraries: List of libraries to include (keys from CDN_URLS)
            additional_modules: List of additional modules to include
            title: Title of the HTML page
            container_id: ID of the container element
            width: Width of the visualization container
            height: Height of the visualization container
            inline_styles: Additional inline styles for the container
            
        Returns:
            HTML string with the visualization
        """
        libraries = libraries or []
        additional_modules = additional_modules or []
        inline_styles = inline_styles or {}
        
        # Convert width and height to strings with units if they're integers
        if isinstance(width, int):
            width = f"{width}px"
        if isinstance(height, int):
            height = f"{height}px"
        
        # Build style attribute for container
        container_styles = {
            "width": width,
            "height": height,
            "margin": "0 auto",
            "position": "relative",
            "overflow": "hidden",
        }
        container_styles.update(inline_styles)
        style_str = "; ".join([f"{k}: {v}" for k, v in container_styles.items()])
        
        # Generate script tags for libraries
        lib_tags = []
        for lib in libraries:
            if lib in Renderer.CDN_URLS:
                lib_tags.append(f'<script src="{Renderer.CDN_URLS[lib]}"></script>')
        
        # Generate script tags for additional modules
        for module in additional_modules:
            if module in Renderer.ADDITIONAL_MODULES:
                lib_tags.append(f'<script src="{Renderer.ADDITIONAL_MODULES[module]}"></script>')
        
        # Build the complete HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        {css_code}
    </style>
    {"".join(lib_tags)}
</head>
<body>
    <div class="container">
        <div id="{container_id}" style="{style_str}"></div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            {js_code}
        }});
    </script>
</body>
</html>"""
        return html
    
    @staticmethod
    def save_html(
        html: str,
        filepath: str,
        overwrite: bool = True
    ) -> str:
        """
        Save HTML to a file.
        
        Args:
            html: HTML string to save
            filepath: Path to save the file to
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the saved file
        """
        if os.path.exists(filepath) and not overwrite:
            base, ext = os.path.splitext(filepath)
            count = 1
            while os.path.exists(f"{base}_{count}{ext}"):
                count += 1
            filepath = f"{base}_{count}{ext}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return os.path.abspath(filepath)
    
    @staticmethod
    def open_in_browser(html_path: str) -> None:
        """
        Open an HTML file in the default browser.
        
        Args:
            html_path: Path to the HTML file
        """
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
    
    @staticmethod
    def generate_script_tag(
        code: str,
        is_module: bool = False,
        script_id: Optional[str] = None
    ) -> str:
        """
        Generate a script tag with the given code.
        
        Args:
            code: JavaScript code
            is_module: Whether to use type="module"
            script_id: Optional ID for the script tag
            
        Returns:
            HTML script tag with the code
        """
        id_attr = f' id="{script_id}"' if script_id else ''
        type_attr = ' type="module"' if is_module else ''
        return f"<script{id_attr}{type_attr}>\n{code}\n</script>"
    
    @staticmethod
    def embed_data(data: Any, var_name: str = "visualizationData") -> str:
        """
        Embed data as a JavaScript variable.
        
        Args:
            data: Data to embed (will be converted to JSON)
            var_name: Name of the JavaScript variable
            
        Returns:
            JavaScript code defining the variable
        """
        json_data = json.dumps(data, default=str)
        return f"const {var_name} = {json_data};" 