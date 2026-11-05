from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Project Cuba Corridor", layout="wide")
st.title("Project Cuba Corridor")
st.write(
    "Crash safety in Cuba, NM and Sandoval County. "
    "Source: UNM Geospatial and Population Studies (UNM-GPS) community crash reports "
    "for NMDOT, 2025 release."
)


def find_file(name):
    # Finds the file even if the download added a suffix like " (1)"
    stem = name.replace(".csv", "")
    matches = sorted(DATA.glob(stem + "*.csv")) if DATA.exists() else []
    if not matches:
        st.error(f"Could not find {name} in the data folder.")
        st.write("Data folder exists:", DATA.exists())
        if DATA.exists():
            st.write("Files found in data folder:", [p.name for p in DATA.iterdir()])
        else:
            st.write("Files found next to the app:", [p.name for p in DATA.parent.iterdir()])
        st.stop()
    return matches[-1]


@st.cache_data
def read_csv_cached(path):
    return pd.read_csv(path)


def load(name):
    return read_csv_cached(find_file(name))


cuba_year = load("cuba_crashes_by_year.csv")
cuba_event = load("cuba_first_harmful_event.csv")
cuba_month = load("cuba_crashes_by_month.csv")
sand_year = load("sandoval_crashes_by_year.csv")
sand_event = load("sandoval_first_harmful_event.csv")
sand_animal = load("sandoval_animal_crashes_by_type_2025.csv")

tab1, tab2, tab3 = st.tabs(["Cuba crashes", "Animal crashes", "About the data"])

# ---------- Tab 1: Cuba crashes ----------
with tab1:
    st.subheader("Crashes per year in Cuba village, 2016 to 2025")
    fig1 = px.bar(
        cuba_year,
        x="year",
        y=["fatal", "injury", "property_damage_only"],
        labels={"value": "Crashes", "year": "Year", "variable": "Severity"},
    )
    fig1.update_xaxes(type="category")
    fig1.update_layout(bargap=0.4)
    st.plotly_chart(fig1)
    st.caption(
        f"Total crashes dropped from {int(cuba_year.total.iloc[0])} in 2016 "
        f"to {int(cuba_year.total.iloc[-1])} in 2025. Numbers are small, so one crash "
        "can change the trend."
    )

    st.subheader("Cuba crashes by month, 2021 to 2025 combined")
    months = [
        "January", "February", "March", "April", "May", "June", "July",
        "August", "September", "October", "November", "December",
    ]
    m = cuba_month.groupby("month", as_index=False)["crashes"].sum()
    m["month"] = pd.Categorical(m["month"], categories=months, ordered=True)
    m = m.sort_values("month")
    fig2 = px.bar(m, x="month", y="crashes", labels={"month": "Month", "crashes": "Crashes"})
    fig2.update_layout(bargap=0.5)
    st.plotly_chart(fig2)

# ---------- Tab 2: Animal crashes ----------
with tab2:
    def animal_share(event_df, year_df):
        animal = event_df[event_df.first_harmful_event == "Collision with Animal"]["crashes"].sum()
        total = year_df[year_df.year >= 2021]["total"].sum()
        return int(animal), int(total), 100 * animal / total

    c_a, c_t, c_p = animal_share(cuba_event, cuba_year)
    s_a, s_t, s_p = animal_share(sand_event, sand_year)

    st.subheader("Share of crashes that started with hitting an animal, 2021 to 2025")
    share = pd.DataFrame(
        {
            "Area": ["Cuba village", "Sandoval County"],
            "Percent of crashes": [c_p, s_p],
        }
    )
    fig3 = px.bar(share, x="Area", y="Percent of crashes", text_auto=".1f")
    fig3.update_layout(bargap=0.6)
    st.plotly_chart(fig3)
    st.caption(
        f"Cuba: {c_a} of {c_t} crashes. Sandoval County: {s_a} of {s_t} crashes. "
        "The county includes Rio Rancho and Bernalillo, so it is a baseline and not "
        "the US 550 corridor."
    )

    st.subheader("Sandoval County: people in animal crashes by animal type, 2025")
    fig4 = px.bar(
        sand_animal.sort_values("people_involved_2025"),
        x="people_involved_2025",
        y="animal",
        orientation="h",
        labels={"people_involved_2025": "People involved", "animal": "Animal"},
    )
    fig4.update_layout(bargap=0.4)
    st.plotly_chart(fig4)
    st.caption("This table counts people, not crashes, and covers 2025 only.")

# ---------- Tab 3: About the data ----------
with tab3:
    st.subheader("Sources")
    st.markdown(
        "- UNM-GPS Community Crash Reports (NMDOT crash database): "
        "https://gps.unm.edu/tru/reports/community-reports/index.html\n"
        "- NMDOT US 550 Wildlife Crossing Project: "
        "https://www.dot.nm.gov/projects/active-projects/us550wildlifeproject/"
    )
    st.subheader("Limitations")
    st.markdown(
        "- Cuba numbers cover the village only, not US 550 north of town.\n"
        "- Counts are small, so trends can change with one or two crashes.\n"
        "- The data covers reported crashes with a death, an injury, or at least $500 in damage.\n"
        "- The data does not give crash locations, so it cannot be mapped by milepost."
    )
