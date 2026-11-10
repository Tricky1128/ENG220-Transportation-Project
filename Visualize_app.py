import json
import geopandas as gpd
import numpy as np
import pandas as pd
import pydeck as pdk
import requests
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="Cuba & County Spatial Analysis", page_icon="🗺️", layout="wide"
)

st.title("🗺️ Spatial Equity & Safety Dashboard: Cuba vs. Sandoval County")
st.markdown("""
This application merges **U.S. Census Bureau ACS data** with an interactive 3D PyDeck map 
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

st.sidebar.header("Map Layer Settings")
map_metric = st.sidebar.selectbox(
    "Select Metric for 3D Map Height & Color:",
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


# Fetch Spatial Boundaries safely with fail-safe fallback check
@st.cache_data
def fetch_census_geometries():
  geojson_url = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer/4/query?where=STATE%3D35+AND+COUNTY%3D043&outFields=GEOID,NAME&outSR=4326&f=geojson"
  headers = {"User-Agent": "Mozilla/5.0"}
  try:
    response = requests.get(geojson_url, headers=headers, timeout=15)
    if response.status_code == 200:
      data = response.json()
      if "features" in data and len(data["features"]) > 0:
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        gdf.set_crs(epsg=4326, inplace=True)
        return gdf
  except Exception:
    pass
  return gpd.GeoDataFrame()


df = fetch_census_acs_data(census_api_key)
gdf_tracts = fetch_census_geometries()

if not df.empty:
  if not gdf_tracts.empty:
    gdf_merged = gdf_tracts.merge(df, on="GEOID", how="inner")
  else:
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
      gdf_merged["Avg_Commute_Mins"] / max_comm
      if max_comm and max_comm > 0
      else 0
  )
  gdf_merged["Vehicle_Need"] = (

    
