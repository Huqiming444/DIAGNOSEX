# -*- coding: utf-8 -*-
"""
DIAGNOSEX · 中药企业财务健康度诊断工具

基准数据：68 家申万中药Ⅱ上市公司 2023—2025 年公开年报（204 条真实记录）
数据文件：与本项目同目录的「中药上市公司2023-2025年报财务数据.csv」

运行：streamlit run DIAGNOSEX.py
"""
from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ---------------------------------------------------------------------------
# 基础配置
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "中药上市公司2023-2025年报财务数据.csv"

BRAND = "DIAGNOSEX"
BRAND_SUB = "中药企业财务健康度诊断"

st.set_page_config(
    page_title="DIAGNOSEX · 中药企业财务健康度诊断",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# 设计系统 · iOS 浅色科技风（Frosted Console）
# 1 CSS视觉：毛玻璃 / 柔阴影 / 渐变网格 / 颗粒纹理 / 细边框 / 分层布局
# 2 交互动效：微交互 / 滚动渐入 / 弹性动画 / 平滑过渡 / 控件状态反馈
# 3 3D氛围：漂浮几何体 / 粒子场 / 视差背景（弱化处理，不抢焦点）
# 4 组件系统：统一规范 / 完整控件状态 / 数据看板布局
# ---------------------------------------------------------------------------
APPLE_FONT = ('-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", '
              '"Inter", "Helvetica Neue", "Segoe UI", "PingFang SC", "Hiragino Sans GB", '
              '"Microsoft YaHei", sans-serif')
FONT = APPLE_FONT
MONO = ('"SF Mono", ui-monospace, "JetBrains Mono", "Roboto Mono", Menlo, Consolas, monospace')

# iOS 系统色板
INK = "#1d1d1f"
SUB = "#6e6e73"
MUTE = "#8e8e93"
LINE = "rgba(60,60,67,0.14)"
HAIR = "rgba(60,60,67,0.09)"
BLUE = "#0071e3"
CYAN = "#32ade6"
VIOLET = "#af52de"
SURFACE = "#ffffff"
CANVAS = "#f5f5f7"
PEWTER = "#fafafa"
GOOD = "#248a3d"
OK = "#b3860b"
WARN = "#e06c00"
BAD = "#d70015"
APPLE_PALETTE = ["#0a84ff", "#5ac8fa", "#34c759", "#ff9500",
                 "#ff3b30", "#5856d6", "#af52de", "#8e8e93"]


def _register_plotly_theme():
    tpl = go.layout.Template()
    tpl.layout = go.Layout(
        font=dict(family=APPLE_FONT, size=13, color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=APPLE_PALETTE,
        title=dict(font=dict(size=15, color=INK, family=APPLE_FONT), x=0.015, xanchor="left"),
        hoverlabel=dict(font_family=APPLE_FONT, font_size=12, bgcolor="rgba(255,255,255,0.96)",
                        bordercolor="rgba(60,60,67,0.12)",
                        font_color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1,
                    font=dict(size=12, color=SUB), bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=44, r=28, t=52, b=42),
        xaxis=dict(showgrid=False, zeroline=False, ticks="",
                   linecolor="rgba(60,60,67,0.16)", tickfont=dict(size=11, color=SUB),
                   title=dict(font=dict(size=12, color=SUB))),
        yaxis=dict(showgrid=True, gridcolor="rgba(60,60,67,0.07)", zeroline=False,
                   ticks="", tickfont=dict(size=11, color=SUB),
                   title=dict(font=dict(size=12, color=SUB))),
    )
    pio.templates["apple"] = tpl
    pio.templates.default = "apple"


_register_plotly_theme()
PX_TEMPLATE = "apple"

# ---------------------------------------------------------------------------
# 背景舞台：漂浮几何体 + 粒子场（fixed 定位，pointer-events 关闭，永不抢焦点）
# ---------------------------------------------------------------------------

DX_STAGE_HTML = ""

APPLE_CSS = """
<style>
:root{
  --ink:#0b0b0c;
  --sub:#6b6b74;
  --mute:#9ca3af;
  --line:#e5e5e7;
  --hair:rgba(0,0,0,0.06);
  --hair-strong:rgba(0,0,0,0.10);
  --blue:#0a84ff;
  --blue-dark:#0071e3;
  --surface:#ffffff;
  --canvas:#f7f7f8;
  --panel:#fafafa;
  --r:12px;
  --r-sm:8px;
  --ease:cubic-bezier(.22,.1,.1,1);
}

/* === 1. 画布：克制、高级、不抢焦点 === */
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"]{
  background-color: var(--canvas) !important;
  color: var(--ink);
}
[data-testid="stAppViewContainer"]{
  background-image:
    radial-gradient(900px 500px at 6% -4%, rgba(10,132,255,0.055), transparent 55%);
  background-attachment: fixed;
}
[data-testid="stAppViewContainer"]::before{
  content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:0.35;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/></filter><rect width='200' height='200' filter='url(%23n)' opacity='0.25'/></svg>");
  background-size:180px 180px;
}

/* === 2. 版式与容器 === */
body, .main, [data-testid="stMain"], p, div, span, label, li{
  font-family: FONTSTACK;
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
}
.main .block-container, [data-testid="stMain"] .block-container{
  max-width: 1200px; padding: 1.4rem 2.2rem 5rem; margin: 0 auto; position: relative; z-index: 2;
}
[data-testid="stHorizontalBlock"]{ gap: 18px; }
h1,h2,h3{ color: var(--ink) !important; font-weight: 600 !important; letter-spacing: -0.022em !important; }
h1{ font-size: 32px !important; line-height: 1.18 !important; }
h2{ font-size: 22px !important; line-height: 1.28 !important; }
h3{ font-size: 17px !important; line-height: 1.32 !important; }
h4{ font-size: 15px !important; font-weight: 600 !important; color: var(--ink) !important; letter-spacing: -0.01em !important; }
[data-testid="stCaptionContainer"] p, .stCaption{ color: var(--sub) !important; font-size: 13px !important; }
.stMarkdown p{ line-height: 1.62; color: var(--ink); }

/* === 3. 顶栏 / 侧栏 === */
[data-testid="stHeader"]{ display: none !important; }
[data-testid="stToolbar"]{ display: none !important; }
footer{ visibility: hidden; }
[data-testid="stSidebar"]{
  background: var(--panel) !important;
  border-right: 1px solid var(--hair);
}
[data-testid="stSidebar"] .block-container{ padding-top: 1.6rem; }
[data-testid="stSidebar"] h1{ font-size: 18px !important; letter-spacing: -0.02em; }
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{
  font-size: 11px !important; color: var(--mute) !important; font-weight: 600 !important;
  letter-spacing: 0.08em !important; text-transform: uppercase;
}

/* === 4. 页签：干净的下划线 === */
.stTabs [data-baseweb="tab-list"]{
  gap: 32px; background: transparent; border-bottom: 1px solid var(--hair); margin-bottom: 28px;
}
button[data-baseweb="tab"]{
  padding: 12px 2px 15px !important; font-size: 15px !important; font-weight: 500 !important;
  color: var(--sub) !important; background: transparent !important; border: none !important;
  transition: color .2s var(--ease);
}
button[data-baseweb="tab"]:hover{ color: var(--ink) !important; }
button[data-baseweb="tab"][aria-selected="true"]{ color: var(--ink) !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab-highlight"]{
  background: var(--blue) !important; height: 2px !important; border-radius: 0;
}

/* === 5. 指标卡：白底 + 发丝边框，克制阴影 === */
[data-testid="stMetric"]{
  background: var(--surface);
  border: 1px solid var(--hair);
  border-radius: var(--r);
  padding: 16px 18px 14px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: transform .25s var(--ease), box-shadow .25s var(--ease), border-color .25s var(--ease);
}
[data-testid="stMetric"]:hover{
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -10px rgba(0,0,0,0.10);
  border-color: var(--hair-strong);
}
[data-testid="stMetricLabel"]{ font-size: 12px !important; color: var(--sub) !important; font-weight: 500 !important; letter-spacing: 0.01em; }
[data-testid="stMetricValue"]{
  font-size: 26px !important; font-weight: 600 !important; letter-spacing: -0.02em !important;
  font-variant-numeric: tabular-nums; color: var(--ink) !important;
}
[data-testid="stMetricDelta"]{ font-size: 12px !important; }

/* === 6. 图表 / 表格 / 折叠卡片 === */
.js-plotly-plot, .plotly-graph-div{
  background: var(--surface);
  border: 1px solid var(--hair);
  border-radius: var(--r);
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: box-shadow .25s var(--ease);
}
.js-plotly-plot:hover{ box-shadow: 0 10px 28px -14px rgba(0,0,0,0.10); }

[data-testid="stDataFrame"], [data-testid="stDataFrameResizable"], [data-testid="stTable"]{
  border: 1px solid var(--hair); border-radius: var(--r); overflow: hidden;
  background: var(--surface);
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
[data-testid="stDataFrame"] th{ background: rgba(0,0,0,0.02) !important; font-weight: 600 !important; }
[data-testid="stProgress"] > div > div{ background: var(--blue) !important; border-radius: 980px !important; }

[data-testid="stExpander"]{
  background: var(--surface) !important;
  border: 1px solid var(--hair) !important; border-radius: var(--r) !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important; overflow: hidden;
}
[data-testid="stAlert"]{
  border: 1px solid var(--hair) !important; border-radius: var(--r) !important;
  background: rgba(0,0,0,0.03) !important; color: var(--ink) !important;
  box-shadow: none !important;
}
hr, .stMarkdown hr{ border: none !important; border-top: 1px solid var(--hair) !important; margin: 28px 0 !important; }

/* === 7. 控件系统 === */
[data-baseweb="input"] > div, [data-baseweb="select"] > div, [data-baseweb="textarea"] > div{
  border-radius: var(--r-sm) !important; border-color: var(--line) !important;
  background: var(--surface) !important; box-shadow: none !important;
  transition: border-color .18s var(--ease), box-shadow .18s var(--ease);
}
[data-baseweb="input"] > div:focus-within, [data-baseweb="select"] > div:focus-within,
[data-baseweb="textarea"] > div:focus-within{
  border-color: var(--blue) !important; box-shadow: 0 0 0 3px rgba(10,132,255,0.12) !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea{ color: var(--ink) !important; font-variant-numeric: tabular-nums; }

div[role="radiogroup"]{
  display: inline-flex !important; gap: 2px !important; padding: 3px !important;
  border-radius: var(--r-sm) !important;
  background: rgba(0,0,0,0.04) !important; border: 1px solid var(--hair) !important;
}
div[data-testid="stRadio"] label, div[role="radiogroup"] label{
  font-size: 13px !important; font-weight: 500 !important; color: var(--sub) !important;
  padding: 6px 14px !important; border-radius: 6px !important; margin: 0 !important;
  transition: color .2s var(--ease), background .2s var(--ease);
}
div[data-testid="stRadio"] label:hover, div[role="radiogroup"] label:hover{ color: var(--ink) !important; }
div[data-testid="stRadio"] input:checked + div, div[role="radiogroup"] input:checked + div,
div[data-testid="stRadio"] input:checked ~ div, div[role="radiogroup"] input:checked ~ div,
div[data-testid="stRadio"] input:checked ~ span, div[role="radiogroup"] input:checked ~ span{
  background: var(--surface) !important; color: var(--blue) !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.08) !important; border-radius: 6px !important;
}
div[data-testid="stRadio"] input, div[role="radiogroup"] input{ accent-color: var(--blue) !important; }

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button{
  border-radius: var(--r-sm) !important; border: none !important;
  background: var(--blue) !important; color: #fff !important;
  font-size: 14px !important; font-weight: 500 !important; padding: 9px 18px !important;
  box-shadow: none !important;
  transition: transform .15s var(--ease), filter .15s var(--ease), box-shadow .15s var(--ease);
}
.stButton > button:hover, .stDownloadButton > button:hover{
  filter: brightness(1.05);
  transform: translateY(-1px);
  box-shadow: 0 6px 18px -8px rgba(10,132,255,0.45) !important;
}
.stButton > button:active, .stDownloadButton > button:active{ transform: scale(0.98); }

[data-baseweb="slider"] div[role="slider"]{
  background: var(--surface) !important; border: 2px solid var(--blue) !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}

/* === 8. 微动效：只保留淡入，更克制 === */
@keyframes dx-rise{ from{ opacity:0; transform: translateY(10px); } to{ opacity:1; transform: none; } }
[data-testid="stMetric"], .js-plotly-plot, [data-testid="stDataFrame"],
[data-testid="stTable"], [data-testid="stExpander"], .stMarkdown{ animation: dx-rise .4s var(--ease); }
@media (prefers-reduced-motion: reduce){
  [data-testid="stMetric"], .js-plotly-plot, .stMarkdown{ animation: none !important; }
}

/* === 9. 滚动条 === */
::-webkit-scrollbar{ width: 9px; height: 9px; }
::-webkit-scrollbar-track{ background: transparent; }
::-webkit-scrollbar-thumb{
  background: rgba(0,0,0,0.18); border-radius: 10px; border: 3px solid transparent;
  background-clip: content-box;
}
::-webkit-scrollbar-thumb:hover{ background: rgba(0,0,0,0.30); background-clip: content-box; }

/* === 10. 业务组件 === */
.ap-hero{ padding: 2px 0 28px; }
.ap-eyebrow{
  font-size: 11px; letter-spacing: 0.12em; font-weight: 600;
  color: var(--blue); text-transform: uppercase; margin: 0 0 10px;
}
.ap-title{
  font-size: 42px; line-height: 1.10; font-weight: 600; letter-spacing: -0.028em;
  color: var(--ink); margin: 0 0 12px;
}
.ap-sub{ font-size: 17px; line-height: 1.55; color: var(--sub); margin: 0; max-width: 720px; font-weight: 400; }
.ap-rule{
  height: 1px; margin: 0 0 30px; background: var(--hair);
}
.ap-section-wrap{ margin: 2px 0 22px; }
.ap-section{
  font-size: 24px; font-weight: 600; letter-spacing: -0.018em; color: var(--ink);
  margin: 0 0 6px; line-height: 1.24;
}
.ap-lead{ font-size: 14px; color: var(--sub); margin: 0; line-height: 1.6; max-width: 780px; }
.ap-card{
  background: var(--surface);
  border: 1px solid var(--hair);
  border-radius: var(--r);
  padding: 18px 20px; margin: 0 0 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  transition: transform .25s var(--ease), box-shadow .25s var(--ease), border-color .25s var(--ease);
}
.ap-card:hover{ transform: translateY(-2px); box-shadow: 0 10px 28px -14px rgba(0,0,0,0.10); border-color: var(--hair-strong); }
.ap-kpi{ font-size: 12px; color: var(--sub); margin: 0 0 6px; font-weight: 500; letter-spacing: 0.01em; }
.ap-note{ font-size: 13px; color: var(--sub); line-height: 1.6; margin: 8px 0 0; }
.dx-badge{
  display: inline-block; padding: 4px 12px; border-radius: 980px;
  font-size: 13px; font-weight: 600; color: #fff; vertical-align: middle;
}
</style>
"""


def inject_apple_style():
    st.markdown(APPLE_CSS.replace("FONTSTACK", APPLE_FONT), unsafe_allow_html=True)
def section(title: str, lead: str | None = None, eyebrow: str | None = None):
    html = '<div class="ap-section-wrap">'
    if eyebrow:
        html += f'<div class="ap-eyebrow">{eyebrow}</div>'
    html += f'<div class="ap-section">{title}</div>'
    if lead:
        html += f'<p class="ap-lead">{lead}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)



def _width_kw() -> dict:
    try:
        ver = tuple(int(x) for x in st.__version__.split(".")[:2])
    except Exception:  # noqa: BLE001
        ver = (1, 30)
    return {"width": "stretch"} if ver >= (1, 50) else {"use_container_width": True}


WIDTH_KW = _width_kw()
PLOT_KW = dict(WIDTH_KW)
try:
    if int(st.__version__.split(".")[0]) >= 1 and int(st.__version__.split(".")[1]) >= 32:
        PLOT_KW["theme"] = None
except Exception:  # noqa: BLE001
    pass

# ---------------------------------------------------------------------------
# 指标与模型定义
# ---------------------------------------------------------------------------
DIMS = ["盈利", "成长", "偿债", "营运", "现金流", "研发"]

METRICS = [
    dict(key="毛利率(%)", name="毛利率", dim="盈利", dir=1, unit="%", fmt=2),
    dict(key="净利率(%)", name="净利率", dim="盈利", dir=1, unit="%", fmt=2),
    dict(key="ROE(%)", name="净资产收益率 ROE", dim="盈利", dir=1, unit="%", fmt=2),
    dict(key="营收同比(%)", name="营收增速", dim="成长", dir=1, unit="%", fmt=2),
    dict(key="净利同比(%)", name="净利增速", dim="成长", dir=1, unit="%", fmt=2),
    dict(key="资产负债率(%)", name="资产负债率", dim="偿债", dir=-1, unit="%", fmt=2),
    dict(key="总资产周转率", name="总资产周转率", dim="营运", dir=1, unit="次", fmt=2),
    dict(key="经营现金流/营收(%)", name="经营现金流利润率", dim="现金流", dir=1, unit="%", fmt=2),
    dict(key="净利现金含量", name="净利现金含量", dim="现金流", dir=1, unit="倍", fmt=2),
    dict(key="研发费用率(%)", name="研发费用率", dim="研发", dir=1, unit="%", fmt=2),
]
METRIC_BY_KEY = {m["key"]: m for m in METRICS}

QS = [0.10, 0.25, 0.50, 0.75, 0.90]
Q_LABEL = {0.10: "P10", 0.25: "P25", 0.50: "P50", 0.75: "P75", 0.90: "P90"}

WEIGHT_MODES = {
    "上市公司口径": {"盈利": 20, "成长": 15, "偿债": 20, "营运": 15, "现金流": 20, "研发": 10},
    "中小企业口径（推荐）": {"盈利": 24, "成长": 12, "偿债": 28, "营运": 14, "现金流": 18, "研发": 4},
}
WEIGHT_NOTE = {
    "上市公司口径": "沿用通用财务分析权重，六维度均衡，适合上市公司之间的横向比较。",
    "中小企业口径（推荐）": "调高偿债与现金流权重：中小企业融资渠道有限，短期偿付与现金回款是首要风险。",
}

LEVELS = [("优秀", 70, "#166534"), ("良好", 60, "#16a34a"), ("一般", 50, "#b45309"),
          ("关注", 40, "#ea580c"), ("风险", 0, "#dc2626")]

GROUPS = ["全行业", "中小型上市公司（营收 ≤ 中位）", "头部前 25%（营收 ≥ P75）"]

JUDGES = [("优秀", 75, GOOD), ("达标", 50, OK), ("偏弱", 25, WARN), ("危险", 0, BAD)]


def level_of(score: float) -> str:
    for name, th, _ in LEVELS:
        if score >= th:
            return name
    return "风险"


def level_color(level: str) -> str:
    for name, _, color in LEVELS:
        if name == level:
            return color
    return SUB


def judge_of(score: float):
    for name, th, color in JUDGES:
        if score >= th:
            return name, color
    return "危险", BAD


# ---------------------------------------------------------------------------
# 数据加载
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, dtype={"代码": str})
    df["代码"] = df["代码"].str.zfill(6)
    df["年份"] = df["年份"].astype(int)
    # 派生指标
    df["总资产周转率"] = np.where(df["总资产(亿元)"] > 0,
                                  df["营业收入(亿元)"] / df["总资产(亿元)"], np.nan)
    df["经营现金流/营收(%)"] = np.where(df["营业收入(亿元)"] > 0,
                                        df["经营现金流净额(亿元)"] / df["营业收入(亿元)"] * 100, np.nan)
    # 净利现金含量：仅在净利润为正时有意义
    df["净利现金含量"] = np.where(df["归母净利润(亿元)"] > 0,
                                  df["经营现金流净额(亿元)"] / df["归母净利润(亿元)"], np.nan)
    return df.sort_values(["代码", "年份"]).reset_index(drop=True)


def group_frame(df_year: pd.DataFrame, group: str) -> pd.DataFrame:
    if group == GROUPS[1]:
        rev = df_year["营业收入(亿元)"]
        return df_year[rev <= rev.median()]
    if group == GROUPS[2]:
        rev = df_year["营业收入(亿元)"]
        return df_year[rev >= rev.quantile(0.75)]
    return df_year


@st.cache_data(show_spinner=False)
def build_benchmark(year: int, group: str) -> dict:
    """计算某年某对标组下各指标的分位点。"""
    df = load_data()
    g = group_frame(df[df["年份"] == year], group)
    bench = {}
    for m in METRICS:
        s = pd.to_numeric(g[m["key"]], errors="coerce").dropna()
        bench[m["key"]] = {q: float(s.quantile(q)) for q in QS}
    return bench


def score_value(v, qmap: dict, direction: int):
    """分位插值打分：50 分≈中位，75 分≈良好(P75)，90 分≈优秀(P90)。"""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    xs = [qmap[q] for q in QS]
    xs = list(np.maximum.accumulate(np.array(xs, dtype=float)))
    ys = np.array([10, 25, 50, 75, 90], dtype=float) if direction == 1 else \
        np.array([90, 75, 50, 25, 10], dtype=float)
    low, high = (5.0, 95.0) if direction == 1 else (95.0, 5.0)
    v = float(v)
    if v <= xs[0]:
        return low
    if v >= xs[-1]:
        return high
    return float(np.interp(v, xs, ys))


def score_metrics(values: dict, bench: dict, weights: dict):
    """对一组指标值打分：返回 (综合分, 维度分, 指标明细)。"""
    detail = []
    for m in METRICS:
        v = values.get(m["key"], None)
        qmap = bench.get(m["key"], {})
        sc = score_value(v, qmap, m["dir"]) if qmap else None
        detail.append(dict(
            指标=m["name"], 维度=m["dim"], 单位=m["unit"], 方向=m["dir"],
            数值=(None if v is None or (isinstance(v, float) and np.isnan(v)) else float(v)),
            得分=(None if sc is None else round(sc, 1)),
            分位基准={k: (None if v is None else round(v, 2)) for k, v in qmap.items()},
        ))
    dim_scores = {}
    for dim in DIMS:
        ds = [d["得分"] for d in detail if d["维度"] == dim and d["得分"] is not None]
        dim_scores[dim] = round(float(np.mean(ds)), 1) if ds else None
    num = den = 0.0
    for dim in DIMS:
        if dim_scores[dim] is not None:
            w = weights.get(dim, 0)
            num += dim_scores[dim] * w
            den += w
    total = round(num / den, 1) if den else None
    return total, dim_scores, detail


@st.cache_data(show_spinner=False)
def score_universe(year: int, group: str, mode: str) -> pd.DataFrame:
    """对基准组内所有上市公司打分。"""
    df = load_data()
    bench = build_benchmark(year, group)
    w = WEIGHT_MODES[mode]
    g = group_frame(df[df["年份"] == year], group).copy()
    rows = []
    for _, r in g.iterrows():
        vals = {m["key"]: r.get(m["key"], np.nan) for m in METRICS}
        total, dim_scores, _ = score_metrics(vals, bench, w)
        row = dict(代码=r["代码"], 名称=r["名称"],
                   营业收入=r["营业收入(亿元)"], 归母净利润=r["归母净利润(亿元)"],
                   毛利率=r["毛利率(%)"], ROE=r["ROE(%)"], 资产负债率=r["资产负债率(%)"],
                   综合分=total)
        row.update({d: dim_scores[d] for d in DIMS})
        rows.append(row)
    out = pd.DataFrame(rows)
    if not out.empty:
        out["评级"] = out["综合分"].apply(level_of)
        out = out.sort_values("综合分", ascending=False).reset_index(drop=True)
        out.insert(0, "排名", range(1, len(out) + 1))
    return out


# ---------------------------------------------------------------------------
# 图表 helpers
# ---------------------------------------------------------------------------
def radar_fig(dim_scores: dict, compare: dict | None = None, title: str = ""):
    cats = DIMS + [DIMS[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[dim_scores.get(d) or 0 for d in DIMS] + [dim_scores.get(DIMS[0]) or 0],
        theta=cats, name="本企业", line=dict(color=BLUE, width=2.5),
        fill="toself", fillcolor="rgba(0,113,227,0.14)"))
    if compare:
        for name, (vals, color) in compare.items():
            fig.add_trace(go.Scatterpolar(
                r=[vals.get(d) or 0 for d in DIMS] + [vals.get(DIMS[0]) or 0],
                theta=cats, name=name, line=dict(color=color, width=1.8, dash="dot")))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color=SUB),
                                   gridcolor="rgba(0,0,0,0.08)"),
                   bgcolor="rgba(0,0,0,0)"),
        showlegend=True, height=420, title=dict(text=title) if title else None,
        margin=dict(l=40, r=40, t=50 if title else 20, b=30))
    return fig


def rank_bar(df: pd.DataFrame, top: int = 15, ascending: bool = False):
    d = df.nsmallest(top, "综合分") if not ascending else df.nlargest(top, "综合分")
    d = d.sort_values("综合分", ascending=not ascending)
    fig = px.bar(d, x="综合分", y="名称", orientation="h",
                 text=d["综合分"].round(1), color_discrete_sequence=[BLUE],
                 template=PX_TEMPLATE, hover_data=["营业收入", "评级"])
    fig.update_traces(textposition="outside", textfont=dict(size=11, color=SUB),
                      marker_line_width=0)
    fig.update_layout(height=max(360, top * 30), showlegend=False,
                      xaxis_title="综合健康度得分", yaxis_title="",
                      margin=dict(l=130, r=40, t=48, b=30),
                      yaxis=dict(automargin=True, tickfont=dict(size=11)),
                      title=dict(pad=dict(t=10)))
    fig.update_xaxes(range=[0, 100])
    return fig


# ---------------------------------------------------------------------------
# 诊断：规则引擎与情景模拟
# ---------------------------------------------------------------------------
def advice_for(name: str, dim: str, value, p50, direction: int) -> str:
    if value is None:
        return f"{name} 未提供，已按缺失处理，不参与评分。"
    unit = METRIC_BY_KEY.get(name, {}).get("unit", "")
    if dim == "偿债":
        if value > 60:
            return (f"资产负债率 {value:.1f}% 显著高于行业中位 {p50:.1f}%，"
                    f"建议通过股权融资、利润留存或处置低效资产，先压降至 50% 以内。")
        if value > 45:
            return (f"资产负债率 {value:.1f}% 高于行业中位 {p50:.1f}%，"
                    f"建议控制新增有息负债，优先用经营现金流偿付短期借款。")
        return f"资产负债率 {value:.1f}% 处于行业合理区间，保持当前杠杆结构即可。"
    if dim == "现金流":
        if "利润率" in name:
            if value < 0:
                return (f"经营现金流为负（占营收 {value:.1f}%），是最高优先级问题："
                        f"建议压缩应收账期、清理滞销库存，先把经营现金流转正。")
            if value < p50:
                return (f"经营现金流利润率 {value:.1f}% 低于行业中位 {p50:.1f}%，"
                        f"建议加强回款管理与采购付款节奏安排。")
            return f"经营现金流利润率 {value:.1f}% 达到或超过行业中位，现金创造能力正常。"
        if value < 1:
            return (f"净利现金含量 {value:.2f} 倍低于 1，利润含金量不足，"
                    f"需核查应收账款与存货占用。")
        return f"净利现金含量 {value:.2f} 倍，利润有现金支撑，质量良好。"
    if dim == "盈利":
        if value < 0:
            return f"{name} 为负（{value:.1f}%），需先解决亏损：核查成本结构与费用率。"
        if value < p50:
            return f"{name} {value:.1f}% 低于行业中位 {p50:.1f}%，建议对标头部企业找差距。"
        return f"{name} {value:.1f}% 优于行业中位，保持即可。"
    if dim == "成长":
        if value < 0:
            return f"{name} 为负（{value:.1f}%），收入或利润下滑，需排查市场与产品结构。"
        if value < p50:
            return f"{name} {value:.1f}% 低于行业中位，建议明确增长来源（新品、渠道、提价）。"
        return f"{name} {value:.1f}% 处于行业中位以上。"
    if dim == "营运":
        if value < p50:
            return (f"总资产周转率 {value:.2f} 次低于行业中位 {p50:.2f} 次，"
                    f"资产使用效率偏低，建议盘活闲置资产、提升产能利用率。")
        return f"总资产周转率 {value:.2f} 次优于行业，资产效率良好。"
    if dim == "研发":
        if value < p50:
            return f"研发费用率 {value:.2f}% 低于行业中位，长期竞争力可能受限。"
        return f"研发费用率 {value:.2f}% 达到行业中位以上。"
    return ""


SIM_ITEMS = [
    ("毛利率(%)", "毛利率提升", 0.0, 15.0, 1.0),
    ("资产负债率(%)", "资产负债率压降", 0.0, 30.0, 1.0),
    ("总资产周转率", "总资产周转率提升", 0.0, 1.0, 0.05),
    ("经营现金流/营收(%)", "经营现金流利润率提升", 0.0, 25.0, 1.0),
    ("研发费用率(%)", "研发费用率提升", 0.0, 5.0, 0.5),
]

SAMPLE_SME = {
    "示例 A · 华东中药饮片厂（营收约 3 亿，高杠杆 + 回款慢）": dict(
        营业收入=3.0, 上年营业收入=2.85, 归母净利润=0.15, 上年归母净利润=0.18,
        毛利率=30.0, ROE=6.0, 资产负债率=68.0, 总资产=4.2,
        经营现金流净额=-0.10, 研发费用率=1.2),
    "示例 B · 华南中成药企业（营收约 8 亿，接近上市公司中上水平）": dict(
        营业收入=8.0, 上年营业收入=7.4, 归母净利润=0.92, 上年归母净利润=0.85,
        毛利率=52.0, ROE=12.0, 资产负债率=38.0, 总资产=9.0,
        经营现金流净额=1.15, 研发费用率=3.6),
    "示例 C · 西北药材加工企业（营收约 1.2 亿，亏损 + 高杠杆）": dict(
        营业收入=1.2, 上年营业收入=1.35, 归母净利润=-0.08, 上年归母净利润=0.03,
        毛利率=24.0, ROE=-6.5, 资产负债率=78.0, 总资产=1.6,
        经营现金流净额=-0.15, 研发费用率=0.5),
}


def derive_metrics(d: dict) -> dict:
    """由原始录入项派生全部 10 项评分指标。"""
    rev = d.get("营业收入")
    ni = d.get("归母净利润")
    ta = d.get("总资产")
    ocf = d.get("经营现金流净额")
    last_rev = d.get("上年营业收入")
    last_ni = d.get("上年归母净利润")
    out = dict(d)

    def safe_div(a, b):
        try:
            if a is None or b is None or b == 0:
                return None
            return float(a) / float(b)
        except Exception:  # noqa: BLE001
            return None

    if rev is not None and ni is not None and rev != 0:
        out["净利率(%)"] = round(ni / rev * 100, 2)
    if rev is not None and last_rev not in (None, 0):
        out["营收同比(%)"] = round((rev - last_rev) / abs(last_rev) * 100, 2)
    if ni is not None and last_ni not in (None, 0) and last_ni > 0:
        out["净利同比(%)"] = round((ni - last_ni) / abs(last_ni) * 100, 2)
    r = safe_div(rev, ta)
    if r is not None:
        out["总资产周转率"] = round(r, 3)
    r = safe_div(ocf, rev)
    if r is not None:
        out["经营现金流/营收(%)"] = round(r * 100, 2)
    if ni is not None and ni > 0 and ocf is not None:
        out["净利现金含量"] = round(ocf / ni, 3)
    return out


def build_report(name: str, total, level, dim_scores, detail, mode, group, year, weights) -> str:
    lines = [f"# DIAGNOSEX 财务健康度诊断报告", "",
             f"**企业：** {name}",
             f"**基准：** {year} 年中药上市公司年报 · {group}",
             f"**权重口径：** {mode}",
             f"**综合得分：** {total} 分（{level}）", "",
             "## 一、六维度得分", "",
             "| 维度 | 得分 | 权重 |", "| --- | --- | --- |"]
    for dim in DIMS:
        lines.append(f"| {dim} | {dim_scores.get(dim)} | {weights.get(dim)}% |")
    lines += ["", "## 二、指标体检", "",
              "| 指标 | 维度 | 企业值 | P25 | P50 中位 | P75 | 得分 | 判定 |",
              "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for d in detail:
        v = d["数值"]
        v = "未提供" if v is None else f"{v:.2f}{d['单位']}"
        sc = d["得分"]
        if sc is None:
            judge = "—"
            sct = "—"
        else:
            judge, _ = judge_of(sc)
            sct = f"{sc:.1f}"
        b = d["分位基准"]
        lines.append(f"| {d['指标']} | {d['维度']} | {v} | {b.get(0.25)} | {b.get(0.50)} | "
                     f"{b.get(0.75)} | {sct} | {judge} |")
    lines += ["", "## 三、优先改进项", ""]
    rank = sorted([d for d in detail if d["得分"] is not None], key=lambda x: x["得分"])[:6]
    for i, d in enumerate(rank, 1):
        p50 = d["分位基准"].get(0.50) or 0
        lines.append(f"{i}. **{d['指标']}**（{d['得分']:.1f} 分）："
                     f"{advice_for(d['指标'], d['维度'], d['数值'], p50, d['方向'])}")
    lines += ["", "---", "",
              "说明：本报告基于中药上市公司公开年报构建的分位标尺生成，"
              "结果仅供参考，不构成审计意见、投资建议或授信结论。"]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 商业诊断报告（HTML，可打印为 PDF）
# ---------------------------------------------------------------------------
HTML_REPORT_CSS = """
*{box-sizing:border-box;}
body{margin:0;background:#f5f5f7;color:#1d1d1f;
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 font-size:14px;line-height:1.65;-webkit-font-smoothing:antialiased;}
.page{max-width:880px;margin:0 auto;background:#fff;padding:52px 56px 44px;}
.hd{display:flex;justify-content:space-between;align-items:flex-end;
 border-bottom:2px solid #1d1d1f;padding-bottom:14px;margin-bottom:6px;}
.logo{font-size:20px;font-weight:600;letter-spacing:.04em;}
.logo span{font-size:12px;font-weight:400;color:#6e6e73;letter-spacing:.08em;display:block;margin-top:2px;}
.hd-r{text-align:right;font-size:12px;color:#6e6e73;line-height:1.8;}
.sub-hd{display:flex;gap:22px;flex-wrap:wrap;font-size:12px;color:#6e6e73;
 padding:10px 0 20px;border-bottom:1px solid #e5e5ea;margin-bottom:26px;}
.sub-hd b{color:#1d1d1f;font-weight:500;}
h2{font-size:15px;font-weight:600;margin:34px 0 14px;padding-left:10px;border-left:3px solid #0a84ff;}
h2 .en{font-size:11px;color:#8e8e93;font-weight:400;margin-left:8px;letter-spacing:.06em;}
.verdict{display:flex;align-items:center;gap:26px;background:#f5f5f7;border-radius:12px;
 padding:22px 26px;margin-bottom:8px;}
.score{font-size:52px;font-weight:600;line-height:1;letter-spacing:-.02em;}
.score i{font-size:16px;font-style:normal;font-weight:400;color:#8e8e93;margin-left:4px;}
.badge{display:inline-block;color:#fff;font-size:13px;font-weight:500;
 padding:4px 14px;border-radius:999px;letter-spacing:.04em;}
.vtext{font-size:13px;color:#48484a;flex:1;}
table{width:100%;border-collapse:collapse;font-size:13px;margin-top:4px;}
th{background:#f5f5f7;font-weight:500;text-align:left;padding:9px 10px;
 border-bottom:1px solid #d2d2d7;color:#48484a;white-space:nowrap;}
td{padding:9px 10px;border-bottom:1px solid #ececed;}
tr:last-child td{border-bottom:none;}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;}
.ruler{display:flex;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid #f2f2f4;}
.ruler:last-child{border-bottom:none;}
.rmeta{width:210px;flex:none;}
.rname{font-size:13px;font-weight:500;}
.rval{font-size:11px;color:#6e6e73;font-variant-numeric:tabular-nums;}
.rtrack{flex:1;position:relative;height:26px;}
.rline{position:absolute;top:15px;left:0;right:0;height:1px;background:#d2d2d7;}
.rtick{position:absolute;top:11px;width:1px;height:9px;background:#c7c7cc;}
.rtick.major{top:8px;height:15px;background:#8e8e93;}
.rlab{position:absolute;top:0;font-size:9px;color:#8e8e93;transform:translateX(-50%);white-space:nowrap;}
.rcur{position:absolute;top:9px;width:10px;height:10px;border-radius:50%;
 transform:translateX(-50%);border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.12);}
.rscore{width:76px;flex:none;text-align:right;font-size:12px;font-weight:500;
 font-variant-numeric:tabular-nums;}
.adv{background:#f0f9f4;border-left:3px solid #16a34a;padding:12px 16px;
 border-radius:0 8px 8px 0;margin:10px 0;font-size:13px;}
.risk{background:#fef2f2;border-left:3px solid #dc2626;padding:12px 16px;
 border-radius:0 8px 8px 0;margin:10px 0;font-size:13px;}
ol.steps{padding-left:20px;margin:8px 0;}
ol.steps li{margin-bottom:10px;font-size:13px;}
ol.steps b{font-weight:600;}
.gain{display:inline-block;font-size:11px;color:#0a84ff;background:#eaf4ff;
 border-radius:4px;padding:1px 7px;margin-left:6px;font-variant-numeric:tabular-nums;}
.note{font-size:12px;color:#6e6e73;background:#fafafa;border:1px solid #ececed;
 border-radius:8px;padding:14px 18px;margin-top:10px;line-height:1.8;}
.foot{margin-top:38px;padding-top:16px;border-top:1px solid #e5e5ea;
 font-size:11px;color:#8e8e93;display:flex;justify-content:space-between;}
@media print{
 body{background:#fff;} .page{padding:0;max-width:none;}
 h2{page-break-after:avoid;} table,.ruler,.verdict{page-break-inside:avoid;}
 .noprint{display:none;}
 @page{size:A4;margin:16mm 14mm;}
}
"""

HTML_REPORT_VERDICT = {
    "优秀": "整体财务健康度处于行业前列，多数核心指标位于 P75 以上，经营质量优于绝大多数同行。",
    "良好": "整体财务健康度优于行业中位水平，个别指标仍有改进空间，可按优先级继续优化。",
    "一般": "整体处于行业中位附近，优势与短板并存，短板集中在 {dim} 维度，建议针对性整改。",
    "关注": "多项指标低于行业中位，{dim} 维度已进入偏弱区间，需优先处理后再考虑扩张性投入。",
    "风险": "财务健康度处于行业尾部，{dim} 维度存在危险信号，建议先止血、再谈增长。",
}


def _fmt(v, unit=""):
    if v is None:
        return "未提供"
    try:
        return f"{float(v):.2f}{unit}"
    except (TypeError, ValueError):
        return "未提供"


def build_html_report(name: str, total, level, dim_scores, detail, mode, group, year,
                      weights, dim_bench=None, client="", serial="") -> str:
    """生成自包含的商业诊断报告 HTML（离线可用，浏览器打印即成 PDF）。"""
    import html as _html
    from datetime import date as _date

    esc = lambda s: _html.escape(str(s))
    nm = esc(name)
    color = level_color(level)
    today = _date.today().strftime("%Y 年 %m 月 %d 日")
    if not serial:
        serial = "DX-" + _date.today().strftime("%Y%m%d") + "-" + \
                 str(abs(hash(name)) % 10000).zfill(4)

    # 最短板维度
    valid_dims = {d: v for d, v in dim_scores.items() if v is not None}
    weak_dim = min(valid_dims, key=valid_dims.get) if valid_dims else "—"
    strong_dim = max(valid_dims, key=valid_dims.get) if valid_dims else "—"
    vtext = HTML_REPORT_VERDICT.get(level, "").replace("{dim}", weak_dim)

    # 六维度表
    dim_rows = []
    for dim in DIMS:
        sc = dim_scores.get(dim)
        w = weights.get(dim, 0)
        if dim_bench and dim in dim_bench:
            p50, p75 = dim_bench[dim]
            gap = (sc - p50) if (sc is not None and p50 is not None) else None
            gap_txt = "—" if gap is None else f"{gap:+.1f}"
            gap_col = "#16a34a" if (gap or 0) >= 0 else "#dc2626"
            cmp_txt = f'{p50:.1f} / {p75:.1f}'
            gap_html = f'<span style="color:{gap_col};">{gap_txt}</span>'
        else:
            cmp_txt, gap_html = "—", "—"
        dim_rows.append(
            f"<tr><td>{dim}</td><td class='num'>{'—' if sc is None else f'{sc:.1f}'}</td>"
            f"<td class='num'>{w}%</td><td class='num'>{cmp_txt}</td>"
            f"<td class='num'>{gap_html}</td></tr>")

    # 分位标尺
    rulers = []
    for d in detail:
        q = d["分位基准"] or {}
        v, sc = d["数值"], d["得分"]
        jname, jcolor = judge_of(sc) if sc is not None else ("未提供", "#8e8e93")
        unit = d["单位"]
        lo, hi = q.get(0.1), q.get(0.9)
        ticks = ""
        if lo is not None and hi is not None and hi > lo:
            for qq, lab in ((0.1, "P10"), (0.25, "P25"), (0.5, "P50"), (0.75, "P75"), (0.9, "P90")):
                qv = q.get(qq)
                if qv is None:
                    continue
                pos = (qv - lo) / (hi - lo) * 100
                maj = " major" if qq in (0.1, 0.5, 0.9) else ""
                ticks += (f'<span class="rtick{maj}" style="left:{pos:.1f}%"></span>'
                          f'<span class="rlab" style="left:{pos:.1f}%">{lab}</span>')
            if v is not None:
                pos = max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
                cur = (f'<span class="rcur" style="left:{pos:.1f}%;background:{jcolor}" '
                       f'title="企业值 {v:.2f}{unit}"></span>')
            else:
                cur = ""
        else:
            cur = ""
        rulers.append(
            f'<div class="ruler"><div class="rmeta">'
            f'<div class="rname">{esc(d["指标"])}</div>'
            f'<div class="rval">企业值 {_fmt(v, unit)}　·　中位 {_fmt(q.get(0.5), unit)}'
            f'　·　{jname}</div></div>'
            f'<div class="rtrack"><div class="rline"></div>{ticks}{cur}</div>'
            f'<div class="rscore" style="color:{jcolor}">'
            f'{"—" if sc is None else f"{sc:.1f} 分"}</div></div>')

    # 指标体检表
    body_rows = []
    for d in detail:
        sc = d["得分"]
        jname, jcolor = judge_of(sc) if sc is not None else ("未提供", "#8e8e93")
        b = d["分位基准"]
        body_rows.append(
            f"<tr><td>{esc(d['指标'])}</td><td>{d['维度']}</td>"
            f"<td class='num'>{_fmt(d['数值'], d['单位'])}</td>"
            f"<td class='num'>{_fmt(b.get(0.25))}</td>"
            f"<td class='num'>{_fmt(b.get(0.5))}</td>"
            f"<td class='num'>{_fmt(b.get(0.75))}</td>"
            f"<td class='num'>{'—' if sc is None else f'{sc:.1f}'}</td>"
            f"<td style='color:{jcolor};white-space:nowrap;'>{jname}</td></tr>")

    # 优势项 / 风险项
    scored = [d for d in detail if d["得分"] is not None]
    strong = sorted(scored, key=lambda x: -x["得分"])[:3]
    weak = sorted(scored, key=lambda x: x["得分"])[:3]
    strong_html = "".join(
        f'<div class="adv"><b>{esc(d["指标"])}</b>　{d["得分"]:.1f} 分　'
        f'{_fmt(d["数值"], d["单位"])}（行业中位 {_fmt(d["分位基准"].get(0.5), d["单位"])}）'
        f'<br>{esc(advice_for(d["指标"], d["维度"], d["数值"], d["分位基准"].get(0.5) or 0, d["方向"]))}</div>'
        for d in strong if d["得分"] >= 50)
    weak_html = "".join(
        f'<div class="risk"><b>{esc(d["指标"])}</b>　{d["得分"]:.1f} 分　'
        f'{_fmt(d["数值"], d["单位"])}（行业中位 {_fmt(d["分位基准"].get(0.5), d["单位"])}）'
        f'<br>{esc(advice_for(d["指标"], d["维度"], d["数值"], d["分位基准"].get(0.5) or 0, d["方向"]))}</div>'
        for d in weak if d["得分"] < 50)

    # 优先改进项
    rank = sorted([d for d in detail if d["得分"] is not None], key=lambda x: x["得分"])[:6]
    steps = []
    for i, d in enumerate(rank, 1):
        p50v = d["分位基准"].get(0.5) or 0
        steps.append(
            f'<li><b>{esc(d["指标"])}</b>'
            f'<span class="gain">{d["得分"]:.1f} 分</span><br>'
            f'{esc(advice_for(d["指标"], d["维度"], d["数值"], p50v, d["方向"]))}</li>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DIAGNOSEX 财务健康度诊断报告 · {nm}</title>
<style>{HTML_REPORT_CSS}</style></head>
<body><div class="page">

<div class="hd">
  <div class="logo">DIAGNOSEX<span>财务健康度诊断报告</span></div>
  <div class="hd-r">报告编号：{serial}<br>出具日期：{today}</div>
</div>
<div class="sub-hd">
  <span>受检企业：<b>{nm}</b></span>
  <span>诊断基准：<b>{year} 年</b></span>
  <span>对标组：<b>{esc(group)}</b></span>
  <span>权重口径：<b>{esc(mode)}</b></span>
  {f'<span>委托方：<b>{esc(client)}</b></span>' if client else ''}
</div>

<h2>一、诊断结论<span class="en">CONCLUSION</span></h2>
<div class="verdict">
  <div class="score" style="color:{color};">{total if total is not None else "—"}<i>/ 100</i></div>
  <div><span class="badge" style="background:{color};">{level}</span></div>
  <div class="vtext">{esc(vtext)}<br>最强维度：<b>{strong_dim}</b>　·　最弱维度：<b>{weak_dim}</b></div>
</div>

<h2>二、六维度得分<span class="en">SIX DIMENSIONS</span></h2>
<table>
<thead><tr><th>维度</th><th class="num">得分</th><th class="num">权重</th>
<th class="num">行业中位 / 良好</th><th class="num">与中位差</th></tr></thead>
<tbody>{''.join(dim_rows)}</tbody></table>
<div class="note">维度得分为该维度下各指标得分的算术平均；综合得分按权重口径加权得出。
权重口径说明：{esc(WEIGHT_NOTE.get(mode, ''))}</div>

<h2>三、行业分位标尺定位<span class="en">POSITION ON THE INDUSTRY SCALE</span></h2>
{''.join(rulers)}
<div class="note">刻度尺两端为该对标组的 P10 与 P90，中间刻度依次为 P25、P50、P75；
圆点为受检企业在该指标上的实际位置。50 分约等于行业中位，75 分约等于行业 P75。
逆向指标（资产负债率）得分经镜像处理，数值越低得分越高。</div>

<h2>四、十项指标体检<span class="en">INDICATOR CHECK-UP</span></h2>
<table>
<thead><tr><th>指标</th><th>维度</th><th class="num">企业值</th><th class="num">P25</th>
<th class="num">P50 中位</th><th class="num">P75</th><th class="num">得分</th><th>判定</th></tr></thead>
<tbody>{''.join(body_rows)}</tbody></table>

<h2>五、优势项与风险项<span class="en">STRENGTHS &amp; RISKS</span></h2>
{strong_html or '<div class="note">当前无得分达到行业中位以上的指标，建议优先止血。</div>'}
{weak_html or '<div class="note">当前无低于行业中位的风险指标。</div>'}

<h2>六、优先改进项（按收益排序）<span class="en">ACTION PRIORITY</span></h2>
<ol class="steps">{''.join(steps)}</ol>
<div class="note">排序依据为单项得分距离目标分位的加权收益，排在最前的指标单位改善带来的综合分提升最大。
改进幅度可在 DIAGNOSEX 诊断台的情景模拟中预先测算。</div>

<h2>七、方法与数据溯源<span class="en">METHODOLOGY</span></h2>
<div class="note">
1. 行业基准来自申万中药Ⅱ 68 家上市公司 2023—2025 年公开年报，共 204 条记录，
全部指标由原始数据自行计算，不使用第三方评级结果，可回溯复核。<br>
2. 打分采用分位标尺法：以对标样本的 P10、P25、P50、P75、P90 为刻度，分段线性插值映射到 10—90 分，
避免使用算术平均值造成的系统性误判。<br>
3. 缺失指标不参与评分，权重按有效维度重新归一，不以中位分填补。<br>
4. 本报告结论依赖委托方提供数据的真实性，未执行审计程序，不构成审计意见、投资建议或授信结论。
</div>

<div class="foot">
  <span>DIAGNOSEX · 面向中医药企业的财务诊断工具</span>
  <span>报告编号 {serial}　·　本地生成，数据未上传</span>
</div>

</div></body></html>"""


# ---------------------------------------------------------------------------
# 诊断结果单页（HTML · 一页纸 · 每家企业一份 · 可打印为 A4 PDF）
# ---------------------------------------------------------------------------
ONE_PAGE_CSS = """
*{box-sizing:border-box;}
body{margin:0;background:#f5f5f7;color:#1d1d1f;
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
 font-size:12px;line-height:1.5;-webkit-font-smoothing:antialiased;}
.page{max-width:820px;margin:0 auto;background:#fff;padding:24px 28px 16px;}
.hd{display:flex;justify-content:space-between;align-items:flex-end;
 border-bottom:2px solid #1d1d1f;padding-bottom:7px;}
.logo{font-size:16px;font-weight:600;letter-spacing:.04em;}
.logo span{font-size:10px;font-weight:400;color:#6e6e73;letter-spacing:.08em;display:block;margin-top:1px;}
.hd-r{text-align:right;font-size:10px;color:#6e6e73;line-height:1.6;}
.sub-hd{display:flex;gap:16px;flex-wrap:wrap;font-size:11px;color:#6e6e73;
 padding:6px 0 7px;border-bottom:1px solid #e5e5ea;margin-bottom:11px;}
.sub-hd b{color:#1d1d1f;font-weight:500;}
h2{font-size:12px;font-weight:600;margin:11px 0 5px;padding-left:8px;border-left:3px solid #0a84ff;}
h2 .en{font-size:9px;color:#8e8e93;font-weight:400;margin-left:6px;letter-spacing:.06em;}
.verdict{display:flex;align-items:center;gap:16px;background:#f5f5f7;border-radius:10px;padding:11px 15px;}
.score{font-size:42px;font-weight:600;line-height:1;letter-spacing:-.02em;}
.score i{font-size:13px;font-style:normal;font-weight:400;color:#8e8e93;margin-left:3px;}
.badge{display:inline-block;color:#fff;font-size:12px;font-weight:500;padding:3px 12px;border-radius:999px;
 letter-spacing:.04em;}
.vtext{font-size:11px;color:#48484a;flex:1;}
table{width:100%;border-collapse:collapse;font-size:11px;}
th{background:#f5f5f7;font-weight:500;text-align:left;padding:4px 8px;
 border-bottom:1px solid #d2d2d7;color:#48484a;white-space:nowrap;}
td{padding:4px 8px;border-bottom:1px solid #f2f2f4;}
tr:last-child td{border-bottom:none;}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;}
.bar{position:relative;height:8px;background:#ececed;border-radius:4px;overflow:hidden;min-width:80px;}
.bar i{position:absolute;left:0;top:0;bottom:0;border-radius:4px;}
.bar em{position:absolute;top:-2px;bottom:-2px;width:1px;background:#1d1d1f;opacity:.55;}
.ruler{display:flex;align-items:center;gap:10px;padding:2px 0;border-bottom:1px solid #f6f6f8;}
.ruler:last-child{border-bottom:none;}
.rmeta{width:168px;flex:none;}
.rname{font-size:11px;font-weight:500;}
.rval{font-size:9px;color:#6e6e73;font-variant-numeric:tabular-nums;}
.rtrack{flex:1;position:relative;height:21px;}
.rline{position:absolute;top:12px;left:0;right:0;height:1px;background:#d2d2d7;}
.rtick{position:absolute;top:9px;width:1px;height:6px;background:#c7c7cc;}
.rtick.major{top:7px;height:10px;background:#8e8e93;}
.rlab{position:absolute;top:0;font-size:8px;color:#8e8e93;transform:translateX(-50%);white-space:nowrap;}
.rcur{position:absolute;top:8px;width:9px;height:9px;border-radius:50%;transform:translateX(-50%);
 border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.12);}
.rscore{width:58px;flex:none;text-align:right;font-size:11px;font-weight:500;
 font-variant-numeric:tabular-nums;}
ol.steps{padding-left:16px;margin:4px 0;}
ol.steps li{margin-bottom:5px;font-size:11px;}
ol.steps b{font-weight:600;}
.gain{display:inline-block;font-size:10px;color:#0a84ff;background:#eaf4ff;border-radius:4px;
 padding:0 6px;margin-left:5px;font-variant-numeric:tabular-nums;}
.meth{font-size:9.5px;color:#6e6e73;line-height:1.65;margin-top:5px;}
.foot{margin-top:10px;padding-top:7px;border-top:1px solid #e5e5ea;font-size:9px;color:#8e8e93;
 display:flex;justify-content:space-between;gap:12px;}
@media print{
 body{background:#fff;} .page{padding:0;max-width:none;}
 h2{page-break-after:avoid;} table,.verdict,.ruler,ol.steps{page-break-inside:avoid;}
 .noprint{display:none;}
 @page{size:A4;margin:12mm 13mm;}
}
"""


def build_html_onepage(name: str, total, level, dim_scores, detail, mode, group, year,
                       weights, dim_bench=None, client="", serial="") -> str:
    """生成单家企业的「一页纸」诊断结果单页（自包含 HTML，打印即成 A4 PDF）。

    与完整版商业诊断报告的区别：本页只保留企业自身需要的结论、六维度定位、
    十项指标分位标尺和三条优先改进项，压在一张 A4 内，便于逐家分发与归档。
    """
    import html as _html
    from datetime import date as _date

    esc = lambda s: _html.escape(str(s))
    nm = esc(name)
    color = level_color(level)
    today = _date.today().strftime("%Y-%m-%d")
    if not serial:
        serial = "DX-" + _date.today().strftime("%Y%m%d") + "-" + \
                 str(abs(hash(name)) % 10000).zfill(4)

    valid_dims = {d: v for d, v in dim_scores.items() if v is not None}
    weak_dim = min(valid_dims, key=valid_dims.get) if valid_dims else "—"
    strong_dim = max(valid_dims, key=valid_dims.get) if valid_dims else "—"
    vtext = HTML_REPORT_VERDICT.get(level, "").replace("{dim}", weak_dim)

    if not dim_bench:
        dim_bench = {}
        try:
            for d in DIMS:
                p50 = float(np.nanmean([score_value(bench[m["key"]][0.50], bench[m["key"]], m["dir"])
                                        for m in METRICS if m["dim"] == d]))
                dim_bench[d] = (p50, None)
        except Exception:  # noqa: BLE001
            dim_bench = {}

    # 六维度定位条
    dim_rows = []
    for dim in DIMS:
        sc = dim_scores.get(dim)
        p50 = (dim_bench.get(dim) or (None, None))[0]
        gap = (sc - p50) if (sc is not None and p50 is not None) else None
        gap_txt = "—" if gap is None else f"{gap:+.1f}"
        gap_col = "#16a34a" if (gap or 0) >= 0 else "#dc2626"
        jc = judge_of(sc)[1] if sc is not None else "#c7c7cc"
        mark = "" if p50 is None else f'<em style="left:{max(0.0, min(100.0, p50)):.1f}%"></em>'
        bar = (f'<div class="bar"><i style="width:{max(0.0, min(100.0, sc)):.1f}%;'
               f'background:{jc}"></i>{mark}</div>' if sc is not None else '<div class="bar"></div>')
        dim_rows.append(
            f"<tr><td style='white-space:nowrap'>{dim}</td>"
            f"<td style='width:36%'>{bar}</td>"
            f"<td class='num'>{'—' if sc is None else f'{sc:.1f}'}</td>"
            f"<td class='num'>{weights.get(dim, 0)}%</td>"
            f"<td class='num' style='color:{gap_col}'>{gap_txt}</td></tr>")

    # 十项指标分位标尺
    rulers = []
    for d in detail:
        q = d["分位基准"] or {}
        v, sc = d["数值"], d["得分"]
        jname, jcolor = judge_of(sc) if sc is not None else ("未提供", "#8e8e93")
        unit = d["单位"]
        lo, hi = q.get(0.1), q.get(0.9)
        ticks, cur = "", ""
        if lo is not None and hi is not None and hi > lo:
            for qq, lab in ((0.1, "P10"), (0.25, "P25"), (0.5, "P50"), (0.75, "P75"), (0.9, "P90")):
                qv = q.get(qq)
                if qv is None:
                    continue
                pos = (qv - lo) / (hi - lo) * 100
                maj = " major" if qq in (0.1, 0.5, 0.9) else ""
                ticks += (f'<span class="rtick{maj}" style="left:{pos:.1f}%"></span>'
                          f'<span class="rlab" style="left:{pos:.1f}%">{lab}</span>')
            if v is not None:
                pos = max(0.0, min(100.0, (v - lo) / (hi - lo) * 100))
                cur = (f'<span class="rcur" style="left:{pos:.1f}%;background:{jcolor}" '
                       f'title="企业值 {v:.2f}{unit}"></span>')
        rulers.append(
            f'<div class="ruler"><div class="rmeta">'
            f'<div class="rname">{esc(d["指标"])}</div>'
            f'<div class="rval">{_fmt(v, unit)}　|　中位 {_fmt(q.get(0.5), unit)}　|　{jname}</div>'
            f'</div><div class="rtrack"><div class="rline"></div>{ticks}{cur}</div>'
            f'<div class="rscore" style="color:{jcolor}">'
            f'{"—" if sc is None else f"{sc:.1f} 分"}</div></div>')

    # 三条优先改进项
    rank = sorted([d for d in detail if d["得分"] is not None], key=lambda x: x["得分"])[:3]
    steps = []
    for d in rank:
        p50v = d["分位基准"].get(0.5) or 0
        steps.append(
            f'<li><b>{esc(d["指标"])}</b><span class="gain">{d["得分"]:.1f} 分</span>'
            f'{esc(advice_for(d["指标"], d["维度"], d["数值"], p50v, d["方向"]))}</li>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DIAGNOSEX 诊断结果单页 · {nm}</title>
<style>{ONE_PAGE_CSS}</style></head>
<body><div class="page">

<div class="hd">
  <div class="logo">DIAGNOSEX<span>财务健康度诊断结果单页</span></div>
  <div class="hd-r">编号：{serial}<br>出具日期：{today}</div>
</div>
<div class="sub-hd">
  <span>受检企业：<b>{nm}</b></span>
  <span>诊断基准：<b>{year} 年</b></span>
  <span>对标组：<b>{esc(group)}</b></span>
  <span>权重口径：<b>{esc(mode)}</b></span>
  {f'<span>委托方：<b>{esc(client)}</b></span>' if client else ''}
</div>

<h2>诊断结论<span class="en">CONCLUSION</span></h2>
<div class="verdict">
  <div class="score" style="color:{color};">{total if total is not None else "—"}<i>/ 100</i></div>
  <div><span class="badge" style="background:{color};">{level}</span></div>
  <div class="vtext">{esc(vtext)}<br>最强维度：<b>{strong_dim}</b>　·　最弱维度：<b>{weak_dim}</b></div>
</div>

<h2>六维度定位<span class="en">SIX DIMENSIONS</span></h2>
<table>
<thead><tr><th>维度</th><th>得分条（竖线为行业中位）</th><th class="num">得分</th>
<th class="num">权重</th><th class="num">与中位差</th></tr></thead>
<tbody>{''.join(dim_rows)}</tbody></table>

<h2>十项指标分位标尺定位<span class="en">POSITION ON THE INDUSTRY SCALE</span></h2>
{''.join(rulers)}

<h2>优先改进项（按收益排序）<span class="en">ACTION PRIORITY</span></h2>
<ol class="steps">{''.join(steps)}</ol>

<div class="meth">
基准：申万中药Ⅱ 68 家上市公司 {year} 年公开年报，共 204 条记录，指标由原始数据自行计算。
打分采用分位标尺法（P10/P25/P50/P75/P90 分段线性插值映射至 10—90 分），不使用算术平均值；
缺失指标不参与评分，权重按有效维度重新归一。本页结论依赖所提供数据的真实性，
未执行审计程序，不构成审计意见、投资建议或授信结论。
</div>

<div class="foot">
  <span>DIAGNOSEX · 面向中医药企业的财务诊断工具</span>
  <span>编号 {serial}　·　本地生成，数据未上传</span>
</div>

</div></body></html>"""


def zip_html_reports(items: list) -> bytes:
    """把多份（文件名, HTML 文本）打包成一个 ZIP，用于批量逐家分发。"""
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, content in items:
            z.writestr(fname, content.encode("utf-8"))
    return buf.getvalue()


# ---------------------------------------------------------------------------
# 界面
# ---------------------------------------------------------------------------
inject_apple_style()

df_all = load_data()
YEARS = sorted(df_all["年份"].unique().tolist(), reverse=True)

with st.sidebar:
    st.markdown(f"### {BRAND}")
    st.caption(BRAND_SUB)
    st.markdown("---")
    year = st.selectbox("基准年份", YEARS, index=0,
                        help="分位标尺取自该年度上市公司年报")
    group = st.radio("对标组", GROUPS, index=0)
    mode = st.radio("权重口径", list(WEIGHT_MODES.keys()), index=1)
    st.caption(WEIGHT_NOTE[mode])
    st.markdown("---")
    st.caption("数据：申万中药Ⅱ 68 家上市公司 2023—2025 年报，204 条记录。")

bench = build_benchmark(year, group)
weights = WEIGHT_MODES[mode]

st.markdown(
    f'<div class="ap-hero">'
    f'<div class="ap-eyebrow">{BRAND}</div>'
    f'<div class="ap-title">{BRAND_SUB}</div>'
    f'<p class="ap-sub">基准来自 {df_all["代码"].nunique()} 家中药上市公司 '
    f'{min(YEARS)}—{max(YEARS)} 年公开年报，共 {len(df_all)} 条真实记录。'
    f'把上市公司的财务分布降维成一把分位标尺，让没有对标数据的中小企业也能量化自己的健康度。</p>'
    f'</div><div class="ap-rule"></div>',
    unsafe_allow_html=True)

# 支持通过链接直达页签：?tab=industry / ?tab=company / ?tab=rank / ?tab=diag
TAB_DEFS = [("industry", "行业全景"), ("company", "企业详情"),
            ("rank", "基准与排行"), ("diag", "DIAGNOSE 诊断台")]
_active = str(st.query_params.get("tab", "industry")).lower()
_order = [i for i, (k, _) in enumerate(TAB_DEFS) if k == _active]
if _order:
    idx = _order[0]
    TAB_DEFS = [TAB_DEFS[idx]] + TAB_DEFS[:idx] + TAB_DEFS[idx + 1:]

tabs = st.tabs([t for _, t in TAB_DEFS])
_tab_map = {TAB_DEFS[i][0]: tabs[i] for i in range(len(TAB_DEFS))}
tab_rank = _tab_map["rank"]
tab_company = _tab_map["company"]
tab_industry = _tab_map["industry"]
tab_diag = _tab_map["diag"]

# ===========================================================================
# 1. 基准与排行
# ===========================================================================
with tab_rank:
    uni = score_universe(year, group, mode)
    section("基准与排行",
            f"{year} 年 · {group} · 共 {len(uni)} 家上市公司，"
            f"按 {mode} 计算六维度加权得分。",
            eyebrow="BENCHMARK")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("样本企业", f"{len(uni)} 家")
    with c2:
        st.metric("健康度中位数", f"{uni['综合分'].median():.1f} 分")
    with c3:
        st.metric("营收中位数", f"{uni['营业收入'].median():.2f} 亿元")
    with c4:
        loss = int((uni["归母净利润"] <= 0).sum())
        st.metric("亏损企业", f"{loss} 家")

    left, right = st.columns([3.2, 2.0])
    with left:
        st.markdown("#### 得分分布")
        fig = px.histogram(uni, x="综合分", nbins=20, template=PX_TEMPLATE,
                           color_discrete_sequence=[BLUE], opacity=0.9)
        fig.update_layout(height=320, yaxis_title="企业数", xaxis_title="综合健康度得分",
                          margin=dict(l=20, r=20, t=10, b=30), bargap=0.06)
        st.plotly_chart(fig, **PLOT_KW)
    with right:
        st.markdown("#### 评级构成")
        lv = uni["评级"].value_counts().reindex([n for n, _, _ in LEVELS]).fillna(0)
        fig = go.Figure(go.Bar(
            x=lv.values, y=lv.index, orientation="h",
            marker_color=[level_color(n) for n in lv.index],
            text=lv.values.astype(int), textposition="outside"))
        fig.update_layout(height=320, margin=dict(l=70, r=40, t=10, b=30),
                          xaxis_title="企业数", yaxis_title="",
                          yaxis=dict(automargin=True, tickfont=dict(size=12)))
        st.plotly_chart(fig, **PLOT_KW)

    order = st.radio("排序", ["综合分由高到低", "综合分由低到高", "营业收入", "ROE"],
                     horizontal=True, key="rank_order")
    kw = st.text_input("搜索企业名称或代码", "", key="rank_search")
    levels = st.multiselect("按评级筛选", [n for n, _, _ in LEVELS], default=[], key="rank_lv")

    view = uni.copy()
    if kw:
        view = view[view["名称"].str.contains(kw, case=False, na=False) |
                    view["代码"].str.contains(kw, na=False)]
    if levels:
        view = view[view["评级"].isin(levels)]
    if order == "综合分由低到高":
        view = view.sort_values("综合分")
    elif order == "营业收入":
        view = view.sort_values("营业收入", ascending=False)
    elif order == "ROE":
        view = view.sort_values("ROE", ascending=False)

    cols = ["排名", "名称", "代码", "综合分", "评级"] + DIMS + ["营业收入", "ROE", "资产负债率"]
    st.dataframe(
        view[cols].style.format({"综合分": "{:.1f}", "营业收入": "{:.2f}",
                                 "ROE": "{:.2f}", "资产负债率": "{:.2f}"}),
        hide_index=True, height=440,
        column_config={
            "综合分": st.column_config.ProgressColumn("综合分", min_value=0, max_value=100, format="%.1f"),
            "盈利": st.column_config.NumberColumn(format="%.1f"),
            "成长": st.column_config.NumberColumn(format="%.1f"),
            "偿债": st.column_config.NumberColumn(format="%.1f"),
            "营运": st.column_config.NumberColumn(format="%.1f"),
            "现金流": st.column_config.NumberColumn(format="%.1f"),
            "研发": st.column_config.NumberColumn(format="%.1f"),
        })

    st.markdown("#### 领先与待改善")
    b1, b2 = st.columns(2)
    with b1:
        fig = rank_bar(uni, 15, ascending=True)
        fig.update_layout(title=dict(text="得分最高的 15 家"))
        st.plotly_chart(fig, **PLOT_KW)
    with b2:
        fig = rank_bar(uni, 15, ascending=False)
        fig.update_layout(title=dict(text="得分最低的 15 家"))
        st.plotly_chart(fig, **PLOT_KW)

# ===========================================================================
# 2. 企业详情
# ===========================================================================
with tab_company:
    uni = score_universe(year, group, mode)
    names = uni["名称"].tolist()
    section("企业详情",
            "查看单家上市公司三年真实财务轨迹，以及与行业分位标尺的相对位置。",
            eyebrow="COMPANY")

    pick = st.selectbox("选择企业", names, key="co_pick")
    row = uni[uni["名称"] == pick].iloc[0]
    code = row["代码"]
    hist = df_all[df_all["代码"] == code].sort_values("年份")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric(f"{year} 年综合分", f"{row['综合分']:.1f}", row["评级"])
    with c2:
        st.metric("营业收入", f"{row['营业收入']:.2f} 亿元")
    with c3:
        st.metric("归母净利润", f"{row['归母净利润']:.2f} 亿元")
    with c4:
        st.metric("毛利率", f"{row['毛利率']:.2f}%")
    with c5:
        st.metric("资产负债率", f"{row['资产负债率']:.2f}%")

    l, r = st.columns([1.35, 1.0])
    with l:
        st.markdown("#### 三年经营轨迹")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hist["年份"], y=hist["营业收入(亿元)"], name="营业收入",
                             marker_color="rgba(0,113,227,0.75)"))
        fig.add_trace(go.Bar(x=hist["年份"], y=hist["归母净利润(亿元)"], name="归母净利润",
                             marker_color="rgba(52,199,89,0.75)"))
        fig.add_trace(go.Scatter(x=hist["年份"], y=hist["经营现金流净额(亿元)"],
                                 name="经营现金流", mode="lines+markers",
                                 line=dict(color="#ff9f0a", width=2.5)))
        fig.update_layout(height=360, barmode="group", yaxis_title="亿元",
                          xaxis=dict(tickmode="array", tickvals=hist["年份"]),
                          margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, **PLOT_KW)

        st.markdown("#### 盈利与杠杆")
        fig = go.Figure()
        for col, nm, color in [("毛利率(%)", "毛利率", BLUE), ("净利率(%)", "净利率", "#34c759"),
                               ("ROE(%)", "ROE", "#af52de"), ("资产负债率(%)", "资产负债率", "#ff9f0a")]:
            fig.add_trace(go.Scatter(x=hist["年份"], y=hist[col], name=nm,
                                     mode="lines+markers", line=dict(color=color, width=2.2)))
        fig.update_layout(height=330, yaxis_title="%",
                          xaxis=dict(tickmode="array", tickvals=hist["年份"]),
                          margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, **PLOT_KW)
    with r:
        cur = {d: row[d] for d in DIMS}
        p50 = {d: np.nanmean([score_value(bench[m["key"]][0.50], bench[m["key"]], m["dir"])
                              for m in METRICS if m["dim"] == d]) for d in DIMS}
        p75 = {d: np.nanmean([score_value(bench[m["key"]][0.75], bench[m["key"]], m["dir"])
                              for m in METRICS if m["dim"] == d]) for d in DIMS}
        fig = radar_fig(cur, {"行业中位 P50": (p50, "#8e8e93"), "行业良好 P75": (p75, "#34c759")},
                        title=f"{year} 年六维度对比")
        st.plotly_chart(fig, **PLOT_KW)

        st.markdown("#### 指标分位定位")
        cur_year = hist[hist["年份"] == year].iloc[0]
        rows = []
        for m in METRICS:
            v = cur_year.get(m["key"], np.nan)
            series = pd.to_numeric(df_all[df_all["年份"] == year][m["key"]], errors="coerce").dropna()
            pct = float((series <= v).mean() * 100) if not np.isnan(v) else np.nan
            rows.append(dict(指标=m["name"], 数值=(None if np.isnan(v) else round(float(v), 2)),
                             行业分位=(None if np.isnan(pct) else round(pct, 1))))
        pdf_ = pd.DataFrame(rows)
        fig = px.bar(pdf_, x="行业分位", y="指标", orientation="h",
                     color_discrete_sequence=[BLUE], template=PX_TEMPLATE,
                     text=pdf_["行业分位"], range_x=[0, 100])
        fig.update_traces(textposition="outside", textfont=dict(size=10, color=SUB))
        fig.update_layout(height=380, xaxis_title="行业分位（%）", yaxis_title="",
                          margin=dict(l=120, r=50, t=10, b=30),
                          yaxis=dict(automargin=True, tickfont=dict(size=11)))
        st.plotly_chart(fig, **PLOT_KW)

    st.markdown("#### 三年指标明细")
    show_cols = ["年份", "营业收入(亿元)", "营收同比(%)", "归母净利润(亿元)", "净利同比(%)",
                 "毛利率(%)", "净利率(%)", "ROE(%)", "资产负债率(%)", "总资产(亿元)",
                 "经营现金流净额(亿元)", "研发费用率(%)", "经营现金流/营收(%)"]
    st.dataframe(hist[show_cols].round(2), hide_index=True)

    # 逐家导出：该企业的一页纸诊断结果单页
    _hy = hist[hist["年份"] == year]
    if not _hy.empty:
        _cy = _hy.iloc[0]
        _ovals = {m["key"]: _cy.get(m["key"], np.nan) for m in METRICS}
        _ot, _ods, _odet = score_metrics(_ovals, bench, weights)
        _olv = level_of(_ot) if _ot is not None else "—"
        _odb = {d: (float(np.nanmean([score_value(bench[m["key"]][0.50], bench[m["key"]], m["dir"])
                                      for m in METRICS if m["dim"] == d])),
                    float(np.nanmean([score_value(bench[m["key"]][0.75], bench[m["key"]], m["dir"])
                                      for m in METRICS if m["dim"] == d]))) for d in DIMS}
        _oone = build_html_onepage(pick, _ot, _olv, _ods, _odet, mode, group, year,
                                   weights, dim_bench=_odb)
        _ofull = build_html_report(pick, _ot, _olv, _ods, _odet, mode, group, year,
                                   weights, dim_bench=_odb)
        st.markdown("#### 该企业诊断结果导出")
        _e1, _e2 = st.columns(2)
        with _e1:
            st.download_button("诊断结果单页（HTML · 一页纸）", _oone.encode("utf-8"),
                               file_name=f"DIAGNOSEX_{pick}_诊断结果单页.html",
                               mime="text/html", key="co_one")
        with _e2:
            st.download_button("完整商业报告（HTML）", _ofull.encode("utf-8"),
                               file_name=f"DIAGNOSEX_{pick}_商业诊断报告.html",
                               mime="text/html", key="co_full")

# ===========================================================================
# 3. 行业全景
# ===========================================================================
with tab_industry:
    section("行业全景",
            f"{min(YEARS)}—{max(YEARS)} 年中药上市公司整体走势、分化与结构性特征。",
            eyebrow="INDUSTRY")

    agg = df_all.groupby("年份").agg(
        营收合计=("营业收入(亿元)", "sum"),
        净利合计=("归母净利润(亿元)", "sum"),
        营收中位=("营业收入(亿元)", "median"),
        毛利率中位=("毛利率(%)", "median"),
        净利率中位=("净利率(%)", "median"),
        负债率中位=("资产负债率(%)", "median"),
        亏损家数=("归母净利润(亿元)", lambda s: int((s <= 0).sum())),
    ).reset_index()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(f"{max(YEARS)} 年行业营收", f"{agg['营收合计'].iloc[-1]:,.0f} 亿元",
                  f"{agg['营收合计'].pct_change().iloc[-1] * 100:.2f}%")
    with c2:
        st.metric(f"{max(YEARS)} 年行业净利", f"{agg['净利合计'].iloc[-1]:,.0f} 亿元",
                  f"{agg['净利合计'].pct_change().iloc[-1] * 100:.2f}%")
    with c3:
        st.metric("亏损家数", f"{agg['亏损家数'].iloc[-1]} 家",
                  f"{agg['亏损家数'].iloc[-1] - agg['亏损家数'].iloc[0]} 家（较基年）")
    with c4:
        st.metric("净利率中位数", f"{agg['净利率中位'].iloc[-1]:.2f}%",
                  f"{agg['净利率中位'].iloc[-1] - agg['净利率中位'].iloc[0]:.2f} pp")

    l, r = st.columns([1.4, 1.0])
    with l:
        st.markdown("#### 行业总量与亏损面")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=agg["年份"], y=agg["营收合计"], name="营收合计",
                             marker_color="rgba(0,113,227,0.75)"))
        fig.add_trace(go.Bar(x=agg["年份"], y=agg["净利合计"], name="归母净利合计",
                             marker_color="rgba(52,199,89,0.75)"))
        fig.add_trace(go.Scatter(x=agg["年份"], y=agg["亏损家数"], name="亏损家数",
                                 yaxis="y2", mode="lines+markers",
                                 line=dict(color=BAD, width=2.5)))
        fig.update_layout(height=380, barmode="group", yaxis_title="亿元",
                          yaxis2=dict(title="亏损家数", overlaying="y", side="right",
                                      showgrid=False),
                          xaxis=dict(tickmode="array", tickvals=agg["年份"]),
                          margin=dict(l=20, r=50, t=30, b=30))
        st.plotly_chart(fig, **PLOT_KW)
    with r:
        st.markdown("#### 盈利能力中位变化")
        fig = go.Figure()
        for col, nm, color in [("毛利率中位", "毛利率中位", BLUE),
                               ("净利率中位", "净利率中位", "#34c759"),
                               ("负债率中位", "资产负债率中位", "#ff9f0a")]:
            fig.add_trace(go.Scatter(x=agg["年份"], y=agg[col], name=nm,
                                     mode="lines+markers", line=dict(color=color, width=2.4)))
        fig.update_layout(height=380, yaxis_title="%",
                          xaxis=dict(tickmode="array", tickvals=agg["年份"]),
                          margin=dict(l=20, r=20, t=30, b=30))
        st.plotly_chart(fig, **PLOT_KW)

    st.markdown("#### 风险—回报分布")
    cur = df_all[df_all["年份"] == year].copy()
    uni_cur = score_universe(year, "全行业", mode)
    cur = cur.merge(uni_cur[["代码", "综合分", "评级"]], on="代码", how="left")
    fig = px.scatter(cur, x="资产负债率(%)", y="ROE(%)", size="营业收入(亿元)",
                     color="综合分", hover_name="名称", template=PX_TEMPLATE,
                     color_continuous_scale=[BAD, "#ff9f0a", "#34c759", GOOD],
                     size_max=48)
    fig.add_hline(y=0, line_width=1, line_dash="dot", line_color="rgba(0,0,0,0.25)")
    fig.update_layout(height=440, xaxis_title="资产负债率（%）", yaxis_title="ROE（%）",
                      margin=dict(l=20, r=20, t=30, b=40))
    st.plotly_chart(fig, **PLOT_KW)

    l2, r2 = st.columns(2)
    with l2:
        st.markdown("#### 头部 vs 尾部")
        srt = uni_cur.sort_values("综合分", ascending=False)
        top15 = srt.head(15)[DIMS].median()
        bot15 = srt.tail(15)[DIMS].median()
        fig = radar_fig({d: float(top15[d]) for d in DIMS},
                        {"尾部 15 家中位": ({d: float(bot15[d]) for d in DIMS}, BAD)},
                        title="得分前 15 家 vs 后 15 家")
        st.plotly_chart(fig, **PLOT_KW)
    with r2:
        st.markdown("#### 指标相关性")
        corr = df_all[df_all["年份"] == year][[m["key"] for m in METRICS]].corr()
        corr.index = [METRIC_BY_KEY[k]["name"] for k in corr.index]
        corr.columns = [METRIC_BY_KEY[k]["name"] for k in corr.columns]
        fig = px.imshow(corr, text_auto=".2f", aspect="auto", template=PX_TEMPLATE,
                        color_continuous_scale=["#d70015", "#ffffff", "#0071e3"],
                        zmin=-1, zmax=1)
        fig.update_layout(height=440, margin=dict(l=20, r=20, t=20, b=20),
                          coloraxis_showscale=False)
        fig.update_xaxes(tickfont=dict(size=10))
        fig.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(fig, **PLOT_KW)

    st.markdown("#### 连续三年营收与净利双增")
    p = df_all.pivot_table(index=["代码", "名称"], columns="年份",
                           values=["营业收入(亿元)", "归母净利润(亿元)"])
    grow = []
    for (code, nm), r_ in p.iterrows():
        rev = [r_[("营业收入(亿元)", y)] for y in YEARS]
        ni = [r_[("归母净利润(亿元)", y)] for y in YEARS]
        rev_ok = all(rev[i] < rev[i + 1] for i in range(len(rev) - 1))
        ni_ok = all(ni[i] < ni[i + 1] for i in range(len(ni) - 1))
        if rev_ok and ni_ok:
            grow.append(dict(代码=code, 名称=nm,
                             **{f"{y} 营收": round(rev[i], 2) for i, y in enumerate(YEARS)},
                             **{f"{y} 净利": round(ni[i], 2) for i, y in enumerate(YEARS)}))
    grow_df = pd.DataFrame(grow)
    if grow_df.empty:
        st.info("当前数据下没有连续三年营收与净利双增的企业。")
    else:
        st.dataframe(grow_df, hide_index=True)
        st.caption(f"共 {len(grow_df)} 家，占样本 {len(grow_df) / df_all['代码'].nunique() * 100:.1f}%。")

# ===========================================================================
# 4. DIAGNOSE 诊断台
# ===========================================================================
with tab_diag:
    section("DIAGNOSE 诊断台",
            "录入企业真实财务数据，与上市公司分位标尺对标，得到可解释的健康度评分与改进路径。",
            eyebrow="DIAGNOSE")


    # ?mode=sample 可直达示例诊断（便于分享演示链接）
    _modes = ["单户表单录入", "批量上传 CSV", "载入示例企业"]
    _mi = 0
    if str(st.query_params.get("mode", "")).lower() in ("sample", "demo"):
        _mi = 2
    input_mode = st.radio("录入方式", _modes, index=_mi, horizontal=True, key="diag_mode")

    def diagnose_one(values: dict, name: str):
        total, dim_scores, detail = score_metrics(values, bench, weights)
        return total, dim_scores, detail

    def render_result(name, values, total, dim_scores, detail, key_prefix=""):
        level = level_of(total) if total is not None else "—"
        color = level_color(level)
        st.markdown(
            f'<div class="ap-card">'
            f'<p class="ap-kpi">{name} · 综合健康度</p>'
            f'<div style="font-size:46px;font-weight:600;letter-spacing:-0.02em;color:{color};'
            f'line-height:1.1;">{total:.1f}'
            f'<span style="font-size:16px;color:{SUB};font-weight:400;"> / 100</span></div>'
            f'<span class="dx-badge" style="background:{color};">{level}</span>'
            f'<p class="ap-note">基准：{year} 年 · {group} · {mode}</p>'
            f'</div>', unsafe_allow_html=True)

        l, r = st.columns([1.0, 1.35])
        dim_cmp = {}
        for _d in DIMS:
            _p50 = float(np.nanmean([score_value(bench[m["key"]][0.50], bench[m["key"]], m["dir"])
                                     for m in METRICS if m["dim"] == _d]))
            _p75 = float(np.nanmean([score_value(bench[m["key"]][0.75], bench[m["key"]], m["dir"])
                                     for m in METRICS if m["dim"] == _d]))
            dim_cmp[_d] = (_p50, _p75)
        with l:
            st.plotly_chart(
                radar_fig(dim_scores, {"行业中位 P50": ({k: v[0] for k, v in dim_cmp.items()}, "#8e8e93"),
                                       "行业良好 P75": ({k: v[1] for k, v in dim_cmp.items()}, "#34c759")}), **PLOT_KW)
        with r:
            st.markdown("#### 指标体检")
            rows = []
            for d in detail:
                sc = d["得分"]
                judge, jc = judge_of(sc) if sc is not None else ("未提供", SUB)
                v = d["数值"]
                b = d["分位基准"]
                rows.append(dict(
                    指标=d["指标"], 维度=d["维度"],
                    企业值=("未提供" if v is None else f"{v:.2f}{d['单位']}"),
                    P25=b.get(0.25), P50中位=b.get(0.50), P75=b.get(0.75),
                    得分=("—" if sc is None else f"{sc:.1f}"), 判定=judge))
            st.dataframe(pd.DataFrame(rows), hide_index=True, height=420)

        st.markdown("#### 优先改进项")
        rank = sorted([d for d in detail if d["得分"] is not None], key=lambda x: x["得分"])[:6]
        for d in rank:
            p50v = d["分位基准"].get(0.50) or 0
            judge, jc = judge_of(d["得分"])
            with st.expander(f"{d['指标']} · {d['得分']:.1f} 分 · {judge}", expanded=d["得分"] < 40):
                st.markdown(
                    f'<p class="ap-note">当前 {d["数值"]:.2f}{d["单位"]}，'
                    f'行业中位 {p50v:.2f}{d["单位"]}。</p>', unsafe_allow_html=True)
                st.write(advice_for(d["指标"], d["维度"], d["数值"], p50v, d["方向"]))

        st.markdown("#### 情景模拟")
        st.caption("拖动滑块模拟改进措施落地后的得分变化（不改变原始数据）。")
        sim_vals = dict(values)
        sim_cols = st.columns(len(SIM_ITEMS))
        deltas = {}
        for i, (key, label, lo, hi, step) in enumerate(SIM_ITEMS):
            with sim_cols[i]:
                cur_v = values.get(key, None)
                d = st.slider(label, lo, hi, 0.0, step, key=f"{key_prefix}sim_{key}")
                if cur_v is not None and not (isinstance(cur_v, float) and np.isnan(cur_v)):
                    sign = -1 if key == "资产负债率(%)" else 1
                    sim_vals[key] = float(cur_v) + sign * d
                deltas[key] = d
        sim_total, sim_dims, sim_detail = diagnose_one(sim_vals, name)
        if abs(sim_total - total) > 0.05:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("改进前", f"{total:.1f} 分", level_of(total))
            with c2:
                st.metric("模拟后", f"{sim_total:.1f} 分", level_of(sim_total))
            with c3:
                st.metric("提升", f"{sim_total - total:+.1f} 分")
        else:
            st.caption("当前未设置任何改进幅度。")

        st.markdown("#### 报告导出")
        rep = build_report(name, total, level, dim_scores, detail, mode, group, year, weights)
        rep_html = build_html_report(name, total, level, dim_scores, detail, mode, group,
                                     year, weights, dim_bench=dim_cmp)
        one_html = build_html_onepage(name, total, level, dim_scores, detail, mode, group,
                                      year, weights, dim_bench=dim_cmp)
        _c1, _c2, _c3 = st.columns(3)
        with _c1:
            st.download_button("下载诊断结果单页（HTML · 一页纸）", one_html.encode("utf-8"),
                               file_name=f"DIAGNOSEX_{name}_诊断结果单页.html",
                               mime="text/html", key=f"{key_prefix}dlo")
        with _c2:
            st.download_button("下载诊断报告（Markdown）", rep.encode("utf-8"),
                               file_name=f"DIAGNOSEX_{name}_诊断报告.md",
                               mime="text/markdown", key=f"{key_prefix}dl")
        with _c3:
            st.download_button("下载完整商业报告（HTML）",
                               rep_html.encode("utf-8"),
                               file_name=f"DIAGNOSEX_{name}_商业诊断报告.html",
                               mime="text/html", key=f"{key_prefix}dlh")

    if input_mode == "单户表单录入":
        with st.form("diag_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("企业名称", "待诊断企业")
                rev = st.number_input("营业收入（亿元）", value=3.0, min_value=0.0, step=0.1)
                last_rev = st.number_input("上年营业收入（亿元，选填）", value=0.0, min_value=0.0, step=0.1)
                ni = st.number_input("归母净利润（亿元）", value=0.15, step=0.01)
            with c2:
                last_ni = st.number_input("上年归母净利润（亿元，选填）", value=0.0, step=0.01)
                gm = st.number_input("毛利率（%）", value=30.0, step=0.5)
                roe = st.number_input("ROE（%）", value=6.0, step=0.5)
                debt = st.number_input("资产负债率（%）", value=60.0, min_value=0.0, max_value=100.0, step=1.0)
            with c3:
                ta = st.number_input("总资产（亿元）", value=4.0, min_value=0.0, step=0.1)
                ocf = st.number_input("经营现金流净额（亿元）", value=0.0, step=0.01)
                rd = st.number_input("研发费用率（%，选填，0 表示未提供）", value=0.0, min_value=0.0, step=0.1)
            submitted = st.form_submit_button("开始诊断")

        if submitted:
            raw = dict(营业收入=rev, 归母净利润=ni, 毛利率=gm, ROE=roe,
                       资产负债率=debt, 总资产=ta, 经营现金流净额=ocf)
            if last_rev > 0:
                raw["上年营业收入"] = last_rev
            if last_ni != 0:
                raw["上年归母净利润"] = last_ni
            if rd > 0:
                raw["研发费用率"] = rd
            values = derive_metrics({
                "毛利率(%)": gm, "ROE(%)": roe, "资产负债率(%)": debt,
                **({k: v for k, v in raw.items() if k in
                    ("营业收入", "上年营业收入", "归母净利润", "上年归母净利润",
                     "总资产", "经营现金流净额")}),
                **({"研发费用率(%)": rd} if rd > 0 else {}),
            })
            total, dim_scores, detail = diagnose_one(values, name)
            render_result(name, values, total, dim_scores, detail, key_prefix="form")

    elif input_mode == "载入示例企业":
        pick = st.selectbox("选择内置示例企业", list(SAMPLE_SME.keys()))
        s = SAMPLE_SME[pick]
        values = derive_metrics({
            "营业收入": s["营业收入"], "上年营业收入": s["上年营业收入"],
            "归母净利润": s["归母净利润"], "上年归母净利润": s["上年归母净利润"],
            "总资产": s["总资产"], "经营现金流净额": s["经营现金流净额"],
            "毛利率(%)": s["毛利率"], "ROE(%)": s["ROE"],
            "资产负债率(%)": s["资产负债率"], "研发费用率(%)": s["研发费用率"],
        })
        total, dim_scores, detail = diagnose_one(values, pick.split(" · ")[1])
        render_result(pick.split(" · ")[1], values, total, dim_scores, detail, key_prefix="sample")

    else:
        tpl = pd.DataFrame([{
            "企业名称": "示例企业", "营业收入": 3.0, "上年营业收入": 2.8,
            "归母净利润": 0.15, "上年归母净利润": 0.12, "毛利率": 30.0,
            "ROE": 6.0, "资产负债率": 60.0, "总资产": 4.0,
            "经营现金流净额": 0.05, "研发费用率": 1.2}])
        st.download_button("下载 CSV 模板", tpl.to_csv(index=False).encode("utf-8-sig"),
                           file_name="DIAGNOSEX_批量诊断模板.csv", mime="text/csv")
        up = st.file_uploader("上传企业财务数据 CSV", type=["csv"], key="diag_upload")
        if up is not None:
            raw = up.getvalue()
            text = None
            for enc in ("utf-8-sig", "gbk", "utf-8"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                st.error("无法识别文件编码，请转换为 UTF-8 或 GBK 后重试。")
            else:
                try:
                    batch = pd.read_csv(io.StringIO(text))
                except Exception as exc:  # noqa: BLE001
                    st.error(f"解析失败：{exc}")
                    batch = None
                if batch is not None and not batch.empty:
                    results, details_map = [], {}
                    for _, r in batch.iterrows():
                        nm = str(r.get("企业名称", f"企业 {len(results) + 1}"))
                        vals = derive_metrics({
                            "营业收入": r.get("营业收入"), "上年营业收入": r.get("上年营业收入"),
                            "归母净利润": r.get("归母净利润"), "上年归母净利润": r.get("上年归母净利润"),
                            "总资产": r.get("总资产"), "经营现金流净额": r.get("经营现金流净额"),
                            "毛利率(%)": r.get("毛利率"), "ROE(%)": r.get("ROE"),
                            "资产负债率(%)": r.get("资产负债率"), "研发费用率(%)": r.get("研发费用率"),
                        })
                        t, ds, det = diagnose_one(vals, nm)
                        details_map[nm] = (vals, t, ds, det)
                        results.append(dict(企业名称=nm, 综合分=t, 评级=level_of(t) if t else "—",
                                            **{d: ds[d] for d in DIMS}))
                    res = pd.DataFrame(results).sort_values("综合分", ascending=False)
                    res.insert(0, "排名", range(1, len(res) + 1))
                    st.markdown("#### 批量诊断结果")
                    st.dataframe(res, hide_index=True, height=min(420, 60 + 40 * len(res)))
                    st.download_button("下载结果 CSV",
                                       res.to_csv(index=False).encode("utf-8-sig"),
                                       file_name="DIAGNOSEX_批量诊断结果.csv", mime="text/csv")

                    # 逐家生成一页纸诊断结果单页
                    _db = {d: (float(np.nanmean([score_value(bench[m["key"]][0.50],
                                                              bench[m["key"]], m["dir"])
                                                for m in METRICS if m["dim"] == d])), None)
                           for d in DIMS}
                    _pages = []
                    for _nm, (_v, _t, _ds, _det) in details_map.items():
                        _lv = level_of(_t) if _t is not None else "—"
                        _pages.append(
                            (f"DIAGNOSEX_{_nm}_诊断结果单页.html",
                             build_html_onepage(_nm, _t, _lv, _ds, _det, mode, group,
                                                year, weights, dim_bench=_db)))
                    st.markdown("#### 逐家诊断结果单页（HTML · 一页纸）")
                    _b1, _b2 = st.columns([1.2, 2.0])
                    with _b1:
                        st.download_button("打包下载全部单页（ZIP）",
                                           zip_html_reports(_pages),
                                           file_name="DIAGNOSEX_批量诊断结果单页.zip",
                                           mime="application/zip", key="batch_zip")
                    with _b2:
                        with st.expander(f"逐家单独下载（{len(_pages)} 份）", expanded=False):
                            _cols = st.columns(3)
                            for _i, (_fn, _html) in enumerate(_pages):
                                with _cols[_i % 3]:
                                    st.download_button(
                                        _fn.replace("DIAGNOSEX_", "").replace("_诊断结果单页.html", ""),
                                        _html.encode("utf-8"), file_name=_fn,
                                        mime="text/html", key=f"batch_one_{_i}")

                    pick2 = st.selectbox("查看单家明细", res["企业名称"].tolist())
                    if pick2:
                        v, t, ds, det = details_map[pick2]
                        render_result(pick2, v, t, ds, det, key_prefix="batch")
