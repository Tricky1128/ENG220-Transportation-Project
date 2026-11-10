import numpy as np
import pandas as pd
import requests
import streamlit as st

# Streamlit Page Setup
st.set_page_config(
    page_title="Cuba & County Spatial Analysis", page_icon="🗺️", layout="wide"
)

st.title("🗺️ Spatial Equity & Safety Dashboard: Cuba vs. Sandoval County")
st.markdown("""
This application combines **U.S. Census Bureau ACS data** with transportation equity variables 
(household income, vehicle access, aggregate commute times) to locate where safety risks and community needs overlap.
""")

# Sidebar Controls
st.sidebar.header("Configuration & Thresholds")
census_api_key = st.sidebar.text_input(
    "Census API Key (Optional)",
    type="password",
    help="Optional key for higher Census API rate limits.",
)
income_threshold = st.sidebar.slider(
    "Filter Low Household Income (< $)", 20000, 100000, 45000
)
min_commute_time = st.sidebar.slider(
    "Filter High Commute Time (> mins)", 15, 60, 30
)


# Fetch Data from U.S. Census Bureau API with robust error handling
@st.cache_data
def fetch_census_acs_data(api_key=""):
    state_fips = "35"  # New Mexico
    county_fips = "043"  # Sandoval County

    variables = "NAME,B19013_001E,B08303_001E,B08301_001E,B25044_001E,B25044_003E,B25044_010E"
    url = f"https://api.census.gov/data/2022/acs/acs5?get={variables}&for=tract:*&in=state:{state_fips}%20county:{county_fips}"

    if api_key:
        url += f"&key={api_key}"

    try:
        response = requests.get(url, timeout=15)

        # Print debug text in logs if status is not 200
        if response.status_code != 200:
            st.error(
                f"Census API returned status code {response.status_code}. Response: {response.text[:200]}"
            )
            return pd.DataFrame()

        raw_data = response.json()
        if len(raw_data) < 2:
            st.warning("Census API returned empty data rows.")
            return pd.DataFrame()

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

        df["GEOID"] = df["state"] + df["county"] + df["tract"]
        df["Median_Income"] = df["B19013_001E"]
        df["Avg_Commute_Mins"] = np.where(
            df["B08301_001E"] > 0,
            df["B08303_001E"] / df["B08301_001E"],
            np.nan,
        )
        df["Zero_Vehicle_Pct"] = np.where(
            df["B25044_001E"] > 0,
            (df["B25044_003E"] + df["B25044_010E"]) / df["B25044_001E"] * 100,
            np.nan,
        )

        return df

    except requests.exceptions.RequestException as e:
        st.error(
            f"Network connection error when reaching Census API: {e}. Check if your firewall/environment blocks outbound requests to api.census.gov."
        )
    except ValueError as e:
        st.error(
            f"Error parsing JSON response from Census API: {e}. Raw content might not be valid JSON."
        )
    except Exception as e:
        st.error(f"Unexpected error: {e}")

    return pd.DataFrame()


df = fetch_census_acs_data(census_api_key)

if not df.empty:
    # Summary Metrics
    st.header("1. Socioeconomic & Commute Metrics")
    m1, m2, m3 = st.columns(3)

    m1.metric("County Avg Income", f"${df['Median_Income'].mean():,.0f}")
    m2.metric("County Avg Commute", f"{df['Avg_Commute_Mins'].mean():.1f} mins")
    m3.metric("Zero-Vehicle Households", f"{df['Zero_Vehicle_Pct'].mean():.1f}%")

    # Composite Index Calculation
    st.header("2. Overlap & Priority Vulnerability Index")

    df["Income_Need"] = 1 - (df["Median_Income"] / df["Median_Income"].max())
    df["Commute_Need"] = df["Avg_Commute_Mins"] / df["Avg_Commute_Mins"].max()
    df["Vehicle_Need"] = df["Zero_Vehicle_Pct"] / df["Zero_Vehicle_Pct"].max()

    df["Vulnerability_Index"] = (
        (
            df["Income_Need"].fillna(0)
            + df["Commute_Need"].fillna(0)
            + df["Vehicle_Need"].fillna(0)
        )
        / 3
        * 100
    )

    priority_tracts = df[
        (df["Median_Income"] < income_threshold)
        & (df["Avg_Commute_Mins"] > min_commute_time)
    ]

    st.subheader("Priority Areas Requiring Safety & Transit Investment")
    st.dataframe(
        priority_tracts[
            [
                "GEOID",
                "NAME",
                "Median_Income",
                "Avg_Commute_Mins",
                "Zero_Vehicle_Pct",
                "Vulnerability_Index",
            ]
        ],
        use_container_width=True,
    )

    st.header("3. Targeted Recommendations")
    st.markdown("""
    - **Transit Infrastructure:** Launch micro-transit/demand-response shuttles in tracts with high zero-vehicle percentages.
    - **Active Transportation:** Install sidewalks, street lighting, and protected bike lanes along major thoroughfares connecting Cuba to broader county transit networks.
    - **Speed & Traffic Calming:** Prioritize speed reduction measures along corridors with high pedestrian traffic and long rural commute dependencies.
    """)
else:
    st.warning(
        "⚠️ No data could be loaded from the Census API endpoint. If running on Streamlit Cloud, check the app logs for details, or try generating a free Census API key from [census.gov/developers](https://api.census.gov/data/key_signup.html) and entering it in the sidebar."
    )
    
