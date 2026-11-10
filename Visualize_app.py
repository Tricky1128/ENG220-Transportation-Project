import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="Cuba & County Spatial Analysis", page_icon="🗺️", layout="wide"
)

st.title("🗺️ Spatial Equity & Safety Dashboard: Cuba vs. Sandoval County")
st.markdown("""
This application merges **U.S. Census Bureau ACS data** with an interactive Plotly visualization 
to evaluate commute times, vehicle accessibility, household income, and high-vulnerability census tracts across Sandoval County & Cuba, NM.
""")

# Sidebar Controls
st.sidebar.header("Configuration & Thresholds")
census_api_key = st.sidebar.text_input(
    "Census API Key (Optional)",
    type="password",
    help="Optional key for higher Census API rate limits.",
)

income_threshold = st.sidebar.slider(
    "Filter Low Household Income (< $)", 20000, 100000, 50000
)
min_commute_time = st.sidebar.slider(
    "Filter High Commute Time (> mins)", 10, 60, 20
)

st.sidebar.header("Chart & Metric Settings")
map_metric = st.sidebar.selectbox(
    "Select Metric to Visualize:",
    [
        "Vulnerability_Index",
        "Median_Income",
        "Avg_Commute_Mins",
        "Zero_Vehicle_Pct",
    ],
)


# Fetch Census ACS Demographics
@st.cache_data
def fetch_census_acs_data(api_key=""):
  state_fips = "35"  # New Mexico
  county_fips = "043"  # Sandoval County

  variables = "NAME,B19013_001E,B08303_001E,B08301_001E,B25044_001E,B25044_003E,B25044_010E"
  url = f"https://api.census.gov/data/2022/acs/acs5?get={variables}&for=tract:*&in=state:{state_fips}%20county:{county_fips}"

  if api_key:
    url += f"&key={api_key}"

  headers = {"User-Agent": "Mozilla/5.0"}

  try:
    response = requests.get(url, headers=headers, timeout=15)
    if response.status_code == 200:
      raw_data = response.json()
      df = pd.DataFrame(raw_data[1:], columns=raw_data[0])

      numeric_cols = [
          "B19013_001E",
          "B08303_001E",
          "B08301_001E",
          "B25044_001E",
          "B25044_003E",
          "B25044_010E",
      ]
      for col in numeric_cols:
        if col in df.columns:
          df[col] = pd.to_numeric(df[col], errors="coerce")
          df[col] = df[col].apply(lambda x: np.nan if x <= 0 else x)

      df["GEOID"] = df["state"] + df["county"] + df["tract"]
      df["Median_Income"] = df["B19013_001E"]

      df["Avg_Commute_Mins"] = np.where(
          (df["B08301_001E"] > 0) & (df["B08303_001E"] > 0),
          df["B08303_001E"] / df["B08301_001E"],
          np.nan,
      )

      df["Zero_Vehicle_Pct"] = np.where(
          df["B25044_001E"] > 0,
          (df["B25044_003E"].fillna(0) + df["B25044_010E"].fillna(0))
          / df["B25044_001E"]
          * 100,
          np.nan,
      )

      return df
  except Exception as e:
    st.error(f"Error fetching Census data: {e}")
  return pd.DataFrame()


df = fetch_census_acs_data(census_api_key)

if not df.empty:
  gdf_merged = df.copy()

  # Calculate Vulnerability Index Score (0-100)
  max_inc = (
      gdf_merged["Median_Income"].max()
      if "Median_Income" in gdf_merged
      else 1
  )
  max_comm = (
      gdf_merged["Avg_Commute_Mins"].max()
      if "Avg_Commute_Mins" in gdf_merged
      else 1
  )
  max_veh = (
      gdf_merged["Zero_Vehicle_Pct"].max()
      if "Zero_Vehicle_Pct" in gdf_merged
      else 1
  )

  gdf_merged["Income_Need"] = (
      1 - (gdf_merged["Median_Income"] / max_inc)
      if max_inc and max_inc > 0
      else 0
  )
  gdf_merged["Commute_Need"] = (
    
