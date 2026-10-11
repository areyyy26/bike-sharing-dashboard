import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

st.title("🚲 Bike Sharing Dashboard")
st.caption("Dashboard interaktif untuk mengeksplorasi pola penyewaan sepeda.")

BASE_DIR = Path(__file__).resolve().parent
CANDIDATE_PATHS = [
    BASE_DIR / "main_data.csv",
    BASE_DIR.parent / "data" / "hour.csv",
    BASE_DIR / "hour.csv",
]

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    data["dteday"] = pd.to_datetime(data["dteday"], errors="coerce")
    return data

data_path = next((path for path in CANDIDATE_PATHS if path.exists()), None)

if data_path is None:
    st.error(
        "Dataset tidak ditemukan. letakkan file hour.csv di folder data/ "
        "atau salin dataset menjadi dashboard/main_data.csv."
    )
    st.stop()

df = load_data(str(data_path))

required_columns = {"dteday", "hr", "cnt", "season", "weathersit"}
missing_columns = required_columns - set(df.columns)
if missing_columns:
    st.error(f"Kolom wajib tidak ditemukan: {', '.join(sorted(missing_columns))}")
    st.stop()

season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_mapping = {
    1: "Clear",
    2: "Mist / Cloudy",
    3: "Light Rain / Snow",
    4: "Heavy Rain / Snow",
}
df["season_label"] = df["season"].map(season_mapping).fillna("Unknown")
df["weather_label"] = df["weathersit"].map(weather_mapping).fillna("Unknown")

# Sidebar filters
st.sidebar.header("Filter Dashboard")
min_date = df["dteday"].min().date()
max_date = df["dteday"].max().date()
date_range = st.sidebar.date_input(
    "Rentang tanggal",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

season_options = sorted(df["season_label"].dropna().unique().tolist())
selected_seasons = st.sidebar.multiselect(
    "Musim",
    options=season_options,
    default=season_options,
)
weather_options = sorted(df["weather_label"].dropna().unique().tolist())
selected_weather = st.sidebar.multiselect(
    "Kondisi cuaca",
    options=weather_options,
    default=weather_options,
)

filtered = df.copy()

if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_date, end_date = date_range
    elif len(date_range) == 1:
        start_date = end_date = date_range[0]
    else:
        st.warning("Pilih rentang tanggal yang valid.")
        st.stop()
else:
    start_date = end_date = date_range

filtered = df[
    df["dteday"].dt.date.between(start_date, end_date)
].copy()

if selected_seasons:
    filtered = filtered[filtered["season_label"].isin(selected_seasons)]
else:
    filtered = filtered.iloc[0:0]
if selected_weather:
    filtered = filtered[filtered["weather_label"].isin(selected_weather)]
else:
    filtered = filtered.iloc[0:0]

if filtered.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Ubah filter di sidebar.")
    st.stop()

# KPI
total_rentals = int(filtered["cnt"].sum())
average_rentals = filtered["cnt"].mean()
active_days = filtered["dteday"].dt.date.nunique()
col1, col2, col3 = st.columns(3)
col1.metric("Total penyewaan", f"{total_rentals:,}".replace(",", "."))
col2.metric("Rata-rata penyewaan per jam", f"{average_rentals:,.1f}".replace(",", "X").replace(".", ",").replace("X", "."))
col3.metric("Jumlah hari dalam data", f"{active_days:,}".replace(",", "."))

st.divider()

# business question 1: hourly pattern
st.subheader("1. Bagaimana pola penyewaan berdasarkan jam?")
hourly = (
    filtered.groupby("hr", as_index=False)["cnt"]
    .sum()
    .sort_values("hr")
)
fig_hour = px.line(
    hourly, x="hr", y="cnt", markers=True,
    title="Total Penyewaan Sepeda Berdasarkan Jam",
    labels={"hr": "Jam", "cnt": "Total penyewaan"},
)
fig_hour.update_layout(
    xaxis=dict(
        tickmode="linear",
        tick0=0,
        dtick=1,
        range=[-0.5, 23.5],
        title="Jam",
    ),
    yaxis=dict(
        rangemode="tozero",
        title="Total penyewaan",
    ),
)

st.plotly_chart(
    fig_hour,
    use_container_width=True,
    key="hour_chart"
)


if not hourly.empty:
    top_hour = hourly.loc[hourly["cnt"].idxmax()]
    lowest_hour = hourly.loc[hourly["cnt"].idxmin()]

    st.info(
        f"Jam dengan total penyewaan tertinggi adalah "
        f"{int(top_hour['hr']):02d}.00 "
        f"({int(top_hour['cnt']):,} penyewaan), sedangkan "
        f"jam terendah adalah {int(lowest_hour['hr']):02d}.00 "
        f"({int(lowest_hour['cnt']):,} penyewaan)."
        .replace(",", ".")
    )



# Business question 2: average rentals by season and weather
left, right = st.columns(2)


with left:
    season_summary = (
        filtered.groupby("season_label", as_index=False)
        .agg(
            average_rentals=("cnt", "mean"),
            observations=("cnt", "size")
        )
    )

    season_order = ["Spring", "Summer", "Fall", "Winter"]

    season_summary["season_label"] = pd.Categorical(
        season_summary["season_label"],
        categories=season_order,
        ordered=True
    )

    season_summary = season_summary.sort_values("season_label")

    fig_season = px.bar(
        season_summary,
        x="season_label",
        y="average_rentals",
        title="Rata-rata Penyewaan Berdasarkan Musim",
        labels={
            "season_label": "Musim",
            "average_rentals": "Rata-rata penyewaan per jam"
        },
        category_orders={
            "season_label": season_order
        }
    )

    st.plotly_chart(fig_season, use_container_width=True)

    if not season_summary.empty:
        best_season = season_summary.loc[
            season_summary["average_rentals"].idxmax()
        ]
        st.info(
            f"Rata-rata tertinggi menurut musim: "
            f"{best_season['season_label']} "
            f"({best_season['average_rentals']:.2f} penyewaan per jam)."
        )


with right:
    weather_summary = (
        filtered.groupby("weather_label", as_index=False)
        .agg(
            average_rentals=("cnt", "mean"),
            observations=("cnt", "size")
        )
        .sort_values("average_rentals", ascending=False)
    )

    fig_weather = px.bar(
        weather_summary,
        x="weather_label",
        y="average_rentals",
        title="Rata-rata Penyewaan Berdasarkan Cuaca",
        labels={
            "weather_label": "Kondisi cuaca",
            "average_rentals": "Rata-rata penyewaan per jam"
        }
    )
    st.plotly_chart(fig_weather, use_container_width=True)

    if not weather_summary.empty:
        best_weather = weather_summary.iloc[0]
        st.info(
            f"Rata-rata tertinggi menurut cuaca: "
            f"{best_weather['weather_label']} "
            f"({best_weather['average_rentals']:.2f} penyewaan per jam)."
        )


st.subheader("Rata-rata penyewaan per jam berdasarkan musim dan cuaca")
avg_season = (
    filtered.groupby("season_label", as_index=False)["cnt"]
    .mean().rename(columns={"cnt": "rata_rata_penyewaan"})
)
avg_weather = (
    filtered.groupby("weather_label", as_index=False)["cnt"]
    .mean().rename(columns={"cnt": "rata_rata_penyewaan"})
)
tab1, tab2 = st.tabs(["Musim", "Cuaca"])
with tab1:
    st.dataframe(avg_season.round(2), use_container_width=True, hide_index=True)
with tab2:
    st.dataframe(avg_weather.round(2), use_container_width=True, hide_index=True)

with st.expander("Lihat data yang digunakan"):
    display_columns = [
        col for col in [
            "dteday", "hr", "season_label", "weather_label",
            "casual", "registered", "cnt"
        ] if col in filtered.columns
    ]
    st.dataframe(filtered[display_columns], use_container_width=True, hide_index=True)

st.caption(
    "Catatan: angka pada dashboard mengikuti filter yang dipilih. "
    "Total penyewaan adalah penjumlahan cnt pada data terfilter."
)
