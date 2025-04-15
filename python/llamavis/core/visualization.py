"""
Core visualization base class for LlamaVis.

This module defines the abstract base class for all visualizations,
providing common functionality and interfaces.
"""

import json
import os
import uuid
import webbrowser
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from .config import VisualizationConfig
from .renderer import Renderer
from .utils import generate_unique_id


class Visualization(ABC):
    """
    Abstract base class for all visualizations.

    This class defines the interface that all specific visualization
    implementations must implement, and provides common functionality.
    """

    def __init__(
        self,
        data: Any,
        config: VisualizationConfig,
        width: int = 800,
        height: int = 600,
        container_id: Optional[str] = None,
        title: str = "Visualization",
    ):
        """
        Initialize visualization.

        Args:
            data: Data to visualize
            config: Visualization configuration
            width: Width of the visualization in pixels
            height: Height of the visualization in pixels
            container_id: HTML ID for the container element
            title: Title of the visualization
        """
        self.data = data
        self.config = config
        self.width = width
        self.height = height
        self.container_id = container_id or generate_unique_id("llamavis-container")
        self.title = title
        self._renderer = Renderer()

    @abstractmethod
    def get_library_includes(self) -> List[str]:
        """
        Get the JavaScript libraries required for this visualization.

        Returns:
            List of library names to include
        """
        pass

    @abstractmethod
    def preprocess_data(self) -> Dict[str, Any]:
        """
        Preprocess the data for visualization.

        Returns:
            Preprocessed data ready for visualization
        """
        pass

    @abstractmethod
    def generate_js_code(self) -> str:
        """
        Generate JavaScript code for the visualization.

        Returns:
            JavaScript code as a string
        """
        pass

    def _generate_html(self) -> str:
        """
        Generate HTML for the visualization.

        Returns:
            HTML document as a string
        """
        # Preprocess data
        processed_data = self.preprocess_data()

        # Generate JavaScript code
        js_code = self.generate_js_code()

        # Get required libraries
        libraries = self.get_library_includes()

        # Generate HTML
        html = self._renderer.generate_html(
            data=processed_data,
            js_code=js_code,
            config=self.config,
            libraries=libraries,
            container_id=self.container_id,
            title=self.title,
            width=self.width,
            height=self.height,
        )

        return html

    def to_html(self) -> str:
        """
        Generate HTML for the visualization.

        Returns:
            HTML document as a string
        """
        return self._generate_html()

    def save(self, filepath: str, embed_resources: bool = False) -> str:
        """
        Save the visualization to an HTML file.

        Args:
            filepath: Path where to save the file
            embed_resources: Whether to embed resources in the HTML

        Returns:
            Absolute path to the saved file
        """
        html = self._generate_html()

        if embed_resources:
            html = self._renderer.embed_resources(html)

        return self._renderer.save_to_file(html, filepath)

    def show(self, use_temp: bool = True, filepath: Optional[str] = None) -> str:
        """
        Open the visualization in a web browser.

        Args:
            use_temp: Whether to use a temporary file
            filepath: Path where to save the file (if not using temp)

        Returns:
            Path to the HTML file
        """
        html = self._generate_html()
        return self._renderer.open_in_browser(html, use_temp, filepath)

    def to_iframe(
        self, width: Optional[int] = None, height: Optional[int] = None
    ) -> str:
        """
        Generate iframe HTML code for embedding the visualization.

        Args:
            width: Width of the iframe (default: same as visualization)
            height: Height of the iframe (default: same as visualization)

        Returns:
            HTML code for embedding in an iframe
        """
        html = self._generate_html()
        return self._renderer.generate_iframe_embed_code(
            html, width or self.width, height or self.height
        )

    def to_json(self) -> str:
        """
        Export the visualization configuration to JSON.

        Returns:
            JSON string with visualization configuration
        """
        config_dict = {
            "type": self.__class__.__name__,
            "config": self.config.to_dict(),
            "width": self.width,
            "height": self.height,
            "container_id": self.container_id,
            "title": self.title,
        }

        return json.dumps(config_dict, indent=2)

    @classmethod
    def from_json(cls, json_str: str, data: Any) -> "Visualization":
        """
        Create a visualization from a JSON configuration.

        Args:
            json_str: JSON string with visualization configuration
            data: Data to visualize

        Returns:
            New visualization instance
        """
        # This is a stub that should be implemented by subclasses
        raise NotImplementedError(
            "from_json must be implemented by concrete visualization classes"
        )

    def update_data(self, data: Any) -> "Visualization":
        """
        Update the data for this visualization.

        Args:
            data: New data to visualize

        Returns:
            Self for method chaining
        """
        self.data = data
        return self

    def update_config(self, **kwargs) -> "Visualization":
        """
        Update the configuration for this visualization.

        Args:
            **kwargs: Configuration parameters to update

        Returns:
            Self for method chaining
        """
        self.config.update(**kwargs)
        return self
