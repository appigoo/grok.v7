import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import requests

# ══════════════════════════════════════════════════════════════════════════════
# 頁面設定
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="美股即時監控系統",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }

    /* Metric 卡片 */
    [data-testid="stMetric"] {
        background: #1e2235; border-radius: 10px;
        padding: 12px 14px; border: 1px solid #2e3456;
    }
    [data-testid="stMetricLabel"] > div {
        font-size: 0.9rem !important; color: #aab4cc !important;
        font-weight: 600; letter-spacing: 0.03em;
    }
    [data-testid="stMetricValue"] > div {
        font-size: 1.55rem !important; color: #ffffff !important; font-weight: 700;
    }
    [data-testid="stMetricDelta"] > div { font-size: 0.9rem !important; font-weight: 600; }

    /* EMA 數值列 */
    .ema-bar {
        background: #151825; border-radius: 8px; padding: 9px 14px;
        margin: 6px 0 8px 0; display: flex; flex-wrap: wrap;
        gap: 12px; border: 1px solid #252840;
    }
    .ema-item { font-size: 0.9rem; font-weight: 600; white-space: nowrap; }
    .ema-label { opacity: 0.7; font-size: 0.78rem; }

    /* 趨勢卡片 */
    .trend-card {
        background: #1e2235; border-radius: 10px;
        padding: 12px 14px; border: 1px solid #2e3456; text-align: center;
    }
    .trend-title { font-size: 0.9rem; color: #aab4cc; font-weight: 600; margin-bottom: 4px; }
    .trend-bull  { color: #00ee66; font-weight: 800; font-size: 1.45rem; }
    .trend-bear  { color: #ff4455; font-weight: 800; font-size: 1.45rem; }
    .trend-side  { color: #ffcc00; font-weight: 800; font-size: 1.45rem; }

    /* 多週期摘要列 */
    .mtf-header {
        background: #151825; border-radius: 10px; padding: 10px 16px;
        margin: 4px 0; border: 1px solid #252840;
        display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
    }
    .mtf-period { font-size: 0.85rem; color: #aab4cc; font-weight: 700; min-width: 52px; }
    .mtf-price  { font-size: 1.05rem; color: #ffffff; font-weight: 700; }
    .mtf-chg-up { font-size: 0.88rem; color: #00ee66; font-weight: 600; }
    .mtf-chg-dn { font-size: 0.88rem; color: #ff4455; font-weight: 600; }
    .mtf-trend-bull { background:#0d2e18; color:#00ee66; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-trend-bear { background:#2e0d0d; color:#ff4455; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-trend-side { background:#28260d; color:#ffcc00; border-radius:4px; padding:2px 8px; font-size:0.82rem; font-weight:700; }
    .mtf-macd-bull  { color:#00ee66; font-size:0.82rem; }
    .mtf-macd-bear  { color:#ff4455; font-size:0.82rem; }
    .mtf-ema-bull   { color:#00ee66; font-size:0.82rem; }
    .mtf-ema-bear   { color:#ff4455; font-size:0.82rem; }
    .mtf-divider    { height:28px; width:1px; background:#2e3456; flex-shrink:0; }

    /* 區塊標題 */
    .mtf-section-title {
        font-size: 1.1rem; font-weight: 700; color: #ddeeff;
        padding: 8px 0 4px 0; border-bottom: 2px solid #2e3456;
        margin: 14px 0 8px 0;
    }

    /* 警示面板 */
    .alert-box {
        padding: 11px 16px; border-radius: 8px; margin: 4px 0;
        font-size: 0.92rem; font-weight: 500; line-height: 1.5;
    }
    .alert-bull { background:#0d2e18; border-left:5px solid #00ee66; color:#88ffbb; }
    .alert-bear { background:#2e0d0d; border-left:5px solid #ff4455; color:#ffaaaa; }
    .alert-vol  { background:#0d1e38; border-left:5px solid #44aaff; color:#aaddff; }
    .alert-info { background:#28260d; border-left:5px solid #ffcc00; color:#fff0aa; }

    /* 市場環境面板 */
    .mkt-panel {
        background: #12151f; border-radius: 12px; padding: 14px 18px;
        border: 1px solid #2a2e48; margin-bottom: 10px;
    }
    .mkt-title {
        font-size: 1rem; font-weight: 700; color: #99aacc;
        letter-spacing: 0.05em; margin-bottom: 10px;
        border-bottom: 1px solid #2a2e48; padding-bottom: 6px;
    }
    .mkt-row { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:6px; }
    .mkt-card {
        background:#1a1e2e; border-radius:8px; padding:8px 14px;
        border:1px solid #252840; flex:1; min-width:100px; text-align:center;
    }
    .mkt-card-label { font-size:0.72rem; color:#7788aa; margin-bottom:2px; }
    .mkt-card-val   { font-size:1.05rem; font-weight:700; color:#eef2ff; }
    .mkt-card-chg-up { font-size:0.78rem; color:#00ee66; }
    .mkt-card-chg-dn { font-size:0.78rem; color:#ff4455; }
    .mkt-card-neu    { font-size:0.78rem; color:#ffcc00; }

    /* VIX 壓力計 */
    .vix-bar-bg  { background:#1a1e2e; border-radius:6px; height:10px; margin:4px 0; overflow:hidden; }
    .vix-bar-fill{ height:100%; border-radius:6px; transition:width 0.4s; }

    /* 情緒儀表 */
    .sentiment-meter {
        display:flex; align-items:center; gap:8px; margin:6px 0;
    }
    .sentiment-label { font-size:0.78rem; color:#7788aa; min-width:52px; }
    .sentiment-bar-bg { flex:1; background:#1a1e2e; border-radius:4px; height:8px; overflow:hidden; }
    .sentiment-bar-fill { height:100%; border-radius:4px; }
    .sentiment-val { font-size:0.78rem; font-weight:700; min-width:40px; text-align:right; }

    /* 新聞條目 */
    .news-item {
        padding: 8px 12px; background:#141824; border-radius:7px;
        margin:4px 0; border-left:3px solid #2a3060;
        font-size:0.82rem; line-height:1.5;
    }
    .news-item:hover { border-left-color:#4466cc; background:#171d2e; }
    .news-src  { font-size:0.7rem; color:#556688; margin-top:2px; }
    .news-bull { border-left-color:#00cc55; }
    .news-bear { border-left-color:#cc3344; }
    .news-neu  { border-left-color:#446688; }

    /* AI 分析面板 */
    .ai-panel {
        background: linear-gradient(135deg, #0e1525 0%, #111e35 100%);
        border-radius: 12px; padding: 20px 22px;
        border: 1px solid #1e3a5f; margin: 12px 0;
        box-shadow: 0 4px 20px rgba(0,100,255,0.08);
    }
    .ai-title {
        font-size: 1.05rem; font-weight: 700; color: #66aaff;
        letter-spacing: 0.04em; margin-bottom: 14px;
        display: flex; align-items: center; gap: 8px;
    }
    .ai-section { margin: 12px 0; }
    .ai-section-title {
        font-size: 0.78rem; font-weight: 700; color: #5577aa;
        text-transform: uppercase; letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .ai-verdict {
        font-size: 1.1rem; font-weight: 800; padding: 8px 16px;
        border-radius: 8px; display: inline-block; margin-bottom: 10px;
    }
    .ai-verdict-bull { background:#0d2e18; color:#00ee66; border:1px solid #00aa44; }
    .ai-verdict-bear { background:#2e0d0d; color:#ff5566; border:1px solid #aa2233; }
    .ai-verdict-side { background:#28260d; color:#ffcc00; border:1px solid #aa9900; }
    .ai-price-row {
        display: flex; gap: 10px; flex-wrap: wrap; margin: 8px 0;
    }
    .ai-price-card {
        background: #141c2e; border-radius: 8px; padding: 10px 14px;
        border: 1px solid #1e2e48; flex: 1; min-width: 100px; text-align:center;
    }
    .ai-price-label { font-size: 0.72rem; color: #5577aa; margin-bottom: 4px; }
    .ai-price-val   { font-size: 1.1rem; font-weight: 700; }
    .ai-price-entry { color: #44aaff; }
    .ai-price-tp    { color: #00ee66; }
    .ai-price-sl    { color: #ff5566; }
    .ai-price-rr    { color: #ffcc00; }
    .ai-reasoning {
        font-size: 0.88rem; color: #99aacc; line-height: 1.7;
        background: #0c1220; border-radius: 8px; padding: 12px 14px;
        border-left: 3px solid #2244aa;
    }
    .ai-risk-warning {
        font-size: 0.75rem; color: #445566; margin-top: 10px;
        padding: 6px 10px; border-radius: 4px; background: #0a0e18;
    }
    .ai-loading {
        text-align: center; padding: 30px;
        color: #4466aa; font-size: 0.9rem;
    }
    @keyframes ai-pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .ai-loading-dot { animation: ai-pulse 1.2s infinite; }

    /* 延長時段面板 */
    .ext-panel {
        background:#0e1020; border-radius:12px; padding:16px 18px;
        border:1px solid #1e2040; margin:10px 0;
    }
    .ext-title {
        font-size:1rem; font-weight:700; color:#88aadd;
        letter-spacing:0.04em; margin-bottom:12px;
        display:flex; align-items:center; gap:8px;
    }
    .ext-toggle-row {
        display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px; align-items:center;
    }
    /* iOS 風格 toggle */
    .ext-toggle {
        display:inline-flex; align-items:center; gap:8px;
        background:#141c2e; border:1px solid #2a3050;
        border-radius:20px; padding:5px 12px 5px 6px;
        cursor:pointer; user-select:none; font-size:0.82rem; color:#7799bb;
        transition:all 0.2s;
    }
    .ext-toggle.active {
        background:#0d2040; border-color:#3366aa; color:#66aaff;
    }
    .ext-toggle-dot {
        width:18px; height:18px; border-radius:50%; background:#334466;
        display:inline-block; transition:background 0.2s;
    }
    .ext-toggle.active .ext-toggle-dot { background:#4488ff; }
    /* 時段標籤 */
    .ext-session-tag {
        display:inline-block; font-size:0.72rem; font-weight:700;
        padding:2px 8px; border-radius:10px; margin-right:4px;
    }
    .ext-tag-pre  { background:#0d2040; color:#44aaff; border:1px solid #224488; }
    .ext-tag-post { background:#1a1040; color:#aa88ff; border:1px solid #442288; }
    .ext-tag-night{ background:#001830; color:#00ccff; border:1px solid #004466; }
    /* 延長時段摘要卡片 */
    .ext-stat-row { display:flex; gap:8px; flex-wrap:wrap; margin:10px 0; }
    .ext-stat-card {
        flex:1; min-width:90px; background:#141c2e; border-radius:8px;
        padding:8px 12px; border:1px solid #1e2e48; text-align:center;
    }
    .ext-stat-label { font-size:0.7rem; color:#5577aa; margin-bottom:3px; }
    .ext-stat-val   { font-size:1rem; font-weight:700; color:#ccd6ee; }
    .ext-stat-chg-up{ font-size:0.75rem; color:#00ee66; }
    .ext-stat-chg-dn{ font-size:0.75rem; color:#ff5566; }

    /* 社群情緒面板 */
    .social-panel {
        background:#0e1525; border-radius:12px; padding:16px 18px;
        border:1px solid #1e2e48; margin:8px 0;
    }
    .social-title {
        font-size:0.92rem; font-weight:700; color:#7799cc;
        letter-spacing:0.04em; margin-bottom:12px;
        display:flex; align-items:center; gap:6px;
    }
    /* 情緒大錶盤 */
    .social-gauge {
        display:flex; align-items:center; gap:16px; margin-bottom:12px;
    }
    .social-score-circle {
        width:72px; height:72px; border-radius:50%;
        display:flex; flex-direction:column; align-items:center;
        justify-content:center; font-weight:800; flex-shrink:0;
        border:3px solid;
    }
    .social-score-num  { font-size:1.4rem; line-height:1; }
    .social-score-lbl  { font-size:0.62rem; opacity:0.8; margin-top:2px; }
    .social-bull-bear  { flex:1; }
    .social-bb-row     { display:flex; align-items:center; gap:6px; margin:4px 0; }
    .social-bb-label   { font-size:0.72rem; color:#5577aa; min-width:34px; }
    .social-bb-bar     { flex:1; background:#141c2e; border-radius:4px; height:7px; overflow:hidden; }
    .social-bb-fill    { height:100%; border-radius:4px; }
    .social-bb-val     { font-size:0.72rem; font-weight:700; min-width:36px; text-align:right; }
    /* 推文列表 */
    .social-tweet {
        padding:8px 10px; background:#111828; border-radius:7px;
        margin:4px 0; border-left:3px solid #1e3060; font-size:0.8rem;
        line-height:1.5; color:#99aacc;
    }
    .social-tweet-bull { border-left-color:#00aa44; }
    .social-tweet-bear { border-left-color:#cc3344; }
    .social-tweet-meta { font-size:0.68rem; color:#334466; margin-top:3px;
                         display:flex; gap:8px; }
    .social-stat-row   { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px; }
    .social-stat       { background:#141c2e; border-radius:6px; padding:5px 10px;
                         font-size:0.78rem; color:#7799bb; border:1px solid #1e2e48; }
    .social-stat b     { color:#aabbdd; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 常數
# ══════════════════════════════════════════════════════════════════════════════
INTERVAL_MAP = {
    "1m":  ("1分鐘",  "1d"),
    "5m":  ("5分鐘",  "5d"),
    "15m": ("15分鐘", "10d"),
    "30m": ("30分鐘", "30d"),
    "1d":  ("日K",    "1y"),
    "1wk": ("週K",    "3y"),
    "1mo": ("月K",    "5y"),
}
ALL_INTERVALS   = list(INTERVAL_MAP.keys())
INTERVAL_LABELS = {k: v[0] for k, v in INTERVAL_MAP.items()}

EMA_CONFIGS = [
    (5,   "#00ff88"), (10,  "#ccff00"), (20,  "#ffaa00"),
    (30,  "#ff5500"), (40,  "#cc00ff"), (60,  "#0088ff"),
    (120, "#00ccff"), (200, "#8866ff"),
]
MA_CONFIGS = [(5, "#ffffff", "dash"), (15, "#ffdd66", "dot")]

# ══════════════════════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════════════════════
if "alert_log"    not in st.session_state: st.session_state.alert_log    = []
if "sent_alerts"  not in st.session_state: st.session_state.sent_alerts  = set()

# ── 交易日誌系統 Session State ───────────────────────────────────────────────
if "trade_log"          not in st.session_state: st.session_state.trade_log          = []
if "calc_log"           not in st.session_state: st.session_state.calc_log           = []
if "decision_log"       not in st.session_state: st.session_state.decision_log       = []
if "open_trades"        not in st.session_state: st.session_state.open_trades        = {}
if "trade_id_counter"   not in st.session_state: st.session_state.trade_id_counter   = 1
if "psych_log"          not in st.session_state: st.session_state.psych_log          = []
# ── 系統建議交易 Session State ──────────────────────────────────────────────
if "trade_suggestions"  not in st.session_state: st.session_state.trade_suggestions  = []
if "sent_suggestions"   not in st.session_state: st.session_state.sent_suggestions   = set()
# ── 進場時機追蹤 Session State（日K信號 → 30分鐘精確進場）───────────────────
if "entry_trackers"     not in st.session_state: st.session_state.entry_trackers     = []
# {symbol, direction, trigger_signal, trigger_price, trigger_time, status, period_src}

# ══════════════════════════════════════════════════════════════════════════════
# 市場環境數據
# ══════════════════════════════════════════════════════════════════════════════

# 大盤指數代號
MARKET_TICKERS = {
    "SPY":  ("標普500 ETF", "spy"),
    "QQQ":  ("那斯達克ETF", "qqq"),
    "DIA":  ("道瓊ETF",     "dia"),
    "^VIX": ("VIX恐慌指數", "vix"),
    "^TNX": ("10年期美債", "tnx"),
    "GLD":  ("黃金ETF",     "gld"),
    "UUP":  ("美元指數ETF", "uup"),
}

@st.cache_data(ttl=120)
def fetch_market_data() -> dict:
    """抓取大盤環境數據，快取 2 分鐘"""
    result = {}
    for ticker, (name, key) in MARKET_TICKERS.items():
        try:
            t  = yf.Ticker(ticker)
            df = t.history(period="5d", interval="1d", auto_adjust=True)
            if df.empty:
                # fallback: try download
                df = yf.download(ticker, period="5d", interval="1d",
                                 auto_adjust=True, progress=False)
                if df.empty:
                    continue
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            # normalize columns
            df.columns = [str(c[0]).strip() if isinstance(c, tuple) else str(c).strip()
                          for c in df.columns]
            if "Close" not in df.columns:
                continue
            last  = float(df["Close"].dropna().iloc[-1])
            prev  = float(df["Close"].dropna().iloc[-2]) if len(df["Close"].dropna()) > 1 else last
            chg   = last - prev
            pct   = chg / prev * 100 if prev else 0
            result[key] = {"name": name, "ticker": ticker,
                           "last": last, "chg": chg, "pct": pct}
        except Exception:
            pass
    return result

@st.cache_data(ttl=120)
@st.cache_data(ttl=3600)
def fetch_vix_history() -> pd.Series:
    """VIX 近 1 年歷史，用於趨勢判斷 & Q2百分位計算（TTL=1小時，日K不需頻繁刷新）"""
    try:
        df = yf.download("^VIX", period="1y", interval="1d",
                         auto_adjust=True, progress=False)
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df["Close"].dropna()
    except Exception:
        return pd.Series(dtype=float)

@st.cache_data(ttl=60)   # 縮短至 60 秒，確保數據更新更即時
def fetch_vix_intraday() -> dict:
    """
    抓取 VIX 盤中即時數據（1分鐘K線），
    計算：當日漲跌幅、近期方向動量、與前日收盤比較。
    """
    result = {
        "spot": None, "open_today": None,
        "chg_from_open": 0, "chg_pct_from_open": 0,
        "chg_from_prev": 0, "chg_pct_from_prev": 0,
        "trend_5bar": "flat",
        "trend_label": "→平穩",
        "last_bar_time": "",    # 最新一根K線的時間（用於診斷）
        "signal": 0,
        "signal_label": "",
        "signal_color": "#888888",
        "bars": None,
        "error": None,
    }
    try:
        res = _yahoo_chart_api("^VIX", "1m", "5d")
        if res["error"] or res["df"] is None:
            result["error"] = res.get("error", "VIX 數據失敗")
            return result

        df = res["df"].dropna()
        if df.empty:
            result["error"] = "VIX 無數據"
            return result

        # 轉換到 ET 時區
        try:
            import pytz as _ptz
            _et = _ptz.timezone("America/New_York")
            if df.index.tzinfo is None:
                df = df.tz_localize("UTC").tz_convert(_et)
            else:
                df = df.tz_convert(_et)
        except Exception:
            pass

        spot = float(df["Close"].iloc[-1])
        result["spot"] = spot
        result["bars"] = df

        # 記錄最新一根時間（供 UI 診斷顯示）
        try:
            result["last_bar_time"] = df.index[-1].strftime("%m/%d %H:%M ET")
        except Exception:
            result["last_bar_time"] = ""

        # 前一交易日收盤：取最後一根「正規盤收盤時段（15:55-16:00）」的數據
        # 不依賴 date() 比較，改用小時判斷，避免盤後/盤前 date 相同問題
        try:
            # 找正規盤的所有K線（09:30-16:00 ET）
            _h = df.index.hour
            _m = df.index.minute
            reg_mask = (
                ((_h > 9) | ((_h == 9) & (_m >= 30))) &
                (_h < 16)
            )
            reg_bars = df[reg_mask]
            if len(reg_bars) >= 2:
                # 最後一個正規盤 session 結束的收盤（前一日）
                last_reg_date = reg_bars.index[-1].date()
                prev_reg_bars = reg_bars[reg_bars.index.map(lambda t: t.date()) < last_reg_date]
                if not prev_reg_bars.empty:
                    prev_close = float(prev_reg_bars["Close"].iloc[-1])
                else:
                    # 當天是第一個正規盤 session，用開盤前第一根作為參考
                    prev_close = float(reg_bars["Close"].iloc[0])
                # 當日收盤（最後一根正規盤）
                today_reg_close = float(reg_bars["Close"].iloc[-1])
                result["chg_from_prev"]     = today_reg_close - prev_close
                result["chg_pct_from_prev"] = (today_reg_close - prev_close) / prev_close * 100
                # spot 可能是盤後價，用 spot 對比前日正規盤收盤
                result["chg_from_prev"]     = spot - prev_close
                result["chg_pct_from_prev"] = (spot - prev_close) / prev_close * 100
        except Exception:
            # fallback：用 date 比較
            today = df.index[-1].date()
            prev_bars_fb = df[df.index.map(lambda t: t.date()) < today]
            if not prev_bars_fb.empty:
                prev_close = float(prev_bars_fb["Close"].iloc[-1])
                result["chg_from_prev"]     = spot - prev_close
                result["chg_pct_from_prev"] = (spot - prev_close) / prev_close * 100

        # 今日開盤（今日第一根正規盤K線）
        try:
            today_date = df.index[-1].date()
            today_bars = df[df.index.map(lambda t: t.date()) == today_date]
            if not today_bars.empty:
                open_today = float(today_bars["Open"].iloc[0])
                result["open_today"]        = open_today
                result["chg_from_open"]     = spot - open_today
                result["chg_pct_from_open"] = (spot - open_today) / open_today * 100
        except Exception:
            pass

        # 近15根1分鐘K線方向動量（= 約15分鐘趨勢）
        if len(df) >= 15:
            last_n = df["Close"].iloc[-15:]
            slope = (float(last_n.iloc[-1]) - float(last_n.iloc[0])) / float(last_n.iloc[0]) * 100
            if slope > 0.8:
                result["trend_5bar"] = "up"
            elif slope < -0.8:
                result["trend_5bar"] = "down"
            else:
                result["trend_5bar"] = "flat"

        result["trend_label"] = {"up": "↑上升中", "down": "↓下降中", "flat": "→平穩"}[result["trend_5bar"]]

        # 綜合訊號：VIX漲→股市空，VIX跌→股市多
        pct = result["chg_pct_from_prev"]
        t5  = result["trend_5bar"]
        if pct > 15 or (pct > 8 and t5 == "up"):
            sig, lbl, col = -4, f"🚨 VIX暴升 {pct:+.1f}% → 極度恐慌，強力看空", "#ff2222"
        elif pct > 5 or (pct > 2 and t5 == "up"):
            sig, lbl, col = -2, f"🔴 VIX上升 {pct:+.1f}% → 恐慌升溫，偏空", "#ff6644"
        elif pct > 0 and t5 == "flat":
            sig, lbl, col = -1, f"🟡 VIX微升 {pct:+.1f}%，輕微壓力", "#ffaa44"
        elif pct < -10 or (pct < -5 and t5 == "down"):
            sig, lbl, col = +3, f"🟢 VIX急跌 {pct:+.1f}% → 恐慌消退，強力看多", "#00ee66"
        elif pct < -2 or t5 == "down":
            sig, lbl, col = +2, f"🟢 VIX下降 {pct:+.1f}% → 市場偏多", "#44cc88"
        else:
            sig, lbl, col = 0, f"⚪ VIX平穩 {pct:+.1f}%，市場中性", "#888888"

        result["signal"]       = sig
        result["signal_label"] = lbl
        result["signal_color"] = col

    except Exception as e:
        result["error"] = str(e)

    return result


@st.cache_data(ttl=120)
def fetch_vix_term_structure() -> dict:
    """
    抓取 VIX 期限結構數據：
    - VIX 現貨 (^VIX)
    - VIX9D 超短期 (^VIX9D) — 9日隱含波動率
    - VIX3M 中期 (^VIX3M) — 3個月
    - VIX6M 長期 (^VIX6M) — 6個月
    期限結構類型：Contango（正向，正常）/ Backwardation（反向，恐慌）
    """
    result = {
        "spot": None, "vix9d": None, "vix3m": None, "vix6m": None,
        "structure": "unknown", "contango_pct": None,
        "panic_type": "normal", "alert_msg": None,
        "spy_1d_chg_pct": None, "vix_1d_chg_pct": 0,
        "source": "none",
    }

    def _fetch_last(ticker):
        try:
            df = yf.download(ticker, period="5d", interval="1d",
                             auto_adjust=True, progress=False)
            if df.empty:
                return None
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            return float(df["Close"].dropna().iloc[-1])
        except Exception:
            return None

    spot  = _fetch_last("^VIX")
    vix9d = _fetch_last("^VIX9D")
    vix3m = _fetch_last("^VIX3M")
    vix6m = _fetch_last("^VIX6M")
    spy   = _fetch_last("SPY")

    result["spot"]  = spot
    result["vix9d"] = vix9d
    result["vix3m"] = vix3m
    result["vix6m"] = vix6m

    # VIX 當日漲跌幅（日K）
    try:
        vix_series = fetch_vix_history()
        if len(vix_series) >= 2:
            vix_1d_chg_pct = float((vix_series.iloc[-1] - vix_series.iloc[-2])
                                   / vix_series.iloc[-2] * 100)
        else:
            vix_1d_chg_pct = 0
    except Exception:
        vix_1d_chg_pct = 0
    result["vix_1d_chg_pct"] = vix_1d_chg_pct

    # SPY 當日漲跌幅
    try:
        spy_df = yf.download("SPY", period="5d", interval="1d",
                             auto_adjust=True, progress=False)
        spy_df.columns = [c[0] if isinstance(c, tuple) else c for c in spy_df.columns]
        spy_s = spy_df["Close"].dropna()
        spy_1d_chg_pct = float((spy_s.iloc[-1] - spy_s.iloc[-2]) / spy_s.iloc[-2] * 100) if len(spy_s) >= 2 else 0
    except Exception:
        spy_1d_chg_pct = 0
    result["spy_1d_chg_pct"] = spy_1d_chg_pct

    vix_spike  = vix_1d_chg_pct > 15

    # 期限結構判斷（用 VIX vs VIX3M）
    if spot and vix3m:
        if spot > vix3m * 1.05:
            result["structure"]    = "Backwardation"
            result["contango_pct"] = (spot - vix3m) / vix3m * 100
            result["panic_type"]   = "systemic"
            if vix_spike and spy_1d_chg_pct < -2:
                result["alert_msg"] = (
                    f"🚨 VIX 暴升 +{vix_1d_chg_pct:.1f}% 且 SPY 重跌 {spy_1d_chg_pct:+.1f}%"
                    f"，期限結構反轉（Backwardation），系統性風險警報！"
                )
            elif vix_spike:
                result["alert_msg"] = (
                    f"🟡 短期恐慌底訊號｜VIX 暴升+{vix_1d_chg_pct:.0f}% 但結構 Contango，非系統風險"
                )
        elif spot < vix3m * 0.95:
            result["structure"]    = "Contango"
            result["contango_pct"] = (vix3m - spot) / spot * 100
            result["panic_type"]   = "short_term_fear" if vix_spike else "normal"
            if vix_spike:
                result["alert_msg"] = (
                    f"📊 VIX 暴升 +{vix_1d_chg_pct:.1f}% 但 SPY 跌幅有限 ({spy_1d_chg_pct:+.1f}%)"
                    f"，Contango 結構完整，可能是短期恐慌底"
                )
        else:
            result["structure"]    = "Flat"
            result["contango_pct"] = 0
            result["panic_type"]   = "normal"

    result["source"] = "yfinance"
    return result


def get_vix_regime(vix: float) -> tuple:
    """回傳 (狀態描述, 顏色, 條寬%) """
    if vix < 13:   return ("超低波動 😴",  "#00ee66", 10)
    if vix < 18:   return ("低波動 ✅",     "#88ff44", 25)
    if vix < 25:   return ("正常範圍 🟡",  "#ffcc00", 45)
    if vix < 30:   return ("偏高警戒 🟠",  "#ff8800", 62)
    if vix < 40:   return ("恐慌模式 🔴",  "#ff4444", 78)
    return             ("極度恐慌 💀",    "#cc0000", 95)

@st.cache_data(ttl=300)
def fetch_news(max_items: int = 8) -> list:
    """
    多來源財經新聞抓取：
    1. Google News RSS（最可靠，免費）
    2. MarketWatch RSS fallback
    回傳 list of dict: {title, link, date, sentiment}
    """
    import re, html as html_lib

    FEEDS = [
        ("Google Finance News",
         "https://news.google.com/rss/search?q=stock+market+wall+street&hl=en-US&gl=US&ceid=US:en"),
        ("Google Economy News",
         "https://news.google.com/rss/search?q=fed+interest+rate+inflation+nasdaq&hl=en-US&gl=US&ceid=US:en"),
        ("MarketWatch",
         "https://feeds.content.dowjones.io/public/rss/mw_marketpulse"),
    ]
    BEAR_KW = ["crash","fall","drop","decline","slump","fear","recession","selloff",
               "inflation","rate hike","sell-off","warning","risk","loss","tumble",
               "plunge","weak","concern","worry","tariff","yield surge"]
    BULL_KW = ["rally","surge","gain","rise","record","growth","beat","strong",
               "upgrade","buy","bull","positive","profit","rebound","recover",
               "outperform","soar","climb","boost","optimism"]

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36"}
    items = []

    for src_name, feed_url in FEEDS:
        if len(items) >= max_items:
            break
        try:
            resp = requests.get(feed_url, timeout=8, headers=headers)
            if resp.status_code != 200:
                continue
            text = resp.text

            # Parse <item> blocks
            item_blocks = re.findall(r"<item>(.*?)</item>", text, re.DOTALL)
            for block in item_blocks:
                if len(items) >= max_items:
                    break
                # Title
                t_match = re.search(r"<title>(.*?)</title>", block, re.DOTALL)
                if not t_match:
                    continue
                title = t_match.group(1)
                title = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"", title)
                title = re.sub(r"<[^>]+>", "", title)
                title = html_lib.unescape(title).strip()
                if not title or len(title) < 10:
                    continue

                # Link
                l_match = re.search(r"<link>(.*?)</link>", block)
                if not l_match:
                    l_match = re.search(r"<guid[^>]*>(.*?)</guid>", block)
                link = l_match.group(1).strip() if l_match else "#"

                # Date
                d_match = re.search(r"<pubDate>(.*?)</pubDate>", block)
                raw_date = d_match.group(1).strip() if d_match else ""
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(raw_date)
                    date_str = dt.strftime("%m/%d %H:%M")
                except Exception:
                    date_str = raw_date[:16]

                # Sentiment
                tl = title.lower()
                if   any(w in tl for w in BEAR_KW): sentiment = "bear"
                elif any(w in tl for w in BULL_KW): sentiment = "bull"
                else:                                sentiment = "neu"

                items.append({
                    "title": title, "link": link,
                    "date": date_str, "sentiment": sentiment,
                    "source": src_name,
                })
        except Exception:
            continue

    return items

def calc_sentiment_score(mkt: dict, vix_hist: pd.Series) -> dict:
    """
    綜合情緒分數計算（0-100，50為中性）
    組成：
      40% VIX 壓力（VIX 低 → 分數高）
      30% SPY 動能（近5日漲跌）
      30% QQQ 動能
    """
    score = 50.0  # 預設中性

    # VIX 分量（反向：VIX 越高 → 越恐慌 → 分數越低）
    vix_now = mkt.get("vix", {}).get("last", 20)
    if vix_now:
        vix_score = max(0, min(100, 100 - (vix_now - 10) * 3.5))
        score = score * 0.6 + vix_score * 0.4

    # SPY 動能分量
    spy = mkt.get("spy", {})
    if spy:
        spy_score = 50 + spy.get("pct", 0) * 8
        spy_score = max(0, min(100, spy_score))
        score = score * 0.7 + spy_score * 0.3

    # QQQ 動能分量
    qqq = mkt.get("qqq", {})
    if qqq:
        qqq_score = 50 + qqq.get("pct", 0) * 8
        qqq_score = max(0, min(100, qqq_score))
        score = score * 0.7 + qqq_score * 0.3

    # VIX 趨勢加減分
    if len(vix_hist) >= 5:
        vix_5d_chg = float(vix_hist.iloc[-1] - vix_hist.iloc[-5])
        score += -vix_5d_chg * 1.2  # VIX 5日上升 → 扣分

    score = max(0, min(100, score))

    if score >= 70:   label, color = "貪婪 🤑",    "#00ee66"
    elif score >= 55: label, color = "樂觀 😊",    "#88ff44"
    elif score >= 45: label, color = "中性 😐",    "#ffcc00"
    elif score >= 30: label, color = "悲觀 😟",    "#ff8800"
    else:             label, color = "極度恐慌 😱", "#ff4444"

    return {"score": round(score, 1), "label": label, "color": color}

def render_market_environment():
    """渲染市場環境面板（大盤 + VIX + 情緒 + 新聞）"""
    st.markdown("---")
    st.subheader("🌐 市場環境總覽")

    mkt      = fetch_market_data()
    vix_hist = fetch_vix_history()
    vix_term = fetch_vix_term_structure()

    # ── 第一行：大盤指數卡片 ─────────────────────────────────────────────
    card_keys = ["spy", "qqq", "dia", "gld", "uup", "tnx"]
    card_cols = st.columns(len(card_keys))
    for col, key in zip(card_cols, card_keys):
        d = mkt.get(key)
        with col:
            if not d:
                st.metric(key.upper(), "N/A")
                continue
            chg_str = f"{d['chg']:+.2f} ({d['pct']:+.2f}%)"
            st.metric(d["name"], f"{d['last']:.2f}", chg_str)

    st.markdown("")

    # ── 第二行：VIX 壓力計 + 情緒儀表 ──────────────────────────────────
    col_vix, col_sent, col_news_hd = st.columns([1, 1, 2])

    with col_vix:
        vix_d = mkt.get("vix", {})
        vix_now = vix_d.get("last", 20)
        vix_chg = vix_d.get("pct", 0)
        regime, bar_color, bar_pct = get_vix_regime(vix_now)

        st.markdown(f"""
        <div class="mkt-panel">
          <div class="mkt-title">😨 VIX 恐慌指數</div>
          <div style="font-size:2rem;font-weight:800;color:{'#ff4444' if vix_now>25 else '#ffcc00' if vix_now>18 else '#00ee66'}">
            {vix_now:.2f}
            <span style="font-size:0.85rem;color:{'#ff4455' if vix_chg>0 else '#00ee66'}">
              {'▲' if vix_chg>0 else '▼'} {abs(vix_chg):.2f}%
            </span>
          </div>
          <div class="vix-bar-bg">
            <div class="vix-bar-fill" style="width:{bar_pct}%;background:{bar_color};"></div>
          </div>
          <div style="font-size:0.85rem;color:{bar_color};margin-top:4px;">{regime}</div>
          <div style="font-size:0.72rem;color:#556688;margin-top:6px;">
            &lt;18 正常　18-25 警戒　&gt;30 恐慌
          </div>
        </div>
        """, unsafe_allow_html=True)

        # VIX 近期走勢迷你圖
        if len(vix_hist) >= 5:
            vix_fig = go.Figure(go.Scatter(
                y=vix_hist.values, mode="lines+markers",
                line=dict(color=bar_color, width=2),
                marker=dict(size=4),
                fill="tozeroy", fillcolor=f"rgba(255,100,100,0.08)",
            ))
            vix_fig.update_layout(
                height=100, margin=dict(l=0,r=0,t=0,b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, xaxis=dict(visible=False),
                yaxis=dict(showgrid=False, tickfont=dict(size=9, color="#556688")),
            )
            st.plotly_chart(vix_fig, use_container_width=True,
                            config={"displayModeBar": False}, key="vix_mini")

    with col_sent:
        sent = calc_sentiment_score(mkt, vix_hist)
        sc   = sent["score"]
        sc_color = sent["color"]

        # 各分項指標
        indicators = []
        if mkt.get("spy"):
            pct = mkt["spy"]["pct"]
            indicators.append(("SPY 動能", 50 + pct*8, "#4488ff"))
        if mkt.get("qqq"):
            pct = mkt["qqq"]["pct"]
            indicators.append(("QQQ 動能", 50 + pct*8, "#aa44ff"))
        vix_comp = max(0, min(100, 100-(vix_now-10)*3.5)) if vix_now else 50
        indicators.append(("VIX 壓力", vix_comp, "#ff8844"))
        if mkt.get("tnx"):
            tnx_pct = mkt["tnx"]["pct"]
            bond_score = max(0, min(100, 50 - tnx_pct*6))
            indicators.append(("債券安全", bond_score, "#44ccff"))

        # 建立情緒分項 HTML（不使用縮排，避免 Streamlit 把空白當 code block）
        meter_parts = []
        for ind_name, ind_val, ind_color in indicators:
            ind_val = max(0, min(100, ind_val))
            meter_parts.append(
                f'<div class="sentiment-meter">'
                f'<span class="sentiment-label">{ind_name}</span>'
                f'<div class="sentiment-bar-bg">'
                f'<div class="sentiment-bar-fill" style="width:{ind_val:.0f}%;background:{ind_color};"></div>'
                f'</div>'
                f'<span class="sentiment-val" style="color:{ind_color}">{ind_val:.0f}</span>'
                f'</div>'
            )
        meter_rows = "".join(meter_parts)

        gradient = "linear-gradient(90deg,#ff4444 0%,#ffcc00 50%,#00ee66 100%)"
        sent_html = (
            f'<div class="mkt-panel">'
            f'<div class="mkt-title">🧠 投資人情緒指數</div>'
            f'<div style="font-size:1.8rem;font-weight:800;color:{sc_color};margin-bottom:4px;">'
            f'{sc:.0f} <span style="font-size:0.9rem">{sent["label"]}</span>'
            f'</div>'
            f'<div class="vix-bar-bg" style="height:12px;margin-bottom:10px;">'
            f'<div class="vix-bar-fill" style="width:{sc:.0f}%;background:{gradient};"></div>'
            f'</div>'
            f'{meter_rows}'
            f'<div style="font-size:0.68rem;color:#445566;margin-top:6px;">'
            f'綜合 VIX壓力(40%) + SPY動能(30%) + QQQ動能(30%)'
            f'</div>'
            f'</div>'
        )
        st.markdown(sent_html, unsafe_allow_html=True)

    with col_news_hd:
        news = fetch_news()
        icons = {"bull": "🟢", "bear": "🔴", "neu": "⚪"}
        if news:
            news_parts = ['<div class="mkt-panel"><div class="mkt-title">📰 即時財經新聞</div>']
            for n in news:
                icon = icons.get(n["sentiment"], "⚪")
                cls  = "news-" + n["sentiment"]
                src  = n.get("source", "")
                news_parts.append(
                    f'<div class="news-item {cls}">'
                    f'{icon} <a href="{n["link"]}" target="_blank" '
                    f'style="color:#ccd6ee;text-decoration:none;">{n["title"]}</a>'
                    f'<div class="news-src">{n["date"]}　{src}</div>'
                    f'</div>'
                )
            news_parts.append('</div>')
            st.markdown("".join(news_parts), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="mkt-panel">'
                '<div class="mkt-title">📰 即時財經新聞</div>'
                '<div style="color:#556688;font-size:0.85rem;padding:8px 0;">'
                '⚠️ 新聞暫時無法載入（網路限制），請稍後重試'
                '</div></div>',
                unsafe_allow_html=True
            )

    # ── VIX 期限結構分析（短期恐慌 vs 系統性風險）────────────────────────
    st.markdown("")
    spot   = vix_term.get("spot")
    vix9d  = vix_term.get("vix9d")
    vix3m  = vix_term.get("vix3m")
    vix6m  = vix_term.get("vix6m")
    struct = vix_term.get("structure", "unknown")
    ptype  = vix_term.get("panic_type", "normal")
    c_pct  = vix_term.get("contango_pct")

    struct_color = {"contango": "#00ee66", "backwardation": "#ff4444",
                    "flat": "#ffcc00", "unknown": "#778899"}.get(struct, "#778899")
    struct_label = {"contango": "Contango ✅ 遠月溢價（正常）",
                    "backwardation": "Backwardation 🚨 近月溢價（警告）",
                    "flat": "Flat ⚖️ 近平",
                    "unknown": "數據不足"}.get(struct, "—")
    ptype_color  = {"short_term": "#ffcc00", "systemic": "#ff4444",
                    "normal": "#00ee66",     "watch": "#ff8800"}.get(ptype, "#778899")
    ptype_label  = {"short_term": "🟡 短期恐慌底（可能反彈）",
                    "systemic":   "🔴 系統性風險（中期調整）",
                    "normal":     "🟢 市場正常",
                    "watch":      "🟠 觀察中"}.get(ptype, "—")

    def _fmt(v): return f"{v:.2f}" if v is not None else "N/A"

    # Build term structure bar chart data
    ts_points = []
    if vix9d:  ts_points.append(("VIX9D\n超短期", vix9d))
    if spot:   ts_points.append(("VIX\n現貨", spot))
    if vix3m:  ts_points.append(("VIX3M\n3個月", vix3m))
    if vix6m:  ts_points.append(("VIX6M\n6個月", vix6m))

    term_cols = st.columns([2, 3])

    with term_cols[0]:
        # Numeric grid
        grid_html = (
            '<div style="background:#0a0e18;border:1px solid #1e2e48;border-radius:12px;padding:14px 16px;">'
            '<div style="font-size:0.82rem;font-weight:700;color:#7799cc;margin-bottom:10px;letter-spacing:1px;">📐 VIX 期限結構</div>'
            f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">'
        )
        for lbl, val in [("VIX9D", vix9d), ("VIX 現貨", spot), ("VIX3M", vix3m), ("VIX6M", vix6m)]:
            is_high = val and val > 25
            c = "#ff4444" if is_high else "#ccd6ee"
            grid_html += (
                f'<div style="background:#0c1220;border:1px solid #1e2e48;border-radius:8px;'
                f'padding:6px 10px;text-align:center;min-width:72px;">'
                f'<div style="font-size:0.65rem;color:#556688;">{lbl}</div>'
                f'<div style="font-size:1.0rem;font-weight:800;color:{c};">{_fmt(val)}</div>'
                f'</div>'
            )
        grid_html += '</div>'
        grid_html += (
            f'<div style="margin-bottom:6px;">'
            f'<span style="font-size:0.72rem;color:#445566;">結構：</span>'
            f'<span style="font-size:0.78rem;font-weight:700;color:{struct_color};">{struct_label}</span>'
            f'</div>'
            f'<div>'
            f'<span style="font-size:0.72rem;color:#445566;">判斷：</span>'
            f'<span style="font-size:0.78rem;font-weight:700;color:{ptype_color};">{ptype_label}</span>'
            f'</div>'
        )
        if c_pct is not None:
            bar_w   = min(100, abs(c_pct) * 3)
            bar_col = "#00ee66" if c_pct > 0 else "#ff4444"
            sign    = "遠月溢價" if c_pct > 0 else "近月溢價"
            grid_html += (
                f'<div style="margin-top:10px;">'
                f'<div style="font-size:0.68rem;color:#445566;margin-bottom:3px;">'
                f'{sign} {abs(c_pct):.1f}%</div>'
                f'<div style="background:#141c2e;border-radius:3px;height:5px;">'
                f'<div style="width:{bar_w}%;background:{bar_col};height:5px;border-radius:3px;"></div>'
                f'</div></div>'
            )
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    with term_cols[1]:
        # Interpretation box + mini chart
        interp = vix_term.get("interpretation", "")
        box_col = {"short_term": "#332200", "systemic": "#330000",
                   "normal": "#002200", "watch": "#221500"}.get(ptype, "#0a0e18")
        border_col = {"short_term": "#ffcc00", "systemic": "#ff4444",
                      "normal": "#00ee66",     "watch": "#ff8800"}.get(ptype, "#1e2e48")
        st.markdown(
            f'<div style="background:{box_col};border:1px solid {border_col}55;'
            f'border-radius:12px;padding:14px 16px;font-size:0.82rem;'
            f'color:#aabbcc;line-height:1.8;">'
            f'<div style="font-size:0.75rem;color:#556688;margin-bottom:6px;letter-spacing:1px;">'
            f'📖 理論解讀</div>'
            f'{interp}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Mini term structure line chart
        if len(ts_points) >= 3:
            import plotly.graph_objects as _go
            labels = [p[0] for p in ts_points]
            values = [p[1] for p in ts_points]
            line_c = "#ff4444" if struct == "backwardation" else "#00ee66"
            ts_fig = _go.Figure(_go.Scatter(
                x=labels, y=values, mode="lines+markers+text",
                line=dict(color=line_c, width=2.5),
                marker=dict(size=8, color=line_c),
                text=[f"{v:.1f}" for v in values],
                textposition="top center",
                textfont=dict(size=10, color="#ccd6ee"),
            ))
            ts_fig.update_layout(
                height=130, margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(tickfont=dict(size=9, color="#556688"),
                           showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, visible=False),
            )
            st.plotly_chart(ts_fig, use_container_width=True,
                            config={"displayModeBar": False}, key="vix_term_chart")

    # ── 第三行：市場環境警示 ──────────────────────────────────────────────
    mkt_alerts = []
    # VIX 期限結構警示（最高優先）
    if vix_term.get("alert"):
        mkt_alerts.append((vix_term["alert_type"], vix_term["alert"]))

    if vix_now > 30:
        mkt_alerts.append(("bear", f"⚠️ VIX 極度恐慌 {vix_now:.1f}，市場波動劇烈，建議謹慎操作"))
    elif vix_now > 25:
        mkt_alerts.append(("info", f"🟠 VIX 偏高 {vix_now:.1f}，市場情緒緊張"))
    elif vix_now < 13:
        mkt_alerts.append(("bull", f"😴 VIX 超低 {vix_now:.1f}，市場過於平靜，注意突發反轉"))

    spy_d = mkt.get("spy", {})
    if spy_d and spy_d.get("pct", 0) < -2:
        mkt_alerts.append(("bear", f"📉 SPY 單日下跌 {spy_d['pct']:.2f}%，大盤走弱"))
    elif spy_d and spy_d.get("pct", 0) > 1.5:
        mkt_alerts.append(("bull", f"📈 SPY 單日上漲 {spy_d['pct']:.2f}%，大盤強勢"))

    qqq_d = mkt.get("qqq", {})
    if qqq_d and qqq_d.get("pct", 0) < -2.5:
        mkt_alerts.append(("bear", f"📉 QQQ 科技股大跌 {qqq_d['pct']:.2f}%"))

    tnx_d = mkt.get("tnx", {})
    if tnx_d and tnx_d.get("last", 0) > 4.8:
        mkt_alerts.append(("bear", f"💸 10年期美債殖利率 {tnx_d['last']:.2f}%，利率壓力大"))

    if mkt_alerts:
        alert_cls = {"bull":"alert-bull","bear":"alert-bear","info":"alert-info","vol":"alert-vol"}
        html_parts = [f'<div class="alert-box {alert_cls.get(t,"alert-info")}">🌐 市場環境　{msg}</div>'
                      for t, msg in mkt_alerts]
        st.markdown("".join(html_parts), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Social Sentiment Module (Yahoo Finance News + Reddit)
# ══════════════════════════════════════════════════════════════════════════════

BULL_KW = ["bull","buy","long","up","breakout","moon","calls","support","surge",
           "rally","gain","beat","strong","upgrade","record","growth","jump","soar"]
BEAR_KW = ["bear","sell","short","down","crash","puts","drop","dump","fall",
           "decline","miss","weak","downgrade","loss","risk","fear","slump","warn"]

def _classify(text: str) -> str:
    tl = text.lower()
    b  = sum(1 for w in BULL_KW if w in tl)
    br = sum(1 for w in BEAR_KW if w in tl)
    if b > br:   return "bull"
    if br > b:   return "bear"
    return "neu"

def _parse_yf_news_item(item):
    import html as html_lib
    from datetime import timezone, datetime as _dt
    content = item.get("content", {})
    if content and isinstance(content, dict):
        title     = html_lib.unescape(content.get("title", "")).strip()
        summary   = html_lib.unescape(content.get("summary", "")).strip()
        link      = (content.get("canonicalUrl") or {}).get("url", "#")
        publisher = (content.get("provider") or {}).get("displayName", "")
        pub_date  = content.get("pubDate", "")
        try:
            dt_str = _dt.strptime(pub_date[:16], "%Y-%m-%dT%H:%M").strftime("%m/%d %H:%M")
        except Exception:
            dt_str = pub_date[:16]
    else:
        title     = html_lib.unescape(item.get("title", "")).strip()
        summary   = html_lib.unescape(item.get("summary", "")).strip()
        link      = item.get("link", "#")
        publisher = item.get("publisher", "")
        ts        = item.get("providerPublishTime", 0)
        dt_str    = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%m/%d %H:%M") if ts else ""
    if not title:
        return None
    return {"title": title, "summary": summary[:120], "link": link,
            "publisher": publisher, "time": dt_str}


@st.cache_data(ttl=180)
def fetch_stocktwits(symbol: str) -> dict:
    import html as html_lib, re
    bull = bear = 0.0
    parsed = []

    # Source 1: yfinance Ticker.news (handles old + new format)
    try:
        raw_news = yf.Ticker(symbol).news or []
        for item in raw_news[:30]:
            p = _parse_yf_news_item(item)
            if not p:
                continue
            s = _classify(p["title"] + " " + p["summary"])
            if s == "bull":   bull += 1
            elif s == "bear": bear += 1
            parsed.append({"body": p["title"], "summary": p["summary"],
                           "sentiment": s, "time": p["time"],
                           "publisher": p["publisher"], "link": p["link"]})
    except Exception:
        pass

    # Source 2: Google News RSS fallback
    if not parsed:
        try:
            url  = ("https://news.google.com/rss/search"
                    "?q=" + symbol + "+stock&hl=en-US&gl=US&ceid=US:en")
            resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                for block in re.findall(r"<item>(.*?)</item>", resp.text, re.DOTALL)[:20]:
                    t_m = re.search(r"<title>(.*?)</title>", block, re.DOTALL)
                    l_m = re.search(r"<link>(https?://\S+?)</link>", block)
                    d_m = re.search(r"<pubDate>(.*?)</pubDate>", block)
                    if not t_m:
                        continue
                    title = html_lib.unescape(re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"",
                                                      t_m.group(1))).strip()
                    link  = l_m.group(1).strip() if l_m else "#"
                    try:
                        from email.utils import parsedate_to_datetime
                        dt_str = parsedate_to_datetime(d_m.group(1)).strftime("%m/%d %H:%M") if d_m else ""
                    except Exception:
                        dt_str = ""
                    s = _classify(title)
                    if s == "bull":   bull += 1
                    elif s == "bear": bear += 1
                    parsed.append({"body": title, "summary": "", "sentiment": s,
                                   "time": dt_str, "publisher": "Google News", "link": link})
        except Exception:
            pass

    total    = bull + bear
    bull_pct = round(bull / total * 100) if total else 50
    return {"bull": int(bull), "bear": int(bear), "total": int(total),
            "bull_pct": bull_pct, "bear_pct": 100 - bull_pct,
            "score": bull_pct, "messages": parsed[:12], "watchlist": 0,
            "source": "Yahoo Finance / Google News"}


@st.cache_data(ttl=300)
def fetch_reddit_sentiment(symbol: str) -> dict:
    """
    Reddit sentiment via multiple fallback methods:
    1. Subreddit RSS feeds (no auth, hardest to block)
    2. Reddit JSON API search
    3. Global Reddit RSS search
    """
    import html as html_lib, re
    from datetime import timezone
    posts = []
    bull = bear = 0
    sym_up  = symbol.upper()
    sym_low = symbol.lower()

    # RSS User-Agent — RSS bots are rarely blocked
    rss_headers = {"User-Agent": "RSS-Reader/2.0 (compatible)"}
    api_headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "application/json",
    }

    def _sym_in(text: str) -> bool:
        t = text.lower()
        return (f"${sym_low}" in t or f" {sym_low} " in t or
                f"({sym_up})" in text or f" {sym_up} " in text or
                t.startswith(sym_low))

    def _ts_to_str(ts) -> str:
        try:
            return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%m/%d %H:%M")
        except Exception:
            return ""

    # ── Strategy 1: Subreddit RSS (most reliable, rarely blocked) ────────
    rss_feeds = [
        ("wallstreetbets", f"https://www.reddit.com/r/wallstreetbets/search.rss?q={sym_up}&sort=new&restrict_sr=1"),
        ("stocks",         f"https://www.reddit.com/r/stocks/search.rss?q={sym_up}&sort=new&restrict_sr=1"),
        ("investing",      f"https://www.reddit.com/r/investing/search.rss?q={sym_up}&sort=new&restrict_sr=1"),
        ("StockMarket",    f"https://www.reddit.com/r/StockMarket/search.rss?q={sym_up}&sort=new&restrict_sr=1"),
    ]
    for sub, feed_url in rss_feeds:
        if len(posts) >= 10:
            break
        try:
            resp = requests.get(feed_url, timeout=10, headers=rss_headers)
            if resp.status_code != 200:
                continue
            # Parse RSS/Atom entries
            entries = re.findall(r"<entry>(.*?)</entry>", resp.text, re.DOTALL)
            if not entries:
                entries = re.findall(r"<item>(.*?)</item>", resp.text, re.DOTALL)
            for entry in entries:
                # Title
                t_m = re.search(r"<title[^>]*>(.*?)</title>", entry, re.DOTALL)
                if not t_m:
                    continue
                title = html_lib.unescape(
                    re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1",
                           re.sub(r"<[^>]+>", "", t_m.group(1)))).strip()
                if not title or len(title) < 5:
                    continue
                # Link
                l_m = re.search(r'<link[^>]+href="([^"]+)"', entry)
                if not l_m:
                    l_m = re.search(r"<link>(https?://[^<]+)</link>", entry)
                link = l_m.group(1).strip() if l_m else "#"
                # Date
                d_m = re.search(r"<updated>(.*?)</updated>", entry)
                if not d_m:
                    d_m = re.search(r"<pubDate>(.*?)</pubDate>", entry)
                try:
                    from email.utils import parsedate_to_datetime
                    raw_date = d_m.group(1).strip() if d_m else ""
                    if "T" in raw_date:
                        from datetime import datetime as _dt
                        dt_str = _dt.fromisoformat(raw_date.replace("Z","+00:00")).strftime("%m/%d %H:%M")
                    else:
                        dt_str = parsedate_to_datetime(raw_date).strftime("%m/%d %H:%M")
                except Exception:
                    dt_str = ""
                s = _classify(title)
                if s == "bull":   bull += 1
                elif s == "bear": bear += 1
                posts.append({"title": title, "sentiment": s,
                              "score": 0, "comments": 0,
                              "url": link, "sub": sub, "time": dt_str})
        except Exception:
            continue

    # ── Strategy 2: Reddit JSON API ──────────────────────────────────────
    if len(posts) < 3:
        for sub in ["wallstreetbets", "stocks", "investing"]:
            if len(posts) >= 8:
                break
            for endpoint in [
                f"https://www.reddit.com/r/{sub}/search.json?q={sym_up}&sort=new&limit=20&restrict_sr=1",
                f"https://www.reddit.com/r/{sub}/search.json?q=%24{sym_up}&sort=new&limit=20&restrict_sr=1",
            ]:
                try:
                    resp = requests.get(endpoint, timeout=10, headers=api_headers)
                    if resp.status_code != 200:
                        continue
                    for item in resp.json().get("data", {}).get("children", []):
                        d     = item.get("data", {})
                        title = html_lib.unescape(d.get("title", "")).strip()
                        if not title:
                            continue
                        s = _classify(title)
                        if s == "bull":   bull += 1
                        elif s == "bear": bear += 1
                        posts.append({"title": title, "sentiment": s,
                                      "score": d.get("score", 0),
                                      "comments": d.get("num_comments", 0),
                                      "url": "https://reddit.com" + d.get("permalink",""),
                                      "sub": sub,
                                      "time": _ts_to_str(d.get("created_utc", 0))})
                    if posts:
                        break
                except Exception:
                    continue

    # ── Strategy 3: Global Reddit RSS search ─────────────────────────────
    if not posts:
        try:
            url  = f"https://www.reddit.com/search.rss?q={sym_up}+stock&sort=new&limit=20"
            resp = requests.get(url, timeout=10, headers=rss_headers)
            if resp.status_code == 200:
                for entry in re.findall(r"<entry>(.*?)</entry>", resp.text, re.DOTALL)[:15]:
                    t_m = re.search(r"<title[^>]*>(.*?)</title>", entry, re.DOTALL)
                    if not t_m:
                        continue
                    title = html_lib.unescape(
                        re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1",
                               re.sub(r"<[^>]+>", "", t_m.group(1)))).strip()
                    if not title:
                        continue
                    l_m = re.search(r'<link[^>]+href="([^"]+)"', entry)
                    link = l_m.group(1) if l_m else "#"
                    s = _classify(title)
                    if s == "bull":   bull += 1
                    elif s == "bear": bear += 1
                    posts.append({"title": title, "sentiment": s,
                                  "score": 0, "comments": 0,
                                  "url": link, "sub": "reddit", "time": ""})
        except Exception:
            pass

    total    = bull + bear
    bull_pct = round(bull / total * 100) if total else 50
    return {"bull": int(bull), "bear": int(bear), "total": int(total),
            "bull_pct": bull_pct, "bear_pct": 100 - bull_pct,
            "score": bull_pct, "posts": posts[:10]}


def sentiment_label_color(score: int) -> tuple:
    if score >= 70: return "#00ee66", "Extreme Greed"
    if score >= 58: return "#88ff44", "Bullish"
    if score >= 43: return "#ffcc00", "Neutral"
    if score >= 30: return "#ff8800", "Bearish"
    return               "#ff4444", "Extreme Fear"


def _gauge_html(sc, color, lbl, bull_p) -> str:
    bear_p = 100 - bull_p
    return (
        f'<div class="social-gauge">'
        f'<div class="social-score-circle" '
        f'style="border-color:{color};background:{color}18;color:{color};">'
        f'<span class="social-score-num">{sc}</span>'
        f'<span class="social-score-lbl">Score</span>'
        f'</div>'
        f'<div class="social-bull-bear">'
        f'<div style="font-size:0.88rem;color:{color};font-weight:700;margin-bottom:6px;">{lbl}</div>'
        f'<div class="social-bb-row"><span class="social-bb-label">Bull</span>'
        f'<div class="social-bb-bar"><div class="social-bb-fill" '
        f'style="width:{bull_p}%;background:#00ee66;"></div></div>'
        f'<span class="social-bb-val" style="color:#00ee66">{bull_p}%</span></div>'
        f'<div class="social-bb-row"><span class="social-bb-label">Bear</span>'
        f'<div class="social-bb-bar"><div class="social-bb-fill" '
        f'style="width:{bear_p}%;background:#ff4444;"></div></div>'
        f'<span class="social-bb-val" style="color:#ff4444">{bear_p}%</span></div>'
        f'</div></div>'
    )


def render_social_sentiment(symbol: str):
    col_st, col_rd = st.columns(2)

    # StockTwits
    with col_st:
        with st.spinner("Loading StockTwits..."):
            st_data = fetch_stocktwits(symbol)
        if not st_data or "error" in st_data:
            err = st_data.get("error","") if st_data else ""
            st.markdown(
                f'<div class="social-panel"><div class="social-title">📰 Yahoo Finance News</div>'
                f'<div style="color:#445566;font-size:0.82rem;">Unable to load{(": "+err[:80]) if err else ""}</div></div>',
                unsafe_allow_html=True)
        else:
            sc = st_data["score"]
            color, lbl = sentiment_label_color(sc)
            stat = (
                f'<div class="social-stat-row">'
                f'<div class="social-stat">Bullish <b style="color:#00ee66">{st_data["bull"]}</b></div>'
                f'<div class="social-stat">Bearish <b style="color:#ff4444">{st_data["bear"]}</b></div>'
                f'<div class="social-stat">Total <b>{st_data["total"]}</b> articles</div>'
                f'</div>'
            )
            gauge = _gauge_html(sc, color, lbl, st_data["bull_pct"])
            parts = [f'<div class="social-panel"><div class="social-title">📰 Yahoo Finance News Sentiment</div>{stat}{gauge}']
            for m in st_data.get("messages", [])[:8]:
                cls   = "social-tweet-" + m["sentiment"]
                icon  = {"bull":"🟢","bear":"🔴","neu":"⚪"}[m["sentiment"]]
                link  = m.get("link","#")
                pub   = m.get("publisher","")
                ts    = m.get("time","")
                summ  = m.get("summary","")
                parts.append(
                    f'<div class="social-tweet {cls}">{icon} '
                    f'<a href="{link}" target="_blank" style="color:#ccd6ee;text-decoration:none;font-weight:500;">{m["body"][:160]}</a>'
                    f'<div class="social-tweet-meta"><span>{pub}</span><span>{ts}</span></div></div>'
                )
            parts.append("</div>")
            st.markdown("".join(parts), unsafe_allow_html=True)

    # Reddit
    with col_rd:
        with st.spinner("Loading Reddit..."):
            rd_data = fetch_reddit_sentiment(symbol)
        if not rd_data or rd_data.get("total", 0) == 0:
            st.markdown(
                f'<div class="social-panel"><div class="social-title">REDDIT Discussions</div>'
                f'<div style="color:#445566;font-size:0.82rem;">No posts found for ${symbol} today</div></div>',
                unsafe_allow_html=True)
        else:
            sc = rd_data["score"]
            color, lbl = sentiment_label_color(sc)
            stat = (
                f'<div class="social-stat-row">'
                f'<div class="social-stat">Bull <b style="color:#00ee66">{rd_data["bull"]}</b></div>'
                f'<div class="social-stat">Bear <b style="color:#ff4444">{rd_data["bear"]}</b></div>'
                f'<div class="social-stat">Total <b>{rd_data["total"]}</b></div>'
                f'</div>'
            )
            gauge = _gauge_html(sc, color, lbl, rd_data["bull_pct"])
            parts = [f'<div class="social-panel"><div class="social-title">REDDIT WSB / Stocks Sentiment</div>{stat}{gauge}']
            for p in rd_data.get("posts", [])[:6]:
                cls  = "social-tweet-" + p["sentiment"]
                icon = {"bull":"🟢","bear":"🔴","neu":"⚪"}[p["sentiment"]]
                ts_str = p.get("time","")
                parts.append(
                    f'<div class="social-tweet {cls}">{icon} '
                    f'<a href="{p["url"]}" target="_blank" style="color:#99aacc;text-decoration:none;">'
                    f'{p["title"][:160]}</a>'
                    f'<div class="social-tweet-meta"><span>r/{p["sub"]}</span>'
                    f'<span>{p["score"]} pts</span><span>{p["comments"]} cmts</span>'
                    f'<span>{ts_str}</span></div></div>'
                )
            parts.append("</div>")
            st.markdown("".join(parts), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Options Flow 期權數據面板
# 數據來源：yfinance option_chain（免費，延遲約15分鐘）
# 指標：P/C Ratio、IV、最大痛點、到期日分佈、大額流向
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def fetch_options_data(symbol: str) -> dict:
    """抓取期權數據，回傳整合分析結果（TTL=10分鐘，避免rate limit）"""
    import time as _time
    try:
        t = yf.Ticker(symbol)

        # Retry 最多3次，每次等待間隔遞增
        exp_dates = None
        for _attempt in range(3):
            try:
                exp_dates = t.options
                break
            except Exception as _e:
                if "Too Many Requests" in str(_e) or "Rate" in str(_e):
                    if _attempt < 2:
                        _time.sleep(2 + _attempt * 2)
                        t = yf.Ticker(symbol)  # 重建 Ticker
                    else:
                        return {"error": "rate_limit"}
                else:
                    return {"error": str(_e)[:80]}

        if not exp_dates:
            return {"error": "no_options"}

        spot = None
        try:
            hist = yf.download(symbol, period="2d", interval="1d",
                               auto_adjust=True, progress=False, multi_level_col=False)
            if not hist.empty:
                spot = float(hist["Close"].iloc[-1])
        except Exception:
            pass

        # 只抓前5個到期日（減少請求數量，降低 rate limit 風險）
        target_dates = exp_dates[:min(5, len(exp_dates))]
        all_calls = []
        all_puts  = []
        by_expiry = []

        for exp in target_dates:
            try:
                _time.sleep(0.3)   # 每次請求間隔 0.3 秒，避免觸發 rate limit
                chain  = t.option_chain(exp)
                calls  = chain.calls.copy()
                puts   = chain.puts.copy()
                calls["expiry"] = exp
                puts["expiry"]  = exp
                calls = calls[(calls["volume"].fillna(0) > 0) | (calls["openInterest"].fillna(0) > 0)]
                puts  = puts[ (puts["volume"].fillna(0)  > 0) | (puts["openInterest"].fillna(0) > 0)]

                c_vol  = int(calls["volume"].fillna(0).sum())
                p_vol  = int(puts["volume"].fillna(0).sum())
                c_oi   = int(calls["openInterest"].fillna(0).sum())
                p_oi   = int(puts["openInterest"].fillna(0).sum())
                c_prem = float((calls["lastPrice"].fillna(0) * calls["volume"].fillna(0)).sum())
                p_prem = float((puts["lastPrice"].fillna(0)  * puts["volume"].fillna(0)).sum())

                atm_iv_c = atm_iv_p = None
                if spot:
                    c_s = calls.copy(); c_s["dist"] = abs(c_s["strike"] - spot)
                    iv_c = c_s.nsmallest(3,"dist")["impliedVolatility"].dropna()
                    if len(iv_c) > 0: atm_iv_c = float(iv_c.mean()) * 100
                    p_s = puts.copy(); p_s["dist"] = abs(p_s["strike"] - spot)
                    iv_p = p_s.nsmallest(3,"dist")["impliedVolatility"].dropna()
                    if len(iv_p) > 0: atm_iv_p = float(iv_p.mean()) * 100

                by_expiry.append({
                    "expiry":exp,"c_vol":c_vol,"p_vol":p_vol,"c_oi":c_oi,"p_oi":p_oi,
                    "c_prem":c_prem,"p_prem":p_prem,"atm_iv_c":atm_iv_c,"atm_iv_p":atm_iv_p,
                    "pc_vol": round(p_vol/c_vol,2) if c_vol>0 else None,
                    "pc_oi":  round(p_oi/c_oi,2)  if c_oi>0  else None,
                })
                all_calls.append(calls)
                all_puts.append(puts)
            except Exception as _ec:
                if "Too Many Requests" in str(_ec) or "Rate" in str(_ec):
                    break   # rate limit 時停止繼續請求，用已抓到的數據
                continue

        if not by_expiry:
            return {"error": "empty_chain"}

        tot_c_vol  = sum(e["c_vol"]  for e in by_expiry)
        tot_p_vol  = sum(e["p_vol"]  for e in by_expiry)
        tot_c_oi   = sum(e["c_oi"]   for e in by_expiry)
        tot_p_oi   = sum(e["p_oi"]   for e in by_expiry)
        tot_c_prem = sum(e["c_prem"] for e in by_expiry)
        tot_p_prem = sum(e["p_prem"] for e in by_expiry)
        pc_vol_total = round(tot_p_vol/tot_c_vol,3) if tot_c_vol>0 else None
        pc_oi_total  = round(tot_p_oi/tot_c_oi,3)  if tot_c_oi>0  else None

        atm_iv_avg = None
        if by_expiry[0]["atm_iv_c"] and by_expiry[0]["atm_iv_p"]:
            atm_iv_avg = round((by_expiry[0]["atm_iv_c"] + by_expiry[0]["atm_iv_p"]) / 2, 1)

        iv_skew = None
        try:
            df_c2 = pd.concat(all_calls[:2]) if all_calls else pd.DataFrame()
            df_p2 = pd.concat(all_puts[:2])  if all_puts  else pd.DataFrame()
            if spot and not df_c2.empty and not df_p2.empty:
                otm_c = df_c2[df_c2["strike"] > spot*1.05]["impliedVolatility"].dropna()
                otm_p = df_p2[df_p2["strike"] < spot*0.95]["impliedVolatility"].dropna()
                if len(otm_c) >= 3 and len(otm_p) >= 3:
                    iv_skew = round((float(otm_p.mean()) - float(otm_c.mean())) * 100, 1)
        except Exception:
            pass

        max_pain = None
        try:
            df_cm = pd.concat(all_calls[:3]) if all_calls else pd.DataFrame()
            df_pm = pd.concat(all_puts[:3])  if all_puts  else pd.DataFrame()
            if not df_cm.empty and not df_pm.empty:
                strikes = sorted(set(df_cm["strike"].tolist() + df_pm["strike"].tolist()))
                pain_vals = []
                for sp in strikes:
                    cp = float(((df_cm["strike"]-sp).clip(lower=0)*df_cm["openInterest"].fillna(0)).sum())
                    pp = float(((sp-df_pm["strike"]).clip(lower=0)*df_pm["openInterest"].fillna(0)).sum())
                    pain_vals.append((sp, cp+pp))
                if pain_vals:
                    max_pain = min(pain_vals, key=lambda x: x[1])[0]
        except Exception:
            pass

        top_trades = []
        try:
            all_rows = []
            for idx in range(min(4, len(all_calls), len(all_puts))):
                c2 = all_calls[idx].copy(); c2["type"] = "CALL"
                p2 = all_puts[idx].copy();  p2["type"] = "PUT"
                all_rows += [c2, p2]
            if all_rows:
                comb = pd.concat(all_rows)
                comb["premium"] = comb["lastPrice"].fillna(0)*comb["volume"].fillna(0)*100
                comb = comb[comb["premium"]>0].sort_values("premium",ascending=False)
                for _, row in comb.head(6).iterrows():
                    top_trades.append({
                        "type":row["type"],"strike":float(row["strike"]),
                        "expiry":str(row["expiry"]),
                        "premium":float(row["premium"]),
                        "volume":int(row["volume"]) if not pd.isna(row["volume"]) else 0,
                        "oi":int(row["openInterest"]) if not pd.isna(row["openInterest"]) else 0,
                        "iv":round(float(row["impliedVolatility"])*100,1) if not pd.isna(row["impliedVolatility"]) else None,
                        "itm":bool(row.get("inTheMoney",False)),
                    })
        except Exception:
            pass

        signal = "neutral"
        signal_reasons = []
        if pc_vol_total is not None:
            if pc_vol_total < 0.6:   signal="bull"; signal_reasons.append(f"P/C成交量={pc_vol_total:.2f}（<0.6 強烈偏多）")
            elif pc_vol_total < 0.8: signal_reasons.append(f"P/C成交量={pc_vol_total:.2f}（偏多）")
            elif pc_vol_total > 1.2: signal="bear"; signal_reasons.append(f"P/C成交量={pc_vol_total:.2f}（>1.2 強烈偏空）")
            elif pc_vol_total > 1.0: signal_reasons.append(f"P/C成交量={pc_vol_total:.2f}（偏空）")
            else:                    signal_reasons.append(f"P/C成交量={pc_vol_total:.2f}（中性）")
        if iv_skew is not None:
            if iv_skew>10:   signal_reasons.append(f"IV Skew=+{iv_skew:.1f}%（市場防跌保護需求高，偏空）")
            elif iv_skew>5:  signal_reasons.append(f"IV Skew=+{iv_skew:.1f}%（輕微偏空）")
            elif iv_skew<-5: signal_reasons.append(f"IV Skew={iv_skew:.1f}%（Call溢價>Put，偏多）")
            else:            signal_reasons.append(f"IV Skew={iv_skew:.1f}%（均衡）")
        if tot_c_prem>0 and tot_p_prem>0:
            pr = tot_p_prem/tot_c_prem
            if pr<0.7:   signal_reasons.append(f"權利金：Call ${tot_c_prem/1e6:.1f}M >> Put ${tot_p_prem/1e6:.1f}M（資金流向多頭）")
            elif pr>1.3: signal_reasons.append(f"權利金：Put ${tot_p_prem/1e6:.1f}M >> Call ${tot_c_prem/1e6:.1f}M（資金流向空頭）")
            else:        signal_reasons.append(f"權利金：Call ${tot_c_prem/1e6:.1f}M / Put ${tot_p_prem/1e6:.1f}M（均衡）")
        if max_pain and spot:
            mp_diff=(max_pain-spot)/spot*100
            signal_reasons.append(f"最大痛點 ${max_pain:.0f}（較現價 {mp_diff:+.1f}%）")

        return {
            "spot":spot,"exp_dates":list(target_dates),"by_expiry":by_expiry,
            "tot_c_vol":tot_c_vol,"tot_p_vol":tot_p_vol,"tot_c_oi":tot_c_oi,"tot_p_oi":tot_p_oi,
            "tot_c_prem":tot_c_prem,"tot_p_prem":tot_p_prem,
            "pc_vol":pc_vol_total,"pc_oi":pc_oi_total,
            "atm_iv":atm_iv_avg,"iv_skew":iv_skew,"max_pain":max_pain,
            "top_trades":top_trades,"signal":signal,"signal_reasons":signal_reasons,
            "covered_dates": len(by_expiry),
        }
    except Exception as e:
        err_str = str(e)
        if "Too Many Requests" in err_str or "Rate" in err_str:
            return {"error": "rate_limit"}
        return {"error": err_str[:80]}


# ══════════════════════════════════════════════════════════════════════════════
# 🗺️ 多時間框架關鍵位分析（月K / 週K / 日K）
# 邏輯：自動識別支撐/阻力 → 三框架綜合評分 → 操作建議
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=1800)
def fetch_mtf_keylevels(symbol: str) -> dict:
    """
    抓取月K/週K/日K數據，計算關鍵支撐/阻力位
    """
    import time as _t
    result = {"symbol": symbol, "price": None, "frames": {}, "error": None}

    frames_cfg = [
        ("月K", "1mo", "5y",  "#cc88ff"),
        ("週K", "1wk", "3y",  "#44aaff"),
        ("日K", "1d",  "1y",  "#44ee88"),
    ]

    try:
        for fname, interval, period, color in frames_cfg:
            _t.sleep(0.3)
            try:
                raw = yf.download(symbol, period=period, interval=interval,
                                  auto_adjust=True, progress=False)
                if raw is None or raw.empty or len(raw) < 10:
                    result["frames"][fname] = {"error": "數據不足"}
                    continue

                # 統一欄位名稱（處理 MultiIndex）
                if isinstance(raw.columns, pd.MultiIndex):
                    raw.columns = [c[0] for c in raw.columns]

                # 確保有必要欄位
                needed = {"Close", "High", "Low"}
                if not needed.issubset(set(raw.columns)):
                    result["frames"][fname] = {"error": f"缺少欄位:{raw.columns.tolist()[:4]}"}
                    continue

                close = raw["Close"].dropna()
                high  = raw["High"].dropna()
                low   = raw["Low"].dropna()

                if len(close) < 10:
                    result["frames"][fname] = {"error": "有效數據不足10根"}
                    continue

                price_now = float(close.iloc[-1])
                if result["price"] is None and price_now > 0:
                    result["price"] = price_now

                # ── 關鍵位識別 ─────────────────────────────────────────────
                levels = []
                window = 3
                n = len(close)

                # 樞軸高點
                for i in range(window, n - window):
                    h = float(high.iloc[i])
                    if all(h >= float(high.iloc[i-j]) for j in range(1, window+1)) and \
                       all(h >= float(high.iloc[i+j]) for j in range(1, window+1)):
                        levels.append(("阻力", h, "pivot", 1))

                # 樞軸低點
                for i in range(window, n - window):
                    l = float(low.iloc[i])
                    if all(l <= float(low.iloc[i-j]) for j in range(1, window+1)) and \
                       all(l <= float(low.iloc[i+j]) for j in range(1, window+1)):
                        levels.append(("支撐", l, "pivot", 1))

                # 近期高低
                levels.append(("阻力", float(high.iloc[-20:].max()), "近期高", 1))
                levels.append(("支撐", float(low.iloc[-20:].min()),  "近期低", 1))
                levels.append(("阻力", float(high.max()), "歷史高", 2))
                levels.append(("支撐", float(low.min()),  "歷史低", 2))

                # 整數關口
                for step in [25, 50, 100, 200]:
                    base = int(price_now / step) * step
                    for mult in range(-4, 6):
                        lvl = base + mult * step
                        if 0 < lvl < price_now * 2.5:
                            tag = "阻力" if lvl > price_now else "支撐"
                            levels.append((tag, float(lvl), f"整{step}", 1))

                # 聚類合併
                levels.sort(key=lambda x: x[1])
                merged = []
                for typ, p, src, w in levels:
                    if merged and abs(p - merged[-1][1]) / max(merged[-1][1], 0.01) < 0.015:
                        prev = merged[-1]
                        merged[-1] = (prev[0], (prev[1]*prev[3] + p*w)/(prev[3]+w),
                                      prev[2], prev[3]+w)
                    else:
                        merged.append((typ, p, src, w))

                # 篩選上下各6個
                resistances = sorted(
                    [(round(p,2), src, round(w,1))
                     for t,p,src,w in merged if p > price_now * 1.003],
                    key=lambda x: x[0])[:6]

                supports = sorted(
                    [(round(p,2), src, round(w,1))
                     for t,p,src,w in merged if p < price_now * 0.997],
                    key=lambda x: -x[0])[:6]

                # 方向判斷
                ema20 = close.ewm(span=min(20,n//2), adjust=False).mean()
                ema60 = close.ewm(span=min(60,n//2), adjust=False).mean()
                e20   = float(ema20.iloc[-1])
                e60   = float(ema60.iloc[-1])
                e20p  = float(ema20.iloc[-5]) if n >= 5 else e20

                if price_now > e20 and price_now > e60 and e20 > e20p:
                    direction, dir_label, dir_color = "bull", "多頭", "#00ee66"
                elif price_now < e20 and price_now < e60 and e20 < e20p:
                    direction, dir_label, dir_color = "bear", "空頭", "#ff5566"
                elif price_now > e20 and e20 <= e20p:
                    direction, dir_label, dir_color = "neutral_bear", "偏空震盪", "#ff8844"
                elif price_now < e20 and e20 >= e20p:
                    direction, dir_label, dir_color = "neutral_bull", "偏多震盪", "#88ee44"
                else:
                    direction, dir_label, dir_color = "neutral", "中性", "#ffcc44"

                chg_pct = float((close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100) if n>=2 else 0

                nr = resistances[0][0] if resistances else None
                ns = supports[0][0]    if supports    else None

                result["frames"][fname] = {
                    "color": color, "price": price_now,
                    "direction": direction, "dir_label": dir_label, "dir_color": dir_color,
                    "chg_pct": round(chg_pct, 2),
                    "ema20": round(e20, 2), "ema60": round(e60, 2),
                    "resistances": resistances, "supports": supports,
                    "nearest_res": nr, "nearest_sup": ns,
                    "dist_res_pct": round((nr-price_now)/price_now*100,1) if nr else None,
                    "dist_sup_pct": round((price_now-ns)/price_now*100,1) if ns else None,
                    "bars": n,
                }

            except Exception as _fe:
                result["frames"][fname] = {"error": str(_fe)[:80]}

        return result

    except Exception as e:
        result["error"] = str(e)[:80]
        return result


def render_mtf_keylevel_analysis(symbol: str, current_price: float = None):
    """多時間框架關鍵位分析面板"""
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">'
        '<div style="font-size:1.1rem;font-weight:900;color:#e0e8ff;font-family:monospace;">'
        '🗺️ 多框架關鍵位分析</div>'
        '<div style="font-size:0.7rem;color:#445566;border:1px solid #223344;border-radius:10px;'
        'padding:1px 8px;">月K · 週K · 日K 三框架綜合</div>'
        '</div>',
        unsafe_allow_html=True)

    with st.spinner(f"計算 {symbol} 關鍵支撐阻力位..."):
        data = fetch_mtf_keylevels(symbol)

    if data.get("error"):
        st.error(f"載入失敗：{data['error']}")
        return

    # price：優先用快取數據，fallback 用 render_single 傳入的即時價格
    price = float(data.get("price") or 0)
    if price <= 0 and current_price and current_price > 0:
        price = float(current_price)
    if price <= 0:
        st.warning("⚠️ 無法取得當前價格，請稍後重試")
        return

    frames = data.get("frames", {})
    frame_order = ["月K", "週K", "日K"]

    # ── 三框架方向評分 ──────────────────────────────────────────────────────
    dir_scores = {"bull": 2, "neutral_bull": 1, "neutral": 0, "neutral_bear": -1, "bear": -2}
    total_score = 0
    valid_frames = 0
    for fn in frame_order:
        fd = frames.get(fn, {})
        if "error" not in fd:
            total_score += dir_scores.get(fd.get("direction", "neutral"), 0)
            valid_frames += 1

    if valid_frames > 0:
        avg_score = total_score / valid_frames
        if avg_score >= 1.5:
            overall = "🟢 三框架一致多頭"; ov_color = "#00ee66"; ov_action = "可積極做多"
        elif avg_score >= 0.5:
            overall = "🟡 偏多（有分歧）";  ov_color = "#aaee44"; ov_action = "輕倉偏多，等信號確認"
        elif avg_score >= -0.5:
            overall = "⚪ 多空分歧震盪";   ov_color = "#ffcc44"; ov_action = "觀望為主，等突破方向"
        elif avg_score >= -1.5:
            overall = "🟠 偏空（有分歧）";  ov_color = "#ff8844"; ov_action = "輕倉偏空，設好止損"
        else:
            overall = "🔴 三框架一致空頭"; ov_color = "#ff5566"; ov_action = "可積極做空"
    else:
        overall = "⚪ 數據不足"; ov_color = "#778899"; ov_action = "暫無建議"

    # ── 找跨框架確認的關鍵位（月K+週K+日K都有的相近水平）────────────────────
    def _collect_levels(frames, frame_order):
        all_res, all_sup = [], []
        for fn in frame_order:
            fd = frames.get(fn, {})
            if "error" in fd: continue
            for p, s, n in fd.get("resistances", []):
                all_res.append((p, fn))
            for p, s, n in fd.get("supports", []):
                all_sup.append((p, fn))
        return all_res, all_sup

    all_res, all_sup = _collect_levels(frames, frame_order)

    def _find_confluences(levels, threshold=0.025):
        if not levels: return []
        levels_s = sorted(levels, key=lambda x: x[0])
        groups = []
        cur_group = [levels_s[0]]
        for item in levels_s[1:]:
            if abs(item[0] - cur_group[0][0]) / max(cur_group[0][0], 0.01) <= threshold:
                cur_group.append(item)
            else:
                groups.append(cur_group)
                cur_group = [item]
        groups.append(cur_group)
        result = []
        for g in groups:
            avg_price = sum(x[0] for x in g) / len(g)
            frames_hit = list(set(x[1] for x in g))
            result.append((round(avg_price, 2), frames_hit, len(g)))
        return sorted(result, key=lambda x: -len(x[1]))

    conf_res = _find_confluences([(p, fn) for p, fn in all_res if p > price])
    conf_sup = _find_confluences([(p, fn) for p, fn in all_sup if p < price])

    # ── 操作建議生成 ────────────────────────────────────────────────────────
    def _make_suggestion(price, conf_res, conf_sup, avg_score, frames):
        day  = frames.get("日K", {})
        week = frames.get("週K", {})

        # price 防護
        safe_price = float(price) if (price and float(price) > 0) else 100.0

        nearest_res = conf_res[0][0] if conf_res else (day.get("nearest_res") or None)
        nearest_sup = conf_sup[0][0] if conf_sup else (day.get("nearest_sup") or None)

        if nearest_res is None: nearest_res = round(safe_price * 1.05, 2)
        if nearest_sup is None: nearest_sup = round(safe_price * 0.95, 2)

        # 多頭劇本
        if avg_score >= 0.5:
            entry   = round(safe_price, 2)
            sl      = round(nearest_sup * 0.99, 2)
            tp1     = round(nearest_res, 2)
            tp2     = round(nearest_res * 1.03, 2) if len(conf_res) > 1 else round(nearest_res * 1.05, 2)
            sl_pct  = round((entry - sl) / entry * 100, 1)
            tp1_pct = round((tp1 - entry) / entry * 100, 1)
            rr1     = round(abs(tp1 - entry) / max(abs(entry - sl), 0.01), 1)
            return {
                "dir": "LONG", "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2,
                "sl_pct": sl_pct, "tp1_pct": tp1_pct, "rr1": rr1,
                "cond": f"守住支撐 ${nearest_sup:.2f}，等待量能確認後進多",
                "break_cond": f"若日K收盤跌破 ${nearest_sup:.2f} → 止損出場",
            }
        # 空頭劇本
        elif avg_score <= -0.5:
            entry   = round(safe_price, 2)
            sl      = round(nearest_res * 1.01, 2)
            tp1     = round(nearest_sup, 2)
            tp2     = round(nearest_sup * 0.97, 2) if len(conf_sup) > 1 else round(nearest_sup * 0.95, 2)
            sl_pct  = round((sl - entry) / entry * 100, 1)
            tp1_pct = round((entry - tp1) / entry * 100, 1)
            rr1     = round(abs(entry - tp1) / max(abs(sl - entry), 0.01), 1)
            return {
                "dir": "SHORT", "entry": entry, "sl": sl, "tp1": tp1, "tp2": tp2,
                "sl_pct": sl_pct, "tp1_pct": tp1_pct, "rr1": rr1,
                "cond": f"阻力 ${nearest_res:.2f} 壓制未突破，等回調後進空",
                "break_cond": f"若日K收盤站上 ${nearest_res:.2f} → 止損出場",
            }
        else:
            return {
                "dir": "WAIT", "entry": safe_price, "sl": None, "tp1": None, "tp2": None,
                "sl_pct": 0, "tp1_pct": 0, "rr1": 0,
                "cond": f"多空分歧，等待突破 ${nearest_res:.2f} 或跌破 ${nearest_sup:.2f} 再入場",
                "break_cond": f"突破 ${nearest_res:.2f} → 做多；跌破 ${nearest_sup:.2f} → 做空",
            }

    sug = _make_suggestion(price, conf_res, conf_sup, avg_score if valid_frames > 0 else 0, frames)

    # ════════════════════ 渲染開始 ════════════════════════════════════════════

    # ── 頂部：整體方向 + 當前價 ────────────────────────────────────────────
    st.markdown(
        f'<div style="background:#07090f;border:1px solid {ov_color}44;border-radius:14px;'
        f'padding:16px 20px;margin-bottom:12px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">'
        f'<div>'
        f'<div style="font-size:1.15rem;font-weight:800;color:{ov_color};">{overall}</div>'
        f'<div style="font-size:0.78rem;color:#778899;margin-top:3px;">💡 {ov_action}</div>'
        f'</div>'
        f'<div style="text-align:right;">'
        f'<div style="font-size:1.6rem;font-weight:900;color:#eef;font-family:monospace;">${price:.2f}</div>'
        f'<div style="font-size:0.72rem;color:#445566;">{symbol} 當前價</div>'
        f'</div></div>'
        f'</div>',
        unsafe_allow_html=True)

    # ── 三框架並排 ─────────────────────────────────────────────────────────
    cols = st.columns(3)
    for ci, fname in enumerate(frame_order):
        fd = frames.get(fname, {})
        with cols[ci]:
            if "error" in fd:
                st.markdown(
                    f'<div style="background:#0c1220;border-radius:10px;padding:12px;'
                    f'color:#445566;font-size:0.78rem;">⚠️ {fname}<br>{fd["error"]}</div>',
                    unsafe_allow_html=True)
                continue

            fc    = fd["color"]
            dlbl  = fd["dir_label"]
            dcol  = fd["dir_color"]
            nr    = fd.get("nearest_res")
            ns    = fd.get("nearest_sup")
            dr    = fd.get("dist_res_pct")
            ds    = fd.get("dist_sup_pct")
            chg   = fd.get("chg_pct", 0)
            chg_c = "#00ee66" if chg >= 0 else "#ff5566"

            # 支撐/阻力列表
            res_html = ""
            for i, (rp, rs, rn) in enumerate(fd["resistances"][:4]):
                is_nearest = (i == 0)
                weight = "font-weight:700;" if is_nearest else ""
                bg = "background:#1a0a28;" if is_nearest else ""
                res_html += (f'<div style="{bg}border-radius:3px;padding:2px 6px;'
                             f'display:flex;justify-content:space-between;">'
                             f'<span style="color:#cc88ff;{weight}">${rp:.2f}</span>'
                             f'<span style="color:#445566;font-size:0.65rem;">{rn}×</span></div>')

            sup_html = ""
            for i, (sp, ss, sn) in enumerate(fd["supports"][:4]):
                is_nearest = (i == 0)
                weight = "font-weight:700;" if is_nearest else ""
                bg = "background:#0a1a28;" if is_nearest else ""
                sup_html += (f'<div style="{bg}border-radius:3px;padding:2px 6px;'
                             f'display:flex;justify-content:space-between;">'
                             f'<span style="color:#44aaff;{weight}">${sp:.2f}</span>'
                             f'<span style="color:#445566;font-size:0.65rem;">{sn}×</span></div>')

            card = (
                f'<div style="background:#0c1220;border:1px solid {fc}44;'
                f'border-top:3px solid {fc};border-radius:10px;padding:12px 14px;">'

                # 標題行
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
                f'<span style="color:{fc};font-weight:800;font-size:0.9rem;">{fname}</span>'
                f'<span style="background:{dcol}22;color:{dcol};border-radius:10px;'
                f'padding:1px 8px;font-size:0.72rem;">{dlbl}</span>'
                f'</div>'

                # 當根漲跌 + EMA
                f'<div style="font-size:0.72rem;color:{chg_c};margin-bottom:6px;">'
                f'本根 {chg:+.2f}%　EMA20:{fd["ema20"]:.2f}</div>'

                # 阻力
                f'<div style="font-size:0.7rem;color:#886699;font-weight:600;'
                f'margin-bottom:3px;margin-top:4px;">▲ 阻力'
                + (f'　<span style="color:#668866;font-size:0.65rem;">最近+{dr:.1f}%</span>' if dr else '')
                + f'</div>'
                + res_html

                # 當前價指示條
                + f'<div style="background:#44aaff;border-radius:2px;height:2px;margin:6px 0;opacity:0.5;"></div>'
                f'<div style="text-align:center;font-size:0.72rem;color:#aabbcc;'
                f'font-weight:700;margin:-2px 0 4px;">📍 ${price:.2f}</div>'

                # 支撐
                + f'<div style="font-size:0.7rem;color:#446699;font-weight:600;margin-bottom:3px;">▼ 支撐'
                + (f'　<span style="color:#668866;font-size:0.65rem;">最近-{ds:.1f}%</span>' if ds else '')
                + f'</div>'
                + sup_html
                + f'</div>'
            )
            st.markdown(card, unsafe_allow_html=True)

    # ── 多框架共振關鍵位 ────────────────────────────────────────────────────
    if conf_res or conf_sup:
        st.markdown(
            '<div style="font-size:0.8rem;font-weight:700;color:#ffcc44;'
            'margin:14px 0 6px;">⚡ 多框架共振關鍵位（越多框架確認越強）</div>',
            unsafe_allow_html=True)

        lvl_html = '<div style="display:flex;flex-wrap:wrap;gap:8px;">'

        for p, fnames, n in conf_res[:5]:
            strength = len(fnames)
            sc = "#ff44aa" if strength >= 3 else "#cc88ff" if strength == 2 else "#886699"
            tag = "🔴🔴🔴" if strength >= 3 else "🔴🔴" if strength == 2 else "🔴"
            dist = round((p - price) / price * 100, 1)
            lvl_html += (
                f'<div style="background:#1a0a20;border:1px solid {sc}55;border-radius:8px;'
                f'padding:6px 12px;min-width:120px;">'
                f'<div style="color:{sc};font-weight:700;">{tag} ${p:.2f}</div>'
                f'<div style="color:#556677;font-size:0.68rem;">'
                f'{"+".join(fnames)}　+{dist:.1f}%</div></div>')

        for p, fnames, n in conf_sup[:5]:
            strength = len(fnames)
            sc = "#44ff88" if strength >= 3 else "#44aaff" if strength == 2 else "#446688"
            tag = "🟢🟢🟢" if strength >= 3 else "🟢🟢" if strength == 2 else "🟢"
            dist = round((price - p) / price * 100, 1)
            lvl_html += (
                f'<div style="background:#0a1a10;border:1px solid {sc}55;border-radius:8px;'
                f'padding:6px 12px;min-width:120px;">'
                f'<div style="color:{sc};font-weight:700;">{tag} ${p:.2f}</div>'
                f'<div style="color:#556677;font-size:0.68rem;">'
                f'{"+".join(fnames)}　-{dist:.1f}%</div></div>')

        lvl_html += '</div>'
        st.markdown(lvl_html, unsafe_allow_html=True)

    # ── 操作建議 ────────────────────────────────────────────────────────────
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    dir_c  = {"LONG": "#00ee66", "SHORT": "#ff5566", "WAIT": "#ffcc44"}[sug["dir"]]
    dir_ic = {"LONG": "▲ 做多",  "SHORT": "▼ 做空",  "WAIT": "⟺ 觀望"}[sug["dir"]]

    sug_html = (
        f'<div style="background:#07090f;border:1px solid {dir_c}44;'
        f'border-left:4px solid {dir_c};border-radius:12px;padding:16px 20px;">'
        f'<div style="font-size:0.72rem;color:#445566;margin-bottom:8px;letter-spacing:1px;">'
        f'📋 三框架綜合操作建議</div>'
        f'<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">'
        f'<span style="background:{dir_c}22;color:{dir_c};border:1px solid {dir_c}55;'
        f'border-radius:20px;padding:3px 14px;font-weight:800;font-size:0.95rem;">{dir_ic}</span>'
        f'<span style="color:#778899;font-size:0.78rem;">{sug["cond"]}</span>'
        f'</div>'
    )

    if sug["dir"] != "WAIT" and sug["sl"]:
        sug_html += (
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:10px;">'
            f'<div><span style="color:#445577;font-size:0.72rem;">進場</span> '
            f'<span style="color:#44aaff;font-weight:700;font-size:1.0rem;">${sug["entry"]:.2f}</span></div>'
            f'<div><span style="color:#445577;font-size:0.72rem;">止損</span> '
            f'<span style="color:#ff4444;font-weight:700;">${sug["sl"]:.2f}</span>'
            f'<span style="color:#663333;font-size:0.7rem;"> (-{sug["sl_pct"]:.1f}%)</span></div>'
            f'<div><span style="color:#445577;font-size:0.72rem;">止盈①</span> '
            f'<span style="color:#44ee66;font-weight:700;">${sug["tp1"]:.2f}</span>'
            f'<span style="color:#336633;font-size:0.7rem;"> (+{sug["tp1_pct"]:.1f}% R:{sug["rr1"]:.1f})</span></div>'
            f'<div><span style="color:#445577;font-size:0.72rem;">止盈②</span> '
            f'<span style="color:#aaffcc;font-weight:600;">${sug["tp2"]:.2f}</span></div>'
            f'</div>'
        )

    sug_html += (
        f'<div style="background:#0c1220;border-radius:6px;padding:8px 12px;'
        f'font-size:0.73rem;color:#ffaa44;">'
        f'⚠️ 出場條件：{sug["break_cond"]}</div>'
        f'<div style="font-size:0.65rem;color:#334455;margin-top:8px;">'
        f'* 關鍵位基於60日月K/週K/日K樞軸點自動計算｜僅供技術參考，不構成投資建議</div>'
        f'</div>'
    )
    st.markdown(sug_html, unsafe_allow_html=True)

    # 重新計算按鈕
    if st.button(f"🔄 重新計算關鍵位 ({symbol})", key=f"recalc_mtf_{symbol}"):
        fetch_mtf_keylevels.clear()
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ⏱️ 進場時機追蹤面板
# 日K/週K 高置信信號觸發後 → 自動監控30分鐘線找精確進場點
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=60)
def fetch_30min_entry_signals(symbol: str) -> dict:
    """抓取30分鐘線，判斷進場時機信號"""
    try:
        raw = yf.download(symbol, period="5d", interval="30m",
                          auto_adjust=True, progress=False)
        if raw is None or raw.empty or len(raw) < 10:
            return {"error": "數據不足"}
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] for c in raw.columns]

        close = raw["Close"].dropna()
        high  = raw["High"].dropna()
        low   = raw["Low"].dropna()
        opn   = raw["Open"].dropna()
        vol   = raw["Volume"].dropna()

        price = float(close.iloc[-1])

        # EMA計算
        e5  = close.ewm(span=5,  adjust=False).mean()
        e10 = close.ewm(span=10, adjust=False).mean()
        e20 = close.ewm(span=20, adjust=False).mean()
        e60 = close.ewm(span=60, adjust=False).mean()

        # MACD
        dif = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        dea = dif.ewm(span=9, adjust=False).mean()
        hist = (dif - dea) * 2

        # 均線聚合度（EMA5/10/20/60間距 vs 5日均距）
        spread_now  = max(float(e5.iloc[-1]), float(e20.iloc[-1])) - min(float(e5.iloc[-1]), float(e20.iloc[-1]))
        spread_avg  = float((abs(e5-e20)).rolling(20).mean().iloc[-1])
        compression = spread_now / max(spread_avg, 0.01)

        # 信號清單
        signals = []

        # S1. 均線聚合後突破（壓縮度<0.4，且本根收破EMA10）
        if compression < 0.4 and float(close.iloc[-1]) > float(e10.iloc[-1]):
            if float(close.iloc[-2]) <= float(e10.iloc[-2]):
                signals.append(("bull", "🔥 均線聚合突破", f"EMA壓縮{compression:.2f}→突破EMA10，精確進場！"))

        # S2. MACD金叉（DIF上穿DEA）
        if float(dif.iloc[-1]) > float(dea.iloc[-1]) and float(dif.iloc[-2]) <= float(dea.iloc[-2]):
            signals.append(("bull", "✅ MACD金叉", f"DIF={float(dif.iloc[-1]):.3f}>DEA={float(dea.iloc[-1]):.3f}"))

        # S3. MACD死叉
        if float(dif.iloc[-1]) < float(dea.iloc[-1]) and float(dif.iloc[-2]) >= float(dea.iloc[-2]):
            signals.append(("bear", "❌ MACD死叉", f"DIF={float(dif.iloc[-1]):.3f}<DEA={float(dea.iloc[-1]):.3f}"))

        # S4. K10大陽線（實體>均值×2.5）
        body_now = abs(float(close.iloc[-1]) - float(opn.iloc[-1]))
        body_avg = float(abs(close - opn).rolling(10).mean().iloc[-1])
        if body_now >= body_avg * 2.5 and float(close.iloc[-1]) > float(opn.iloc[-1]):
            signals.append(("bull", "🚀 大陽線", f"實體{body_now:.2f}={body_now/body_avg:.1f}×均值，量能爆發"))

        # S5. 放量突破EMA20
        vol_ma = vol.rolling(10).mean()
        if (float(close.iloc[-1]) > float(e20.iloc[-1]) and
            float(close.iloc[-2]) <= float(e20.iloc[-2]) and
            float(vol.iloc[-1]) > float(vol_ma.iloc[-1]) * 1.5):
            signals.append(("bull", "📈 放量突破EMA20", f"量{float(vol.iloc[-1])/float(vol_ma.iloc[-1]):.1f}×均量"))

        # S6. EMA多頭排列（30分鐘EMA5>10>20>60）
        if float(e5.iloc[-1]) > float(e10.iloc[-1]) > float(e20.iloc[-1]) > float(e60.iloc[-1]):
            signals.append(("bull", "⚔️ 30分鐘EMA多頭排列", f"EMA5>{float(e5.iloc[-1]):.2f}>EMA20>{float(e20.iloc[-1]):.2f}>EMA60"))

        # S7. EMA空頭排列
        if float(e5.iloc[-1]) < float(e10.iloc[-1]) < float(e20.iloc[-1]) < float(e60.iloc[-1]):
            signals.append(("bear", "💀 30分鐘EMA空頭排列", f"EMA5<{float(e5.iloc[-1]):.2f}<EMA20<{float(e20.iloc[-1]):.2f}<EMA60"))

        # ── S8. VIX驟降確認（最強進場催化劑）──────────────────────────────
        # 邏輯：抓取VIX 30分鐘線，偵測最新根VIX是否快速下跌
        # VIX驟降 = 市場恐慌消散 = 資金流向風險資產 = 多頭最強催化
        vix_drop_pct  = 0.0
        vix_now       = None
        vix_signal    = None
        try:
            _vix_raw = yf.download("^VIX", period="3d", interval="30m",
                                   auto_adjust=True, progress=False)
            if _vix_raw is not None and not _vix_raw.empty and len(_vix_raw) >= 3:
                if isinstance(_vix_raw.columns, pd.MultiIndex):
                    _vix_raw.columns = [c[0] for c in _vix_raw.columns]
                _vc = _vix_raw["Close"].dropna()
                vix_now      = float(_vc.iloc[-1])
                vix_prev1    = float(_vc.iloc[-2])
                vix_prev3    = float(_vc.iloc[-4]) if len(_vc) >= 4 else vix_prev1
                vix_drop_pct = (vix_prev1 - vix_now) / vix_prev1 * 100   # 正=下跌

                # 單根跌幅 ≥3%：強力VIX驟降
                if vix_drop_pct >= 3.0:
                    signals.append(("bull", "🔥 VIX驟降",
                        f"VIX {vix_prev1:.2f}→{vix_now:.2f} 單根跌{vix_drop_pct:.1f}%"
                        f"，市場恐慌快速消散，多頭最強催化！"))
                    vix_signal = "strong_bull"
                # 單根跌幅 1.5-3%：溫和VIX下行
                elif vix_drop_pct >= 1.5:
                    signals.append(("bull", "📉 VIX下行",
                        f"VIX {vix_prev1:.2f}→{vix_now:.2f} 跌{vix_drop_pct:.1f}%，情緒改善"))
                    vix_signal = "mild_bull"
                # 3根合計跌幅 ≥5%：趨勢性VIX下行
                elif (vix_prev3 - vix_now) / vix_prev3 * 100 >= 5.0:
                    _3bar_drop = (vix_prev3 - vix_now) / vix_prev3 * 100
                    signals.append(("bull", "📊 VIX趨勢下行",
                        f"VIX 3根累跌{_3bar_drop:.1f}%（{vix_prev3:.2f}→{vix_now:.2f}），持續去恐慌"))
                    vix_signal = "trend_bull"
                # VIX驟升 ≥3%：警告，不宜進多
                elif vix_drop_pct <= -3.0:
                    signals.append(("bear", "🚨 VIX驟升",
                        f"VIX {vix_prev1:.2f}→{vix_now:.2f} 單根升{abs(vix_drop_pct):.1f}%"
                        f"，市場恐慌急升，嚴禁追多！"))
                    vix_signal = "strong_bear"
        except Exception:
            pass   # VIX 抓取失敗不影響其他信號

        # EMA方向判斷
        if float(e5.iloc[-1]) > float(e20.iloc[-1]) > float(e60.iloc[-1]):
            ema_dir = "bull"
        elif float(e5.iloc[-1]) < float(e20.iloc[-1]) < float(e60.iloc[-1]):
            ema_dir = "bear"
        else:
            ema_dir = "neutral"

        macd_dir = "bull" if float(dif.iloc[-1]) > float(dea.iloc[-1]) else "bear"

        return {
            "price":        price,
            "e5":           round(float(e5.iloc[-1]),  2),
            "e10":          round(float(e10.iloc[-1]), 2),
            "e20":          round(float(e20.iloc[-1]), 2),
            "e60":          round(float(e60.iloc[-1]), 2),
            "dif":          round(float(dif.iloc[-1]), 3),
            "dea":          round(float(dea.iloc[-1]), 3),
            "compression":  round(compression, 2),
            "ema_dir":      ema_dir,
            "macd_dir":     macd_dir,
            "signals":      signals,
            "bars":         len(close),
            "vix_now":      round(vix_now, 2) if vix_now else None,
            "vix_drop_pct": round(vix_drop_pct, 1),
            "vix_signal":   vix_signal,
        }
    except Exception as e:
        return {"error": str(e)[:80]}


def render_entry_tracker_panel():
    """⏱️ 進場時機追蹤面板"""
    trackers = [t for t in st.session_state.get("entry_trackers", [])
                if t["status"] == "追蹤中"]
    if not trackers:
        return

    st.markdown("---")
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
        '<div style="font-size:1.1rem;font-weight:900;color:#ffe066;font-family:monospace;">'
        '⏱️ 進場時機追蹤</div>'
        '<div style="font-size:0.7rem;color:#665500;border:1px solid #443300;'
        'border-radius:10px;padding:1px 8px;background:#1a1200;">'
        '日K信號 → 30分鐘精確進場</div>'
        f'<div style="font-size:0.72rem;color:#556677;margin-left:auto;">'
        f'追蹤中 {len(trackers)} 個</div>'
        '</div>',
        unsafe_allow_html=True)

    for i, tracker in enumerate(trackers):
        sym  = tracker["symbol"]
        dire = tracker["direction"]
        dc   = "#00ee66" if dire == "LONG" else "#ff5566"
        di   = "▲ 做多" if dire == "LONG" else "▼ 做空"

        # 抓30分鐘信號
        m30 = fetch_30min_entry_signals(sym)
        has_err = "error" in m30

        # 30分鐘信號與方向是否一致
        entry_signals = []
        if not has_err:
            for stype, sname, sdesc in m30.get("signals", []):
                if stype == ("bull" if dire == "LONG" else "bear"):
                    entry_signals.append((sname, sdesc))

        # 綜合進場就緒度
        readiness = len(entry_signals)
        if readiness >= 3:
            ready_label = "🟢 強烈進場信號"; ready_color = "#00ee66"
        elif readiness >= 2:
            ready_label = "🟡 進場信號確認"; ready_color = "#ffcc44"
        elif readiness == 1:
            ready_label = "🟠 初步信號，等確認"; ready_color = "#ff8844"
        else:
            ready_label = "⚪ 尚無進場信號"; ready_color = "#556677"

        # 30分鐘EMA方向匹配
        ema_match = not has_err and (
            (dire == "LONG"  and m30.get("ema_dir") == "bull") or
            (dire == "SHORT" and m30.get("ema_dir") == "bear"))
        macd_match = not has_err and (
            (dire == "LONG"  and m30.get("macd_dir") == "bull") or
            (dire == "SHORT" and m30.get("macd_dir") == "bear"))

        # 倒計時計算
        expire_str = tracker.get("expire_time", "")
        time_left_str = ""
        expire_warn   = False
        try:
            _exp = datetime.strptime(f"{datetime.now().year}/{expire_str}", "%Y/%m/%d %H:%M")
            _diff = (_exp - datetime.now()).total_seconds() / 3600
            if _diff <= 0:
                time_left_str = "⏰ 已過期"
                expire_warn = True
            elif _diff < 1:
                time_left_str = f"⏰ {int(_diff*60)}分鐘後過期"
                expire_warn = True
            else:
                time_left_str = f"⏱ 剩{_diff:.1f}h"
        except Exception:
            time_left_str = ""

        # 自動止損止盈
        sl  = tracker.get("sl")
        tp1 = tracker.get("tp1")
        tp2 = tracker.get("tp2")
        atr = tracker.get("atr", 0)
        rr  = tracker.get("rr", 1.3)

        # 卡片邊框顏色
        card_border     = "#ff4400" if expire_warn else dc
        card_border_dim = card_border + "33"
        time_color      = "#ff6622" if expire_warn else "#445566"
        ema_color       = "#00ee66" if ema_match else "#ff5566"
        ema_icon        = "✅" if ema_match else "❌"
        macd_color      = "#00ee66" if macd_match else "#ff5566"
        macd_icon       = "✅" if macd_match else "❌"
        comp_color      = "#ffcc44" if (not has_err and m30.get("compression", 1) < 0.4) else "#445566"
        comp_icon       = "🔥" if (not has_err and m30.get("compression", 1) < 0.4) else "📊"

        card = (
            f'<div style="background:#0c1208;border:1px solid {card_border_dim};'
            f'border-left:3px solid {card_border};'
            f'border-radius:10px;padding:14px 16px;margin:8px 0;">'

            # 頂行
            f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:8px;">'
            f'<span style="color:#eef;font-weight:800;font-size:1rem;">${sym}</span>'
            f'<span style="background:{dc}22;color:{dc};border:1px solid {dc}55;'
            f'border-radius:16px;padding:2px 10px;font-weight:700;font-size:0.82rem;">{di}</span>'
            f'<span style="background:#0a1020;color:#6688bb;border:1px solid #223344;'
            f'border-radius:8px;padding:1px 7px;font-size:0.65rem;">{tracker["period_src"]}觸發</span>'
            f'<span style="color:#557799;font-size:0.68rem;">📌 {tracker["trigger_signal"]}</span>'
            f'<span style="color:#334455;font-size:0.63rem;">{tracker["trigger_time"]} @ ${tracker["trigger_price"]:.2f}</span>'
            f'<span style="color:{time_color};font-size:0.65rem;margin-left:auto;">{time_left_str}</span>'
            f'<span style="background:#1a1a00;color:{ready_color};border:1px solid {ready_color}44;'
            f'border-radius:8px;padding:1px 8px;font-size:0.7rem;">{ready_label}</span>'
            f'</div>'

            # 止損止盈列
            + (f'<div style="display:flex;gap:14px;flex-wrap:wrap;'
               f'background:#080c06;border-radius:6px;padding:6px 12px;margin-bottom:8px;">'
               f'<span style="color:#445566;font-size:0.68rem;">📐 ATR={atr:.2f}</span>'
               f'<span style="color:#778899;font-size:0.68rem;">止損</span>'
               f'<span style="color:#ff5566;font-weight:600;font-size:0.78rem;">${sl:.2f}</span>'
               f'<span style="color:#334455;font-size:0.63rem;">'
               f'({abs(sl-tracker["trigger_price"])/tracker["trigger_price"]*100:.1f}%)</span>'
               f'<span style="color:#778899;font-size:0.68rem;">止盈①</span>'
               f'<span style="color:#44ee66;font-weight:600;font-size:0.78rem;">${tp1:.2f}</span>'
               f'<span style="color:#778899;font-size:0.68rem;">止盈②</span>'
               f'<span style="color:#00ffaa;font-weight:600;font-size:0.78rem;">${tp2:.2f}</span>'
               f'<span style="color:#446644;font-size:0.65rem;">R:R≈{rr:.1f}</span>'
               f'</div>'
               if sl and tp1 else '')

            # 30分鐘狀態列
            + f'<div style="background:#080e04;border-radius:6px;padding:8px 12px;margin-bottom:8px;">'
            f'<div style="font-size:0.7rem;color:#445566;margin-bottom:5px;">📊 30分鐘線即時狀態</div>'
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        )

        if has_err:
            card += f'<span style="color:#665544;font-size:0.72rem;">⚠️ {m30["error"]}</span>'
        else:
            p = m30["price"]
            vix_now  = m30.get("vix_now")
            vix_drop = m30.get("vix_drop_pct", 0)
            vix_sig  = m30.get("vix_signal")

            # VIX 顏色和標籤
            if vix_sig == "strong_bull":
                vix_color = "#00ff88"; vix_icon = "🔥"
            elif vix_sig == "mild_bull":
                vix_color = "#88ee44"; vix_icon = "📉"
            elif vix_sig == "trend_bull":
                vix_color = "#44bbff"; vix_icon = "📊"
            elif vix_sig == "strong_bear":
                vix_color = "#ff2244"; vix_icon = "🚨"
            else:
                vix_color = "#445566"; vix_icon = "➖"

            card += (
                f'<div style="text-align:center;">'
                f'<div style="color:#aabbcc;font-size:0.75rem;font-weight:600;">${p:.2f}</div>'
                f'<div style="color:#334455;font-size:0.62rem;">現價</div></div>'

                f'<div style="text-align:center;">'
                f'<div style="color:{ema_color};font-size:0.75rem;">'
                f'{ema_icon} EMA {m30["ema_dir"].upper()}</div>'
                f'<div style="color:#334455;font-size:0.62rem;">均線方向</div></div>'

                f'<div style="text-align:center;">'
                f'<div style="color:{macd_color};font-size:0.75rem;">'
                f'{macd_icon} MACD</div>'
                f'<div style="color:#334455;font-size:0.62rem;">DIF={m30["dif"]}</div></div>'

                f'<div style="text-align:center;">'
                f'<div style="color:{comp_color};font-size:0.75rem;">'
                f'{comp_icon} 聚合{m30["compression"]:.2f}</div>'
                f'<div style="color:#334455;font-size:0.62rem;">均線壓縮度</div></div>'

                # VIX 欄位
                + (f'<div style="text-align:center;background:#0a0e16;border-radius:5px;padding:2px 8px;">'
                   f'<div style="color:{vix_color};font-size:0.75rem;font-weight:700;">'
                   f'{vix_icon} VIX {vix_now:.1f}</div>'
                   f'<div style="color:{vix_color};font-size:0.62rem;">'
                   f'{"▼" if vix_drop>0 else "▲"}{abs(vix_drop):.1f}%</div>'
                   f'</div>'
                   if vix_now else
                   f'<div style="text-align:center;">'
                   f'<div style="color:#334455;font-size:0.72rem;">VIX --</div></div>')
            )

        card += '</div></div>'

        # 30分鐘進場信號列表
        if entry_signals:
            card += '<div style="display:flex;flex-direction:column;gap:3px;margin-bottom:8px;">'
            for sname, sdesc in entry_signals:
                card += (f'<div style="background:#0a1a06;border-left:2px solid #00ee66;'
                         f'border-radius:4px;padding:4px 10px;">'
                         f'<span style="color:#44ee66;font-size:0.74rem;font-weight:600;">{sname}</span>'
                         f'<span style="color:#667788;font-size:0.7rem;margin-left:8px;">{sdesc}</span>'
                         f'</div>')
            card += '</div>'
        elif not has_err:
            card += (f'<div style="font-size:0.72rem;color:#445566;'
                     f'background:#080c06;border-radius:4px;padding:5px 10px;margin-bottom:8px;">'
                     f'💤 30分鐘線尚無方向一致進場信號，繼續等待...</div>')

        # 建議
        if not has_err:
            vix_sig   = m30.get("vix_signal")
            vix_drop  = m30.get("vix_drop_pct", 0)
            vix_boost = vix_sig in ("strong_bull",) and dire == "LONG"
            vix_warn  = vix_sig == "strong_bear"  and dire == "LONG"

            if vix_warn:
                advice = "🚨 VIX 急升，市場恐慌惡化，暫停進多計劃！等 VIX 穩定後再評估"
                advice_color = "#ff2244"
            elif readiness >= 2 and ema_match and macd_match and vix_boost:
                advice = (f"⚡⚡ 極強進場確認：30分鐘多重信號 + VIX驟降{vix_drop:.1f}%！"
                          f"{'回調EMA10' if dire=='LONG' else '反彈EMA10'}附近進場，"
                          f"止損{'EMA20下方' if dire=='LONG' else 'EMA20上方'}  ← 最高置信")
                advice_color = "#00ff88"
            elif readiness >= 2 and ema_match and macd_match:
                advice = (f"✅ 多重30分鐘信號確認，"
                          f"{'回調至EMA10附近' if dire=='LONG' else '反彈至EMA10附近'}可進場，"
                          f"止損設{'EMA20' if dire=='LONG' else 'EMA20'}")
                advice_color = "#44ee66"
            elif readiness >= 1 and vix_boost:
                advice = f"🔥 VIX驟降{vix_drop:.1f}%確認，等待30分鐘均線突破信號後進場"
                advice_color = "#ffcc44"
            elif readiness >= 1:
                advice = f"⚠️ 初步信號，等待{'MACD金叉+量能確認' if dire=='LONG' else 'MACD死叉+量能確認'}後進場"
                advice_color = "#ffaa44"
            else:
                advice = f"⌛ 繼續等待30分鐘線 {'均線聚合突破+MACD金叉' if dire=='LONG' else '均線壓制+MACD死叉'} + VIX配合"
                advice_color = "#556677"

            card += (f'<div style="font-size:0.73rem;color:{advice_color};'
                     f'background:#0a1008;border-radius:5px;padding:6px 10px;">{advice}</div>')

        card += '</div>'
        st.markdown(card, unsafe_allow_html=True)

    # 操作按鈕列
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ 清除已完成追蹤", key="clear_entry_trackers"):
            st.session_state.entry_trackers = [
                t for t in st.session_state.entry_trackers
                if t["status"] == "追蹤中"]
            st.rerun()


def render_options_panel(symbol: str):
    """期權數據面板 — P/C Ratio、IV、最大痛點、流向、到期日分佈"""
    with st.spinner(f"載入 {symbol} 期權數據（最多約5秒）..."):
        data = fetch_options_data(symbol)

    if "error" in data:
        err = data["error"]
        if err == "rate_limit":
            st.markdown(
                '<div style="background:#1a2030;border:1px solid #445;border-radius:8px;padding:16px;">'
                '<div style="color:#ffaa44;font-size:0.9rem;font-weight:600;margin-bottom:6px;">⏳ Yahoo Finance 請求過於頻繁</div>'
                '<div style="color:#8899aa;font-size:0.8rem;">yfinance 免費 API 有速率限制，期權數據已快取10分鐘。</div>'
                '<div style="color:#8899aa;font-size:0.8rem;margin-top:4px;">請等待 <b style="color:#ffcc44;">1-2 分鐘</b> 後點擊「強制刷新數據快取」再試，或繼續使用其他面板。</div>'
                '</div>',
                unsafe_allow_html=True)
            if st.button(f"🔄 清除期權快取並重試 ({symbol})", key=f"opt_retry_{symbol}"):
                fetch_options_data.clear()
                st.rerun()
        else:
            msg = {
                "no_options": "此股票無期權市場（通常為小型股）",
                "empty_chain": "期權鏈數據為空，請稍後再試",
            }.get(err, f"載入失敗：{err}")
            st.markdown(
                f'<div style="background:#1a2535;border:1px solid #334;border-radius:8px;'
                f'padding:16px;color:#667788;font-size:0.85rem;">🔒 {msg}</div>',
                unsafe_allow_html=True)
        return

    spot=data.get("spot"); pc_vol=data.get("pc_vol"); pc_oi=data.get("pc_oi")
    atm_iv=data.get("atm_iv"); iv_skew=data.get("iv_skew"); max_pain=data.get("max_pain")
    signal=data.get("signal","neutral"); reasons=data.get("signal_reasons",[])
    sig_color={"bull":"#00ee66","bear":"#ff4444","neutral":"#aabb88"}[signal]
    sig_icon={"bull":"🐂","bear":"🐻","neutral":"⚖️"}[signal]
    sig_label={"bull":"偏多","bear":"偏空","neutral":"中性"}[signal]

    def _mc(col,title,value,sub="",color="#ccd6ee",warn=""):
        with col:
            st.markdown(
                f'<div style="background:#111e2e;border:1px solid #223344;border-radius:8px;padding:12px 10px;text-align:center;">' +
                f'<div style="font-size:0.72rem;color:#5577aa;margin-bottom:4px;">{title}</div>' +
                f'<div style="font-size:1.3rem;font-weight:700;color:{color};">{value}</div>' +
                f'<div style="font-size:0.7rem;color:#6688aa;margin-top:2px;">{sub}</div>' +
                (f'<div style="font-size:0.68rem;color:#ffaa44;margin-top:3px;">{warn}</div>' if warn else "") +
                '</div>', unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    if pc_vol is not None:
        pc_c="#00ee66" if pc_vol<0.8 else ("#ff4444" if pc_vol>1.2 else "#ffcc44")
        _mc(c1,"P/C 成交量比",f"{pc_vol:.2f}",f"C:{data['tot_c_vol']//1000}K P:{data['tot_p_vol']//1000}K",pc_c,"偏多" if pc_vol<0.8 else ("偏空" if pc_vol>1.2 else "中性"))
    else: _mc(c1,"P/C 成交量比","N/A","","#445566")
    if pc_oi is not None:
        oi_c="#00ee66" if pc_oi<0.8 else ("#ff4444" if pc_oi>1.2 else "#ffcc44")
        _mc(c2,"P/C 未平倉比",f"{pc_oi:.2f}",f"C:{data['tot_c_oi']//1000}K P:{data['tot_p_oi']//1000}K",oi_c)
    else: _mc(c2,"P/C 未平倉比","N/A","","#445566")
    if atm_iv is not None:
        iv_c="#ff6644" if atm_iv>80 else ("#ffaa44" if atm_iv>60 else ("#ffcc44" if atm_iv>40 else "#00cc99"))
        _mc(c3,"ATM IV（近月）",f"{atm_iv:.1f}%","隱含波動率",iv_c,"極高恐慌" if atm_iv>80 else ("高波動" if atm_iv>60 else ("偏高" if atm_iv>40 else "正常")))
    else: _mc(c3,"ATM IV（近月）","N/A","","#445566")
    if iv_skew is not None:
        sk_c="#ff4444" if iv_skew>8 else ("#ffcc44" if iv_skew>3 else ("#00ee66" if iv_skew<-3 else "#aabbcc"))
        _mc(c4,"IV Skew（Put-Call）",f"{iv_skew:+.1f}%","OTM Put-Call IV",sk_c,"防護需求↑" if iv_skew>5 else ("Call溢價↑" if iv_skew<-5 else "均衡"))
    else: _mc(c4,"IV Skew","N/A","","#445566")
    if max_pain is not None and spot:
        mp_d=(max_pain-spot)/spot*100
        _mc(c5,"最大痛點",f"${max_pain:.0f}",f"現價${spot:.0f}（{mp_d:+.1f}%）","#aaffcc" if abs(mp_d)<3 else ("#ffaa44" if abs(mp_d)<8 else "#ff6644"))
    else: _mc(c5,"最大痛點","N/A","","#445566")

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    col_s,col_e = st.columns([1,1])

    with col_s:
        rh="".join(f'<div style="padding:3px 0;border-bottom:1px solid #1e2e3e;font-size:0.78rem;color:#99aacc;">• {r}</div>' for r in reasons)
        st.markdown(
            f'<div style="background:#0e1e2e;border:1px solid {sig_color}44;border-radius:8px;padding:14px;">' +
            f'<div style="font-size:0.85rem;font-weight:700;color:{sig_color};margin-bottom:8px;">{sig_icon} 期權流向信號：{sig_label}</div>' +
            rh + '<div style="font-size:0.68rem;color:#446;margin-top:8px;">⚠️ 期權為附加信號，需配合技術面確認。高P/C可能是對沖而非純空頭。</div></div>',
            unsafe_allow_html=True)

    with col_e:
        by_exp=data.get("by_expiry",[])
        if by_exp:
            rows=[]
            for e in by_exp[:6]:
                pc=f"{e['pc_vol']:.2f}" if e["pc_vol"] else "—"
                pc_c="#00ee66" if (e["pc_vol"] and e["pc_vol"]<0.8) else ("#ff4444" if (e["pc_vol"] and e["pc_vol"]>1.2) else "#ffcc44")
                iv_s=f"{e['atm_iv_c']:.0f}%" if e["atm_iv_c"] else "—"
                rows.append(f'<tr><td style="color:#aabbcc;padding:3px 6px;">{e["expiry"][5:]}</td><td style="color:#66aaff;text-align:right;padding:3px 6px;">{e["c_vol"]:,}</td><td style="color:#ff6666;text-align:right;padding:3px 6px;">{e["p_vol"]:,}</td><td style="color:{pc_c};text-align:right;padding:3px 6px;">{pc}</td><td style="color:#aacc88;text-align:right;padding:3px 6px;">{iv_s}</td></tr>')
            st.markdown(
                '<div style="background:#0e1e2e;border:1px solid #223;border-radius:8px;padding:12px;">' +
                '<div style="font-size:0.8rem;font-weight:700;color:#7799cc;margin-bottom:8px;">📅 各到期日期權分佈</div>' +
                '<table style="width:100%;border-collapse:collapse;font-size:0.75rem;">' +
                '<tr style="color:#556677;border-bottom:1px solid #223;"><th style="text-align:left;padding:3px 6px;">到期日</th><th style="text-align:right;padding:3px 6px;">Call量</th><th style="text-align:right;padding:3px 6px;">Put量</th><th style="text-align:right;padding:3px 6px;">P/C</th><th style="text-align:right;padding:3px 6px;">ATM IV</th></tr>' +
                "".join(rows) + '</table></div>', unsafe_allow_html=True)

    top=data.get("top_trades",[])
    if top:
        st.markdown('<div style="font-size:0.8rem;font-weight:700;color:#7799cc;margin:10px 0 4px;">💰 大額期權流向（依保費規模排序）</div>',unsafe_allow_html=True)
        cards=[]
        for tr in top:
            ic=tr["type"]=="CALL"
            bg="#0d2010" if ic else "#200d0d"; bd="#00aa44" if ic else "#aa2222"
            ti="📈 CALL" if ic else "📉 PUT"
            itm='<span style="background:#335;color:#aaf;font-size:0.65rem;padding:1px 4px;border-radius:3px;margin-left:4px;">ITM</span>' if tr["itm"] else ""
            pm=tr["premium"]/1e6; ps=f"${pm:.2f}M" if pm>=0.1 else f"${tr['premium']/1e3:.0f}K"
            iv_s=f"IV {tr['iv']:.0f}%" if tr["iv"] else ""
            cards.append(f'<div style="background:{bg};border:1px solid {bd}44;border-radius:6px;padding:10px 12px;flex:1;min-width:140px;"><div style="font-size:0.8rem;font-weight:700;color:{"#00cc55" if ic else "#ee3333"};">{ti}{itm}</div><div style="font-size:1.0rem;font-weight:700;color:#eef;margin:4px 0;">Strike ${tr["strike"]:.0f}</div><div style="font-size:0.72rem;color:#8899aa;">{tr["expiry"][5:]}</div><div style="font-size:0.78rem;color:#ffcc44;font-weight:600;margin-top:4px;">{ps}</div><div style="font-size:0.7rem;color:#667788;">Vol {tr["volume"]:,} · OI {tr["oi"]:,} · {iv_s}</div></div>')
        for row in [cards[:3],cards[3:6]]:
            if row: st.markdown(f'<div style="display:flex;gap:8px;margin-bottom:6px;">'+"".join(row)+"</div>",unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.68rem;color:#334455;margin-top:8px;">數據來源：Yahoo Finance Options（約15分鐘延遲）｜高P/C可能包含機構對沖部位</div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# AI 技術分析模組
# ══════════════════════════════════════════════════════════════════════════════

def build_analysis_prompt(symbol: str, interval_label: str, df: pd.DataFrame,
                          mkt: dict = None) -> str:
    """把技術指標數據打包成結構化 prompt 給 Claude 分析"""
    if df.empty:
        return ""

    close = df["Close"]
    last  = float(close.iloc[-1])
    high  = float(df["High"].iloc[-1])
    low_  = float(df["Low"].iloc[-1])
    vol   = int(df["Volume"].iloc[-1])

    # EMA 數值
    ema_vals = {n: round(float(calc_ema(close, n).iloc[-1]), 2) for n, _ in EMA_CONFIGS}
    # MACD
    dif, dea, hist = calc_macd(close)
    dif_val  = round(float(dif.iloc[-1]), 4)
    dea_val  = round(float(dea.iloc[-1]), 4)
    hist_val = round(float(hist.iloc[-1]), 4)
    # 金叉死叉
    macd_sig = "金叉(多)" if dif_val > dea_val else "死叉(空)"
    # 支撐阻力
    pivots_h, pivots_l = calc_pivot(df)
    resist  = round(max(p[1] for p in pivots_h), 2) if pivots_h else None
    support = round(min(p[1] for p in pivots_l), 2) if pivots_l else None
    # 成交量
    vol_ma5    = float(df["Volume"].rolling(5).mean().iloc[-1])
    vol_ratio  = round(vol / vol_ma5, 2) if vol_ma5 > 0 else 1
    # 趨勢
    trend = detect_trend(df)
    # 近期漲跌（5根）
    ret5 = round((last / float(close.iloc[-6]) - 1) * 100, 2) if len(close) > 6 else 0
    # 波動率（近20根ATR簡化版）
    atr = round(float((df["High"] - df["Low"]).tail(20).mean()), 2)

    # 大盤環境
    mkt_ctx = ""
    if mkt:
        spy = mkt.get("spy", {})
        vix = mkt.get("vix", {})
        if spy: mkt_ctx += f"\n- SPY: ${spy.get('last',0):.2f} ({spy.get('pct',0):+.2f}%)"
        if vix: mkt_ctx += f"\n- VIX: {vix.get('last',20):.1f}"

    prompt = f"""你是一位專業的美股技術分析師，請根據以下數據對 {symbol} 進行分析，並給出具體的操作建議。

## 基本資訊
- 股票代號：{symbol}
- 時間週期：{interval_label}
- 最新價格：${last:.2f}
- 本K高/低：${high:.2f} / ${low_:.2f}
- 近5根漲跌幅：{ret5:+.2f}%
- 平均波幅(ATR)：${atr:.2f}

## EMA 均線系統
- EMA5: ${ema_vals[5]} {'↑' if last > ema_vals[5] else '↓'}
- EMA10: ${ema_vals[10]} {'↑' if last > ema_vals[10] else '↓'}
- EMA20: ${ema_vals[20]} {'↑' if last > ema_vals[20] else '↓'}
- EMA60: ${ema_vals[60]} {'↑' if last > ema_vals[60] else '↓'}
- EMA120: ${ema_vals[120]} {'↑' if last > ema_vals[120] else '↓'}
- EMA200: ${ema_vals[200]} {'↑' if last > ema_vals[200] else '↓'}
- 均線排列：{trend}

## MACD (12,26,9)
- DIF: {dif_val}
- DEA: {dea_val}
- MACD柱: {hist_val}
- 信號：{macd_sig}

## 支撐與阻力
- 最近阻力位：{'$' + str(resist) if resist else '未偵測到'}
- 最近支撐位：{'$' + str(support) if support else '未偵測到'}

## 成交量
- 當前成交量：{vol/10000:.1f}萬股
- 相對均量倍數：{vol_ratio:.1f}x {'（異常放量）' if vol_ratio > 2 else ''}

## 大盤環境{mkt_ctx if mkt_ctx else '\n- 數據未載入'}

---

請以 JSON 格式回覆，欄位如下：
{{
  "verdict": "做多/做空/觀望",
  "confidence": 75,
  "trend_analysis": "（2-3句趨勢分析）",
  "entry_price": 123.45,
  "entry_note": "（進場條件說明）",
  "take_profit_1": 128.00,
  "take_profit_2": 132.00,
  "stop_loss": 119.50,
  "risk_reward": "1:2.5",
  "key_risks": "（主要風險1-2點）",
  "reasoning": "（完整分析邏輯，繁體中文，150字以內）"
}}

注意：
1. entry_price / take_profit / stop_loss 必須是數字，根據支撐阻力和ATR計算
2. stop_loss 做多時設在支撐位下方1-2個ATR，做空時設在阻力位上方
3. 只回覆 JSON，不要有任何其他文字或markdown標記
"""
    return prompt


# ── AI：只用 Groq（免費，每天14400次）───────────────────────────────────────
def get_groq_key() -> str:
    """從 secrets 或 session_state 取得 Groq API Key"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("groq_key", "")

# 向後相容別名
def get_ai_key(provider: str) -> str:
    return get_groq_key()


def call_groq_analysis(prompt: str) -> dict:
    """呼叫 Groq API（LLaMA 3.3 70B）進行技術分析"""
    import json

    api_key = get_groq_key()
    if not api_key:
        return {"error": "NO_KEY"}

    system_msg = (
        "你是專業美股技術分析師，擅長解讀均線、MACD、支撐阻力。"
        "永遠以繁體中文回覆，且只輸出純 JSON，不含任何 markdown 或多餘文字。"
    )
    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": prompt},
                ],
                "max_tokens": 1000,
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        if resp.status_code == 401:
            return {"error": "Groq API Key 無效，請重新輸入"}
        if resp.status_code == 429:
            return {"error": "RATE_LIMIT"}
        if resp.status_code != 200:
            return {"error": f"Groq 錯誤 {resp.status_code}: {resp.text[:200]}"}

        text = resp.json()["choices"][0]["message"]["content"]
        text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(text)

    except json.JSONDecodeError as e:
        return {"error": f"JSON 解析失敗：{e}"}
    except Exception as e:
        return {"error": str(e)}


# 向後相容別名
def call_ai_analysis(prompt, provider="groq"): return call_groq_analysis(prompt)
def call_claude_analysis(prompt):              return call_groq_analysis(prompt)
def get_anthropic_key():                       return get_groq_key()




# 各供應商說明
PROVIDER_INFO = {
    "gemini": {
        "name":        "Gemini 2.0 Flash",
        "free":        True,
        "quota":       "每天 1,500 次，每分鐘 60 次",
        "url":         "https://aistudio.google.com/apikey",
        "placeholder": "AIza...",
        "secret_key":  "GEMINI_API_KEY",
        "guide":       "前往 aistudio.google.com → Get API Key → Create API Key",
    },
    "groq": {
        "name":        "Groq LLaMA 3.3 70B",
        "free":        True,
        "quota":       "每天 14,400 次",
        "url":         "https://console.groq.com/keys",
        "placeholder": "gsk_...",
        "secret_key":  "GROQ_API_KEY",
        "guide":       "前往 console.groq.com → API Keys → Create API Key",
    },
    "claude": {
        "name":        "Claude Sonnet",
        "free":        False,
        "quota":       "按用量付費，每次約 $0.003",
        "url":         "https://console.anthropic.com/",
        "placeholder": "sk-ant-api03-...",
        "secret_key":  "ANTHROPIC_API_KEY",
        "guide":       "前往 console.anthropic.com → API Keys → Create Key",
    },
}


def render_ai_result_card(result: dict, compact: bool = False):
    """可重用：把 AI 分析結果渲染成卡片 HTML"""
    if not result or "error" in result:
        return

    verdict    = result.get("verdict", "觀望")
    confidence = result.get("confidence", 50)
    trend_txt  = result.get("trend_analysis", "")
    entry      = result.get("entry_price", 0) or 0
    entry_note = result.get("entry_note", "")
    tp1        = result.get("take_profit_1", 0) or 0
    tp2        = result.get("take_profit_2", 0) or 0
    sl         = result.get("stop_loss", 0) or 0
    rr         = result.get("risk_reward", "—")
    risks      = result.get("key_risks", "")
    reasoning  = result.get("reasoning", "")
    signals    = result.get("_signals", [])
    symbol     = result.get("_symbol", "")
    period     = result.get("_period", "")
    ttime      = result.get("_trigger_time", datetime.now().strftime("%H:%M:%S"))

    verdict_cls  = {"做多": "ai-verdict-bull", "做空": "ai-verdict-bear"}.get(verdict, "ai-verdict-side")
    verdict_icon = {"做多": "▲ 做多", "做空": "▼ 做空"}.get(verdict, "◆ 觀望")
    conf_color   = "#00ee66" if confidence >= 70 else "#ffcc00" if confidence >= 50 else "#ff5566"

    signal_tags = "".join(
        f'<span style="background:#1a2a1a;border:1px solid #2a4a2a;border-radius:4px;'
        f'padding:2px 7px;font-size:0.72rem;color:#88cc88;margin-right:4px;">{s}</span>'
        for s in signals
    )

    def pct_str(val, base):
        if not base or not val: return ""
        return f' ({((val-base)/base*100):+.1f}%)'

    html = (
        f'<div class="ai-panel">'
        f'<div class="ai-title">🤖 AI 信號分析'
        f'<span style="font-size:0.72rem;color:#334466;font-weight:400;margin-left:8px;">'
        f'{symbol} · {period} · {ttime}</span></div>'

        + (f'<div style="margin-bottom:10px;">{signal_tags}</div>' if signal_tags else "")

        + f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;">'
        f'<span class="ai-verdict {verdict_cls}">{verdict_icon}</span>'
        f'<div>'
        f'<div style="font-size:0.7rem;color:#5577aa;margin-bottom:2px;">信心度</div>'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<div style="width:100px;background:#141c2e;border-radius:4px;height:7px;">'
        f'<div style="width:{confidence}%;height:7px;border-radius:4px;background:{conf_color};"></div>'
        f'</div>'
        f'<span style="color:{conf_color};font-weight:700;font-size:0.88rem;">{confidence}%</span>'
        f'</div></div></div>'

        + (f'<div class="ai-section">'
           f'<div class="ai-section-title">📊 趨勢</div>'
           f'<div class="ai-reasoning">{trend_txt}</div>'
           f'</div>' if trend_txt else "")

        + f'<div class="ai-section">'
        f'<div class="ai-section-title">💰 操作價位</div>'
        f'<div class="ai-price-row">'
        f'<div class="ai-price-card"><div class="ai-price-label">進場</div>'
        f'<div class="ai-price-val ai-price-entry">${entry:.2f}</div>'
        f'<div style="font-size:0.68rem;color:#334466;">{entry_note[:20]}</div></div>'

        f'<div class="ai-price-card"><div class="ai-price-label">止盈①</div>'
        f'<div class="ai-price-val ai-price-tp">${tp1:.2f}</div>'
        f'<div style="font-size:0.68rem;color:#00aa44;">{pct_str(tp1,entry)}</div></div>'

        f'<div class="ai-price-card"><div class="ai-price-label">止盈②</div>'
        f'<div class="ai-price-val ai-price-tp">${tp2:.2f}</div>'
        f'<div style="font-size:0.68rem;color:#00aa44;">{pct_str(tp2,entry)}</div></div>'

        f'<div class="ai-price-card"><div class="ai-price-label">止損</div>'
        f'<div class="ai-price-val ai-price-sl">${sl:.2f}</div>'
        f'<div style="font-size:0.68rem;color:#cc3333;">{pct_str(sl,entry)}</div></div>'

        f'<div class="ai-price-card"><div class="ai-price-label">盈虧比</div>'
        f'<div class="ai-price-val ai-price-rr">{rr}</div></div>'
        f'</div></div>'

        + (f'<div class="ai-section">'
           f'<div class="ai-section-title">🧠 分析</div>'
           f'<div class="ai-reasoning">{reasoning}</div>'
           f'</div>' if reasoning else "")

        + (f'<div class="ai-section">'
           f'<div class="ai-section-title">⚠️ 風險</div>'
           f'<div class="ai-reasoning" style="border-left-color:#cc4444;">{risks}</div>'
           f'</div>' if risks else "")

        + f'<div class="ai-risk-warning">⚠️ AI 自動生成，僅供技術參考，不構成投資建議</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_groq_key_setup(uid: str = "default"):
    """若沒有 Groq Key，顯示設定引導（簡潔版）"""
    st.markdown(
        '<div class="ai-panel">'
        '<div class="ai-title">🤖 AI 信號分析 <span style="font-size:0.78rem;'
        'color:#00cc55;font-weight:400;">（由 Groq 免費提供）</span></div>'
        '<div style="color:#ffcc00;font-size:0.88rem;margin-bottom:8px;">'
        '⚙️ 設定 Groq API Key 即可啟用，每天免費 14,400 次</div>'
        '<div style="font-size:0.82rem;color:#7788aa;line-height:1.9;">'
        '1. 前往 <a href="https://console.groq.com/keys" target="_blank" '
        'style="color:#66aaff;">console.groq.com/keys</a>，用 Google 帳號登入<br>'
        '2. 點 <b style="color:#aabbcc">Create API Key</b>，複製 <code>gsk_...</code> 開頭的 Key<br>'
        '3. 貼到下方（或寫入 <code>.streamlit/secrets.toml</code> 永久保存）'
        '</div></div>',
        unsafe_allow_html=True,
    )
    key_input = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        key=f"groq_key_setup_input_{uid}",
    )
    if key_input:
        st.session_state["groq_key"] = key_input.strip()
        st.success("✅ Groq Key 已儲存！交易信號出現時將自動觸發 AI 分析")
        st.rerun()


def render_ai_analysis(symbol: str, interval_label: str, df: pd.DataFrame,
                       mkt: dict = None):
    """Groq 專用：顯示 Key 設定 或 手動觸發分析"""
    if not get_groq_key():
        render_groq_key_setup(uid=f"{symbol}_{interval_label}")
        return

    col_title, col_btn = st.columns([4, 1])
    with col_title:
        st.markdown(
            '<div style="font-size:0.95rem;font-weight:700;color:#66aaff;margin:4px 0;">'
            '🤖 AI 分析（Groq · 免費）</div>',
            unsafe_allow_html=True,
        )
    with col_btn:
        run_ai = st.button("🔍 立即分析", key=f"ai_btn_{symbol}_{interval_label}",
                           use_container_width=True)

    result_key = f"ai_manual_{symbol}_{interval_label}"

    if run_ai:
        with st.spinner("🤖 Groq 分析中..."):
            prompt = build_analysis_prompt(symbol, interval_label, df, mkt)
            result = call_groq_analysis(prompt)
            result["_symbol"] = symbol
            result["_period"] = interval_label
            result["_trigger_time"] = datetime.now().strftime("%H:%M:%S")
            st.session_state[result_key] = result

    result = st.session_state.get(result_key)
    if not result:
        st.markdown(
            '<div class="ai-panel" style="padding:14px 18px;">'
            '<span style="color:#334466;font-size:0.85rem;">'
            '有交易信號時 AI 自動分析 · 或點「立即分析」手動觸發</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    if "error" in result:
        err = result["error"]
        if err == "RATE_LIMIT":
            st.warning("⏳ Groq 請求頻率過高，請 60 秒後再試（每分鐘限 30 次）")
        elif err == "NO_KEY":
            st.session_state.pop("groq_key", None)
            st.rerun()
        else:
            st.error(f"❌ AI 分析失敗：{err}")
        return

    render_ai_result_card(result)


def render_signal_ai_panel():
    """顯示所有由交易信號自動觸發的 AI 分析結果（置於警示面板旁）"""
    results = st.session_state.get("ai_signal_results", [])
    if not results:
        return

    st.markdown("---")
    st.subheader("🤖 AI 信號分析記錄")
    for r in results[:5]:   # 最多顯示最新 5 筆
        if "error" not in r:
            render_ai_result_card(r)
            st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Telegram
# ══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg: str):
    # 雙重防護：沒有活躍股票時，一律不發送
    try:
        if not st.session_state.get("_active_symbols"):
            return
    except Exception:
        return
    try:
        token   = st.secrets["TELEGRAM_BOT_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}, timeout=5,
        )
    except Exception:
        pass

def add_alert(symbol: str, period: str, msg: str, atype: str = "info"):
    now = datetime.now().strftime("%H:%M:%S")
    key = f"{symbol}|{period}|{msg}"
    if key not in st.session_state.sent_alerts:
        # ── 衝突偵測：同一 symbol+period 內是否已有反向訊號 ──────────────────
        conflict_note = ""
        recent_same = [
            a for a in st.session_state.alert_log[:10]
            if a["股票"] == symbol and a["週期"] == period
        ]
        if recent_same:
            opposite = {"bull": "bear", "bear": "bull"}
            has_opposite = any(a["類型"] == opposite.get(atype) for a in recent_same)
            if has_opposite:
                if atype == "bull":
                    conflict_note = "　⚡【多空分歧】同時存在空頭訊號，短多但中線謹慎，勿重倉！"
                elif atype == "bear":
                    conflict_note = "　⚡【多空分歧】同時存在多頭訊號，注意支撐，空單設好止損！"
        final_msg = msg + conflict_note
        st.session_state.alert_log.insert(0,
            {"時間": now, "股票": symbol, "週期": period, "訊息": final_msg, "類型": atype})
        st.session_state.alert_log = st.session_state.alert_log[:200]
        st.session_state.sent_alerts.add(key)
        send_telegram(f"📊 [{symbol} {period}] {final_msg}")


# ── 高置信信號 → 自動生成模擬建議交易 ──────────────────────────────────────
# 觸發條件：10年回測 WR ≥ 95% 的信號（F6/F7/F8/F9/P6）
# 以及組合信號達到足夠置信度時

# 信號→建議對照表（key片段, direction, wr, n, atr_sl_mult, atr_tp_mult）
_HIGH_CONF_SIGNALS = {
    # key片段           方向      WR      n     SL倍  TP1倍  TP2倍  說明
    "F6-衰竭跳空上":   ("SHORT", 100.0, 157,  1.5,  2.0,  3.5,  "衰竭跳空(上)｜10年WR=100%收低"),
    "F7-衰竭跳空下":   ("LONG",  100.0, 150,  1.5,  2.0,  3.5,  "衰竭跳空(下)反彈｜10年WR=100%收高"),
    "F8-持續跳空上":   ("LONG",  100.0,  90,  1.5,  2.0,  3.5,  "持續跳空(上)｜10年WR=100%收高"),
    "F9-持續跳空下":   ("SHORT",  99.0, 105,  1.5,  2.0,  3.0,  "持續跳空(下)｜10年WR=99%收低"),
    "P6-跳空量能強化":  ("LONG",  100.0,  38,  1.2,  1.8,  3.0,  "突破跳空量能強化｜10年WR=100%"),
    "F0-超級跳空":      ("LONG",   85.0,  20,  2.0,  2.5,  4.0,  "超級跳空缺口｜強烈趨勢啟動"),
    # 突破跳空(下) - 從信號文字判斷
    "突破跳空(下)":    ("SHORT", 100.0,  46,  1.5,  2.0,  3.5,  "突破跳空(下)｜10年WR=100%收低"),
    "突破跳空(上)":    ("LONG",  100.0,  57,  1.5,  2.0,  3.5,  "突破跳空(上)｜10年WR=100%收高"),
}

def generate_trade_suggestion(symbol: str, period: str, signal_msg: str,
                               atype: str, price: float, atr: float):
    """
    根據高置信信號自動生成模擬建議交易。
    只針對 WR≥95% 的信號，計算進場/止損/止盈。
    """
    if not price or not atr or atr <= 0:
        return

    # 比對高置信信號
    matched = None
    for key_frag, params in _HIGH_CONF_SIGNALS.items():
        if key_frag in signal_msg:
            matched = params
            break

    # 若未命中高置信信號，判斷組合信號（bull/bear 且訊息含多個高WR特徵）
    if not matched:
        # 組合信號：至少含2個以下關鍵詞才觸發（置信度較低，WR約65-75%）
        bull_keys = ["MACD金叉", "EMA金叉", "底部反彈", "均線聚合突破", "OBV突破", "EMA壓縮爆發"]
        bear_keys = ["MACD死叉", "EMA死叉", "空頭排列", "衰竭", "頂背離", "均線壓制"]
        if atype == "bull":
            hits = sum(1 for k in bull_keys if k in signal_msg)
            if hits >= 1:
                matched = ("LONG", 65.0, 50, 1.2, 1.5, 2.5, f"組合多頭信號（{hits}項確認）")
        elif atype == "bear":
            hits = sum(1 for k in bear_keys if k in signal_msg)
            if hits >= 1:
                matched = ("SHORT", 65.0, 50, 1.2, 1.5, 2.5, f"組合空頭信號（{hits}項確認）")

    if not matched:
        return

    direction, wr, n_samples, sl_mult, tp1_mult, tp2_mult, desc = matched

    # 計算進場/止損/止盈
    if direction == "LONG":
        entry  = round(price, 2)
        sl     = round(price - atr * sl_mult, 2)
        tp1    = round(price + atr * tp1_mult, 2)
        tp2    = round(price + atr * tp2_mult, 2)
    else:
        entry  = round(price, 2)
        sl     = round(price + atr * sl_mult, 2)
        tp1    = round(price - atr * tp1_mult, 2)
        tp2    = round(price - atr * tp2_mult, 2)

    risk_pct  = round(abs(entry - sl) / entry * 100, 2)
    reward1   = round(abs(tp1 - entry) / abs(entry - sl), 1) if sl != entry else 0
    reward2   = round(abs(tp2 - entry) / abs(entry - sl), 1) if sl != entry else 0

    # 置信度分級
    if wr >= 99:   conf_tag = "⭐⭐⭐ 極高置信"; conf_color = "#00ff88"
    elif wr >= 90: conf_tag = "⭐⭐ 高置信";    conf_color = "#44ee66"
    elif wr >= 70: conf_tag = "⭐ 中高置信";   conf_color = "#aaee44"
    else:          conf_tag = "📊 參考";        conf_color = "#ffcc44"

    sug_key = f"{symbol}|{period}|{direction}|{entry}|{desc[:20]}"
    if sug_key in st.session_state.sent_suggestions:
        return

    st.session_state.sent_suggestions.add(sug_key)
    now = datetime.now().strftime("%H:%M:%S")
    suggestion = {
        "時間":       now,
        "股票":       symbol,
        "週期":       period,
        "方向":       direction,
        "進場":       entry,
        "止損":       sl,
        "止盈1":      tp1,
        "止盈2":      tp2,
        "風險%":      risk_pct,
        "盈虧比1":    reward1,
        "盈虧比2":    reward2,
        "WR":         wr,
        "樣本數":     n_samples,
        "置信":       conf_tag,
        "置信色":     conf_color,
        "描述":       desc,
        "來源信號":   signal_msg[:80],
        "ATR":        round(atr, 2),
        "狀態":       "待確認",   # 待確認 / 已採納 / 已忽略
    }
    st.session_state.trade_suggestions.insert(0, suggestion)
    st.session_state.trade_suggestions = st.session_state.trade_suggestions[:50]


def add_entry_tracker(symbol: str, direction: str, trigger_signal: str,
                      trigger_price: float, period_src: str,
                      atr: float = 0.0):
    """
    日K/週K高置信信號觸發後，自動建立「30分鐘進場時機追蹤」任務。
    追蹤邏輯：在30分鐘線等待均線聚合突破 / MACD金叉 / K10大陽線確認進場。
    包含：ATR止損自動計算、2小時倒計時、信號優先級
    """
    # 去重：同股同方向只保留一個追蹤（若新信號優先級更高則更新）
    existing = [t for t in st.session_state.entry_trackers
                if t["symbol"] == symbol and t["direction"] == direction
                and t["status"] == "追蹤中"]
    if existing:
        # 如果新信號優先級更高（F6/F7/F8/F9 > K18/K19 > EMA排列），覆蓋觸發信號描述
        HIGH_PRIORITY = ("F6","F7","F8","F9","K18","K19","K12","K13")
        if any(hp in trigger_signal for hp in HIGH_PRIORITY):
            existing[0]["trigger_signal"] = trigger_signal
            existing[0]["trigger_price"]  = trigger_price
            existing[0]["trigger_time"]   = datetime.now().strftime("%m/%d %H:%M")
            # 重置到期時間
            existing[0]["expire_time"]    = (datetime.now() + timedelta(hours=4)).strftime("%m/%d %H:%M")
        return

    # ATR止損計算（若未提供ATR，使用觸發價的1.5%估算）
    safe_atr  = atr if atr > 0 else trigger_price * 0.015
    sl_long   = round(trigger_price - safe_atr * 1.5, 2)   # 多頭止損：-1.5 ATR
    sl_short  = round(trigger_price + safe_atr * 1.5, 2)   # 空頭止損：+1.5 ATR
    tp1_long  = round(trigger_price + safe_atr * 2.0, 2)   # 多頭止盈1：+2 ATR
    tp2_long  = round(trigger_price + safe_atr * 4.0, 2)   # 多頭止盈2：+4 ATR
    tp1_short = round(trigger_price - safe_atr * 2.0, 2)
    tp2_short = round(trigger_price - safe_atr * 4.0, 2)

    # 有效時間（日K信號4小時，週K信號24小時，月K信號72小時）
    if "月" in period_src:
        expire_h = 72
    elif "週" in period_src:
        expire_h = 24
    else:
        expire_h = 4

    tracker = {
        "id":             len(st.session_state.entry_trackers) + 1,
        "symbol":         symbol,
        "direction":      direction,
        "trigger_signal": trigger_signal,
        "trigger_price":  trigger_price,
        "trigger_time":   datetime.now().strftime("%m/%d %H:%M"),
        "expire_time":    (datetime.now() + timedelta(hours=expire_h)).strftime("%m/%d %H:%M"),
        "expire_h":       expire_h,
        "period_src":     period_src,
        "status":         "追蹤中",
        "entry_price":    None,
        "entry_time":     None,
        "entry_signal":   None,
        "atr":            round(safe_atr, 2),
        "sl":             sl_long  if direction == "LONG" else sl_short,
        "tp1":            tp1_long if direction == "LONG" else tp1_short,
        "tp2":            tp2_long if direction == "LONG" else tp2_short,
        "rr":             round(safe_atr * 2.0 / (safe_atr * 1.5), 1),  # 固定 R:R = 1.33
    }
    st.session_state.entry_trackers.insert(0, tracker)
    st.session_state.entry_trackers = st.session_state.entry_trackers[:20]

# ══════════════════════════════════════════════════════════════════════════════
# 交易日誌系統（Trading Log System）
# 記錄：計算步驟 → 訊號決策 → 交易記錄 → 績效統計
# ══════════════════════════════════════════════════════════════════════════════

def tl_log_calc(symbol: str, period: str, step: str, detail: str,
                value=None, unit: str = "", level: str = "info"):
    """
    記錄計算步驟日誌
    level: info / trigger / skip / error
    """
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "symbol":    symbol,
        "period":    period,
        "step":      step,
        "detail":    detail,
        "value":     value,
        "unit":      unit,
        "level":     level,
    }
    st.session_state.calc_log.insert(0, entry)
    st.session_state.calc_log = st.session_state.calc_log[:500]


def tl_log_decision(symbol: str, period: str, detector: str,
                    triggered: bool, reason: str,
                    signal_type: str = "info", confidence: int = 50,
                    key_values: dict = None):
    """
    記錄偵測器決策日誌
    detector:    偵測器名稱（如 E0, I2, G7...）
    triggered:   是否觸發
    reason:      觸發/未觸發原因
    confidence:  信心度 0-100
    key_values:  關鍵計算值 dict
    """
    entry = {
        "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol":      symbol,
        "period":      period,
        "detector":    detector,
        "triggered":   triggered,
        "signal_type": signal_type,
        "reason":      reason,
        "confidence":  confidence,
        "key_values":  key_values or {},
    }
    st.session_state.decision_log.insert(0, entry)
    st.session_state.decision_log = st.session_state.decision_log[:300]


def tl_open_trade(symbol: str, direction: str, entry_price: float,
                  entry_time: str = None, size: float = 1.0,
                  stop_loss: float = None, take_profit: float = None,
                  reason: str = "", signals: list = None,
                  period: str = "") -> str:
    """
    開倉記錄
    direction: LONG / SHORT
    返回 trade_id
    """
    tid = f"T{st.session_state.trade_id_counter:04d}"
    st.session_state.trade_id_counter += 1
    now = entry_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    trade = {
        "trade_id":    tid,
        "symbol":      symbol,
        "direction":   direction,
        "entry_price": entry_price,
        "entry_time":  now,
        "size":        size,
        "stop_loss":   stop_loss,
        "take_profit": take_profit,
        "entry_reason": reason,
        "entry_signals": signals or [],
        "period":      period,
        "status":      "OPEN",
        "exit_price":  None,
        "exit_time":   None,
        "exit_reason": None,
        "pnl":         None,
        "pnl_pct":     None,
        "duration":    None,
        "calc_steps":  [],   # 開倉時的計算快照
    }
    st.session_state.open_trades[tid] = trade
    st.session_state.trade_log.insert(0, trade)
    st.session_state.trade_log = st.session_state.trade_log[:200]
    return tid


def tl_close_trade(trade_id: str, exit_price: float,
                   exit_time: str = None, reason: str = "") -> dict:
    """
    平倉記錄，計算損益
    返回平倉後的 trade dict
    """
    if trade_id not in st.session_state.open_trades:
        return {}

    trade = st.session_state.open_trades[trade_id]
    now   = exit_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ep  = trade["entry_price"]
    xp  = exit_price
    sz  = trade["size"]
    dir = trade["direction"]

    raw_pnl = (xp - ep) if dir == "LONG" else (ep - xp)
    pnl     = raw_pnl * sz
    pnl_pct = raw_pnl / ep * 100

    # 計算持倉時間
    try:
        t0 = datetime.strptime(trade["entry_time"], "%Y-%m-%d %H:%M:%S")
        t1 = datetime.strptime(now,                 "%Y-%m-%d %H:%M:%S")
        dur_min = int((t1 - t0).total_seconds() / 60)
        duration = f"{dur_min}分鐘" if dur_min < 60 else f"{dur_min//60}時{dur_min%60}分"
    except Exception:
        duration = "N/A"

    trade.update({
        "status":      "CLOSED",
        "exit_price":  exit_price,
        "exit_time":   now,
        "exit_reason": reason,
        "pnl":         round(pnl, 4),
        "pnl_pct":     round(pnl_pct, 3),
        "duration":    duration,
    })

    # 從未平倉中移除
    del st.session_state.open_trades[trade_id]

    # 更新 trade_log 中的記錄
    for i, t in enumerate(st.session_state.trade_log):
        if t["trade_id"] == trade_id:
            st.session_state.trade_log[i] = trade
            break

    return trade


def tl_calc_stats() -> dict:
    """計算整體績效統計"""
    closed = [t for t in st.session_state.trade_log if t["status"] == "CLOSED"]
    if not closed:
        return {"total": 0}

    pnls     = [t["pnl_pct"] for t in closed if t["pnl_pct"] is not None]
    wins     = [p for p in pnls if p > 0]
    losses   = [p for p in pnls if p <= 0]
    total    = len(pnls)
    win_rate = len(wins) / total * 100 if total > 0 else 0
    avg_win  = sum(wins)  / len(wins)  if wins   else 0
    avg_loss = sum(losses)/ len(losses)if losses  else 0
    profit_factor = abs(sum(wins) / sum(losses)) if sum(losses) != 0 else float("inf")
    total_pnl_pct = sum(pnls)

    # 最大回撤
    cumulative = []
    cum = 0
    for p in reversed(pnls):
        cum += p
        cumulative.append(cum)
    peak = 0
    max_dd = 0
    for c in cumulative:
        if c > peak: peak = c
        dd = peak - c
        if dd > max_dd: max_dd = dd

    return {
        "total":          total,
        "wins":           len(wins),
        "losses":         len(losses),
        "win_rate":       round(win_rate, 1),
        "avg_win":        round(avg_win, 3),
        "avg_loss":       round(avg_loss, 3),
        "profit_factor":  round(profit_factor, 2),
        "total_pnl_pct":  round(total_pnl_pct, 3),
        "max_drawdown":   round(max_dd, 3),
        "expectancy":     round(win_rate/100*avg_win + (1-win_rate/100)*avg_loss, 3),
    }


def tl_log_psychology(symbol: str, emotion: str, note: str,
                      pnl_pct: float, trade_id: str,
                      confidence: int = 50, fatigue: int = 30):
    """
    記錄交易心理狀態
    emotion:    冷靜 / 自信 / FOMO / 恐懼 / 貪婪 / 疲勞
    confidence: 信心度 0-100
    fatigue:    疲勞度 0-100
    """
    entry = {
        "timestamp":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol":     symbol,
        "trade_id":   trade_id,
        "emotion":    emotion,
        "note":       note,
        "pnl_pct":    pnl_pct,
        "confidence": confidence,
        "fatigue":    fatigue,
    }
    if "psych_log" not in st.session_state:
        st.session_state.psych_log = []
    st.session_state.psych_log.insert(0, entry)
    st.session_state.psych_log = st.session_state.psych_log[:200]
def render_trading_log():
    """完整交易日誌系統 v3.0 - 四大核心模組"""
    st.markdown("---")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      <div style="font-size:1.5rem;font-weight:900;color:#e0e8ff;font-family:'Courier New',monospace;">
        📒 TRADING LOG
      </div>
      <div style="font-size:0.72rem;color:#445577;padding:2px 10px;
                  border:1px solid #223355;border-radius:20px;font-family:monospace;">v3.0</div>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "📋 執行記錄", "🛡 風險管理", "📊 Setup績效",
        "🧠 心理日誌", "📈 績效統計", "➕ 新增交易", "🤖 AI研究"
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1: 執行記錄（Entry / Exit / Size / PnL / R-multiple）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[0]:
        st.markdown("#### 📋 交易執行記錄")
        all_log = st.session_state.trade_log
        open_tr = st.session_state.open_trades

        # ── 未平倉 ───────────────────────────────────────────────────────────
        if open_tr:
            st.markdown(f"**🟡 持倉中（{len(open_tr)}筆）**")
            for tid, t in open_tr.items():
                dc   = "#00ee66" if t["direction"]=="LONG" else "#ff5566"
                dl   = "▲ LONG"  if t["direction"]=="LONG" else "▼ SHORT"
                sl   = t.get("stop_loss"); tp = t.get("take_profit")
                risk = abs(t["entry_price"] - sl) if sl else None
                rr   = abs((tp - t["entry_price"]) / risk) if (tp and risk) else None
                st.markdown(f"""
                <div style="background:#0c1220;border-left:3px solid {dc};
                            border-radius:6px;padding:10px 14px;margin:4px 0;font-family:monospace;font-size:0.82rem;">
                  <div style="display:flex;justify-content:space-between;">
                    <div>
                      <span style="color:#7799cc;">{tid}</span>
                      <span style="color:{dc};font-weight:700;margin:0 8px;">{dl}</span>
                      <span style="color:#ccd6ee;font-weight:700;">{t['symbol']}</span>
                      <span style="color:#556677;margin-left:6px;">{t.get('period','')}</span>
                    </div>
                    <span style="color:#ffdd44;font-size:0.72rem;">⏳ OPEN</span>
                  </div>
                  <div style="display:flex;gap:20px;margin-top:6px;flex-wrap:wrap;">
                    <div><span style="color:#445577;">Entry</span> <span style="color:#ccd6ee;font-weight:600;">{t['entry_price']:.2f}</span></div>
                    <div><span style="color:#445577;">Size</span>  <span style="color:#ccd6ee;">{t['size']}</span></div>
                    <div><span style="color:#ff5566;">Stop</span>  <span style="color:#ff8888;">{f'{sl:.2f}' if sl else '—'}</span></div>
                    <div><span style="color:#44dd88;">Target</span><span style="color:#88ffcc;">{f'{tp:.2f}' if tp else '—'}</span></div>
                    <div><span style="color:#cc88ff;">R:R</span>   <span style="color:#ddaaff;">{f'{rr:.1f}:1' if rr else '—'}</span></div>
                    <div><span style="color:#445577;">Setup</span> <span style="color:#aabbcc;">{t.get('setup','—')}</span></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(f"平倉 {tid}"):
                    cx1,cx2,cx3 = st.columns(3)
                    with cx1: x_px = st.number_input("出場價", value=float(t["entry_price"]), step=0.01, key=f"xpx_{tid}")
                    with cx2: x_rs = st.text_input("出場原因", key=f"xrs_{tid}")
                    with cx3: x_em = st.selectbox("情緒狀態", ["冷靜","貪婪","恐懼","FOMO","疲勞","自信"], key=f"xem_{tid}")
                    if st.button(f"✅ 確認平倉 {tid}", key=f"xcl_{tid}", type="primary"):
                        res = tl_close_trade(tid, x_px, reason=x_rs)
                        res["exit_emotion"] = x_em
                        # 記錄心理日誌
                        tl_log_psychology(t["symbol"], x_em, x_rs, res.get("pnl_pct",0), tid)
                        st.success(f"平倉 {tid}：{res['pnl_pct']:+.2f}%")
                        st.rerun()
        else:
            st.info("目前無未平倉交易")

        # ── 已平倉記錄表 ─────────────────────────────────────────────────────
        closed = [t for t in all_log if t["status"]=="CLOSED"]
        if closed:
            st.markdown(f"**📋 已平倉記錄（{len(closed)}筆）**")
            rows = []
            for t in closed:
                ep   = t["entry_price"]; xp = t.get("exit_price", ep)
                sl   = t.get("stop_loss"); risk = abs(ep-sl) if sl else None
                pnl  = t.get("pnl_pct",0) or 0
                r_mult = pnl/100*ep/risk if (risk and risk>0) else None
                rows.append({
                    "ID":      t["trade_id"],
                    "股票":    t["symbol"],
                    "方向":    t["direction"],
                    "Setup":   t.get("setup","—"),
                    "Entry":   ep,
                    "Exit":    xp,
                    "Stop":    f"{sl:.2f}" if sl else "—",
                    "Size":    t["size"],
                    "PnL%":    f"{pnl:+.2f}%",
                    "PnL$":    f"{t.get('pnl',0):+.2f}",
                    "R-mult":  f"{r_mult:+.2f}R" if r_mult else "—",
                    "持倉":    t.get("duration","—"),
                    "情緒":    t.get("exit_emotion","—"),
                })
            df_c = pd.DataFrame(rows)
            def _color(val):
                if "+" in str(val) and val!="—": return "color:#00ee66;font-weight:bold"
                if "-" in str(val) and val!="—": return "color:#ff5566;font-weight:bold"
                return ""
            st.dataframe(df_c.style.applymap(_color, subset=["PnL%","PnL$","R-mult"]),
                         use_container_width=True, height=280)
            csv = df_c.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 下載 CSV", csv,
                               f"trades_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                               mime="text/csv")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2: 風險管理（Position Sizing / Risk% / Stop / R-multiples）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[1]:
        st.markdown("#### 🛡 風險管理儀表板")
        rc1, rc2 = st.columns([1,2])
        with rc1:
            st.markdown("**⚙️ 風控參數**")
            acct_size  = st.number_input("帳戶資金 ($)", value=float(st.session_state.get("_acct_size",100000)), step=1000.0, key="_acct_size_input")
            risk_pct   = st.number_input("單筆風險 %", value=float(st.session_state.get("_risk_pct",1.0)), step=0.1, min_value=0.1, max_value=5.0, key="_risk_pct_input")
            st.session_state["_acct_size"] = acct_size
            st.session_state["_risk_pct"]  = risk_pct
            max_risk_amt = acct_size * risk_pct / 100
            st.markdown(f"""
            <div style="background:#0c1220;border:1px solid #1e3050;border-radius:8px;padding:12px;margin-top:8px;font-family:monospace;">
              <div style="color:#445577;font-size:0.72rem;">單筆最大風險金額</div>
              <div style="color:#ff8855;font-size:1.4rem;font-weight:900;">${max_risk_amt:,.0f}</div>
              <div style="color:#445577;font-size:0.72rem;margin-top:8px;">當前持倉風險</div>
              <div style="color:#ffdd44;font-size:1.1rem;font-weight:700;">
                ${sum(abs(t['entry_price']-t.get('stop_loss',t['entry_price']))*t['size']
                      for t in st.session_state.open_trades.values()
                      if t.get('stop_loss')):,.0f}
              </div>
            </div>
            """, unsafe_allow_html=True)

        with rc2:
            st.markdown("**🧮 倉位計算器**")
            ps1, ps2, ps3 = st.columns(3)
            with ps1: ps_entry = st.number_input("進場價", value=400.0, step=0.01, key="ps_entry")
            with ps2: ps_stop  = st.number_input("止損價", value=395.0, step=0.01, key="ps_stop")
            with ps3: ps_sym   = st.text_input("股票",   value="TSLA",               key="ps_sym")
            if ps_entry != ps_stop:
                risk_per_share = abs(ps_entry - ps_stop)
                shares = int(max_risk_amt / risk_per_share)
                total_exposure = shares * ps_entry
                pct_of_acct    = total_exposure / acct_size * 100
                st.markdown(f"""
                <div style="background:#0a1020;border:1px solid #223355;border-radius:8px;
                            padding:14px;font-family:monospace;">
                  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;text-align:center;">
                    <div>
                      <div style="color:#445577;font-size:0.72rem;">建議股數</div>
                      <div style="color:#00ee66;font-size:1.5rem;font-weight:900;">{shares}</div>
                    </div>
                    <div>
                      <div style="color:#445577;font-size:0.72rem;">每股風險</div>
                      <div style="color:#ff8855;font-size:1.5rem;font-weight:900;">${risk_per_share:.2f}</div>
                    </div>
                    <div>
                      <div style="color:#445577;font-size:0.72rem;">總曝險</div>
                      <div style="color:#ffdd44;font-size:1.5rem;font-weight:900;">${total_exposure:,.0f}</div>
                    </div>
                    <div>
                      <div style="color:#445577;font-size:0.72rem;">佔帳戶</div>
                      <div style="color:#cc88ff;font-size:1.5rem;font-weight:900;">{pct_of_acct:.1f}%</div>
                    </div>
                  </div>
                  <div style="margin-top:12px;padding:8px;background:#141c2e;border-radius:6px;
                              font-size:0.78rem;color:#667799;">
                    止損金額: <span style="color:#ff5566;">${shares*risk_per_share:,.0f}</span>
                    （{risk_pct}% 帳戶）　
                    1R = ${shares*risk_per_share:,.0f}　
                    2R目標 = ${ps_entry + (ps_entry-ps_stop)*2:.2f}　
                    3R目標 = ${ps_entry + (ps_entry-ps_stop)*3:.2f}
                  </div>
                </div>
                """, unsafe_allow_html=True)

        # ── R-multiple 分布圖 ─────────────────────────────────────────────────
        closed_r = [t for t in st.session_state.trade_log
                    if t["status"]=="CLOSED" and t.get("stop_loss") and t.get("pnl_pct")]
        if len(closed_r) >= 2:
            st.markdown("**📊 R-Multiple 分布**")
            r_mults = []
            for t in closed_r:
                ep = t["entry_price"]; sl = t["stop_loss"]; risk = abs(ep-sl)
                if risk > 0:
                    r_mults.append(t["pnl_pct"]/100*ep/risk)
            if r_mults:
                import plotly.graph_objects as go
                colors = ["#00ee66" if r>=0 else "#ff5566" for r in r_mults]
                fig = go.Figure(go.Bar(y=r_mults, marker_color=colors, opacity=0.85, marker_line_width=0))
                fig.add_hline(y=0, line_color="#334455", line_width=1)
                fig.add_hline(y=1, line_color="rgba(0,238,102,0.25)", line_width=1, line_dash="dot")
                fig.add_hline(y=2, line_color="rgba(255,221,68,0.25)", line_width=1, line_dash="dot")
                fig.update_layout(paper_bgcolor="#0a0e18", plot_bgcolor="#0c1220",
                                  font=dict(color="#7799cc",family="monospace"),
                                  height=220, margin=dict(l=40,r=10,t=10,b=30),
                                  yaxis=dict(gridcolor="#1a2535",title="R"),
                                  xaxis=dict(gridcolor="#1a2535",title="交易序號"))
                st.plotly_chart(fig, use_container_width=True)
                avg_r = sum(r_mults)/len(r_mults)
                st.markdown(f"平均R: **{avg_r:+.2f}R**　最大虧損: **{min(r_mults):.2f}R**　最大獲利: **{max(r_mults):.2f}R**")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3: Setup績效（每個偵測器的實際勝率/盈虧/Expectancy）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[2]:
        st.markdown("#### 📊 Setup 績效分析")
        closed_all = [t for t in st.session_state.trade_log if t["status"]=="CLOSED"]
        if not closed_all:
            st.info("尚無已平倉交易記錄")
        else:
            from collections import defaultdict
            setup_stats = defaultdict(lambda: {"trades":[]})
            for t in closed_all:
                s = t.get("setup","未分類")
                pnl = t.get("pnl_pct",0) or 0
                ep  = t["entry_price"]; sl = t.get("stop_loss")
                risk = abs(ep-sl) if sl else None
                r = pnl/100*ep/risk if (risk and risk>0) else None
                setup_stats[s]["trades"].append({"pnl":pnl,"r":r,"tid":t["trade_id"]})

            # 計算每個 Setup 的統計
            rows_s = []
            for setup, data in sorted(setup_stats.items()):
                trs   = data["trades"]
                n     = len(trs)
                wins  = [x for x in trs if x["pnl"]>0]
                loss  = [x for x in trs if x["pnl"]<=0]
                wr    = len(wins)/n*100 if n>0 else 0
                avg_w = sum(x["pnl"] for x in wins)/len(wins)   if wins else 0
                avg_l = sum(x["pnl"] for x in loss)/len(loss)   if loss else 0
                exp   = wr/100*avg_w + (1-wr/100)*avg_l
                r_vals = [x["r"] for x in trs if x["r"] is not None]
                avg_r  = sum(r_vals)/len(r_vals) if r_vals else None
                rows_s.append({
                    "Setup":      setup,
                    "筆數":       n,
                    "勝率%":      f"{wr:.0f}%",
                    "平均獲利%":  f"{avg_w:+.2f}%",
                    "平均虧損%":  f"{avg_l:+.2f}%",
                    "期望值%":    f"{exp:+.2f}%",
                    "平均R":      f"{avg_r:+.2f}R" if avg_r else "—",
                    "評級":       ("⭐⭐⭐" if wr>=60 and (avg_r or 0)>=1.5
                                   else "⭐⭐" if wr>=50 else "⭐" if exp>0 else "❌"),
                })

            df_s = pd.DataFrame(rows_s).sort_values("期望值%", ascending=False)
            def _color_setup(val):
                if "+" in str(val): return "color:#00ee66;font-weight:bold"
                if "-" in str(val): return "color:#ff5566;font-weight:bold"
                if "⭐" in str(val): return "color:#ffdd44"
                if "❌" in str(val): return "color:#ff4444"
                return ""
            st.dataframe(df_s.style.applymap(_color_setup,
                         subset=["平均獲利%","平均虧損%","期望值%","平均R","評級"]),
                         use_container_width=True, height=320)

            # 最佳/最差 Setup
            best = rows_s[0] if rows_s else None
            if best:
                st.markdown(f"""
                <div style="display:flex;gap:12px;margin-top:8px;">
                  <div style="background:#0d2218;border:1px solid #00ee6633;border-radius:8px;
                              padding:10px 16px;flex:1;font-family:monospace;font-size:0.82rem;">
                    <div style="color:#00ee66;font-weight:700;">🏆 最佳 Setup</div>
                    <div style="color:#ccd6ee;margin-top:4px;">{best['Setup']}</div>
                    <div style="color:#aabbcc;">期望值 {best['期望值%']}　勝率 {best['勝率%']}　{best['平均R']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4: 心理日誌（情緒/疲勞/FOMO/信心 vs 交易結果）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[3]:
        st.markdown("#### 🧠 交易心理日誌")
        psych_log = st.session_state.get("psych_log", [])

        # 情緒 vs 勝率統計
        if psych_log:
            from collections import defaultdict
            emo_stats = defaultdict(lambda:{"wins":0,"total":0,"pnls":[]})
            for e in psych_log:
                em = e.get("emotion","未知")
                emo_stats[em]["total"] += 1
                emo_stats[em]["pnls"].append(e.get("pnl_pct",0))
                if e.get("pnl_pct",0) > 0: emo_stats[em]["wins"] += 1

            st.markdown("**📊 情緒狀態 vs 勝率（核心統計）**")
            emo_colors = {
                "冷靜":"#00ee66","自信":"#44dd88",
                "FOMO":"#ff5566","恐懼":"#ff8855",
                "貪婪":"#ffaa00","疲勞":"#cc6655","其他":"#7799cc"
            }
            cards = ['<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:16px;">']
            for em, data in sorted(emo_stats.items(), key=lambda x:-x[1]["total"]):
                n    = data["total"]; wins = data["wins"]
                wr   = wins/n*100 if n>0 else 0
                avg  = sum(data["pnls"])/n if n>0 else 0
                col  = emo_colors.get(em,"#7799cc")
                warn = "⚠️" if (wr<40 and n>=2) else ""
                cards.append(f"""
                <div style="background:#0c1220;border:1px solid {col}44;border-left:3px solid {col};
                            border-radius:8px;padding:10px 14px;min-width:120px;font-family:monospace;">
                  <div style="color:{col};font-weight:700;font-size:0.85rem;">{warn}{em}</div>
                  <div style="color:#ccd6ee;font-size:1.4rem;font-weight:900;">{wr:.0f}%</div>
                  <div style="background:#141c2e;border-radius:2px;height:3px;margin:4px 0;">
                    <div style="width:{wr}%;background:{col};height:3px;border-radius:2px;"></div>
                  </div>
                  <div style="color:#445566;font-size:0.72rem;">{n}筆　avg{avg:+.1f}%</div>
                </div>""")
            cards.append("</div>")
            st.markdown("".join(cards), unsafe_allow_html=True)

            # 情緒交易警告
            bad_emotions = {em:d for em,d in emo_stats.items()
                            if d["total"]>=2 and d["wins"]/d["total"]<0.4}
            if bad_emotions:
                st.markdown("""
                <div style="background:#2a0d0d;border:1px solid #ff444444;border-radius:8px;
                            padding:12px 16px;margin-bottom:12px;">
                  <div style="color:#ff5566;font-weight:700;margin-bottom:6px;">
                    🚨 情緒交易警告
                  </div>""" +
                "".join(f'<div style="color:#cc8888;font-size:0.82rem;margin:2px 0;">'
                        f'{em}狀態下勝率僅 {d["wins"]/d["total"]*100:.0f}%'
                        f'（{d["total"]}筆），建議此狀態下暫停交易</div>'
                        for em,d in bad_emotions.items()) +
                "</div>", unsafe_allow_html=True)

            # 心理日誌列表
            st.markdown("**📝 心理記錄**")
            for e in psych_log[-20:][::-1]:
                em  = e.get("emotion","—")
                col = emo_colors.get(em,"#7799cc")
                pnl = e.get("pnl_pct",0)
                st.markdown(f"""
                <div style="background:#0c1220;border-left:2px solid {col};
                            border-radius:4px;padding:6px 12px;margin:3px 0;
                            font-family:monospace;font-size:0.78rem;">
                  <span style="color:{col};font-weight:700;">{em}</span>
                  <span style="color:#445566;margin:0 8px;">{e.get('timestamp','')}</span>
                  <span style="color:{'#00ee66' if pnl>=0 else '#ff5566'};font-weight:600;">{pnl:+.2f}%</span>
                  <span style="color:#667788;margin-left:10px;">{e.get('note','')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("尚無心理記錄。平倉時選擇情緒狀態即可自動記錄。")

        # 手動記錄心理狀態
        with st.expander("✍️ 手動記錄當前心理狀態"):
            pm1, pm2 = st.columns(2)
            with pm1:
                pm_em  = st.selectbox("情緒", ["冷靜","自信","FOMO","恐懼","貪婪","疲勞"], key="pm_em")
                pm_conf= st.slider("信心度", 0, 100, 60, key="pm_conf")
            with pm2:
                pm_fat = st.slider("疲勞度", 0, 100, 30, key="pm_fat")
                pm_note= st.text_input("備注（市場觀察/今日狀態）", key="pm_note")
            if st.button("📝 記錄心理狀態", key="pm_save"):
                tl_log_psychology("—", pm_em, pm_note, 0, "—",
                                  confidence=pm_conf, fatigue=pm_fat)
                st.success("已記錄")
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 5: 績效統計（完整Risk-adjusted）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[4]:
        st.markdown("#### 📈 績效統計（Risk-Adjusted）")
        stats = tl_calc_stats()
        if stats.get("total",0) == 0:
            st.info("尚無已平倉交易")
        else:
            t  = stats["total"]; w = stats["wins"]; l = stats["losses"]
            wr = stats["win_rate"]; pf = stats["profit_factor"]
            tot = stats["total_pnl_pct"]; dd = stats["max_drawdown"]
            exp = stats["expectancy"]
            wr_c  = "#00ee66" if wr>=55 else "#ffdd44" if wr>=40 else "#ff5566"
            pnl_c = "#00ee66" if tot>=0 else "#ff5566"
            pf_c  = "#00ee66" if pf>=1.5 else "#ffdd44" if pf>=1 else "#ff5566"

            # KPI 行
            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0;">
              {''.join(f"""
              <div style="background:#0a1020;border:1px solid #1e3050;border-radius:10px;padding:14px;text-align:center;">
                <div style="color:#445577;font-size:0.72rem;">{label}</div>
                <div style="color:{color};font-size:1.6rem;font-weight:900;font-family:monospace;">{value}</div>
                <div style="color:#445566;font-size:0.7rem;">{sub}</div>
              </div>"""
              for label,value,color,sub in [
                ("總交易",f"{t}",    "#ccd6ee",f"勝{w}/敗{l}"),
                ("勝率",  f"{wr:.0f}%",wr_c,    f"W:{w} L:{l}"),
                ("累計損益",f"{tot:+.1f}%",pnl_c,f"期望值{exp:+.2f}%"),
                ("獲利因子",f"{pf:.2f}",pf_c,   f"最大回撤{dd:.1f}%"),
              ])}
            </div>
            """, unsafe_allow_html=True)

            # 盈虧曲線
            closed_c = [t for t in st.session_state.trade_log if t["status"]=="CLOSED"]
            if len(closed_c) >= 2:
                import plotly.graph_objects as go
                pnls = [t.get("pnl_pct",0) for t in reversed(closed_c)]
                cum  = []; s=0
                for p in pnls: s+=p; cum.append(s)
                colors = ["#00ee66" if p>=0 else "#ff5566" for p in pnls]
                fig = go.Figure()
                fig.add_trace(go.Bar(y=pnls, name="單筆%", marker_color=colors,
                                     opacity=0.7, marker_line_width=0))
                fig.add_trace(go.Scatter(y=cum, name="累計%", mode="lines+markers",
                                         line=dict(color="#66bbff",width=2),
                                         marker=dict(size=4)))
                fig.update_layout(paper_bgcolor="#0a0e18",plot_bgcolor="#0c1220",
                                  font=dict(color="#7799cc",family="monospace"),
                                  height=260,margin=dict(l=40,r=10,t=10,b=30),
                                  legend=dict(orientation="h",y=1.1),
                                  yaxis=dict(gridcolor="#1a2535",zeroline=True,
                                             zerolinecolor="#334455"),
                                  xaxis=dict(gridcolor="#1a2535"))
                st.plotly_chart(fig, use_container_width=True)

            # 詳細統計
            st.markdown(f"""
            <div style="background:#0c1220;border:1px solid #1e2e48;border-radius:8px;
                        padding:14px 20px;font-family:monospace;font-size:0.82rem;">
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;">
                <div><span style="color:#445577;">平均獲利</span><span style="color:#00ee66;font-weight:700;margin-left:10px;">+{stats['avg_win']:.2f}%</span></div>
                <div><span style="color:#445577;">平均虧損</span><span style="color:#ff5566;font-weight:700;margin-left:10px;">{stats['avg_loss']:.2f}%</span></div>
                <div><span style="color:#445577;">盈虧比</span><span style="color:#ffdd44;font-weight:700;margin-left:10px;">{f"{abs(stats['avg_win']/stats['avg_loss']):.2f}:1" if stats['avg_loss'] != 0 else '∞'}</span></div>
                <div><span style="color:#445577;">最大回撤</span><span style="color:#ff8855;font-weight:700;margin-left:10px;">-{dd:.2f}%</span></div>
                <div><span style="color:#445577;">期望值/筆</span><span style="color:{'#00ee66' if exp>=0 else '#ff5566'};font-weight:700;margin-left:10px;">{exp:+.3f}%</span></div>
                <div><span style="color:#445577;">獲利因子</span><span style="color:{pf_c};font-weight:700;margin-left:10px;">{pf:.2f}</span></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 6: 新增交易（手動完整填寫）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[5]:
        st.markdown("#### ➕ 新增交易記錄")
        na1, na2, na3 = st.columns(3)
        with na1:
            na_sym  = st.text_input("股票代號", "TSLA", key="na_sym").upper()
            na_dir  = st.selectbox("方向", ["LONG","SHORT"], key="na_dir")
            na_setup= st.selectbox("Setup類型", [
                "G7-長盤整突破","E0-底部反彈","I1-MACD底背離","I2-MACD頂背離",
                "N1-ORB突破","N2-整理回測","N3-關鍵水平","O1-MTF共振",
                "D5-空頭排列","D6-均線壓制",
                "P1-VIX恐慌反彈","P2-VIX暴漲反向","P3-射擊之星","P5-連跌反彈","P6-跳空量能",
                "手動/其他"
            ], key="na_setup")
        with na2:
            na_ep   = st.number_input("進場價 (Entry)", value=400.0, step=0.01, key="na_ep")
            na_sl   = st.number_input("止損價 (Stop)",  value=395.0, step=0.01, key="na_sl")
            na_tp   = st.number_input("目標價 (Target)",value=410.0, step=0.01, key="na_tp")
        with na3:
            na_sz   = st.number_input("股數 (Size)",    value=100.0, step=10.0,  key="na_sz")
            na_em   = st.selectbox("進場情緒", ["冷靜","自信","FOMO","恐懼","貪婪","疲勞"], key="na_em")
            na_period= st.text_input("週期", "日K", key="na_period")
        na_reason = st.text_input("進場理由（可填入觸發訊號）", key="na_reason",
                                   placeholder="例：G7爆量突破399+EMA5金叉+縮量回測守住")
        na_note   = st.text_area("交易備注（市場環境/計劃）", key="na_note", height=80,
                                  placeholder="例：VIX=25高恐慌，但TSLA日K出現底背離，計劃若跌破395立即止損")

        if st.button("📝 記錄開倉", type="primary", key="na_open"):
            if na_sym and na_ep > 0:
                # 計算R:R
                risk_per  = abs(na_ep - na_sl)
                reward    = abs(na_tp - na_ep)
                rr_ratio  = reward/risk_per if risk_per > 0 else 0
                acct      = st.session_state.get("_acct_size",100000)
                rp        = st.session_state.get("_risk_pct",1.0)
                max_loss  = acct * rp / 100
                suggest_sz= int(max_loss / risk_per) if risk_per > 0 else 0

                tid = tl_open_trade(
                    symbol=na_sym, direction=na_dir,
                    entry_price=na_ep, size=na_sz,
                    stop_loss=na_sl if na_sl!=na_ep else None,
                    take_profit=na_tp if na_tp!=na_ep else None,
                    reason=na_reason, period=na_period,
                    signals=na_reason.split("＋") if na_reason else [],
                )
                st.session_state.open_trades[tid]["setup"]         = na_setup
                st.session_state.open_trades[tid]["entry_emotion"] = na_em
                st.session_state.open_trades[tid]["note"]          = na_note
                # 記錄心理日誌
                tl_log_psychology(na_sym, na_em, f"開倉 {na_dir} {na_ep}", 0, tid)
                tl_log_calc(na_sym, na_period, "手動開倉",
                            f"{na_dir} @ {na_ep} | SL:{na_sl} | TP:{na_tp} | R:R={rr_ratio:.1f}",
                            na_ep, "USD", "trigger")
                st.success(f"✅ 已記錄 {tid}：{na_dir} {na_sym} @ {na_ep:.2f}"
                           f"　R:R={rr_ratio:.1f}:1　建議股數={suggest_sz}（風控{rp}%）")
                st.rerun()
            else:
                st.error("請填寫股票代號和進場價格")

        # 快速平倉
        if st.session_state.open_trades:
            st.markdown("---")
            st.markdown("**🔒 快速平倉**")
            qc1,qc2,qc3,qc4 = st.columns(4)
            with qc1: q_tid = st.selectbox("選擇交易", list(st.session_state.open_trades.keys()), key="q_tid")
            with qc2: q_xp  = st.number_input("出場價", value=400.0, step=0.01, key="q_xp")
            with qc3: q_em  = st.selectbox("出場情緒", ["冷靜","自信","FOMO","恐懼","貪婪","疲勞"], key="q_em")
            with qc4: q_rsn = st.text_input("出場原因", key="q_rsn")
            if st.button("🔒 確認平倉", type="secondary", key="q_close"):
                res = tl_close_trade(q_tid, q_xp, reason=q_rsn)
                res["exit_emotion"] = q_em
                tl_log_psychology(res["symbol"], q_em, q_rsn, res.get("pnl_pct",0), q_tid)
                pnl_icon = "🟢" if res["pnl_pct"]>=0 else "🔴"
                st.success(f"{pnl_icon} {q_tid} 平倉：{res['pnl_pct']:+.2f}% | {res['duration']}")
                st.rerun()

        # 清除
        st.markdown("---")
        if st.button("🗑 清除全部交易日誌", key="clear_all_tl", type="secondary"):
            for k in ["trade_log","calc_log","decision_log","psych_log"]:
                st.session_state[k] = []
            st.session_state.open_trades      = {}
            st.session_state.trade_id_counter = 1
            st.success("已清除")
            st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 7: AI 交易研究（自動發現最佳Setup / 市場環境 / 倉位）
    # ══════════════════════════════════════════════════════════════════════════
    with tabs[6]:
        render_ai_research_tab()
# ══════════════════════════════════════════════════════════════════════════════
# AI 交易研究系統 - Trading Intelligence Platform
# ══════════════════════════════════════════════════════════════════════════════

def _build_research_context() -> dict:
    """從交易日誌萃取結構化數據供 AI 分析"""
    closed   = [t for t in st.session_state.trade_log if t["status"] == "CLOSED"]
    psych    = st.session_state.get("psych_log", [])
    dec_log  = st.session_state.get("decision_log", [])
    alerts   = st.session_state.get("alert_log", [])

    if not closed:
        return {}

    from collections import defaultdict

    # ── Setup 統計 ───────────────────────────────────────────────────────────
    setup_data = defaultdict(lambda: {"trades": [], "pnls": [], "r_mults": []})
    for t in closed:
        s   = t.get("setup", "未分類")
        pnl = t.get("pnl_pct", 0) or 0
        ep  = t["entry_price"]; sl = t.get("stop_loss")
        risk = abs(ep - sl) if sl else None
        r    = pnl / 100 * ep / risk if (risk and risk > 0) else None
        setup_data[s]["pnls"].append(pnl)
        if r: setup_data[s]["r_mults"].append(r)

    setup_summary = {}
    for s, d in setup_data.items():
        n    = len(d["pnls"])
        wins = [p for p in d["pnls"] if p > 0]
        avg_r = sum(d["r_mults"]) / len(d["r_mults"]) if d["r_mults"] else None
        setup_summary[s] = {
            "n": n,
            "win_rate": len(wins) / n * 100,
            "avg_pnl": sum(d["pnls"]) / n,
            "total_pnl": sum(d["pnls"]),
            "avg_r": round(avg_r, 2) if avg_r else None,
        }

    # ── 情緒 vs 績效 ─────────────────────────────────────────────────────────
    emotion_data = defaultdict(lambda: {"wins": 0, "total": 0, "pnls": []})
    for e in psych:
        em = e.get("emotion", "未知")
        emotion_data[em]["total"] += 1
        pnl = e.get("pnl_pct", 0)
        emotion_data[em]["pnls"].append(pnl)
        if pnl > 0: emotion_data[em]["wins"] += 1

    emotion_summary = {
        em: {
            "win_rate": d["wins"]/d["total"]*100 if d["total"] else 0,
            "avg_pnl": sum(d["pnls"])/len(d["pnls"]) if d["pnls"] else 0,
            "n": d["total"],
        }
        for em, d in emotion_data.items()
    }

    # ── 時間段分析（早盤/午盤/尾盤）────────────────────────────────────────
    time_data = defaultdict(list)
    for t in closed:
        try:
            h = int(t["entry_time"][11:13])
            if   h < 10:  slot = "早盤(9-10)"
            elif h < 12:  slot = "上午(10-12)"
            elif h < 14:  slot = "午盤(12-14)"
            elif h < 16:  slot = "下午(14-16)"
            else:          slot = "尾盤(16+)"
            time_data[slot].append(t.get("pnl_pct", 0) or 0)
        except Exception:
            pass

    time_summary = {
        slot: {"avg_pnl": sum(v)/len(v), "n": len(v), "win_rate": len([x for x in v if x>0])/len(v)*100}
        for slot, v in time_data.items() if v
    }

    # ── 倉位大小 vs 績效 ─────────────────────────────────────────────────────
    size_buckets = {"小倉(<50)": [], "中倉(50-200)": [], "大倉(>200)": []}
    for t in closed:
        sz = t.get("size", 0)
        p  = t.get("pnl_pct", 0) or 0
        if sz < 50:    size_buckets["小倉(<50)"].append(p)
        elif sz < 200: size_buckets["中倉(50-200)"].append(p)
        else:          size_buckets["大倉(>200)"].append(p)

    size_summary = {
        k: {"avg_pnl": sum(v)/len(v), "n": len(v)}
        for k, v in size_buckets.items() if v
    }

    # ── 最近警示信號統計 ─────────────────────────────────────────────────────
    signal_counts = defaultdict(int)
    for a in alerts[:100]:
        for kw in ["G7","E0","I1","I2","D5","D6","N1","N2","N3","O1","K3","C3","M1","M4"]:
            if kw in a.get("訊息", ""):
                signal_counts[kw] += 1

    return {
        "total_trades":    len(closed),
        "setup_summary":   setup_summary,
        "emotion_summary": emotion_summary,
        "time_summary":    time_summary,
        "size_summary":    size_summary,
        "signal_counts":   dict(signal_counts),
        "overall_win_rate": len([t for t in closed if (t.get("pnl_pct",0) or 0)>0]) / len(closed) * 100,
        "overall_pnl":      sum(t.get("pnl_pct",0) or 0 for t in closed),
    }


def _call_ai_research(question: str, context: dict, mode: str) -> str:
    """呼叫 Groq API 進行交易研究分析（使用現有 Groq key）"""
    import json

    api_key = get_groq_key()
    if not api_key:
        return "❌ 未設置 API Key，請在側欄輸入 Groq API Key"

    system_prompts = {
        "setup": "你是頂尖量化交易分析師。用繁體中文分析Setup績效，直接列出排名和可操作建議，語氣精準有力如Bloomberg報告。",
        "market": "你是市場環境分析師。用繁體中文分析最適合的市場環境、交易時段和情緒管理建議。",
        "position": "你是風險管理專家。用繁體中文分析最優倉位大小、止損設置和資金管理規則，基於Kelly公式。",
    }

    ctx_str = json.dumps(context, ensure_ascii=False, indent=2)
    user_msg = f"""交易數據：
{ctx_str}

問題：{question}

要求：1)基於數據給具體結論 2)識別3個最重要發現 3)給立即可執行建議 4)用繁體中文純文字回覆"""

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": system_prompts.get(mode, system_prompts["setup"])},
                    {"role": "user",   "content": user_msg},
                ],
                "max_tokens": 1500,
                "temperature": 0.4,
            },
            timeout=45,
        )
        if resp.status_code == 401:
            return "❌ Groq API Key 無效"
        if resp.status_code == 429:
            return "⏱ 請求頻率限制，請稍後重試"
        if resp.status_code != 200:
            return f"❌ API 錯誤 {resp.status_code}"
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⏱ 請求超時（45秒），請稍後重試"
    except Exception as e:
        return f"❌ 錯誤：{type(e).__name__}: {e}"


def render_ai_research_tab():
    """AI 交易研究介面 - Bloomberg Terminal 風格"""
    # ── 掃描線背景 + 終端機美學 ──────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600;700&family=Orbitron:wght@700;900&display=swap');
    .tip-terminal {
        background: #000;
        border: 1px solid #ff9900;
        border-radius: 4px;
        padding: 20px;
        font-family: 'IBM Plex Mono', monospace;
        position: relative;
        overflow: hidden;
    }
    .tip-terminal::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255,153,0,0.015) 2px,
            rgba(255,153,0,0.015) 4px
        );
        pointer-events: none;
    }
    .tip-header {
        font-family: 'Orbitron', monospace;
        color: #ff9900;
        font-size: 0.65rem;
        letter-spacing: 3px;
        margin-bottom: 12px;
        border-bottom: 1px solid #ff990044;
        padding-bottom: 8px;
    }
    .tip-rank { color: #ff9900; font-weight: 700; }
    .tip-pos  { color: #00ff88; }
    .tip-neg  { color: #ff3333; }
    .tip-dim  { color: #666; font-size: 0.78rem; }
    .tip-val  { color: #ffcc44; font-weight: 600; }
    .tip-ai-output {
        background: #050505;
        border: 1px solid #ff990066;
        border-left: 3px solid #ff9900;
        border-radius: 3px;
        padding: 16px 20px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        color: #ccaa77;
        line-height: 1.8;
        white-space: pre-wrap;
        margin-top: 12px;
    }
    .tip-btn {
        background: #0a0a0a;
        border: 1px solid #ff9900;
        color: #ff9900;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 2px;
        padding: 6px 16px;
        cursor: pointer;
        transition: all 0.15s;
    }
    .tip-metric {
        display: inline-block;
        background: #0a0800;
        border: 1px solid #ff990033;
        border-radius: 2px;
        padding: 8px 14px;
        margin: 4px;
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

    ctx = _build_research_context()

    if not ctx:
        st.markdown("""
        <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:20px;font-family:'IBM Plex Mono',monospace;">
          <div style="font-family:'Orbitron',monospace;color:#ff9900;font-size:0.65rem;letter-spacing:3px;margin-bottom:12px;border-bottom:1px solid rgba(255,153,0,0.27);padding-bottom:8px;">◈ TRADING INTELLIGENCE PLATFORM  ◈  NO DATA</div>
          <div style="color:#ff9900;font-family:'IBM Plex Mono',monospace;font-size:0.82rem;">
            ▸ 尚無交易記錄可供分析<br>
            ▸ 請先在「新增交易」Tab 記錄至少 3 筆已平倉交易<br>
            ▸ 數據越多，AI 分析越精準
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    n    = ctx["total_trades"]
    wr   = ctx["overall_win_rate"]
    pnl  = ctx["overall_pnl"]
    wr_c = "#00ff88" if wr >= 55 else "#ffcc44" if wr >= 40 else "#ff3333"

    # ── 終端機頂部狀態列 ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:20px;font-family:'IBM Plex Mono',monospace;">
      <div style="font-family:'Orbitron',monospace;color:#ff9900;font-size:0.65rem;letter-spacing:3px;margin-bottom:12px;border-bottom:1px solid rgba(255,153,0,0.27);padding-bottom:8px;">
        ◈ TRADING INTELLIGENCE PLATFORM v1.0 ◈ LIVE ANALYSIS ◈ {n} TRADES LOADED
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;">
        <div style="display:inline-block;background:#0a0800;border:1px solid rgba(255,153,0,0.2);border-radius:2px;padding:8px 14px;margin:4px;text-align:center;font-family:'IBM Plex Mono',monospace;">
          <div style="color:#666;font-size:0.78rem;">TOTAL TRADES</div>
          <div style="color:#ff9900;font-weight:700;" style="font-size:1.4rem;">{n}</div>
        </div>
        <div style="display:inline-block;background:#0a0800;border:1px solid rgba(255,153,0,0.2);border-radius:2px;padding:8px 14px;margin:4px;text-align:center;font-family:'IBM Plex Mono',monospace;">
          <div style="color:#666;font-size:0.78rem;">WIN RATE</div>
          <div style="color:{wr_c};font-size:1.4rem;font-weight:700;">{wr:.1f}%</div>
        </div>
        <div style="display:inline-block;background:#0a0800;border:1px solid rgba(255,153,0,0.2);border-radius:2px;padding:8px 14px;margin:4px;text-align:center;font-family:'IBM Plex Mono',monospace;">
          <div style="color:#666;font-size:0.78rem;">TOTAL PnL</div>
          <div class="{'tip-pos' if pnl>=0 else 'tip-neg'}" style="font-size:1.4rem;font-weight:700;">{pnl:+.1f}%</div>
        </div>
        <div style="display:inline-block;background:#0a0800;border:1px solid rgba(255,153,0,0.2);border-radius:2px;padding:8px 14px;margin:4px;text-align:center;font-family:'IBM Plex Mono',monospace;">
          <div style="color:#666;font-size:0.78rem;">SETUPS</div>
          <div style="color:#ffcc44;font-weight:600;" style="font-size:1.4rem;">{len(ctx['setup_summary'])}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 三大研究模組 ─────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    # ══ 模組 1：最賺錢 Setup ══════════════════════════════════════════════════
    with col1:
        setup_sm = ctx.get("setup_summary", {})
        ranked = sorted(setup_sm.items(),
                        key=lambda x: x[1]["total_pnl"], reverse=True)

        rows_html = ""
        for i, (s, d) in enumerate(ranked[:6]):
            medal = ["①","②","③","④","⑤","⑥"][i]
            wr_s  = d["win_rate"]
            ap    = d["avg_pnl"]
            col_s = "#00ff88" if ap > 0 else "#ff3333"
            r_str = f"{d['avg_r']:+.1f}R" if d.get("avg_r") else "—"
            rows_html += f"""
            <div style="border-bottom:1px solid #ff990022;padding:6px 0;display:flex;justify-content:space-between;align-items:center;">
              <div>
                <span style="color:#ff9900;font-weight:700;">{medal}</span>
                <span style="color:#ddbb88;font-size:0.78rem;margin-left:6px;">{s[:18]}</span>
              </div>
              <div style="text-align:right;">
                <span style="color:{col_s};font-weight:700;font-size:0.82rem;">{ap:+.1f}%</span>
                <span style="color:#666;font-size:0.78rem;" style="margin-left:6px;">{wr_s:.0f}%WR {r_str}</span>
              </div>
            </div>"""

        _m1_html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Orbitron:wght@700&display=swap" rel="stylesheet">
        <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:16px;font-family:'IBM Plex Mono',monospace;min-height:240px;">
          <div style="font-family:'Orbitron',monospace;color:#ff9900;font-size:0.6rem;letter-spacing:3px;margin-bottom:10px;border-bottom:1px solid rgba(255,153,0,0.25);padding-bottom:6px;">◈ MODULE 01 ◈ SETUP RANKING</div>
          <div style="font-size:0.75rem;">{rows_html if rows_html else '<span style="color:#666;">數據不足</span>'}</div>
        </div></body></html>"""
        import streamlit.components.v1 as _comp1
        _comp1.html(_m1_html, height=280, scrolling=False)

        if st.button("🤖 AI 分析最佳 Setup", key="ai_setup", use_container_width=True):
            with st.spinner("⚡ 分析中..."):
                result = _call_ai_research("找出最賺錢的Setup和原因，並給出具體改進建議", ctx, "setup")
                st.session_state["ai_setup_result"] = result
        if st.session_state.get("ai_setup_result"):
            _ai_txt = st.session_state["ai_setup_result"]
            import streamlit.components.v1 as _comp_air
            _ai_esc = _ai_txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            _ai_h = f'''<!DOCTYPE html><html><body style="margin:0;background:#050505;">
            <div style="border-left:3px solid #ff9900;padding:14px 18px;font-family:IBM Plex Mono,monospace;
            font-size:0.8rem;color:#ccaa77;line-height:1.8;white-space:pre-wrap;">{_ai_esc}</div>
            </body></html>'''
            _comp_air.html(_ai_h, height=min(60+len(_ai_txt)//2,480), scrolling=True)

    # ══ 模組 2：最適市場環境 ══════════════════════════════════════════════════
    with col2:
        time_sm = ctx.get("time_summary", {})
        emo_sm  = ctx.get("emotion_summary", {})

        time_rows = ""
        for slot, d in sorted(time_sm.items(), key=lambda x: x[1]["avg_pnl"], reverse=True):
            c = "#00ff88" if d["avg_pnl"] > 0 else "#ff3333"
            time_rows += f"""
            <div style="border-bottom:1px solid #ff990022;padding:5px 0;display:flex;justify-content:space-between;">
              <span style="color:#ddbb88;font-size:0.78rem;">{slot}</span>
              <span style="color:{c};font-weight:700;">{d['avg_pnl']:+.1f}%</span>
              <span style="color:#666;font-size:0.78rem;">{d['win_rate']:.0f}%WR ×{d['n']}</span>
            </div>"""

        emo_rows = ""
        best_emo  = max(emo_sm.items(), key=lambda x: x[1]["win_rate"]) if emo_sm else None
        worst_emo = min(emo_sm.items(), key=lambda x: x[1]["win_rate"]) if emo_sm else None
        for em, d in sorted(emo_sm.items(), key=lambda x: -x[1]["win_rate"])[:4]:
            c = "#00ff88" if d["win_rate"] >= 55 else "#ffcc44" if d["win_rate"] >= 40 else "#ff3333"
            warn = " ⚠" if d["win_rate"] < 40 and d["n"] >= 2 else ""
            emo_rows += f"""
            <div style="border-bottom:1px solid #ff990022;padding:4px 0;display:flex;justify-content:space-between;">
              <span style="color:#ddbb88;font-size:0.78rem;">{em}{warn}</span>
              <span style="color:{c};font-weight:700;">{d['win_rate']:.0f}%WR</span>
              <span style="color:#666;font-size:0.78rem;">{d['avg_pnl']:+.1f}% ×{d['n']}</span>
            </div>"""

        _m2_html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Orbitron:wght@700&display=swap" rel="stylesheet">
        <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:16px;font-family:'IBM Plex Mono',monospace;min-height:240px;">
          <div style="font-family:'Orbitron',monospace;color:#ff9900;font-size:0.6rem;letter-spacing:3px;margin-bottom:10px;border-bottom:1px solid rgba(255,153,0,0.25);padding-bottom:6px;">◈ MODULE 02 ◈ MARKET ENV</div>
          <div style="color:rgba(255,153,0,0.5);font-size:0.62rem;margin-bottom:4px;">TIME SLOT PERFORMANCE</div>
          <div style="font-size:0.75rem;margin-bottom:10px;">{time_rows if time_rows else '<span style="color:#666;">需要時間數據</span>'}</div>
          <div style="color:rgba(255,153,0,0.5);font-size:0.62rem;margin-bottom:4px;">EMOTION STATE ANALYSIS</div>
          <div style="font-size:0.75rem;">{emo_rows if emo_rows else '<span style="color:#666;">需要情緒記錄</span>'}</div>
        </div></body></html>"""
        import streamlit.components.v1 as _comp2
        _comp2.html(_m2_html, height=320, scrolling=False)

        if st.button("🤖 AI 分析最佳市場環境", key="ai_market", use_container_width=True):
            with st.spinner("⚡ 分析中..."):
                result = _call_ai_research("分析最適合的市場環境和交易時段，情緒管理建議", ctx, "market")
                st.session_state["ai_market_result"] = result
        if st.session_state.get("ai_market_result"):
            _ai_txt = st.session_state["ai_market_result"]
            import streamlit.components.v1 as _comp_air
            _ai_esc = _ai_txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            _ai_h = f'''<!DOCTYPE html><html><body style="margin:0;background:#050505;">
            <div style="border-left:3px solid #ff9900;padding:14px 18px;font-family:IBM Plex Mono,monospace;
            font-size:0.8rem;color:#ccaa77;line-height:1.8;white-space:pre-wrap;">{_ai_esc}</div>
            </body></html>'''
            _comp_air.html(_ai_h, height=min(60+len(_ai_txt)//2,480), scrolling=True)

    # ══ 模組 3：最佳倉位 ══════════════════════════════════════════════════════
    with col3:
        size_sm = ctx.get("size_summary", {})
        acct    = st.session_state.get("_acct_size", 100000)
        risk_p  = st.session_state.get("_risk_pct", 1.0)

        # Kelly 公式計算
        closed_all = [t for t in st.session_state.trade_log if t["status"] == "CLOSED"]
        pnls_all   = [t.get("pnl_pct", 0) or 0 for t in closed_all]
        wins_all   = [p for p in pnls_all if p > 0]
        loss_all   = [p for p in pnls_all if p <= 0]
        kelly_str  = "—"
        if wins_all and loss_all:
            w_prob = len(wins_all) / len(pnls_all)
            avg_w  = sum(wins_all) / len(wins_all) / 100
            avg_l  = abs(sum(loss_all) / len(loss_all)) / 100
            b      = avg_w / avg_l if avg_l > 0 else 1
            kelly  = w_prob - (1 - w_prob) / b
            kelly_str = f"{kelly*100:.1f}%"
            half_kelly = kelly * 0.5
            rec_size = int(acct * half_kelly / 0.02) if half_kelly > 0 else 0

        size_rows = ""
        for k, d in sorted(size_sm.items(), key=lambda x: x[1]["avg_pnl"], reverse=True):
            c = "#00ff88" if d["avg_pnl"] > 0 else "#ff3333"
            size_rows += f"""
            <div style="border-bottom:1px solid #ff990022;padding:5px 0;display:flex;justify-content:space-between;">
              <span style="color:#ddbb88;font-size:0.78rem;">{k}</span>
              <span style="color:{c};font-weight:700;">{d['avg_pnl']:+.1f}%</span>
              <span style="color:#666;font-size:0.78rem;">×{d['n']}筆</span>
            </div>"""

        _hk_disp = f'{half_kelly*100:.1f}%' if wins_all and loss_all else '—'
        _m3_html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:transparent;">
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Orbitron:wght@700&display=swap" rel="stylesheet">
        <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:16px;font-family:'IBM Plex Mono',monospace;min-height:240px;">
          <div style="font-family:'Orbitron',monospace;color:#ff9900;font-size:0.6rem;letter-spacing:3px;margin-bottom:10px;border-bottom:1px solid rgba(255,153,0,0.25);padding-bottom:6px;">◈ MODULE 03 ◈ POSITION SIZING</div>
          <div style="color:rgba(255,153,0,0.5);font-size:0.62rem;margin-bottom:4px;">SIZE vs PERFORMANCE</div>
          <div style="font-size:0.75rem;margin-bottom:10px;">{size_rows if size_rows else '<span style="color:#666;">需要倉位數據</span>'}</div>
          <div style="color:rgba(255,153,0,0.5);font-size:0.62rem;margin-bottom:6px;">KELLY CRITERION</div>
          <div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,153,0,0.1);">
              <span style="color:#666;font-size:0.78rem;">Full Kelly</span><span style="color:#ffcc44;font-weight:600;">{kelly_str}</span></div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,153,0,0.1);">
              <span style="color:#666;font-size:0.78rem;">Half Kelly（建議）</span><span style="color:#00ff88;">{_hk_disp}</span></div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid rgba(255,153,0,0.1);">
              <span style="color:#666;font-size:0.78rem;">當前風險設置</span><span style="color:#ffcc44;font-weight:600;">{risk_p}%</span></div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;">
              <span style="color:#666;font-size:0.78rem;">建議單筆風險$</span><span style="color:#00ff88;">${acct*risk_p/100:,.0f}</span></div>
          </div>
        </div></body></html>"""
        import streamlit.components.v1 as _comp3
        _comp3.html(_m3_html, height=320, scrolling=False)

        if st.button("🤖 AI 優化倉位策略", key="ai_position", use_container_width=True):
            with st.spinner("⚡ 分析中..."):
                result = _call_ai_research(
                    f"基於Kelly公式={kelly_str}，分析最優倉位大小和止損設置，給出具體資金管理規則",
                    ctx, "position")
                st.session_state["ai_position_result"] = result
        if st.session_state.get("ai_position_result"):
            _ai_txt = st.session_state["ai_position_result"]
            import streamlit.components.v1 as _comp_air
            _ai_esc = _ai_txt.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            _ai_h = f'''<!DOCTYPE html><html><body style="margin:0;background:#050505;">
            <div style="border-left:3px solid #ff9900;padding:14px 18px;font-family:IBM Plex Mono,monospace;
            font-size:0.8rem;color:#ccaa77;line-height:1.8;white-space:pre-wrap;">{_ai_esc}</div>
            </body></html>'''
            _comp_air.html(_ai_h, height=min(60+len(_ai_txt)//2,480), scrolling=True)

    # ── 綜合 AI 深度報告 ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;color:#ff990066;
                font-size:0.65rem;letter-spacing:3px;text-align:center;margin:8px 0;">
      ━━━━━━━━━━━━━━━━━━━━━━ DEEP ANALYSIS ━━━━━━━━━━━━━━━━━━━━━━
    </div>
    """, unsafe_allow_html=True)

    qcol1, qcol2 = st.columns([3, 1])
    with qcol1:
        custom_q = st.text_input("", placeholder="自定義研究問題（例：為何週五的交易勝率特別低？）",
                                 key="ai_custom_q",
                                 label_visibility="collapsed")
    with qcol2:
        ai_mode = st.selectbox("", ["setup","market","position"],
                               key="ai_mode_sel", label_visibility="collapsed")

    if st.button("◈ 執行深度分析", key="ai_deep", type="primary", use_container_width=True):
        q = custom_q or "綜合分析我的交易系統，找出最重要的3個改進點"
        with st.spinner("⚡ AI 正在深度分析您的交易數據..."):
            result = _call_ai_research(q, ctx, ai_mode)
            st.session_state["ai_deep_result"] = result

    if st.session_state.get("ai_deep_result"):
        _deep_txt = st.session_state["ai_deep_result"]
        _ts = datetime.now().strftime('%Y-%m-%d %H:%M')
        st.markdown(f"""
        <div style="background:#000;border:1px solid #ff9900;border-radius:4px;padding:20px;font-family:IBM Plex Mono,monospace;">
          <div style="font-family:Orbitron,monospace;color:#ff9900;font-size:0.65rem;letter-spacing:3px;margin-bottom:12px;border-bottom:1px solid rgba(255,153,0,0.27);padding-bottom:8px;">◈ DEEP ANALYSIS REPORT ◈ {_ts}</div>
          <div style="background:#050505;border-left:3px solid #ff9900;padding:16px 20px;font-family:IBM Plex Mono,monospace;font-size:0.82rem;color:#ccaa77;line-height:1.9;white-space:pre-wrap;">
{_deep_txt}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 清除按鈕
        if st.button("清除報告", key="clear_ai"):
            for k in ["ai_setup_result","ai_market_result","ai_position_result","ai_deep_result"]:
                st.session_state.pop(k, None)
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=60)
# ══════════════════════════════════════════════════════════════════════════════
# 延長時段數據（盤前 Pre-market / 盤後 After-hours / 夜盤）
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=90)   # 延長至 90 秒，減少 429
def _yahoo_chart_api(symbol: str, interval: str, range_str: str) -> dict:
    """
    底層 Yahoo Finance Chart API 請求（含盤前盤後）。
    所有上層函數共享此快取，避免重複請求同一 endpoint。
    ttl=90 秒：既保持數據新鮮，又不會因頻繁刷新觸發 429。
    """
    from urllib.parse import quote as _urlencode
    # ^ 符號需要 URL encode，否則部分代理會拒絕請求
    encoded_symbol = _urlencode(symbol, safe="")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/122.0 Safari/537.36",
        "Accept":   "application/json",
        "Referer":  "https://finance.yahoo.com",
    }
    # 嘗試 query1，失敗自動 fallback 到 query2
    for host in ("query1", "query2"):
        url = (
            f"https://{host}.finance.yahoo.com/v8/finance/chart/{encoded_symbol}"
            f"?interval={interval}&range={range_str}&includePrePost=true"
            f"&events=div%2Csplits&corsDomain=finance.yahoo.com"
        )
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 429:
                return {"error": "Yahoo 請求過於頻繁，請稍後再試", "df": None}
            if resp.status_code != 200:
                continue   # 試下一個 host
            data  = resp.json()
            r_lst = data.get("chart", {}).get("result", [])
            if not r_lst:
                err = data.get("chart", {}).get("error", {})
                return {"error": f"Yahoo 無數據: {err}", "df": None}
            r          = r_lst[0]
            timestamps = r.get("timestamp", [])
            quotes     = r.get("indicators", {}).get("quote", [{}])[0]
            if not timestamps:
                return {"error": "Yahoo 回傳空時間序列", "df": None}
            df = pd.DataFrame({
                "Open":   quotes.get("open",   [None]*len(timestamps)),
                "High":   quotes.get("high",   [None]*len(timestamps)),
                "Low":    quotes.get("low",    [None]*len(timestamps)),
                "Close":  quotes.get("close",  [None]*len(timestamps)),
                "Volume": quotes.get("volume", [0]*len(timestamps)),
            }, index=pd.to_datetime(timestamps, unit="s", utc=True))
            try:
                import pytz as _ptz
                df = df.tz_convert(_ptz.timezone("America/New_York"))
            except Exception:
                pass
            df = df.dropna(subset=["Close"])
            df["Volume"] = df["Volume"].fillna(0).astype(int)
            df = df.sort_index()
            return {"error": None, "df": df}
        except Exception as e:
            last_err = str(e)
            continue
    return {"error": last_err if 'last_err' in dir() else "所有請求均失敗", "df": None}


@st.cache_data(ttl=90)
def fetch_data(symbol: str, interval: str, prepost: bool = False) -> pd.DataFrame:
    _, period = INTERVAL_MAP[interval]

    # 分鐘級別 + 開啟延長時段 → 共享快取的 Yahoo Chart API
    if prepost and interval in ("1m", "5m", "15m", "30m"):
        yf_range = {"1m": "5d", "5m": "5d", "15m": "10d", "30m": "20d"}.get(interval, "5d")
        result   = _yahoo_chart_api(symbol, interval, yf_range)
        if result["df"] is not None and not result["df"].empty:
            return result["df"]
        # 429 或失敗時 fallback（不再重試，避免加重限流）

    # 標準抓取（日K/週K/月K 或 prepost=False 或 API 失敗 fallback）
    try:
        df = yf.download(symbol, period=period, interval=interval,
                         auto_adjust=True, progress=False)
        if df.empty:
            return pd.DataFrame()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        df.dropna(inplace=True)
        df = df.sort_index()
        return df
    except Exception:
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# 技術指標
# ══════════════════════════════════════════════════════════════════════════════
def calc_ema(s, n):  return s.ewm(span=n, adjust=False).mean()
def calc_ma(s, n):   return s.rolling(n).mean()

def calc_macd(s, fast=12, slow=26, sig=9):
    dif  = calc_ema(s, fast) - calc_ema(s, slow)
    dea  = calc_ema(dif, sig)
    return dif, dea, (dif - dea) * 2

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def calc_adx(df, period=14):
    """
    計算 ADX / +DI / -DI（趨勢強度與方向）
    ADX>25 趨勢有效；-DI>+DI 空頭主導；+DI>-DI 多頭主導
    """
    try:
        hi = df["High"]; lo = df["Low"]; cl = df["Close"]
        tr = pd.concat([
            (hi - lo),
            (hi - cl.shift(1)).abs(),
            (lo - cl.shift(1)).abs()
        ], axis=1).max(axis=1)
        up = hi.diff(); dn = -lo.diff()
        pdm = up.where((up > dn) & (up > 0), 0.0)
        ndm = dn.where((dn > up) & (dn > 0), 0.0)
        atr = tr.ewm(com=period-1, adjust=False).mean()
        pdi = 100 * pdm.ewm(com=period-1, adjust=False).mean() / atr.replace(0, np.nan)
        ndi = 100 * ndm.ewm(com=period-1, adjust=False).mean() / atr.replace(0, np.nan)
        dx  = ((pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan)) * 100
        adx = dx.ewm(com=period-1, adjust=False).mean()
        return adx, pdi, ndi
    except Exception:
        empty = pd.Series([np.nan]*len(df))
        return empty, empty, empty

def calc_willr(df, period=14):
    """
    Williams %R：範圍 -100~0
    < -80 超賣（潛在反彈）；> -20 超買（潛在回落）
    """
    try:
        hi_max = df["High"].rolling(period).max()
        lo_min = df["Low"].rolling(period).min()
        rng = hi_max - lo_min
        return -100 * (hi_max - df["Close"]) / rng.replace(0, np.nan)
    except Exception:
        return pd.Series([np.nan]*len(df))


def calc_pivot(df, interval: str = "1d"):
    """
    依週期動態調整掃描參數，並用「價格合理範圍過濾（±30%）」
    確保阻力/支撐位一定在當前價格附近，不出現歷史舊極值。
    """
    # 依週期決定 left、right、掃描的最近 N 根 K 線
    pivot_cfg = {
        "1m":  (3, 3, 120),
        "5m":  (3, 3, 100),
        "15m": (3, 3, 80),
        "30m": (3, 3, 60),
        "1d":  (5, 5, 60),
        "1wk": (3, 3, 40),
        "1mo": (2, 2, 24),   # 月K只看近24根(2年)，避免抓到5年前低點
    }
    left, right, tail_n = pivot_cfg.get(interval, (3, 3, 60))

    sub = df.tail(tail_n)
    if len(sub) < left + right + 2:
        return [], []

    hi, lo, idx = sub["High"].values, sub["Low"].values, sub.index
    current_price = float(df["Close"].iloc[-1])

    # 只接受距離當前價格 ±30% 以內的 pivot（過濾歷史遠古價位）
    price_lo = current_price * 0.70
    price_hi = current_price * 1.30

    highs, lows = [], []
    for i in range(left, len(sub) - right):
        if hi[i] == max(hi[i-left:i+right+1]) and price_lo <= hi[i] <= price_hi:
            highs.append((idx[i], float(hi[i])))
        if lo[i] == min(lo[i-left:i+right+1]) and price_lo <= lo[i] <= price_hi:
            lows.append((idx[i], float(lo[i])))

    return highs, lows

def calc_trendline(df, mode="high", lookback=60, min_points=2):
    """
    計算下降趨勢線（mode='high'）或上升趨勢線（mode='low'）。
    用最近 lookback 根K線的局部高/低點做線性回歸。
    返回 dict:
      slope, intercept, r2, current_val,
      points: [(bar_idx, price), ...],
      breakout: bool（當前價格是否突破趨勢線）
      distance_pct: 當前價格距趨勢線的百分比
    """
    result = {"slope": None, "intercept": None, "r2": None,
              "current_val": None, "points": [], "breakout": False,
              "distance_pct": 0, "valid": False}
    try:
        n = min(lookback, len(df))
        sub = df.iloc[-n:]
        col = "High" if mode == "high" else "Low"
        vals = sub[col].values if col in sub.columns else sub["Close"].values
        price_col = sub["Close"].values

        # 找局部極值點（窗口=3）
        pts = []
        for i in range(2, len(vals)-2):
            if mode == "high":
                if vals[i] >= max(vals[max(0,i-3):i+1]) and vals[i] >= max(vals[i:min(len(vals),i+4)]):
                    pts.append((i, float(vals[i])))
            else:
                if vals[i] <= min(vals[max(0,i-3):i+1]) and vals[i] <= min(vals[i:min(len(vals),i+4)]):
                    pts.append((i, float(vals[i])))

        # 合併過近的點（保留更極端的）
        merged = []
        for idx, v in pts:
            if not merged or idx - merged[-1][0] >= 5:
                merged.append((idx, v))
            elif (mode == "high" and v > merged[-1][1]) or (mode == "low" and v < merged[-1][1]):
                merged[-1] = (idx, v)

        if len(merged) < min_points:
            return result

        # 只用最近的幾個點做回歸（最多5個）
        use_pts = merged[-5:]
        xs = [p[0] for p in use_pts]
        ys = [p[1] for p in use_pts]
        # 用 numpy polyfit 做線性回歸（不依賴 scipy）
        coeffs = np.polyfit(xs, ys, 1)
        slope, intercept = float(coeffs[0]), float(coeffs[1])
        # 計算 R²
        ys_pred = [slope*x + intercept for x in xs]
        ss_res = sum((y-yp)**2 for y,yp in zip(ys,ys_pred))
        ss_tot = sum((y-sum(ys)/len(ys))**2 for y in ys)
        r = (1 - ss_res/ss_tot)**0.5 if ss_tot > 0 else 0

        # 當前趨勢線值
        cur_bar = len(sub) - 1
        cur_val = slope * cur_bar + intercept
        cur_price = float(price_col[-1])

        breakout = (cur_price > cur_val) if mode == "high" else (cur_price < cur_val)
        dist_pct = (cur_price - cur_val) / cur_val * 100

        result.update({
            "slope": slope, "intercept": intercept, "r2": r**2,
            "current_val": cur_val, "points": use_pts,
            "breakout": breakout, "distance_pct": dist_pct,
            "cur_price": cur_price, "valid": r**2 >= 0.5
        })
    except Exception:
        pass
    return result

def detect_trend(df) -> str:
    if len(df) < 60: return "盤整"
    c = df["Close"]
    e5, e20, e60 = calc_ema(c,5).iloc[-1], calc_ema(c,20).iloc[-1], calc_ema(c,60).iloc[-1]
    e200 = calc_ema(c,200).iloc[-1] if len(df) >= 200 else None
    if e200:
        if e5>e20>e60>e200: return "多頭"
        if e5<e20<e60<e200: return "空頭"
    else:
        if e5>e20>e60: return "多頭"
        if e5<e20<e60: return "空頭"
    return "盤整"

def get_macd_signal(df) -> str:
    if len(df) < 30: return "—"
    dif, dea, _ = calc_macd(df["Close"])
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]: return "⬆金叉"
    if dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]: return "⬇死叉"
    return "DIF↑" if dif.iloc[-1] > dea.iloc[-1] else "DIF↓"

def get_ema_signal(df) -> str:
    if len(df) < 20: return "—"
    c = df["Close"]
    e5, e20 = calc_ema(c,5), calc_ema(c,20)
    if e5.iloc[-1] > e20.iloc[-1] and e5.iloc[-2] <= e20.iloc[-2]: return "多排↑"
    if e5.iloc[-1] < e20.iloc[-1] and e5.iloc[-2] >= e20.iloc[-2]: return "空排↓"
    return "EMA↑" if e5.iloc[-1] > e20.iloc[-1] else "EMA↓"


# ══════════════════════════════════════════════════════════════════════════════
# 線性回歸通道偵測
# ══════════════════════════════════════════════════════════════════════════════
def calc_channel(df, lookback=25):
    """
    線性回歸通道：上軌/中軌/下軌 + R² + 方向
    """
    import numpy as np
    if len(df) < lookback:
        return None
    sub   = df.tail(lookback)
    hi    = sub["High"].values.astype(float)
    lo    = sub["Low"].values.astype(float)
    cl    = sub["Close"].values.astype(float)
    x     = np.arange(len(cl), dtype=float)

    mid_c   = np.polyfit(x, cl, 1)
    mid_y   = np.polyval(mid_c, x)
    hi_c    = np.polyfit(x, hi, 1)
    lo_c    = np.polyfit(x, lo, 1)
    upper_y = np.polyval(hi_c, x)
    lower_y = np.polyval(lo_c, x)

    ss_res = ((cl - mid_y) ** 2).sum()
    ss_tot = ((cl - cl.mean()) ** 2).sum()
    r2     = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0

    slope_pct = mid_c[0] / cl.mean() * 100
    direction = "up" if slope_pct > 0.015 else ("down" if slope_pct < -0.015 else "flat")

    width_pct = (upper_y[-1] - lower_y[-1]) / mid_y[-1] * 100

    return {
        "direction": direction,
        "slope_pct": slope_pct,
        "upper":     float(upper_y[-1]),
        "mid":       float(mid_y[-1]),
        "lower":     float(lower_y[-1]),
        "r2":        r2,
        "width_pct": width_pct,
    }


def detect_channel_signals(df):
    """
    偵測通道反轉買賣訊號，回傳 list of (msg, atype, is_action)
    涵蓋：下降通道底反彈、上升通道頂壓回、通道方向突破
    is_action=True 代表強力買入/賣出信號，觸發 Toast
    """
    signals = []
    if len(df) < 30:
        return signals

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    opn    = df["Open"]
    vol    = df["Volume"]
    price  = float(close.iloc[-1])
    prev   = float(close.iloc[-2])
    prev_l = float(low.iloc[-2])
    prev_h = float(high.iloc[-2])

    dif, dea, hist = calc_macd(close)
    rsi = calc_rsi(close, 14)
    vol_ma5 = vol.rolling(5).mean()
    is_bull_bar = price > float(opn.iloc[-1])
    is_bear_bar = price < float(opn.iloc[-1])

    for lookback, label in [(15, "短"), (25, "中"), (40, "長")]:
        ch = calc_channel(df, lookback=lookback)
        # 降低 R² 門檻至 0.30，提高靈敏度
        if ch is None or ch["r2"] < 0.30:
            continue

        tol = (ch["upper"] - ch["lower"]) * 0.25   # 容差 = 通道寬 25%

        # ── A. 下降通道底部反彈（買入機會）──────────────────────────────────
        if ch["direction"] == "down":

            # 條件：前根觸及下軌 + 當根陽線反彈
            touched = prev_l <= ch["lower"] + tol
            bounced = price > prev and is_bull_bar

            if touched and bounced:
                tags   = []
                score  = 0   # 共振分數

                # MACD 柱負值收縮（底背離）
                if (hist.iloc[-1] < 0
                        and abs(hist.iloc[-1]) < abs(hist.iloc[-2])):
                    tags.append("MACD柱收縮"); score += 1
                # DIF 回升
                if dif.iloc[-1] > dif.iloc[-2]:
                    tags.append("DIF回升"); score += 1
                # RSI 超賣（<35）反彈
                if not rsi.empty and rsi.iloc[-2] < 35 and rsi.iloc[-1] > rsi.iloc[-2]:
                    tags.append(f"RSI超賣回升({rsi.iloc[-1]:.0f})"); score += 2
                # 放量陽線
                if vol.iloc[-1] > vol_ma5.iloc[-1] * 1.3:
                    tags.append("放量"); score += 1
                # 連續陽線確認
                if price > float(close.iloc[-2]) > float(close.iloc[-3]):
                    tags.append("連陽確認"); score += 1

                conf      = "｜" + " + ".join(tags) if tags else ""
                strength  = "⭐⭐⭐ 強力" if score >= 3 else ("⭐⭐ 中等" if score >= 2 else "⭐ 初步")
                is_action = score >= 2   # 2分以上觸發 Toast

                signals.append((
                    f"🟢 【{strength}買入】{label}下降通道底反彈"
                    f"｜下軌${ch['lower']:.2f} R²={ch['r2']:.2f} 現價${price:.2f}{conf}",
                    "bull", is_action
                ))

            # 下降通道上軌突破（趨勢反轉）
            if price > ch["upper"] and prev <= ch["upper"]:
                is_bull_strong = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.5
                strength = "⭐⭐⭐ 放量" if is_bull_strong else "⭐⭐"
                signals.append((
                    f"🚀 【{strength}反轉突破】{label}下降通道上軌突破"
                    f"｜上軌${ch['upper']:.2f} R²={ch['r2']:.2f}",
                    "bull", True
                ))

        # ── B. 上升通道頂部壓回（賣出機會）──────────────────────────────────
        if ch["direction"] == "up":

            touched  = prev_h >= ch["upper"] - tol
            rejected = price < prev and is_bear_bar

            if touched and rejected:
                tags  = []
                score = 0

                if (hist.iloc[-1] > 0
                        and abs(hist.iloc[-1]) < abs(hist.iloc[-2])):
                    tags.append("MACD柱收縮"); score += 1
                if dif.iloc[-1] < dif.iloc[-2]:
                    tags.append("DIF轉弱"); score += 1
                if not rsi.empty and rsi.iloc[-2] > 65 and rsi.iloc[-1] < rsi.iloc[-2]:
                    tags.append(f"RSI超買回落({rsi.iloc[-1]:.0f})"); score += 2
                if vol.iloc[-1] > vol_ma5.iloc[-1] * 1.3:
                    tags.append("放量"); score += 1
                if price < float(close.iloc[-2]) < float(close.iloc[-3]):
                    tags.append("連陰確認"); score += 1

                conf      = "｜" + " + ".join(tags) if tags else ""
                strength  = "⭐⭐⭐ 強力" if score >= 3 else ("⭐⭐ 中等" if score >= 2 else "⭐ 初步")
                is_action = score >= 2

                signals.append((
                    f"🔴 【{strength}賣出】{label}上升通道頂壓回"
                    f"｜上軌${ch['upper']:.2f} R²={ch['r2']:.2f} 現價${price:.2f}{conf}",
                    "bear", is_action
                ))

            # 上升通道下軌跌破（趨勢反轉）
            if price < ch["lower"] and prev >= ch["lower"]:
                is_bear_strong = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.5
                strength = "⭐⭐⭐ 放量" if is_bear_strong else "⭐⭐"
                signals.append((
                    f"💀 【{strength}反轉跌破】{label}上升通道下軌跌破"
                    f"｜下軌${ch['lower']:.2f} R²={ch['r2']:.2f}",
                    "bear", True
                ))

    return signals


# ══════════════════════════════════════════════════════════════════════════════
# 警示邏輯
# ══════════════════════════════════════════════════════════════════════════════
def detect_candlestick_patterns(df: pd.DataFrame) -> list:
    """
    20種K線形態識別（無需TA-Lib）
    返回：[(name, alert_type, message), ...]
    只偵測最新1根（單K）或最新2-3根（組合K）

    形態清單：
    單K：
      K01 錘頭線        K02 吊頸線        K03 射擊之星      K04 倒錘頭
      K05 看漲十字星    K06 看跌十字星    K07 蜻蜓十字      K08 墓碑十字
      K09 紡錘線多      K10 大陽線        K11 大陰線
    雙K：
      K12 看漲吞噬      K13 看跌吞噬      K14 看漲孕線      K15 看跌孕線
      K16 貫穿線        K17 烏雲蓋頂
    三K：
      K18 早晨之星      K19 黃昏之星      K20 三白兵 / 三黑鴉
    """
    results = []
    if len(df) < 5:
        return results

    o  = df["Open"];  h  = df["High"]
    l  = df["Low"];   c  = df["Close"]

    # ── 最新3根數據 ──────────────────────────────────────────────────────────
    o1,h1,l1,c1 = float(o.iloc[-1]),float(h.iloc[-1]),float(l.iloc[-1]),float(c.iloc[-1])
    o2,h2,l2,c2 = float(o.iloc[-2]),float(h.iloc[-2]),float(l.iloc[-2]),float(c.iloc[-2])
    o3,h3,l3,c3 = float(o.iloc[-3]),float(h.iloc[-3]),float(l.iloc[-3]),float(c.iloc[-3])

    body1  = abs(c1-o1); body2 = abs(c2-o2); body3 = abs(c3-o3)
    hi1    = max(c1,o1); lo1  = min(c1,o1)
    hi2    = max(c2,o2); lo2  = min(c2,o2)
    hi3    = max(c3,o3); lo3  = min(c3,o3)
    uw1    = h1-hi1;  dw1  = lo1-l1         # 上/下影線（最新根）
    uw2    = h2-hi2;  dw2  = lo2-l2
    rng1   = h1-l1 if h1>l1 else 0.001       # 總波幅

    bull1  = c1>o1; bear1 = c1<o1
    bull2  = c2>o2; bear2 = c2<o2
    bull3  = c3>o3; bear3 = c3<o3

    # 10日平均實體（判斷「大/小」基準）
    body_avg = float(abs(c-o).rolling(10).mean().iloc[-1]) or (rng1*0.5)
    # 近5根趨勢（判斷在上升/下降末端）
    trend_up   = float(c.iloc[-2]) > float(c.iloc[-6]) if len(c)>=6 else False
    trend_down = float(c.iloc[-2]) < float(c.iloc[-6]) if len(c)>=6 else False

    # ════════════════ 單K形態 ════════════════════════════════════════════════

    # K01 錘頭線 Hammer（下降趨勢末端，下影≥2×實體，上影<0.3×實體）
    if (trend_down and body1 > 0 and
        dw1 >= body1*2 and uw1 <= body1*0.3 and
        body1 < body_avg*1.5):
        results.append(("K01-錘頭線", "bull",
            f"🔨 【K01·錘頭線】下影線{dw1:.2f}≥實體{body1:.2f}×2，下降趨勢末端｜潛在底部反轉，等次根確認收高"))

    # K02 吊頸線 Hanging Man（上升趨勢末端，形狀同錘頭但反向含義）
    elif (trend_up and body1 > 0 and
          dw1 >= body1*2 and uw1 <= body1*0.3 and
          body1 < body_avg*1.5):
        results.append(("K02-吊頸線", "bear",
            f"🪝 【K02·吊頸線】上升末端出現錘頭形（下影{dw1:.2f}），主力誘多警告｜需次根收低確認"))

    # K03 射擊之星 Shooting Star（上升趨勢末端，上影≥2×實體，下影<0.3×實體）
    if (trend_up and body1 > 0 and
        uw1 >= body1*2 and dw1 <= body1*0.3 and
        body1 < body_avg*1.5):
        results.append(("K03-射擊之星", "bear",
            f"⭐ 【K03·射擊之星】上影線{uw1:.2f}≥實體×2，上升趨勢末端｜潛在頂部反轉警告"))

    # K04 倒錘頭 Inverted Hammer（下降趨勢末端，形狀同射擊之星但偏多）
    elif (trend_down and body1 > 0 and
          uw1 >= body1*2 and dw1 <= body1*0.3 and
          body1 < body_avg*1.5):
        results.append(("K04-倒錘頭", "bull",
            f"🔄 【K04·倒錘頭】下降末端上影長{uw1:.2f}，買方試探力量｜需次根大陽線確認反轉"))

    # K05 看漲十字星 Bullish Doji（下降趨勢末端，實體≤波幅3%）
    if (trend_down and rng1 > 0 and body1/rng1 <= 0.03 and
        body1 < body_avg*0.1 and rng1 > body_avg*0.3):
        results.append(("K05-看漲十字星", "bull",
            f"✚ 【K05·看漲十字星】開收幾乎相同（實體{body1:.3f}），下降趨勢變盤信號"))

    # K06 看跌十字星 Bearish Doji（上升趨勢末端）
    elif (trend_up and rng1 > 0 and body1/rng1 <= 0.03 and
          body1 < body_avg*0.1 and rng1 > body_avg*0.3):
        results.append(("K06-看跌十字星", "bear",
            f"✚ 【K06·看跌十字星】開收幾乎相同（實體{body1:.3f}），上升趨勢變盤信號"))

    # K07 蜻蜓十字 Dragonfly Doji（開=收=高，長下影）
    if (body1 < body_avg*0.05 and dw1 >= rng1*0.7 and uw1 <= rng1*0.1):
        results.append(("K07-蜻蜓十字", "bull",
            f"🐉 【K07·蜻蜓十字】長下影{dw1:.2f}，強力買盤承接｜底部反轉信號"))

    # K08 墓碑十字 Gravestone Doji（開=收=低，長上影）
    if (body1 < body_avg*0.05 and uw1 >= rng1*0.7 and dw1 <= rng1*0.1):
        results.append(("K08-墓碑十字", "bear",
            f"🪦 【K08·墓碑十字】長上影{uw1:.2f}，高位賣盤強烈｜頂部反轉信號"))

    # K09 紡錘線（多方）小實體+雙影均長，下降趨勢末端→買賣均衡偏多
    if (trend_down and body1 < body_avg*0.5 and
        dw1 >= body1 and uw1 >= body1 and
        rng1 > body_avg*0.5 and bull1):
        results.append(("K09-多頭紡錘線", "bull",
            f"🪀 【K09·多頭紡錘線】下降末端多空均衡（實體{body1:.2f}，雙影均長），做空動能減弱"))

    # K10 大陽線（實體≥2.5×10日均實體，bull）
    if (bull1 and body1 >= body_avg*2.5 and
        dw1 <= body1*0.2 and uw1 <= body1*0.2):
        results.append(("K10-大陽線", "bull",
            f"🚀 【K10·大陽線】實體{body1:.2f}（均值{body_avg:.2f}的{body1/body_avg:.1f}倍），買盤壓倒性強勢"))

    # K11 大陰線（實體≥2.5×10日均實體，bear）
    if (bear1 and body1 >= body_avg*2.5 and
        dw1 <= body1*0.2 and uw1 <= body1*0.2):
        results.append(("K11-大陰線", "bear",
            f"💥 【K11·大陰線】實體{body1:.2f}（均值{body_avg:.2f}的{body1/body_avg:.1f}倍），賣盤壓倒性強勢"))

    # ════════════════ 雙K形態 ════════════════════════════════════════════════

    # K12 看漲吞噬 Bullish Engulfing（前陰+後大陽完全包覆）
    if (bear2 and bull1 and
        o1 <= lo2 and c1 >= hi2 and
        body1 > body2):
        results.append(("K12-看漲吞噬", "bull",
            f"🟢 【K12·看漲吞噬】大陽線完全吞噬前陰線（{body1:.2f}>{body2:.2f}）｜強烈底部反轉"))

    # K13 看跌吞噬 Bearish Engulfing（前陽+後大陰完全包覆）
    if (bull2 and bear1 and
        o1 >= hi2 and c1 <= lo2 and
        body1 > body2):
        results.append(("K13-看跌吞噬", "bear",
            f"🔴 【K13·看跌吞噬】大陰線完全吞噬前陽線（{body1:.2f}>{body2:.2f}）｜強烈頂部反轉"))

    # K14 看漲孕線 Bullish Harami（前大陰+後小陽，完全在前實體內）
    if (bear2 and bull1 and
        o1 > lo2 and c1 < hi2 and
        body1 < body2*0.5):
        results.append(("K14-看漲孕線", "bull",
            f"🤰 【K14·看漲孕線】小陽線孕育於前大陰內（實體{body1:.2f}<{body2:.2f}×0.5），動能衰竭偏多"))

    # K15 看跌孕線 Bearish Harami（前大陽+後小陰，完全在前實體內）
    if (bull2 and bear1 and
        o1 < hi2 and c1 > lo2 and
        body1 < body2*0.5):
        results.append(("K15-看跌孕線", "bear",
            f"🤰 【K15·看跌孕線】小陰線孕育於前大陽內（實體{body1:.2f}<{body2:.2f}×0.5），動能衰竭偏空"))

    # K16 貫穿線 Piercing Line（下降趨勢：前大陰+後陽開於前低下方，收超過前實體中點）
    if (trend_down and bear2 and bull1 and
        o1 < l2 and
        c1 > (o2+c2)/2 and c1 < o2):
        results.append(("K16-貫穿線", "bull",
            f"🗡️ 【K16·貫穿線】陽線收盤穿越前陰中點（{c1:.2f}>{(o2+c2)/2:.2f}），底部反轉確認"))

    # K17 烏雲蓋頂 Dark Cloud Cover（上升趨勢：前大陽+後陰開高，收低於前實體中點）
    if (trend_up and bull2 and bear1 and
        o1 > h2 and
        c1 < (o2+c2)/2 and c1 > o2):
        results.append(("K17-烏雲蓋頂", "bear",
            f"☁️ 【K17·烏雲蓋頂】陰線收盤穿越前陽中點（{c1:.2f}<{(o2+c2)/2:.2f}），頂部反轉確認"))

    # ════════════════ 三K形態 ════════════════════════════════════════════════

    # K18 早晨之星 Morning Star（下降趨勢：大陰+小實體+大陽）
    if (trend_down and bear3 and bull1 and
        body2 < body_avg*0.4 and           # 中間星形小實體
        body3 > body_avg and body1 > body_avg and
        c1 > (o3+c3)/2 and                 # 最後陽線收盤過前大陰中點
        max(o2,c2) < min(o3,c3) and        # 星形與前陰有缺口（下跳）
        max(o2,c2) < min(o1,c1)):          # 星形與後陽有缺口（上跳）
        results.append(("K18-早晨之星", "bull",
            f"🌅 【K18·早晨之星】三K底部反轉：大陰({body3:.2f})+星形({body2:.2f})+大陽({body1:.2f})"
            f"｜最高置信底部反轉形態！"))

    # K19 黃昏之星 Evening Star（上升趨勢：大陽+小實體+大陰）
    if (trend_up and bull3 and bear1 and
        body2 < body_avg*0.4 and
        body3 > body_avg and body1 > body_avg and
        c1 < (o3+c3)/2 and
        min(o2,c2) > max(o3,c3) and        # 星形與前陽有缺口（上跳）
        min(o2,c2) > max(o1,c1)):          # 星形與後陰有缺口（下跳）
        results.append(("K19-黃昏之星", "bear",
            f"🌆 【K19·黃昏之星】三K頂部反轉：大陽({body3:.2f})+星形({body2:.2f})+大陰({body1:.2f})"
            f"｜最高置信頂部反轉形態！"))

    # K20a 三白兵 Three White Soldiers（連續3根大陽線，每根開在前根實體內，收創新高）
    if (bull1 and bull2 and bull3 and
        body1>body_avg and body2>body_avg and body3>body_avg and
        o1>o2 and o2>o3 and               # 每根開在前根實體內
        c1>c2 and c2>c3 and               # 每根收盤創新高
        o1<c2 and o2<c3 and               # 開盤在前根實體內（非跳空）
        uw1<body1*0.2 and uw2<body2*0.2): # 無長上影（非衰竭）
        results.append(("K20a-三白兵", "bull",
            f"⚔️ 【K20a·三白兵】連續3根大陽線逐步推高（{c3:.2f}→{c2:.2f}→{c1:.2f}）｜強烈多頭趨勢確立"))

    # K20b 三黑鴉 Three Black Crows（連續3根大陰線，每根開在前根實體內，收創新低）
    if (bear1 and bear2 and bear3 and
        body1>body_avg and body2>body_avg and body3>body_avg and
        o1<o2 and o2<o3 and
        c1<c2 and c2<c3 and
        o1>c2 and o2>c3 and               # 開盤在前根實體內
        dw1<body1*0.2 and dw2<body2*0.2):
        results.append(("K20b-三黑鴉", "bear",
            f"🐦‍⬛ 【K20b·三黑鴉】連續3根大陰線逐步下殺（{c3:.2f}→{c2:.2f}→{c1:.2f}）｜強烈空頭趨勢確立"))

    return results


def run_alerts(symbol, period_label, df, trigger_ai=False, mkt=None):
    """
    偵測四大類技術信號：
    A. 趨勢正在形成  B. 趨勢已確立
    C. 趨勢反轉訊號  D. 原有突破（支撐/阻力）
    """
    # 防護：symbol 必須在目前活躍監控列表中，否則拒絕執行（防止空輸入時觸發）
    import re as _re_guard
    if not symbol or not _re_guard.match(r'^[A-Z\.\-]{1,10}$', str(symbol)):
        return
    _active = st.session_state.get("_active_symbols", [])
    if _active and symbol not in _active:
        return

    if len(df) < 35: return

    close  = df["Close"]
    high   = df["High"]
    low    = df["Low"]
    opn    = df["Open"]
    vol    = df["Volume"]
    new_signals = []

    # ── 預算指標 ──────────────────────────────────────────────────────────────
    e5   = calc_ema(close, 5)
    e10  = calc_ema(close, 10)
    e20  = calc_ema(close, 20)
    e60  = calc_ema(close, 60)
    dif, dea, hist = calc_macd(close)
    vol_ma5 = vol.rolling(5).mean()
    atr = (high - low).rolling(14).mean().iloc[-1]  # Average True Range

    price      = float(close.iloc[-1])
    prev_price = float(close.iloc[-2])

    # ════════════════════════════════════════════════════════════════════════
    # A. 趨勢「正在形成」偵測（Early-stage, 2-3 根確認）
    # ════════════════════════════════════════════════════════════════════════

    # A1. MACD 柱連續 3 根擴大（動能積累中）
    h = hist.iloc
    if (h[-1] > h[-2] > h[-3] > 0) and h[-3] > 0:
        add_alert(symbol, period_label,
                  f"📈 趨勢形成中｜MACD 柱連續擴大 ×3 (動能累積) +{h[-1]:.4f}", "bull")
        new_signals.append("MACD柱連漲×3")
    elif (h[-1] < h[-2] < h[-3] < 0) and h[-3] < 0:
        add_alert(symbol, period_label,
                  f"📉 趨勢形成中｜MACD 柱連續縮小 ×3 (賣壓累積) {h[-1]:.4f}", "bear")
        new_signals.append("MACD柱連跌×3")

    # A2. EMA5 斜率連續 3 根上升（短線趨勢啟動）
    e5_slope = [e5.iloc[i] - e5.iloc[i-1] for i in range(-3, 0)]
    if all(s > 0 for s in e5_slope) and e5.iloc[-1] > e20.iloc[-1]:
        add_alert(symbol, period_label,
                  f"📈 趨勢形成中｜EMA5 斜率連升 ×3 且在 EMA20 上方", "bull")
        new_signals.append("EMA5斜率連升")
    elif all(s < 0 for s in e5_slope) and e5.iloc[-1] < e20.iloc[-1]:
        add_alert(symbol, period_label,
                  f"📉 趨勢形成中｜EMA5 斜率連降 ×3 且在 EMA20 下方", "bear")
        new_signals.append("EMA5斜率連降")

    # A3. 價格連續 4 根收在 EMA20 之上（多方站穩）
    above20 = all(close.iloc[i] > e20.iloc[i] for i in range(-4, 0))
    below20 = all(close.iloc[i] < e20.iloc[i] for i in range(-4, 0))
    if above20 and close.iloc[-5] <= e20.iloc[-5]:   # 之前在下方
        add_alert(symbol, period_label,
                  "📈 趨勢形成中｜價格連續 4 根站上 EMA20（多方確認）", "bull")
        new_signals.append("站上EMA20×4")
    elif below20 and close.iloc[-5] >= e20.iloc[-5]:
        add_alert(symbol, period_label,
                  "📉 趨勢形成中｜價格連續 4 根跌破 EMA20（空方確認）", "bear")
        new_signals.append("跌破EMA20×4")

    # ════════════════════════════════════════════════════════════════════════
    # E. 底部升浪偵測（對應圖片：空頭排列→收縮→多頭排列全程買入提醒）
    # ════════════════════════════════════════════════════════════════════════

    e30 = calc_ema(close, 30)

    # ── E0. 最最早期：空頭排列低點反彈第一根（箭頭形態）──────────────────
    # 條件：
    #   1. 均線仍是空頭排列（EMA5 < EMA20）
    #   2. 近N根出現明顯低點（比前5根都低）
    #   3. 當前K線是陽線（開<收）
    #   4. 收盤開始從低點反彈（比低點高）
    #   5. 量能相對前幾根開始放大（底部量）
    if len(close) >= 15:
        try:
            _e0_e5  = float(e5.iloc[-1])
            _e0_e20 = float(e20.iloc[-1])
            _e0_e5p = float(e5.iloc[-2])

            # 仍是空頭排列（EMA5 < EMA20）
            _e0_bear_align = _e0_e5 < _e0_e20

            # 當前K線是陽線
            _e0_open  = float(df["Open"].iloc[-1]) if "Open" in df.columns else float(close.iloc[-1])
            _e0_price = float(close.iloc[-1])
            _e0_bull_bar = _e0_price > _e0_open

            # 近10根內有明顯低點（V底）
            _e0_recent = close.iloc[-10:]
            _e0_low_idx = int(_e0_recent.values.argmin())
            _e0_low_val = float(_e0_recent.min())
            _e0_recovery = (_e0_price - _e0_low_val) / _e0_low_val * 100
            _e0_v_shape  = _e0_low_idx >= 2 and _e0_low_idx <= 8  # 低點在近期，已反彈
            _e0_enough_recovery = _e0_recovery > 0.15  # 已反彈至少0.15%

            # EMA5 斜率開始向上（剛止跌）
            _e0_e5_turning = _e0_e5 >= _e0_e5p  # EMA5 不再下降

            # DIF 斜率轉正（動能轉向）
            _e0_dif_turn = float(dif.iloc[-1]) > float(dif.iloc[-2])

            # 量能相對前3根放大（底部放量）
            _e0_vol_now  = float(vol.iloc[-1])
            _e0_vol_prev = float(vol.iloc[-4:-1].mean()) if len(vol) >= 4 else _e0_vol_now
            _e0_vol_expand = _e0_vol_now >= _e0_vol_prev * 0.8  # 量能不萎縮即可

            if (_e0_bear_align and _e0_bull_bar and _e0_v_shape
                    and _e0_enough_recovery and _e0_e5_turning
                    and _e0_dif_turn and _e0_vol_expand):
                ck = f"{symbol}|{period_label}|空頭底部反彈|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    _e0_tags = [f"低點{_e0_low_val:.2f}已反彈+{_e0_recovery:.2f}%"]
                    if _e0_dif_turn: _e0_tags.append("DIF轉向↑")
                    if _e0_e5_turning: _e0_tags.append("EMA5止跌")
                    add_alert(symbol, period_label,
                              f"🟡 【底部反彈初訊】空頭排列中低點反彈第一根陽線"
                              f"（低點{_e0_low_val:.2f}→現價{_e0_price:.2f}，+{_e0_recovery:.2f}%）"
                              f"，EMA5止跌＋DIF轉向，均線翻多前最早期入場機會"
                              f"｜{'＋'.join(_e0_tags)}，注意確認後再加倉！", "bull")
                    new_signals.append(f"底部反彈初訊+{_e0_recovery:.2f}%")
                    tl_log_decision(symbol, period_label, "E0",
                                    triggered=True, signal_type="bull",
                                    reason=f"空頭排列底部反彈：低點{_e0_low_val:.2f}→{_e0_price:.2f}(+{_e0_recovery:.2f}%)",
                                    confidence=60,
                                    key_values={"EMA5止跌": _e0_e5_turning, "DIF轉向": _e0_dif_turn,
                                                "反彈幅度": f"{_e0_recovery:.2f}%", "低點位置": _e0_low_idx})
        except Exception:
            pass
    if len(close) >= 20:
        # MACD 深負值後連續3根收縮（對應圖中 MACD 從 -0.48 開始回升）
        hist_neg_shrink = (
            hist.iloc[-1] < 0 and hist.iloc[-2] < 0 and hist.iloc[-3] < 0 and
            abs(hist.iloc[-1]) < abs(hist.iloc[-2]) < abs(hist.iloc[-3]) and
            abs(hist.iloc[-3]) > abs(hist.iloc[-20:].mean()) * 0.8   # 之前是深負值
        )
        dif_slope_turn = (
            dif.iloc[-1] > dif.iloc[-2] > dif.iloc[-3]  # DIF 連升
        )
        if hist_neg_shrink and dif_slope_turn:
            depth = abs(float(hist.iloc[-3]))
            add_alert(symbol, period_label,
                      f"🟡 【底部預警】MACD 負值底背離 + DIF 回升"
                      f"（深度={depth:.4f}，空頭動能衰竭，升浪醞釀）", "bull")
            new_signals.append("MACD底背離醞釀")

    # ── E2. 早期確認：空頭 EMA 排列首次出現收縮（均線聚合）────────────────
    was_full_bear = (
        float(e5.iloc[-5]) < float(e10.iloc[-5])   # 簡單判斷幾天前是空頭
    ) if len(close) >= 5 else False

    spread_e5_e30_now  = float(e30.iloc[-1]) - float(e5.iloc[-1])
    spread_e5_e30_prev = float(e30.iloc[-2]) - float(e5.iloc[-2])
    spread_e5_e30_2ago = float(e30.iloc[-3]) - float(e5.iloc[-3])

    # 空頭排列中 EMA 擴散縮小（空頭 EMA5 < EMA30，但差距收窄）
    bear_spread_shrinking = (
        spread_e5_e30_now > 0 and      # 仍是空頭（EMA5 < EMA30）
        spread_e5_e30_now < spread_e5_e30_prev < spread_e5_e30_2ago and   # 連縮
        spread_e5_e30_now < spread_e5_e30_2ago * 0.6                      # 縮幅>40%
    )
    _dif_slope_turn = dif.iloc[-1] > dif.iloc[-2] > dif.iloc[-3]
    if bear_spread_shrinking and hist.iloc[-1] < 0 and _dif_slope_turn:
        add_alert(symbol, period_label,
                  f"🟡 【底部預警】空頭 EMA 排列收縮中"
                  f"（EMA5-30 差距 {spread_e5_e30_2ago:.3f}→{spread_e5_e30_now:.3f}）"
                  f" 多頭排列即將形成", "bull")
        new_signals.append("空頭EMA收縮")

    # ── E3. 關鍵確認：EMA5 上穿 EMA10 + EMA20（升浪啟動訊號）──────────────
    # 對應圖中均線從聚合點開始多頭發散
    e5_cross_e10 = e5.iloc[-1] > e10.iloc[-1] and e5.iloc[-2] <= e10.iloc[-2]
    e5_cross_e20 = e5.iloc[-1] > e20.iloc[-1] and e5.iloc[-2] <= e20.iloc[-2]
    e5_cross_e30 = e5.iloc[-1] > e30.iloc[-1] and e5.iloc[-2] <= e30.iloc[-2]

    cross_count = sum([e5_cross_e10, e5_cross_e20, e5_cross_e30])
    if cross_count >= 2:
        lines_crossed = []
        if e5_cross_e10: lines_crossed.append("EMA10")
        if e5_cross_e20: lines_crossed.append("EMA20")
        if e5_cross_e30: lines_crossed.append("EMA30")
        add_alert(symbol, period_label,
                  f"🟢 【買入訊號】EMA5 同時上穿 {'/'.join(lines_crossed)}"
                  f"（均線黃金交叉集群，升浪啟動）", "bull")
        new_signals.append(f"EMA5金叉集群×{cross_count}")

    # ── E4. 升浪加速：空頭→多頭排列完全翻轉（圖中升浪中段最強訊號）────────
    was_bear_order = (
        len(close) >= 10 and
        float(e5.iloc[-10]) < float(e10.iloc[-10]) < float(e20.iloc[-10])
    )
    is_now_bull_order = (
        float(e5.iloc[-1]) > float(e10.iloc[-1]) > float(e20.iloc[-1]) > float(e30.iloc[-1])
    )
    if was_bear_order and is_now_bull_order:
        # 計算升幅
        bottom_price = float(close.iloc[-20:].min()) if len(close) >= 20 else price
        rise_pct = (price - bottom_price) / bottom_price * 100
        add_alert(symbol, period_label,
                  f"🚀 【買入確認】空頭排列完全翻轉為多頭排列"
                  f"（距底部 +{rise_pct:.2f}%，升浪已確立）", "bull")
        new_signals.append("空→多排列翻轉")

    # ── E5. 底部多指標共振買入（最高強度，對應圖中最佳買點區域）────────────
    macd_gold = dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]  # MACD金叉
    price_above_e20 = float(close.iloc[-1]) > float(e20.iloc[-1])
    e5_above_e10 = float(e5.iloc[-1]) > float(e10.iloc[-1])
    bull_candle = float(close.iloc[-1]) > float(opn.iloc[-1])
    vol_expand = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.2   # 量能配合

    bottom_resonance = sum([
        macd_gold,
        price_above_e20,
        e5_above_e10,
        bull_candle,
        vol_expand,
        hist.iloc[-1] > hist.iloc[-2] > 0,   # MACD柱擴大
    ])
    if bottom_resonance >= 4:
        tags = []
        if macd_gold:          tags.append("MACD金叉")
        if price_above_e20:    tags.append("站上EMA20")
        if e5_above_e10:       tags.append("EMA排列")
        if bull_candle:        tags.append("陽線確認")
        if vol_expand:         tags.append("量能配合")
        add_alert(symbol, period_label,
                  f"🔔 【強烈買入】底部多指標共振 ({bottom_resonance}/6)"
                  f" ｜{'＋'.join(tags)}", "bull")
        new_signals.append(f"底部共振×{bottom_resonance}")

    # ════════════════════════════════════════════════════════════════════════
    # B. 趨勢「已確立」偵測（多指標共振）
    # ════════════════════════════════════════════════════════════════════════

    # B1. MACD 金叉 / 死叉
    if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]:
        add_alert(symbol, period_label, "✅ 趨勢確立｜MACD 金叉 🟢", "bull")
        new_signals.append("MACD金叉")
    if dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]:
        add_alert(symbol, period_label, "✅ 趨勢確立｜MACD 死叉 🔴", "bear")
        new_signals.append("MACD死叉")

    # B2. EMA5 穿越 EMA20
    if e5.iloc[-1] > e20.iloc[-1] and e5.iloc[-2] <= e20.iloc[-2]:
        add_alert(symbol, period_label, "✅ 趨勢確立｜EMA5 上穿 EMA20 ⬆️", "bull")
        new_signals.append("EMA5上穿EMA20")
    if e5.iloc[-1] < e20.iloc[-1] and e5.iloc[-2] >= e20.iloc[-2]:
        add_alert(symbol, period_label, "✅ 趨勢確立｜EMA5 下穿 EMA20 ⬇️", "bear")
        new_signals.append("EMA5下穿EMA20")

    # B3. 多頭/空頭 EMA 完整排列（強趨勢共振）
    ema_vals = [calc_ema(close, n).iloc[-1] for n, _ in EMA_CONFIGS]
    if all(ema_vals[i] > ema_vals[i+1] for i in range(len(ema_vals)-1)):
        add_alert(symbol, period_label, "🚀 趨勢確立｜全 EMA 多頭排列（強勢上升趨勢）", "bull")
        new_signals.append("全EMA多頭排列")
        add_entry_tracker(symbol, "LONG", "全EMA多頭排列", price, period_label)
    elif all(ema_vals[i] < ema_vals[i+1] for i in range(len(ema_vals)-1)):
        add_alert(symbol, period_label, "💀 趨勢確立｜全 EMA 空頭排列（強勢下降趨勢）", "bear")
        new_signals.append("全EMA空頭排列")
        add_entry_tracker(symbol, "SHORT", "全EMA空頭排列", price, period_label)

    # B4. 放量突破/跌破支撐阻力
    itvl_key   = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(period_label, "1d")
    pivots_h, pivots_l = calc_pivot(df, interval=itvl_key)
    if pivots_h:
        broken = [p[1] for p in pivots_h if prev_price <= p[1] < price]
        if broken:
            vol_surge = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.5
            tag = "放量" if vol_surge else ""
            add_alert(symbol, period_label,
                      f"✅ 趨勢確立｜{tag}突破阻力位 ${max(broken):.2f} ⚡", "bull")
            new_signals.append(f"突破阻力${max(broken):.2f}")
    if pivots_l:
        broken = [p[1] for p in pivots_l if price < p[1] <= prev_price]
        if broken:
            vol_surge = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.5
            tag = "放量" if vol_surge else ""
            add_alert(symbol, period_label,
                      f"✅ 趨勢確立｜{tag}跌破支撐位 ${min(broken):.2f} ⚠️", "bear")
            new_signals.append(f"跌破支撐${min(broken):.2f}")

    # B5. 異常放量
    if vol.iloc[-1] > vol_ma5.iloc[-1] * 2:
        add_alert(symbol, period_label,
                  f"📊 異常放量 {vol.iloc[-1]/vol_ma5.iloc[-1]:.1f}x 均量", "vol")
        new_signals.append(f"異常放量{vol.iloc[-1]/vol_ma5.iloc[-1]:.1f}x")

    # ════════════════════════════════════════════════════════════════════════
    # C0. 通道反轉偵測（下降通道底反彈 / 上升通道頂壓回 / 通道突破）
    # ════════════════════════════════════════════════════════════════════════
    for _ch_result in detect_channel_signals(df):
        _ch_msg, _ch_type = _ch_result[0], _ch_result[1]
        _is_action = _ch_result[2] if len(_ch_result) > 2 else False
        add_alert(symbol, period_label, _ch_msg, _ch_type)
        new_signals.append(_ch_msg[:25])
        # 強力信號觸發即時 Toast 彈窗
        if _is_action:
            _icon = "🟢" if _ch_type == "bull" else "🔴"
            st.toast(f"{_icon} {symbol} {period_label}\n{_ch_msg[:60]}", icon=_icon)

    # C. 趨勢「反轉」偵測
    # ════════════════════════════════════════════════════════════════════════

    # C1. MACD 背離（Price vs MACD histogram）
    # 多頭背離：價格創新低但 MACD 柱走高（底背離）
    if len(close) >= 20:
        recent_low_price  = close.iloc[-20:].min()
        recent_low_macd_h = hist.iloc[-20:].min()
        # 底背離：當前是近20根新低，但MACD柱比上個低點高
        if (close.iloc[-1] <= recent_low_price * 1.002 and
            hist.iloc[-1] > hist.iloc[-10:].min() * 1.3 and
            hist.iloc[-1] < 0):
            add_alert(symbol, period_label,
                      "🔄 反轉訊號｜MACD 底背離（價格新低，動能回升）", "bull")
            new_signals.append("MACD底背離")

        # 頂背離：當前是近20根新高，但MACD柱比上個高點低
        recent_high_price = close.iloc[-20:].max()
        if (close.iloc[-1] >= recent_high_price * 0.998 and
            hist.iloc[-1] < hist.iloc[-10:].max() * 0.7 and
            hist.iloc[-1] > 0):
            add_alert(symbol, period_label,
                      "🔄 反轉訊號｜MACD 頂背離（價格新高，動能減弱）", "bear")
            new_signals.append("MACD頂背離")

    # C2. K 線反轉形態
    body     = abs(close.iloc[-1] - opn.iloc[-1])
    up_wick  = high.iloc[-1] - max(close.iloc[-1], opn.iloc[-1])
    dn_wick  = min(close.iloc[-1], opn.iloc[-1]) - low.iloc[-1]
    body_avg = abs(close - opn).rolling(10).mean().iloc[-1]

    # 錘頭（下影線長 > 2倍實體，在下降趨勢末端）→ 多頭反轉
    if (dn_wick > body * 2 and dn_wick > body_avg and
            up_wick < body * 0.3 and
            close.iloc[-3] < close.iloc[-5]):     # 之前在下降
        add_alert(symbol, period_label,
                  f"🔄 反轉訊號｜錘頭K線（下影線={dn_wick:.2f}，潛在底部反彈）", "bull")
        new_signals.append("錘頭K線")

    # 流星（上影線長 > 2倍實體，在上升趨勢末端）→ 空頭反轉
    if (up_wick > body * 2 and up_wick > body_avg and
            dn_wick < body * 0.3 and
            close.iloc[-3] > close.iloc[-5]):     # 之前在上升
        add_alert(symbol, period_label,
                  f"🔄 反轉訊號｜流星K線（上影線={up_wick:.2f}，潛在頂部反轉）", "bear")
        new_signals.append("流星K線")

    # 吞噬形態（Engulfing）
    prev_body = close.iloc[-2] - opn.iloc[-2]
    curr_body = close.iloc[-1] - opn.iloc[-1]
    # 多頭吞噬：前紅後大綠
    if (prev_body < 0 and curr_body > 0 and
            opn.iloc[-1] < close.iloc[-2] and close.iloc[-1] > opn.iloc[-2] and
            abs(curr_body) > abs(prev_body)):
        add_alert(symbol, period_label,
                  "🔄 反轉訊號｜多頭吞噬（大陽線吞噬前陰線）", "bull")
        new_signals.append("多頭吞噬")
    # 空頭吞噬：前綠後大紅
    if (prev_body > 0 and curr_body < 0 and
            opn.iloc[-1] > close.iloc[-2] and close.iloc[-1] < opn.iloc[-2] and
            abs(curr_body) > abs(prev_body)):
        add_alert(symbol, period_label,
                  "🔄 反轉訊號｜空頭吞噬（大陰線吞噬前陽線）", "bear")
        new_signals.append("空頭吞噬")

    # ── C2-EXT. 完整20種K線形態偵測（無需TA-Lib）────────────────────────────
    _candle_signals = detect_candlestick_patterns(df)
    for _cs_name, _cs_type, _cs_msg in _candle_signals:
        _cs_ck = f"{symbol}|{period_label}|{_cs_name}|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
        if _cs_ck not in st.session_state.sent_alerts:
            st.session_state.sent_alerts.add(_cs_ck)
            add_alert(symbol, period_label, _cs_msg, _cs_type)
            new_signals.append(_cs_name)
            # 高置信K線形態 → 建立進場追蹤
            if _cs_name in ("K18-早晨之星", "K12-看漲吞噬", "K20a-三白兵", "K07-蜻蜓十字"):
                add_entry_tracker(symbol, "LONG", _cs_name, float(close.iloc[-1]), period_label)
            elif _cs_name in ("K19-黃昏之星", "K13-看跌吞噬", "K20b-三黑鴉", "K08-墓碑十字"):
                add_entry_tracker(symbol, "SHORT", _cs_name, float(close.iloc[-1]), period_label)

    # C3. 快速跌破 EMA60（趨勢破壞）
    if (close.iloc[-1] < e60.iloc[-1] and
            close.iloc[-2] >= e60.iloc[-2] and
            close.iloc[-3] >= e60.iloc[-3]):      # 連續2根在上方，突然跌破
        chg_pct = abs(price - float(e60.iloc[-1])) / float(e60.iloc[-1]) * 100
        add_alert(symbol, period_label,
                  f"⚠️ 反轉訊號｜跌破 EMA60（趨勢支撐破壞，偏差 {chg_pct:.1f}%）", "bear")
        new_signals.append("跌破EMA60")
    if (close.iloc[-1] > e60.iloc[-1] and
            close.iloc[-2] <= e60.iloc[-2] and
            close.iloc[-3] <= e60.iloc[-3]):
        chg_pct = abs(price - float(e60.iloc[-1])) / float(e60.iloc[-1]) * 100
        add_alert(symbol, period_label,
                  f"📈 反轉訊號｜突破 EMA60（趨勢壓力突破，偏差 {chg_pct:.1f}%）", "bull")
        new_signals.append("突破EMA60")

    # C3b. RSI 超賣/超買反轉
    rsi_series = calc_rsi(close, 14)
    if len(rsi_series.dropna()) >= 5:
        rsi_now  = float(rsi_series.iloc[-1])
        rsi_prev = float(rsi_series.iloc[-2])
        rsi_3ago = float(rsi_series.iloc[-4]) if len(rsi_series) >= 4 else rsi_prev

        # ── C3b-1. RSI 從超賣穿越30（底部反彈確認）
        if rsi_prev < 30 and rsi_now >= 30:
            add_alert(symbol, period_label,
                      f"🟢 反轉訊號｜RSI 超賣回升穿越30 ({rsi_now:.1f}) 潛在底部反彈", "bull")
            new_signals.append(f"RSI超賣回升{rsi_now:.0f}")

        # ── C3b-2. RSI 從超買回落穿越70（頂部預警）
        elif rsi_prev > 70 and rsi_now <= 70:
            add_alert(symbol, period_label,
                      f"🔴 反轉訊號｜RSI 超買回落穿越70 ({rsi_now:.1f}) 潛在頂部回撤", "bear")
            new_signals.append(f"RSI超買回落{rsi_now:.0f}")

        # ── C3b-3. RSI 持續在超買區且仍上升（強勢延伸，圖右側74的場景）
        elif rsi_now > 70 and rsi_prev > 70 and rsi_now > rsi_prev:
            ck = f"{symbol}|{period_label}|RSI超買強勢延伸|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"🚀 【RSI超買強勢】RSI={rsi_now:.1f} 持續在超買區且仍上升"
                          f"，強勢趨勢延伸中，不宜輕易做空，但注意高位風險！", "bull")
                new_signals.append(f"RSI超買強勢延伸{rsi_now:.0f}")

        # ── C3b-4. RSI 持續在超賣區且仍下降（弱勢延伸，繼續下跌）
        elif rsi_now < 30 and rsi_prev < 30 and rsi_now < rsi_prev:
            ck = f"{symbol}|{period_label}|RSI超賣弱勢延伸|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"💀 【RSI超賣弱勢】RSI={rsi_now:.1f} 持續在超賣區且仍下降"
                          f"，弱勢延伸，避免接刀！等待RSI回升再考慮入場。", "bear")
                new_signals.append(f"RSI超賣弱勢延伸{rsi_now:.0f}")

        # ── C3b-5. RSI 底背離（價格新低但RSI未新低，圖中底部反彈前的最早期訊號）
        if len(rsi_series.dropna()) >= 20:
            _rsi20 = rsi_series.dropna().iloc[-20:]
            _close20 = close.iloc[-20:]
            # 找兩個低點
            _rsi_min_idx  = int(_rsi20.values.argmin())
            _price_min_idx = int(_close20.values.argmin())
            # 如果價格低點比RSI低點更靠後（更近期），且價格更低但RSI更高 → 底背離
            if (_price_min_idx > _rsi_min_idx + 2
                    and float(_close20.iloc[-1]) > float(_close20.iloc[_price_min_idx])  # 已離底
                    and float(_rsi20.iloc[_price_min_idx]) > float(_rsi20.iloc[_rsi_min_idx]) * 0.98):
                _rsi_at_bottom = float(_rsi20.iloc[_price_min_idx])
                _rsi_at_first  = float(_rsi20.iloc[_rsi_min_idx])
                if _rsi_at_bottom > _rsi_at_first * 1.05:  # RSI底背離確認
                    ck = f"{symbol}|{period_label}|RSI底背離|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📈 【RSI底背離】價格創新低但RSI未創新低"
                                  f"（RSI底={_rsi_at_first:.1f}→{_rsi_at_bottom:.1f}）"
                                  f"，反彈動能醞釀中！", "bull")
                        new_signals.append(f"RSI底背離")

    # C3c. MACD 從深負值金叉（圖中底部最強反轉訊號）
    # 普通金叉 vs 深負值金叉：深負值代表空頭積累能量更多，反轉力度更強
    if len(close) >= 30:
        _dif_c = float(dif.iloc[-1]); _dea_c = float(dea.iloc[-1])
        _dif_p = float(dif.iloc[-2]); _dea_p = float(dea.iloc[-2])
        _golden_cross = _dif_c > _dea_c and _dif_p <= _dea_p
        if _golden_cross:
            # 找金叉前的DIF最低點（代表下跌深度）
            _dif_min = float(dif.iloc[-30:].min())
            if _dif_min < -0.5:   # 深負值金叉（之前跌很深）
                ck = f"{symbol}|{period_label}|MACD深谷金叉|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if _dif_min < -1.0:
                        _depth_lbl = f"極深谷({_dif_min:.3f})"
                    else:
                        _depth_lbl = f"深谷({_dif_min:.3f})"
                    add_alert(symbol, period_label,
                              f"🔔 【MACD深谷金叉】MACD從{_depth_lbl}完成金叉"
                              f"（DIF={_dif_c:.3f} 上穿 DEA={_dea_c:.3f}）"
                              f"，深度越深反轉力度越強，底部反彈確認！", "bull")
                    new_signals.append(f"MACD深谷金叉{_dif_min:.2f}")

    # C3d. MACD 深谷震盪底（圖中特殊場景：DIF=-7.37但柱→-0.099，DIF與DEA快要貼合）
    # 與C3c不同：C3c是「剛完成金叉」，C3d是「即將金叉但DIF仍在極深位，需謹慎」
    if len(hist) >= 10 and len(dif) >= 10:
        _c3d_dif_cur   = float(dif.iloc[-1])
        _c3d_dea_cur   = float(dea.iloc[-1])
        _c3d_hist_cur  = float(hist.iloc[-1])
        _c3d_hist_min  = float(hist.iloc[-40:].min()) if len(hist) >= 40 else float(hist.min())
        _c3d_hist_range = abs(_c3d_hist_min)

        # 條件：DIF在極深負值（<-3），但柱已收縮至不足原來10%（即將金叉）
        _c3d_deep_dif   = _c3d_dif_cur < -3.0
        _c3d_hist_tiny  = _c3d_hist_range > 0 and abs(_c3d_hist_cur) < _c3d_hist_range * 0.1
        _c3d_near_cross = abs(_c3d_dif_cur - _c3d_dea_cur) < abs(_c3d_dif_cur) * 0.02  # 差距<2%
        _c3d_dif_rising = float(dif.iloc[-1]) > float(dif.iloc[-3])  # DIF仍在上升

        if _c3d_deep_dif and _c3d_hist_tiny and _c3d_near_cross:
            _c3d_ck = f"{symbol}|{period_label}|MACD深谷震盪底|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if _c3d_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_c3d_ck)
                _recovery_pct = (abs(_c3d_hist_cur) / _c3d_hist_range) * 100
                add_alert(symbol, period_label,
                          f"⚡ 【MACD深谷震盪底】DIF={_c3d_dif_cur:.3f}（極深負值）"
                          f"，MACD柱已從最深{_c3d_hist_min:.2f}收縮至{_c3d_hist_cur:.3f}"
                          f"（僅剩{_recovery_pct:.1f}%），DIF即將與DEA={_c3d_dea_cur:.3f}金叉"
                          f"，⚠️ 注意：DIF仍在極深位，非真實反轉！"
                          f"需配合價格突破均線壓力帶才能確認{'（DIF持續上升中）' if _c3d_dif_rising else '（DIF未確認上升）'}", "info")
                new_signals.append(f"MACD深谷震盪底DIF{_c3d_dif_cur:.1f}")
                tl_log_decision(symbol, period_label, "C3d",
                                triggered=True, signal_type="info",
                                reason=f"DIF={_c3d_dif_cur:.2f}極深，柱剩{_recovery_pct:.1f}%，即將金叉但需謹慎",
                                confidence=45,
                                key_values={"DIF": _c3d_dif_cur, "DEA": _c3d_dea_cur,
                                            "柱": _c3d_hist_cur, "柱最深": _c3d_hist_min,
                                            "已收縮": f"{100-_recovery_pct:.0f}%"})
    if e5.iloc[-1] > e10.iloc[-1] and e5.iloc[-2] <= e10.iloc[-2]:
        add_alert(symbol, period_label,
                  "🔄 反轉訊號｜EMA5 上穿 EMA10（短線動能反轉向上）", "bull")
        new_signals.append("EMA5/10金叉")
    if e5.iloc[-1] < e10.iloc[-1] and e5.iloc[-2] >= e10.iloc[-2]:
        add_alert(symbol, period_label,
                  "🔄 反轉訊號｜EMA5 下穿 EMA10（短線動能反轉向下）", "bear")
        new_signals.append("EMA5/10死叉")

    # ════════════════════════════════════════════════════════════════════════
    # D. 均線集群反轉偵測（對應圖片場景：多頭排列頂部死亡交叉集群）
    # ════════════════════════════════════════════════════════════════════════

    e30  = calc_ema(close, 30)
    e_vals_now  = {5: e5.iloc[-1],  10: e10.iloc[-1],
                   20: e20.iloc[-1], 30: e30.iloc[-1], 60: e60.iloc[-1]}
    e_vals_prev = {5: e5.iloc[-2],  10: e10.iloc[-2],
                   20: e20.iloc[-2], 30: e30.iloc[-2], 60: e60.iloc[-2]}

    # D1. 均線集群收縮（EMA5~EMA60 價差急劇縮小 → 即將死叉）
    spread_now  = e_vals_now[5]  - e_vals_now[60]
    spread_prev = e_vals_prev[5] - e_vals_prev[60]
    spread_2ago = float(e5.iloc[-3]) - float(e60.iloc[-3])
    was_bull_spread = spread_2ago > 0 and spread_prev > 0  # 之前是多頭排列
    if (was_bull_spread and
            spread_now < spread_prev * 0.5 and   # 擴散值縮小超過50%
            spread_now > 0):                      # 尚未死叉但快了
        add_alert(symbol, period_label,
                  f"⚠️ 頂部預警｜EMA5-60 多頭擴散急速收縮"
                  f"（{spread_2ago:.3f}→{spread_prev:.3f}→{spread_now:.3f}）"
                  f" 死叉風險升高", "bear")
        new_signals.append("EMA集群收縮")

    # D2. 均線集群死亡交叉：EMA5 連續下穿多條均線（圖片核心場景）
    crossed_down = []
    for n, e_now, e_prev in [
        (10,  e10,  None),
        (20,  e20,  None),
        (30,  e30,  None),
    ]:
        e_ser = calc_ema(close, n)
        if e5.iloc[-1] < e_ser.iloc[-1] and e5.iloc[-2] >= e_ser.iloc[-2]:
            crossed_down.append(f"EMA{n}")
    if len(crossed_down) >= 2:
        add_alert(symbol, period_label,
                  f"🔴 【賣出信號】EMA5 同時下穿 {'/'.join(crossed_down)}"
                  f"（均線死亡交叉集群，強烈賣出訊號）", "bear")
        new_signals.append(f"EMA5死叉集群×{len(crossed_down)}")
    elif len(crossed_down) == 1:
        add_alert(symbol, period_label,
                  f"🔴 反轉訊號｜EMA5 下穿 {crossed_down[0]}", "bear")
        new_signals.append(f"EMA5下穿{crossed_down[0]}")

    # D3. 頂部多指標共振賣出（最高強度警告）
    # 條件：價格從近期高點回落 + MACD 頂背離 + 均線開始死叉 + 放量陰線
    recent_high = float(close.iloc[-20:].max()) if len(close) >= 20 else price
    price_from_top_pct = (recent_high - price) / recent_high * 100
    macd_topdiv = (close.iloc[-1] >= recent_high * 0.997 and
                   hist.iloc[-1] < hist.iloc[-10:].max() * 0.7 and
                   hist.iloc[-1] > 0)
    ema_death   = len(crossed_down) >= 1
    bear_candle = float(close.iloc[-1]) < float(opn.iloc[-1])
    vol_surge   = vol.iloc[-1] > vol_ma5.iloc[-1] * 1.3

    resonance_count = sum([macd_topdiv, ema_death, bear_candle, vol_surge,
                           price_from_top_pct > 0.3])
    if resonance_count >= 3:
        tags = []
        if macd_topdiv:            tags.append("MACD頂背離")
        if ema_death:              tags.append(f"均線死叉")
        if bear_candle:            tags.append("頂部陰線")
        if vol_surge:              tags.append("放量出貨")
        if price_from_top_pct>0.3: tags.append(f"距高點-{price_from_top_pct:.1f}%")
        add_alert(symbol, period_label,
                  f"🚨 【強烈賣出】頂部多指標共振 ({resonance_count}/5)"
                  f" ｜{'＋'.join(tags)}", "bear")
        new_signals.append(f"頂部共振×{resonance_count}")

    # D4. 多頭排列崩潰：前一根是完整多頭排列，現在 EMA 排列開始倒序
    was_full_bull = all(e_vals_prev[a] > e_vals_prev[b]
                        for a, b in [(5,10),(10,20),(20,30),(30,60)])
    is_bull_broken = not all(e_vals_now[a] > e_vals_now[b]
                             for a, b in [(5,10),(10,20),(20,30),(30,60)])
    if was_full_bull and is_bull_broken:
        add_alert(symbol, period_label,
                  "⚠️ 頂部預警｜多頭 EMA 排列首次出現破口（趨勢轉弱開始）", "bear")
        new_signals.append("多頭排列破口")

    # ── D5. 完整空頭排列確認（圖中核心場景：EMA5<10<20<30<60<120<200）────────
    # D 節原有偵測器只抓「剛死叉瞬間」，但圖中已完成排列，持續壓制更重要
    _e120 = calc_ema(close, 120)
    _e200 = calc_ema(close, 200) if len(close) >= 200 else None

    _e_now_ext = {5: e5.iloc[-1], 10: e10.iloc[-1], 20: e20.iloc[-1],
                  30: e30.iloc[-1], 60: e60.iloc[-1]}
    _e_now_ext[120] = float(_e120.iloc[-1])
    if _e200 is not None:
        _e_now_ext[200] = float(_e200.iloc[-1])

    # 計算有幾層是空頭排列（由小到大均線依次遞增）
    _bear_layers = []
    _chain = [5, 10, 20, 30, 60, 120]
    if _e200 is not None: _chain.append(200)
    for i in range(len(_chain)-1):
        a, b = _chain[i], _chain[i+1]
        if _e_now_ext[a] < _e_now_ext[b]:
            _bear_layers.append(f"EMA{a}<{b}")

    # 完整空頭排列：5層以上（EMA5<10<20<30<60<120）
    _full_bear_align = len(_bear_layers) >= 5
    # 強化版：含EMA200（6層）
    _ultra_bear_align = (len(_chain) >= 7 and len(_bear_layers) >= 6)

    if _full_bear_align:
        _d5_ck = f"{symbol}|{period_label}|完整空頭排列確認|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
        if _d5_ck not in st.session_state.sent_alerts:
            st.session_state.sent_alerts.add(_d5_ck)
            # 計算排列壓力帶：最低均線（EMA5）到最高均線的價差
            _bear_top = max(_e_now_ext.values())     # 最高均線 = 最大阻力
            _bear_bot = min(_e_now_ext.values())     # 最低均線 = 第一支撐
            _align_spread = _bear_top - _bear_bot
            _align_grade = "🚨 超強空頭" if _ultra_bear_align else "🔴 完整空頭"
            add_alert(symbol, period_label,
                      f"{_align_grade}排列｜{'→'.join(['EMA'+str(x) for x in _chain[:len(_bear_layers)+1]])}"
                      f"（{len(_bear_layers)}層均線全部空頭排列）"
                      f"，多頭反彈均面臨 {_bear_bot:.2f}-{_bear_top:.2f} 均線壓力帶（寬{_align_spread:.2f}）"
                      f"，趨勢明確向下，反彈宜輕倉！", "bear")
            new_signals.append(f"空頭排列{len(_bear_layers)}層確認")
            tl_log_decision(symbol, period_label, "D5",
                            triggered=True, signal_type="bear",
                            reason=f"完整空頭排列{len(_bear_layers)}層，均線壓力帶{_bear_bot:.2f}-{_bear_top:.2f}",
                            confidence=70 + len(_bear_layers) * 4,
                            key_values={f"EMA{k}": round(v, 3) for k, v in sorted(_e_now_ext.items())
                                        if k <= 60})

    # ── D6. 反彈觸及均線壓力帶後拒絕下跌（均線壓制反彈失敗）────────────────
    # 場景：上漲觸及 EMA5/10 附近，但收盤跌回 → 空頭排列壓制確認
    if _full_bear_align and len(df) >= 3:
        _d6_hi   = float(df["High"].iloc[-1]) if "High" in df.columns else price
        _d6_op   = float(opn.iloc[-1])
        _d6_cl   = price
        # 上影線觸及某條均線，但收盤在開盤以下（看跌吞噬/上引線）
        _upper_shadow = _d6_hi - max(_d6_op, _d6_cl)
        _body         = abs(_d6_cl - _d6_op)
        _d6_bear_candle = _d6_cl < _d6_op  # 陰線

        # 找到高點觸及的均線
        _rejected_ema = None
        for _ema_p in [5, 10, 20, 30]:
            _ev = _e_now_ext.get(_ema_p, 0)
            if abs(_d6_hi - _ev) / _ev < 0.003 and _d6_cl < _ev:  # 高點碰到均線但收在下面
                _rejected_ema = _ema_p
                break

        if _rejected_ema and _d6_bear_candle and _upper_shadow > _body * 0.5:
            _d6_ck = f"{symbol}|{period_label}|反彈均線壓制|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if _d6_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_d6_ck)
                add_alert(symbol, period_label,
                          f"📉 【反彈被均線壓制】K線高點{_d6_hi:.2f}觸及 EMA{_rejected_ema}={_e_now_ext[_rejected_ema]:.2f}"
                          f" 後收盤{_d6_cl:.2f}跌回均線下方"
                          f"，上引線={_upper_shadow:.3f} 空頭排列壓制有效！"
                          f"　做空機會，止損設於 EMA{_rejected_ema} 之上", "bear")
                new_signals.append(f"反彈EMA{_rejected_ema}壓制")
                tl_log_decision(symbol, period_label, "D6",
                                triggered=True, signal_type="bear",
                                reason=f"反彈至EMA{_rejected_ema}={_e_now_ext[_rejected_ema]:.2f}被壓制，陰線收{_d6_cl:.2f}",
                                confidence=78,
                                key_values={"觸及均線": f"EMA{_rejected_ema}", "高點": _d6_hi,
                                            "收盤": _d6_cl, "上影線": round(_upper_shadow,3)})

    # ── D7. EMA 長短期扭曲結構（圖中關鍵：EMA200在EMA5下方 + EMA120<EMA60）──
    # 場景：EMA200=395 < EMA5=401，長期均線低於短期 → 長期底部還在下方
    #       EMA120=415 < EMA60=422 → 中長線空頭扭曲（先下後上的中期下跌）
    if len(close) >= 120:
        _d7_e200 = float(calc_ema(close, 200).iloc[-1]) if len(close) >= 200 else None
        _d7_e120 = float(calc_ema(close, 120).iloc[-1])
        _d7_e60  = float(e60.iloc[-1])
        _d7_e5   = float(e5.iloc[-1])
        _d7_e20  = float(e20.iloc[-1])

        # 情形1：EMA200低於EMA5（長線底部在短線下方 → 夾擊結構）
        _d7_e200_below_short = _d7_e200 is not None and _d7_e200 < _d7_e5
        # 情形2：EMA120 < EMA60（中長線倒序 → 空頭深度下跌扭曲）
        _d7_mid_inverted = _d7_e120 < _d7_e60
        # 情形3：整體均線離散度 > 5%（高度發散，趨勢強）
        _all_emas = [_d7_e5, _d7_e20, _d7_e60, _d7_e120]
        if _d7_e200: _all_emas.append(_d7_e200)
        _d7_dispersion = (max(_all_emas) - min(_all_emas)) / min(_all_emas) * 100

        if _d7_e200_below_short and _d7_mid_inverted:
            _d7_ck = f"{symbol}|{period_label}|EMA長短期扭曲|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
            if _d7_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_d7_ck)
                _squeeze = _d7_e60 - _d7_e200   # 夾擊空間
                add_alert(symbol, period_label,
                          f"⚠️ 【EMA長短期扭曲結構】EMA200={_d7_e200:.1f}（長線底部）"
                          f"仍低於EMA5={_d7_e5:.1f}（短線）"
                          f"，同時EMA120={_d7_e120:.1f}<EMA60={_d7_e60:.1f}（中長線空頭扭曲）"
                          f"，價格夾在長線支撐({_d7_e200:.1f})與均線壓力帶({_d7_e5:.1f}-{_d7_e60:.1f})之間"
                          f"，夾擊空間{_squeeze:.1f}點，趨勢混沌！"
                          f"　均線離散度{_d7_dispersion:.1f}%（{'高度發散' if _d7_dispersion>5 else '正常'}）", "bear")
                new_signals.append(f"EMA長短扭曲離散{_d7_dispersion:.0f}%")
                tl_log_decision(symbol, period_label, "D7",
                                triggered=True, signal_type="bear",
                                reason=f"EMA200({_d7_e200:.1f})<EMA5({_d7_e5:.1f})且EMA120<EMA60，離散度{_d7_dispersion:.1f}%",
                                confidence=72,
                                key_values={"EMA200": round(_d7_e200,1), "EMA120": round(_d7_e120,1),
                                            "EMA60": round(_d7_e60,1), "EMA5": round(_d7_e5,1),
                                            "離散度": f"{_d7_dispersion:.1f}%", "夾擊空間": round(_squeeze,1)})

        elif _d7_mid_inverted and not _d7_e200_below_short:
            # 僅中長線扭曲（不含EMA200）
            _d7b_ck = f"{symbol}|{period_label}|EMA中長扭曲|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
            if _d7b_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_d7b_ck)
                add_alert(symbol, period_label,
                          f"📊 【EMA中長期扭曲】EMA120={_d7_e120:.1f}<EMA60={_d7_e60:.1f}"
                          f"（中長線空頭排列倒序），趨勢已有深度下跌後的技術性反彈特徵"
                          f"，均線離散度{_d7_dispersion:.1f}%", "bear")
                new_signals.append(f"EMA中長扭曲")

    # ── D8. 均線離散度趨勢強度指標（Dispersion Index）─────────────────────────
    # 均線越發散 → 趨勢越強；均線收斂 → 趨勢衰退，可能反轉
    if len(close) >= 60:
        _d8_emas = {5: float(e5.iloc[-1]), 10: float(e10.iloc[-1]),
                    20: float(e20.iloc[-1]), 30: float(e30.iloc[-1]),
                    60: float(e60.iloc[-1])}
        _d8_prev_emas = {5: float(e5.iloc[-2]), 10: float(e10.iloc[-2]),
                         20: float(e20.iloc[-2]), 30: float(e30.iloc[-2]),
                         60: float(e60.iloc[-2])}

        _d8_spread_now  = max(_d8_emas.values()) - min(_d8_emas.values())
        _d8_spread_prev = max(_d8_prev_emas.values()) - min(_d8_prev_emas.values())

        # 離散度百分比（相對於均值）
        _d8_mean = sum(_d8_emas.values()) / len(_d8_emas)
        _d8_di_pct = _d8_spread_now / _d8_mean * 100

        # 離散度在擴大（趨勢加速）
        _d8_expanding = _d8_spread_now > _d8_spread_prev * 1.05

        # 空頭排列下的高離散度 = 空頭趨勢強度高
        _d8_is_bear = _d8_emas[5] < _d8_emas[60]
        _d8_ck_day  = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]

        if _d8_di_pct > 4 and _d8_is_bear:
            _d8_ck = f"{symbol}|{period_label}|空頭均線高離散|{_d8_ck_day}"
            if _d8_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_d8_ck)
                _d8_grade = "🔴 極高強度" if _d8_di_pct > 7 else "⚠️ 高強度" if _d8_di_pct > 4 else "📊 中等"
                add_alert(symbol, period_label,
                          f"{_d8_grade}空頭趨勢｜EMA離散度={_d8_di_pct:.1f}%"
                          f"（均線最高{max(_d8_emas.values()):.1f}"
                          f"vs最低{min(_d8_emas.values()):.1f}，差{_d8_spread_now:.1f}點）"
                          f"，{'離散擴大中（空頭加速）' if _d8_expanding else '離散收縮（趨勢減速）'}"
                          f"，短線反彈空間受限於均線壓力帶！", "bear")
                new_signals.append(f"空頭離散度{_d8_di_pct:.1f}%")

        elif _d8_di_pct > 4 and not _d8_is_bear:
            _d8_ck = f"{symbol}|{period_label}|多頭均線高離散|{_d8_ck_day}"
            if _d8_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_d8_ck)
                add_alert(symbol, period_label,
                          f"🚀 強勢多頭趨勢｜EMA離散度={_d8_di_pct:.1f}%"
                          f"（EMA5={_d8_emas[5]:.1f}領跑EMA60={_d8_emas[60]:.1f}）"
                          f"，{'擴散加速，順勢持多！' if _d8_expanding else '擴散放緩，注意減速'}", "bull")
                new_signals.append(f"多頭離散度{_d8_di_pct:.1f}%")

    # ════════════════════════════════════════════════════════════════════════
    # F. 跳空缺口偵測（掃描最近 N 根，捕捉日K/週K/月K 跳空）
    # ════════════════════════════════════════════════════════════════════════
    if len(df) >= 5:
        itvl_key_gap = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(period_label, "1d")
        is_daily_tf  = itvl_key_gap in ("1d", "1wk", "1mo")

        # 掃描窗口：首次啟動時回掃更多根補抓歷史缺口，之後縮短避免重複
        # 週K/月K 低頻，首次用較大窗口；之後只掃最新 2-3 根
        _first_scan_key = f"gap_scanned_{symbol}_{period_label}"
        if _first_scan_key not in st.session_state:
            # 首次：日K回掃5根，週K/月K回掃8根（覆蓋近2個月的週K）
            scan_bars = 8 if itvl_key_gap in ("1wk", "1mo") else 5
            st.session_state[_first_scan_key] = True
        else:
            # 之後：只掃最新 2-3 根（增量更新）
            scan_bars = 3 if itvl_key_gap in ("1wk", "1mo") else 2

        min_gap_pct       = 0.05 if is_daily_tf else 0.10
        vol_thresh_surge  = 1.3  if is_daily_tf else 1.5
        vol_thresh_strong = 1.8  if is_daily_tf else 2.0

        in_bull_trend = float(e5.iloc[-1]) > float(e20.iloc[-1]) > float(e60.iloc[-1])
        in_bear_trend = float(e5.iloc[-1]) < float(e20.iloc[-1])

        def _bar_date(idx_val):
            return idx_val.strftime("%Y%m%d") if hasattr(idx_val, "strftime") else str(idx_val)[:10]

        # ── 掃描最近 scan_bars 根 K 線（含當根）─────────────────────────────
        # 規則：只有最新根（scan_i==1）才真正發出警示和Telegram
        #       歷史根只靜默記錄到 sent_alerts（防止重啟後重複發送），不發通知
        for scan_i in range(scan_bars, 0, -1):
            bar_i      = -scan_i          # 被掃描根（-1=最新）
            prev_i     = -(scan_i + 1)    # 前一根
            is_latest  = (scan_i == 1)    # 只有最新根才真正通知

            if abs(prev_i) > len(df): continue

            b_open  = float(opn.iloc[bar_i])
            b_close = float(close.iloc[bar_i])
            b_high  = float(high.iloc[bar_i])
            b_low   = float(low.iloc[bar_i])
            p_high  = float(high.iloc[prev_i])
            p_low   = float(low.iloc[prev_i])
            p_close = float(close.iloc[prev_i])
            if p_close == 0: continue

            # ATR（用於建議交易止損/止盈計算）
            _atr_window = max(3, min(14, len(close) + bar_i))
            atr_val = float((high - low).iloc[bar_i-_atr_window:bar_i].mean()) if _atr_window > 0 else float(b_high - b_low)

            gap_up_sz   = b_open - p_high
            gap_dn_sz   = p_low  - b_open
            gap_up_pct  = gap_up_sz / p_close * 100
            gap_dn_pct  = gap_dn_sz / p_close * 100

            # 計算當時的量能比（用那根K線對應位置的均量）
            vol_slice   = vol.iloc[:len(vol)+bar_i+1] if bar_i < -1 else vol.iloc[:-1]
            vol_ma_val  = vol_slice.rolling(10).mean().iloc[-1] if len(vol_slice) >= 3 else vol_slice.mean()
            if pd.isna(vol_ma_val) or vol_ma_val == 0:
                vol_ma_val = vol.iloc[bar_i]
            vol_ratio   = float(vol.iloc[bar_i]) / float(vol_ma_val)
            vol_surge   = vol_ratio >= vol_thresh_surge
            vol_strong  = vol_ratio >= vol_thresh_strong

            is_bull_bar = b_close > b_open
            is_bear_bar = b_close < b_open
            bar_date    = _bar_date(df.index[bar_i])

            # ── F0. 超級跳空（財報/重大消息級別）───────────────────────────
            # 條件：跳空幅度 ≥ 5% 且 量能 ≥ 5x，屬於機構強制重新定價
            _e200 = float(calc_ema(close, 200).iloc[bar_i]) if len(close) >= 200 else None
            _e20  = float(calc_ema(close, 20).iloc[bar_i])
            _above_e200 = (_e200 is not None) and (b_open > _e200)
            _above_e20  = b_open > _e20

            if gap_up_pct >= 5.0 and vol_ratio >= 5.0:
                ck = f"{symbol}|{period_label}|超級跳空上漲|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        tags = [f"跳空+{gap_up_pct:.1f}%", f"量×{vol_ratio:.0f}"]
                        if _above_e200: tags.append("突破EMA200長線")
                        if _above_e20:  tags.append("突破EMA20中線")
                        if b_close > b_open * 1.02: tags.append("強收陽線")
                        add_alert(symbol, period_label,
                                  f"🚀🚀 【財報級跳空】超級跳空上漲 +{gap_up_pct:.1f}%"
                                  f"（開{b_open:.2f} 前高{p_high:.2f}）"
                                  f" 量爆×{vol_ratio:.0f}｜{'＋'.join(tags)}"
                                  f"，可能為財報/重大消息，注意追高風險！", "bull")
                        new_signals.append(f"超級跳空+{gap_up_pct:.1f}%")

            elif gap_dn_pct >= 5.0 and vol_ratio >= 5.0:
                ck = f"{symbol}|{period_label}|超級跳空下跌|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        add_alert(symbol, period_label,
                                  f"💀💀 【財報級跳空】超級跳空下跌 -{gap_dn_pct:.1f}%"
                                  f"（開{b_open:.2f} 前低{p_low:.2f}）"
                                  f" 量爆×{vol_ratio:.0f}｜嚴重崩跌，避免接刀！", "bear")
                        new_signals.append(f"超級跳空下跌{gap_dn_pct:.1f}%")

            # ── F1. 向上跳空 + 放量 ──────────────────────────────────────
            if gap_up_pct >= min_gap_pct and vol_surge:
                ck = f"{symbol}|{period_label}|跳空上漲|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:   # 只有最新根才發通知
                        tags = [f"缺口+{gap_up_pct:.2f}%", f"量×{vol_ratio:.1f}"]
                        if vol_strong:                  tags.append("強放量")
                        if is_bull_bar:                 tags.append("陽線確認")
                        if in_bull_trend:               tags.append("多頭趨勢")
                        if dif.iloc[-1] > dea.iloc[-1]: tags.append("MACD多方")
                        strength = "🔔 【強烈買入】" if vol_strong and is_bull_bar else "🟢 【買入訊號】"
                        add_alert(symbol, period_label,
                                  f"{strength}跳空上漲 +{gap_up_pct:.2f}%"
                                  f"（開{b_open:.2f} 前高{p_high:.2f}）"
                                  f" 放量×{vol_ratio:.1f}｜{'＋'.join(tags)}", "bull")
                        new_signals.append(f"跳空上漲{gap_up_pct:.2f}%")

            # ── F2. 向上跳空無放量 ───────────────────────────────────────
            elif gap_up_pct >= 0.3 and not vol_surge:
                ck = f"{symbol}|{period_label}|跳空無量|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        add_alert(symbol, period_label,
                                  f"⚠️ 跳空上漲 +{gap_up_pct:.2f}%"
                                  f"（開{b_open:.2f} 前高{p_high:.2f}）"
                                  f" 量能僅×{vol_ratio:.1f}，注意假突破", "info")
                        new_signals.append(f"跳空無量{gap_up_pct:.2f}%")

            # ── F3. 向下跳空 + 放量 ──────────────────────────────────────
            if gap_dn_pct >= min_gap_pct and vol_surge:
                ck = f"{symbol}|{period_label}|跳空下跌|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        tags = [f"缺口-{gap_dn_pct:.2f}%", f"量×{vol_ratio:.1f}"]
                        if vol_strong:    tags.append("強放量")
                        if is_bear_bar:   tags.append("陰線確認")
                        if in_bear_trend: tags.append("空頭趨勢")
                        strength = "🔴 【強烈賣出】" if vol_strong and is_bear_bar else "🟠 【賣出訊號】"
                        add_alert(symbol, period_label,
                                  f"{strength}跳空下跌 -{gap_dn_pct:.2f}%"
                                  f"（開{b_open:.2f} 前低{p_low:.2f}）"
                                  f" 放量×{vol_ratio:.1f}｜{'＋'.join(tags)}", "bear")
                        new_signals.append(f"跳空下跌{gap_dn_pct:.2f}%")

            # ── F6. 衰竭跳空(上) → 空頭訊號（10年回測：隔日收低率100%，n=157）─
            # 定義：跳空上漲，但今日最高點低於前日最高（無力突破，動能衰竭）
            # 關鍵識別：今日最高 < 前日最高（HIGH_High_% < 0）
            if gap_up_pct >= min_gap_pct and vol_surge and b_high < p_high:
                ck = f"{symbol}|{period_label}|衰竭跳空上|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        _fail_pct = (p_high - b_high) / p_high * 100
                        _f6_msg = (f"🚨🚨 【F6·衰竭跳空(上)】跳空+{gap_up_pct:.2f}%"
                                   f" 但今高{b_high:.2f}<前高{p_high:.2f}（差{_fail_pct:.2f}%）"
                                   f" 量×{vol_ratio:.1f}"
                                   f"｜10年回測隔日收低率100%（n=157）"
                                   f"，上漲無力／主力出貨，最強空頭信號！")
                        add_alert(symbol, period_label, _f6_msg, "bear")
                        new_signals.append(f"F6-衰竭跳空上空頭{gap_up_pct:.1f}%")
                        generate_trade_suggestion(symbol, period_label, f"F6-衰竭跳空上空頭{gap_up_pct:.1f}%",
                                                  "bear", b_close, atr_val)
                        add_entry_tracker(symbol, "SHORT", f"F6-衰竭跳空上", b_close, period_label)

            # ── F7. 衰竭跳空(下) → 多頭訊號（10年回測：隔日收高率100%，n=150）─
            # 定義：跳空下跌，今日最低點低於前日最低（超跌後市場承接力強）
            # 關鍵識別：今日最低 < 前日最低
            if gap_dn_pct >= min_gap_pct and vol_surge and b_low < p_low:
                ck = f"{symbol}|{period_label}|衰竭跳空下|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        _low_ext = (p_low - b_low) / p_low * 100
                        _f7_msg = (f"🚀🚀 【F7·衰竭跳空(下)反彈】跳空-{gap_dn_pct:.2f}%"
                                   f" 且今低{b_low:.2f}<前低{p_low:.2f}（超跌{_low_ext:.2f}%）"
                                   f" 量×{vol_ratio:.1f}"
                                   f"｜10年回測隔日收高率100%（n=150）"
                                   f"，超跌承接有力，最強逆向買入！")
                        add_alert(symbol, period_label, _f7_msg, "bull")
                        new_signals.append(f"F7-衰竭跳空下反彈{gap_dn_pct:.1f}%")
                        generate_trade_suggestion(symbol, period_label, f"F7-衰竭跳空下反彈{gap_dn_pct:.1f}%",
                                                  "bull", b_close, atr_val)
                        add_entry_tracker(symbol, "LONG", f"F7-衰竭跳空下", b_close, period_label)

            # ── F8. 持續跳空(上) → 多頭訊號（10年回測：隔日收高率100%，n=90）──
            # 定義：跳空上漲，且今日最高突破前日最高（延伸突破，趨勢持續）
            # 關鍵識別：今日最高 > 前日最高（HIGH_High_% > 0）
            # 與F6相反——同樣跳空上漲，但今高>前高，動能持續而非衰竭
            if gap_up_pct >= min_gap_pct and vol_surge and b_high > p_high:
                ck = f"{symbol}|{period_label}|持續跳空上|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        _ext_pct = (b_high - p_high) / p_high * 100
                        _f8_msg = (f"🚀🚀 【F8·持續跳空(上)】跳空+{gap_up_pct:.2f}%"
                                   f" 且今高{b_high:.2f}>前高{p_high:.2f}（延伸+{_ext_pct:.2f}%）"
                                   f" 量×{vol_ratio:.1f}"
                                   f"｜10年回測隔日收高率100%（n=90）"
                                   f"，突破持續延伸，多頭趨勢最強確認！")
                        add_alert(symbol, period_label, _f8_msg, "bull")
                        new_signals.append(f"F8-持續跳空上多頭{gap_up_pct:.1f}%")
                        generate_trade_suggestion(symbol, period_label, f"F8-持續跳空上多頭{gap_up_pct:.1f}%",
                                                  "bull", b_close, atr_val)
                        add_entry_tracker(symbol, "LONG", f"F8-持續跳空上", b_close, period_label)

            # ── F9. 突破/持續跳空(下) → 空頭訊號（10年回測：隔日收低率99%，n=105）
            # 定義：跳空下跌，且今日最低繼續破前日最低（空頭趨勢持續延伸）
            # 注：此條件與F7(衰竭跳空下)相同——兩者在數據上完全重疊
            # F7已覆蓋此偵測，此處作為補充強調空頭版本（用不同識別key）
            # 特殊情況：跳空下跌 + 今低<前低 + 收陰線（比F7更強的空頭確認）
            if gap_dn_pct >= min_gap_pct and vol_surge and b_low < p_low and is_bear_bar:
                ck = f"{symbol}|{period_label}|持續跳空下|{bar_date}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    if is_latest:
                        _brk_pct = (p_low - b_low) / p_low * 100
                        _f9_msg = (f"🚨🚨 【F9·持續跳空(下)】跳空-{gap_dn_pct:.2f}%"
                                   f" 今低{b_low:.2f}<前低{p_low:.2f}（破底{_brk_pct:.2f}%）"
                                   f" 陰線確認 量×{vol_ratio:.1f}"
                                   f"｜10年回測隔日收低率99%（n=105）"
                                   f"，空頭持續延伸破底，強烈做空！")
                        add_alert(symbol, period_label, _f9_msg, "bear")
                        new_signals.append(f"F9-持續跳空下空頭{gap_dn_pct:.1f}%")
                        generate_trade_suggestion(symbol, period_label, f"F9-持續跳空下空頭{gap_dn_pct:.1f}%",
                                                  "bear", b_close, atr_val)
                        add_entry_tracker(symbol, "SHORT", f"F9-持續跳空下", b_close, period_label)

        # ── F4. 缺口回補測試（固定看最新根）─────────────────────────────────
        curr_low = float(low.iloc[-1])
        for lb in range(2, min(15, len(df)-1)):
            ph_lb = float(high.iloc[-(lb+1)])
            op_lb = float(opn.iloc[-lb])
            if op_lb > ph_lb:
                if ph_lb * 0.993 <= curr_low <= ph_lb * 1.005:
                    ck = f"{symbol}|{period_label}|缺口回補|{_bar_date(df.index[-1])}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"⚠️ 跳空缺口回補測試｜缺口頂 ${ph_lb:.2f}"
                                  f"，支撐能否守住是關鍵", "info")
                        new_signals.append("缺口回補測試")
                break

        # ── F5. 島形頂部反轉 ─────────────────────────────────────────────────
        if len(df) >= 3:
            p_close_f5 = float(close.iloc[-2]) if float(close.iloc[-2]) else 1
            gap_up_2ago    = float(opn.iloc[-2]) - float(high.iloc[-3])
            gap_down_today = float(low.iloc[-2]) - float(opn.iloc[-1])
            if gap_up_2ago > 0 and gap_down_today > 0:
                ck = f"{symbol}|{period_label}|島形頂部|{_bar_date(df.index[-1])}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"🚨 【島形頂部反轉】連續跳空孤島"
                              f"（上跳+{gap_up_2ago/p_close_f5*100:.2f}%"
                              f" 下跳-{gap_down_today/p_close_f5*100:.2f}%）強烈賣出", "bear")
                    new_signals.append("島形頂部反轉")

    # ════════════════════════════════════════════════════════════════════════
    # G. 均線極度聚合偵測（最佳交易時機：爆發前的壓縮）
    # 對應圖片：V型反轉後所有EMA收縮到392-393極小範圍 → 即將方向選擇
    # ════════════════════════════════════════════════════════════════════════
    if len(df) >= 20:
        # 計算所有 EMA 的當前值
        ema_set = {}
        for n in [5, 10, 20, 30, 60]:
            s = calc_ema(close, n)
            ema_set[n] = float(s.iloc[-1])

        ema_vals_list = list(ema_set.values())
        ema_max  = max(ema_vals_list)
        ema_min  = min(ema_vals_list)
        ema_mean = sum(ema_vals_list) / len(ema_vals_list)

        # 聚合程度：所有EMA的極差相對於均價的百分比
        compress_pct = (ema_max - ema_min) / ema_mean * 100 if ema_mean else 999

        # 歷史聚合程度（20根前的EMA極差，用來判斷是否在收縮中）
        ema_set_20ago = {}
        for n in [5, 10, 20, 30, 60]:
            s = calc_ema(close, n)
            if len(s) >= 20:
                ema_set_20ago[n] = float(s.iloc[-20])
        if ema_set_20ago:
            vals_20ago   = list(ema_set_20ago.values())
            compress_20ago = (max(vals_20ago) - min(vals_20ago)) / (sum(vals_20ago)/len(vals_20ago)) * 100
        else:
            compress_20ago = compress_pct

        # 判斷是否在持續收縮（5根前 vs 現在）
        ema_set_5ago = {}
        for n in [5, 10, 20, 30, 60]:
            s = calc_ema(close, n)
            if len(s) >= 5:
                ema_set_5ago[n] = float(s.iloc[-5])
        vals_5ago      = list(ema_set_5ago.values()) if ema_set_5ago else ema_vals_list
        compress_5ago  = (max(vals_5ago) - min(vals_5ago)) / (sum(vals_5ago)/len(vals_5ago)) * 100

        # 均線排列方向（用 EMA5 vs EMA60 判斷當前偏多/偏空/中性）
        e5_now  = ema_set[5]
        e60_now = ema_set[60]
        bias = "多頭偏向" if e5_now > e60_now * 1.001 else (
               "空頭偏向" if e5_now < e60_now * 0.999 else "完全中性")

        # 收縮中（20根前擴散→現在收縮）
        shrinking = compress_pct < compress_20ago * 0.6   # 收縮幅度超過40%

        # ── G1. 極度聚合（最緊繃，隨時爆發）──────────────────────────────
        # 圖中後半段：所有EMA差距<0.2%，是爆發前最後壓縮
        if compress_pct < 0.15:
            # 判斷爆發方向可能性
            price_vs_ema = (price - ema_mean) / ema_mean * 100
            direction_hint = ""
            if price > ema_max:
                direction_hint = "，價格在均線上方 → 偏多突破"
            elif price < ema_min:
                direction_hint = "，價格在均線下方 → 偏空突破"
            else:
                direction_hint = "，價格在均線内 → 方向未定"

            ck = f"{symbol}|{period_label}|EMA極度聚合|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"⚡ 【最佳時機】EMA5-60 極度聚合 {compress_pct:.3f}%"
                          f"（{ema_min:.2f}~{ema_max:.2f}）{direction_hint}"
                          f"，即將方向性爆發，密切關注！", "info")
                new_signals.append(f"EMA極度聚合{compress_pct:.3f}%")

        # ── G2. 高度聚合 + 持續收縮（爆發前預警）─────────────────────────
        elif compress_pct < 0.40 and shrinking:
            ck = f"{symbol}|{period_label}|EMA高度聚合|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"🔶 【爆發預警】EMA 高度聚合 {compress_pct:.3f}%"
                          f"（從 {compress_20ago:.2f}% 收縮至 {compress_pct:.2f}%）"
                          f"，{bias}，注意突破方向", "info")
                new_signals.append(f"EMA高度聚合{compress_pct:.2f}%")

        # ── G3. 聚合後方向突破（聚合結束，趨勢啟動）──────────────────────
        # 剛從聚合狀態（5根前聚合）突然擴散（現在擴散）
        just_exploded = compress_5ago < 0.40 and compress_pct > compress_5ago * 1.8

        if just_exploded:
            if e5_now > ema_set.get(10, e5_now) > ema_set.get(20, e5_now):
                ck = f"{symbol}|{period_label}|聚合後多頭突破|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"🚀 【買入時機】均線聚合後多頭方向爆發"
                              f"（聚合 {compress_5ago:.3f}% → 擴散 {compress_pct:.3f}%）"
                              f"，趨勢啟動！", "bull")
                    new_signals.append("聚合後多頭爆發")
            elif e5_now < ema_set.get(10, e5_now) < ema_set.get(20, e5_now):
                ck = f"{symbol}|{period_label}|聚合後空頭突破|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"💀 【賣出時機】均線聚合後空頭方向爆發"
                              f"（聚合 {compress_5ago:.3f}% → 擴散 {compress_pct:.3f}%）"
                              f"，趨勢下行！", "bear")
                    new_signals.append("聚合後空頭爆發")

        # ── G4. V型反轉後聚合（最強買入場景）────────────────────────────
        # 條件：近20根有明顯低點（V底），MACD完成金叉，且均線正在聚合
        if len(close) >= 20:
            recent_low_idx  = int(close.iloc[-20:].values.argmin())
            recent_low_val  = float(close.iloc[-20:].min())
            recovery_pct    = (price - recent_low_val) / recent_low_val * 100
            macd_golded     = dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]
            v_shape         = recovery_pct > 1.5 and recent_low_idx < 15  # 低點在中前段，已反彈
            in_compression  = compress_pct < 0.50

            if v_shape and macd_golded and in_compression:
                ck = f"{symbol}|{period_label}|V型反轉聚合|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"🔔 【最佳買入】V型反轉後均線聚合"
                              f"（底部 ${recent_low_val:.2f} 已反彈 +{recovery_pct:.1f}%）"
                              f" + MACD金叉 + EMA聚合 {compress_pct:.3f}%"
                              f"，等待突破方向確認後入場！", "bull")
                    new_signals.append(f"V型反轉聚合+MACD金叉")

        # ── G5. 均線回測再突破（第二次聚合後突破，更可靠）──────────────────
        # 圖中形態：第一次聚合突破後，均線回縮再次纏繞，然後再度向上發散
        if len(close) >= 30:
            try:
                # 用 EMA5/10/20/30 計算壓縮度（比 EMA60 對短周期更靈敏）
                _e5h  = calc_ema(close, 5).iloc[-30:]
                _e10h = calc_ema(close, 10).iloc[-30:]
                _e20h = calc_ema(close, 20).iloc[-30:]
                _e30h = calc_ema(close, 30).iloc[-30:]
                _mean = (_e5h + _e10h + _e20h + _e30h) / 4
                _compress_g5 = (
                    (_e5h - _e30h).abs()
                ) / _mean * 100   # EMA5 vs EMA30 極差 / 均值

                # 閾值依時間週期調整（1分鐘更靈敏，用 0.15%）
                _tight_thresh = 0.20
                _tight_mask_g5 = _compress_g5 < _tight_thresh
                _tight_idx_g5  = [i for i, v in enumerate(_tight_mask_g5) if v]

                if len(_tight_idx_g5) >= 3:
                    _last_tight  = _tight_idx_g5[-1]
                    _first_tight = _tight_idx_g5[0]
                    _tight_dur   = _last_tight - _first_tight
                    _bars_since  = 29 - _last_tight

                    e5_cur  = float(_e5h.iloc[-1])
                    e20_cur = float(_e20h.iloc[-1])
                    e30_cur = float(_e30h.iloc[-1])
                    comp_cur = float(_compress_g5.iloc[-1])

                    # 多頭回測再突破：壓縮後突破，EMA5 > EMA20 > EMA30
                    if (_tight_dur >= 3 and _bars_since >= 2
                            and comp_cur > _tight_thresh * 1.2
                            and e5_cur > e20_cur > e30_cur
                            and e5_cur > float(_e5h.iloc[-4])):
                        ck = f"{symbol}|{period_label}|均線回測再突破|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                        if ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(ck)
                            add_alert(symbol, period_label,
                                      f"🎯 【回測再突破】均線纏繞({_tight_dur}根 <{_tight_thresh}%)"
                                      f"→突破後回測→二次向上發散"
                                      f"（EMA5:{e5_cur:.2f}>EMA20:{e20_cur:.2f}>EMA30:{e30_cur:.2f}）"
                                      f"，二次突破成功率更高！", "bull")
                            new_signals.append("均線回測再突破")

                    # 空頭回測再下破
                    elif (_tight_dur >= 3 and _bars_since >= 2
                            and comp_cur > _tight_thresh * 1.2
                            and e5_cur < e20_cur < e30_cur
                            and e5_cur < float(_e5h.iloc[-4])):
                        ck = f"{symbol}|{period_label}|均線回測再下破|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                        if ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(ck)
                            add_alert(symbol, period_label,
                                      f"⚠️ 【回測再下破】均線纏繞({_tight_dur}根)"
                                      f"→下破後回測→二次向下發散"
                                      f"（EMA5:{e5_cur:.2f}<EMA20:{e20_cur:.2f}<EMA30:{e30_cur:.2f}）"
                                      f"，空頭加速！", "bear")
                            new_signals.append("均線回測再下破")
            except Exception:
                pass

        # ── G6. 均線聚合中縮量陰線回測不破（最佳低風險買入點）───────────────
        # 圖中箭頭形態：
        #   - 均線已極度壓縮（所有EMA在0.3%以內）
        #   - 出現一根陰線（小回測）
        #   - 收盤仍在 EMA20 支撐上方
        #   - DIF 向上（底背離醞釀）
        #   - 這根陰線之後 = 低風險買入窗口
        if len(close) >= 20:
            try:
                _g6_e5  = float(calc_ema(close, 5).iloc[-1])
                _g6_e10 = float(calc_ema(close, 10).iloc[-1])
                _g6_e20 = float(calc_ema(close, 20).iloc[-1])
                _g6_e30 = float(calc_ema(close, 30).iloc[-1])
                _g6_e60 = float(calc_ema(close, 60).iloc[-1])
                _g6_emas = [_g6_e5, _g6_e10, _g6_e20, _g6_e30, _g6_e60]
                _g6_mean = sum(_g6_emas) / len(_g6_emas)
                _g6_spread = (max(_g6_emas) - min(_g6_emas)) / _g6_mean * 100

                _g6_price  = float(close.iloc[-1])
                _g6_open   = float(df["Open"].iloc[-1]) if "Open" in df.columns else _g6_price
                _g6_is_bear_bar = _g6_price < _g6_open   # 陰線

                _g6_dif, _g6_dea, _ = calc_macd(close)
                _g6_dif_now  = float(_g6_dif.iloc[-1])
                _g6_dif_prev = float(_g6_dif.iloc[-2])
                _g6_dif_rising = _g6_dif_now > _g6_dif_prev

                # 均線聚合 + 陰線回測 + 不破EMA20支撐 + DIF向上
                _g6_support_hold = _g6_price > _g6_e20 * 0.9992  # 距EMA20不超過0.08%
                _g6_above_mid    = _g6_price > _g6_mean * 0.9995 # 仍在均線叢中/上方

                # 前幾根均線方向：至少EMA5在上升趨勢
                _g6_e5_prev = float(calc_ema(close, 5).iloc[-3])
                _g6_uptrend = _g6_e5 >= _g6_e5_prev  # EMA5 不是在下降

                if (_g6_spread < 0.30          # 均線高度聚合
                        and _g6_is_bear_bar     # 這根是陰線
                        and _g6_support_hold    # 收盤守住EMA20
                        and _g6_above_mid       # 在均線叢中上方
                        and _g6_dif_rising      # DIF向上（動能醞釀）
                        and _g6_uptrend):       # 短期趨勢向上

                    ck = f"{symbol}|{period_label}|聚合縮量回測買點|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        _tag_list = [f"壓縮{_g6_spread:.3f}%", f"EMA20支撐{_g6_e20:.2f}"]
                        if _g6_dif_now < 0:
                            _tag_list.append("DIF負值向上↑（底背離醞釀）")
                        else:
                            _tag_list.append("DIF正值向上↑")
                        add_alert(symbol, period_label,
                                  f"🎯 【聚合回測買點】均線極度壓縮({_g6_spread:.3f}%)"
                                  f"，陰線回測守住EMA20({_g6_e20:.2f})"
                                  f"，DIF向上醞釀突破"
                                  f"｜{'＋'.join(_tag_list)}"
                                  f"，低風險買入窗口！", "bull")
                        new_signals.append(f"聚合回測買點{_g6_spread:.3f}%")
            except Exception:
                pass

        # ── G7. 長時間盤整後爆量突破（圖中最強形態）──────────────────────────
        # 條件：
        #   1. 近N根均線持續壓縮（盤整時間夠長，蓄力越久爆發越猛）
        #   2. 當根是大陽線（開<收，漲幅明顯）
        #   3. 量能爆發（×5以上）
        #   4. 突破前盤整高點
        if len(close) >= 25:
            try:
                _g7_e5  = calc_ema(close, 5)
                _g7_e20 = calc_ema(close, 20)
                _g7_e60 = calc_ema(close, 60)

                # 計算過去40根每根的壓縮度
                _g7_n = min(40, len(close)-2)
                _g7_compress_hist = []
                for _j in range(-_g7_n-1, -1):
                    _e5j  = float(_g7_e5.iloc[_j])
                    _e20j = float(_g7_e20.iloc[_j])
                    _e60j = float(_g7_e60.iloc[_j])
                    _mj   = (_e5j+_e20j+_e60j)/3
                    _g7_compress_hist.append((max(_e5j,_e20j,_e60j)-min(_e5j,_e20j,_e60j))/_mj*100)

                # 盤整持續根數（壓縮 < 0.5%）
                _g7_tight_bars = sum(1 for c in _g7_compress_hist if c < 0.5)
                _g7_tight_pct  = _g7_tight_bars / len(_g7_compress_hist) if _g7_compress_hist else 0

                # 當根是大陽線
                _g7_price = float(close.iloc[-1])
                _g7_open  = float(df["Open"].iloc[-1]) if "Open" in df.columns else _g7_price
                _g7_bar_pct = (_g7_price - _g7_open) / _g7_open * 100
                _g7_bull_bar = _g7_bar_pct > 0.2  # 漲幅>0.2%

                # 量能爆發
                _g7_vol_now  = float(vol.iloc[-1])
                _g7_vol_ma20 = float(vol.rolling(20).mean().iloc[-1]) if len(vol) >= 20 else _g7_vol_now
                _g7_vol_x    = _g7_vol_now / _g7_vol_ma20 if _g7_vol_ma20 > 0 else 1

                # 突破盤整高點
                _g7_range_high = float(close.iloc[-_g7_n-1:-1].max())
                _g7_breakout   = _g7_price > _g7_range_high * 1.001

                # 當前均線壓縮度（確認是從聚合直接突破，不是早就分散了）
                _g7_cur_compress = _g7_compress_hist[-1] if _g7_compress_hist else 999

                if (_g7_tight_pct >= 0.6        # 60%以上根數都在盤整
                        and _g7_tight_bars >= 15 # 至少盤整15根
                        and _g7_bull_bar         # 大陽線
                        and _g7_vol_x >= 5.0     # 量能×5以上
                        and _g7_breakout):        # 突破盤整高點

                    ck = f"{symbol}|{period_label}|長盤整爆量突破|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        # 依盤整時間和量能評級
                        if _g7_tight_bars >= 40 and _g7_vol_x >= 8:
                            _g7_grade = "🚀🚀 極強"
                        elif _g7_tight_bars >= 25 or _g7_vol_x >= 8:
                            _g7_grade = "🚀 強力"
                        else:
                            _g7_grade = "⚡ 有效"
                        add_alert(symbol, period_label,
                                  f"{_g7_grade}【長盤整爆量突破】"
                                  f"盤整{_g7_tight_bars}根後大陽線突破（漲{_g7_bar_pct:+.2f}%）"
                                  f"，量爆×{_g7_vol_x:.1f}（{_g7_vol_now/10000:.0f}萬）"
                                  f"，突破盤整高點{_g7_range_high:.2f}"
                                  f"，蓄力越久爆發越猛，趨勢啟動！", "bull")
                        new_signals.append(f"長盤整×{_g7_tight_bars}爆量×{_g7_vol_x:.0f}突破")
                        conf = min(95, 60 + _g7_tight_bars//2 + int(_g7_vol_x)*2)
                        tl_log_decision(symbol, period_label, "G7",
                                        triggered=True, signal_type="bull",
                                        reason=f"長盤整{_g7_tight_bars}根後爆量{_g7_vol_x:.1f}×突破高點{_g7_range_high:.2f}",
                                        confidence=min(conf, 95),
                                        key_values={"盤整根數": _g7_tight_bars, "量能倍數": f"{_g7_vol_x:.1f}x",
                                                    "陽線漲幅": f"{_g7_bar_pct:+.2f}%", "突破高點": _g7_range_high})

                # 空頭版：長盤整後放量跌破
                elif (_g7_tight_pct >= 0.6 and _g7_tight_bars >= 15
                        and _g7_bar_pct < -0.2 and _g7_vol_x >= 5.0
                        and _g7_price < float(close.iloc[-_g7_n-1:-1].min()) * 0.999):
                    ck = f"{symbol}|{period_label}|長盤整爆量跌破|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"💀 【長盤整爆量跌破】盤整{_g7_tight_bars}根後放量下破"
                                  f"（跌{_g7_bar_pct:.2f}%，量×{_g7_vol_x:.1f}）"
                                  f"，空頭方向確認，注意下行風險！", "bear")
                        new_signals.append(f"長盤整×{_g7_tight_bars}爆量跌破")

            except Exception:
                pass
    # ══════════════════════════════════════════════════════════════════════════
    try:
        _e5   = float(calc_ema(close, 5).iloc[-1])
        _e10  = float(calc_ema(close, 10).iloc[-1])
        _e20  = float(calc_ema(close, 20).iloc[-1])
        _e30  = float(calc_ema(close, 30).iloc[-1])
        _e60  = float(calc_ema(close, 60).iloc[-1])
        _price = float(close.iloc[-1])

        # 均線多頭排列：EMA5 > EMA10 > EMA20 > EMA30，且全部朝上
        _bull_align = (_e5 > _e10 > _e20 > _e30)
        _bear_align = (_e5 < _e10 < _e20 < _e30)

        # 量能計算：當前量 vs 近20根均量
        _vol_now  = float(vol.iloc[-1])
        _vol_ma20 = float(vol.rolling(20).mean().iloc[-1]) if len(vol) >= 20 else _vol_now
        _vol_x    = _vol_now / _vol_ma20 if _vol_ma20 > 0 else 1

        # 量能從低迷到爆發：近5根均量 vs 近20根均量，判斷是否突然放量
        _vol_ma5_now  = float(vol.iloc[-5:].mean()) if len(vol) >= 5 else _vol_now
        _vol_quiet    = _vol_ma5_now < _vol_ma20 * 0.7   # 近期量能低迷
        _vol_prev_low = float(vol.iloc[-6:-1].mean()) if len(vol) >= 6 else _vol_ma20
        _vol_surge_x  = _vol_now / _vol_prev_low if _vol_prev_low > 0 else 1

        # ── H1. 量能暴增 + 多頭排列（趨勢加速上漲）────────────────────────
        if _bull_align and _vol_x >= 3.0 and _price > _e5:
            ck = f"{symbol}|{period_label}|量能爆發多頭|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                _surge_desc = f"量×{_vol_x:.1f}（前均量{_vol_ma20/10000:.0f}萬→當前{_vol_now/10000:.0f}萬）"
                if _vol_x >= 8.0:
                    _h1_prefix = "🚀🔥 【極端爆量·多頭加速】"
                    _h1_suffix = f"量能達均量×{_vol_x:.0f}，屬機構性掃單！"
                elif _vol_x >= 5.0:
                    _h1_prefix = "🔥🔥 【超級爆量·多頭加速】"
                    _h1_suffix = f"量能達均量×{_vol_x:.0f}，強力追漲。"
                else:
                    _h1_prefix = "🔥 【量能爆發·多頭加速】"
                    _h1_suffix = "趨勢加速上漲！"
                add_alert(symbol, period_label,
                          f"{_h1_prefix}EMA5>{_e5:.2f}>EMA10>EMA20>EMA30 完整多頭排列"
                          f"，{_surge_desc}，{_h1_suffix}", "bull")
                new_signals.append(f"量爆×{_vol_x:.1f}多頭排列")

        # ── H2. 低迷量後突然爆量 + 均線突破（圖中 18:50 底部反彈場景）───
        elif _vol_surge_x >= 4.0 and _price > _e20 and _e5 > _e20:
            ck = f"{symbol}|{period_label}|低迷後爆量突破|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"⚡ 【低迷後爆量突破】量能靜止後突然暴增×{_vol_surge_x:.1f}"
                          f"，價格突破EMA20（{_e20:.2f}），EMA5>{_e5:.2f}>EMA20，注意追漲！", "bull")
                new_signals.append(f"低迷後爆量×{_vol_surge_x:.1f}")

        # ── H3. 量能爆發 + 空頭排列（趨勢加速下跌）────────────────────────
        elif _bear_align and _vol_x >= 3.0 and _price < _e5:
            ck = f"{symbol}|{period_label}|量能爆發空頭|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
            if ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(ck)
                add_alert(symbol, period_label,
                          f"💀 【量能爆發·空頭加速】EMA5<EMA10<EMA20<EMA30 完整空頭排列"
                          f"，量×{_vol_x:.1f}，趨勢加速下跌，避免接刀！", "bear")
                new_signals.append(f"量爆×{_vol_x:.1f}空頭排列")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # I. MACD 背離偵測（底背離/頂背離）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        # 依時間週期動態調整窗口：日K兩個頂可能相距60根，分鐘級40根就夠
        _i_window = 80 if any(x in period_label for x in ["日","1d","wk","mo","月","週","季","年"]) else 40
        _i_since_max = 40 if any(x in period_label for x in ["日","1d","wk","mo","月","週","季","年"]) else 20

        if len(close) >= _i_window // 2:
            _dif_i, _dea_i, _ = calc_macd(close)
            _n = min(_i_window, len(close))
            _cN   = close.iloc[-_n:]
            _difN = _dif_i.iloc[-_n:]

            def _find_lows(series):
                vals = list(series.values)
                lows = []
                for i in range(2, len(vals)-2):
                    if vals[i] < vals[i-1] and vals[i] < vals[i-2] and \
                       vals[i] < vals[i+1] and vals[i] < vals[i+2]:
                        lows.append(i)
                merged = []
                for idx in lows:
                    if not merged or idx - merged[-1] > 5:
                        merged.append(idx)
                    elif vals[idx] < vals[merged[-1]]:
                        merged[-1] = idx
                return merged[-2:] if len(merged) >= 2 else []

            def _find_highs(series):
                vals = list(series.values)
                highs = []
                for i in range(2, len(vals)-2):
                    if vals[i] > vals[i-1] and vals[i] > vals[i-2] and \
                       vals[i] > vals[i+1] and vals[i] > vals[i+2]:
                        highs.append(i)
                merged = []
                for idx in highs:
                    if not merged or idx - merged[-1] > 5:
                        merged.append(idx)
                    elif vals[idx] > vals[merged[-1]]:
                        merged[-1] = idx
                return merged[-2:] if len(merged) >= 2 else []

            # ── I1. MACD 底背離 ──────────────────────────────────────────────
            _pl = _find_lows(_cN)
            if len(_pl) >= 2:
                _p1 = float(_cN.iloc[_pl[-2]]); _p2 = float(_cN.iloc[_pl[-1]])
                _d1 = float(_difN.iloc[_pl[-2]]); _d2 = float(_difN.iloc[_pl[-1]])
                _since = (_n-1) - _pl[-1]
                _dif_rising = float(_dif_i.iloc[-1]) > float(_dif_i.iloc[-1-min(3,len(_dif_i)-1)])
                if (_p2 < _p1*0.9995 and _d2 > _d1*1.01 and _dif_rising and _since <= _i_since_max):
                    ck = f"{symbol}|{period_label}|MACD底背離|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📈 【MACD底背離】價格創新低({_p1:.2f}→{_p2:.2f})"
                                  f" 但DIF未創新低({_d1:.3f}→{_d2:.3f})"
                                  f"，空頭動能衰竭，可能即將反彈！", "bull")
                        new_signals.append("MACD底背離")

            # ── I2. MACD 頂背離 ──────────────────────────────────────────────
            _ph = _find_highs(_cN)
            if len(_ph) >= 2:
                _p1 = float(_cN.iloc[_ph[-2]]); _p2 = float(_cN.iloc[_ph[-1]])
                _d1 = float(_difN.iloc[_ph[-2]]); _d2 = float(_difN.iloc[_ph[-1]])
                _since = (_n-1) - _ph[-1]
                _dif_falling = float(_dif_i.iloc[-1]) < float(_dif_i.iloc[-1-min(3,len(_dif_i)-1)])
                # 頂背離強度：DIF差距越大越可靠
                _div_strength = (_d1 - _d2) / abs(_d1) * 100 if _d1 != 0 else 0
                if (_p2 > _p1*1.0005 and _d2 < _d1*0.99 and _dif_falling and _since <= _i_since_max):
                    ck = f"{symbol}|{period_label}|MACD頂背離|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        if _div_strength > 50:
                            _div_grade = "🚨 極強頂背離"
                        elif _div_strength > 25:
                            _div_grade = "⚠️ 強頂背離"
                        else:
                            _div_grade = "📉 頂背離"
                        add_alert(symbol, period_label,
                                  f"{_div_grade}｜價格創新高({_p1:.2f}→{_p2:.2f}，+{(_p2-_p1)/_p1*100:.1f}%)"
                                  f" 但DIF大幅衰退({_d1:.2f}→{_d2:.2f}，-{_div_strength:.0f}%)"
                                  f"，多頭動能嚴重衰竭，頂部反轉風險極高！", "bear")
                        new_signals.append(f"MACD頂背離DIF衰退{_div_strength:.0f}%")
                        tl_log_decision(symbol, period_label, "I2",
                                        triggered=True, signal_type="bear",
                                        reason=f"頂背離：價格{_p1:.2f}→{_p2:.2f}，DIF {_d1:.2f}→{_d2:.2f} 衰退{_div_strength:.0f}%",
                                        confidence=min(50 + int(_div_strength//2), 95),
                                        key_values={"高點1價格": _p1, "高點2價格": _p2,
                                                    "DIF高點1": round(_d1,2), "DIF高點2": round(_d2,2),
                                                    "DIF衰退": f"{_div_strength:.0f}%"})

            # ── I3. 絕對高點背離（圖中最典型：498創新高但DIF遠低於歷史峰值）──
            # 適用於跨週期頂背離：用全局DIF峰值比較，不依賴局部高點匹配
            if len(close) >= 30:
                _dif_all_max = float(_dif_i.iloc[:-5].max())   # 歷史DIF峰值（排除最近5根）
                _dif_cur     = float(_dif_i.iloc[-1])
                _price_cur   = float(close.iloc[-1])
                _price_max_n = float(close.iloc[-_n:].max())   # 近N根價格最高
                _dif_at_peak_bar = int(_dif_i.iloc[:-5].values.argmax())  # DIF峰值所在的bar
                _price_at_dif_peak = float(close.iloc[_dif_at_peak_bar])  # DIF峰值時的價格

                # 條件：當前價格接近歷史最高，但DIF遠低於歷史峰值
                _price_near_high  = _price_cur >= _price_max_n * 0.85    # 在最高點85%以內（放寬）
                _dif_far_below    = _dif_cur < _dif_all_max * 0.60       # DIF不足峰值60%
                _dif_declining    = _dif_cur < float(_dif_i.iloc[-5])    # DIF仍在下降
                _dif_was_positive = _dif_all_max > 1.0                   # 確認有過明顯升浪

                if (_price_near_high and _dif_far_below
                        and _dif_declining and _dif_was_positive):
                    _decay_pct = (1 - _dif_cur / _dif_all_max) * 100
                    ck = f"{symbol}|{period_label}|MACD絕對頂背離|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        if _decay_pct > 70:
                            _i3_grade = "🚨 極端頂背離"
                        elif _decay_pct > 50:
                            _i3_grade = "⚠️ 嚴重頂背離"
                        else:
                            _i3_grade = "📉 頂背離"
                        add_alert(symbol, period_label,
                                  f"{_i3_grade}｜價格在高位({_price_cur:.2f}，近高{_price_max_n:.2f}的{_price_cur/_price_max_n*100:.0f}%)"
                                  f" 但DIF僅剩歷史峰值的{100-_decay_pct:.0f}%"
                                  f"（峰值DIF={_dif_all_max:.2f}→當前={_dif_cur:.2f}，衰退{_decay_pct:.0f}%）"
                                  f"，多頭動能嚴重透支，大頂風險極高！", "bear")
                        new_signals.append(f"絕對頂背離DIF僅剩{100-_decay_pct:.0f}%")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # J. MACD Histogram 動能衰竭偵測
    # ══════════════════════════════════════════════════════════════════════════
    try:
        if len(close) >= 15:
            _dif_j, _dea_j, _hist_j = calc_macd(close)
            _hn  = float(_hist_j.iloc[-1])
            _hp  = float(_hist_j.iloc[-2])
            _h3  = float(_hist_j.iloc[-4])
            _s5  = (float(close.iloc[-1]) - float(close.iloc[-5])) / float(close.iloc[-5]) * 100
            _dif_now = float(_dif_j.iloc[-1])

            # ── J1. 多頭動能衰竭 ─────────────────────────────────────────────
            if (_hn > 0 and _hp > 0 and abs(_hn) < abs(_hp) < abs(_h3)
                    and _s5 < 0.1 and _dif_now > 0):
                ck = f"{symbol}|{period_label}|多頭動能衰竭|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"⚠️ 【多頭動能衰竭】Histogram連縮({_h3:.3f}→{_hp:.3f}→{_hn:.3f})"
                              f"，上漲動能減弱，注意高位風險！", "bear")
                    new_signals.append("多頭動能衰竭")

            # ── J2. 空頭動能衰竭 ─────────────────────────────────────────────
            elif (_hn < 0 and _hp < 0 and abs(_hn) < abs(_hp) < abs(_h3)
                    and _s5 > -0.1 and _dif_now < 0):
                ck = f"{symbol}|{period_label}|空頭動能衰竭|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"💡 【空頭動能衰竭】Histogram絕對值連縮({_h3:.3f}→{_hp:.3f}→{_hn:.3f})"
                              f"，下跌動能減弱，可能即將止跌反彈！", "bull")
                    new_signals.append("空頭動能衰竭")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # K. 趨勢線突破 + 水平支撐/阻力偵測（日K圖三點下降壓力線場景）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        if len(df) >= 20:
            _k_close = df["Close"]
            _k_price = float(_k_close.iloc[-1])

            # ── K1. 下降趨勢線突破（由空轉多的關鍵訊號）────────────────────
            _tl_down = calc_trendline(df, mode="high", lookback=min(80, len(df)), min_points=2)
            if _tl_down and _tl_down["valid"]:
                _tl_val  = _tl_down["current_val"]
                _tl_dist = _tl_down["distance_pct"]
                _tl_r2   = _tl_down["r2"]
                _tl_slope= _tl_down["slope"]
                _tl_pts  = len(_tl_down["points"])

                # 突破下降趨勢線（上方 0~3%）
                if _tl_down["breakout"] and 0 < _tl_dist < 3.0:
                    ck = f"{symbol}|{period_label}|下降趨勢線突破|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        _slope_str = f"{_tl_slope*5:.2f}/週" if "日" in period_label or "1d" in period_label else f"{_tl_slope:.3f}/根"
                        add_alert(symbol, period_label,
                                  f"🚀 【趨勢線突破】突破{_tl_pts}點下降壓力線"
                                  f"（趨勢線={_tl_val:.2f}，當前={_k_price:.2f}，距離+{_tl_dist:.2f}%）"
                                  f"，斜率{_slope_str}，R²={_tl_r2:.2f}"
                                  f"，空頭格局可能終結，注意量能確認！", "bull")
                        new_signals.append(f"下降趨勢線突破+{_tl_dist:.2f}%")

                # 接近下降趨勢線壓力（上方 -1% 到 0）
                elif not _tl_down["breakout"] and -1.5 < _tl_dist < 0:
                    ck = f"{symbol}|{period_label}|接近下降趨勢線|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"⚠️ 【趨勢線壓力】接近{_tl_pts}點下降壓力線"
                                  f"（趨勢線={_tl_val:.2f}，當前={_k_price:.2f}，距{abs(_tl_dist):.2f}%）"
                                  f"，注意阻力，突破前謹慎追漲！", "bear")
                        new_signals.append(f"接近下降趨勢線{_tl_dist:.2f}%")

            # ── K2. 上升趨勢線跌破（由多轉空的關鍵訊號）────────────────────
            _tl_up = calc_trendline(df, mode="low", lookback=min(80, len(df)), min_points=2)
            if _tl_up and _tl_up["valid"]:
                _tlu_val  = _tl_up["current_val"]
                _tlu_dist = _tl_up["distance_pct"]
                _tlu_pts  = len(_tl_up["points"])

                if _tl_up["breakout"] and -3.0 < _tlu_dist < 0:
                    ck = f"{symbol}|{period_label}|上升趨勢線跌破|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"💀 【趨勢線跌破】跌破{_tlu_pts}點上升支撐線"
                                  f"（趨勢線={_tlu_val:.2f}，當前={_k_price:.2f}，{_tlu_dist:.2f}%）"
                                  f"，多頭格局破壞，注意下行風險！", "bear")
                        new_signals.append(f"上升趨勢線跌破{_tlu_dist:.2f}%")

            # ── K3. 水平支撐反彈（多次測試後反彈，圖中390-395支撐帶）────────
            if len(_k_close) >= 30:
                # 找近30根的支撐帶（多次觸及的水平區間）
                _k_lows = sorted([float(_k_close.iloc[i]) for i in range(-30, 0)])
                _k_support_zone_low  = np.percentile(_k_lows, 8)   # 最低8%分位
                _k_support_zone_high = np.percentile(_k_lows, 18)  # 最低18%分位

                # 近期觸及支撐帶（近10根有碰到）
                _k_recent_lows = [float(df["Low"].iloc[i]) if "Low" in df.columns
                                  else float(_k_close.iloc[i]) for i in range(-10, 0)]
                _k_touched_support = any(_k_support_zone_low * 0.995 <= l <= _k_support_zone_high * 1.01
                                         for l in _k_recent_lows)
                # 當前價格在支撐帶上方反彈（至少1%）
                _k_rebounded = _k_price > _k_support_zone_high * 1.01

                if _k_touched_support and _k_rebounded:
                    _k_touch_count = sum(1 for l in _k_recent_lows
                                         if _k_support_zone_low * 0.995 <= l <= _k_support_zone_high * 1.02)
                    ck = f"{symbol}|{period_label}|支撐帶反彈|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📈 【支撐帶反彈】{_k_touch_count}次測試支撐帶"
                                  f"（{_k_support_zone_low:.2f}-{_k_support_zone_high:.2f}）後反彈"
                                  f"，當前={_k_price:.2f}"
                                  f"，支撐有效！可考慮逢低做多。", "bull")
                        new_signals.append(f"支撐帶反彈×{_k_touch_count}")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # L. 箱體突破偵測（長期橫盤後向上/向下突破阻力/支撐）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        if len(df) >= 25:
            _l_close = df["Close"]
            _l_price = float(_l_close.iloc[-1])

            def _calc_box(series, window=20, exclude_recent=3):
                base = series.iloc[-(window + exclude_recent):-exclude_recent]
                if len(base) < 5: return None
                hi = float(base.max()); lo = float(base.min()); mid = float(base.mean())
                return {"high": hi, "low": lo, "mid": mid,
                        "range_pct": (hi-lo)/mid*100, "bars": len(base)}

            # 找最緊的盤整窗口
            _best_box = None
            for _w in [10, 15, 20, 25]:
                _box = _calc_box(_l_close, window=_w)
                if _box and _box["range_pct"] < 1.8:
                    if _best_box is None or _box["range_pct"] < _best_box["range_pct"]:
                        _best_box = _box; _best_box["window"] = _w

            if _best_box:
                _bhi = _best_box["high"]; _blo = _best_box["low"]
                _brng = _best_box["range_pct"]; _bw = _best_box["window"]

                _l_vol_now = float(vol.iloc[-1])
                _l_vol_ma  = float(vol.iloc[-10:-1].mean()) if len(vol) >= 11 else _l_vol_now
                _l_vol_x   = _l_vol_now / _l_vol_ma if _l_vol_ma > 0 else 1

                _le5 = float(calc_ema(_l_close, 5).iloc[-1])
                _le10= float(calc_ema(_l_close, 10).iloc[-1])
                _le20= float(calc_ema(_l_close, 20).iloc[-1])
                _le30= float(calc_ema(_l_close, 30).iloc[-1])
                _l_bull_align = _le5 > _le10 > _le20 > _le30
                _l_bear_align = _le5 < _le10 < _le20 < _le30

                _ldif, _ldea, _ = calc_macd(_l_close)
                _l_dif_above = float(_ldif.iloc[-1]) > float(_ldea.iloc[-1])
                _l_dif_below = float(_ldif.iloc[-1]) < float(_ldea.iloc[-1])

                _l_break_up_pct = (_l_price - _bhi) / _bhi * 100
                _l_break_dn_pct = (_l_price - _blo) / _blo * 100

                # ── L1. 向上突破箱體 ─────────────────────────────────────────
                if (_l_price > _bhi * 1.003 and _l_break_up_pct < 5.0
                        and _l_vol_x >= 1.5 and _l_bull_align and _l_dif_above):
                    ck = f"{symbol}|{period_label}|箱體向上突破|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        _pfx = "🚀🚀 【超強" if _l_vol_x >= 5 else "🚀 【"
                        add_alert(symbol, period_label,
                                  f"{_pfx}箱體向上突破】橫盤{_bw}根"
                                  f"（箱頂{_bhi:.2f}，波動{_brng:.3f}%）"
                                  f"→ 放量×{_l_vol_x:.1f}突破至{_l_price:.2f}（+{_l_break_up_pct:.2f}%）"
                                  f"，均線多頭排列＋MACD翻正，阻力轉支撐，可積極追進！", "bull")
                        new_signals.append(f"箱體突破+{_l_break_up_pct:.2f}%×{_l_vol_x:.0f}倍量")

                # ── L2. 向下跌破箱體 ─────────────────────────────────────────
                elif (_l_price < _blo * 0.997 and _l_break_dn_pct > -5.0
                        and _l_vol_x >= 1.5 and _l_bear_align and _l_dif_below):
                    ck = f"{symbol}|{period_label}|箱體向下跌破|{df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"💀 【箱體向下跌破】橫盤{_bw}根"
                                  f"（箱底{_blo:.2f}，波動{_brng:.3f}%）"
                                  f"→ 放量×{_l_vol_x:.1f}跌破至{_l_price:.2f}（{_l_break_dn_pct:.2f}%）"
                                  f"，均線空頭排列＋MACD翻負，支撐轉阻力！", "bear")
                        new_signals.append(f"箱體跌破{_l_break_dn_pct:.2f}%×{_l_vol_x:.0f}倍量")

                # ── L3. 超長橫盤蓄勢預警 ─────────────────────────────────────
                elif _brng < 0.4 and _bw >= 12:
                    ck = f"{symbol}|{period_label}|超長橫盤預警|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"⏳ 【蓄勢待發】橫盤已{_bw}根，波動僅{_brng:.3f}%"
                                  f"（{_blo:.2f}-{_bhi:.2f}）"
                                  f"，能量極度壓縮，隨時可能方向性突破，密切監控！", "bull")
                        new_signals.append(f"超長橫盤{_bw}根{_brng:.3f}%")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # L. VIX 轉折 × 股價位置 共振訊號（圖：VIX高位轉跌＋股價低位→強力買入）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        _vix = fetch_vix_intraday()
        if not _vix.get("error") and _vix.get("spot"):
            _vix_spot   = float(_vix["spot"])
            _vix_pct    = float(_vix.get("chg_pct_from_prev", 0))
            _vix_trend  = _vix.get("trend_5bar", "flat")
            _vix_signal = int(_vix.get("signal", 0))   # -4~+4

            _lp = float(close.iloc[-1])
            _lp_low20  = float(close.iloc[-20:].min()) if len(close) >= 20 else _lp
            _lp_high20 = float(close.iloc[-20:].max()) if len(close) >= 20 else _lp
            _lp_range  = _lp_high20 - _lp_low20
            # 股價在近20根的相對位置（0=最低，100=最高）
            _lp_pos = (_lp - _lp_low20) / _lp_range * 100 if _lp_range > 0 else 50

            _ts = df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:13]

            # ── L1. VIX 高位急跌 + 股價在低位（最強買入共振）─────────────────
            # 圖中 20:00 場景：VIX 從高位開始下降，TSLA 從低點反彈
            if (_vix_signal >= 2          # VIX 下跌（利多股市）
                    and _vix_pct < -1.5   # VIX 較前日跌超1.5%
                    and _lp_pos < 35      # 股價在近期低位
                    and _vix_spot > 18):  # VIX 仍在相對高位（下跌空間大）
                ck = f"{symbol}|{period_label}|VIX高位急跌低位共振|{_ts}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"🚀 【VIX×股價共振買入】VIX={_vix_spot:.1f} 高位急跌 {_vix_pct:+.1f}%"
                              f"（{_vix.get('trend_label','')}）"
                              f"，股價在近期低位（位置{_lp_pos:.0f}%）"
                              f"，恐慌消退＋股價超跌，強力買入共振！", "bull")
                    new_signals.append(f"VIX高跌{_vix_pct:.1f}%×股價低位{_lp_pos:.0f}%")

            # ── L2. VIX 低位 + 股價創新高（趨勢延伸確認）────────────────────
            elif (_vix_signal >= 1 and _vix_spot < 16 and _lp_pos > 80):
                ck = f"{symbol}|{period_label}|VIX低位股價強勢|{_ts}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"📈 【低恐慌+強勢確認】VIX={_vix_spot:.1f} 低位平穩"
                              f"，股價在近期高位（{_lp_pos:.0f}%）"
                              f"，市場情緒穩定，趨勢延伸有效！", "bull")
                    new_signals.append(f"VIX低{_vix_spot:.0f}×股價強{_lp_pos:.0f}%")

            # ── L3. VIX 急升 + 股價在高位（頂部反轉預警）───────────────────
            elif (_vix_signal <= -2       # VIX 上升（利空股市）
                    and _vix_pct > 2.0    # VIX 較前日升超2%
                    and _lp_pos > 70      # 股價在近期高位
                    and _vix_spot > 18):  # VIX 有明顯水平
                ck = f"{symbol}|{period_label}|VIX急升高位共振|{_ts}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"⚠️ 【VIX×股價共振賣出】VIX={_vix_spot:.1f} 急升 {_vix_pct:+.1f}%"
                              f"（{_vix.get('trend_label','')}）"
                              f"，股價在近期高位（位置{_lp_pos:.0f}%）"
                              f"，恐慌升溫＋股價高位，注意下行風險！", "bear")
                    new_signals.append(f"VIX急升{_vix_pct:.1f}%×股價高位{_lp_pos:.0f}%")

            # ── L4. VIX 暴升（恐慌級別）+ 任意倉位（極端風險警報）────────────
            if _vix_signal <= -4 or (_vix_pct > 10 and _vix_spot > 25):
                ck = f"{symbol}|{period_label}|VIX極端恐慌|{_ts}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    add_alert(symbol, period_label,
                              f"🚨 【極端恐慌警報】VIX={_vix_spot:.1f} 暴升 {_vix_pct:+.1f}%"
                              f"，市場進入恐慌模式，所有多單注意風控！", "bear")
                    new_signals.append(f"VIX極端恐慌{_vix_spot:.0f}")

            # ── L5. VIX 絕對水平警戒區（無論漲跌，水平本身就有意義）─────────
            # 圖中 VIX=25.66 已進入高恐慌區（>25），TSLA 對應跌到 399 區
            _vix_zone_ck = f"{symbol}|{period_label}|VIX水平警戒|{df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]}"
            if _vix_zone_ck not in st.session_state.sent_alerts:
                if _vix_spot >= 30:
                    st.session_state.sent_alerts.add(_vix_zone_ck)
                    add_alert(symbol, period_label,
                              f"🚨 【VIX極度恐慌區】VIX={_vix_spot:.1f} ≥30"
                              f"，歷史上此水平對應市場重大下跌，極端謹慎！", "bear")
                    new_signals.append(f"VIX極度恐慌≥30")
                elif _vix_spot >= 25:
                    st.session_state.sent_alerts.add(_vix_zone_ck)
                    add_alert(symbol, period_label,
                              f"⚠️ 【VIX高恐慌區】VIX={_vix_spot:.1f} 介於25-30"
                              f"，市場恐慌情緒明顯，股票下行壓力大，謹慎持多！", "bear")
                    new_signals.append(f"VIX高恐慌25-30")
                elif _vix_spot <= 13:
                    st.session_state.sent_alerts.add(_vix_zone_ck)
                    add_alert(symbol, period_label,
                              f"📊 【VIX極低參考】VIX={_vix_spot:.1f} ≤13"
                              f"，市場樂觀但回測顯示此區間隔日收高率僅40.6%（低於隨機）"
                              f"，過度樂觀易反轉，謹慎追多！", "info")
                    new_signals.append(f"VIX極低謹慎≤13")

            # ── L6. VIX 盤中急升偵測（當日漲幅，圖中3/6當天+28%場景）─────────
            # chg_pct_from_prev 是相對前日收盤的變化
            _vix_intraday_surge = abs(_vix_pct) > 15  # 當日漲跌超15%
            if _vix_intraday_surge:
                _surge_ck = f"{symbol}|{period_label}|VIX盤中急升|{_ts}"
                if _surge_ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(_surge_ck)
                    if _vix_pct > 15:   # 急升→股市恐慌
                        add_alert(symbol, period_label,
                                  f"🚨 【VIX盤中暴升{_vix_pct:+.0f}%】VIX={_vix_spot:.1f}"
                                  f"，單日恐慌指數暴增，可能對應股市急跌！"
                                  f"（參考：股價近期低位{_lp_low20:.2f}）", "bear")
                        new_signals.append(f"VIX盤中暴升{_vix_pct:.0f}%")
                    else:               # 急跌→恐慌消退
                        add_alert(symbol, period_label,
                                  f"🚀 【VIX盤中暴跌{_vix_pct:.0f}%】VIX={_vix_spot:.1f}"
                                  f"，恐慌指數單日大幅消退，股市反彈機率大！", "bull")
                        new_signals.append(f"VIX盤中暴跌{_vix_pct:.0f}%")

            # ── L7. VIX 多日趨勢偵測（日K視角：圖中從15→23.76持續上升）────────
            try:
                _vix_hist = fetch_vix_history()
                if len(_vix_hist) >= 10:
                    _vh = _vix_hist.values
                    _vh_now  = float(_vh[-1])
                    _vh_5d   = float(_vh[-5])    # 5日前
                    _vh_10d  = float(_vh[-10])   # 10日前
                    _vh_low  = float(min(_vh[-20:]))  # 近20日最低
                    _vh_high = float(max(_vh[-20:]))  # 近20日最高

                    # 多日累計升幅
                    _vix_5d_chg  = (_vh_now - _vh_5d)  / _vh_5d  * 100
                    _vix_10d_chg = (_vh_now - _vh_10d) / _vh_10d * 100

                    # 位置：在近20日區間的百分位
                    _vix_pos = (_vh_now - _vh_low) / (_vh_high - _vh_low) * 100 if _vh_high > _vh_low else 50

                    _ts_day = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:10]

                    # VIX 多日持續上升（系統性風險積累）
                    if _vix_5d_chg > 15 and _vix_10d_chg > 20:
                        _ck7 = f"{symbol}|{period_label}|VIX多日上升趨勢|{_ts_day}"
                        if _ck7 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck7)
                            if _vix_10d_chg > 40:
                                _v7g = "🚨 系統性風險警報"
                            elif _vix_10d_chg > 25:
                                _v7g = "⚠️ 風險持續累積"
                            else:
                                _v7g = "📊 恐慌升溫"
                            add_alert(symbol, period_label,
                                      f"{_v7g}｜VIX 5日+{_vix_5d_chg:.0f}%、10日+{_vix_10d_chg:.0f}%"
                                      f"（{_vh_10d:.1f}→{_vh_now:.1f}）"
                                      f"，恐慌情緒持續累積，非短期波動！"
                                      f"（VIX在近20日{_vix_pos:.0f}%分位）", "bear")
                            new_signals.append(f"VIX多日升{_vix_10d_chg:.0f}%")

                    # VIX 多日持續下降（系統性風險消退，利多）
                    elif _vix_5d_chg < -15 and _vix_10d_chg < -20:
                        _ck7 = f"{symbol}|{period_label}|VIX多日下降趨勢|{_ts_day}"
                        if _ck7 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck7)
                            add_alert(symbol, period_label,
                                      f"📈 【恐慌持續消退】VIX 5日{_vix_5d_chg:.0f}%、10日{_vix_10d_chg:.0f}%"
                                      f"（{_vh_10d:.1f}→{_vh_now:.1f}）"
                                      f"，市場風險持續下降，有利股市上漲！", "bull")
                            new_signals.append(f"VIX多日降{_vix_10d_chg:.0f}%")

                    # VIX 處於近期高位且未回落（壓頂）
                    if _vix_pos > 80 and _vh_now > 20:
                        _ck7b = f"{symbol}|{period_label}|VIX近期高位壓頂|{_ts_day}"
                        if _ck7b not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck7b)
                            add_alert(symbol, period_label,
                                      f"⚠️ 【VIX近期高位壓頂】VIX={_vh_now:.1f} 處於20日{_vix_pos:.0f}%分位"
                                      f"（近期低{_vh_low:.1f} 高{_vh_high:.1f}）"
                                      f"，恐慌未消退，股市反彈空間受限！", "bear")
                            new_signals.append(f"VIX高位壓頂{_vh_now:.0f}")
            except Exception:
                pass

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # M. ADX 趨勢強度 + Williams %R 超買超賣偵測
    # ══════════════════════════════════════════════════════════════════════════
    try:
        if len(df) >= 20 and "High" in df.columns and "Low" in df.columns:
            _adx, _pdi, _ndi = calc_adx(df, 14)
            _willr = calc_willr(df, 14)

            _adx_v  = float(_adx.iloc[-1])  if not np.isnan(float(_adx.iloc[-1]))  else None
            _pdi_v  = float(_pdi.iloc[-1])  if not np.isnan(float(_pdi.iloc[-1]))  else None
            _ndi_v  = float(_ndi.iloc[-1])  if not np.isnan(float(_ndi.iloc[-1]))  else None
            _wr_v   = float(_willr.iloc[-1]) if not np.isnan(float(_willr.iloc[-1])) else None
            _wr_p   = float(_willr.iloc[-2]) if len(_willr)>=2 and not np.isnan(float(_willr.iloc[-2])) else _wr_v
            _adx_p  = float(_adx.iloc[-2])  if len(_adx)>=2  and not np.isnan(float(_adx.iloc[-2]))  else _adx_v

            _ts = df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:13]

            # ── M1. ADX 空頭趨勢確認（-DI>+DI 且 ADX>25）────────────────────
            if _adx_v and _pdi_v and _ndi_v:
                _bear_trend = _ndi_v > _pdi_v and _adx_v > 25
                _bull_trend = _pdi_v > _ndi_v and _adx_v > 25
                _adx_rising = _adx_v > _adx_p if _adx_p else False

                if _bear_trend:
                    ck = f"{symbol}|{period_label}|ADX空頭趨勢|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        _strength = "強烈" if _adx_v > 35 else "有效" if _adx_v > 25 else "醞釀中"
                        add_alert(symbol, period_label,
                                  f"💀 【ADX空頭趨勢{_strength}】ADX={_adx_v:.1f}"
                                  f"，-DI({_ndi_v:.1f})>+DI({_pdi_v:.1f})空頭主導"
                                  f"{'，ADX上升趨勢加強中！' if _adx_rising else '，ADX持平趨勢穩定。'}", "bear")
                        new_signals.append(f"ADX空頭{_adx_v:.0f}-DI>{_pdi_v:.0f}")

                elif _bull_trend:
                    ck = f"{symbol}|{period_label}|ADX多頭趨勢|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        _strength = "強烈" if _adx_v > 35 else "有效"
                        add_alert(symbol, period_label,
                                  f"🚀 【ADX多頭趨勢{_strength}】ADX={_adx_v:.1f}"
                                  f"，+DI({_pdi_v:.1f})>-DI({_ndi_v:.1f})多頭主導"
                                  f"{'，ADX上升趨勢加強！' if _adx_rising else '。'}", "bull")
                        new_signals.append(f"ADX多頭{_adx_v:.0f}+DI>{_ndi_v:.0f}")

                # ── M2. DI 交叉（方向轉換最早期訊號）────────────────────────
                _pdi_p = float(_pdi.iloc[-2]) if len(_pdi)>=2 else _pdi_v
                _ndi_p = float(_ndi.iloc[-2]) if len(_ndi)>=2 else _ndi_v
                _bull_cross = _pdi_v > _ndi_v and _pdi_p <= _ndi_p   # +DI上穿-DI
                _bear_cross = _ndi_v > _pdi_v and _ndi_p <= _pdi_p   # -DI上穿+DI

                if _bull_cross:
                    ck = f"{symbol}|{period_label}|DI多頭交叉|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📈 【DI多頭交叉】+DI({_pdi_v:.1f}) 上穿 -DI({_ndi_v:.1f})"
                                  f"，方向由空轉多，趨勢反轉訊號！ADX={_adx_v:.1f}", "bull")
                        new_signals.append(f"DI多頭交叉")

                elif _bear_cross:
                    ck = f"{symbol}|{period_label}|DI空頭交叉|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📉 【DI空頭交叉】-DI({_ndi_v:.1f}) 上穿 +DI({_pdi_v:.1f})"
                                  f"，方向由多轉空，趨勢反轉訊號！ADX={_adx_v:.1f}", "bear")
                        new_signals.append(f"DI空頭交叉")

            # ── M3. Williams %R 超買/超賣偵測 ────────────────────────────────
            if _wr_v is not None:
                # 超賣回升穿越-80（底部反彈訊號）
                if _wr_p is not None and _wr_p < -80 and _wr_v >= -80:
                    ck = f"{symbol}|{period_label}|WR超賣回升|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"🟢 【Williams %R超賣回升】WR穿越-80({_wr_v:.1f})"
                                  f"，從超賣區反彈，潛在底部買入機會！", "bull")
                        new_signals.append(f"WR超賣回升{_wr_v:.0f}")

                # 超買回落穿越-20（頂部回落訊號）
                elif _wr_p is not None and _wr_p > -20 and _wr_v <= -20:
                    ck = f"{symbol}|{period_label}|WR超買回落|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"🔴 【Williams %R超買回落】WR穿越-20({_wr_v:.1f})"
                                  f"，從超買區回落，潛在頂部賣出訊號！", "bear")
                        new_signals.append(f"WR超買回落{_wr_v:.0f}")

                # 持續在超賣區（-80以下）且開始回升
                elif _wr_v < -80 and _wr_p is not None and _wr_v > _wr_p:
                    ck = f"{symbol}|{period_label}|WR深度超賣回升|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"💡 【Williams %R深度超賣】WR={_wr_v:.1f}(<-80)"
                                  f" 且開始回升，極度超賣反彈機率高！", "bull")
                        new_signals.append(f"WR深度超賣{_wr_v:.0f}")

                # M4. ADX+WR 組合：趨勢有效 + 未到超賣（圖中當前狀態：ADX=25，WR=-47）
                # 含義：空頭趨勢有效，但WR還在中間，跌勢可能繼續
                if (_adx_v and _ndi_v and _pdi_v
                        and _adx_v > 25 and _ndi_v > _pdi_v    # 有效空頭趨勢
                        and -80 < _wr_v < -20):                  # WR中性（未超賣）
                    ck = f"{symbol}|{period_label}|ADX空趨勢WR中性|{_ts}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"⚠️ 【空頭趨勢仍有空間】ADX={_adx_v:.1f}空頭有效"
                                  f"，WR={_wr_v:.1f} 尚未達超賣區(-80)"
                                  f"，下跌動能未耗盡，暫不宜抄底！", "bear")
                        new_signals.append(f"ADX空頭WR中性{_wr_v:.0f}")

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # N. 三大策略形態偵測
    #    N1. ORB 開盤區間突破（Phase A→B→C→D）
    #    N2. Consolidation 回測支撐再進場（圖1步驟5）
    #    N3. Key Level 強度評分（多次反彈+強烈反應）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        _n_price = float(close.iloc[-1])
        _n_open  = float(df["Open"].iloc[-1])   if "Open"  in df.columns else _n_price
        _n_high  = float(df["High"].iloc[-1])   if "High"  in df.columns else _n_price
        _n_low   = float(df["Low"].iloc[-1])    if "Low"   in df.columns else _n_price
        _n_ts    = df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]

        # ── N1. ORB 開盤區間突破（僅限分鐘級時間週期）──────────────────────
        _is_intraday = any(x in period_label for x in ["1分","5分","15分","30分","1m","5m","15m","30m"])
        if _is_intraday and len(df) >= 10 and "High" in df.columns:
            # 取當日前6根5分鐘K（=開盤30分鐘）計算 ORB
            try:
                _today_idx = df.index[-1].date() if hasattr(df.index[-1], 'date') else None
                if _today_idx:
                    _today_bars = df[df.index.date == _today_idx] if hasattr(df.index, 'date') else df.iloc[-40:]
                    _orb_bars   = _today_bars.iloc[:6]   # 前6根 = 開盤30分鐘（5m週期）
                    if len(_orb_bars) >= 3:
                        _orb_hi = float(_orb_bars["High"].max())
                        _orb_lo = float(_orb_bars["Low"].min())
                        _orb_rng = _orb_hi - _orb_lo

                        # Phase B：當前突破 ORB 高點
                        _orb_breakout_up   = _n_price > _orb_hi * 1.002
                        _orb_breakout_down = _n_price < _orb_lo * 0.998

                        # Phase C：突破後回測守住（在ORB高點上方0-1.5%）
                        # 需要：前幾根已突破，當前根回測但收在 ORB 高點附近
                        _prev_max = float(df["High"].iloc[-6:-1].max()) if len(df) >= 6 else _n_price
                        _prev_min = float(df["Low"].iloc[-6:-1].min())  if len(df) >= 6 else _n_price
                        _prev_broke_hi = _prev_max > _orb_hi * 1.003   # 之前已突破
                        _prev_broke_lo = _prev_min < _orb_lo * 0.997   # 之前已跌破

                        _retest_hi_hold = (_prev_broke_hi and                           # 之前突破過
                                           _n_low <= _orb_hi * 1.008 and               # 當根回測到 ORB 附近
                                           _n_price >= _orb_hi * 0.998 and             # 但收盤守住
                                           _n_price > _n_open)                          # 陽線收

                        _retest_lo_hold = (_prev_broke_lo and
                                           _n_high >= _orb_lo * 0.992 and
                                           _n_price <= _orb_lo * 1.002 and
                                           _n_price < _n_open)

                        if _retest_hi_hold:
                            ck = f"{symbol}|{period_label}|ORB回測支撐|{_n_ts}"
                            if ck not in st.session_state.sent_alerts:
                                st.session_state.sent_alerts.add(ck)
                                # VIX 過濾：抓即時VIX方向
                                try:
                                    _orb_vix = fetch_vix_intraday()
                                    _vix_ok   = _orb_vix.get("signal", 0) >= 0   # VIX不在急升（≥0=中性/下跌）
                                    _vix_note = (f"｜VIX={_orb_vix['spot']:.1f}{'✅下行' if _orb_vix['signal']>0 else '⚠️留意'}"
                                                 if _orb_vix.get("spot") else "")
                                    _conf_boost = 10 if _orb_vix.get("signal", 0) > 0 else 0
                                except Exception:
                                    _vix_ok = True; _vix_note = ""; _conf_boost = 0

                                if _vix_ok:
                                    add_alert(symbol, period_label,
                                              f"🎯 【ORB Phase C 進場信號】突破開盤區間高點{_orb_hi:.2f}"
                                              f"後回測守住，陽線確認支撐"
                                              f"，目標看 Phase D 新高！{_vix_note}"
                                              f"（ORB區間{_orb_lo:.2f}-{_orb_hi:.2f}，寬度{_orb_rng:.2f}）"
                                              f"　止損設於ORB低點{_orb_lo:.2f}以下", "bull")
                                    new_signals.append(f"ORB突破回測買入{_orb_hi:.2f}")
                                    tl_log_decision(symbol, period_label, "N1-ORB",
                                                    triggered=True, signal_type="bull",
                                                    reason=f"Phase C：突破{_orb_hi:.2f}後回測守住，陽線收盤",
                                                    confidence=75 + _conf_boost,
                                                    key_values={"ORB高": _orb_hi, "ORB低": _orb_lo,
                                                                "區間寬度": round(_orb_rng,2), "當前": _n_price})
                                else:
                                    add_alert(symbol, period_label,
                                              f"⚠️ 【ORB信號被VIX過濾】ORB突破條件成立但VIX急升"
                                              f"（VIX={_orb_vix.get('spot','?'):.1f}），暫緩進場觀察", "info")
                                    new_signals.append("ORB被VIX過濾")

                        elif _retest_lo_hold:
                            ck = f"{symbol}|{period_label}|ORB跌破回測|{_n_ts}"
                            if ck not in st.session_state.sent_alerts:
                                st.session_state.sent_alerts.add(ck)
                                add_alert(symbol, period_label,
                                          f"📉 【ORB跌破回測做空】跌破開盤區間低點{_orb_lo:.2f}"
                                          f"後反彈回測但守不住，陰線確認"
                                          f"，看空目標！止損設於ORB高點{_orb_hi:.2f}以上", "bear")
                                new_signals.append(f"ORB跌破回測做空{_orb_lo:.2f}")

            except Exception:
                pass

        # ── N2. Consolidation 突破後回測支撐進場（圖1步驟5）──────────────────
        # 邏輯：G7 檢測到盤整突破（多根前），現在回測到突破點附近，守住→進場
        if len(close) >= 20:
            _n2_window = 25
            _n2_c  = close.iloc[-_n2_window:]
            _n2_hi = float(_n2_c.max())           # 盤整突破後的最高點
            _n2_range_hi = float(close.iloc[-_n2_window:-8].max())  # 排除最近8根（突破後的上漲段）

            # 當前在突破點附近（距突破頂±0.5%）
            _n2_near_breakout  = abs(_n_price - _n2_range_hi) / _n2_range_hi < 0.005
            # 之前有過突破（5根前的最高點 > 更之前的盤整頂）
            _n2_broke = _n2_hi > _n2_range_hi * 1.008
            # 當前陽線（守住支撐）
            _n2_bull_bar = _n_price > _n_open and _n_price >= _n2_range_hi * 0.998

            # 量能縮小（回測時量小是好事）
            _n2_vol_now  = float(vol.iloc[-1])
            _n2_vol_prev = float(vol.iloc[-6:-1].mean()) if len(vol) >= 6 else _n2_vol_now
            _n2_low_vol  = _n2_vol_now < _n2_vol_prev * 0.7  # 回測量縮

            if _n2_broke and _n2_near_breakout and _n2_bull_bar:
                ck = f"{symbol}|{period_label}|整理突破回測|{_n_ts}"
                if ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(ck)
                    vol_note = "（縮量回測更佳✅）" if _n2_low_vol else ""
                    add_alert(symbol, period_label,
                              f"🎯 【整理突破回測買點】價格突破盤整頂{_n2_range_hi:.2f}後"
                              f"回測守住{vol_note}"
                              f"，陽線確認支撐，圖1策略步驟5進場！"
                              f"　止損設於{_n2_range_hi * 0.995:.2f}以下", "bull")
                    new_signals.append(f"整理突破回測{_n2_range_hi:.2f}")
                    tl_log_decision(symbol, period_label, "N2-Consolidation",
                                    triggered=True, signal_type="bull",
                                    reason=f"突破{_n2_range_hi:.2f}後回測守住，{'縮量' if _n2_low_vol else '量正常'}",
                                    confidence=70 + (10 if _n2_low_vol else 0),
                                    key_values={"突破頂": _n2_range_hi, "當前": _n_price,
                                                "距突破頂": f"{(_n_price-_n2_range_hi)/_n2_range_hi*100:+.2f}%",
                                                "縮量": _n2_low_vol})

        # ── N3. Key Level 強度評分（圖3：多次反彈+強烈反應）──────────────────
        if len(close) >= 30 and "High" in df.columns:
            _n3_lookback = min(60, len(close))
            _n3_c  = close.iloc[-_n3_lookback:]
            _n3_hi = df["High"].iloc[-_n3_lookback:]
            _n3_lo = df["Low"].iloc[-_n3_lookback:]

            # 自動找關鍵水平（用近60根的最高頻率價格區間）
            _n3_vals  = _n3_c.values
            _n3_all   = np.concatenate([_n3_vals, _n3_hi.values, _n3_lo.values])
            _n3_p10   = np.percentile(_n3_all, 10)   # 支撐帶低
            _n3_p90   = np.percentile(_n3_all, 90)   # 阻力帶高

            # 對每個候選水平評分（每次測試的反應幅度）
            def _key_level_score(level_price, tolerance=0.005):
                touches = 0; strong_reactions = 0
                n3_len = len(_n3_vals)
                for i in range(n3_len):
                    lo_i = float(_n3_lo.iloc[i]); hi_i = float(_n3_hi.iloc[i])
                    cl_i = float(_n3_c.iloc[i])
                    # 觸及此水平（低點或高點在容忍範圍內）
                    if abs(lo_i - level_price)/level_price < tolerance or \
                       abs(hi_i - level_price)/level_price < tolerance:
                        touches += 1
                        # 強烈反應：觸及後下一根的價格變動超過0.3%（圖3：Strong Reaction）
                        if i + 1 < n3_len:
                            next_cl  = float(_n3_c.iloc[i+1])
                            reaction = abs(next_cl - cl_i) / level_price * 100
                            if reaction > 0.3: strong_reactions += 1
                        # 或當根K線本身寬度超過0.6%（長影線強烈反應）
                        elif (hi_i - lo_i) / level_price * 100 > 0.6:
                            strong_reactions += 1
                return touches, strong_reactions

            # 當前價格附近±2%的支撐/阻力評分
            for _lv_offset in [-0.008, -0.004, 0, 0.004, 0.008]:
                _lv = _n_price * (1 + _lv_offset)
                _lv_touches, _lv_strong = _key_level_score(_lv)

                # 圖3標準：≥3次觸及 + ≥2次強烈反應
                if _lv_touches >= 3 and _lv_strong >= 2:
                    _lv_type  = "支撐" if _lv < _n_price else "阻力" if _lv > _n_price else "當前關鍵位"
                    _lv_grade = "🔑🔑 極強" if _lv_touches >= 5 else "🔑 強"
                    ck = f"{symbol}|{period_label}|關鍵水平{_lv:.2f}|{_n_ts[:10]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"{_lv_grade}關鍵{_lv_type}位 {_lv:.2f}"
                                  f"（{_lv_touches}次測試，{_lv_strong}次強烈反應）"
                                  f"，符合圖3 Key Level 3項標準！"
                                  f"　當前距此水平{(_n_price-_lv)/_lv*100:+.2f}%",
                                  "bull" if _lv < _n_price else "bear")
                        new_signals.append(f"關鍵{_lv_type}位{_lv:.2f}×{_lv_touches}")
                        tl_log_decision(symbol, period_label, "N3-KeyLevel",
                                        triggered=True,
                                        signal_type="bull" if _lv < _n_price else "bear",
                                        reason=f"{_lv_type}位{_lv:.2f}：{_lv_touches}次觸及，{_lv_strong}次強烈反應",
                                        confidence=min(50 + _lv_touches*8 + _lv_strong*5, 90),
                                        key_values={"水平": round(_lv,2), "觸及次數": _lv_touches,
                                                    "強烈反應": _lv_strong, "類型": _lv_type})
                    break  # 只報最強的一個水平

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # O. 多時間框架趨勢共振 + 下跌目標位預測
    #    O1. MTF 多框架趨勢共振（日K+週K+月K同向 → 超強信號）
    #    O2. 歷史回撤中位數預測目標支撐位
    #    O3. 週K/月K 大週期空頭底背離預警（反轉準備信號）
    # ══════════════════════════════════════════════════════════════════════════
    try:
        import yfinance as _yf_o
        _o_price  = float(close.iloc[-1])
        _o_ts_day = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]

        # ── O1. MTF 多時間框架趨勢共振 ────────────────────────────────────────
        # 拉取日K、週K、月K，判斷各自 EMA5/20 的多空方向
        @st.cache_data(ttl=300)
        def _fetch_mtf_trend(sym):
            result = {}
            for iv, rng, label in [("1d","3mo","日K"), ("1wk","1y","週K"), ("1mo","5y","月K")]:
                try:
                    _df = _yf_o.download(sym, period=rng, interval=iv,
                                         auto_adjust=True, progress=False)
                    if _df.empty or len(_df) < 10: continue
                    _df.columns = [c[0] if isinstance(c,tuple) else c for c in _df.columns]
                    _c = _df["Close"].dropna()
                    _e5  = float(_c.ewm(span=5,  adjust=False).mean().iloc[-1])
                    _e20 = float(_c.ewm(span=20, adjust=False).mean().iloc[-1])
                    _e60 = float(_c.ewm(span=60, adjust=False).mean().iloc[-1]) if len(_c)>=60 else None
                    _price_last = float(_c.iloc[-1])
                    # 趨勢：bull=EMA5>EMA20，bear=EMA5<EMA20
                    direction = "bull" if _e5 > _e20 else "bear"
                    # 相對EMA60位置（加分項）
                    above_e60 = (_e5 > _e60) if _e60 else None
                    result[label] = {
                        "direction": direction,
                        "e5": _e5, "e20": _e20,
                        "price": _price_last,
                        "above_e60": above_e60,
                        "pct_from_e20": (_price_last - _e20) / _e20 * 100,
                    }
                except Exception:
                    pass
            return result

        _mtf = _fetch_mtf_trend(symbol)

        if len(_mtf) >= 2:
            _bull_count = sum(1 for v in _mtf.values() if v["direction"] == "bull")
            _bear_count = sum(1 for v in _mtf.values() if v["direction"] == "bear")
            _frames_bear = [k for k,v in _mtf.items() if v["direction"] == "bear"]
            _frames_bull = [k for k,v in _mtf.items() if v["direction"] == "bull"]

            # 多框架全空頭共振（圖中週K空頭場景）
            if _bear_count >= 2:
                _o1_ck = f"{symbol}|{period_label}|MTF空頭共振|{_o_ts_day}"
                if _o1_ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(_o1_ck)
                    _frame_detail = "　".join([
                        f"{k}({'空' if v['direction']=='bear' else '多'}·距EMA20={v['pct_from_e20']:+.1f}%)"
                        for k,v in _mtf.items()
                    ])
                    if _bear_count == 3:
                        _o1_grade = "🚨 三框架全空頭"
                        _o1_conf  = 90
                    else:
                        _o1_grade = "⚠️ 雙框架空頭共振"
                        _o1_conf  = 72
                    add_alert(symbol, period_label,
                              f"{_o1_grade}｜{'+'.join(_frames_bear)}同時看空"
                              f"（{_frame_detail}）"
                              f"，多時間框架趨勢一致，下行動能最強！", "bear")
                    new_signals.append(f"MTF{_bear_count}框架空頭共振")
                    tl_log_decision(symbol, period_label, "O1-MTF",
                                    triggered=True, signal_type="bear",
                                    reason=f"{'+'.join(_frames_bear)}框架EMA5<EMA20空頭共振",
                                    confidence=_o1_conf,
                                    key_values={k: v["direction"] for k,v in _mtf.items()})

            # 多框架全多頭共振
            elif _bull_count >= 2:
                _o1b_ck = f"{symbol}|{period_label}|MTF多頭共振|{_o_ts_day}"
                if _o1b_ck not in st.session_state.sent_alerts:
                    st.session_state.sent_alerts.add(_o1b_ck)
                    _o1b_grade = "🚀🚀 三框架全多頭" if _bull_count == 3 else "🚀 雙框架多頭共振"
                    add_alert(symbol, period_label,
                              f"{_o1b_grade}｜{'+'.join(_frames_bull)}同時看多"
                              f"，多時間框架趨勢共振，上行動能最強！", "bull")
                    new_signals.append(f"MTF{_bull_count}框架多頭共振")

        # ── O2. 歷史回撤分析 + 下跌目標位預測 ──────────────────────────────────
        # 從近期高點計算合理的回撤目標（基於歷史回撤中位數）
        if len(close) >= 30 and "High" in df.columns:
            _o2_high = float(df["High"].iloc[-60:].max()) if len(df)>=60 else float(df["High"].max())
            _o2_cur  = _o_price
            _o2_from_top = (_o2_cur - _o2_high) / _o2_high * 100  # 已跌幅度

            # 只在已從高點回落5%以上時計算目標
            if _o2_from_top < -5:
                # 用 ATR 估算波動率
                if "Low" in df.columns:
                    _atr_n = min(14, len(df)-1)
                    _hi_s  = df["High"].iloc[-_atr_n:]
                    _lo_s  = df["Low"].iloc[-_atr_n:]
                    _cl_s  = close.iloc[-_atr_n-1:-1]
                    _tr    = [max(float(_hi_s.iloc[i])-float(_lo_s.iloc[i]),
                                  abs(float(_hi_s.iloc[i])-float(_cl_s.iloc[i])),
                                  abs(float(_lo_s.iloc[i])-float(_cl_s.iloc[i])))
                              for i in range(min(_atr_n, len(_hi_s), len(_lo_s), len(_cl_s)))]
                    _atr   = sum(_tr) / len(_tr) if _tr else _o2_cur * 0.01

                    # 目標位：黃金回撤（38.2%/50%/61.8%）從高點計算
                    _fib_targets = {
                        "38.2%回撤": _o2_high * (1 - 0.382 * abs(_o2_from_top/100) * (100/abs(_o2_from_top))),
                        "50%回撤":   _o2_high * 0.50 if _o2_from_top < -30 else _o2_cur - _atr * 3,
                        "ATR×3目標": _o2_cur - _atr * 3,
                    }

                    # 使用 EMA200 作為最強支撐目標
                    if len(close) >= 200:
                        _e200_target = float(calc_ema(close, 200).iloc[-1])
                        _fib_targets["EMA200支撐"] = _e200_target

                    _o2_ck = f"{symbol}|{period_label}|回撤目標分析|{_o_ts_day}"
                    if _o2_ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_o2_ck)
                        _tgt_str = "　".join([
                            f"{k}={v:.2f}（距今{(v-_o2_cur)/_o2_cur*100:+.1f}%）"
                            for k,v in _fib_targets.items()
                            if v < _o2_cur  # 只顯示在當前價格以下的目標
                        ])
                        if _tgt_str:
                            add_alert(symbol, period_label,
                                      f"📐 【回撤目標位分析】已從高點{_o2_high:.2f}下跌{_o2_from_top:.1f}%"
                                      f"，技術目標支撐：{_tgt_str}"
                                      f"　（ATR={_atr:.2f}，波動基準）", "bear")
                            new_signals.append(f"回撤目標高點{_o2_high:.0f}已跌{_o2_from_top:.0f}%")

        # ── O3. 週K/月K 大週期底背離預警（空頭末期反轉準備信號）─────────────
        # 當日K已出現底背離（I1觸發），且週K RSI偏低 → 大週期反轉前兆
        @st.cache_data(ttl=600)
        def _fetch_weekly_rsi(sym):
            try:
                _df = _yf_o.download(sym, period="2y", interval="1wk",
                                     auto_adjust=True, progress=False)
                if _df.empty or len(_df) < 20: return None, None
                _df.columns = [c[0] if isinstance(c,tuple) else c for c in _df.columns]
                _c = _df["Close"].dropna()
                delta = _c.diff()
                gain  = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
                loss  = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
                rs    = gain / loss
                rsi   = 100 - 100/(1+rs)
                return float(rsi.iloc[-1]), float(rsi.iloc[-2])
            except Exception:
                return None, None

        _w_rsi, _w_rsi_prev = _fetch_weekly_rsi(symbol)

        if _w_rsi is not None:
            _o3_ck = f"{symbol}|{period_label}|週K底背離預警|{_o_ts_day}"
            # 週K RSI<40 且日K已有底背離信號（新信號列表中）
            _has_daily_diverg = any("底背離" in s or "MACD深谷" in s for s in new_signals)
            if _w_rsi < 40 and _o3_ck not in st.session_state.sent_alerts:
                st.session_state.sent_alerts.add(_o3_ck)
                _rsi_trend = "↑回升" if _w_rsi > _w_rsi_prev else "↓仍下行"
                if _w_rsi < 30:
                    _o3_grade = "🔔 週K超賣區"
                    _o3_note  = "歷史上週K RSI<30 往往是大週期底部！"
                elif _w_rsi < 35:
                    _o3_grade = "📊 週K深度偏空"
                    _o3_note  = "接近週K超賣，留意底部信號"
                else:
                    _o3_grade = "📊 週K偏空"
                    _o3_note  = "週K趨勢仍偏空"

                add_alert(symbol, period_label,
                          f"{_o3_grade}｜週K RSI={_w_rsi:.1f}{_rsi_trend}"
                          f"，{_o3_note}"
                          f"{'　⚡日K已出現底背離，多框架共振底部！' if _has_daily_diverg else ''}"
                          f"　（配合日K信號確認後再布局，勿搶底）",
                          "bull" if _has_daily_diverg and _w_rsi < 35 else "info")
                new_signals.append(f"週KRSI{_w_rsi:.0f}{'底部共振' if _has_daily_diverg else '偏空'}")
                tl_log_decision(symbol, period_label, "O3-WeeklyRSI",
                                triggered=True,
                                signal_type="bull" if _has_daily_diverg and _w_rsi < 35 else "info",
                                reason=f"週K RSI={_w_rsi:.1f}({'超賣' if _w_rsi<30 else '偏空'})"
                                       f"{'，日K底背離共振' if _has_daily_diverg else ''}",
                                confidence=55 + (20 if _has_daily_diverg else 0) + (15 if _w_rsi<30 else 0),
                                key_values={"週K RSI": round(_w_rsi,1), "前週RSI": round(_w_rsi_prev,1),
                                            "趨勢": _rsi_trend, "日K底背離": _has_daily_diverg})

    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════════
    # P. 回測驗證信號（5年1256筆TSLA日K，僅WR≥55%且n≥20入列）
    #    P1. VIX恐慌區反彈買入    WR=55.8% n=77  (VIX 18-35 + 當日漲幅 5-15%)
    #    P2. VIX暴漲極端反向買入  WR=64.0% n=25  (VIX 當日漲>10%)
    #    P3. 射擊之星觀察          WR=51.9% n=77  (5年無效→降為info觀察)
    #    P4. 十字星多頭            WR=58.2% n=55  (5年確認有效)
    #    P5. 連漲5-9天換向視窗    WR=59-80% n=77-5 (10年確認，第9-10天過熱最強)
    #    P6. 突破跳空量能強化版    WR=100%  n=38  (5年完美紀錄)
    # ══════════════════════════════════════════════════════════════════════════
    try:
        if len(df) >= 10 and not close.empty:
            _p_ts  = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:10]
            _p_tsh = df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:13]
            _p_c   = float(close.iloc[-1])
            _p_o   = float(opn.iloc[-1])
            _p_h   = float(high.iloc[-1])
            _p_l   = float(low.iloc[-1])
            _p_c1  = float(close.iloc[-2]) if len(close) >= 2 else _p_c
            _p_h1  = float(high.iloc[-2])  if len(high)  >= 2 else _p_h
            _p_l1  = float(low.iloc[-2])   if len(low)   >= 2 else _p_l
            _p_rng = _p_h - _p_l if _p_h > _p_l else 0.001
            _p_body = abs(_p_c - _p_o)
            _p_uvs = _p_h - max(_p_c, _p_o)   # 上引線
            _p_lvs = min(_p_c, _p_o) - _p_l   # 下引線
            # 均量（10日）
            _p_vol_ma = float(vol.rolling(10).mean().iloc[-1]) if len(vol) >= 10 else float(vol.mean())
            _p_vol_r  = float(vol.iloc[-1]) / _p_vol_ma if _p_vol_ma > 0 else 1.0

            # ── P1. VIX恐慌區反彈買入（VIX 18-35，回測WR=55.8%）─────────────
            try:
                _vix_p1 = fetch_vix_history()
                if len(_vix_p1) >= 2:
                    _vix_now  = float(_vix_p1.iloc[-1])
                    _vix_prev = float(_vix_p1.iloc[-2])
                    _vix_chg  = (_vix_now - _vix_prev) / _vix_prev * 100 if _vix_prev > 0 else 0
                    _p1_zone  = 18 <= _vix_now <= 35
                    _p1_rise  = 5 <= _vix_chg <= 15  # 溫和上升（非暴升），恐慌升溫但未崩潰
                    if _p1_zone and _p1_rise:
                        ck_p1 = f"{symbol}|{period_label}|P1-VIX恐慌區反彈|{_p_ts}"
                        if ck_p1 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(ck_p1)
                            add_alert(symbol, period_label,
                                      f"📈 【P1·VIX恐慌區反彈】VIX={_vix_now:.1f}（18-35恐慌區）"
                                      f"當日+{_vix_chg:.1f}%｜回測隔日收高率55.8%"
                                      f"，恐慌升溫但未崩潰，反彈機率偏高", "bull")
                            new_signals.append(f"P1-VIX恐慌區反彈{_vix_now:.0f}")
            except Exception:
                pass

            # ── P2. VIX暴漲極端反向買入（VIX當日漲>10%，回測WR=64%）─────────
            try:
                _vix_p2 = fetch_vix_history()
                if len(_vix_p2) >= 2:
                    _vix2_now  = float(_vix_p2.iloc[-1])
                    _vix2_prev = float(_vix_p2.iloc[-2])
                    _vix2_chg  = (_vix2_now - _vix2_prev) / _vix2_prev * 100 if _vix2_prev > 0 else 0
                    if _vix2_chg > 10:
                        ck_p2 = f"{symbol}|{period_label}|P2-VIX暴漲反向|{_p_ts}"
                        if ck_p2 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(ck_p2)
                            _p2_grade = "🚀🚀" if _vix2_chg > 20 else "🚀"
                            add_alert(symbol, period_label,
                                      f"{_p2_grade} 【P2·VIX暴漲反向買入】VIX單日+{_vix2_chg:.1f}%"
                                      f"（{_vix2_prev:.1f}→{_vix2_now:.1f}）"
                                      f"｜回測隔日收高率64%（n=25）"
                                      f"，極端恐慌往往是短期底部，逆勢反彈機率最高", "bull")
                            new_signals.append(f"P2-VIX暴漲{_vix2_chg:.0f}%反向買入")
            except Exception:
                pass

            # ── P3. 射擊之星（5年WR=51.9%→降為觀察信號，需多重條件才升bear）────
            # 1年回測WR=72.7%（n=11），5年回測WR=51.9%（n=77），信號不穩定
            # 降為info警示；若配合衰竭跳空(上)同時出現則升為bear
            if _p_rng > 0:
                _p3_uvs_ratio = _p_uvs / _p_rng   # 上引線佔全幅比例
                _p3_body_ratio = _p_body / _p_rng  # 實體佔全幅比例
                _p3_shooting = (
                    _p3_uvs_ratio >= 0.45      # 上引線超過全幅45%
                    and _p3_body_ratio <= 0.35  # 實體不超過35%
                    and _p_uvs >= _p_body * 1.8 # 上引線≥實體1.8倍
                    and _p_h > _p_h1            # 當日最高突破前高（更典型）
                )
                if _p3_shooting:
                    ck_p3 = f"{symbol}|{period_label}|P3-射擊之星|{_p_tsh}"
                    if ck_p3 not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p3)
                        _p3_vol = "放量" if _p_vol_r >= 1.3 else "縮量"
                        _p3_bear_bar = _p_c < _p_o
                        # 5年數據：單純射擊之星WR僅51.9%，需額外確認
                        # 加強條件：陰線+放量 → 稍強但仍需謹慎（5年n=15，WR=33%更差）
                        _atype = "info"
                        _note = "5年回測WR=51.9%（n=77），單獨信號可靠度低，需搭配其他空頭確認"
                        add_alert(symbol, period_label,
                                  f"⚠️ 【P3·射擊之星觀察】上引線{_p_uvs:.2f}（{_p3_uvs_ratio*100:.0f}%）"
                                  f"／實體{_p3_body_ratio*100:.0f}%"
                                  f"，{_p3_vol}×{_p_vol_r:.1f}，{'陰線' if _p3_bear_bar else '陽線'}"
                                  f"｜{_note}", _atype)
                        new_signals.append("P3-射擊之星觀察")

            # ── P4. 十字星多頭（開收接近，回測隔日收高率60%）──────────────────
            # 定義：實體極小（≤全幅8%），上下引線均有，不在明顯上升趨勢頂部
            if _p_rng > 0:
                _p4_body_ratio = _p_body / _p_rng
                _p4_doji = (
                    _p4_body_ratio <= 0.08      # 實體佔全幅≤8%（極小實體）
                    and _p_uvs > _p_body * 0.8  # 有一定上引線
                    and _p_lvs > _p_body * 0.8  # 有一定下引線
                    and _p_rng > _p_c * 0.003   # 排除極小波動的平坦K線
                )
                _p4_not_top = not (_p_h > _p_h1 * 1.005 and float(close.iloc[-3]) < _p_c1 if len(close) >= 3 else False)
                if _p4_doji and _p4_not_top:
                    ck_p4 = f"{symbol}|{period_label}|P4-十字星多頭|{_p_tsh}"
                    if ck_p4 not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p4)
                        add_alert(symbol, period_label,
                                  f"✚ 【P4·十字星】實體{_p4_body_ratio*100:.1f}%"
                                  f"（開{_p_o:.2f} 收{_p_c:.2f}）"
                                  f"，市場方向猶豫｜回測隔日收高率60%（n=10）"
                                  f"，多空均衡後偏向多方，需配合其他買入信號確認", "info")
                        new_signals.append("P4-十字星多頭60%")

            # ── P5. 連漲換向視窗（10年實證）──────────────────────────────────
            # 10年數據（2515筆）：
            #   連漲5天→59.7%，連漲6天→58.7%，連漲9天→62.5%，連漲10天→80%⭐⭐
            #   連跌6天→36.4%❌，連跌7天→33.3%❌（繼續跌，非反彈）
            if len(df) >= 12:
                _p5_up_cnt = 0
                _p5_dn_cnt = 0
                for _bi in range(1, 13):
                    if len(close) <= _bi: break
                    _diff = float(close.iloc[-_bi]) - float(close.iloc[-_bi-1])
                    if _diff > 0:
                        if _p5_dn_cnt > 0: break
                        _p5_up_cnt += 1
                    elif _diff < 0:
                        if _p5_up_cnt > 0: break
                        _p5_dn_cnt += 1
                    else:
                        break

                # 連漲5-8天：出場觀察視窗（WR 58-67%）
                if 5 <= _p5_up_cnt <= 8:
                    ck_p5 = f"{symbol}|{period_label}|P5-連漲換向|{_p_ts}"
                    if ck_p5 not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p5)
                        _p5_chg = (_p_c - float(close.iloc[-_p5_up_cnt-1])) / float(close.iloc[-_p5_up_cnt-1]) * 100 if float(close.iloc[-_p5_up_cnt-1]) > 0 else 0
                        _p5_wr = {5:"59.7", 6:"58.7", 7:"48.1", 8:"61.5"}.get(_p5_up_cnt, "58+")
                        try:
                            _p5_rsi = float(calc_rsi(close, 14).iloc[-1])
                            _rsi_tag = f"，RSI={_p5_rsi:.0f}{'🔴超買' if _p5_rsi>=70 else ''}"
                        except Exception:
                            _rsi_tag = ""
                        add_alert(symbol, period_label,
                                  f"⚠️ 【P5·連漲{_p5_up_cnt}天換向視窗】累漲{_p5_chg:+.1f}%{_rsi_tag}"
                                  f"｜10年回測同向率={_p5_wr}%，高位換向壓力增加"
                                  f"，注意縮倉或設置移動止損", "info")
                        new_signals.append(f"P5-連漲{_p5_up_cnt}天換向視窗")

                # 連漲9-10天：過熱極端信號（WR=62-80%，強烈換向警告）
                elif _p5_up_cnt >= 9:
                    ck_p5b = f"{symbol}|{period_label}|P5-連漲過熱|{_p_ts}"
                    if ck_p5b not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p5b)
                        _p5_chg = (_p_c - float(close.iloc[-_p5_up_cnt-1])) / float(close.iloc[-_p5_up_cnt-1]) * 100 if float(close.iloc[-_p5_up_cnt-1]) > 0 else 0
                        _p5_wr10 = "80" if _p5_up_cnt >= 10 else "62.5"
                        add_alert(symbol, period_label,
                                  f"🚨 【P5·連漲{_p5_up_cnt}天極度過熱】累漲{_p5_chg:+.1f}%"
                                  f"｜10年回測第{_p5_up_cnt}天同向率高達{_p5_wr10}%"
                                  f"（動能極端，通常是最後衝刺）"
                                  f"，強烈建議高位減倉，防止急速反轉！", "bear")
                        new_signals.append(f"P5-連漲{_p5_up_cnt}天極度過熱")

                # 連跌6-7天：10年數據顯示繼續下跌（非反彈！）
                elif _p5_dn_cnt >= 6:
                    ck_p5c = f"{symbol}|{period_label}|P5-連跌警示|{_p_ts}"
                    if ck_p5c not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p5c)
                        _p5_chg = (_p_c - float(close.iloc[-_p5_dn_cnt-1])) / float(close.iloc[-_p5_dn_cnt-1]) * 100 if float(close.iloc[-_p5_dn_cnt-1]) > 0 else 0
                        _p5_wr_dn = {6:"36.4", 7:"33.3"}.get(_p5_dn_cnt, "35")
                        add_alert(symbol, period_label,
                                  f"🚨 【P5·連跌{_p5_dn_cnt}天空頭延續】累跌{_p5_chg:+.1f}%"
                                  f"｜10年回測連跌{_p5_dn_cnt}天後隔日收高率僅{_p5_wr_dn}%"
                                  f"，空頭趨勢持續，勿接刀！等待止跌信號", "bear")
                        new_signals.append(f"P5-連跌{_p5_dn_cnt}天空頭延續")

            # ── P6. 突破跳空量能強化版（跳空上漲+量≥1.5x，回測WR=100%）─────
            if len(df) >= 3:
                _p6_gap   = float(opn.iloc[-1]) - float(high.iloc[-2])
                _p6_gapc  = _p6_gap / float(close.iloc[-2]) * 100 if float(close.iloc[-2]) > 0 else 0
                _p6_is_gap_up  = _p6_gap > 0 and _p6_gapc >= 0.3
                _p6_vol_strong = _p_vol_r >= 1.5
                _p6_bull_bar   = _p_c > _p_o
                _p6_above_vwap = _p_c > float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else True
                if _p6_is_gap_up and _p6_vol_strong and _p6_bull_bar:
                    ck_p6 = f"{symbol}|{period_label}|P6-跳空量能強化|{_p_tsh}"
                    if ck_p6 not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck_p6)
                        _p6_tags = [f"缺口+{_p6_gapc:.2f}%", f"量×{_p_vol_r:.1f}"]
                        if _p6_above_vwap: _p6_tags.append("收于均線上方")
                        if _p_vol_r >= 2.0: _p6_tags.append("⚡超強放量")
                        add_alert(symbol, period_label,
                                  f"🚀 【P6·突破跳空量能強化】{'+'.join(_p6_tags)}"
                                  f"，陽線確認｜回測同類型隔日收高率100%（n=15）"
                                  f"，量價雙確認為最強買入形態，優先執行", "bull")
                        new_signals.append(f"P6-跳空量能強化+{_p6_gapc:.1f}%×{_p_vol_r:.1f}")
                        _p6_atr = float((high - low).tail(14).mean())
                        generate_trade_suggestion(symbol, period_label,
                                                  f"P6-跳空量能強化+{_p6_gapc:.1f}%×{_p_vol_r:.1f}",
                                                  "bull", float(close.iloc[-1]), _p6_atr)

        # ════════════════════════════════════════════════════════════════════
        # Q 節：圖表結構偵測器（Volume Profile / DTR / VIX百分位）
        # ════════════════════════════════════════════════════════════════════

        # ── Q3. DTR/ATR 波幅使用率警戒（今日波幅耗盡，追單風險極高）────────
        # 來源：圖中 DTR=6.15 / ATR=6.24 / Pct=98.5% → CAUTION
        # 邏輯：當日高低差（DTR）接近14日均值（ATR）→ 當日動能耗盡，不宜追單
        try:
            if len(df) >= 15:
                _q3_dtr = float(high.iloc[-1]) - float(low.iloc[-1])
                _q3_atr = float((high - low).rolling(14).mean().iloc[-1])
                _q3_pct = (_q3_dtr / _q3_atr * 100) if _q3_atr > 0 else 0

                _q3_ck = f"{symbol}|{period_label}|Q3-DTR警戒|{_bar_date(df.index[-1])}"
                if _q3_ck not in st.session_state.sent_alerts:
                    if _q3_pct >= 110:
                        # 超出常態：波動超過ATR，反轉風險極高
                        st.session_state.sent_alerts.add(_q3_ck)
                        add_alert(symbol, period_label,
                                  f"🚨 【Q3·DTR/ATR={_q3_pct:.0f}%】今日波幅${_q3_dtr:.2f}"
                                  f" 超出14日均值${_q3_atr:.2f}（{_q3_pct:.0f}%）"
                                  f"｜波動嚴重超出常態，反轉風險極高，嚴禁追單！", "bear")
                        new_signals.append(f"Q3-DTR/ATR={_q3_pct:.0f}%過熱")
                    elif _q3_pct >= 95:
                        # CAUTION區：今日動能幾乎耗盡
                        st.session_state.sent_alerts.add(_q3_ck)
                        add_alert(symbol, period_label,
                                  f"⚠️ 【Q3·DTR/ATR警戒={_q3_pct:.0f}%】今日波幅"
                                  f"${_q3_dtr:.2f}已達ATR${_q3_atr:.2f}的{_q3_pct:.0f}%"
                                  f"｜CAUTION：今日動能近耗盡，追單風險高，等待次日重置", "info")
                        new_signals.append(f"Q3-DTR/ATR={_q3_pct:.0f}%CAUTION")
        except Exception:
            pass

        # ── Q2. VIX 歷史百分位偵測（升級L5，加入相對歷史位置）───────────────
        # 邏輯：VIX絕對值不夠，需要知道當前VIX在過去1年的歷史百分位
        #       百分位>=90% → 極端恐慌，逆向買入信號加強
        #       百分位<=10% → 極度樂觀，下跌風險被低估
        try:
            _q2_vix_hist = fetch_vix_history()
            if len(_q2_vix_hist) >= 20:
                # 抓1年數據計算百分位（如果有的話）
                _q2_vix_1y = None
                try:
                    _q2_df1y = yf.download("^VIX", period="1y", interval="1d",
                                           auto_adjust=True, progress=False, multi_level_col=False)
                    if not _q2_df1y.empty:
                        _q2_vix_1y = _q2_df1y["Close"].dropna()
                except Exception:
                    pass

                _q2_series = _q2_vix_1y if (_q2_vix_1y is not None and len(_q2_vix_1y) >= 50) else _q2_vix_hist
                _q2_now    = float(_q2_series.iloc[-1])
                _q2_pctile = float((_q2_series <= _q2_now).sum() / len(_q2_series) * 100)
                _q2_mean   = float(_q2_series.mean())
                _q2_std    = float(_q2_series.std())
                _q2_n      = len(_q2_series)

                _q2_ts  = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:10]
                _q2_ck  = f"{symbol}|{period_label}|Q2-VIX百分位|{_q2_ts}"

                if _q2_ck not in st.session_state.sent_alerts:
                    if _q2_pctile >= 90:
                        # 極端恐慌 → 歷史上此百分位後1個月平均上漲
                        st.session_state.sent_alerts.add(_q2_ck)
                        add_alert(symbol, period_label,
                                  f"🚀 【Q2·VIX極端恐慌百分位{_q2_pctile:.0f}%】VIX={_q2_now:.1f}"
                                  f"（{_q2_n}日均值{_q2_mean:.1f}±{_q2_std:.1f}）"
                                  f"｜歷史前10%極端恐慌水平，逆向買入信號強化！"
                                  f"（需配合技術面確認底部）", "bull")
                        new_signals.append(f"Q2-VIX極端恐慌{_q2_pctile:.0f}%ile")
                        generate_trade_suggestion(symbol, period_label,
                                                  f"Q2-VIX極端恐慌百分位{_q2_pctile:.0f}%",
                                                  "bull", float(close.iloc[-1]),
                                                  float((high - low).rolling(14).mean().iloc[-1]))
                    elif _q2_pctile >= 75:
                        st.session_state.sent_alerts.add(_q2_ck)
                        add_alert(symbol, period_label,
                                  f"⚠️ 【Q2·VIX高位百分位{_q2_pctile:.0f}%】VIX={_q2_now:.1f}"
                                  f"（高於{_q2_n}日中{_q2_pctile:.0f}%的交易日）"
                                  f"｜市場恐慌偏高，注意支撐位，勿重倉追空", "info")
                        new_signals.append(f"Q2-VIX高位{_q2_pctile:.0f}%ile")
                    elif _q2_pctile <= 10:
                        # 極度樂觀 → 警惕黑天鵝
                        st.session_state.sent_alerts.add(_q2_ck)
                        add_alert(symbol, period_label,
                                  f"🚨 【Q2·VIX極低百分位{_q2_pctile:.0f}%】VIX={_q2_now:.1f}"
                                  f"（低於{_q2_n}日中{100-_q2_pctile:.0f}%的交易日）"
                                  f"｜市場極度自滿，尾部風險被低估，黑天鵝警戒！", "bear")
                        new_signals.append(f"Q2-VIX極低自滿{_q2_pctile:.0f}%ile")
        except Exception:
            pass

        # ── Q1. 成交量真空帶偵測（Volume Gap — 快速穿越風險/機會）────────────
        # 邏輯：用近N日K線建立「成交量密度Map」，找出低密度空洞區間
        # 若當前價格剛進入低密度區 → 缺乏支撐，可能加速
        # 真空帶底部有大成交量帶 → 強支撐
        try:
            if len(df) >= 60:
                _q1_price_now  = float(close.iloc[-1])
                _q1_price_prev = float(close.iloc[-2])

                # 建立 price-volume histogram（60日）
                _q1_h = high.iloc[-60:].values
                _q1_l = low.iloc[-60:].values
                _q1_v = vol.iloc[-60:].values

                # 每根K線的成交量分配到其高低範圍的價格格（步長=ATR/5）
                _q1_atr  = float((high - low).rolling(14).mean().iloc[-1])
                _q1_step = max(_q1_atr / 5, 0.5)

                # 確定價格範圍
                _q1_lo = min(_q1_l) * 0.995
                _q1_hi = max(_q1_h) * 1.005
                _q1_bins = int((_q1_hi - _q1_lo) / _q1_step) + 1
                if _q1_bins > 200: _q1_bins = 200; _q1_step = (_q1_hi - _q1_lo) / 200

                _q1_vol_map = [0.0] * _q1_bins

                for _bi in range(len(_q1_h)):
                    _bh, _bl, _bv = _q1_h[_bi], _q1_l[_bi], _q1_v[_bi]
                    _range_bins = max(1, int((_bh - _bl) / _q1_step))
                    _v_per_bin  = _bv / _range_bins
                    _start_bin  = int((_bl - _q1_lo) / _q1_step)
                    for _k in range(_range_bins):
                        _idx = _start_bin + _k
                        if 0 <= _idx < _q1_bins:
                            _q1_vol_map[_idx] += _v_per_bin

                # 找「真空帶」：連續N個格子的成交量低於平均的20%
                _q1_avg_vol = sum(_q1_vol_map) / max(1, len(_q1_vol_map))
                _q1_thresh  = _q1_avg_vol * 0.2
                _q1_gap_threshold = 3  # 至少連續3格才算真空帶

                # 找當前價格附近（±15%）的真空帶
                _q1_cur_bin = int((_q1_price_now - _q1_lo) / _q1_step)
                _q1_search_range = int(_q1_price_now * 0.15 / _q1_step)

                # 向下找真空帶
                _q1_gap_dn_start = _q1_gap_dn_end = None
                _gap_count = 0
                for _bi in range(max(0, _q1_cur_bin - 1), max(0, _q1_cur_bin - _q1_search_range), -1):
                    if _q1_vol_map[_bi] <= _q1_thresh:
                        _gap_count += 1
                        if _gap_count >= _q1_gap_threshold:
                            _q1_gap_dn_end   = _q1_lo + _bi * _q1_step
                            _q1_gap_dn_start = _q1_lo + (_bi - _gap_count + 1) * _q1_step
                            break
                    else:
                        _gap_count = 0

                # 向上找真空帶
                _q1_gap_up_start = _q1_gap_up_end = None
                _gap_count = 0
                for _bi in range(min(_q1_bins-1, _q1_cur_bin + 1), min(_q1_bins-1, _q1_cur_bin + _q1_search_range)):
                    if _q1_vol_map[_bi] <= _q1_thresh:
                        _gap_count += 1
                        if _gap_count >= _q1_gap_threshold:
                            _q1_gap_up_start = _q1_lo + (_bi - _gap_count + 1) * _q1_step
                            _q1_gap_up_end   = _q1_lo + _bi * _q1_step
                            break
                    else:
                        _gap_count = 0

                _q1_ts = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1])[:10]

                # 剛剛跌入下方真空帶（前一根在真空帶上方，當根進入）
                if _q1_gap_dn_start and _q1_gap_dn_end:
                    _gap_size = _q1_price_now - _q1_gap_dn_start
                    _gap_pct  = _gap_size / _q1_price_now * 100
                    _entered_gap = _q1_price_now < _q1_gap_dn_end and _q1_price_prev >= _q1_gap_dn_end

                    if _entered_gap:
                        _q1_ck = f"{symbol}|{period_label}|Q1-跌入真空帶|{_q1_ts}"
                        if _q1_ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_q1_ck)
                            add_alert(symbol, period_label,
                                      f"🚨 【Q1·跌入成交量真空帶】當前${_q1_price_now:.2f}"
                                      f" 剛跌入低密度區（${_q1_gap_dn_start:.0f}–${_q1_gap_dn_end:.0f}）"
                                      f"｜此區間60日內成交量極少，缺乏支撐"
                                      f"，可能快速下殺至真空帶底部${_q1_gap_dn_start:.0f}！", "bear")
                            new_signals.append(f"Q1-跌入真空帶${_q1_gap_dn_start:.0f}-${_q1_gap_dn_end:.0f}")

                    # 即使未剛剛進入，若已在真空帶內也提示
                    elif _q1_gap_dn_start <= _q1_price_now <= _q1_gap_dn_end:
                        _q1_ck2 = f"{symbol}|{period_label}|Q1-在真空帶內|{_q1_ts}"
                        if _q1_ck2 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_q1_ck2)
                            _to_bottom = _q1_price_now - _q1_gap_dn_start
                            add_alert(symbol, period_label,
                                      f"⚠️ 【Q1·處於成交量真空帶】${_q1_price_now:.2f}"
                                      f" 在低密度區（${_q1_gap_dn_start:.0f}–${_q1_gap_dn_end:.0f}）"
                                      f"｜距底部支撐${_to_bottom:.1f}（{_to_bottom/_q1_price_now*100:.1f}%）"
                                      f"，缺乏阻力，波動方向將加速", "bear")
                            new_signals.append(f"Q1-在真空帶內底${_q1_gap_dn_start:.0f}")

                # 剛剛突破進入上方真空帶（加速上行）
                if _q1_gap_up_start and _q1_gap_up_end:
                    _entered_gap_up = _q1_price_now > _q1_gap_up_start and _q1_price_prev <= _q1_gap_up_start
                    if _entered_gap_up:
                        _q1_ck3 = f"{symbol}|{period_label}|Q1-突破真空帶|{_q1_ts}"
                        if _q1_ck3 not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_q1_ck3)
                            add_alert(symbol, period_label,
                                      f"🚀 【Q1·突破進入上方真空帶】當前${_q1_price_now:.2f}"
                                      f" 進入低密度區（${_q1_gap_up_start:.0f}–${_q1_gap_up_end:.0f}）"
                                      f"｜此區間阻力極少，可能快速拉升至真空帶頂部${_q1_gap_up_end:.0f}！", "bull")
                            new_signals.append(f"Q1-突破真空帶${_q1_gap_up_start:.0f}-${_q1_gap_up_end:.0f}")
        except Exception:
            pass

        # ══════════════════════════════════════════════════════════════════════
        # R節：信號品質升級 — 價量背離 + 波段高低點
        # ══════════════════════════════════════════════════════════════════════

        # ── R1. 價量背離偵測（Price-Volume Divergence）─────────────────────
        # 多頭背離：價跌量縮 = 賣壓耗盡，底部反轉信號（買入）
        # 空頭背離：價漲量縮 = 上漲動能不足，頂部警告（賣出）
        # 強烈空頭：價連漲3根但每根成交量遞減 = 主力撤退，假突破
        try:
            if len(df) >= 8 and "Volume" in df.columns:
                _r1_c   = close.iloc[-6:].values
                _r1_v   = vol.iloc[-6:].values
                _r1_v_avg = float(vol.iloc[-20:].mean()) if len(vol) >= 20 else float(vol.mean())

                # 近3根方向
                _r1_c3  = _r1_c[-3:]
                _r1_v3  = _r1_v[-3:]
                _r1_c3_up   = all(_r1_c3[i] > _r1_c3[i-1] for i in range(1,3))  # 連漲
                _r1_c3_down = all(_r1_c3[i] < _r1_c3[i-1] for i in range(1,3))  # 連跌
                _r1_v3_shrink = all(_r1_v3[i] < _r1_v3[i-1] for i in range(1,3)) # 量遞減
                _r1_v3_expand = all(_r1_v3[i] > _r1_v3[i-1] for i in range(1,3)) # 量遞增

                _r1_ck_base = f"{symbol}|{period_label}|PVD"
                _r1_ts = df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]

                # 空頭背離：價連漲3根，量卻遞減（且量低於均量）
                if _r1_c3_up and _r1_v3_shrink and float(_r1_v3[-1]) < _r1_v_avg * 0.8:
                    _ck = f"{_r1_ck_base}|空頭背離|{_r1_ts}"
                    if _ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_ck)
                        _prise_rise = (_r1_c3[-1] - _r1_c3[0]) / _r1_c3[0] * 100
                        _vol_drop   = (1 - _r1_v3[-1] / _r1_v3[0]) * 100
                        add_alert(symbol, period_label,
                                  f"⚠️ 【R1·價量空頭背離】價連漲{_prise_rise:.1f}%但量遞減{_vol_drop:.0f}%"
                                  f"（末根量僅均量{_r1_v3[-1]/_r1_v_avg*100:.0f}%）"
                                  f"｜上漲動能不足，主力撤退跡象，謹慎追多！", "bear")
                        new_signals.append("R1-價漲量縮背離")

                # 多頭背離：價連跌3根，量卻遞減（跌勢動能衰竭）
                elif _r1_c3_down and _r1_v3_shrink and float(_r1_v3[-1]) < _r1_v_avg * 0.7:
                    _ck = f"{_r1_ck_base}|多頭背離|{_r1_ts}"
                    if _ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_ck)
                        _price_fall = (_r1_c3[0] - _r1_c3[-1]) / _r1_c3[0] * 100
                        _vol_drop   = (1 - _r1_v3[-1] / _r1_v3[0]) * 100
                        add_alert(symbol, period_label,
                                  f"🔄 【R1·價量多頭背離】價連跌{_price_fall:.1f}%但量遞減{_vol_drop:.0f}%"
                                  f"（末根量僅均量{_r1_v3[-1]/_r1_v_avg*100:.0f}%）"
                                  f"｜下跌動能衰竭，賣壓耗盡，底部反轉可能！", "bull")
                        new_signals.append("R1-價跌量縮反轉")

                # 量能爆炸確認突破：價漲+量同步遞增（最強確認）
                elif _r1_c3_up and _r1_v3_expand and float(_r1_v3[-1]) > _r1_v_avg * 1.5:
                    _ck = f"{_r1_ck_base}|量能確認|{_r1_ts}"
                    if _ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_ck)
                        _vol_ratio = _r1_v3[-1] / _r1_v_avg
                        add_alert(symbol, period_label,
                                  f"🚀 【R1·量價齊升確認】價連漲+量遞增，末根量{_vol_ratio:.1f}×均量"
                                  f"｜主力積極建倉，突破動能充足，多頭最強確認！", "bull")
                        new_signals.append("R1-量價齊升確認")
        except Exception:
            pass

        # ── R2. 波段高點/低點自動標記（Swing High/Low）──────────────────────
        # 邏輯：偵測最近N根K線中的局部極值，判斷是否剛突破前波高點或跌破前波低點
        # 突破前波高點 + 量能確認 → 趨勢延伸多頭信號
        # 跌破前波低點 + 量能確認 → 趨勢延伸空頭信號
        try:
            if len(df) >= 20 and "High" in df.columns:
                _r2_h  = high.values
                _r2_l  = low.values
                _r2_c  = close.values
                _r2_v  = vol.values
                _r2_n  = len(_r2_c)

                # 尋找前波高點（排除最近3根，往前找5-20根內的最高高點）
                _r2_lookback = min(20, _r2_n - 4)
                _r2_prev_hi  = float(max(_r2_h[-_r2_lookback-3:-3]))
                _r2_prev_lo  = float(min(_r2_l[-_r2_lookback-3:-3]))
                _r2_curr     = float(_r2_c[-1])
                _r2_curr_h   = float(_r2_h[-1])
                _r2_curr_l   = float(_r2_l[-1])
                _r2_vol_avg  = float(vol.rolling(14).mean().iloc[-1])
                _r2_vol_surge = float(_r2_v[-1]) > _r2_vol_avg * 1.4

                _r2_ts = df.index[-1].strftime('%Y%m%d') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:10]

                # 突破前波高點（收盤站上+量能確認）
                if (_r2_curr > _r2_prev_hi * 1.005 and
                    float(_r2_c[-2]) <= _r2_prev_hi and _r2_vol_surge):
                    _ck = f"{symbol}|{period_label}|R2突破前波高|{_r2_ts}"
                    if _ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_ck)
                        add_alert(symbol, period_label,
                                  f"🏆 【R2·突破前波高點】收盤{_r2_curr:.2f}突破前{_r2_lookback}根高點"
                                  f"{_r2_prev_hi:.2f}（+{(_r2_curr/_r2_prev_hi-1)*100:.1f}%）"
                                  f"｜量能{float(_r2_v[-1])/_r2_vol_avg:.1f}×確認，趨勢延伸多頭！", "bull")
                        new_signals.append(f"R2-突破前波高{_r2_prev_hi:.2f}")

                # 跌破前波低點（收盤跌穿+量能確認）
                elif (_r2_curr < _r2_prev_lo * 0.995 and
                      float(_r2_c[-2]) >= _r2_prev_lo and _r2_vol_surge):
                    _ck = f"{symbol}|{period_label}|R2跌破前波低|{_r2_ts}"
                    if _ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_ck)
                        add_alert(symbol, period_label,
                                  f"💥 【R2·跌破前波低點】收盤{_r2_curr:.2f}跌破前{_r2_lookback}根低點"
                                  f"{_r2_prev_lo:.2f}（-{(1-_r2_curr/_r2_prev_lo)*100:.1f}%）"
                                  f"｜量能{float(_r2_v[-1])/_r2_vol_avg:.1f}×確認，趨勢延伸空頭！", "bear")
                        new_signals.append(f"R2-跌破前波低{_r2_prev_lo:.2f}")
        except Exception:
            pass

        # ══════════════════════════════════════════════════════════════════════
        # S節：盤整區間偵測 + 突破預警系統
        # 自動劃出上下邊界 → 監控放量突破 → 配合VIX+背景方向給信心度
        # ══════════════════════════════════════════════════════════════════════
        try:
            if len(df) >= 15 and "High" in df.columns:
                # ── S1. 壓縮盤整區間偵測 ────────────────────────────────────
                # 邏輯：找最近 N 根K線（排除最後1根）的最高/最低
                # 若(最高-最低)/ATR < 壓縮閾值 → 確認盤整
                _s_lookback = min(30, len(df) - 1)
                _s_window   = df.iloc[-_s_lookback-1:-1]   # 排除最後1根

                _s_hi   = float(_s_window["High"].max())
                _s_lo   = float(_s_window["Low"].min())
                _s_rng  = _s_hi - _s_lo
                _s_atr  = float((high - low).rolling(14).mean().iloc[-2])  # 用前一根ATR
                _s_rng_atr_ratio = _s_rng / max(_s_atr, 0.01)

                # 壓縮閾值：區間寬度 < 1.2×ATR = 高度壓縮
                _s_compressed = _s_rng_atr_ratio < 1.2

                # 還需要確認K線密集在區間中段（非趨勢行進）
                # 用收盤價標準差 vs ATR 來判斷
                _s_close_std = float(_s_window["Close"].std())
                _s_tight = _s_close_std / max(_s_atr, 0.01) < 0.35

                _s_ts = df.index[-1].strftime('%Y%m%d%H%M') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:16]
                _s_date = _s_ts[:8]

                # ── S2. 突破偵測（最新根K線放量突破邊界）──────────────────
                _s_curr      = float(close.iloc[-1])
                _s_prev      = float(close.iloc[-2])
                _s_curr_h    = float(high.iloc[-1])
                _s_curr_l    = float(low.iloc[-1])
                _s_vol_now   = float(vol.iloc[-1])
                _s_vol_avg   = float(vol.rolling(10).mean().iloc[-1])
                _s_vol_surge = _s_vol_now > _s_vol_avg * 1.3   # 放量閾值

                # 突破確認：收盤站上/穿破邊界 + 量能配合
                _s_break_up   = (_s_curr > _s_hi * 1.002 and
                                 _s_prev <= _s_hi and _s_vol_surge)
                _s_break_down = (_s_curr < _s_lo * 0.998 and
                                 _s_prev >= _s_lo and _s_vol_surge)

                # 即將突破（收盤在邊界±0.15%內，量能開始放大）
                _s_near_break_up   = (abs(_s_curr - _s_hi) / _s_hi < 0.0015 and
                                      _s_vol_now > _s_vol_avg * 1.1)
                _s_near_break_down = (abs(_s_curr - _s_lo) / _s_lo < 0.0015 and
                                      _s_vol_now > _s_vol_avg * 1.1)

                if _s_compressed and _s_tight:
                    # ── S3. 取得背景方向（日K EMA排列 → 決定突破偏向）────
                    try:
                        _s_daily = yf.download(symbol, period="60d", interval="1d",
                                               auto_adjust=True, progress=False)
                        if isinstance(_s_daily.columns, pd.MultiIndex):
                            _s_daily.columns = [c[0] for c in _s_daily.columns]
                        _s_d_close = _s_daily["Close"].dropna()
                        _s_e20d = float(_s_d_close.ewm(span=20).mean().iloc[-1])
                        _s_e60d = float(_s_d_close.ewm(span=60).mean().iloc[-1])
                        _s_e200d= float(_s_d_close.ewm(span=200).mean().iloc[-1])
                        _s_daily_price = float(_s_d_close.iloc[-1])
                        if _s_daily_price > _s_e20d > _s_e60d > _s_e200d:
                            _s_bg_dir = "bull"; _s_bg_label = "日K全EMA多頭排列"
                        elif _s_daily_price < _s_e20d < _s_e60d < _s_e200d:
                            _s_bg_dir = "bear"; _s_bg_label = "日K全EMA空頭排列"
                        else:
                            _s_bg_dir = "neutral"; _s_bg_label = "日K震盪"
                    except Exception:
                        _s_bg_dir = "neutral"; _s_bg_label = "背景未知"

                    # ── S4. VIX即時方向 ────────────────────────────────────
                    try:
                        _s_vix = fetch_vix_intraday()
                        _s_vix_bull = _s_vix.get("signal", 0) > 0   # VIX下行
                        _s_vix_bear = _s_vix.get("signal", 0) < 0   # VIX上行
                        _s_vix_val  = _s_vix.get("spot", None)
                        _s_vix_note = f"VIX={_s_vix_val:.1f}" if _s_vix_val else "VIX未知"
                    except Exception:
                        _s_vix_bull = False; _s_vix_bear = False
                        _s_vix_note = "VIX未知"

                    # ── 盤整區間提示（尚未突破，僅提示壓縮）──────────────
                    _s_compress_ck = f"{symbol}|{period_label}|盤整壓縮|{_s_date}"
                    if _s_compress_ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(_s_compress_ck)
                        _s_conf_pct = int((1 - _s_rng_atr_ratio / 1.2) * 100)
                        _s_bias = ("偏多突破" if _s_bg_dir == "bull"
                                   else "偏空突破" if _s_bg_dir == "bear"
                                   else "方向待定")
                        add_alert(symbol, period_label,
                                  f"🔲 【S1·盤整壓縮{_conf_pct}%】近{_s_lookback}根K線"
                                  f"區間${_s_lo:.2f}–${_s_hi:.2f}（寬{_s_rng:.2f}={_s_rng_atr_ratio:.1f}×ATR）"
                                  f"｜{_s_bg_label}背景→{_s_bias}"
                                  f"｜{_s_vix_note}"
                                  f"｜等待放量突破確認方向！", "info")
                        new_signals.append(f"S1-盤整壓縮{_s_rng_atr_ratio:.1f}xATR")
                        # 建立進場追蹤（預備狀態）
                        if _s_bg_dir == "bull":
                            add_entry_tracker(symbol, "LONG",
                                              f"S1-盤整壓縮等突破上邊界${_s_hi:.2f}",
                                              _s_hi, period_label)
                        elif _s_bg_dir == "bear":
                            add_entry_tracker(symbol, "SHORT",
                                              f"S1-盤整壓縮等突破下邊界${_s_lo:.2f}",
                                              _s_lo, period_label)

                    # ── 即將突破警告 ────────────────────────────────────────
                    if _s_near_break_up and not _s_break_up:
                        _ck = f"{symbol}|{period_label}|即將突破上|{_s_ts}"
                        if _ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck)
                            _conf = 70 + (15 if _s_bg_dir=="bull" else 0) + (10 if _s_vix_bull else 0)
                            add_alert(symbol, period_label,
                                      f"⚡ 【S2·即將突破上邊界】現價${_s_curr:.2f}逼近阻力${_s_hi:.2f}"
                                      f"（距離{(_s_hi-_s_curr)/_s_hi*100:.2f}%）量{_s_vol_now/_s_vol_avg:.1f}×放大"
                                      f"｜{_s_bg_label}+{_s_vix_note}｜突破信心{_conf}%"
                                      f"｜突破目標：${_s_hi+_s_rng:.2f}（+{_s_rng/_s_hi*100:.1f}%）", "bull")
                            new_signals.append(f"S2-即將突破上${_s_hi:.2f}")

                    if _s_near_break_down and not _s_break_down:
                        _ck = f"{symbol}|{period_label}|即將突破下|{_s_ts}"
                        if _ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck)
                            _conf = 70 + (15 if _s_bg_dir=="bear" else 0) + (10 if _s_vix_bear else 0)
                            add_alert(symbol, period_label,
                                      f"⚡ 【S2·即將跌破下邊界】現價${_s_curr:.2f}逼近支撐${_s_lo:.2f}"
                                      f"（距離{(_s_curr-_s_lo)/_s_lo*100:.2f}%）量{_s_vol_now/_s_vol_avg:.1f}×放大"
                                      f"｜{_s_bg_label}+{_s_vix_note}｜跌破信心{_conf}%"
                                      f"｜跌破目標：${_s_lo-_s_rng:.2f}（-{_s_rng/_s_lo*100:.1f}%）", "bear")
                            new_signals.append(f"S2-即將跌破下${_s_lo:.2f}")

                    # ── 突破確認（最高置信）────────────────────────────────
                    if _s_break_up:
                        _ck = f"{symbol}|{period_label}|突破確認上|{_s_ts}"
                        if _ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck)
                            _conf = 80 + (15 if _s_bg_dir=="bull" else -10) + (10 if _s_vix_bull else 0)
                            _target1 = _s_hi + _s_rng          # 目標1：區間等幅投射
                            _target2 = _s_hi + _s_rng * 2.0    # 目標2：2倍
                            _sl      = _s_hi - _s_atr * 0.5    # 止損：突破點下方半個ATR
                            add_alert(symbol, period_label,
                                      f"🚀🚀 【S3·盤整突破確認·多頭】收盤${_s_curr:.2f}放量突破"
                                      f"盤整上邊界${_s_hi:.2f}（量{_s_vol_now/_s_vol_avg:.1f}×）"
                                      f"｜{_s_bg_label}+{_s_vix_note}"
                                      f"｜信心{_conf}%"
                                      f"｜目標①${_target1:.2f} 目標②${_target2:.2f}"
                                      f"｜止損${_sl:.2f}", "bull")
                            new_signals.append(f"S3-盤整突破上確認${_s_curr:.2f}")
                            generate_trade_suggestion(symbol, period_label,
                                                      f"S3-盤整突破上${_s_hi:.2f}",
                                                      "bull", _s_curr, _s_atr)
                            add_entry_tracker(symbol, "LONG",
                                              f"S3-盤整突破上${_s_hi:.2f}",
                                              _s_curr, period_label, atr=_s_atr)

                    elif _s_break_down:
                        _ck = f"{symbol}|{period_label}|突破確認下|{_s_ts}"
                        if _ck not in st.session_state.sent_alerts:
                            st.session_state.sent_alerts.add(_ck)
                            _conf = 80 + (15 if _s_bg_dir=="bear" else -10) + (10 if _s_vix_bear else 0)
                            _target1 = _s_lo - _s_rng
                            _target2 = _s_lo - _s_rng * 2.0
                            _sl      = _s_lo + _s_atr * 0.5
                            add_alert(symbol, period_label,
                                      f"💥💥 【S3·盤整跌破確認·空頭】收盤${_s_curr:.2f}放量跌破"
                                      f"盤整下邊界${_s_lo:.2f}（量{_s_vol_now/_s_vol_avg:.1f}×）"
                                      f"｜{_s_bg_label}+{_s_vix_note}"
                                      f"｜信心{_conf}%"
                                      f"｜目標①${_target1:.2f} 目標②${_target2:.2f}"
                                      f"｜止損${_sl:.2f}", "bear")
                            new_signals.append(f"S3-盤整跌破下確認${_s_curr:.2f}")
                            generate_trade_suggestion(symbol, period_label,
                                                      f"S3-盤整跌破下${_s_lo:.2f}",
                                                      "bear", _s_curr, _s_atr)
                            add_entry_tracker(symbol, "SHORT",
                                              f"S3-盤整跌破下${_s_lo:.2f}",
                                              _s_curr, period_label, atr=_s_atr)

        except Exception:
            pass

    except Exception:
        pass
        return
    ai_key = f"ai_signal_{symbol}_{period_label}_{'_'.join(new_signals[:2])}"
    if ai_key in st.session_state:
        return

    signal_summary = "、".join(new_signals)
    prompt = build_analysis_prompt(symbol, period_label, df, mkt)
    prompt = f"【觸發信號】{symbol} {period_label} 剛出現：{signal_summary}\n\n" + prompt
    result = call_groq_analysis(prompt)
    result["_signals"]      = new_signals
    result["_symbol"]       = symbol
    result["_period"]       = period_label
    result["_trigger_time"] = datetime.now().strftime("%H:%M:%S")
    st.session_state[ai_key] = result
    if "ai_signal_results" not in st.session_state:
        st.session_state["ai_signal_results"] = []
    st.session_state["ai_signal_results"].insert(0, result)
    st.session_state["ai_signal_results"] = st.session_state["ai_signal_results"][:20]

# ══════════════════════════════════════════════════════════════════════════════
# 建立 K 線圖
# ══════════════════════════════════════════════════════════════════════════════
def build_chart(symbol, df, interval_label, compact=False, max_bars=90, ext_data=None):
    if df.empty: return None

    # ── 限制最多顯示 90 根 K 線，避免圖表擁擠 ──
    # EMA/MACD 用完整數據計算（保留歷史），再截取最後 90 根顯示
    MAX_BARS = max(10, int(max_bars))   # 使用者自訂，最少10根
    close_full, vol_full = df["Close"], df["Volume"]
    ema_s_full = {n: calc_ema(close_full, n) for n, _ in EMA_CONFIGS}
    ma_s_full  = {n: calc_ma(close_full,  n) for n, _, _ in MA_CONFIGS}
    dif_full, dea_full, hist_full = calc_macd(close_full)

    # 截取最後 90 根用於繪圖
    df   = df.tail(MAX_BARS).copy()
    close, vol = df["Close"], df["Volume"]
    ema_s = {n: s.tail(MAX_BARS) for n, s in ema_s_full.items()}
    ma_s  = {n: s.tail(MAX_BARS) for n, s in ma_s_full.items()}
    dif   = dif_full.tail(MAX_BARS)
    dea   = dea_full.tail(MAX_BARS)
    hist  = hist_full.tail(MAX_BARS)

    # 支撐阻力用截取後的資料
    itvl_code = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(interval_label, "1d")
    pivots_h, pivots_l = calc_pivot(df, interval=itvl_code)

    # ── 消除休市空白：把 DatetimeIndex 轉成字串當 category label ──────────
    # Plotly category 軸只顯示實際存在的類別，自動跳過休市間隙
    intraday = interval_label in {"1分鐘","5分鐘","15分鐘","30分鐘"}
    fmt = "%m/%d %H:%M" if intraday else "%y/%m/%d"
    xlabels = [t.strftime(fmt) for t in df.index]
    # 所有 series 也配對成同樣的字串 index，確保對齊
    vol_ma5 = vol.rolling(5).mean()

    chart_h = 520 if compact else 920
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.50, 0.15, 0.20, 0.15], vertical_spacing=0.018,
        subplot_titles=(f"{symbol} ({interval_label})", "成交量", "MACD", "MTF BX Signal"),
    )
    ann_size = 11 if compact else 13
    for ann in fig.layout.annotations:
        ann.font.size  = ann_size
        ann.font.color = "#ccddee"

    # K 線：區分正規時段（綠/紅）和延長時段（藍/紫）
    try:
        import pytz as _pytz
        _et = _pytz.timezone("America/New_York")
        _idx_et = df.index.tz_convert(_et) if df.index.tzinfo else df.index.tz_localize("UTC").tz_convert(_et)
        def _is_regular(t):
            return (t.hour > 9 or (t.hour == 9 and t.minute >= 30)) and t.hour < 16
        _reg_mask = [_is_regular(t) for t in _idx_et]
        _ext_mask = [not m for m in _reg_mask]
    except Exception:
        _reg_mask = [True] * len(df)
        _ext_mask = [False] * len(df)

    _has_ext = any(_ext_mask)

    if _has_ext:
        # 正規時段 K 線
        _reg_idx = [i for i,m in enumerate(_reg_mask) if m]
        if _reg_idx:
            fig.add_trace(go.Candlestick(
                x=[xlabels[i] for i in _reg_idx],
                open=[df["Open"].iloc[i]  for i in _reg_idx],
                high=[df["High"].iloc[i]  for i in _reg_idx],
                low= [df["Low"].iloc[i]   for i in _reg_idx],
                close=[df["Close"].iloc[i] for i in _reg_idx],
                increasing_line_color="#00cc44", increasing_fillcolor="#00cc44",
                decreasing_line_color="#ff4444", decreasing_fillcolor="#ff4444",
                name="正規時段", showlegend=True,
            ), row=1, col=1)
        # 延長時段 K 線（藍/紫色）
        _ext_idx = [i for i,m in enumerate(_ext_mask) if m]
        if _ext_idx:
            fig.add_trace(go.Candlestick(
                x=[xlabels[i] for i in _ext_idx],
                open=[df["Open"].iloc[i]  for i in _ext_idx],
                high=[df["High"].iloc[i]  for i in _ext_idx],
                low= [df["Low"].iloc[i]   for i in _ext_idx],
                close=[df["Close"].iloc[i] for i in _ext_idx],
                increasing_line_color="#3399ff", increasing_fillcolor="#3399ff",
                decreasing_line_color="#9944ff", decreasing_fillcolor="#9944ff",
                name="延長時段", showlegend=True, opacity=0.85,
            ), row=1, col=1)
    else:
        fig.add_trace(go.Candlestick(
            x=xlabels, open=df["Open"], high=df["High"], low=df["Low"], close=close,
            increasing_line_color="#00cc44", increasing_fillcolor="#00cc44",
            decreasing_line_color="#ff4444", decreasing_fillcolor="#ff4444",
            name="K線", showlegend=False,
        ), row=1, col=1)

    # ── 盤前/盤後 K 線疊加（Yahoo Finance 延長時段）───────────────────────
    if ext_data:
        _ext_sessions = [
            ("pre",       ext_data.get("pre",       pd.DataFrame()), "#3399ff", "#9944ff", "盤前"),
            ("post",      ext_data.get("post",      pd.DataFrame()), "#00ccaa", "#cc8800", "盤後"),
            ("overnight", ext_data.get("overnight", pd.DataFrame()), "#00aaaa", "#886600", "夜盤"),
        ]
        for _sess_key, _sdf, _cup, _cdn, _sname in _ext_sessions:
            if _sdf.empty:
                continue
            # Align to same fmt string labels
            _sdf = _sdf.copy()
            _sdf.index = pd.to_datetime(_sdf.index)
            _xlbl = [t.strftime(fmt) for t in _sdf.index]
            _cols = [c[0] if isinstance(c, tuple) else c for c in _sdf.columns]
            _sdf.columns = _cols
            if not all(c in _sdf.columns for c in ["Open","High","Low","Close"]):
                continue
            fig.add_trace(go.Candlestick(
                x=_xlbl,
                open=_sdf["Open"], high=_sdf["High"],
                low=_sdf["Low"],   close=_sdf["Close"],
                name=_sname,
                increasing_line_color=_cup, increasing_fillcolor=_cup,
                decreasing_line_color=_cdn, decreasing_fillcolor=_cdn,
                line=dict(width=0.8), opacity=0.85,
            ), row=1, col=1)

    # EMA 線
    for n, color in EMA_CONFIGS:
        fig.add_trace(go.Scatter(
            x=xlabels, y=ema_s[n],
            line=dict(color=color, width=1.3), name=f"EMA{n}", opacity=0.9,
        ), row=1, col=1)

    # MA 線
    for n, color, dash in MA_CONFIGS:
        fig.add_trace(go.Scatter(
            x=xlabels, y=ma_s[n],
            line=dict(color=color, width=1.8, dash=dash), name=f"MA{n}",
        ), row=1, col=1)

    # 支撐阻力
    if pivots_h:
        r = max(p[1] for p in pivots_h)
        fig.add_hline(y=r, line=dict(color="#ff8888", dash="dash", width=1.5),
                      annotation_text=f"阻力 {r:.2f}",
                      annotation_font=dict(size=12, color="#ff8888"),
                      annotation_bgcolor="rgba(30,10,10,0.8)", row=1, col=1)
    if pivots_l:
        s = min(p[1] for p in pivots_l)
        fig.add_hline(y=s, line=dict(color="#88ff88", dash="dash", width=1.5),
                      annotation_text=f"支撐 {s:.2f}",
                      annotation_font=dict(size=12, color="#88ff88"),
                      annotation_bgcolor="rgba(10,30,10,0.8)", row=1, col=1)

    # ── 跳空缺口視覺標記 ─────────────────────────────────────────────────────
    try:
        itvl_key_chart = {v[0]: k for k, v in INTERVAL_MAP.items()}.get(interval_label, "1d")
        is_daily_chart  = itvl_key_chart in ("1d", "1wk", "1mo")
        min_gap_vis     = 0.05 if is_daily_chart else 0.10
        vol_ma10_chart  = df["Volume"].rolling(10).mean()

        gap_up_xs, gap_up_ys, gap_up_txt   = [], [], []
        gap_dn_xs, gap_dn_ys, gap_dn_txt   = [], [], []

        scan_n = min(len(df)-1, 30)
        for gi in range(1, scan_n + 1):
            idx_pos  = len(df) - scan_n - 1 + gi
            if idx_pos < 1: continue
            b_open   = float(df["Open"].iloc[idx_pos])
            p_high   = float(df["High"].iloc[idx_pos - 1])
            p_low    = float(df["Low"].iloc[idx_pos - 1])
            p_close  = float(df["Close"].iloc[idx_pos - 1])
            if p_close == 0: continue
            gap_up   = (b_open - p_high) / p_close * 100
            gap_dn   = (p_low  - b_open) / p_close * 100
            vol_ma_v = float(vol_ma10_chart.iloc[idx_pos])
            vol_r    = float(df["Volume"].iloc[idx_pos]) / max(vol_ma_v, 1) if not (vol_ma_v != vol_ma_v) else 1.0

            xlab = xlabels[idx_pos]
            mid_gap_up = (b_open + p_high) / 2
            mid_gap_dn = (b_open + p_low)  / 2

            if gap_up >= min_gap_vis:
                gap_up_xs.append(xlab)
                gap_up_ys.append(mid_gap_up)
                gap_up_txt.append(f"跳空上漲 +{gap_up:.2f}%<br>量×{vol_r:.1f} {'🔔' if vol_r>=1.3 else '⚠️'}")
                # shaded gap zone
                fig.add_hrect(y0=p_high, y1=b_open,
                              fillcolor="rgba(0,255,100,0.07)",
                              line_width=0, row=1, col=1)
                fig.add_hline(y=p_high, line=dict(color="rgba(0,255,100,0.3)", width=1, dash="dot"),
                              row=1, col=1)

            if gap_dn >= min_gap_vis:
                gap_dn_xs.append(xlab)
                gap_dn_ys.append(mid_gap_dn)
                gap_dn_txt.append(f"跳空下跌 -{gap_dn:.2f}%<br>量×{vol_r:.1f} {'🔴' if vol_r>=1.3 else '⚠️'}")
                fig.add_hrect(y0=b_open, y1=p_low,
                              fillcolor="rgba(255,60,60,0.07)",
                              line_width=0, row=1, col=1)

        if gap_up_xs:
            fig.add_trace(go.Scatter(
                x=gap_up_xs, y=gap_up_ys, mode="markers",
                marker=dict(symbol="triangle-up", size=14,
                            color="#00ff88", line=dict(color="#ffffff", width=1)),
                name="跳空上漲", hovertext=gap_up_txt, hoverinfo="text+x",
            ), row=1, col=1)
        if gap_dn_xs:
            fig.add_trace(go.Scatter(
                x=gap_dn_xs, y=gap_dn_ys, mode="markers",
                marker=dict(symbol="triangle-down", size=14,
                            color="#ff4444", line=dict(color="#ffffff", width=1)),
                name="跳空下跌", hovertext=gap_dn_txt, hoverinfo="text+x",
            ), row=1, col=1)
    except Exception:
        pass

    # ── 線性回歸通道 ─────────────────────────────────────────────────────────
    try:
        ch = calc_channel(df, lookback=min(30, len(df)))
        if ch and ch["r2"] >= 0.40:
            import numpy as np
            sub    = df.tail(min(30, len(df)))
            x      = np.arange(len(sub))
            hi_c   = np.polyfit(x, sub["High"].values.astype(float), 1)
            lo_c   = np.polyfit(x, sub["Low"].values.astype(float), 1)
            mid_c  = np.polyfit(x, sub["Close"].values.astype(float), 1)
            xlbl_ch = xlabels[-min(30, len(df)):]
            x_ends  = [0, len(sub)-1]

            ch_color  = "#4488ff" if ch["direction"] == "up" else (
                        "#ff6644" if ch["direction"] == "down" else "#aaaaaa")
            ch_label  = {"up":"上升通道","down":"下降通道","flat":"橫盤通道"}[ch["direction"]]

            for coeffs, y_offset, dash, ann in [
                (hi_c,  0, "solid", f"{ch_label} R²={ch['r2']:.2f}"),
                (lo_c,  0, "solid", None),
                (mid_c, 0, "dot",   None),
            ]:
                y_vals = [float(np.polyval(coeffs, xi)) for xi in x_ends]
                fig.add_trace(go.Scatter(
                    x=[xlbl_ch[0], xlbl_ch[-1]],
                    y=y_vals,
                    mode="lines",
                    line=dict(color=ch_color, width=1.2 if dash=="solid" else 0.8,
                              dash=dash),
                    opacity=0.65,
                    showlegend=(ann is not None),
                    name=ann or "",
                ), row=1, col=1)
    except Exception:
        pass

    # 最高最低
    max_pos = int(df["High"].values.argmax())
    min_pos = int(df["Low"].values.argmin())
    fig.add_annotation(x=xlabels[max_pos], y=float(df["High"].max()),
        text=f"▲ {df['High'].max():.2f}", showarrow=True,
        arrowhead=2, arrowcolor="#ff4444", arrowwidth=2,
        font=dict(color="#ff8888", size=11, family="Arial Black"),
        bgcolor="rgba(30,10,10,0.85)", bordercolor="#ff4444", borderwidth=1,
        row=1, col=1)
    fig.add_annotation(x=xlabels[min_pos], y=float(df["Low"].min()),
        text=f"▼ {df['Low'].min():.2f}", showarrow=True,
        arrowhead=2, arrowcolor="#ff4444", arrowwidth=2,
        font=dict(color="#ff8888", size=11, family="Arial Black"),
        bgcolor="rgba(30,10,10,0.85)", bordercolor="#ff4444", borderwidth=1,
        row=1, col=1)

    # ── 成交量 ──────────────────────────────────────────────────────────────
    col_vol = ["#00cc44" if c >= o else "#ff4444"
               for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(x=xlabels, y=vol, marker_color=col_vol,
                         name="成交量", showlegend=False), row=2, col=1)
    vol_ma5 = vol.rolling(5).mean()
    fig.add_trace(go.Scatter(x=xlabels, y=vol_ma5,
                              line=dict(color="#ffaa00", width=1.5), name="VOL MA5"), row=2, col=1)

    # 異常放量：只標記「最顯著的幾根」，用柱子邊框高亮 + 頂部小鑽石
    # 策略：同一段密集放量只取最大的那根，避免連續出現滿屏標注
    anomaly_mask = (vol > vol_ma5 * 2).values
    if anomaly_mask.any():
        # 把連續異常段落找出來，每段只取量最大的那根
        groups, in_group, g_start = [], False, 0
        for i, flag in enumerate(anomaly_mask):
            if flag and not in_group:
                in_group, g_start = True, i
            elif not flag and in_group:
                groups.append((g_start, i - 1))
                in_group = False
        if in_group:
            groups.append((g_start, len(anomaly_mask) - 1))

        # 每段取量最大的 bar 的 integer position
        rep_pos = []
        for g0, g1 in groups:
            seg_vals = vol.values[g0:g1+1]
            rep_pos.append(g0 + int(seg_vals.argmax()))

        rep_x    = [xlabels[p]  for p in rep_pos]
        rep_vol  = [float(vol.values[p]) for p in rep_pos]
        rep_ma   = []
        for p in rep_pos:
            mv = vol_ma5.values[p]
            try:
                import math
                rep_ma.append(float(mv) if not math.isnan(float(mv)) else 1.0)
            except Exception:
                rep_ma.append(1.0)
        mult_txt = [f"異常放量 {v/max(m,1):.1f}x 均量"
                    for v, m in zip(rep_vol, rep_ma)]

        # 柱頂鑽石標記（不加擁擠文字，hover 查看倍數）
        fig.add_trace(go.Scatter(
            x=rep_x, y=rep_vol,
            mode="markers",
            marker=dict(color="#ff00ff", size=11, symbol="diamond",
                        line=dict(color="#ffffff", width=1.2)),
            name="異常放量",
            hovertext=mult_txt,
            hoverinfo="text+x",
        ), row=2, col=1)

    # ── MACD ────────────────────────────────────────────────────────────────
    bar_col = ["#ff4444" if v >= 0 else "#00cc44" for v in hist]
    fig.add_trace(go.Bar(x=xlabels, y=hist, marker_color=bar_col,
                         name="MACD柱", showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=xlabels, y=dif,
                              line=dict(color="#ffaa00", width=1.5), name="DIF"), row=3, col=1)
    fig.add_trace(go.Scatter(x=xlabels, y=dea,
                              line=dict(color="#0088ff", width=1.5), name="DEA"), row=3, col=1)

    # ── 金叉/死叉（智能去擁擠）────────────────────────────────────────────
    # 收集所有原始交叉點
    raw_crosses = []
    for i in range(1, len(dif)):
        if dif.iloc[i] > dea.iloc[i] and dif.iloc[i-1] <= dea.iloc[i-1]:
            raw_crosses.append((i, "gold"))
        elif dif.iloc[i] < dea.iloc[i] and dif.iloc[i-1] >= dea.iloc[i-1]:
            raw_crosses.append((i, "dead"))

    # 間距過濾：相鄰標注至少 min_gap 根 K 線，且同方向連發只取最新
    total_bars = len(dif)
    min_gap    = max(6, total_bars // 20)
    max_labels = 3 if compact else 5

    filtered, last_pos, last_type = [], -9999, None
    for pos, ctype in reversed(raw_crosses):
        gap_ok  = (pos - last_pos) >= min_gap or last_pos == -9999
        diff_ok = (ctype != last_type) or last_pos == -9999
        if gap_ok and diff_ok:
            filtered.insert(0, (pos, ctype))
            last_pos, last_type = pos, ctype
        if len(filtered) >= max_labels:
            break

    # 繪製：金叉標在底部（ay 正值=往下偏移），死叉標在頂部（ay 負值=往上偏移）
    # 固定像素偏移，不依賴 MACD 數值範圍，確保 compact/full 都清晰
    base_px = 38 if compact else 46

    for seq, (pos, ctype) in enumerate(filtered):
        x_val  = xlabels[pos]
        y_val  = float(dif.iloc[pos])
        extra  = 1 + (seq % 2) * 0.45    # 偶數序號偏移更遠，水平錯開
        if ctype == "gold":
            ay_px  = int(base_px * extra)     # 正 = 箭頭朝上，標籤在下方
            text   = "⬆ 金叉"
            fcol, bgcol, bcol, acol = "#ffee55", "rgba(36,32,0,0.92)", "#bbaa00", "#ddcc00"
        else:
            ay_px  = -int(base_px * extra)    # 負 = 箭頭朝下，標籤在上方
            text   = "⬇ 死叉"
            fcol, bgcol, bcol, acol = "#ff9999", "rgba(36,0,0,0.92)", "#bb3333", "#cc4444"

        fig.add_annotation(
            x=x_val, y=y_val, text=text,
            showarrow=True, arrowhead=2, arrowwidth=1.5,
            ax=0, ay=ay_px,
            arrowcolor=acol,
            font=dict(color=fcol, size=9 if compact else 10, family="Arial Black"),
            bgcolor=bgcol, bordercolor=bcol, borderwidth=1, borderpad=3,
            row=3, col=1,
        )

    leg_sz = 8 if compact else 11

    # ── MTF BX Signal（多時間框架突破強度直方圖）────────────────────────────
    # 邏輯：用4個維度各打分 → 加總得出每根K的多空強度
    # D1: 價格 vs EMA20（+1多/-1空）
    # D2: EMA20 vs EMA60（+1多/-1空）
    # D3: MACD hist 方向 + 動能（+2強多/+1弱多/-1弱空/-2強空）
    # D4: 近3根K線趨勢動能（收盤連續升/降）
    try:
        _bx_close  = close_full.tail(MAX_BARS)
        _bx_e20    = calc_ema(_bx_close, 20)
        _bx_e60    = calc_ema(_bx_close, 60)
        _bx_hist   = hist_full.tail(MAX_BARS)

        _bx_scores = []
        for _i in range(len(_bx_close)):
            _sc = 0
            _c  = float(_bx_close.iloc[_i])
            _e20= float(_bx_e20.iloc[_i])
            _e60= float(_bx_e60.iloc[_i])
            _h  = float(_bx_hist.iloc[_i])

            # D1: 價格 vs EMA20
            _sc += 1 if _c > _e20 else -1
            # D2: EMA20 vs EMA60
            _sc += 1 if _e20 > _e60 else -1
            # D3: MACD 強度
            if _i > 0:
                _h_prev = float(_bx_hist.iloc[_i-1])
                if _h > 0 and _h > _h_prev:   _sc += 2   # 紅柱擴張（強多）
                elif _h > 0:                    _sc += 1   # 紅柱收縮
                elif _h < 0 and _h < _h_prev:  _sc -= 2   # 綠柱擴張（強空）
                else:                            _sc -= 1
            # D4: 近3根K線方向
            if _i >= 2:
                _c0 = float(_bx_close.iloc[_i])
                _c1 = float(_bx_close.iloc[_i-1])
                _c2 = float(_bx_close.iloc[_i-2])
                if _c0 > _c1 > _c2:   _sc += 1
                elif _c0 < _c1 < _c2: _sc -= 1

            _bx_scores.append(_sc)

        # 平滑（3根EMA）
        import pandas as _pd2
        _bx_s = _pd2.Series(_bx_scores)
        _bx_smooth = _bx_s.ewm(span=3, adjust=False).mean()

        # 顏色：深綠/亮綠/深紅/亮紅，4層強度
        _bx_colors = []
        for v in _bx_smooth:
            if   v >= 4:   _bx_colors.append("#00ff88")    # 強多
            elif v >= 1:   _bx_colors.append("#44bb66")    # 弱多
            elif v >= -1:  _bx_colors.append("#886644")    # 中性偏多
            elif v >= -4:  _bx_colors.append("#cc4444")    # 弱空
            else:          _bx_colors.append("#ff2244")    # 強空

        fig.add_trace(go.Bar(
            x=xlabels, y=_bx_smooth,
            marker_color=_bx_colors,
            name="MTF BX", showlegend=True,
            hovertemplate="MTF BX: %{y:.1f}<extra></extra>",
        ), row=4, col=1)

        # 零軸參考線
        fig.add_hline(y=0, line_color="#334455", line_width=1, row=4, col=1)
        # 強度閾值線
        fig.add_hline(y=3,  line_color="#006633", line_width=0.8,
                      line_dash="dot", row=4, col=1)
        fig.add_hline(y=-3, line_color="#660022", line_width=0.8,
                      line_dash="dot", row=4, col=1)

    except Exception as _bx_err:
        pass  # 靜默失敗，不影響主圖

    # ── x 軸刻度標籤：依週期選擇合適格式 ─────────────────────────────────
    # 日K以下用日期+時間，日K及以上只用日期
    intraday_intervals = {"1分鐘","5分鐘","15分鐘","30分鐘"}
    if interval_label in intraday_intervals:
        tick_fmt = "%m/%d %H:%M"
        # 每隔幾根顯示一個刻度，避免密集
        n_ticks  = 8
    else:
        tick_fmt = "%Y/%m/%d"
        n_ticks  = 8

    # 用整數位置作為 x 軸刻度位置（category 模式下 x 軸是 0,1,2,...）
    total   = len(df)
    step    = max(1, total // n_ticks)
    tick_positions = list(range(0, total, step))
    tick_labels    = [df.index[i].strftime(tick_fmt) for i in tick_positions]

    fig.update_layout(
        height=chart_h, template="plotly_dark",
        paper_bgcolor="#0e1117", plot_bgcolor="#111520",
        font=dict(family="Arial, sans-serif", size=10 if compact else 11, color="#ccddee"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
            font=dict(size=leg_sz, color="#ddeeff"),
            bgcolor="rgba(14,17,23,0.85)", bordercolor="#2e3456", borderwidth=1,
            itemsizing="constant",
            traceorder="normal",
        ),
        margin=dict(l=6, r=6, t=36 if compact else 44, b=4),
        xaxis_rangeslider_visible=False,
        xaxis_type="category",
        xaxis2_type="category",
        xaxis3_type="category",
        xaxis4_type="category",
    )

    # 套用自訂刻度到所有 x 軸
    for axis_name in ["xaxis", "xaxis2", "xaxis3", "xaxis4"]:
        fig.update_layout(**{
            axis_name: dict(
                type="category",
                showgrid=True, gridcolor="#1a1e30",
                tickfont=dict(size=9 if compact else 10),
                tickmode="array",
                tickvals=tick_positions,
                ticktext=tick_labels,
                tickangle=-35,
            )
        })

    fig.update_yaxes(showgrid=True, gridcolor="#1a1e30",
                     tickfont=dict(size=9 if compact else 10))

    # ── 盤整區間視覺化（上下邊界橫線 + 半透明填色）──────────────────────────
    try:
        if len(df) >= 15:
            _cz_lookback = min(30, len(df) - 1)
            _cz_window   = df.iloc[-_cz_lookback-1:-1]
            _cz_hi   = float(_cz_window["High"].max())
            _cz_lo   = float(_cz_window["Low"].min())
            _cz_rng  = _cz_hi - _cz_lo
            _cz_atr  = float((df["High"] - df["Low"]).rolling(14).mean().iloc[-2])
            _cz_ratio = _cz_rng / max(_cz_atr, 0.01)
            _cz_std  = float(_cz_window["Close"].std())
            _cz_compressed = _cz_ratio < 1.2 and _cz_std / max(_cz_atr, 0.01) < 0.35

            if _cz_compressed:
                # 上邊界橫線（阻力）
                fig.add_hline(
                    y=_cz_hi, row=1, col=1,
                    line=dict(color="#ffcc44", width=1.5, dash="dot"),
                    annotation_text=f"盤整上界 ${_cz_hi:.2f}",
                    annotation_position="right",
                    annotation_font=dict(color="#ffcc44", size=9),
                )
                # 下邊界橫線（支撐）
                fig.add_hline(
                    y=_cz_lo, row=1, col=1,
                    line=dict(color="#44aaff", width=1.5, dash="dot"),
                    annotation_text=f"盤整下界 ${_cz_lo:.2f}",
                    annotation_position="right",
                    annotation_font=dict(color="#44aaff", size=9),
                )
                # 半透明填色區間
                fig.add_hrect(
                    y0=_cz_lo, y1=_cz_hi,
                    fillcolor="rgba(255,200,50,0.04)",
                    line_width=0, row=1, col=1,
                )
                # 寬度標注
                fig.add_annotation(
                    x=xlabels[-int(len(xlabels)*0.15)],
                    y=(_cz_hi + _cz_lo) / 2,
                    text=f"⟺ 盤整 {_cz_ratio:.1f}×ATR",
                    showarrow=False,
                    font=dict(color="#998833", size=8),
                    bgcolor="rgba(20,15,0,0.7)",
                    bordercolor="#665500",
                    borderwidth=1,
                    borderpad=3,
                    row=1, col=1,
                )
    except Exception:
        pass

    # ── 高置信信號進場箭頭標記（來自 alert_log）────────────────────────────
    # 在K線圖上標記 F6/F7/F8/F9/K18/K19/全EMA排列/R1/R2 等高置信信號
    try:
        HIGH_SIG_BULL = ("F7", "F8", "K18", "全EMA多頭排列", "早晨之星",
                         "R1-量價齊升", "R2-突破前波高", "R1-價跌量縮",
                         "均線聚合後突破", "K12-看漲吞噬", "三白兵",
                         "S3-盤整突破上")
        HIGH_SIG_BEAR = ("F6", "F9", "K19", "全EMA空頭排列", "黃昏之星",
                         "R1-價漲量縮", "R2-跌破前波低",
                         "K13-看跌吞噬", "三黑鴉",
                         "S3-盤整跌破下")

        _log = st.session_state.get("alert_log", [])
        # 只取本圖表 symbol 的日K/週K訊號（避免5分鐘噪音）
        _chart_alerts = [
            e for e in _log
            if e.get("股票") == symbol
            and e.get("週期") == interval_label
        ]

        _annotated = set()
        for _ae in _chart_alerts[-60:]:
            _msg  = _ae.get("訊息", "")
            _atype = _ae.get("類型", "")

            # 判斷是否高置信
            is_bull_sig = any(k in _msg for k in HIGH_SIG_BULL) and _atype == "bull"
            is_bear_sig = any(k in _msg for k in HIGH_SIG_BEAR) and _atype == "bear"
            if not (is_bull_sig or is_bear_sig):
                continue

            # 找對應K線位置（比對日期）
            _atime = _ae.get("時間", "")[:10]   # 取 YYYY-MM-DD
            _match_idx = None
            for _xi, _xlab in enumerate(xlabels):
                if _atime in str(_xlab):
                    _match_idx = _xi
                    break

            if _match_idx is None:
                continue
            _dedup_key = f"{_atime}|{'bull' if is_bull_sig else 'bear'}"
            if _dedup_key in _annotated:
                continue
            _annotated.add(_dedup_key)

            if is_bull_sig:
                _y_val = float(df["Low"].iloc[_match_idx]) * 0.993
                _txt   = "▲"
                _color = "#00ff88"
                _ay    = 28
            else:
                _y_val = float(df["High"].iloc[_match_idx]) * 1.007
                _txt   = "▼"
                _color = "#ff4466"
                _ay    = -28

            fig.add_annotation(
                x=xlabels[_match_idx], y=_y_val,
                text=_txt,
                showarrow=False,
                font=dict(color=_color, size=14 if compact else 16, family="Arial Black"),
                row=1, col=1,
            )
    except Exception:
        pass

    return fig

# ══════════════════════════════════════════════════════════════════════════════
# 多週期摘要列
# ══════════════════════════════════════════════════════════════════════════════
def _render_mtf_confluence(symbol: str, mtf_data: dict):
    """
    多週期共振分析：短週期 + 長週期信號一致時，信號可靠性大幅提升。
    評分系統：每個條件 +1（多頭）或 -1（空頭），綜合判斷方向與強度。
    VIX 作為全市場環境調節器：高恐慌壓制多頭訊號，低恐慌放大多頭訊號。
    """
    if len(mtf_data) < 2:
        return

    # ── 0. 抓取 VIX 盤中即時數據（分鐘級，比日K更即時）────────────────────
    try:
        vix_intra    = fetch_vix_intraday()
        vix_spot     = vix_intra.get("spot") or None
        vix_signal   = vix_intra.get("signal", 0)
        vix_sig_lbl  = vix_intra.get("signal_label", "")
        vix_sig_col  = vix_intra.get("signal_color", "#888888")
        vix_trend_lb = vix_intra.get("trend_label", "→平穩")
        vix_pct      = vix_intra.get("chg_pct_from_prev", 0)
        vix_bar_time = vix_intra.get("last_bar_time", "")
        _vix_err     = vix_intra.get("error")
        # 期限結構用 vix_spot 或 fallback 到 term structure 的 spot
        vix_term     = fetch_vix_term_structure()
        if vix_spot is None:
            vix_spot = vix_term.get("spot") or 20
        panic_type   = vix_term.get("panic_type", "normal")
        vix_struct   = vix_term.get("structure", "unknown")
        vix_ok       = True
    except Exception:
        vix_spot, vix_signal, vix_sig_lbl = 20, 0, ""
        vix_sig_col, vix_trend_lb, vix_pct = "#888888", "", 0
        panic_type, vix_struct = "normal", "unknown"
        vix_ok = False

    # ── VIX 環境調節（直接使用分鐘級信號）──────────────────────────────────
    vix_momentum_score = vix_signal   # 已包含方向，VIX漲=負分，VIX跌=正分
    vix_momentum_label = vix_sig_lbl
    vix_momentum_color = vix_sig_col
    #   暴升 >+15%  → 極度恐慌，強烈看空
    # VIX 水位調節（保持不變）
    if panic_type == "systemic" and vix_spot > 30:
        vix_bull_multiplier = 0.40
        vix_bear_multiplier = 1.50
        vix_label = f"🔴 VIX系統風險 {vix_spot:.1f} Backwardation → 多頭訊號折扣60%"
        vix_color = "#ff4444"
    elif panic_type == "systemic":
        vix_bull_multiplier = 0.60
        vix_bear_multiplier = 1.30
        vix_label = f"🟠 VIX系統風險 {vix_spot:.1f} Backwardation → 多頭訊號折扣40%"
        vix_color = "#ff8844"
    elif vix_spot > 25:
        vix_bull_multiplier = 0.80
        vix_bear_multiplier = 1.15
        vix_label = f"🟡 VIX偏高 {vix_spot:.1f} → 多頭訊號折扣20%"
        vix_color = "#ffcc44"
    elif panic_type == "short_term":
        vix_bull_multiplier = 1.15
        vix_bear_multiplier = 0.85
        vix_label = f"💛 VIX短期恐慌底 {vix_spot:.1f} Contango → 逢低機會，多頭+15%"
        vix_color = "#ffee44"
    elif vix_spot < 15 and vix_struct == "Contango":
        vix_bull_multiplier = 1.20
        vix_bear_multiplier = 0.90
        vix_label = f"🟢 VIX極低 {vix_spot:.1f} Contango → 低恐慌環境，多頭+20%"
        vix_color = "#00cc88"
    elif vix_spot < 20:
        vix_bull_multiplier = 1.10
        vix_bear_multiplier = 0.95
        vix_label = f"🟢 VIX正常 {vix_spot:.1f} → 市場平靜，訊號正常"
        vix_color = "#44aa77"
    else:
        vix_bull_multiplier = 1.0
        vix_bear_multiplier = 1.0
        vix_label = f"⚪ VIX {vix_spot:.1f} → 中性環境"
        vix_color = "#667788"

    # ── 1. 計算每個週期的多/空傾向分數 ──────────────────────────────────────
    weight_map = {"1m": 1, "5m": 2, "15m": 3, "30m": 4,
                  "1d": 6, "1wk": 8, "1mo": 10}

    bull_score = 0
    bear_score = 0
    total_weight = 0
    period_signals = []

    for itvl, d in mtf_data.items():
        w = weight_map.get(itvl, 2)
        total_weight += w

        s = 0
        reasons = []
        if d["trend"] == "多頭":    s += 2; reasons.append("多頭排列")
        elif d["trend"] == "空頭":  s -= 2; reasons.append("空頭排列")
        if d["dif"] > d["dea"]:     s += 1; reasons.append("MACD多方")
        else:                        s -= 1; reasons.append("MACD空方")
        if d["dif"] > d["dea"] and d["dif_prev"] <= d["dea_prev"]:
            s += 2; reasons.append("剛金叉✨")
        elif d["dif"] < d["dea"] and d["dif_prev"] >= d["dea_prev"]:
            s -= 2; reasons.append("剛死叉💀")
        if d["ema5"] > d["ema20"]:  s += 1; reasons.append("短均多頭")
        else:                        s -= 1; reasons.append("短均空頭")

        # 套用 VIX 調節到各週期分數
        s_adj = s * vix_bull_multiplier if s > 0 else s * vix_bear_multiplier
        bull_score += max(0,  s_adj) * w
        bear_score += max(0, -s_adj) * w
        period_signals.append({
            "itvl": itvl, "label": d["label"],
            "score": s, "score_adj": s_adj, "w": w, "reasons": reasons
        })

    # ── 2. 共振強度計算（含 VIX 調節）──────────────────────────────────────
    max_possible = total_weight * 5 * max(vix_bull_multiplier, vix_bear_multiplier)
    bull_pct = bull_score / max_possible * 100 if max_possible else 0
    bear_pct = bear_score / max_possible * 100 if max_possible else 0
    net_pct  = bull_pct - bear_pct

    # VIX 動量作為獨立加減項（±4~±8 分，相當於一個強週期訊號）
    # 直接加到 net_pct（每 1 分 ≈ 5% 影響）
    vix_momentum_contribution = vix_momentum_score * 5
    net_pct_raw    = net_pct   # 保留未調整值供顯示
    net_pct       += vix_momentum_contribution

    bull_periods   = sum(1 for p in period_signals if p["score"] > 0)
    bear_periods   = sum(1 for p in period_signals if p["score"] < 0)
    total_periods  = len(period_signals)
    consensus_ratio = max(bull_periods, bear_periods) / total_periods if total_periods else 0

    if net_pct > 25 and consensus_ratio >= 0.75:
        confluence_label = "🚀 強烈多頭共振"
        bar_color = "#00ff88"
        bg_color  = "rgba(0,60,30,0.5)"
        direction = "LONG"
    elif net_pct > 10 and consensus_ratio >= 0.6:
        confluence_label = "📈 多頭偏向"
        bar_color = "#44cc88"
        bg_color  = "rgba(0,40,20,0.4)"
        direction = "偏多"
    elif net_pct < -25 and consensus_ratio >= 0.75:
        confluence_label = "💀 強烈空頭共振"
        bar_color = "#ff4444"
        bg_color  = "rgba(60,0,0,0.5)"
        direction = "SHORT"
    elif net_pct < -10 and consensus_ratio >= 0.6:
        confluence_label = "📉 空頭偏向"
        bar_color = "#cc4444"
        bg_color  = "rgba(40,0,0,0.4)"
        direction = "偏空"
    else:
        confluence_label = "⚖️ 多空分歧，觀望"
        bar_color = "#888888"
        bg_color  = "rgba(30,30,30,0.4)"
        direction = "中性"

    # ── 3. 短週期 vs 長週期背離偵測 ──────────────────────────────────────
    divergence_msg = ""
    itvl_keys = list(mtf_data.keys())
    if len(itvl_keys) >= 2:
        short_itvl = itvl_keys[0]   # 最短週期（如 1m）
        long_itvl  = itvl_keys[-1]  # 最長週期（如 30m）
        short_score = next(p["score"] for p in period_signals if p["itvl"] == short_itvl)
        long_score  = next(p["score"] for p in period_signals if p["itvl"] == long_itvl)
        short_label = mtf_data[short_itvl]["label"]
        long_label  = mtf_data[long_itvl]["label"]
        if short_score > 1 and long_score < -1:
            divergence_msg = f"⚠️ 背離警告：{short_label} 偏多 但 {long_label} 偏空 → 短多不可靠，等長週期轉向"
        elif short_score < -1 and long_score > 1:
            divergence_msg = f"💡 反彈機會：{short_label} 偏空 但 {long_label} 偏多 → 短空可能是回調，長線仍多"

    # ── 4. 渲染共振面板 ────────────────────────────────────────────────────
    bar_w  = min(100, abs(net_pct) * 2)

    # VIX 壓力條（獨立顯示，視覺化調節幅度）
    vix_bar_w = min(100, vix_spot * 2.5)   # VIX 40 → 100%
    vix_adj_pct = abs(vix_bull_multiplier - 1.0) * 100
    vix_adj_sign = "+" if vix_bull_multiplier > 1 else "-"
    vix_adj_str = f"{vix_adj_sign}{vix_adj_pct:.0f}% 多頭" if vix_bull_multiplier != 1.0 else "中性"

    rows_html = ""
    for p in period_signals:
        _s    = p["score"]
        _sadj = p.get("score_adj", _s)
        _col  = "#00cc66" if _s > 0 else ("#ff4444" if _s < 0 else "#888888")
        _icon = "▲" if _s > 2 else ("△" if _s > 0 else ("▼" if _s < -2 else ("▽" if _s < 0 else "◆")))
        _reasons = " · ".join(p["reasons"][:3])
        # 若VIX調節改變了分數方向，顯示警告
        _adj_note = ""
        if vix_bull_multiplier != 1.0 and _s > 0:
            _adj_note = f' <span style="color:{vix_color};font-size:0.65rem;">×{vix_bull_multiplier:.2f}</span>'
        rows_html += (
            f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0;border-bottom:1px solid #1a2535;">'
            f'  <span style="color:#6688aa;min-width:38px;font-size:0.78rem;">{p["label"]}</span>'
            f'  <span style="color:{_col};font-weight:700;min-width:20px;">{_icon}</span>'
            f'  <div style="flex:1;background:#0d1520;border-radius:3px;height:5px;">'
            f'    <div style="width:{min(100,abs(_s)*20)}%;height:100%;background:{_col};border-radius:3px;"></div>'
            f'  </div>'
            f'  <span style="color:#445566;font-size:0.7rem;min-width:140px;">{_reasons}</span>'
            f'  {_adj_note}'
            f'</div>'
        )

    div_html = (
        f'<div style="background:#0d1a2d;border:1px solid #1e3050;border-radius:8px;padding:12px 16px;margin:10px 0;">'
        # 標題列
        f'  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">'
        f'    <span style="font-weight:700;font-size:1rem;color:#cce8ff;">🔗 多週期共振分析</span>'
        f'    <span style="background:{bar_color}22;border:1px solid {bar_color}55;'
        f'          color:{bar_color};padding:3px 10px;border-radius:12px;font-weight:700;">'
        f'      {confluence_label}</span>'
        f'  </div>'
        # VIX 盤中即時動量列
        f'  <div style="background:#0a1525;border:1px solid {vix_momentum_color}44;border-radius:6px;'
        f'       padding:6px 10px;margin-bottom:6px;display:flex;align-items:center;gap:10px;">'
        f'    <span style="color:{vix_momentum_color};font-size:0.75rem;font-weight:700;min-width:60px;">'
        f'      📡 VIX即時</span>'
        f'    <span style="color:{vix_momentum_color};font-size:0.82rem;font-weight:700;">'
        f'      {vix_spot:.2f}　{vix_trend_lb}　{vix_pct:+.1f}%</span>'
        f'    <span style="color:{vix_momentum_color};font-size:0.78rem;flex:1;">'
        f'      　{vix_momentum_label}</span>'
        f'    <span style="color:#334455;font-size:0.68rem;">更新:{vix_bar_time}</span>'
        f'  </div>'
        # VIX 期限結構環境列
        f'  <div style="background:#0a1525;border:1px solid {vix_color}44;border-radius:6px;'
        f'       padding:6px 10px;margin-bottom:10px;display:flex;align-items:center;gap:10px;">'
        f'    <span style="color:{vix_color};font-size:0.75rem;font-weight:700;min-width:60px;">'
        f'      📊 VIX環境</span>'
        f'    <div style="flex:1;background:#0d1520;border-radius:3px;height:6px;">'
        f'      <div style="width:{vix_bar_w:.0f}%;height:100%;background:linear-gradient(90deg,#44aa77,#ffcc44,#ff4444);'
        f'           border-radius:3px;"></div>'
        f'      <div style="width:2px;height:10px;background:#fff3;position:relative;'
        f'           margin-top:-8px;left:{min(98,vix_bar_w):.0f}%;"></div>'
        f'    </div>'
        f'    <span style="color:{vix_color};font-size:0.78rem;min-width:260px;">'
        f'      {vix_label}　<span style="color:#667788;">({vix_adj_str})</span></span>'
        f'  </div>'
        # 多空強度條
        f'  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
        f'    <span style="color:#445566;font-size:0.75rem;">空頭</span>'
        f'    <div style="flex:1;background:#0d1520;border-radius:4px;height:8px;position:relative;">'
        f'      <div style="width:{bar_w/2}%;height:100%;background:{bar_color};border-radius:4px;'
        f'           position:absolute;{"left:50%" if net_pct>=0 else f"left:{50-bar_w/2}%"};"></div>'
        f'      <div style="width:1px;height:100%;background:#445566;position:absolute;left:50%;"></div>'
        f'    </div>'
        f'    <span style="color:#445566;font-size:0.75rem;">多頭</span>'
        f'    <span style="color:{bar_color};font-weight:700;min-width:60px;text-align:right;">'
        f'      {direction} {abs(net_pct):.0f}%</span>'
        f'  </div>'
        f'  {rows_html}'
        f'  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">'
        f'    <span style="color:#445566;font-size:0.75rem;">空頭</span>'
        f'    <div style="flex:1;background:#0d1520;border-radius:4px;height:8px;position:relative;">'
        f'      <div style="width:50%;height:100%;background:#1e2e40;position:absolute;left:0;"></div>'
        f'      <div style="width:{bar_w/2}%;height:100%;background:{bar_color};border-radius:4px;'
        f'           position:absolute;{"left:50%" if net_pct>=0 else f"left:{50-bar_w/2}%"};"></div>'
        f'      <div style="width:1px;height:100%;background:#445566;position:absolute;left:50%;"></div>'
        f'    </div>'
        f'    <span style="color:#445566;font-size:0.75rem;">多頭</span>'
        f'    <span style="color:{bar_color};font-weight:700;min-width:60px;text-align:right;">'
        f'      {direction} {abs(net_pct):.0f}%</span>'
        f'  </div>'
        f'  {rows_html}'
        + (f'  <div style="margin-top:8px;padding:6px 10px;background:#1a2030;border-radius:5px;'
           f'       color:#ffaa44;font-size:0.8rem;">{divergence_msg}</div>' if divergence_msg else '')
        + f'</div>'
    )
    st.markdown(f'<div id="mtf-confluence-{symbol}">{div_html}</div>',
    unsafe_allow_html=True)


def render_mtf_summary(symbol, selected_intervals, show_alerts, prepost=False):
    st.markdown(f'<div class="mtf-section-title">🔀 多週期總覽 — {symbol}</div>',
    unsafe_allow_html=True)
    rows    = []
    mtf_data = {}   # {itvl: {"df": df, "label": label, "trend": trend, ...}}
    for itvl in selected_intervals:
        label, _ = INTERVAL_MAP[itvl]
        df = fetch_data(symbol, itvl, prepost=prepost)
        if df.empty:
            rows.append(
                f'<div class="mtf-header"><span class="mtf-period">{label}</span>'
                f'<span style="color:#555">數據載入失敗</span></div>')
            continue

        if show_alerts:
            run_alerts(symbol, label, df)

        close   = df["Close"]
        last    = float(close.iloc[-1])
        prev    = float(close.iloc[-2]) if len(close) > 1 else last
        chg     = last - prev
        pct     = chg / prev * 100 if prev else 0
        hi      = float(df["High"].iloc[-1])
        lo      = float(df["Low"].iloc[-1])
        vol_k   = int(df["Volume"].iloc[-1]) // 10000

        chg_cls   = "mtf-chg-up" if chg >= 0 else "mtf-chg-dn"
        chg_arrow = "▲" if chg >= 0 else "▼"

        trend     = detect_trend(df)
        t_cls     = {"多頭":"mtf-trend-bull","空頭":"mtf-trend-bear","盤整":"mtf-trend-side"}[trend]
        t_icon    = {"多頭":"▲","空頭":"▼","盤整":"◆"}[trend]

        macd_s    = get_macd_signal(df)
        macd_cls  = "mtf-macd-bull" if any(x in macd_s for x in ["金叉","↑"]) else "mtf-macd-bear"

        ema_s     = get_ema_signal(df)
        ema_cls   = "mtf-ema-bull" if any(x in ema_s for x in ["↑","多"]) else "mtf-ema-bear"

        # EMA 聚合壓縮度
        _ema_ns = [5, 10, 20, 30, 60]
        _ema_vs = [float(calc_ema(df["Close"], n).iloc[-1]) for n in _ema_ns]
        _mean_v = sum(_ema_vs) / len(_ema_vs)
        _compress = (max(_ema_vs) - min(_ema_vs)) / _mean_v * 100 if _mean_v else 999
        if _compress < 0.15:
            compress_tag = f'<span style="color:#ff9900;font-weight:700;animation:blink 1s infinite;">⚡聚合{_compress:.2f}%</span>'
        elif _compress < 0.40:
            compress_tag = f'<span style="color:#ffcc00;">🔶聚合{_compress:.2f}%</span>'
        elif _compress < 0.80:
            compress_tag = f'<span style="color:#88aacc;">收縮{_compress:.2f}%</span>'
        else:
            compress_tag = f'<span style="color:#445566;">分散{_compress:.2f}%</span>'

        # 收集多週期數據供共振分析
        _dif, _dea, _ = calc_macd(df["Close"])
        mtf_data[itvl] = {
            "label":    label,
            "df":       df,
            "trend":    trend,
            "macd_s":   macd_s,
            "dif":      float(_dif.iloc[-1]),
            "dea":      float(_dea.iloc[-1]),
            "dif_prev": float(_dif.iloc[-2]) if len(_dif) > 1 else float(_dif.iloc[-1]),
            "dea_prev": float(_dea.iloc[-2]) if len(_dea) > 1 else float(_dea.iloc[-1]),
            "close":    float(df["Close"].iloc[-1]),
            "compress": _compress,
            "ema5":     _ema_vs[0],
            "ema20":    float(calc_ema(df["Close"], 20).iloc[-1]),
            "ema60":    float(calc_ema(df["Close"], 60).iloc[-1]),
        }

        rows.append(
            f'<div class="mtf-header">'
            f'  <span class="mtf-period">{label}</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="mtf-price">${last:.2f}</span>'
            f'  <span class="{chg_cls}">{chg_arrow} {chg:+.2f} ({pct:+.2f}%)</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span style="color:#6688aa;font-size:0.82rem">H:{hi:.2f}　L:{lo:.2f}　量:{vol_k}萬</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="{t_cls}">{t_icon} {trend}</span>'
            f'  <div class="mtf-divider"></div>'
            f'  <span class="{macd_cls}">MACD: {macd_s}</span>'
            f'  <span class="{ema_cls}">EMA: {ema_s}</span>'
            f'  <div class="mtf-divider"></div>'
            f'  {compress_tag}'
            f'</div>'
        )
    st.markdown(f'<div id="mtf-rows-{symbol}">{"".join(rows)}</div>',
    unsafe_allow_html=True)

    # ── 多週期共振分析（跨週期連動預測）────────────────────────────────────
    if len(mtf_data) >= 2:
        _render_mtf_confluence(symbol, mtf_data)

# ══════════════════════════════════════════════════════════════════════════════
# 多週期 K 線圖
# ══════════════════════════════════════════════════════════════════════════════
def render_mtf_charts(symbol, selected_intervals, layout_mode, max_bars=90, prepost=False):
    if not selected_intervals:
        st.info("請至少選擇一個時間週期")
        return
    st.markdown(f'<div class="mtf-section-title">📊 多週期 K 線圖 — {symbol}</div>',
    unsafe_allow_html=True)

    if layout_mode == "並排（2欄）":
        pairs = [selected_intervals[i:i+2] for i in range(0, len(selected_intervals), 2)]
        for pair in pairs:
            cols = st.columns(len(pair))
            for col, itvl in zip(cols, pair):
                label, _ = INTERVAL_MAP[itvl]
                df = fetch_data(symbol, itvl, prepost=prepost)
                with col:
                    if df.empty:
                        st.error(f"{label} 無數據")
                    else:
                        fig = build_chart(symbol, df, label, compact=True, max_bars=max_bars)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True,
                                            config={"displayModeBar": False},
                                            key=f"mtf_{symbol}_{itvl}")
    else:
        for itvl in selected_intervals:
            label, _ = INTERVAL_MAP[itvl]
            df = fetch_data(symbol, itvl, prepost=prepost)
            if df.empty:
                st.error(f"{label} 無數據")
            else:
                fig = build_chart(symbol, df, label, compact=False, max_bars=max_bars)
                if fig:
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": True},
                                    key=f"mtf_{symbol}_{itvl}_full")

# ══════════════════════════════════════════════════════════════════════════════
# 單週期渲染
# ══════════════════════════════════════════════════════════════════════════════
def render_traffic_light(symbol: str, df, last: float, trend: str, interval: str):
    """
    🚦 交通燈 + 一鍵指令面板
    最頂部顯示：🟢做多 / 🔴做空 / 🟡觀望
    點進去才看詳細
    """
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]
    vol   = df["Volume"]

    # ── 計算交通燈分數 ─────────────────────────────────────────────────────
    score = 0   # 正=多頭，負=空頭

    # 1. EMA排列（最重要）
    ema_vals = [float(close.ewm(span=n, adjust=False).mean().iloc[-1])
                for n in [5, 10, 20, 60, 120, 200]]
    if all(ema_vals[i] > ema_vals[i+1] for i in range(len(ema_vals)-1)):
        score += 3   # 全多頭排列
    elif ema_vals[0] > ema_vals[2] > ema_vals[4]:
        score += 2   # 部分多頭
    elif all(ema_vals[i] < ema_vals[i+1] for i in range(len(ema_vals)-1)):
        score -= 3   # 全空頭排列
    elif ema_vals[0] < ema_vals[2] < ema_vals[4]:
        score -= 2

    # 2. MACD方向
    dif = close.ewm(span=12).mean() - close.ewm(span=26).mean()
    dea = dif.ewm(span=9).mean()
    if float(dif.iloc[-1]) > float(dea.iloc[-1]):
        score += 1
        if float(dif.iloc[-1]) > float(dif.iloc[-2]):
            score += 1   # DIF上升中
    else:
        score -= 1
        if float(dif.iloc[-1]) < float(dif.iloc[-2]):
            score -= 1

    # 3. RSI位置
    delta = close.diff()
    gain  = delta.where(delta > 0, 0).rolling(14).mean()
    loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi   = 100 - 100 / (1 + gain / loss.replace(0, 1e-9))
    rsi_v = float(rsi.iloc[-1])
    if rsi_v >= 55:   score += 1
    elif rsi_v <= 45: score -= 1
    if rsi_v <= 30:   score += 2   # 超賣反彈機會
    if rsi_v >= 70:   score -= 1   # 超買警惕

    # 4. 價格 vs EMA20
    e20 = float(close.ewm(span=20).mean().iloc[-1])
    if last > e20 * 1.005:  score += 1
    elif last < e20 * 0.995: score -= 1

    # 5. 盤整壓縮偵測（中性加權）
    if len(df) >= 15:
        _w = df.iloc[-16:-1]
        _rng = float(_w["High"].max()) - float(_w["Low"].min())
        _atr = float((high - low).rolling(14).mean().iloc[-1])
        _compressed = _rng / max(_atr, 0.01) < 1.2
    else:
        _compressed = False

    # ── 方向判定 ──────────────────────────────────────────────────────────
    if score >= 4:
        light = "🟢"; action = "做多"; light_color = "#00ee66"
        light_bg = "#001a08"; light_border = "#004422"
        confidence = min(95, 60 + score * 5)
    elif score >= 2:
        light = "🟢"; action = "偏多"; light_color = "#44cc66"
        light_bg = "#001208"; light_border = "#003322"
        confidence = min(80, 50 + score * 5)
    elif score <= -4:
        light = "🔴"; action = "做空"; light_color = "#ff4455"
        light_bg = "#1a0008"; light_border = "#440011"
        confidence = min(95, 60 + abs(score) * 5)
    elif score <= -2:
        light = "🔴"; action = "偏空"; light_color = "#cc4466"
        light_bg = "#120008"; light_border = "#330011"
        confidence = min(80, 50 + abs(score) * 5)
    else:
        light = "🟡"; action = "觀望"; light_color = "#ffcc44"
        light_bg = "#1a1400"; light_border = "#443300"
        confidence = 40

    # ── 計算進場/止損/目標 ─────────────────────────────────────────────────
    atr_val = float((high - low).rolling(14).mean().iloc[-1])
    if action in ("做多", "偏多"):
        entry  = round(last, 2)
        sl     = round(last - atr_val * 1.5, 2)
        tp1    = round(last + atr_val * 2.0, 2)
        tp2    = round(last + atr_val * 4.0, 2)
        rr     = round(atr_val * 2.0 / max(atr_val * 1.5, 0.01), 1)
    elif action in ("做空", "偏空"):
        entry  = round(last, 2)
        sl     = round(last + atr_val * 1.5, 2)
        tp1    = round(last - atr_val * 2.0, 2)
        tp2    = round(last - atr_val * 4.0, 2)
        rr     = round(atr_val * 2.0 / max(atr_val * 1.5, 0.01), 1)
    else:
        entry = sl = tp1 = tp2 = rr = None

    # ── 壓縮區間提示 ───────────────────────────────────────────────────────
    compress_note = "🔲 均線壓縮中，等待方向突破" if _compressed else ""

    # ── 主卡片 HTML ────────────────────────────────────────────────────────
    # 信心條
    bar_w   = confidence
    bar_col = light_color

    card = (
        f'<div style="background:{light_bg};border:2px solid {light_border};'
        f'border-radius:16px;padding:18px 22px;margin-bottom:16px;">'

        # 頂行：交通燈 + 股票 + 動作
        f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
        f'<span style="font-size:2.8rem;line-height:1;">{light}</span>'
        f'<div>'
        f'<div style="color:#ccddee;font-size:0.75rem;margin-bottom:2px;">${symbol} · {interval}</div>'
        f'<div style="color:{light_color};font-weight:900;font-size:1.6rem;'
        f'font-family:monospace;letter-spacing:2px;">{action}</div>'
        f'</div>'
        f'<div style="margin-left:auto;text-align:right;">'
        f'<div style="color:#445566;font-size:0.68rem;margin-bottom:4px;">信心度</div>'
        f'<div style="color:{light_color};font-weight:800;font-size:1.3rem;">{confidence}%</div>'
        f'</div></div>'

        # 信心條
        f'<div style="background:#0a0c10;border-radius:6px;height:6px;'
        f'margin-bottom:14px;overflow:hidden;">'
        f'<div style="width:{bar_w}%;height:6px;border-radius:6px;'
        f'background:linear-gradient(90deg,{bar_col}88,{bar_col});"></div></div>'
    )

    # 進場指令區
    if entry and action != "觀望":
        sl_pct  = abs(entry - sl) / entry * 100
        tp1_pct = abs(tp1  - entry) / entry * 100
        card += (
            f'<div style="display:grid;grid-template-columns:repeat(4,1fr);'
            f'gap:10px;margin-bottom:12px;">'

            f'<div style="background:#0a1018;border-radius:8px;padding:10px;text-align:center;">'
            f'<div style="color:#445566;font-size:0.65rem;margin-bottom:4px;">進場價</div>'
            f'<div style="color:#aabbff;font-weight:700;font-size:1.0rem;">${entry:.2f}</div>'
            f'</div>'

            f'<div style="background:#1a0808;border-radius:8px;padding:10px;text-align:center;">'
            f'<div style="color:#445566;font-size:0.65rem;margin-bottom:4px;">止損</div>'
            f'<div style="color:#ff5566;font-weight:700;font-size:1.0rem;">${sl:.2f}</div>'
            f'<div style="color:#663333;font-size:0.62rem;">-{sl_pct:.1f}%</div>'
            f'</div>'

            f'<div style="background:#081a08;border-radius:8px;padding:10px;text-align:center;">'
            f'<div style="color:#445566;font-size:0.65rem;margin-bottom:4px;">目標①</div>'
            f'<div style="color:#44ee66;font-weight:700;font-size:1.0rem;">${tp1:.2f}</div>'
            f'<div style="color:#336633;font-size:0.62rem;">+{tp1_pct:.1f}%</div>'
            f'</div>'

            f'<div style="background:#081a08;border-radius:8px;padding:10px;text-align:center;">'
            f'<div style="color:#445566;font-size:0.65rem;margin-bottom:4px;">目標②</div>'
            f'<div style="color:#00ffaa;font-weight:700;font-size:1.0rem;">${tp2:.2f}</div>'
            f'<div style="color:#336633;font-size:0.62rem;">R:R {rr:.1f}x</div>'
            f'</div>'
            f'</div>'
        )
    elif action == "觀望":
        card += (
            f'<div style="background:#0a0c08;border-radius:8px;padding:12px;'
            f'margin-bottom:12px;text-align:center;">'
            f'<div style="color:#667788;font-size:0.85rem;">'
            f'⌛ 多空信號互相抵消，等待明確方向後再進場</div>'
            f'</div>'
        )

    # 壓縮提示
    if compress_note:
        card += (
            f'<div style="background:#141000;border:1px solid #443300;'
            f'border-radius:6px;padding:8px 12px;margin-bottom:10px;">'
            f'<span style="color:#ffcc44;font-size:0.75rem;">{compress_note}</span>'
            f'<span style="color:#665500;font-size:0.7rem;margin-left:8px;">'
            f'突破上邊界→追多｜跌破下邊界→追空</span>'
            f'</div>'
        )

    # 評分細節（可展開）
    score_detail = (
        f'EMA排列{"✅" if score > 0 else "❌"}  '
        f'MACD{"✅" if float(dif.iloc[-1])>float(dea.iloc[-1]) else "❌"}  '
        f'RSI={rsi_v:.0f}{"⚠️超買" if rsi_v>=70 else "⚠️超賣" if rsi_v<=30 else ""}  '
        f'ATR={atr_val:.2f}  綜合分={score:+d}'
    )
    card += (
        f'<div style="color:#334455;font-size:0.65rem;padding-top:8px;'
        f'border-top:1px solid #1a2030;">{score_detail}</div>'
        f'</div>'
    )

    st.markdown(card, unsafe_allow_html=True)
    return action, entry, sl, tp1, tp2, confidence


def render_daily_briefing(symbols: list):
    """
    📋 每日操作簡報
    開盤前自動生成所有股票的今日計劃
    """
    import pytz as _ptz
    _et  = _ptz.timezone("America/New_York")
    _now = datetime.now(_et)
    _is_premarket = _now.hour < 9 or (_now.hour == 9 and _now.minute < 30)

    st.markdown(
        f'<div style="background:#07090f;border:1px solid #1e2e48;'
        f'border-radius:14px;padding:16px 20px;margin-bottom:16px;">'
        f'<div style="font-size:0.78rem;font-weight:700;color:#445577;'
        f'letter-spacing:1px;margin-bottom:4px;">'
        f'📋 今日操作簡報 · {_now.strftime("%m/%d")} ET</div>'
        f'<div style="font-size:0.65rem;color:#334455;margin-bottom:12px;">'
        f'{"🌅 開盤前評估" if _is_premarket else "📊 盤中更新"}</div>',
        unsafe_allow_html=True)

    rows = []
    for sym in symbols[:8]:   # 最多8個
        try:
            _df = fetch_data(sym, "1d")
            if _df.empty or len(_df) < 5:
                continue
            _c    = _df["Close"]
            _last = float(_c.iloc[-1])
            _atr  = float((_df["High"] - _df["Low"]).rolling(14).mean().iloc[-1])
            # 快速評分
            _e5   = float(_c.ewm(span=5).mean().iloc[-1])
            _e20  = float(_c.ewm(span=20).mean().iloc[-1])
            _e60  = float(_c.ewm(span=60).mean().iloc[-1])
            _dif  = float((_c.ewm(span=12).mean() - _c.ewm(span=26).mean()).iloc[-1])
            _dea  = float((_c.ewm(span=12).mean() - _c.ewm(span=26).mean()).ewm(span=9).mean().iloc[-1])

            _sc = 0
            if _e5 > _e20 > _e60:   _sc += 2
            elif _e5 < _e20 < _e60: _sc -= 2
            if _dif > _dea: _sc += 1
            else:           _sc -= 1
            if _last > _e20 * 1.005: _sc += 1
            elif _last < _e20 * 0.995: _sc -= 1

            if _sc >= 3:
                _light = "🟢"; _act = "做多"
                _lc    = "#00ee66"
                _sl    = round(_last - _atr * 1.5, 2)
                _tp    = round(_last + _atr * 2.0, 2)
            elif _sc <= -3:
                _light = "🔴"; _act = "做空"
                _lc    = "#ff5566"
                _sl    = round(_last + _atr * 1.5, 2)
                _tp    = round(_last - _atr * 2.0, 2)
            else:
                _light = "🟡"; _act = "觀望"
                _lc    = "#ffcc44"
                _sl    = _tp = None

            rows.append({
                "sym": sym, "last": _last, "light": _light,
                "act": _act, "lc": _lc, "sl": _sl, "tp": _tp,
                "atr": _atr, "sc": _sc
            })
        except Exception:
            continue

    if not rows:
        st.markdown('<div style="color:#445566;font-size:0.8rem;">暫無數據</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # 表格渲染
    tbl = (
        '<table style="width:100%;border-collapse:collapse;font-size:0.78rem;">'
        '<tr style="color:#334455;border-bottom:1px solid #1a2030;">'
        '<th style="text-align:left;padding:4px 8px;">股票</th>'
        '<th style="padding:4px 8px;">方向</th>'
        '<th style="padding:4px 8px;">現價</th>'
        '<th style="padding:4px 8px;">止損</th>'
        '<th style="padding:4px 8px;">目標</th>'
        '<th style="padding:4px 8px;">ATR</th>'
        '<th style="padding:4px 8px;">評分</th>'
        '</tr>'
    )
    for r in rows:
        _sl_str = f'${r["sl"]:.2f}' if r["sl"] else '—'
        _tp_str = f'${r["tp"]:.2f}' if r["tp"] else '—'
        tbl += (
            f'<tr style="border-bottom:1px solid #0e1520;">'
            f'<td style="padding:6px 8px;color:#aabbcc;font-weight:700;">${r["sym"]}</td>'
            f'<td style="padding:6px 8px;text-align:center;">'
            f'<span style="background:{r["lc"]}22;color:{r["lc"]};'
            f'border-radius:10px;padding:2px 10px;font-weight:700;">'
            f'{r["light"]} {r["act"]}</span></td>'
            f'<td style="padding:6px 8px;text-align:center;color:#778899;">${r["last"]:.2f}</td>'
            f'<td style="padding:6px 8px;text-align:center;color:#ff5566;">{_sl_str}</td>'
            f'<td style="padding:6px 8px;text-align:center;color:#44ee66;">{_tp_str}</td>'
            f'<td style="padding:6px 8px;text-align:center;color:#445566;">${r["atr"]:.2f}</td>'
            f'<td style="padding:6px 8px;text-align:center;'
            f'color:{"#00ee66" if r["sc"]>0 else "#ff5566" if r["sc"]<0 else "#ffcc44"};">'
            f'{r["sc"]:+d}</td>'
            f'</tr>'
        )
    tbl += '</table>'
    st.markdown(tbl, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_single(symbol, interval, show_alerts, max_bars=90, show_pre=False, show_post=False, show_night=False):
    label, _ = INTERVAL_MAP[interval]
    _prepost = show_pre or show_post or show_night
    with st.spinner(f"載入 {symbol} {label} 數據中..."):
        df = fetch_data(symbol, interval, prepost=_prepost)

    if df.empty:
        st.error(f"❌ 無法取得 {symbol} 數據")
        return

    close   = df["Close"]
    last    = float(close.iloc[-1])
    prev    = float(close.iloc[-2]) if len(close) > 1 else last
    chg     = last - prev
    pct     = chg / prev * 100 if prev else 0
    vol_now = int(df["Volume"].iloc[-1])
    trend   = detect_trend(df)

    # 判斷最新數據時間和時段
    try:
        import pytz as _ptz
        _et = _ptz.timezone("America/New_York")
        _last_ts = df.index[-1]
        if _last_ts.tzinfo is None:
            _last_ts = _last_ts.tz_localize("UTC").tz_convert(_et)
        else:
            _last_ts = _last_ts.tz_convert(_et)
        _h, _m = _last_ts.hour, _last_ts.minute
        if (_h > 9 or (_h == 9 and _m >= 30)) and _h < 16:
            _session_label = "🟢 正規盤中"
            _session_color = "#00cc44"
        elif _h >= 4 and (_h < 9 or (_h == 9 and _m < 30)):
            _session_label = "🔵 盤前"
            _session_color = "#3399ff"
        elif _h >= 16 and _h < 20:
            _session_label = "🟡 盤後"
            _session_color = "#ffcc00"
        else:
            _session_label = "🌙 夜盤"
            _session_color = "#aa88ff"
        _data_time_str = _last_ts.strftime("%m/%d %H:%M ET")
    except Exception:
        _session_label = ""
        _session_color = "#888888"
        _data_time_str = ""

    # ── 🚦 交通燈指令面板（最頂部，用戶第一眼看到）──────────────────────────
    render_traffic_light(symbol, df, last, trend, label)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("最新價格",      f"${last:.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
    c2.metric("成交量（萬股）", f"{vol_now/10000:.1f}")
    c3.metric("本K最高",       f"${df['High'].iloc[-1]:.2f}")
    c4.metric("本K最低",       f"${df['Low'].iloc[-1]:.2f}")
    t_cls  = {"多頭":"trend-bull","空頭":"trend-bear","盤整":"trend-side"}[trend]
    t_icon = {"多頭":"▲","空頭":"▼","盤整":"◆"}[trend]
    with c5:
        st.markdown(
            f'<div class="trend-card"><div class="trend-title">趨勢判斷</div>'
            f'<div class="{t_cls}">{t_icon} {trend}</div>'
            f'<div style="font-size:0.68rem;color:{_session_color};margin-top:3px;">'
            f'{_session_label}</div>'
            f'<div style="font-size:0.62rem;color:#445566;">{_data_time_str}</div>'
            f'</div>',
    unsafe_allow_html=True)

    # 如果數據時間超過 15 分鐘，提示用戶刷新
    try:
        from datetime import datetime as _dtnow, timezone as _tz
        _now_et = datetime.now(_ptz.timezone("America/New_York"))
        _age_min = (_now_et - _last_ts).total_seconds() / 60
        if _age_min > 15 and _prepost:
            col_warn, col_btn = st.columns([3, 1])
            with col_warn:
                st.warning(f"⚠️ 數據時間：{_data_time_str}（{_age_min:.0f} 分鐘前），可能非最新盤前數據")
            with col_btn:
                if st.button("🔄 強制刷新", key=f"force_refresh_{symbol}_{interval}"):
                    st.cache_data.clear()
                    st.rerun()
    except Exception:
        pass

    # EMA 列
    items = []
    for n, color in EMA_CONFIGS:
        val   = float(calc_ema(close,n).iloc[-1])
        arrow = "↑" if last > val else "↓"
        items.append(
            f'<span class="ema-item" style="color:{color}">'
            f'<span class="ema-label">EMA{n} </span>{val:.2f}'
            f'<span style="font-size:0.72rem;opacity:0.6"> {arrow}</span></span>')
    st.markdown('<div class="ema-bar">' + "".join(items) + '</div>',
    unsafe_allow_html=True)

    # 若有任何延長時段開啟，取得 Yahoo Finance 延長時段數據傳給 build_chart
    _ext_for_chart = None
    if show_pre or show_post or show_night:
        _ext_for_chart = fetch_extended_data(symbol)

    fig = build_chart(symbol, df, label, max_bars=max_bars, ext_data=_ext_for_chart)
    if fig:
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": True},
                        key=f"single_{symbol}_{interval}")

    if show_alerts:
        mkt_data = fetch_market_data() if show_market else {}
        run_alerts(symbol, label, df,
                   trigger_ai=show_ai, mkt=mkt_data)

    # ── AI 技術分析面板 ─────────────────────────────────────────────────────
    if show_ai:
        mkt = fetch_market_data() if show_market else {}
        st.markdown("---")
        render_ai_analysis(symbol, label, df, mkt=mkt)

    # Extended session panel
    if show_pre or show_post or show_night:
        st.markdown("---")
        render_extended_session(symbol, show_pre, show_post, show_night)

    # Social sentiment panel
    if show_social:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:1.05rem;font-weight:700;color:#7799cc;margin-bottom:8px;">'
            '💬 Social Sentiment</div>',
    unsafe_allow_html=True)
        render_social_sentiment(symbol)

    # Options Flow panel
    if show_options:
        st.markdown("---")
        st.markdown(
            '<div style="font-size:1.05rem;font-weight:700;color:#7799cc;margin-bottom:8px;">'
            '📊 Options Flow 期權數據</div>',
            unsafe_allow_html=True)
        render_options_panel(symbol)

    # ── 多時間框架關鍵位綜合分析面板 ─────────────────────────────────────────
    if show_mtf_keylevels:
        st.markdown("---")
        render_mtf_keylevel_analysis(symbol, current_price=last)

# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📈 美股監控系統")
    st.markdown("---")

    raw_input = st.text_area("股票代號（空格分隔，例：TSLA AAPL NVDA）", value="", height=80,
                             key="symbol_input_area",
                             placeholder="TSLA AAPL NVDA")
    # 同時支援空格、逗號、換行、全形逗號分隔
    import re as _re
    symbols = [s.strip().upper() for s in _re.split(r'[\s,，\n]+', raw_input) if s.strip()]
    # 過濾非法代號（只允許字母和.）
    symbols = [s for s in symbols if _re.match(r'^[A-Z\.\-]{1,10}$', s)]
    # 同步到 session_state 讓 send_telegram 能檢查
    st.session_state["_active_symbols"] = symbols

    st.markdown("---")
    st.markdown("#### 📅 監控模式")
    mode = st.radio("", ["單一週期", "多週期同時監控"], horizontal=True,
                    label_visibility="collapsed")

    if mode == "單一週期":
        single_interval = st.selectbox(
            "時間週期",
            ALL_INTERVALS,
            format_func=lambda x: INTERVAL_LABELS[x],
            index=4,
        )
        layout_mode = None
        selected    = []

    else:
        st.markdown("**勾選要同時顯示的週期：**")
        selected    = []
        defaults    = {"5m", "15m", "1d"}
        left_col, right_col = st.columns(2)
        for i, itvl in enumerate(ALL_INTERVALS):
            col = left_col if i % 2 == 0 else right_col
            if col.checkbox(INTERVAL_LABELS[itvl], value=(itvl in defaults), key=f"cb_{itvl}"):
                selected.append(itvl)
        st.markdown("")
        layout_mode = st.radio("圖表排列方式",
                               ["並排（2欄）", "堆疊（全寬）"], horizontal=True)

    st.markdown("---")
    st.markdown("**🔄 自動監控**")

    if "monitoring" not in st.session_state:
        st.session_state.monitoring = False

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶ 啟動監控", use_container_width=True,
                     type="primary" if not st.session_state.monitoring else "secondary",
                     disabled=st.session_state.monitoring):
            st.session_state.monitoring = True
            st.rerun()
    with col_stop:
        if st.button("⏹ 停止監控", use_container_width=True,
                     type="primary" if st.session_state.monitoring else "secondary",
                     disabled=not st.session_state.monitoring):
            st.session_state.monitoring = False
            st.rerun()

    if st.session_state.monitoring:
        st.markdown(
            '<div style="background:#0d2e18;border:1px solid #00aa44;border-radius:6px;'
            'padding:6px 12px;font-size:0.82rem;color:#00ee66;text-align:center;">'
            '🟢 監控中 — 自動刷新中</div>',
        unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="background:#1a1e2e;border:1px solid #334466;border-radius:6px;'
            'padding:6px 12px;font-size:0.82rem;color:#556688;text-align:center;">'
            '⏸ 已暫停 — 點「啟動」開始監控</div>',
    unsafe_allow_html=True)

    refresh_sec  = st.slider("刷新間隔（秒）", 30, 300, 60, step=30,
                             disabled=not st.session_state.monitoring)
    auto_refresh = st.session_state.monitoring

    st.markdown("---")
    st.markdown("**📊 K 線顯示根數**")
    max_bars = st.number_input(
        "每張圖最多顯示幾根 K 線",
        min_value=20, max_value=500, value=90, step=10,
        help="建議：分鐘圖 60-120 根，日K 60-90 根，週K/月K 40-60 根",
    )

    st.markdown("---")
    show_alerts  = st.toggle("啟用警示偵測",     value=True)
    show_market  = st.toggle("顯示市場環境面板",   value=True)
    show_ai      = st.toggle("啟用 AI 技術分析",  value=True)
    show_social  = st.toggle("社群情緒面板 (StockTwits/Reddit)", value=True)
    show_options = st.toggle("📊 期權數據面板 (P/C Ratio / IV / 流向)", value=True)
    show_mtf_keylevels = st.toggle("🗺️ 多框架關鍵位分析 (月/週/日)", value=True)
    show_briefing = st.toggle("📋 今日操作簡報（全股票一覽）", value=True)

    st.markdown("---")
    st.markdown("**🌙 延長時段**")
    show_pre   = st.toggle("📈 盤前 (Pre-market 04:00-09:30)", value=False)
    show_post  = st.toggle("📉 盤後 (After-hours 16:00-20:00)", value=False)
    show_night = st.toggle("🌙 夜盤 (Overnight 20:00-04:00)", value=False)

    if st.button("🗑️ 清除警示記錄"):
        st.session_state.alert_log   = []
        st.session_state.sent_alerts = set()
        st.toast("警示記錄已清除")

    if st.button("🔄 強制刷新數據快取"):
        st.cache_data.clear()
        st.toast("快取已清除，下次刷新將重新抓取最新數據")
        st.rerun()

    if st.session_state.alert_log:
        csv_data = pd.DataFrame(st.session_state.alert_log).to_csv(
            index=False, encoding="utf-8-sig")
        st.download_button("📥 匯出警示 CSV", csv_data, "alerts.csv", "text/csv")

    st.markdown("---")
    st.caption("數據來源：Yahoo Finance\n\n⚠️ 僅供參考，不構成投資建議")

# ══════════════════════════════════════════════════════════════════════════════
# 主區域
# ══════════════════════════════════════════════════════════════════════════════
st.title("🇺🇸 美股即時監控系統")

if not symbols:
    st.session_state["_active_symbols"] = []   # 立即清空，阻止任何後續發送
    st.info("👈 請在左側輸入股票代號（例如：TSLA AAPL NVDA）")
    if auto_refresh:
        time.sleep(refresh_sec)
        st.cache_data.clear()
        st.rerun()
    st.stop()

# ── 📋 今日操作簡報（最頂部，全股票一覽）─────────────────────────────────────
if show_briefing:
    render_daily_briefing(symbols)

# ── 市場環境面板（置頂）──────────────────────────────────────────────────────
if show_market:
    render_market_environment()
    st.markdown("---")

stock_tabs = st.tabs([f"📊 {s}" for s in symbols])

for tab, symbol in zip(stock_tabs, symbols):
    with tab:
        if mode == "單一週期":
            render_single(symbol, single_interval, show_alerts, max_bars=max_bars, show_pre=show_pre, show_post=show_post, show_night=show_night)

        else:
            if not selected:
                st.warning("⚠️ 請在左側至少勾選一個時間週期")
            else:
                _mtf_prepost = show_pre or show_post or show_night
                # ① 多週期摘要
                render_mtf_summary(symbol, selected, show_alerts, prepost=_mtf_prepost)
                st.markdown("---")
                # ② 多週期 K 線圖
                render_mtf_charts(symbol, selected, layout_mode, max_bars=max_bars, prepost=_mtf_prepost)

# ══════════════════════════════════════════════════════════════════════════════
# ⏱️ 進場時機追蹤面板
# ══════════════════════════════════════════════════════════════════════════════
render_entry_tracker_panel()

# ══════════════════════════════════════════════════════════════════════════════
# 📋 系統建議交易面板（高置信信號自動生成）
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("trade_suggestions"):
    st.markdown("---")
    sugs = st.session_state.trade_suggestions
    pending = [s for s in sugs if s["狀態"] == "待確認"]
    adopted = [s for s in sugs if s["狀態"] == "已採納"]

    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">'
        '<div style="font-size:1.2rem;font-weight:900;color:#e0e8ff;font-family:monospace;">📋 系統建議交易</div>'
        f'<div style="background:#1a2a1a;color:#44ee66;border:1px solid #336633;border-radius:20px;'
        f'padding:2px 10px;font-size:0.75rem;">⏳ 待確認 {len(pending)}</div>'
        f'<div style="background:#1a1a2e;color:#6688ff;border:1px solid #334488;border-radius:20px;'
        f'padding:2px 10px;font-size:0.75rem;">✅ 已採納 {len(adopted)}</div>'
        '<div style="font-size:0.72rem;color:#445566;margin-left:8px;">依據10年回測高置信信號自動生成｜僅供參考</div>'
        '</div>',
        unsafe_allow_html=True)

    for i, sug in enumerate(sugs[:12]):
        is_long   = sug["方向"] == "LONG"
        dir_color = "#00ee66" if is_long else "#ff5566"
        dir_icon  = "▲ LONG"  if is_long else "▼ SHORT"
        bg_color  = "#0a1a0f"  if is_long else "#1a0a0a"
        bd_color  = "#224422"  if is_long else "#442222"
        st_color  = {"待確認": "#ffcc44", "已採納": "#44aaff", "已忽略": "#445566"}[sug["狀態"]]

        ep   = sug["進場"]
        sl   = sug["止損"]
        tp1  = sug["止盈1"]
        tp2  = sug["止盈2"]
        rr1  = sug["盈虧比1"]
        rr2  = sug["盈虧比2"]
        risk = sug["風險%"]

        card_html = (
            f'<div style="background:{bg_color};border:1px solid {bd_color};border-left:3px solid {dir_color};'
            f'border-radius:8px;padding:12px 16px;margin:6px 0;">'

            # 頂行：方向 + 股票 + 週期 + 置信 + 狀態 + 時間
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:8px;">'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<span style="color:{dir_color};font-weight:800;font-size:0.95rem;">{dir_icon}</span>'
            f'<span style="color:#eef;font-weight:700;font-size:1.0rem;">${sug["股票"]}</span>'
            f'<span style="color:#556677;font-size:0.75rem;">{sug["週期"]}</span>'
            f'<span style="color:{sug["置信色"]};font-size:0.72rem;border:1px solid {sug["置信色"]}44;'
            f'border-radius:4px;padding:1px 6px;">{sug["置信"]}</span>'
            f'<span style="background:#1a2030;color:#aabbcc;font-size:0.7rem;border-radius:4px;padding:1px 6px;">'
            f'WR {sug["WR"]:.0f}% (n={sug["樣本數"]})</span>'
            f'</div>'
            f'<div style="display:flex;align-items:center;gap:8px;">'
            f'<span style="color:{st_color};font-size:0.72rem;">{sug["狀態"]}</span>'
            f'<span style="color:#334455;font-size:0.68rem;">{sug["時間"]}</span>'
            f'</div></div>'

            # 價格行
            f'<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:6px;">'
            f'<div><span style="color:#556677;font-size:0.72rem;">進場</span> '
            f'<span style="color:#44aaff;font-weight:700;font-size:1.05rem;">${ep:.2f}</span></div>'
            f'<div><span style="color:#556677;font-size:0.72rem;">止損</span> '
            f'<span style="color:#ff4444;font-weight:600;">${sl:.2f}</span>'
            f'<span style="color:#663333;font-size:0.7rem;margin-left:3px;">(-{risk:.1f}%)</span></div>'
            f'<div><span style="color:#556677;font-size:0.72rem;">止盈①</span> '
            f'<span style="color:#44ee66;font-weight:600;">${tp1:.2f}</span>'
            f'<span style="color:#336633;font-size:0.7rem;margin-left:3px;">R:{rr1:.1f}</span></div>'
            f'<div><span style="color:#556677;font-size:0.72rem;">止盈②</span> '
            f'<span style="color:#aaffcc;font-weight:600;">${tp2:.2f}</span>'
            f'<span style="color:#225533;font-size:0.7rem;margin-left:3px;">R:{rr2:.1f}</span></div>'
            f'<div><span style="color:#556677;font-size:0.72rem;">ATR</span> '
            f'<span style="color:#778899;">{sug["ATR"]:.2f}</span></div>'
            f'</div>'

            # 信號依據
            f'<div style="font-size:0.73rem;color:#667788;margin-bottom:4px;">'
            f'📌 {sug["描述"]}</div>'
            f'<div style="font-size:0.68rem;color:#445566;border-top:1px solid #1e2e3e;padding-top:4px;">'
            f'來源：{sug["來源信號"][:80]}</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # 按鈕行
        if sug["狀態"] == "待確認":
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4])
            with btn_col1:
                if st.button(f"✅ 採納加入日誌", key=f"adopt_sug_{i}"):
                    st.session_state.trade_suggestions[i]["狀態"] = "已採納"
                    tl_open_trade(
                        symbol     = sug["股票"],
                        direction  = sug["方向"],
                        entry_price= sug["進場"],
                        stop_loss  = sug["止損"],
                        take_profit= sug["止盈1"],
                        reason     = sug["描述"],
                        signals    = [sug["來源信號"]],
                        period     = sug["週期"],
                    )
                    st.toast(f"✅ {sug['股票']} {sug['方向']} ${sug['進場']:.2f} 已加入交易日誌！")
                    st.rerun()
            with btn_col2:
                if st.button(f"❌ 忽略", key=f"dismiss_sug_{i}"):
                    st.session_state.trade_suggestions[i]["狀態"] = "已忽略"
                    st.rerun()

    if st.button("🗑️ 清除已處理建議", key="clear_processed_sugs"):
        st.session_state.trade_suggestions = [s for s in sugs if s["狀態"] == "待確認"]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 警示面板 + 統計分析
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.alert_log:
    st.markdown("---")
    log = st.session_state.alert_log

    # ── 統計分析 ─────────────────────────────────────────────────────────────
    st.subheader("📊 警示統計分析")

    from collections import defaultdict
    # Per-symbol stats
    sym_stats = defaultdict(lambda: {
        "bull": 0, "bear": 0, "vol": 0, "info": 0,
        "signals": [], "periods": defaultdict(int)
    })
    for e in log:
        s = e["股票"]
        t = e["類型"]
        sym_stats[s][t] = sym_stats[s].get(t, 0) + 1
        sym_stats[s]["signals"].append(e["訊息"])
        if e.get("週期"):
            sym_stats[s]["periods"][e["週期"]] += 1

    def _trend_label(bull, bear, vol):
        total = bull + bear
        if total == 0:
            return "⚪ 中性", "#778899", 50
        score = bull / total * 100
        if score >= 70:   return "🟢 強勢多頭", "#00ee66", int(score)
        if score >= 55:   return "🟡 偏多",     "#aaee44", int(score)
        if score >= 45:   return "⚪ 震盪",     "#ffcc00", int(score)
        if score >= 30:   return "🟠 偏空",     "#ff8800", int(score)
        return                   "🔴 強勢空頭", "#ff4444", int(score)

    # ── 每股摘要卡片（純 HTML flex，避免 st.columns DOM 衝突）────────────────
    syms = sorted(sym_stats.keys())
    all_cards = ['<div style="display:flex;flex-wrap:wrap;gap:12px;margin:12px 0;">']
    for sym in syms:
        ss = sym_stats[sym]
        bull, bear, vol = ss["bull"], ss["bear"], ss["vol"]
        total = bull + bear + vol + ss["info"]
        trend_lbl, trend_color, score = _trend_label(bull, bear, vol)
        periods    = ss["periods"]
        top_period = max(periods, key=periods.get) if periods else "-"
        sig_counts = defaultdict(int)
        for s in ss["signals"]:
            if   "金叉" in s or "上穿" in s:    sig_counts["金叉/上穿"]   += 1
            elif "死叉" in s or "下穿" in s:    sig_counts["死叉/下穿"]   += 1
            elif "突破阻力" in s:                sig_counts["突破阻力"]    += 1
            elif "跌破支撐" in s:                sig_counts["跌破支撐"]    += 1
            elif "異常放量" in s:                sig_counts["異常放量"]    += 1
            elif "真空帶" in s:                  sig_counts["成交量真空帶"] += 1
            elif "DTR/ATR" in s:                 sig_counts["DTR波幅警戒"] += 1
            elif "VIX" in s and "百分位" in s:   sig_counts["VIX百分位"]   += 1
            elif "跳空" in s:                    sig_counts["跳空信號"]    += 1
            else:                                sig_counts["其他"]         += 1
        top_sig   = max(sig_counts, key=sig_counts.get) if sig_counts else "-"
        top_sig_n = sig_counts.get(top_sig, 0)
        all_cards.append(
            f'<div style="flex:1;min-width:180px;max-width:260px;background:#0c1220;'
            f'border:1px solid {trend_color}55;border-radius:12px;padding:14px 16px;">'
            f'<div style="font-size:1.1rem;font-weight:800;color:#ccd6ee;margin-bottom:4px;">${sym}</div>'
            f'<div style="font-size:0.88rem;font-weight:700;color:{trend_color};margin-bottom:8px;">{trend_lbl}</div>'
            f'<div style="background:#141c2e;border-radius:3px;height:5px;margin-bottom:10px;">'
            f'<div style="width:{score}%;background:{trend_color};height:5px;border-radius:3px;"></div></div>'
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">'
            f'<span style="background:#0d2e18;color:#00ee66;border-radius:4px;padding:1px 6px;font-size:0.72rem;">🟢 {bull}</span>'
            f'<span style="background:#2e0d0d;color:#ff5566;border-radius:4px;padding:1px 6px;font-size:0.72rem;">🔴 {bear}</span>'
            f'<span style="background:#1a1428;color:#cc88ff;border-radius:4px;padding:1px 6px;font-size:0.72rem;">📊 {vol}</span>'
            f'<span style="background:#141c2e;color:#7799cc;border-radius:4px;padding:1px 6px;font-size:0.72rem;">Σ {total}</span>'
            f'</div>'
            f'<div style="font-size:0.72rem;color:#445566;line-height:1.8;">'
            f'主要信號：<span style="color:#aabbcc">{top_sig} ×{top_sig_n}</span><br>'
            f'活躍週期：<span style="color:#aabbcc">{top_period}</span>'
            f'</div></div>'
        )
    all_cards.append('</div>')
    st.markdown(f'<div id="alert-cards-panel">{"".join(all_cards)}</div>',
    unsafe_allow_html=True)

    # ── 整體市場情緒 ─────────────────────────────────────────────────────────
    total_bull = sum(v["bull"] for v in sym_stats.values())
    total_bear = sum(v["bear"] for v in sym_stats.values())
    total_vol  = sum(v["vol"]  for v in sym_stats.values())
    all_total  = total_bull + total_bear + total_vol
    market_score = int(total_bull / (total_bull + total_bear) * 100) if (total_bull + total_bear) > 0 else 50
    market_lbl, market_color, _ = _trend_label(total_bull, total_bear, total_vol)

    st.markdown(
        f'<div style="background:#0a0e18;border:1px solid #1e2e48;border-radius:12px;'
        f'padding:14px 20px;margin:12px 0;display:flex;align-items:center;gap:20px;">'
        f'<div style="flex:1;">'
        f'<div style="font-size:0.78rem;color:#445566;margin-bottom:4px;">整體市場情緒</div>'
        f'<div style="font-size:1.05rem;font-weight:700;color:{market_color};">{market_lbl}</div>'
        f'<div style="background:#141c2e;border-radius:4px;height:8px;margin-top:8px;">'
        f'<div style="width:{market_score}%;background:{market_color};height:8px;border-radius:4px;"></div>'
        f'</div></div>'
        f'<div style="display:flex;gap:16px;font-size:0.82rem;">'
        f'<div style="text-align:center;"><div style="color:#00ee66;font-weight:700;font-size:1.1rem;">{total_bull}</div>'
        f'<div style="color:#445566;">多頭信號</div></div>'
        f'<div style="text-align:center;"><div style="color:#ff5566;font-weight:700;font-size:1.1rem;">{total_bear}</div>'
        f'<div style="color:#445566;">空頭信號</div></div>'
        f'<div style="text-align:center;"><div style="color:#cc88ff;font-weight:700;font-size:1.1rem;">{total_vol}</div>'
        f'<div style="color:#445566;">量能信號</div></div>'
        f'<div style="text-align:center;"><div style="color:#7799cc;font-weight:700;font-size:1.1rem;">{all_total}</div>'
        f'<div style="color:#445566;">總信號數</div></div>'
        f'</div></div>',
        unsafe_allow_html=True)

    # ── 警示記錄列表 ─────────────────────────────────────────────────────────
    st.subheader("🔔 警示訊息記錄")

    # ══════════════════════════════════════════════════════════════════════════
    # 🧠 智慧摘要面板：自動彙整所有警示 → 一句話交易建議
    # ══════════════════════════════════════════════════════════════════════════
    def render_alert_summary(log_data: list):
        """
        彙整警示記錄，依每個股票輸出：
        - 多空評分 / 信心條（加權質量評分，非簡單計數）
        - 最重要的3個信號（按優先級篩選）
        - 一句話操作建議（方向 + 進場條件 + 止損位）
        - 衝突警告（僅高優先級衝突才顯示）
        """
        if not log_data:
            return

        from collections import defaultdict
        import re as _re
        sym_log = defaultdict(list)
        for e in log_data:
            sym_log[e["股票"]].append(e)

        # ── 信號優先級權重（越高越重要，決定評分貢獻）────────────────────────
        # 分3層：
        #   高置信結構信號（8-10）：10年回測驗證，WR≥95%
        #   中置信形態信號（4-7）：有統計支撐，WR≥60%
        #   低置信觀察信號（1-3）：需結合其他信號確認
        PRIORITY = {
            # ── 第一層：極高置信（WR≥99%，10年驗證）─────────────────────────
            "F6": 10, "F7": 10, "F8": 10, "F9": 10,   # 跳空系列
            "P6": 9,  "突破跳空": 9,                    # 量能突破跳空
            "K18-早晨之星": 9, "K19-黃昏之星": 9,       # 三K組合形態
            "K12-看漲吞噬": 8, "K13-看跌吞噬": 8,       # 強力雙K吞噬
            "Q2": 8,  "衰竭跳空": 8,                    # VIX極端+衰竭

            # ── 第二層：高置信（WR≥70%，結構信號）────────────────────────────
            "全EMA多頭排列": 8, "全EMA空頭排列": 8,     # 最強趨勢結構
            "強勢多頭趨勢": 7,  "空頭排列": 7,           # EMA排列
            "雙框架多頭": 7,    "雙框架空頭": 7,         # MTF共振
            "多框架共振": 7,                              # MTF
            "Q1": 7,  "底背離": 7, "頂背離": 7,          # 背離+真空帶
            "I2": 7,  "I1": 6,  "I3": 8,                # MACD背離
            "E5": 6,  "D5": 6,                           # 底/頂結構
            "K20a-三白兵": 7, "K20b-三黑鴉": 7,          # 三K趨勢
            "K16-貫穿線": 6, "K17-烏雲蓋頂": 6,          # 雙K反轉
            "K07-蜻蜓十字": 6, "K08-墓碑十字": 6,        # 特殊十字

            # ── 第三層：中置信（WR≥55%，需確認）─────────────────────────────
            "VIX極度恐慌": 6, "VIX暴": 5,               # VIX
            "Q3": 5,  "DTR": 5,                          # 波幅
            "深谷金叉": 6,  "MACD金叉": 5,               # MACD
            "MACD死叉": 5,  "底部金叉": 5,               # MACD
            "均線聚合後突破": 6, "均線壓縮": 4,           # 均線形態
            "S3-盤整突破上": 9, "S3-盤整跌破下": 9,      # 盤整突破確認（高置信）
            "S2-即將突破上": 6, "S2-即將跌破下": 6,      # 即將突破預警
            "S1-盤整壓縮":  4,                            # 盤整壓縮提示
            "關鍵阻力": 4,  "關鍵支撐": 4,               # 關鍵位
            "K10-大陽線": 5, "K11-大陰線": 5,            # 大K
            "K01-錘頭線": 4, "K02-吊頸線": 4,            # 單K反轉
            "K03-射擊之星": 4, "K04-倒錘頭": 4,
            "K05-看漲十字星": 4, "K06-看跌十字星": 4,
            "K14-看漲孕線": 4, "K15-看跌孕線": 4,
            "K09-多頭紡錘線": 3,

            # ── 第四層：低置信（僅作觀察）────────────────────────────────────
            "EMA金叉": 3,   "EMA死叉": 3,               # 短線EMA
            "異常放量": 3,  "跳空": 3,                   # 量/跳空
            "錘頭K線": 2,  "流星K線": 2,                 # 舊版K線（被新版取代）
            "多頭吞噬": 2, "空頭吞噬": 2,                # 舊版（被K12/K13取代）
            "RSI": 2,      "超賣": 2, "超買": 2,         # RSI基礎
        }

        # 高優先級閾值（低於此值的反向信號不觸發「多空分歧」警告）
        CONFLICT_THRESHOLD = 4

        def _score_msg(msg: str) -> int:
            best = 1
            for k, v in PRIORITY.items():
                if k in msg and v > best:
                    best = v
            return best

        def _build_suggestion(sym: str, entries: list) -> dict:
            bull_msgs = [e for e in entries if e["類型"] == "bull"]
            bear_msgs = [e for e in entries if e["類型"] == "bear"]
            info_msgs = [e for e in entries if e["類型"] == "info"]

            # ── 加權質量評分（非線性：高分信號指數級貢獻）──────────────────
            def _weighted_score(msgs):
                scores = sorted([_score_msg(e["訊息"]) for e in msgs], reverse=True)
                total = 0
                for i, s in enumerate(scores):
                    # 遞減加權：第1個×1.0，第2個×0.7，第3個×0.5，之後×0.3
                    weight = [1.0, 0.7, 0.5] + [0.3]*(len(scores)-3)
                    total += s * weight[i]
                return total

            bull_score = _weighted_score(bull_msgs)
            bear_score = _weighted_score(bear_msgs)
            total      = bull_score + bear_score
            bull_pct   = int(bull_score / total * 100) if total > 0 else 50

            # ── 組合加成：關鍵組合出現額外提升方向信心 ──────────────────────
            bull_texts = " ".join(e["訊息"] for e in bull_msgs)
            bear_texts = " ".join(e["訊息"] for e in bear_msgs)

            # 加成組合（多頭）
            bull_combos = 0
            if "全EMA多頭排列" in bull_texts and ("MACD金叉" in bull_texts or "深谷金叉" in bull_texts):
                bull_combos += 15   # 均線排列 + MACD同向 → 最強組合
            if ("雙框架" in bull_texts or "多框架共振" in bull_texts) and "突破" in bull_texts:
                bull_combos += 12   # MTF共振 + 突破
            if "底背離" in bull_texts and ("錘頭" in bull_texts or "吞噬" in bull_texts or "K18" in bull_texts):
                bull_combos += 10   # 背離 + K線確認
            if "均線聚合後突破" in bull_texts:
                bull_combos += 8    # 均線聚合突破

            # 加成組合（空頭）
            bear_combos = 0
            if "全EMA空頭排列" in bear_texts and ("MACD死叉" in bear_texts or "頂背離" in bear_texts):
                bear_combos += 15
            if ("雙框架" in bear_texts or "多框架共振" in bear_texts) and ("跌破" in bear_texts or "空頭" in bear_texts):
                bear_combos += 12
            if "頂背離" in bear_texts and ("射擊之星" in bear_texts or "K19" in bear_texts or "K13" in bear_texts):
                bear_combos += 10
            if "烏雲蓋頂" in bear_texts or "K17" in bear_texts:
                bear_combos += 6

            # 重新計算含組合加成的百分比
            adj_bull = bull_score + bull_combos
            adj_bear = bear_score + bear_combos
            adj_total = adj_bull + adj_bear
            bull_pct = int(adj_bull / adj_total * 100) if adj_total > 0 else 50

            # ── 方向判斷（60/40閾值）────────────────────────────────────────
            if bull_pct >= 60:
                direction = "LONG";  dir_color = "#00ee66"
                dir_icon  = "▲";    dir_label = "做多"
            elif bull_pct <= 40:
                direction = "SHORT"; dir_color = "#ff5566"
                dir_icon  = "▼";    dir_label = "做空"
            else:
                direction = "WAIT";  dir_color = "#ffcc44"
                dir_icon  = "⟺";   dir_label = "觀望"

            # ── 衝突偵測：只有高優先級反向信號才算「真衝突」────────────────
            high_bull = [e for e in bull_msgs if _score_msg(e["訊息"]) >= CONFLICT_THRESHOLD]
            high_bear = [e for e in bear_msgs if _score_msg(e["訊息"]) >= CONFLICT_THRESHOLD]
            has_conflict = len(high_bull) > 0 and len(high_bear) > 0
            conflict_str = ""
            if has_conflict:
                opposite = high_bear if direction == "LONG" else high_bull
                conflict_str = f"⚡ {len(opposite)} 條高優先級反向信號，建議等突破確認再進場"

            # ── 信心等級 ────────────────────────────────────────────────────
            max_s = max(bull_score, bear_score)
            if max_s >= 25 and not has_conflict:
                confidence = "⭐⭐⭐ 極高置信"
                conf_color = "#ffdd44"
            elif max_s >= 15:
                confidence = "⭐⭐ 高置信"
                conf_color = "#ffaa44"
            elif max_s >= 8:
                confidence = "⭐ 中等置信"
                conf_color = "#ff8844"
            else:
                confidence = "📊 低置信（觀察）"
                conf_color = "#778899"

            # ── 前3重要信號（多空各取優先級最高）───────────────────────────
            top_bull = sorted(bull_msgs, key=lambda e: _score_msg(e["訊息"]), reverse=True)[:3]
            top_bear = sorted(bear_msgs, key=lambda e: _score_msg(e["訊息"]), reverse=True)[:3]
            top_info = sorted(info_msgs, key=lambda e: _score_msg(e["訊息"]), reverse=True)[:1]

            if direction == "LONG":
                key3 = top_bull[:2] + (top_bear[:1] if has_conflict else [])
            elif direction == "SHORT":
                key3 = top_bear[:2] + (top_bull[:1] if has_conflict else [])
            else:
                key3 = top_bull[:1] + top_bear[:1] + top_info[:1]
            key3 = key3[:3]

            def _shorten(msg: str) -> str:
                clean = _re.sub(r'｜10年回測.*', '', msg)
                clean = _re.sub(r'｜回測隔日.*', '', clean)
                clean = _re.sub(r'（n=\d+[^）]*）', '', clean)
                clean = _re.sub(r'\s+', ' ', clean)
                return clean[:58].strip()

            key3_texts = []
            for e in key3:
                ic = {"bull":"🟢","bear":"🔴","info":"🔵","vol":"🟣"}.get(e["類型"],"⚪")
                key3_texts.append(f"{ic} {_shorten(e['訊息'])}")

            # 找系統建議交易中對應的
            sug_entry = None
            for s in st.session_state.get("trade_suggestions", []):
                if s["股票"] == sym and s["狀態"] == "待確認":
                    sug_entry = s
                    break

            return {
                "symbol": sym, "direction": direction,
                "dir_color": dir_color, "dir_icon": dir_icon, "dir_label": dir_label,
                "bull_pct": bull_pct, "bear_pct": 100-bull_pct,
                "bull_count": len(bull_msgs), "bear_count": len(bear_msgs),
                "total": len(entries),
                "key3": key3_texts, "conflict": conflict_str,
                "has_conflict": has_conflict,
                "confidence": confidence, "conf_color": conf_color,
                "bull_combos": bull_combos, "bear_combos": bear_combos,
                "sug": sug_entry,
            }

        summaries = {sym: _build_suggestion(sym, entries)
                     for sym, entries in sym_log.items()}

        # ── 渲染摘要面板 ──────────────────────────────────────────────────────
        st.markdown(
            '<div style="background:#07090f;border:1px solid #1e2e48;border-radius:14px;'
            'padding:16px 20px;margin-bottom:16px;">'
            '<div style="font-size:0.78rem;font-weight:700;color:#445577;letter-spacing:1px;'
            'margin-bottom:12px;">🧠 智慧摘要 · 一鍵讀懂所有警示</div>',
            unsafe_allow_html=True)

        for sym, s in summaries.items():
            bc = s["bull_pct"]
            bear_pct = 100 - bc
            dc = s["dir_color"]
            sug = s["sug"]

            # 進場/止損文字
            trade_line = ""
            if sug:
                ep, sl1, tp1 = sug["進場"], sug["止損"], sug["止盈1"]
                rr = sug["盈虧比1"]
                sl_pct  = abs(ep - sl1) / ep * 100
                tp_pct  = abs(tp1 - ep) / ep * 100
                sug_color = "#00ee66" if sug["方向"] == "LONG" else "#ff5566"
                trade_line = (
                    f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px;'
                    f'background:#0c1520;border-radius:6px;padding:8px 12px;align-items:center;">'
                    f'<span style="color:#778899;font-size:0.7rem;">系統建議</span>'
                    f'<span style="color:{sug_color};font-weight:700;font-size:0.85rem;">'
                    f'{"▲ LONG" if sug["方向"]=="LONG" else "▼ SHORT"}</span>'
                    f'<span style="color:#556677;font-size:0.72rem;">進場</span>'
                    f'<span style="color:#44aaff;font-weight:600;">${ep:.2f}</span>'
                    f'<span style="color:#556677;font-size:0.72rem;">止損</span>'
                    f'<span style="color:#ff4444;font-weight:600;">${sl1:.2f}</span>'
                    f'<span style="color:#663333;font-size:0.68rem;">(-{sl_pct:.1f}%)</span>'
                    f'<span style="color:#556677;font-size:0.72rem;">止盈</span>'
                    f'<span style="color:#44ee66;font-weight:600;">${tp1:.2f}</span>'
                    f'<span style="color:#336633;font-size:0.68rem;">(+{tp_pct:.1f}% R:{rr:.1f})</span>'
                    f'<span style="color:#445566;font-size:0.65rem;margin-left:4px;">'
                    f'WR {sug["WR"]:.0f}% n={sug["樣本數"]} {sug["置信"]}</span>'
                    f'</div>'
                )
            elif s["direction"] != "WAIT":
                # 無系統建議時給文字建議
                if s["direction"] == "LONG":
                    trade_line = (
                        f'<div style="font-size:0.75rem;color:#667788;margin-top:6px;'
                        f'padding:6px 10px;background:#0c1520;border-radius:6px;">'
                        f'💡 等待回調至支撐確認，量縮後再進場；無高置信跳空信號，輕倉試多</div>')
                else:
                    trade_line = (
                        f'<div style="font-size:0.75rem;color:#667788;margin-top:6px;'
                        f'padding:6px 10px;background:#0c1520;border-radius:6px;">'
                        f'💡 等待反彈至阻力壓制確認，無高置信跳空信號，輕倉試空，嚴設止損</div>')

            # 衝突標籤
            conflict_html = ""
            if s["has_conflict"]:
                conflict_html = (
                    f'<span style="background:#2a1a00;color:#ffaa44;border:1px solid #664400;'
                    f'border-radius:4px;padding:1px 7px;font-size:0.68rem;margin-left:6px;">'
                    f'⚡ 多空分歧</span>')

            card = (
                f'<div style="background:#0c1220;border:1px solid {dc}33;border-left:3px solid {dc};'
                f'border-radius:10px;padding:14px 16px;margin:8px 0;">'

                # 頂行：股票名 + 方向 + 置信 + 衝突
                f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px;">'
                f'<span style="color:#eef;font-weight:800;font-size:1.05rem;">${sym}</span>'
                f'<span style="background:{dc}22;color:{dc};border:1px solid {dc}55;'
                f'border-radius:20px;padding:2px 12px;font-weight:700;font-size:0.85rem;">'
                f'{s["dir_icon"]} {s["dir_label"]}</span>'
                f'<span style="background:#1a1a00;color:{s["conf_color"]};border:1px solid {s["conf_color"]}44;'
                f'border-radius:10px;padding:1px 8px;font-size:0.68rem;">{s["confidence"]}</span>'
                + (f'<span style="background:#00441a;color:#44ff88;border:1px solid #006633;'
                   f'border-radius:10px;padding:1px 7px;font-size:0.65rem;">⚡ 組合+{s["bull_combos"]}</span>'
                   if s["bull_combos"] > 0 and s["direction"] == "LONG" else '')
                + (f'<span style="background:#440011;color:#ff8888;border:1px solid #660022;'
                   f'border-radius:10px;padding:1px 7px;font-size:0.65rem;">⚡ 組合+{s["bear_combos"]}</span>'
                   if s["bear_combos"] > 0 and s["direction"] == "SHORT" else '')
                + (f'<span style="background:#2a1a00;color:#ffaa44;border:1px solid #664400;'
                   f'border-radius:4px;padding:1px 7px;font-size:0.68rem;">⚡ 高優先衝突</span>'
                   if s["has_conflict"] else '')
                + f'<span style="color:#334455;font-size:0.68rem;margin-left:auto;">'
                f'📊 {s["bull_count"]}多/{s["bear_count"]}空/{s["total"]}條</span>'
                f'</div>'

                # 多空信心條（加權評分）
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
                f'<span style="color:#00ee66;font-size:0.68rem;width:30px;">多{bc}%</span>'
                f'<div style="flex:1;background:#0e1e0e;border-radius:4px;height:8px;overflow:hidden;">'
                f'<div style="width:{bc}%;background:linear-gradient(90deg,#00ee66,#44bb88);'
                f'height:8px;border-radius:4px;transition:width 0.3s;"></div></div>'
                f'<div style="flex:1;background:#1e0e0e;border-radius:4px;height:8px;overflow:hidden;">'
                f'<div style="width:{bear_pct}%;background:linear-gradient(90deg,#bb4444,#ff5566);'
                f'height:8px;border-radius:4px;float:right;"></div></div>'
                f'<span style="color:#ff5566;font-size:0.68rem;width:30px;text-align:right;">空{bear_pct}%</span>'
                f'</div>'

                # 關鍵信號（前3，加優先級標籤）
                f'<div style="display:flex;flex-direction:column;gap:3px;margin-bottom:6px;">'
            )
            for kt in s["key3"]:
                card += (
                    f'<div style="font-size:0.74rem;color:#99aabb;'
                    f'background:#0a1018;border-radius:4px;padding:4px 10px;'
                    f'border-left:2px solid #1e2e3e;">{kt}</div>')
            card += f'</div>'

            # 衝突說明
            if s["conflict"]:
                card += (f'<div style="font-size:0.71rem;color:#ffaa44;'
                         f'background:#1a1000;border-radius:4px;padding:5px 10px;'
                         f'margin-bottom:4px;">⚠️ {s["conflict"]}</div>')

            card += trade_line + '</div>'
            st.markdown(card, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    render_alert_summary(log)
    st.markdown("---")

    cls_map = {"bull":"alert-bull","bear":"alert-bear","vol":"alert-vol","info":"alert-info"}
    for e in log[:40]:
        cls   = cls_map.get(e["類型"], "alert-info")
        p_tag = f'【{e["週期"]}】' if e.get("週期") else ""
        st.markdown(
            f'<div class="alert-box {cls}">'
            f'🕐 {e["時間"]}　【{e["股票"]}】{p_tag}　{e["訊息"]}'
            f'</div>',
            unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 交易日誌面板
# ══════════════════════════════════════════════════════════════════════════════
render_trading_log()

# ══════════════════════════════════════════════════════════════════════════════
# 自動刷新
# ══════════════════════════════════════════════════════════════════════════════
if auto_refresh:
    time.sleep(refresh_sec)
    st.cache_data.clear()
    st.rerun()
