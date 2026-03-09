import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
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
if "alert_log"   not in st.session_state: st.session_state.alert_log   = []
if "sent_alerts" not in st.session_state: st.session_state.sent_alerts = set()

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
def fetch_vix_history() -> pd.Series:
    """VIX 近 30 日歷史，用於趨勢判斷"""
    try:
        df = yf.download("^VIX", period="30d", interval="1d",
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
        st.session_state.alert_log.insert(0,
            {"時間": now, "股票": symbol, "週期": period, "訊息": msg, "類型": atype})
        st.session_state.alert_log = st.session_state.alert_log[:200]
        st.session_state.sent_alerts.add(key)
        send_telegram(f"📊 [{symbol} {period}] {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# 數據抓取
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
    elif all(ema_vals[i] < ema_vals[i+1] for i in range(len(ema_vals)-1)):
        add_alert(symbol, period_label, "💀 趨勢確立｜全 EMA 空頭排列（強勢下降趨勢）", "bear")
        new_signals.append("全EMA空頭排列")

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

    # C4. EMA5/EMA10 黃金/死亡交叉（短線反轉確認）
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
        if len(close) >= 40:
            _dif_i, _dea_i, _ = calc_macd(close)
            _c40   = close.iloc[-40:]
            _dif40 = _dif_i.iloc[-40:]

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
            _pl = _find_lows(_c40)
            if len(_pl) >= 2:
                _p1 = float(_c40.iloc[_pl[-2]]); _p2 = float(_c40.iloc[_pl[-1]])
                _d1 = float(_dif40.iloc[_pl[-2]]); _d2 = float(_dif40.iloc[_pl[-1]])
                _since = 39 - _pl[-1]
                _dif_rising = float(_dif_i.iloc[-1]) > float(_dif_i.iloc[-1-min(3,len(_dif_i)-1)])
                if (_p2 < _p1*0.9995 and _d2 > _d1*1.01 and _dif_rising and _since <= 20):
                    ck = f"{symbol}|{period_label}|MACD底背離|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📈 【MACD底背離】價格創新低({_p1:.2f}→{_p2:.2f})"
                                  f" 但DIF未創新低({_d1:.3f}→{_d2:.3f})"
                                  f"，空頭動能衰竭，可能即將反彈！", "bull")
                        new_signals.append("MACD底背離")

            # ── I2. MACD 頂背離 ──────────────────────────────────────────────
            _ph = _find_highs(_c40)
            if len(_ph) >= 2:
                _p1 = float(_c40.iloc[_ph[-2]]); _p2 = float(_c40.iloc[_ph[-1]])
                _d1 = float(_dif40.iloc[_ph[-2]]); _d2 = float(_dif40.iloc[_ph[-1]])
                _since = 39 - _ph[-1]
                _dif_falling = float(_dif_i.iloc[-1]) < float(_dif_i.iloc[-1-min(3,len(_dif_i)-1)])
                if (_p2 > _p1*1.0005 and _d2 < _d1*0.99 and _dif_falling and _since <= 20):
                    ck = f"{symbol}|{period_label}|MACD頂背離|{df.index[-1].strftime('%Y%m%d%H') if hasattr(df.index[-1],'strftime') else str(df.index[-1])[:13]}"
                    if ck not in st.session_state.sent_alerts:
                        st.session_state.sent_alerts.add(ck)
                        add_alert(symbol, period_label,
                                  f"📉 【MACD頂背離】價格創新高({_p1:.2f}→{_p2:.2f})"
                                  f" 但DIF未創新高({_d1:.3f}→{_d2:.3f})"
                                  f"，多頭動能衰竭，注意回落風險！", "bear")
                        new_signals.append("MACD頂背離")

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

    except Exception:
        pass

    # ── 有新信號 → 自動觸發 AI 分析 ──────────────────────────────────────────
    if not new_signals or not trigger_ai:
        return
    if not get_groq_key():
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

    chart_h = 520 if compact else 820
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.56, 0.19, 0.25], vertical_spacing=0.02,
        subplot_titles=(f"{symbol} ({interval_label})", "成交量", "MACD"),
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
        # category 類型：plotly 只顯示有數據的 bar，自動跳過休市空白
        xaxis_type="category",
        xaxis2_type="category",
        xaxis3_type="category",
    )

    # 套用自訂刻度到所有 x 軸
    for axis_name in ["xaxis", "xaxis2", "xaxis3"]:
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
            if   "金叉" in s or "上穿" in s:  sig_counts["金叉/上穿"] += 1
            elif "死叉" in s or "下穿" in s:  sig_counts["死叉/下穿"] += 1
            elif "突破阻力" in s:              sig_counts["突破阻力"]  += 1
            elif "跌破支撐" in s:              sig_counts["跌破支撐"]  += 1
            elif "異常放量" in s:              sig_counts["異常放量"]  += 1
            else:                              sig_counts["其他"]       += 1
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
# 自動刷新
# ══════════════════════════════════════════════════════════════════════════════
if auto_refresh:
    time.sleep(refresh_sec)
    st.cache_data.clear()
    st.rerun()
