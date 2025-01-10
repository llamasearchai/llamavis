# LlamaVis

LlamaVis is a Python visualization library designed for the LlamaSearch.AI ecosystem. It provides a flexible and powerful way to create interactive visualizations using modern JavaScript libraries like Three.js, D3.js, Chart.js, GSAP, and Lottie.

## Features

- Create visualizations with minimal code
- Support for multiple visualization libraries:
  - Chart.js for basic charts (line, bar, pie, radar, etc.)
  - D3.js for complex visualizations (networks, trees, heatmaps)
  - Three.js for 3D visualizations (coming soon)
  - GSAP for animations (coming soon)
  - Lottie for vector animations (coming soon)
- Easily customizable themes and styles
- Data preprocessing utilities
- Export visualizations to HTML or iframe embeds
- Interactive visualizations with tooltips, zooming, and filtering

## Installation

```bash
pip install llamavis
```

## Quick Start

```python
import pandas as pd
import numpy as np
from llamavis import LineChart, VisualizationConfig, ChartType

# Create some sample data
dates = pd.date_range(start='2023-01-01', periods=30, freq='D')
values = np.sin(np.linspace(0, 4*np.pi, 30)) * 10 + np.random.randn(30) * 2
df = pd.DataFrame({'date': dates, 'value': values})

# Create a line chart
chart = LineChart(
    data=df,
    config=VisualizationConfig(
        chart_type=ChartType.LINE,
        theme="llamasearch",
        title="Sample Line Chart",
        show_legend=True
    ),
    width=800,
    height=400
)

# Show the chart in a web browser
chart.show()

# Save the chart to an HTML file
chart.save("line_chart.html")
```

## More Examples

### Bar Chart

```python
from llamavis import BarChart
import pandas as pd

data = {
    'Category': ['A', 'B', 'C', 'D', 'E'],
    'Value': [5, 7, 3, 9, 6]
}
df = pd.DataFrame(data)

chart = BarChart(data=df)
chart.show()
```

### Network Graph

```python
from llamavis import NetworkGraph
import pandas as pd

# Create network data
edges = [
    {'source': 'A', 'target': 'B', 'weight': 5},
    {'source': 'A', 'target': 'C', 'weight': 3},
    {'source': 'B', 'target': 'C', 'weight': 2},
    {'source': 'B', 'target': 'D', 'weight': 4},
    {'source': 'C', 'target': 'E', 'weight': 1},
    {'source': 'D', 'target': 'E', 'weight': 3}
]

graph = NetworkGraph(data=edges)
graph.show()
```

### Heatmap

```python
from llamavis import HeatmapVis
import numpy as np
import pandas as pd

# Create sample data
data = np.random.randn(10, 10)
rows = [f'Row {i}' for i in range(10)]
cols = [f'Col {i}' for i in range(10)]

# Convert to DataFrame
df = pd.DataFrame(data, index=rows, columns=cols)
df = df.reset_index().melt(id_vars='index', var_name='column', value_name='value')

heatmap = HeatmapVis(data=df, title="Random Heatmap")
heatmap.show()
```

## Documentation

For more detailed documentation and examples, visit the [LlamaVis Documentation](https://docs.llamasearch.ai/llamavis/).

## Integration with Other LlamaSearch.AI Packages

LlamaVis works seamlessly with other packages in the LlamaSearch.AI ecosystem:

- **LlamaDB**: Visualize query results directly from LlamaDB
- **LlamaIndex**: Create visualizations from indexed document data
- **LlamaStream**: Real-time visualization of streaming data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
# Updated in commit 1 - 2025-04-04 17:24:42

# Updated in commit 9 - 2025-04-04 17:24:42

# Updated in commit 17 - 2025-04-04 17:24:43

# Updated in commit 25 - 2025-04-04 17:24:43

# Updated in commit 1 - 2025-04-05 14:31:34

# Updated in commit 9 - 2025-04-05 14:31:34

# Updated in commit 17 - 2025-04-05 14:31:35

# Updated in commit 25 - 2025-04-05 14:31:35

# Updated in commit 1 - 2025-04-05 15:18:02

# Updated in commit 9 - 2025-04-05 15:18:02

# Updated in commit 17 - 2025-04-05 15:18:02

# Updated in commit 25 - 2025-04-05 15:18:02

# Updated in commit 1 - 2025-04-05 15:48:49

# Updated in commit 9 - 2025-04-05 15:48:50

# Updated in commit 17 - 2025-04-05 15:48:50

# Updated in commit 25 - 2025-04-05 15:48:50

# Updated in commit 1 - 2025-04-05 16:54:16

# Updated in commit 9 - 2025-04-05 16:54:16

# Updated in commit 17 - 2025-04-05 16:54:17

# Updated in commit 25 - 2025-04-05 16:54:17

# Updated in commit 1 - 2025-04-05 17:25:52

# Updated in commit 9 - 2025-04-05 17:25:52
