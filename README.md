# Financial Transactions Dashboard

A comprehensive interactive dashboard built with Dash for analyzing and visualizing financial transaction data. This application provides powerful insights into user spending patterns, merchant performance, geographical distribution of transactions, and more..

![Financial Transactions Dashboard](https://i.imgur.com/R14plod.png)

## Table of Contents
- [Goals](#goals)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Usage Scenarios](#usage-scenarios)
- [Interactive Features](#interactive-features)
- [State Persistence](#state-persistence)
- [Caching Mechanism](#caching-mechanism)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Performance Optimization](#performance-optimization)
- [License](#license)

## Goals

The Financial Transactions Dashboard aims to solve several key challenges in financial data analysis:

- **Comprehensive Data Visualization**: Transform complex financial transaction data into intuitive, interactive visualizations that reveal patterns and insights not easily discernible from raw data.
- **Multi-dimensional Analysis**: Enable analysis across multiple dimensions (users, merchants, geography, time) to provide a holistic view of financial activity.
- **Performance Optimization**: Handle large datasets efficiently through caching and optimized data structures to ensure responsive user experience.
- **User-friendly Interface**: Provide an intuitive interface that allows both technical and non-technical users to explore and analyze financial data effectively.
- **Decision Support**: Facilitate data-driven decision making by highlighting key performance indicators and trends in financial transactions.
- **Fraud Detection**: Help identify suspicious patterns and potential fraudulent activities through specialized visualization and analysis tools.

## Features

### Multi-tab Interface
- **Home Tab**: Overview of transaction data with geographical distribution and key metrics
- **User Tab**: Detailed analysis of individual user spending patterns and behavior
- **Merchant Tab**: Performance metrics and transaction patterns for different merchants
- **Cluster Tab**: Advanced clustering analysis to group similar transactions or users
- **Fraud Detection Tab**: Tools to identify and analyze potentially fraudulent transactions

### Interactive Visualizations
- **Dynamic Charts**: Interactive charts that respond to user input and selection
- **Geographical Mapping**: USA map visualization with state-by-state transaction data
- **Bar Charts**: Visualize top merchants, users, and transaction patterns
- **Pie Charts**: Distribution analysis for gender, age groups, and transaction channels
- **Interactive Navigation**: Click on bars in charts to navigate to detailed views of that data point

### Data Analysis Tools
- **KPI Overview**: Key performance indicators for quick insights
- **Filtering Options**: Filter data by various parameters including state, age group, gender, etc.
- **Sorting Functionality**: Sort tables by different columns to identify patterns
- **Selection Options**: Use dropdowns and input fields to select specific data points for analysis
- **Search Functionality**: Search for specific users, merchants, or transactions

### User Interface
- **Responsive Design**: Optimized for different screen sizes
- **Dark/Light Mode**: Toggle between display themes for better readability (keyboard shortcut: 't')
- **Settings Menu**: Customize application settings (keyboard shortcut: 's')
- **Tooltips**: Informative tooltips that can be toggled on/off
- **Resizable Layout**: Dynamically resize the left and right columns using a draggable handle

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Sufficient RAM (minimum 8GB recommended) for handling large datasets

### Step-by-step Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/financial-transactions-dashboard.git
   cd financial-transactions-dashboard
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Prepare the data directory:
   ```bash
   # Ensure the assets/data directory exists and contains the required data files
   # The application expects CSV files for transactions, users, and cards data
   # as well as a JSON file for MCC codes
   ```

5. Pre-cached data (recommended):
   Due to the amount of data needing processing, we pre-cached the needed data which you can download from here
   [here](https://workupload.com/file/HpPmKVTzLq3)

   This will save you several hours of computing time during the initial startup. After downloading, extract the files to the `assets/data` directory.

## Usage

1. Start the application:
   ```bash
   python main.py
   ```

2. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050
   ```

3. Initial startup requires data processing and cache creation, which may take several hours depending on your hardware. To skip this wait, use the pre-cached data available in step 5 of the Installation section.

4. Use the navigation tabs at the top of the right column to explore different views of the data.

5. Customize the application using the settings menu (gear icon in the top-left corner or press 's' key).

6. Toggle between dark and light mode using the sun/moon icon in the top-right corner or press 't' key.

## Usage Scenarios

### Financial Analysts
- **Transaction Pattern Analysis**: Identify spending patterns across different demographics and geographical regions. For example, analyze how spending habits differ between age groups or compare transaction volumes across different states.
- **Merchant Performance Evaluation**: Analyze which merchants are generating the most transactions and revenue. Track month-over-month changes in merchant performance and identify emerging trends.
- **User Behavior Study**: Understand how different user segments behave in terms of spending habits. Examine frequency of transactions, preferred payment methods, and spending categories for different user groups.
- **Anomaly Detection**: Identify unusual transaction patterns that may indicate fraud or other issues. Set up alerts for transactions that deviate significantly from established patterns.
- **Seasonal Trend Analysis**: Identify cyclical patterns in transaction data to understand seasonal effects on spending behavior and prepare for anticipated volume changes.

### Business Decision Makers
- **Strategic Planning**: Use geographical and demographic insights to inform business strategy. Identify underserved regions or demographics that represent growth opportunities.
- **Performance Monitoring**: Track key performance indicators related to financial transactions. Create custom dashboards focusing on metrics most relevant to specific business objectives.
- **Market Segmentation**: Identify valuable customer segments based on transaction behavior. Develop targeted strategies for high-value segments to increase retention and lifetime value.
- **Resource Allocation**: Determine where to focus resources based on transaction volume and value. Optimize staffing, marketing spend, and technology investments based on data-driven insights.
- **Competitive Analysis**: Compare transaction patterns across different merchant categories to understand market positioning and identify competitive advantages or gaps.

### Data Scientists
- **Pattern Discovery**: Explore the data to discover hidden patterns and correlations. Use the interactive visualizations to identify relationships between variables that might not be apparent in raw data.
- **Model Development**: Use the clustering functionality to develop and test segmentation models. Export the results for further analysis or integration with other predictive models.
- **Hypothesis Testing**: Validate hypotheses about user behavior or merchant performance. Quickly test assumptions by filtering and visualizing relevant subsets of data.
- **Feature Engineering**: Identify important features for predictive modeling. Analyze which transaction attributes have the strongest correlations with target variables like spending amount or fraud likelihood.
- **Algorithm Validation**: Test the effectiveness of clustering algorithms by visualizing the resulting segments and evaluating their business relevance and actionability.

### Risk Management Teams
- **Fraud Pattern Identification**: Analyze historical fraud cases to identify common patterns and develop more effective detection rules.
- **Risk Scoring**: Develop and refine risk scoring models based on transaction characteristics, user profiles, and merchant categories.
- **Exposure Analysis**: Identify areas of highest financial exposure by analyzing transaction volumes and values across different segments.
- **Scenario Testing**: Simulate different risk scenarios by filtering and analyzing subsets of transaction data to prepare contingency plans.
- **Control Effectiveness**: Evaluate the effectiveness of existing risk controls by tracking changes in risk metrics over time.

### Marketing Teams
- **Campaign Effectiveness**: Measure the impact of marketing campaigns by analyzing changes in transaction patterns before, during, and after campaign periods.
- **Customer Journey Mapping**: Analyze transaction sequences to understand the customer journey and identify opportunities for engagement.
- **Cross-selling Opportunities**: Identify potential cross-selling opportunities by analyzing co-occurrence patterns in transaction categories.
- **Loyalty Program Design**: Use transaction frequency and value patterns to design more effective loyalty programs targeted at specific customer segments.
- **ROI Measurement**: Calculate return on investment for marketing initiatives by tracking resulting changes in transaction behavior.

## Interactive Features

### Navigation via Bar Charts
The dashboard allows you to navigate between tabs by clicking on bars in bar charts:
- Clicking on a user bar in the "Top Spending Users" chart navigates to the User tab with that user's details
- Clicking on a merchant bar in the "Most Valuable Merchants" or "Most Visited Merchants" chart navigates to the Merchant tab with that merchant's details

### Sorting and Filtering
- **Table Sorting**: Click on column headers in data tables to sort by that column
- **Dropdown Filters**: Use dropdown menus to filter data by various parameters
- **Input Fields**: Enter specific values in input fields to search for particular records
- **Toggle Buttons**: Switch between different views or data subsets

### Resizable Layout
- A draggable handle between the left and right columns allows you to resize the layout according to your preference
- Minimum widths are enforced to ensure usability (left column: 250px, right column: 760px)

### Keyboard Shortcuts
- **'s' key**: Toggle the settings menu
- **'t' key**: Toggle between dark and light mode
- Shortcuts have a 1-second cooldown to prevent accidental triggering
- Shortcuts are disabled when modifier keys (Ctrl, Alt, Meta/Cmd) are pressed or when focus is in an input field

### Graph Export
- All graphs and visualizations in the dashboard can be exported as images
- Click on the camera icon in the top-right corner of any graph to download it as a PNG file
- Exported images maintain the current state of the visualization, including all applied filters and customizations
- High-resolution exports are suitable for inclusion in reports and presentations

## State Persistence

The application maintains state persistence through several mechanisms:

### Session Storage
- User preferences and settings are stored in the browser's session storage
- This ensures that settings are preserved when navigating between tabs or refreshing the page
- The following settings are persisted:
  - Dark/light mode preference
  - Map color scale selection
  - Map text color
  - Color scale visibility
  - Tooltip visibility
  - Settings canvas placement

### Application State Management
- The application uses a central state management system through the `APP_STATE_STORE`
- State changes are tracked and applied consistently across the application
- The state is automatically reapplied when the page is reloaded

## Caching Mechanism

The dashboard implements a sophisticated caching system to enhance performance:

### Data Caching
- **Initial Processing Cache**: Raw data is processed and optimized on first load, then cached to disk
- **Tab-specific Caches**: Each tab maintains its own cache of processed data
- **Cache Invalidation**: Caches are automatically invalidated when data changes or when configuration parameters change

### Cache Implementation
- The `DataCacher` class in `backend/data_cacher.py` manages the caching system
- Essential cache files include processed transaction data, user data, merchant aggregations, and pre-computed visualizations
- Caches are stored in the `assets/data/cache` directory as Parquet files and pickle files

### Parallel Processing
- The application uses `ThreadPoolExecutor` to initialize tab data in parallel
- This significantly reduces loading time, especially for large datasets

## Project Structure

```text
├── assets/               # Static assets (CSS, JS, icons, images)
│   ├── css/              # Stylesheet files
│   ├── data/             # Sample data files (CSV, Parquet, JSON)
│   │   └── cache/        # Cached data files for performance
│   ├── icons/            # SVG icons used in the dashboard
│   └── js/               # JavaScript files for client-side functionality
├── backend/              # Data handling, callbacks, business logic
│   ├── callbacks/        # Dash callback functions
│   │   └── tabs/         # Tab-specific callbacks
│   ├── data_setup/       # Data preparation and processing
│   │   └── tabs/         # Tab-specific data preparation
│   ├── data_cacher.py    # Caching system implementation
│   ├── data_handler.py   # Data loading and transformation
│   └── data_manager.py   # Central data management
├── components/           # Reusable Dash components and factories
│   ├── factories/        # Component creation factories
│   ├── tabs/             # Tab-specific components
│   └── constants.py      # Application constants
├── frontend/             # UI configuration, icons, layouts
│   ├── layout/           # Dashboard layout structure
│   │   ├── left/         # Left column layout
│   │   └── right/        # Right column layout
│   │       └── tabs/     # Tab-specific layouts
│   ├── component_ids.py  # Component ID definitions
│   └── icon_manager.py   # Icon management
├── info/                 # Documentation, product backlog, ideas
├── utils/                # Utility modules
│   ├── benchmark.py      # Performance benchmarking
│   ├── logger.py         # Logging functionality
│   └── utils.py          # Miscellaneous utilities
├── main.py               # Application entry point
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## Technologies Used

- **[Dash](https://dash.plotly.com/)** (3.0.4): Framework for building analytical web applications
- **[Plotly](https://plotly.com/python/)** (6.1.1): Interactive visualization library
- **[Pandas](https://pandas.pydata.org/)** (2.2.3): Data manipulation and analysis
- **[NumPy](https://numpy.org/)** (2.2.5): Numerical computing
- **[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)** (2.0.3): Bootstrap components for Dash
- **[scikit-learn](https://scikit-learn.org/)** (1.7.0rc1): Machine learning for clustering
- **[pgeocode](https://pypi.org/project/pgeocode/)** (0.5.0): Geographical coding
- **[Shapely](https://shapely.readthedocs.io/)** (2.1.0): Manipulation of geometric objects
- **[PyArrow](https://arrow.apache.org/docs/python/)** (20.0.0): Efficient data handling
- **[Bootstrap Icons](https://icons.getbootstrap.com/)**: Icon library for UI elements
- **[Font Awesome](https://fontawesome.com/)**: Additional icon library

## Performance Optimization

The dashboard includes several performance optimizations:

- **Parallel Data Loading**: Uses ThreadPoolExecutor to load and process data in parallel
- **Efficient Data Storage**: Converts CSV files to Parquet format for faster reading and reduced memory usage
- **Data Type Optimization**: Optimizes data types to reduce memory footprint
- **Lazy Loading**: Loads only necessary data for the current view
- **Caching**: Caches processed data to avoid redundant calculations
- **Benchmarking**: Includes utilities to monitor and optimize performance
- **Pagination**: Implements server-side pagination for large data tables

## License

This project is licensed under the MIT License - see the LICENSE file for details.
