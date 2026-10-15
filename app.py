"""Stream Light — an interactive Streamlit dashboard for the crypto signal engine."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import crypto


st.set_page_config(
    page_title="Stream Light · Crypto Signals",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&display=swap');
    :root { --ink:#101a25; --muted:#82909c; --line:#e7ecef; --mint:#16b887; --sky:#dff8ef; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
    .stApp { background:#f6f8f8; color:var(--ink); }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:#101a25; border-right:0; }
    [data-testid="stSidebar"] * { color:#e7eef2; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#9eabb5; }
    .block-container { padding-top:2.1rem; max-width:1440px; }
    .brand { display:flex; align-items:center; gap:11px; margin:4px 0 35px; font-weight:800; font-size:19px; letter-spacing:-.5px; }
    .brand-mark { width:34px;height:34px;border-radius:11px;background:#19be8c;display:grid;place-items:center;color:#0d3026;font-size:19px; }
    .eyebrow { font-size:11px;text-transform:uppercase;letter-spacing:1.6px;color:#7b8993;font-weight:700; }
    .hero-title { font-size:34px;line-height:1.12;font-weight:800;letter-spacing:-1.2px;margin:7px 0 7px;color:#101a25; }
    .hero-sub { color:#7c8993;font-size:14px;margin-bottom:20px; }
    .top-right { text-align:right;padding-top:3px;color:#85929b;font-size:12px; }
    .live-dot { display:inline-block;width:7px;height:7px;border-radius:50%;background:#18b987;margin:0 7px 1px 0;box-shadow:0 0 0 4px #e1f8f0; }
    .panel { background:white;border:1px solid #e9edef;border-radius:16px;padding:20px 22px;box-shadow:0 4px 16px rgba(21,40,50,.025); }
    .panel-title { font-weight:700;font-size:15px;color:#15222e; }
    .panel-caption { color:#85919b;font-size:12px;margin-top:3px; }
    .metric-card { background:white;border:1px solid #e9edef;border-radius:14px;padding:16px 18px;min-height:102px; }
    .metric-label { color:#89959e;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.8px; }
    .metric-value { font-size:23px;font-weight:750;letter-spacing:-.5px;color:#14212b;margin-top:7px; }
    .metric-note { color:#9aa4aa;font-size:11px;margin-top:2px; }
    .signal-card { background:#10271f;border-radius:17px;padding:22px 24px;color:white;min-height:250px;position:relative;overflow:hidden; }
    .signal-card:after { content:'';position:absolute;width:180px;height:180px;right:-54px;top:-54px;border-radius:50%;background:rgba(26,192,139,.10); }
    .signal-label { color:#a2b9af;font-size:11px;text-transform:uppercase;letter-spacing:1.3px;font-weight:700; }
    .signal-value { font-size:42px;font-weight:800;letter-spacing:-1px;margin-top:14px;line-height:1; }
    .signal-meta { color:#a8c2b6;font-size:13px;margin-top:13px; }
    .confidence-track { height:5px;border-radius:6px;background:#30483d;margin-top:18px;overflow:hidden; }
    .confidence-fill { height:100%;background:#25d39d;border-radius:6px; }
    .notice { border-radius:12px;background:#edf6ff;border:1px solid #dcecf9;padding:14px 16px;color:#486580;font-size:13px; }
    .sample-tag { display:inline-block;border-radius:20px;padding:5px 9px;background:#fff4dc;color:#9b7225;font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase; }
    div[data-testid="stButton"] button { border-radius:10px;border:0;background:#16b887;color:#082c22;font-weight:700;height:44px;transition:.15s; }
    div[data-testid="stButton"] button:hover { background:#0ca878;color:#fff; }
    div[data-testid="stFileUploader"] section { border-radius:12px;border-color:#3b4a55; }
    .stSelectbox label,.stSlider label,.stNumberInput label { color:#c0cbd2!important;font-size:12px!important; }
    div[data-testid="stDataFrame"] { border:1px solid #edf0f1;border-radius:10px;overflow:hidden; }
    hr { border-color:#e9edef; }
    .footer { color:#99a4aa;font-size:11px;text-align:center;padding:20px 0 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_state():
    for key, value in {"bars": None, "source_name": None, "trained": None, "signal": None}.items():
        if key not in st.session_state:
            st.session_state[key] = value


def chart_for(data: pd.DataFrame, live_price: float | None = None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["timestamp"], y=data["price"], mode="lines", name="BTC / USDT",
        line=dict(color="#18b887", width=2),
        fill="tozeroy", fillcolor="rgba(24,184,135,.07)",
        hovertemplate="%{x|%H:%M:%S}<br>$%{y:,.2f}<extra></extra>",
    ))
    if live_price is not None:
        fig.add_hline(y=live_price, line_dash="dot", line_color="#80939a", line_width=1)
    fig.update_layout(
        height=310, margin=dict(l=0,r=8,t=18,b=0), paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, hovermode="x unified",
        font=dict(family="DM Sans", color="#7f8b94", size=11),
        xaxis=dict(showgrid=False, zeroline=False, linecolor="#edf0f1", tickformat="%H:%M"),
        yaxis=dict(showgrid=True, gridcolor="#f0f3f3", zeroline=False, tickprefix="$", tickformat=",.0f", side="right"),
    )
    return fig


def sample_data():
    # Preview values mirror the supplied example and are intentionally synthetic.
    idx = pd.date_range("2026-10-11 09:00", periods=1829, freq="s")
    base = 59980 + pd.Series(range(1829)).map(lambda i: -0.19*i + 100*__import__("math").sin(i/48) + 24*__import__("math").sin(i/7)).to_numpy()
    return pd.DataFrame({"timestamp": idx, "price": base, "qty": 1.0, "buy": .5, "n": 1})


init_state()

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◈</div><span>stream<span style="color:#20cf9a">light</span></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Signal workspace</div>', unsafe_allow_html=True)
    st.markdown("\n")
    st.selectbox("Market", ["BTC / USDT"], index=0, help="Market symbol configured in your .env")
    bar_seconds = st.slider("Bar size", min_value=1, max_value=10, value=1, help="Group trades into bars of this many seconds.")
    predict_ahead = st.slider("Predict ahead", min_value=3, max_value=30, value=10, help="Number of bars used for the future label.")
    class_share = st.slider("BUY / SELL share", min_value=10, max_value=40, value=25, help="Tail share used to define BUY and SELL labels.")
    st.markdown("\n")
    st.markdown('<div class="eyebrow">Your market data</div>', unsafe_allow_html=True)
    upload = st.file_uploader("Upload trade CSV", type=["csv"], label_visibility="collapsed", help="Binance raw trades or a CSV with timestamp, price, quantity, and side columns.")
    if upload is not None and (st.session_state.source_name != upload.name):
        try:
            raw = crypto.load_trades(io.BytesIO(upload.getvalue()))
            bars = crypto.features(crypto.to_bars(raw, bar_seconds)).dropna(subset=crypto.FEATS)
            if bars.empty:
                st.error("Not enough valid trades to calculate the model features.")
            else:
                st.session_state.bars = bars.tail(30000).reset_index(drop=True)
                st.session_state.source_name = upload.name
                st.session_state.trained = None
                st.session_state.signal = None
                st.success(f"Loaded {len(bars):,} feature-ready bars")
        except Exception as exc:
            st.error(f"Could not read this CSV: {exc}")
    if st.session_state.bars is not None and st.button("Clear uploaded data", use_container_width=True):
        st.session_state.bars = None
        st.session_state.source_name = None
        st.session_state.trained = None
        st.session_state.signal = None
        st.rerun()
    st.markdown("\n")
    st.markdown('<div style="font-size:11px;color:#82909a;line-height:1.6">Paper money only · Signals are educational examples, not financial advice.</div>', unsafe_allow_html=True)

bars = st.session_state.bars
is_sample = bars is None
display_bars = sample_data() if is_sample else bars

head_l, head_r = st.columns([3, 1])
with head_l:
    st.markdown('<div class="eyebrow">Market intelligence · BTC / USDT</div><div class="hero-title">Crypto signal dashboard</div><div class="hero-sub">Machine learning insights from Binance trade data, made clear.</div>', unsafe_allow_html=True)
with head_r:
    st.markdown('<div class="top-right"><span class="live-dot"></span>Signal engine ready<br><span style="font-size:11px">Supervised models · Paper trading</span></div>', unsafe_allow_html=True)

price_now = float(display_bars["price"].iloc[-1])
m1, m2, m3, m4 = st.columns(4)
for col, label, value, note in [
    (m1, "Market price", f"${price_now:,.2f}", "BTC / USDT"),
    (m2, "Bars analyzed", f"{len(display_bars):,}", "1-second trade bars" if is_sample else st.session_state.source_name),
    (m3, "Selected model", "Random Forest", "200 estimators · max depth 5"),
    (m4, "Account mode", "Paper", "No real orders are placed"),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

st.markdown("\n")
chart_col, signal_col = st.columns([1.75, 1], gap="large")
with chart_col:
    st.markdown('<div class="panel"><div class="panel-title">Price movement</div><div class="panel-caption">Recent market bars · hover to inspect price</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_for(display_bars), use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
    if is_sample:
        st.markdown('<div style="margin-top:9px"><span class="sample-tag">Sample preview</span> <span style="color:#95a0a5;font-size:11px">Illustrative data based on the supplied output. Upload a CSV to calculate your own results.</span></div>', unsafe_allow_html=True)

with signal_col:
    result = st.session_state.signal
    if result:
        sig, conf, live_price, plan = result
        color = {"BUY":"#32d49e", "SELL":"#ff7f76", "HOLD":"#f3c969"}[sig]
        st.markdown(f'<div class="signal-card"><div class="signal-label"><span class="live-dot"></span>Latest model signal</div><div class="signal-value" style="color:{color}">{sig}</div><div class="signal-meta">Confidence <b>{conf:.0%}</b> &nbsp;·&nbsp; Price <b>${live_price:,.2f}</b></div><div class="confidence-track"><div class="confidence-fill" style="width:{conf:.0%}"></div></div></div>', unsafe_allow_html=True)
        st.markdown("\n")
        st.markdown(f'<div class="notice"><b>Paper plan</b><br>{plan}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-card"><div class="signal-label">Signal preview <span class="sample-tag" style="margin-left:7px">Illustrative</span></div><div class="signal-value" style="color:#32d49e">BUY</div><div class="signal-meta">Confidence <b>62%</b> &nbsp;·&nbsp; Price <b>$82,988.36</b></div><div class="confidence-track"><div class="confidence-fill" style="width:62%"></div></div></div>', unsafe_allow_html=True)
        st.markdown("\n")
        st.markdown('<div class="notice"><b>Paper plan</b><br>Paper BUY: spend 100.00 USDT = 0.001205 coin</div>', unsafe_allow_html=True)
    model_options = list(crypto.get_models().keys())
    chosen_model = st.selectbox("Model for live signal", model_options, index=min(1, len(model_options)-1))
    if st.button("Get live signal", use_container_width=True):
        if not st.session_state.trained:
            st.warning("Train the models first to generate a signal.")
        else:
            try:
                live_model = st.session_state.trained[chosen_model]["model"]
                with st.spinner("Requesting recent Binance trades…"):
                    sig, conf, live_price = crypto.live_signal(live_model, sec=bar_seconds)
                plan = crypto.paper_plan(sig, live_price, cash=1000.0, risk_pct=class_share)
                st.session_state.signal = (sig, conf, live_price, plan)
                st.rerun()
            except Exception as exc:
                st.error(f"Could not fetch a live signal: {exc}")

st.markdown("\n")
table_col, train_col = st.columns([1.65, 1], gap="large")
with table_col:
    st.markdown('<div class="panel"><div class="panel-title">Model performance</div><div class="panel-caption">Accuracy compared with the majority-class baseline</div>', unsafe_allow_html=True)
    if st.session_state.trained:
        rows = [{"Model": name, "Accuracy": f"{item['accuracy']:.3f}", "Baseline": f"{item['baseline']:.3f}", "Status": "Above baseline" if item["accuracy"] > item["baseline"] else "Below baseline"} for name, item in st.session_state.trained.items()]
    else:
        rows = [
            {"Model":"Decision Tree", "Accuracy":"0.376", "Baseline":"0.611", "Status":"Below baseline"},
            {"Model":"Random Forest", "Accuracy":"0.389", "Baseline":"0.611", "Status":"Below baseline"},
        ]
        if "XGBoost" in crypto.get_models():
            rows.append({"Model":"XGBoost", "Accuracy":"—", "Baseline":"0.611", "Status":"Train to calculate"})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True, height=174)
    st.markdown('<div style="color:#98a2a8;font-size:11px;margin-top:8px">Accuracy should beat baseline; otherwise the model learned little useful signal.</div></div>', unsafe_allow_html=True)
with train_col:
    st.markdown('<div class="panel"><div class="panel-title">Train your models</div><div class="panel-caption">Fit and compare the available classifiers</div>', unsafe_allow_html=True)
    st.markdown("\n")
    if is_sample:
        st.markdown('<div class="notice">Upload your Binance or trade CSV to train models on real input data. The table shows the supplied sample output.</div>', unsafe_allow_html=True)
    can_train = not is_sample and len(display_bars) >= 100
    if st.button("Train models", use_container_width=True, disabled=not can_train):
        trained = {}
        models = crypto.get_models()
        progress = st.progress(0, text="Preparing models…")
        for i, (name, model) in enumerate(models.items(), start=1):
            try:
                accuracy, baseline = crypto.train(display_bars, model, ahead=predict_ahead, tail=class_share / 100)
                trained[name] = {"model": model, "accuracy": accuracy, "baseline": baseline}
            except Exception as exc:
                st.warning(f"{name} could not be trained: {exc}")
            progress.progress(i / len(models), text=f"Trained {name}")
        st.session_state.trained = trained
        st.session_state.signal = None
        st.rerun()
    if st.session_state.trained:
        st.success(f"{len(st.session_state.trained)} model(s) trained on {len(display_bars):,} bars.")
    elif not is_sample:
        st.caption("Upload data is ready. Train to refresh the comparison.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="footer">STREAM LIGHT &nbsp;·&nbsp; Sample preview uses illustrative values &nbsp;·&nbsp; Paper money only</div>', unsafe_allow_html=True)
