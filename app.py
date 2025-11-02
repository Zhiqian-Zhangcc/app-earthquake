import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Earthquake & Tsunami Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Earthquake & Tsunami Data Explorer")
st.markdown("""
This application displays global earthquake and tsunami data (2015–2022).
You can explore different earthquake characteristics and trends by selecting the year and magnitude range. 
""")

@st.cache_data
def load_data():
    df = pd.read_csv("earthquake.csv")

    df = df.dropna(subset=["magnitude", "depth", "Year", "latitude", "longitude"])
    df["Year"] = df["Year"].astype(int)
    df["tsunami"] = df["tsunami"].apply(lambda x: "Yes" if x == 1 else "No")

    return df


data = load_data()

st.sidebar.header("Data Filtering")

years = sorted(data["Year"].unique())
selected_year = st.sidebar.selectbox("Select Year", years, index=len(years) - 1)

min_mag = float(data["magnitude"].min())
max_mag = float(data["magnitude"].max())
selected_mag_range = st.sidebar.slider(
    "Select Magnitude Range",
    min_value=min_mag,
    max_value=max_mag,
    value=(min_mag, max_mag),
    step=0.1,
)

filtered = data[
    (data["Year"] == selected_year)
    & (data["magnitude"].between(selected_mag_range[0], selected_mag_range[1]))
]

st.markdown(
    f"### Current Filter Criteria：{selected_year} Year, Magnitude Range {selected_mag_range[0]:.1f} – {selected_mag_range[1]:.1f}"
)

st.subheader("Average Magnitude Trend by Year")

avg_mag = data.groupby("Year")["magnitude"].mean().reset_index()

fig1 = px.line(
    avg_mag,
    x="Year",
    y="magnitude",
    title="Variation Trend of Average Magnitude Across Years",
    markers=True,
)
fig1.update_traces(line_color="#FF6B6B", line_width=3)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Relationship Between Earthquake Depth and Magnitude (Data of the Current Year)")

fig2 = px.scatter(
    filtered,
    x="depth",
    y="magnitude",
    color="tsunami",
    title=f"{selected_year} Earthquake Depth and Magnitude Distribution of [the Year]",
    labels={"depth": "Earthquake Depth (km)", "magnitude": "Magnitude"},
    color_discrete_map={"Yes": "#FF5E5E", "No": "#4F9D9D"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Tsunami Event Proportion (2015–2022)")

tsunami_count = data["tsunami"].value_counts().reset_index()
tsunami_count.columns = ["Tsunami", "Count"]

fig3 = px.pie(
    tsunami_count,
    names="Tsunami",
    values="Count",
    title="Tsunami Event Proportion",
    color="Tsunami",
    color_discrete_map={"Tsunami": "#FF5E5E", "Earthquake": "#4F9D9D"},
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("Global Earthquake Distribution Map")

if not filtered.empty:
    fig_map = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        color="magnitude",
        size="magnitude",
        hover_name="place" if "place" in filtered.columns else None,
        hover_data=["depth", "tsunami"],
        projection="natural earth",
        title=f"{selected_year} Global Earthquake Distribution Map of [the Year] (Displayed by Magnitude)",
        color_continuous_scale="Reds",
        size_max=10,
    )

    fig_map.update_geos(
        showland=True,
        landcolor="rgb(230, 230, 230)",
        showcountries=True,
        countrycolor="white",
    )

    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.info("There is no earthquake data under the current filter criteria. Please adjust the magnitude range or year.")

with st.expander("View Filtered Data (First 20 Rows)"):
    st.dataframe(filtered.head(20))


st.markdown("---")
st.markdown(
   "Developer(s): Zhang Hanleran, Zhang Zhiqian, Zhang Minghao ｜ Data Source: Global Earthquake Dataset (2015–2022)"
)
