import streamlit as st
import pandas as pd
import plotly.express as px
import wbgapi as wb

# Page Configuration
st.set_page_config(
    page_title="Global Carbon Emissions Tracker",
    layout="wide"
)

# --- Helper Functions ---
@st.cache_data
def fetch_co2_data():
    """
    Fetches CO2 emissions (metric tons per capita) for all countries.
    Indicator: EN.ATM.CO2E.PC
    """
    # Fetch data for all countries, excluding aggregates
    data = wb.data.DataFrame('EN.ATM.CO2E.PC', labels=True)
    
    # The dataframe comes in wide format (years as columns). 
    # Let's reset index to get Country Code and Name
    data = data.reset_index()
    
    # Melt to long format for easier plotting
    # Columns are like 'YR1990', 'YR1991', etc.
    id_vars = ['economy', 'Country']
    value_vars = [c for c in data.columns if c.startswith('YR')]
    
    df_long = data.melt(id_vars=id_vars, value_vars=value_vars, var_name='year_col', value_name='co2_per_capita')
    
    # Clean up year column (remove 'YR')
    df_long['year'] = df_long['year_col'].str.replace('YR', '').astype(int)
    
    # Drop rows with missing values
    df_long = df_long.dropna(subset=['co2_per_capita'])
    
    return df_long

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
        
        # Sidebar Controls
        st.sidebar.header("Settings")
        
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)
        
        # Filter data for selected year
        year_df = df[df['year'] == selected_year]
        
        # --- Visualizations ---
        
        # 1. Global Map
        st.subheader(f"Global Emissions Map ({selected_year})")
        
        fig_map = px.choropleth(
            year_df,
            locations="economy",
            color="co2_per_capita",
            hover_name="Country",
            color_continuous_scale="RdYlOr", # Red-Yellow-Orange (Red = High)
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
        st.plotly_chart(fig_map, use_container_width=True)
        
        # 2. Top Emitters Bar Chart
        st.subheader(f"Top 10 Emitters per Capita ({selected_year})")
        
        top_10 = year_df.sort_values('co2_per_capita', ascending=False).head(10)
        
        fig_bar = px.bar(
            top_10,
            x="co2_per_capita",
            y="Country",
            orientation='h',
            color="co2_per_capita",
            color_continuous_scale="RdYlOr",
            labels={"co2_per_capita": "CO₂ (metric tons/capita)"}
        )
        
        fig_bar.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # Footer
        st.markdown("---")
        st.caption("Built by [Jimmy Matewere](https://github.com/Jimmy-JayJay) | Data: World Bank (Indicator EN.ATM.CO2E.PC)")
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
