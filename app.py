import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page Config
st.set_page_config(
    page_title="Global Carbon Emissions Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .stApp {
            background-color: #0a192f;
            color: #e6f1ff;
        }
        
        [data-testid="stSidebar"] {
            background-color: rgba(17, 34, 64, 0.8);
            border-right: 1px solid rgba(100, 255, 218, 0.1);
        }
        
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
            color: #e6f1ff !important;
            font-family: 'Inter', sans-serif;
        }
        
        [data-testid="stMetricValue"] {
            color: #64ffda !important;
        }
        [data-testid="stMetricLabel"] {
            color: #8892b0 !important;
        }
        
        .stSlider [data-baseweb="slider"] {
            color: #64ffda;
        }
        
        a {
            color: #64ffda !important;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        
        .css-1r6slb0 {
            background: rgba(17, 34, 64, 0.6);
            border-radius: 12px;
            border: 1px solid rgba(100, 255, 218, 0.1);
            padding: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def fetch_co2_data():
    """Fetch CO2 emissions data from World Bank API (Indicator: EN.ATM.CO2E.PC)"""
    url = "http://api.worldbank.org/v2/country/all/indicator/EN.ATM.CO2E.PC"
    
    params = {
        "format": "json",
        "per_page": 20000,
        "source": 75
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if len(data) < 2:
            return pd.DataFrame()
            
        records = data[1]
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)
        
        if 'country' not in df.columns or 'value' not in df.columns or 'countryiso3code' not in df.columns:
            return pd.DataFrame()

        df['Country'] = df['country'].apply(lambda x: x['value'] if isinstance(x, dict) else '')
        df['economy'] = df['countryiso3code']
        
        df = df.rename(columns={'value': 'co2_per_capita', 'date': 'year'})
        df['year'] = df['year'].astype(int)
        
        df = df.dropna(subset=['co2_per_capita'])
        df = df[df['economy'].notna() & (df['economy'] != '')]
        
        return df[['economy', 'Country', 'year', 'co2_per_capita']]
        
    except Exception:
        return pd.DataFrame()

# Header
st.title("Global Carbon Emissions ")
st.markdown("Visualization of **CO₂ emissions per capita** (metric tons). Data: [World Bank](https://data.worldbank.org/indicator/EN.ATM.CO2E.PC).")

# Main App Logic
with st.spinner("Loading data..."):
    df = fetch_co2_data()
    
    if df.empty:
        st.error("Unable to load data. Please try again later.")
    else:
        # Sidebar Controls
        st.sidebar.header("Controls")
        
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)
        
        year_df = df[df['year'] == selected_year]
        
        # Metrics
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Countries", len(year_df))
        col2.metric("Global Avg", f"{year_df['co2_per_capita'].mean():.2f} t" if not year_df.empty else "N/A")
        
        # Layout: Map (Top) and Top 10 (Bottom)
        
        # Global Map
        st.subheader(f"Global Map ({selected_year})")
        
        fig_map = px.choropleth(
            year_df,
            locations="economy",
            locationmode="ISO-3",
            color="co2_per_capita",
            hover_name="Country",
            color_continuous_scale="Portland",
            range_color=[0, 20],
            labels={"co2_per_capita": "CO₂ (t/capita)"}
        )
        
        fig_map.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                showlakes=False,
                showframe=False,
                projection_type="natural earth",
                coastlinecolor="rgba(100, 255, 218, 0.1)",
                landcolor="rgba(100, 255, 218, 0.02)"
            ),
            font=dict(family="Inter, sans-serif", color="#e6f1ff"),
            coloraxis_colorbar=dict(
                title="t/capita",
                thickness=15,
                len=0.6,
                tickfont=dict(color="#8892b0")
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        
        st.markdown("---")
        
        # Top Emitters Bar Chart
        st.subheader("Top Emitters")
        
        top_10 = year_df.sort_values('co2_per_capita', ascending=False).head(10)
        
        fig_bar = px.bar(
            top_10,
            x="Country",
            y="co2_per_capita",
            orientation='v',
            color="co2_per_capita",
            color_continuous_scale="Portland",
            range_color=[0, 20],
            text="co2_per_capita"
        )
        
        fig_bar.update_traces(
            texttemplate='%{text:.1f}',
            textposition='outside',
            textfont=dict(color="#8892b0", size=11)
        )
        
        fig_bar.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin={"r":0,"t":20,"l":0,"b":0},
            yaxis=dict(
                showgrid=True, 
                gridcolor="rgba(100, 255, 218, 0.05)", 
                showticklabels=True,
                title=None,
                range=[0, top_10['co2_per_capita'].max() * 1.15]
            ),
            xaxis=dict(
                categoryorder='total descending', 
                tickfont=dict(color="#e6f1ff", size=11),
                title=None
            ),
            font=dict(family="Inter, sans-serif", color="#e6f1ff"),
            showlegend=False,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #8892b0; font-size: 0.8rem;'>"
            "Built by <a href='https://github.com/Jimmy-JayJay' target='_blank'>Jimmy Matewere</a> | "
            "Data: <a href='https://data.worldbank.org/indicator/EN.ATM.CO2E.PC' target='_blank'>World Bank ESG</a>"
            "</div>",
            unsafe_allow_html=True
        )

