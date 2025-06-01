# Financial Transactions Dashboard

A comprehensive interactive dashboard built with Dash for analyzing and visualizing financial transaction data. This
application provides powerful insights into user spending patterns, merchant performance, geographical distribution of
transactions, and more.

![Financial Transactions Dashboard](https://i.imgur.com/4SD606X.png)

## Features

- **Multi-tab Interface**: Navigate between Home, User, Merchant, Cluster, and Fraud detection views
- **Interactive Visualizations**: Dynamic charts and graphs that respond to user input
- **KPI Overview**: Key performance indicators for quick insights
- **User Analysis**: Detailed user spending patterns and behavior
- **Merchant Analysis**: Performance metrics for different merchants
- **Cluster Visualization**: Group similar transactions or users for pattern recognition
- **Fraud Detection**: Identify suspicious transactions
- **Geographical Mapping**: Visualize transaction data on maps
- **Dark/Light Mode**: Toggle between display themes for better readability
- **Responsive Design**: Optimized for different screen sizes

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/financial-transactions-dashboard.git
   cd financial-transactions-dashboard
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

3. Use the navigation tabs to explore different views of the data.

## Project Structure

```text
├── assets/               # Static assets (CSS, JS, icons, images)
│   ├── css/              # Stylesheet files
│   ├── data/             # Sample data files (CSV, Parquet, JSON)
│   ├── icons/            # SVG icons used in the dashboard
│   └── js/               # JavaScript files for client-side functionality
├── backend/              # Data handling, callbacks, business logic
│   ├── callbacks/        # Dash callback functions
│   ├── data_setup/       # Data preparation and processing
│   ├── data_handler.py   # Data loading and transformation
│   └── data_manager.py   # Central data management
├── components/           # Reusable Dash components and factories
│   ├── factories/        # Component creation factories
│   ├── tabs/             # Tab-specific components
│   └── constants.py      # Application constants
├── frontend/             # UI configuration, icons, layouts
│   ├── layout/           # Dashboard layout structure
│   └── component_ids.py  # Component ID definitions
├── info/                 # Documentation, product backlog, ideas
├── utils/                # Utility modules (logger, benchmarks, etc.)
├── main.py               # Application entry point
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Technologies Used

- **[Dash](https://dash.plotly.com/)** (3.0.4): Framework for building analytical web applications
- **[Plotly](https://plotly.com/python/)** (6.1.1): Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)** (2.2.3): Data manipulation and analysis
- **[NumPy](https://numpy.org/)** (2.2.5): Numerical computing
- **[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)** (2.0.3): Bootstrap
  components for Dash
- **[scikit-learn](https://scikit-learn.org/)** (1.7.0rc1): Machine learning for clustering
- **[pgeocode](https://pypi.org/project/pgeocode/)** (0.5.0): Geographical coding
- **[Shapely](https://shapely.readthedocs.io/)** (2.1.0): Manipulation of geometric objects
- **[PyArrow](https://arrow.apache.org/docs/python/)** (20.0.0): Efficient data handling

## Performance Optimization

The dashboard includes several performance optimizations:

- Parallel data loading using ThreadPoolExecutor
- Efficient data storage with Parquet format
- Optimized data structures for quick access
- Benchmarking utilities to monitor performance

## License

This project is licensed under the MIT License - see the LICENSE file for details.
