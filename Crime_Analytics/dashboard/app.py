"""
Crime Analytics Dashboard - India - NO DATABASE VERSION
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
HERO_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Police_Lights.jpg/3840px-Police_Lights.jpg"


st.set_page_config(
    page_title="Crime Analytics Dashboard - India",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

        :root {{
            --bg: #081018;
            --panel: rgba(10, 18, 28, 0.82);
            --panel-strong: rgba(9, 14, 22, 0.94);
            --border: rgba(255, 255, 255, 0.09);
            --text: #f6f4ed;
            --muted: #aeb9c7;
            --red: #ff5f5f;
            --amber: #ffbd59;
            --blue: #88d9ff;
        }}

        .stApp {{
            background:
                linear-gradient(180deg, rgba(6, 12, 18, 0.92), rgba(6, 12, 18, 0.98)),
                radial-gradient(circle at top right, rgba(255, 95, 95, 0.08), transparent 24%),
                linear-gradient(135deg, #05090e 0%, #0a1018 100%);
            color: var(--text);
            font-family: 'Space Grotesk', sans-serif;
        }}

        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(10, 16, 24, 0.98), rgba(7, 11, 18, 0.98));
            border-right: 1px solid var(--border);
        }}

        .block-container {{
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }}

        h1, h2, h3, p, span, label, div {{
            font-family: 'Space Grotesk', sans-serif;
        }}

        .hero {{
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            min-height: 280px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background:
                linear-gradient(90deg, rgba(6, 10, 16, 0.90) 0%, rgba(6, 10, 16, 0.70) 45%, rgba(6, 10, 16, 0.45) 100%),
                url('{HERO_IMAGE_URL}');
            background-size: cover;
            background-position: center;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 24px 44px rgba(0, 0, 0, 0.28);
        }}

        .eyebrow {{
            font-family: 'IBM Plex Mono', monospace;
            color: var(--amber);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.76rem;
        }}

        .hero h1 {{
            margin: 0.5rem 0 0.4rem 0;
            font-size: 2.5rem;
            letter-spacing: -0.04em;
            max-width: 680px;
        }}

        .hero-copy {{
            max-width: 620px;
            color: #edf2f8;
            font-size: 1rem;
            line-height: 1.5;
        }}

        .mini-note {{
            color: var(--muted);
            font-size: 0.86rem;
            margin-top: 0.75rem;
        }}

        .section-tag {{
            color: var(--amber);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.76rem;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin: 0.9rem 0 0.45rem 0;
        }}

        .focus-strip {{
            background: linear-gradient(135deg, rgba(255, 95, 95, 0.08), rgba(136, 217, 255, 0.05));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.9rem;
        }}

        .focus-title {{
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        .focus-copy {{
            color: var(--muted);
            font-size: 0.94rem;
        }}

        div[data-testid="stMetric"] {{
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 0.65rem 0.9rem;
        }}

        div[data-testid="stDataFrame"], div[data-testid="stPlotlyChart"] {{
            background: var(--panel-strong);
            border-radius: 18px;
            border: 1px solid var(--border);
            padding: 0.35rem;
        }}

        @media (max-width: 900px) {{
            .hero h1 {{
                font-size: 2rem;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#f6f4ed", "family": "Space Grotesk, sans-serif"},
        "xaxis": {
            "gridcolor": "rgba(255,255,255,0.08)",
            "tickfont": {"color": "#cfd8e3"},
            "title_font": {"color": "#aeb9c7"},
        },
        "yaxis": {
            "gridcolor": "rgba(255,255,255,0.08)",
            "tickfont": {"color": "#cfd8e3"},
            "title_font": {"color": "#aeb9c7"},
        },
        "legend": {
            "font": {"color": "#f6f4ed"},
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        "margin": {"l": 20, "r": 20, "t": 56, "b": 24},
    }
}


@st.cache_resource
def get_conn():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "india_crime_analytics"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
        )
    except Exception:
        return None


@st.cache_data
def load_local_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(DATA_DIR / "crime_state_year.csv"),
        pd.read_csv(DATA_DIR / "crime_city_year.csv"),
    )


@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, str]:
    conn = get_conn()
    if conn is not None:
        try:
            state_df = pd.read_sql(
                "SELECT * FROM crime_state_year ORDER BY year, state, crime_category",
                conn,
            )
            city_df = pd.read_sql(
                "SELECT * FROM crime_city_year ORDER BY year, state, city",
                conn,
            )
            return state_df, city_df, "PostgreSQL"
        except Exception:
            pass
    state_df, city_df = load_local_data()
    return state_df, city_df, "Local CSV fallback"


def format_number(value: float | int) -> str:
    return f"{int(round(value)):,}"


def safe_first(frame: pd.DataFrame, column: str, default: str = "N/A") -> str:
    if frame.empty or column not in frame.columns:
        return default
    value = frame.iloc[0][column]
    return str(value) if pd.notna(value) else default


state_df, city_df, source_label = load_data()

with st.sidebar:
    st.markdown("### 🚨 Filters")
    all_categories = sorted(state_df["crime_category"].unique().tolist())
    selected_categories = st.multiselect("Crime Categories", all_categories, default=all_categories)
    all_states = sorted(state_df["state"].unique().tolist())
    focus_state = st.selectbox("Deep-Dive State", all_states, index=0)
    year_min, year_max = int(state_df["year"].min()), int(state_df["year"].max())
    year_range = st.slider("Year Range", year_min, year_max, (year_min, year_max))

national_state = state_df[
    (state_df["crime_category"].isin(selected_categories))
    & (state_df["year"].between(*year_range))
].copy()

focus_state_df = national_state[national_state["state"] == focus_state].copy()
focus_city_df = city_df[
    (city_df["state"] == focus_state) & (city_df["year"].between(*year_range))
].copy()

if national_state.empty:
    st.warning("No national records match the current filters. Broaden the filters and try again.")
    st.stop()

if focus_state_df.empty:
    st.warning(f"No deep-dive records are available for {focus_state} under the current filters.")
    st.stop()

latest_year = int(national_state["year"].max())
latest_slice = national_state[national_state["year"] == latest_year].copy()
prev_slice = national_state[national_state["year"] == latest_year - 1].copy()

focus_latest_year = int(focus_state_df["year"].max())
focus_latest = focus_state_df[focus_state_df["year"] == focus_latest_year].copy()
focus_city_latest = focus_city_df[focus_city_df["year"] == focus_latest_year].copy()

total_cases = int(national_state["cases_reported"].sum())
avg_rate = float(latest_slice["crime_rate_per_100k"].mean()) if not latest_slice.empty else 0.0
prev_total = float(prev_slice["cases_reported"].sum()) if not prev_slice.empty else 0.0
current_total = float(latest_slice["cases_reported"].sum()) if not latest_slice.empty else 0.0
yoy = ((current_total - prev_total) / prev_total * 100) if prev_total else 0.0
top_state = (
    latest_slice.groupby("state", as_index=False)["cases_reported"].sum().sort_values("cases_reported", ascending=False).head(1)["state"].iloc[0]
    if not latest_slice.empty
    else "N/A"
)

focus_top_category = (
    focus_latest.groupby("crime_category", as_index=False)["cases_reported"]
    .sum()
    .sort_values("cases_reported", ascending=False)
    .head(1)
)
focus_fastest_growth = (
    focus_state_df.groupby("crime_category", as_index=False)["yoy_change_pct"]
    .mean()
    .sort_values("yoy_change_pct", ascending=False)
    .head(1)
)
focus_safest_city = focus_city_latest.sort_values("crime_rate_per_100k").head(1)

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">India Crime Analytics</div>
        <h1>See the pressure points fast.</h1>
        <div class="hero-copy">
            Filter national crime trends, compare states, and inspect one selected state in detail.
        </div>
        <div class="mini-note">Source: {source_label} | National latest year: {latest_year} | Deep-dive state: {focus_state} ({focus_latest_year})</div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Recorded Cases", format_number(total_cases))
metric_cols[1].metric("Avg Crime Rate", f"{avg_rate:.1f}")
metric_cols[2].metric("YoY Shift", f"{yoy:+.1f}%")
metric_cols[3].metric("Highest Pressure State", top_state)

st.markdown('<div class="section-tag">National Overview</div>', unsafe_allow_html=True)
col1, col2 = st.columns((1.15, 0.85))

with col1:
    trend_df = (
        national_state.groupby(["year", "crime_category"], as_index=False)["cases_reported"]
        .sum()
        .sort_values("year")
    )
    fig_trend = px.line(
        trend_df,
        x="year",
        y="cases_reported",
        color="crime_category",
        markers=True,
        color_discrete_sequence=["#ff5f5f", "#ffbd59", "#88d9ff", "#8ddf9b", "#d891ff"],
    )
    fig_trend.update_traces(line=dict(width=3), marker=dict(size=7))
    fig_trend.update_layout(template=PLOTLY_TEMPLATE, height=400, title="Crime Volume by Category")
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    state_rank = (
        latest_slice.groupby("state", as_index=False)
        .agg(
            cases_reported=("cases_reported", "sum"),
            crime_rate_per_100k=("crime_rate_per_100k", "mean"),
        )
        .sort_values(["crime_rate_per_100k", "cases_reported"], ascending=[False, False])
        .head(10)
    )
    fig_rank = px.bar(
        state_rank.sort_values("crime_rate_per_100k"),
        x="crime_rate_per_100k",
        y="state",
        orientation="h",
        color="crime_rate_per_100k",
        color_continuous_scale=["#88d9ff", "#ffbd59", "#ff5f5f"],
        hover_data=["cases_reported"],
    )
    fig_rank.update_layout(template=PLOTLY_TEMPLATE, height=400, coloraxis_showscale=False, title=f"Highest Crime Rate States ({latest_year})")
    st.plotly_chart(fig_rank, use_container_width=True)

st.markdown('<div class="section-tag">State Deep-Dive</div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="focus-strip">
        <div class="focus-title">{focus_state} Deep Dive</div>
        <div class="focus-copy">
            Top category: {safe_first(focus_top_category, 'crime_category')} |
            Fastest growth: {safe_first(focus_fastest_growth, 'crime_category')} |
            Lowest city rate: {safe_first(focus_safest_city, 'city')}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

focus_metric_cols = st.columns(4)
focus_metric_cols[0].metric(f"{focus_state} Cases", format_number(focus_latest["cases_reported"].sum()))
focus_metric_cols[1].metric(f"{focus_state} Avg Rate", f"{focus_latest['crime_rate_per_100k'].mean():.1f}")
focus_metric_cols[2].metric("Top Category", safe_first(focus_top_category, "crime_category"))
focus_metric_cols[3].metric("Cities Tracked", format_number(len(focus_city_latest)))

col3, col4 = st.columns((1.05, 0.95))

with col3:
    focus_trend = (
        focus_state_df.groupby(["year", "crime_category"], as_index=False)["cases_reported"]
        .sum()
        .sort_values("year")
    )
    fig_focus = px.area(
        focus_trend,
        x="year",
        y="cases_reported",
        color="crime_category",
        color_discrete_sequence=["#ff5f5f", "#ffbd59", "#88d9ff", "#8ddf9b", "#d891ff"],
    )
    fig_focus.update_layout(template=PLOTLY_TEMPLATE, height=410, title=f"{focus_state} Crime Trend")
    st.plotly_chart(fig_focus, use_container_width=True)

with col4:
    city_rank = (
        focus_city_latest.sort_values(["crime_rate_per_100k", "cases_reported"], ascending=[False, False])
        .head(10)
    )
    fig_city = px.scatter(
        city_rank,
        x="detection_rate",
        y="crime_rate_per_100k",
        size="cases_reported",
        color="severity_index",
        hover_name="city",
        color_continuous_scale=["#88d9ff", "#ffbd59", "#ff5f5f"],
        labels={
            "detection_rate": "Detection Rate %",
            "crime_rate_per_100k": "Crime Rate per 100k",
            "severity_index": "Severity",
        },
    )
    fig_city.update_layout(template=PLOTLY_TEMPLATE, height=410, title=f"{focus_state} Urban Hotspots ({focus_latest_year})")
    st.plotly_chart(fig_city, use_container_width=True)

col5, col6 = st.columns((0.95, 1.05))

with col5:
    focus_category_mix = (
        focus_latest.groupby("crime_category", as_index=False)["cases_reported"]
        .sum()
        .sort_values("cases_reported", ascending=False)
    )
    fig_mix = px.pie(
        focus_category_mix,
        names="crime_category",
        values="cases_reported",
        hole=0.56,
        color_discrete_sequence=["#ff5f5f", "#ffbd59", "#88d9ff", "#8ddf9b", "#d891ff"],
    )
    fig_mix.update_layout(template=PLOTLY_TEMPLATE, height=360, title=f"{focus_state} Category Share ({focus_latest_year})")
    st.plotly_chart(fig_mix, use_container_width=True)

with col6:
    city_watchlist = (
        focus_city_latest[
            ["city", "cases_reported", "crime_rate_per_100k", "detection_rate", "severity_index"]
        ]
        .sort_values(["severity_index", "crime_rate_per_100k"], ascending=[False, False])
        .rename(
            columns={
                "city": "City",
                "cases_reported": "Cases",
                "crime_rate_per_100k": "Rate / 100k",
                "detection_rate": "Detection %",
                "severity_index": "Severity",
            }
        )
        .head(6)
    )
    st.markdown("#### City Watchlist")
    st.dataframe(city_watchlist, use_container_width=True, hide_index=True)

st.markdown('<div class="section-tag">Latest National Evidence</div>', unsafe_allow_html=True)
display_df = (
    latest_slice[
        [
            "state",
            "crime_category",
            "year",
            "cases_reported",
            "crime_rate_per_100k",
            "solved_cases",
            "charge_sheet_rate",
            "severity_index",
            "yoy_change_pct",
        ]
    ]
    .sort_values(["severity_index", "cases_reported"], ascending=[False, False])
    .rename(
        columns={
            "state": "State",
            "crime_category": "Category",
            "year": "Year",
            "cases_reported": "Cases",
            "crime_rate_per_100k": "Rate / 100k",
            "solved_cases": "Solved Cases",
            "charge_sheet_rate": "Charge-sheet %",
            "severity_index": "Severity",
            "yoy_change_pct": "YoY %",
        }
    )
)
st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption(
    "Made by [Bhoomika S](https://github.com/Bhoomika-404Error)."
)
