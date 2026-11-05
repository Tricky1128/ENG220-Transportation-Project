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
    "us550_phase_crashes.csv": """phase,mileposts,miles,deer_crashes,elk_crashes,total_crashes,crashes_per_mile
Phase 1,MP 64.93 to 69.14,4.21,42,73,115,27.3
Phase 2,MP 69.14 to 72.98,3.84,38,60,98,25.5
Phase 3,MP 72.98 to 75.62,2.64,33,31,64,24.2
Phase 4,MP 75.62 to 80.64,5.02,52,70,122,24.3
""",
    "us550_planned_structures.csv": """structure,type,milepost,phase
WC-01,Overpass,65.97,Phase 1
WC-04,Underpass,67.55,Phase 1
WC-05,Overpass,68.46,Phase 5
WC-07,Overpass,70.28,Phase 2
WC-08,Underpass,71.81,Phase 2
WC-10,Underpass,72.99,Phase 3
WC-12,Underpass,74.85,Phase 3
WC-16,Overpass,76.98,Phase 4
""",
}


def load(name):
    return pd.read_csv(io.StringIO(DATA_TEXT[name]))


cuba_year = load("cuba_crashes_by_year.csv")
cuba_event = load("cuba_first_harmful_event.csv")
cuba_month = load("cuba_crashes_by_month.csv")
sand_year = load("sandoval_crashes_by_year.csv")
sand_event = load("sandoval_first_harmful_event.csv")

tab1, tab2, tab_us550, tab3 = st.tabs(
    ["Cuba crashes", "Animal crashes", "US 550 wildlife corridor", "About the data"]
)

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
    st.caption(
        f"Only {int(m.crashes.sum())} crashes over five years, so this pattern is weak. "
        "One crash can move a bar. Treat it as a rough look, not a seasonal trend."
    )

# ---------- Tab 2: Animal crashes ----------
with tab2:
    def animal_by_year(event_df, year_df):
        a = event_df[event_df.first_harmful_event == "Collision with Animal"][["year", "crashes"]]
        t = year_df[year_df.year >= 2021][["year", "total"]]
        out = a.merge(t, on="year")
        out["percent"] = 100 * out["crashes"] / out["total"]
        return out

    cu = animal_by_year(cuba_event, cuba_year)
    cu["Area"] = "Cuba village"
    sa = animal_by_year(sand_event, sand_year)
    sa["Area"] = "Sandoval County"
    both = pd.concat([cu, sa])

    st.subheader("Share of crashes that started with hitting an animal, by year")
    fig3 = px.bar(
        both,
        x="year",
        y="percent",
        color="Area",
        barmode="group",
        text_auto=".1f",
        labels={"percent": "Percent of all crashes", "year": "Year"},
    )
    fig3.update_xaxes(type="category")
    fig3.update_layout(bargap=0.4)
    st.plotly_chart(fig3)

    cu_a, cu_t = int(cu.crashes.sum()), int(cu.total.sum())
    sa_a, sa_t = int(sa.crashes.sum()), int(sa.total.sum())
    st.caption(
        f"2021 to 2025: Cuba had {cu_a} animal crashes out of {cu_t} total "
        f"({100 * cu_a / cu_t:.1f}%). Sandoval County had {sa_a} out of {sa_t:,} "
        f"({100 * sa_a / sa_t:.1f}%)."
    )
    st.info(
        "How to read this: Cuba's share was higher than the county's in every year, "
        "but Cuba had only 1 to 3 animal crashes a year, so one crash moves its bar a lot. "
        "Sandoval County is mostly urban. Rio Rancho alone was about 64% of county crashes "
        "from 2021 to 2025, and 87% of county crashes in 2025 were on urban roads. So this "
        "compares a rural village with a mostly suburban county, and part of the gap may be "
        "rural versus urban driving. The data does not say which road each crash was on."
    )

    st.subheader("Cuba village by animal type")
    st.markdown(
        "The UNM table that splits animal crashes by type only covers one year in the file "
        "I used, 2025. In 2025 Cuba had 1 animal crash, and it involved **elk**. Two people "
        "were in it, with no apparent injuries. Every other animal type was zero. "
        "One crash is too few to draw a conclusion, so the elk and deer breakdown on the "
        "next tab, which covers the US 550 hotspot north of Cuba, is the better source "
        "for animal types."
    )


# ---------- Tab: US 550 wildlife corridor ----------
with tab_us550:
    ph = load("us550_phase_crashes.csv")
    structures = load("us550_planned_structures.csv")

    st.subheader("Reported elk and deer crashes on US 550 north of Cuba, 2008 to 2021")
    st.write(
        "NMDOT's scoping report split the wildlife hotspot (MP 64.93 to MP 80.64) into "
        "four building phases. These are the reported crashes in each phase."
    )
    ph["label"] = ph["phase"] + " (" + ph["mileposts"] + ")"
    long = ph.melt(
        id_vars=["label"],
        value_vars=["elk_crashes", "deer_crashes"],
        var_name="Animal",
        value_name="Crashes",
    )
    long["Animal"] = long["Animal"].map({"elk_crashes": "Elk", "deer_crashes": "Mule deer"})
    fig5 = px.bar(long, x="label", y="Crashes", color="Animal", labels={"label": ""})
    fig5.update_layout(bargap=0.4)
    st.plotly_chart(fig5)

    st.subheader("Crashes per mile in each phase")
    fig6 = px.bar(
        ph,
        x="label",
        y="crashes_per_mile",
        text_auto=".1f",
        labels={"label": "", "crashes_per_mile": "Reported crashes per mile, 2008 to 2021"},
    )
    fig6.update_layout(bargap=0.5)
    st.plotly_chart(fig6)
    st.caption(
        f"Total: {int(ph.total_crashes.sum())} crashes over {ph.miles.sum():.2f} miles "
        f"({int(ph.elk_crashes.sum())} elk, {int(ph.deer_crashes.sum())} mule deer). "
        "Crashes per mile are close to even across the four phases, about 24 to 27 per mile, "
        "so the whole stretch is a hotspot and not one single spot."
    )

    st.subheader("Which animals: elk vs mule deer")
    sp = pd.DataFrame(
        {
            "Animal": ["Elk", "Mule deer"],
            "Crashes": [int(ph.elk_crashes.sum()), int(ph.deer_crashes.sum())],
        }
    )
    sp["Label"] = sp["Crashes"].astype(str) + " (" + (100 * sp["Crashes"] / sp["Crashes"].sum()).round(1).astype(str) + "%)"
    fig7 = px.bar(sp, x="Animal", y="Crashes", text="Label")
    fig7.update_layout(bargap=0.6)
    st.plotly_chart(fig7)
    st.caption(
        "Reported elk and mule deer crashes, MP 64.93 to 80.64, 2008 to 2021. "
        "Other animals such as bears or cougars are not in these tables."
    )

    st.subheader("Planned wildlife crossings (from the scoping report)")
    st.dataframe(structures, hide_index=True)
    st.caption(
        "Phase 5 is optional in the report. NMDOT notes it is a low crossing-activity area "
        "and an overpass there may not be very effective."
    )

    st.info(
        "Read this carefully: (1) These counts only include crashes with elk and mule deer. "
        "Other animals were left out of the report's tables. "
        "(2) They are reported crashes only. The report says many wildlife crashes are never "
        "reported and the real number on US 550 could be much higher. "
        "(3) The report's introduction says 208 wildlife crashes from 2009 to 2022, while its "
        "tables say 399 elk and deer crashes from 2008 to 2021. The report does not explain "
        "the difference in what I read, so each number is labeled with its own years here. "
        "(4) This corridor is north and west of Cuba village, so these crashes are not in the "
        "village numbers on the other tabs."
    )


# ---------- Tab 3: About the data ----------
with tab3:
    st.subheader("Sources")
    st.markdown(
        "- UNM-GPS Community Crash Reports (NMDOT crash database): "
        "https://gps.unm.edu/tru/reports/community-reports/index.html\n"
        "- NMDOT US 550 Wildlife Crossing Project: "
        "https://www.dot.nm.gov/projects/active-projects/us550wildlifeproject/\n"
        "- NMDOT, US-550 MP 64.93 to MP 80.64 WVC Mitigation Scoping Report, July 2023 "
        "(crash counts by phase and planned crossing locations), linked from the project page above."
    )
    st.subheader("Limitations")
    st.markdown(
        "- Cuba numbers cover the village only, not US 550 north of town.\n"
        "- Counts are small, so trends can change with one or two crashes.\n"
        "- The county comparison is mostly Rio Rancho and other urban roads, so it is a rough "
        "baseline, not a like-for-like comparison.\n"
        "- The data covers reported crashes with a death, an injury, or at least $500 in damage.\n"
        "- The UNM data does not give crash locations, so the Cuba and county charts cannot be "
        "mapped by milepost. The US 550 tab uses the scoping report's counts by phase instead."
    )
