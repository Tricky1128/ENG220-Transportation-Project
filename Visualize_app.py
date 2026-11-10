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
      gdf_merged["Zero_Vehicle_Pct"] / max_veh
      if max_veh and max_veh > 0
      else 0
  )

  gdf_merged["Vulnerability_Index"] = (
      gdf_merged[["Income_Need", "Commute_Need", "Vehicle_Need"]].mean(axis=1)
      * 100
  ).round(1)

  # 1. Summary Metrics Display
  st.header("1. Socioeconomic & Commute Metrics")
  m1, m2, m3, m4 = st.columns(4)

  m1.metric(
      "County Avg Income",
      (
          f"${gdf_merged['Median_Income'].mean():,.0f}"
          if not pd.isna(gdf_merged["Median_Income"].mean())
          else "N/A"
      ),
  )
  m2.metric(
      "County Avg Commute",
      (
          f"{gdf_merged['Avg_Commute_Mins'].mean():.1f} mins"
          if not pd.isna(gdf_merged["Avg_Commute_Mins"].mean())
          else "N/A"
      ),
  )
  m3.metric(
      "Zero-Vehicle Households",
      (
          f"{gdf_merged['Zero_Vehicle_Pct'].mean():.1f}%"
          if not pd.isna(gdf_merged["Zero_Vehicle_Pct"].mean())
          else "N/A"
      ),
  )
  m4.metric("Total Tracts Analyzed", len(gdf_merged))

  # 2. PyDeck 3D Map Visualization (Only if boundaries loaded successfully)
  st.header("2. Interactive Geospatial PyDeck Visualization")
  if not gdf_tracts.empty and "geometry" in gdf_merged:
    selected_max = (
        gdf_merged[map_metric].max() if gdf_merged[map_metric].max() > 0 else 1
    )

    def calculate_color(row):
      val = row[map_metric]
      if pd.isna(val):
        return [200, 200, 200, 100]
      ratio = min(max(val / selected_max, 0), 1)
      return [int(255 * ratio), int(255 * (1 - ratio)), 50, 180]

    gdf_merged["color"] = gdf_merged.apply(calculate_color, axis=1)
    gdf_merged["elevation"] = (
        gdf_merged[map_metric].fillna(0) / selected_max
    ) * 5000

    layer_tracts = pdk.Layer(
        "GeoJsonLayer",
        gdf_merged,
        opacity=0.7,
        stroked=True,
        filled=True,
        extruded=True,
        wireframe=True,
        get_elevation="elevation",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 200],
        line_width_min_pixels=1,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=35.60, longitude=-106.90, zoom=8.5, pitch=45, bearing=15
    )

    name_col = "NAME_x" if "NAME_x" in gdf_merged else "NAME"
    r = pdk.Deck(
        layers=[layer_tracts],
        initial_view_state=view_state,
        tooltip={
            "html": f"""
                    <b>Tract Name:</b> {{{name_col}}}<br/>
                    <b>GEOID:</b> {{GEOID}}<br/>
                    <b>Median Income:</b> ${{Median_Income}}<br/>
                    <b>Avg Commute:</b> {{Avg_Commute_Mins}} mins<br/>
                    <b>Zero-Vehicle %:</b> {{Zero_Vehicle_Pct}}%<br/>
                    <b>Vulnerability Score:</b> {{Vulnerability_Index}} / 100
                """,
            "style": {"backgroundColor": "navy", "color": "white"},
        },
    )
    st.pydeck_chart(r)
  else:
    st.info(
        "Map boundaries temporarily unavailable; displaying tabular data"
        " analysis below."
    )

  # 3. Filtered Priority Table
  st.header("3. Overlap Priority Intervention Zones")
  priority_tracts = gdf_merged[
      (gdf_merged["Median_Income"] <= income_threshold)
      | (gdf_merged["Avg_Commute_Mins"] >= min_commute_time)
  ].sort_values(by="Vulnerability_Index", ascending=False)

  st.subheader(f"Matching Census Tracts (Found {len(priority_tracts)})")

  name_col_table = "NAME_x" if "NAME_x" in priority_tracts else "NAME"
  display_df = pd.DataFrame(
      priority_tracts[[
          "GEOID",
          name_col_table,
          "Median_Income",
          "Avg_Commute_Mins",
          "Zero_Vehicle_Pct",
          "Vulnerability_Index",
      ]]
  ).rename(columns={name_col_table: "Tract Name"})

  st.dataframe(display_df, use_container_width=True)

else:
  st.warning(
      "⚠️ Data could not be loaded from the Census API. Please provide a"
      " Census API key in the sidebar."
  )
    
