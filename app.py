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
本应用展示了 **全球地震与海啸数据（2015–2022）**。  
你可以通过选择年份与震级范围来探索不同的地震特征与趋势。  
""")

@st.cache_data
def load_data():
    df = pd.read_csv("earthquake.csv")

    df = df.dropna(subset=["magnitude", "depth", "Year", "latitude", "longitude"])
    df["Year"] = df["Year"].astype(int)
    df["tsunami"] = df["tsunami"].apply(lambda x: "Yes" if x == 1 else "No")

    return df


data = load_data()

st.sidebar.header("数据筛选")

years = sorted(data["Year"].unique())
selected_year = st.sidebar.selectbox("选择年份", years, index=len(years) - 1)

min_mag = float(data["magnitude"].min())
max_mag = float(data["magnitude"].max())
selected_mag_range = st.sidebar.slider(
    "选择震级范围",
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
    f"### 当前筛选条件：{selected_year} 年，震级范围 {selected_mag_range[0]:.1f} – {selected_mag_range[1]:.1f}"
)

st.subheader("年份平均震级趋势")

avg_mag = data.groupby("Year")["magnitude"].mean().reset_index()

fig1 = px.line(
    avg_mag,
    x="Year",
    y="magnitude",
    title="各年份平均震级变化趋势",
    markers=True,
)
fig1.update_traces(line_color="#FF6B6B", line_width=3)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("地震深度与震级关系（当年数据）")

fig2 = px.scatter(
    filtered,
    x="depth",
    y="magnitude",
    color="tsunami",
    title=f"{selected_year} 年地震深度与震级分布",
    labels={"depth": "地震深度 (km)", "magnitude": "震级"},
    color_discrete_map={"Yes": "#FF5E5E", "No": "#4F9D9D"},
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("海啸事件比例（2015–2022）")

tsunami_count = data["tsunami"].value_counts().reset_index()
tsunami_count.columns = ["Tsunami", "Count"]

fig3 = px.pie(
    tsunami_count,
    names="Tsunami",
    values="Count",
    title="海啸事件比例",
    color="Tsunami",
    color_discrete_map={"Yes": "#FF5E5E", "No": "#4F9D9D"},
)
st.plotly_chart(fig3, use_container_width=True)

st.subheader("全球地震分布地图")

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
        title=f"{selected_year} 年全球地震分布图（按震级显示）",
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
    st.info("当前筛选条件下没有地震数据，请调整震级范围或年份。")

with st.expander("查看筛选后的数据（前20行）"):
    st.dataframe(filtered.head(20))


st.markdown("---")
st.markdown(
    "**开发者：** 张韩乐然 张祉谦 张明皓 ｜ **数据来源：** Global Earthquake Dataset (2015–2022)"
)
