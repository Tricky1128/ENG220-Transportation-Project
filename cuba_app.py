import io

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Project Cuba Corridor", layout="wide")
st.title("Project Cuba Corridor")
st.write(
    "Crash safety in Cuba, NM and Sandoval County. "
    "Source: UNM Geospatial and Population Studies (UNM-GPS) community crash reports "
    "for NMDOT, 2025 release."
)


# The data is stored right here, so no separate data folder is needed.
DATA_TEXT = {
    "cuba_crashes_by_year.csv": """year,fatal,injury,property_damage_only,total
2016,0,3,7,10
2017,1,3,15,19
2018,0,1,10,11
2019,0,4,4,8
2020,0,4,7,11
2021,0,3,13,16
2022,2,6,6,14
2023,0,3,5,8
2024,0,1,5,6
2025,0,2,3,5
""",
    "cuba_first_harmful_event.csv": """first_harmful_event,year,crashes
Collision with Animal,2021,3
Collision with Fixed Object,2021,7
Collision with Motor Vehicle,2021,4
Collision with Other Non-Fixed Object,2021,1
Collision with Person,2021,0
Pedestrian,2021,0
Non-Collision,2021,1
Collision with Animal,2022,2
Collision with Fixed Object,2022,4
Collision with Motor Vehicle,2022,5
Collision with Other Non-Fixed Object,2022,0
Collision with Person,2022,1
Pedestrian,2022,1
Non-Collision,2022,2
Collision with Animal,2023,1
Collision with Fixed Object,2023,0
Collision with Motor Vehicle,2023,6
Collision with Other Non-Fixed Object,2023,0
Collision with Person,2023,0
Pedestrian,2023,0
Non-Collision,2023,1
Collision with Animal,2024,2
Collision with Fixed Object,2024,1
Collision with Motor Vehicle,2024,3
Collision with Other Non-Fixed Object,2024,0
Collision with Person,2024,0
Pedestrian,2024,0
Non-Collision,2024,0
Collision with Animal,2025,1
Collision with Fixed Object,2025,0
Collision with Motor Vehicle,2025,4
Collision with Other Non-Fixed Object,2025,0
Collision with Person,2025,0
Pedestrian,2025,0
Non-Collision,2025,0
""",
    "cuba_crashes_by_month.csv": """month,year,crashes
January,2021,1
February,2021,2
March,2021,0
April,2021,0
May,2021,1
June,2021,0
July,2021,2
August,2021,1
September,2021,3
October,2021,3
November,2021,3
December,2021,0
January,2022,1
February,2022,1
March,2022,1
April,2022,0
May,2022,2
June,2022,0
July,2022,1
August,2022,1
September,2022,5
October,2022,1
November,2022,1
December,2022,0
January,2023,0
February,2023,0
March,2023,0
April,2023,0
May,2023,1
June,2023,1
July,2023,1
August,2023,1
September,2023,1
October,2023,1
November,2023,2
December,2023,0
January,2024,1
February,2024,1
March,2024,0
April,2024,0
May,2024,0
June,2024,2
July,2024,1
August,2024,0
September,2024,0
October,2024,0
November,2024,1
December,2024,0
January,2025,0
February,2025,0
March,2025,0
April,2025,0
May,2025,0
June,2025,1
July,2025,1
August,2025,0
September,2025,1
October,2025,0
November,2025,0
December,2025,2
""",
    "sandoval_crashes_by_year.csv": """year,fatal,injury,property_damage_only,total
2016,11,569,1350,1930
2017,13,570,1513,2096
2018,20,605,1528,2153
2019,16,655,1467,2138
2020,14,481,1188,1683
2021,17,555,1364,1936
2022,19,564,1482,2065
2023,13,565,1464,2042
2024,16,638,1673,2327
2025,14,666,1908,2588
""",
    "sandoval_first_harmful_event.csv": """first_harmful_event,year,crashes
Collision with Animal,2021,74
Collision with Fixed Object,2021,262
Collision with Motor Vehicle,2021,1392
Collision with Other Non-Fixed Object,2021,49
Collision with Person,2021,26
Pedestrian,2021,13
Non-Collision,2021,82
Collision with Animal,2022,66
Collision with Fixed Object,2022,301
Collision with Motor Vehicle,2022,1488
Collision with Other Non-Fixed Object,2022,55
Collision with Person,2022,21
Pedestrian,2022,9
Non-Collision,2022,77
Collision with Animal,2023,75
Collision with Fixed Object,2023,292
Collision with Motor Vehicle,2023,1473
Collision with Other Non-Fixed Object,2023,44
Collision with Person,2023,40
Pedestrian,2023,25
Non-Collision,2023,86
Collision with Animal,2024,80
Collision with Fixed Object,2024,291
Collision with Motor Vehicle,2024,1680
Collision with Other Non-Fixed Object,2024,53
Collision with Person,2024,28
Pedestrian,2024,12
Non-Collision,2024,104
Collision with Animal,2025,78
Collision with Fixed Object,2025,377
Collision with Motor Vehicle,2025,1948
Collision with Other Non-Fixed Object,2025,84
Collision with Person,2025,30
Pedestrian,2025,14
Non-Collision,2025,67
""",
    "sandoval_animal_crashes_by_type_2025.csv": """animal,people_involved_2025
Elk,72
Deer,29
Small Domestic Animal,20
Cattle/Cow,15
Small Game Animal,14
Bear,6
Missing Subanalysis Data,6
Horse,5
""",
}


def load(name):
    return pd.read_csv(io.StringIO(DATA_TEXT[name]))


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
