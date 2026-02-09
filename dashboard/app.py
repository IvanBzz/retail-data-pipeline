import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ритейл Аналитика",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — dark, data-dense, clean ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #0a0d14;
    color: #e2e8f0;
}
.stApp { background: #0a0d14; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 60% 40%, rgba(99,102,241,.12) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0 0 .4rem;
    letter-spacing: -1px;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
}
.hero-tag {
    display: inline-block;
    background: rgba(99,102,241,.15);
    border: 1px solid rgba(99,102,241,.35);
    color: #a5b4fc;
    font-family: 'Space Mono', monospace;
    font-size: .7rem;
    padding: .2rem .65rem;
    border-radius: 20px;
    margin-top: .8rem;
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.kpi-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.kpi-card:hover { border-color: #4f46e5; }
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: var(--accent, #6366f1);
    border-radius: 12px 0 0 12px;
}
.kpi-label {
    font-size: .72rem;
    font-weight: 500;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-bottom: .5rem;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.75rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
}
.kpi-delta {
    font-size: .78rem;
    color: #10b981;
    margin-top: .4rem;
}

/* ── Section headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: .6rem;
    margin-bottom: 1rem;
}
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -.5px;
}
.section-badge {
    background: rgba(99,102,241,.12);
    border: 1px solid rgba(99,102,241,.25);
    color: #818cf8;
    font-size: .65rem;
    font-family: 'Space Mono', monospace;
    padding: .15rem .5rem;
    border-radius: 4px;
}

/* ── Chart containers ── */
.chart-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #334155 30%, #4f46e5 50%, #334155 70%, transparent);
    margin: 2rem 0;
}

/* ── Streamlit metric override ── */
[data-testid="stMetric"] {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    border-radius: 12px !important;
    padding: 1.2rem 1.5rem !important;
}
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: .78rem !important; }
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-family: 'Space Mono', monospace !important; }
</style>
""", unsafe_allow_html=True)

# ── Plotly dark theme shared config ───────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#94a3b8", size=12),
    margin=dict(t=20, b=40, l=10, r=10),
    legend=dict(
        bgcolor="rgba(17,24,39,.8)",
        bordercolor="#1e293b",
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="#1e293b",
        linecolor="#334155",
        tickfont=dict(size=11),
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="#1e293b",
        linecolor="#334155",
        tickfont=dict(size=11),
        zeroline=False,
    ),
)
ACCENT_PALETTE = ["#6366f1","#06b6d4","#10b981","#f59e0b","#f43f5e","#a78bfa","#34d399"]

def format_date_ru(date_str):
    if not date_str or not isinstance(date_str, str) or "-" not in date_str:
        return date_str
    months = {
        "01": "Янв", "02": "Фев", "03": "Мар", "04": "Апр",
        "05": "Май", "06": "Июн", "07": "Июл", "08": "Авг",
        "09": "Сен", "10": "Окт", "11": "Ноя", "12": "Дек"
    }
    try:
        y, m = date_str.split("-")
        return f"{months.get(m, m)} {y}"
    except:
        return date_str

def format_kpi(value, is_money=False):
    if value >= 1_000_000:
        res = f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        res = f"{value / 1_000:.1f}K"
    else:
        res = f"{value:,.0f}" if value % 1 == 0 else f"{value:,.1f}"
    return f"${res}" if is_money else res

# ── Data loading ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    base_path = os.path.join(project_root, "data", "marts")

    try:
        retention_df = pd.read_parquet(os.path.join(base_path, "cohort_retention.parquet"))
        rfm_df       = pd.read_parquet(os.path.join(base_path, "rfm_segments.parquet"))
        
        # ГАРАНТИРУЕМ НИЖНИЙ РЕГИСТР ДЛЯ ВСЕХ КОЛОНОК
        retention_df.columns = [c.lower() for c in retention_df.columns]
        rfm_df.columns       = [c.lower() for c in rfm_df.columns]
        
        retention_df["cohort_month"] = pd.to_datetime(
            retention_df["cohort_month"]
        ).dt.strftime("%Y-%m")
        return retention_df, rfm_df
    except FileNotFoundError:
        return None, None

retention_df, rfm_df = load_data()

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">📊 Платформа Ритейл Аналитики</div>
  <p class="hero-sub">Продуктовая аналитика · Когортное удержание · RFM-сегментация</p>
  <span class="hero-tag">ЖИВЫЕ ДАННЫЕ</span>
</div>
""", unsafe_allow_html=True)

# ── No data fallback ───────────────────────────────────────────────────────────
if retention_df is None or rfm_df is None:
    st.error("⚠️ Данные не найдены. Сначала запустите `python etl/build_dwh.py`.")
    st.stop()

# ── Sidebar Filters ────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<style>
/* Возвращаем темный фон сайдбара */
[data-testid="stSidebar"] {
    background-color: #0a0d14;
}
/* Жесткий фикс для тегов мультиселекта (кнопочки стран) */
span[data-baseweb="tag"] {
    background-color: #6366f1 !important;
}
div[data-testid="stMultiSelectTag"] {
    background-color: #6366f1 !important;
    border-radius: 4px !important;
}
div[data-testid="stMultiSelectTag"] span {
    color: white !important;
}
/* Цвет иконки закрытия (крестика) */
div[data-testid="stMultiSelectTag"] svg {
    fill: white !important;
}
</style>
""", unsafe_allow_html=True)
st.sidebar.title("🔍 Фильтры")

# Get unique countries from both dataframes to be safe
rfm_countries = set(rfm_df["country"].unique()) if "country" in rfm_df.columns else set()
ret_countries = set(retention_df["country"].unique()) if "country" in retention_df.columns else set()
all_countries = sorted(list(rfm_countries | ret_countries))

selected_countries = st.sidebar.multiselect("Выберите страны", all_countries, default=all_countries)

# ── Country Filtering ──────────────────────────────────────────────────────────
if all_countries and not selected_countries:
    st.warning("⚠️ Выберите хотя бы одну страну")
    st.stop()

if selected_countries:
    if "country" in rfm_df.columns:
        rfm_df = rfm_df[rfm_df["country"].isin(selected_countries)]
    if "country" in retention_df.columns:
        retention_df = retention_df[retention_df["country"].isin(selected_countries)]

if rfm_df.empty or (retention_df is not None and retention_df.empty):
    st.warning("⚠️ Нет данных для выбранных параметров")
    st.stop()

# ── Data processing ────────────────────────────────────────────────────────────
# Aggregate by cohort_month and month_index to handle multiple countries/duplicates
# This ensures correct totals when multiple countries are selected
group_cols = ["cohort_month", "month_index"]
if "activity_month" in retention_df.columns:
    group_cols.append("activity_month")

retention_df = (
    retention_df.groupby(group_cols, as_index=False)
    .agg({"active_users": "sum", "total_revenue": "sum"})
)

# Ensure data is sorted for cumsum and first month calculation
retention_df = retention_df.sort_values(["cohort_month", "month_index"])

# Calculate cumulative revenue
retention_df["cumulative_revenue"] = (
    retention_df.groupby("cohort_month")["total_revenue"]
    .cumsum()
)

# Calculate retention rate robustly
# 1. Get cohort size (active users at month_index == 0)
agg_cohorts = retention_df[retention_df["month_index"] == 0].groupby("cohort_month", as_index=False).agg(
    cohort_size=("active_users", "sum")
)

# 2. Merge back and calculate rate, handling potential name conflicts and empty cohorts
if not agg_cohorts.empty:
    retention_df = retention_df.merge(agg_cohorts, on="cohort_month", how="left", suffixes=("", "_agg"))
    retention_df["retention_rate"] = (
        retention_df["active_users"] / retention_df["cohort_size"].replace(0, pd.NA)
    ).fillna(0)
else:
    retention_df["cohort_size"] = 0
    retention_df["retention_rate"] = 0.0

# ── RFM segmentation helper ────────────────────────────────────────────────────
def get_segment(row):
    r, f = row.get("r_score", 0), row.get("f_score", 0)
    if r >= 4 and f >= 4:  return "VIP-клиенты"
    if r <= 2 and f >= 4:  return "В зоне риска"
    if r >= 4 and f <= 2:  return "Новички"
    if r <= 2 and f <= 2:  return "Ушедшие"
    return "Стандартные"

if "r_score" in rfm_df.columns and "f_score" in rfm_df.columns:
    rfm_df["segment"] = rfm_df.apply(get_segment, axis=1)
else:
    rfm_df["segment"] = "Стандартные"

SEGMENT_COLORS = {
    "VIP-клиенты": "#6366f1",
    "В зоне риска": "#f59e0b",
    "Новички":      "#10b981",
    "Ушедшие":      "#f43f5e",
    "Стандартные":  "#64748b",
}

# ── KPI section ───────────────────────────────────────────────────────────────
# Use rfm_df['monetary'].sum() as the most reliable way to get total revenue
total_revenue   = rfm_df["monetary"].sum() if "monetary" in rfm_df.columns else 0
total_customers = rfm_df["customerid"].nunique() if "customerid" in rfm_df.columns else 0
avg_clv         = rfm_df["monetary"].mean() if "monetary" in rfm_df.columns else 0
avg_orders      = rfm_df["frequency"].mean() if "frequency" in rfm_df.columns else 0
champ_pct       = (rfm_df["segment"] == "VIP-клиенты").mean() * 100 if not rfm_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Общая выручка",           format_kpi(total_revenue, is_money=True))
col2.metric("Активные клиенты",        format_kpi(total_customers))
col3.metric("Средний LTV клиента",     format_kpi(avg_clv, is_money=True))
col4.metric("Среднее кол-во заказов",  format_kpi(avg_orders))
col5.metric("Доля VIP",                f"{champ_pct:.1f}%")

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — Retention heatmap + LTV curves
# ══════════════════════════════════════════════════════════════════════════════
col_a, col_b = st.columns([1.1, 1], gap="large")

with col_a:
    st.markdown("""
    <div class="section-header">
      <span class="section-title">🔥 Когортное удержание клиентов</span>
      <span class="section-badge">ТЕПЛОВАЯ КАРТА</span>
    </div>
    """, unsafe_allow_html=True)

    pivot = (
        retention_df
        .pivot(index="cohort_month", columns="month_index", values="retention_rate")
        .iloc[:, :13]   # cap at 12 months after cohort
    )

    fig_ret = go.Figure(go.Heatmap(
        z=pivot.values * 100,
        x=[f"M+{i}" for i in pivot.columns],
        y=[format_date_ru(d) for d in pivot.index.tolist()],
        colorscale=[
            [0.0,  "#0f172a"],
            [0.15, "#1e1b4b"],
            [0.35, "#3730a3"],
            [0.6,  "#6366f1"],
            [0.8,  "#818cf8"],
            [1.0,  "#c7d2fe"],
        ],
        text=[[f"{v:.1f}%" if not pd.isna(v) else "" for v in row]
              for row in pivot.values * 100],
        texttemplate="%{text}",
        textfont=dict(size=9, color="white"),
        hovertemplate="Когорта: %{y}<br>Месяц: %{x}<br>Удержание: %{z:.1f}%<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="Удержание %", font=dict(size=11)),
            tickfont=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
            tickcolor="#64748b",
        ),
    ))
    fig_ret.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
    )
    fig_ret.update_xaxes(title="Месяцев после первой покупки")
    fig_ret.update_yaxes(title="Когорта")
    st.plotly_chart(fig_ret, use_container_width=True, config={"displayModeBar": False})

with col_b:
    st.markdown("""
    <div class="section-header">
      <span class="section-title">💰 Накопленный LTV по когортам</span>
      <span class="section-badge">ТРЕНД</span>
    </div>
    """, unsafe_allow_html=True)

    recent_cohorts = sorted(retention_df["cohort_month"].unique())[-7:-1]
    ltv_data = retention_df[retention_df["cohort_month"].isin(recent_cohorts)]

    fig_ltv = go.Figure()
    for i, cohort in enumerate(sorted(ltv_data["cohort_month"].unique())):
        d = ltv_data[ltv_data["cohort_month"] == cohort].sort_values("month_index")
        color = ACCENT_PALETTE[i % len(ACCENT_PALETTE)]
        cohort_label = format_date_ru(cohort)
        fig_ltv.add_trace(go.Scatter(
            x=d["month_index"], y=d["cumulative_revenue"],
            mode="lines+markers",
            name=cohort_label,
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            hovertemplate=f"<b>{cohort_label}</b><br>Месяц: %{{x}}<br>LTV: $%{{y:,.0f}}<extra></extra>",
        ))

    fig_ltv.update_layout(
        **PLOTLY_LAYOUT,
        height=380,
    )
    fig_ltv.update_xaxes(title="Номер месяца", dtick=1)
    fig_ltv.update_yaxes(title="Накопленная выручка ($)", tickformat="$,.0f")
    st.plotly_chart(fig_ltv, use_container_width=True, config={"displayModeBar": False})

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — RFM segmentation
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <span class="section-title">🎯 RFM-сегментация клиентов</span>
  <span class="section-badge">ДАВНОСТЬ · ЧАСТОТА · ДЕНЬГИ</span>
</div>
""", unsafe_allow_html=True)

col_c, col_d, col_e = st.columns([0.9, 1.1, 0.9], gap="large")

with col_c:
    seg_counts = rfm_df["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]

    fig_pie = go.Figure(go.Pie(
        labels=seg_counts["segment"],
        values=seg_counts["count"],
        hole=0.55,
        marker=dict(
            colors=[SEGMENT_COLORS.get(s, "#64748b") for s in seg_counts["segment"]],
            line=dict(color="#0a0d14", width=2),
        ),
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>%{value:,} клиентов (%{percent})<extra></extra>",
    ))
    fig_pie.add_annotation(
        text=f"<b>{total_customers:,}</b><br><span style='font-size:10px'>клиентов</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=15, color="#f1f5f9"),
        align="center",
    )
    fig_pie.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        showlegend=True,
    )
    fig_pie.update_layout(legend=dict(orientation="v", x=1, y=0.5))
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

with col_d:
    fig_scatter = go.Figure()
    # Check if necessary columns exist for the scatter plot
    required_cols = {"recency", "monetary", "frequency"}
    if required_cols.issubset(rfm_df.columns):
        for seg, color in SEGMENT_COLORS.items():
            d = rfm_df[rfm_df["segment"] == seg]
            if d.empty:
                continue
            fig_scatter.add_trace(go.Scatter(
                x=d["recency"],
                y=d["monetary"],
                mode="markers",
                name=seg,
                marker=dict(
                    size=d["frequency"].clip(upper=30) * 1.5 + 3,
                    color=color,
                    opacity=0.7,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    f"<b>{seg}</b><br>"
                    "Давность: %{x} дн.<br>Выручка: $%{y:,.0f}<extra></extra>"
                ),
            ))
    else:
        st.info("💡 Недостаточно данных для построения точечного графика (Recency/Monetary/Frequency)")

    fig_scatter.update_layout(
        **PLOTLY_LAYOUT,
        height=320,
        showlegend=False,
    )
    fig_scatter.update_xaxes(title="Давность (дней с последней покупки)")
    fig_scatter.update_yaxes(title="Выручка ($, лог. шкала)", type="log",
                             tickformat="$,.0f")
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

with col_e:
    # Segment summary table
    # Check if necessary columns exist for the summary table
    table_cols = {"customerid", "monetary", "recency"}
    if table_cols.issubset(rfm_df.columns):
        seg_stats = (
            rfm_df.groupby("segment")
            .agg(
                customers  =("customerid", "count"),
                avg_revenue=("monetary",   "mean"),
                avg_recency=("recency",    "mean"),
            )
            .round(0)
            .reset_index()
            .sort_values("avg_revenue", ascending=False)
        )

        # Render as Streamlit dataframe for better robustness and theme integration
        st.dataframe(
            seg_stats,
            column_config={
                "segment": "Сегмент",
                "customers": st.column_config.NumberColumn(
                    "Клиентов",
                    help="Количество клиентов в сегменте",
                    format="%d",
                ),
                "avg_revenue": st.column_config.NumberColumn(
                    "Ср. LTV",
                    help="Средняя выручка на одного клиента",
                    format="$%d",
                ),
                "avg_recency": st.column_config.NumberColumn(
                    "Давность",
                    help="Среднее количество дней с последней покупки",
                    format="%d дн.",
                ),
            },
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("💡 Недостаточно данных для сводной таблицы сегментов")

st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — Monthly Revenue trend
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <span class="section-title">📈 Динамика выручки по месяцам</span>
  <span class="section-badge">ВСЕ КОГОРТЫ</span>
</div>
""", unsafe_allow_html=True)

if "activity_month" in retention_df.columns and "total_revenue" in retention_df.columns:
    monthly = (
        retention_df
        .groupby("activity_month")["total_revenue"]
        .sum()
        .reset_index()
        .sort_values("activity_month")
    )
    monthly["activity_month_str"] = pd.to_datetime(
        monthly["activity_month"]
    ).dt.strftime("%Y-%m")
    monthly["activity_month_ru"] = monthly["activity_month_str"].apply(format_date_ru)

    fig_rev = go.Figure()
    fig_rev.add_trace(go.Scatter(
        x=monthly["activity_month_ru"],
        y=monthly["total_revenue"],
        fill="tozeroy",
        fillcolor="rgba(99,102,241,.12)",
        line=dict(color="#6366f1", width=2.5),
        mode="lines",
        hovertemplate="Месяц: %{x}<br>Выручка: $%{y:,.0f}<extra></extra>",
    ))
    fig_rev.update_layout(
        **PLOTLY_LAYOUT,
        height=240,
    )
    fig_rev.update_xaxes(title="")
    fig_rev.update_yaxes(title="Выручка ($)", tickformat="$,.0f")
    st.plotly_chart(fig_rev, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("💡 Недостаточно данных для построения графика динамики выручки")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.5rem 0 0;color:#334155;
            font-family:'Space Mono',monospace;font-size:.7rem;letter-spacing:.05em">
  ПЛАТФОРМА РИТЕЙЛ АНАЛИТИКИ · DUCKDB + STREAMLIT
</div>
""", unsafe_allow_html=True)
