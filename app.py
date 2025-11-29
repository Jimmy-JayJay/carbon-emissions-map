import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page Configuration
st.set_page_config(
    page_title="Global Carbon Emissions Tracker",
    layout="wide"
)

# --- Helper Functions ---
@st.cache_data
def fetch_co2_data():
    """
    Fetches CO2 emissions data directly from World Bank API.
    Indicator: EN.ATM.CO2E.PC
    """
    # API Endpoint
    url = "http://api.worldbank.org/v2/country/all/indicator/EN.ATM.CO2E.PC"
    
    # Parameters
    params = {
        "format": "json",
        "per_page": 20000, # Try to get everything in one go (max is usually 20k or so)
        "source": 75 # ESG Data
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # The API returns a list: [metadata, data]
    if len(data) < 2:
        raise ValueError("Invalid API response")
        
    records = data[1]
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Extract country name from the 'country' dict column
    df['Country'] = df['country'].apply(lambda x: x['value'])
    df['economy'] = df['country'].apply(lambda x: x['id'])
    
    # Rename and clean
    df = df.rename(columns={'value': 'co2_per_capita', 'date': 'year'})
    df['year'] = df['year'].astype(int)
    
    # Drop rows with missing values
    df = df.dropna(subset=['co2_per_capita'])
    
    # Filter out aggregates (World, Regions, etc.) if possible
    # The API returns aggregates too. Usually they have 'iso2' codes like '1W', 'Z4' etc.
    # But 'economy' here is iso3. 
    # A simple way to filter is to check if 'economy' is a valid country code.
    # For now, we'll keep it simple, or we can filter by a known list if needed.
    
    return df[['economy', 'Country', 'year', 'co2_per_capita']]

# --- Main Layout ---
st.title("Global Carbon Emissions Tracker")
st.markdown("""
Interactive visualization of **CO₂ emissions per capita** (metric tons) across the globe.  
Data Source: [World Bank Open Data](https://data.worldbank.org/indicator/EN.ATM.CO2E.PC).
""")

# Load Data
with st.spinner("Fetching latest data from World Bank..."):
    try:
        df = fetch_co2_data()
        
        if df.empty:
            st.warning("No CO₂ data available from the API at this time.")
        else:
            # Sidebar Controls
            st.sidebar.header("Settings")
            
            min_year = int(df['year'].min())
            max_year = int(df['year'].max())
            
            selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)
        
            # Filter data for selected year
            year_df = df[df['year'] == selected_year]
            
            # Show data stats in sidebar
            st.sidebar.markdown("---")
            st.sidebar.metric("Countries with Data", len(year_df))
            st.sidebar.metric("Global Avg CO₂", f"{year_df['co2_per_capita'].mean():.2f} t" if not year_df.empty else "N/A")
            
            # --- Visualizations ---
            
            # 1. Global Map
            st.subheader(f"Global Emissions Map ({selected_year})")
            
            fig_map = px.choropleth(
                year_df,
                locations="economy",
                color="co2_per_capita",
                hover_name="Country",
                color_continuous_scale="YlOrRd", # Red-Yellow-Orange (Red = High)
                range_color=[0, 20], # Cap at 20 to see variation better (some outliers like Qatar are very high)
                labels={"co2_per_capita": "CO₂ (metric tons/capita)"},
                title=f"CO₂ Emissions per Capita in {selected_year}"
            )
            
            fig_map.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin={"r":0,"t":40,"l":0,"b":0},
                geo=dict(
                    bgcolor="rgba(0,0,0,0)",
                    showlakes=False,
                    showframe=False,
                    projection_type="natural earth"
                )
            )
            st.plotly_chart(fig_map, use_container_width=True, key=f"map_{selected_year}")
            
            # 2. Top Emitters Bar Chart
            st.subheader(f"Top 10 Emitters per Capita ({selected_year})")
            
            top_10 = year_df.sort_values('co2_per_capita', ascending=False).head(10)
            
            fig_bar = px.bar(
                top_10,
                x="co2_per_capita",
                y="Country",
                orientation='h',
                color="co2_per_capita",
                color_continuous_scale="YlOrRd",
                labels={"co2_per_capita": "CO₂ (metric tons/capita)"}
            )
            
            fig_bar.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig_bar, use_container_width=True, key=f"bar_{selected_year}")
        
        # Footer
        st.markdown("---")
        st.caption("Built by [Jimmy Matewere](https://github.com/Jimmy-JayJay) | Data: [World Bank ESG Data](https://data.worldbank.org/indicator/EN.ATM.CO2E.PC) (Indicator EN.ATM.CO2E.PC)")
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
