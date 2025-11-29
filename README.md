# Global Carbon Emissions Tracker 🌍

Interactive global map visualizing CO₂ emissions per capita using World Bank data. Built with Python and Streamlit to track environmental impact trends from 1990 to present, highlighting disparities in global carbon footprints.

## Features

- **Interactive Choropleth Map**: Visualizes CO₂ emissions per capita (metric tons) for every country.
- **Time Slider**: Explore how emissions have changed over the last 30+ years.
- **Top Emitters Ranking**: Identifies countries with the highest per-capita carbon footprints.
- **Live Data**: Fetches the latest available data directly from the World Bank API.

## Tech Stack

- **Python 3.8+**
- **Streamlit**: Interactive web framework
- **Plotly**: Geospatial visualizations
- **WBGAPI**: World Bank Data API wrapper for Python
- **Pandas**: Data manipulation

## Running Locally

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## Data Source

Data is sourced from the [World Bank Open Data](https://data.worldbank.org/) portal, specifically indicator `EN.ATM.CO2E.PC` (CO2 emissions, metric tons per capita).

## Author

Built by [Jimmy Matewere](https://github.com/Jimmy-JayJay) - Climate Scientist & Data Analyst
