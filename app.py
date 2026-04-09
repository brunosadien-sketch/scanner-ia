import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time

st.set_page_config(page_title="AI Trading System V11", layout="wide")

st.title("🚀 AI Trading System V11 - Dynamic Market Scanner")

TG_TOKEN = st.secrets["TELEGRAM_TOKEN"]
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# -------- TELEGRAM -------- #
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -------- DYNAMIC UNIVERSE -------- #

def get_universe():
    # US Small & Mid Caps (sample large)
    us = [
        "PLTR","SOFI","UPST","RKLB","AFRM","IONQ","LCID","RIVN",
        "FUBO","OPEN","RUN","U","PATH","HOOD","AI","SNOW"
    ]

    # Europe
    eu = [
        "AIR.PA","MC.PA","OR.PA","BNP.PA","SAN.PA",
        "SAP.DE","ASML.AS","ADYEN.AS"
    ]

    return us + eu

# -------- FAST FILTER -------- #

def fast_filter(stocks):
    selected = []

    for s in stocks:
        try:
            data = yf.download(s, period="1mo", progress=False)

            if data.empty:
                continue

            vol = data["Volume"].mean()
            returns = data["Close"].pct_change().std()

            # Filtre intelligent
            if vol > 300000 and returns > 0.02:
                selected.append(s)

        except:
            continue

    return selected

# -------- ANALYSIS -------- #

def analyze(stock):
    try:
        data = yf.download(stock, period="6mo", progress=False)

        if len(data) < 50:
            return None

        data["MA20"] = data["Close"].rolling(20).mean()
        data["Return"] = data["Close"].pct_change()

        last = data.iloc[-1]

        momentum = data["Return"].mean()
        volatility = data["Return"].std()

        score = momentum*100*0.6 + volatility*100*0.4

        signal = "HOLD"
        if momentum > 0.02 and score > 5:
            signal = "BUY"
        elif momentum < -0.01:
            signal = "SELL"

        return {
            "Stock": stock,
            "Price": round(last["Close"],2),
            "Momentum": round(momentum*100,2),
            "Volatility": round(volatility*100,2),
            "Score": round(score,2),
            "Signal": signal
        }

    except:
        return None

# -------- MAIN -------- #

universe = get_universe()

st.write(f"🌍 Universe size: {len(universe)}")

with st.spinner("⚡ Filtering market..."):
    filtered = fast_filter(universe)

st.write(f"🎯 After filter: {len(filtered)} stocks")

results = []

with st.spinner("🔍 Scanning opportunities..."):
    for stock in filtered:
        res = analyze(stock)
        if res:
            results.append(res)
        time.sleep(0.1)

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

if not df.empty:

    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🏆 Opportunities")
    st.dataframe(df, use_container_width=True)

    # -------- ALERTES -------- #

    buys = df[df["Signal"] == "BUY"]

    if not buys.empty:
        msg = "🚨 BUY SIGNALS 🚨\n\n"
        for _, row in buys.iterrows():
            msg += f"{row['Stock']} Score:{row['Score']}\n"

        send_telegram(msg)
        st.success("📲 Telegram alert sent")

    # -------- TOP PICKS -------- #

    st.subheader("🔥 Top Picks")
    st.write(df.head(5))

    # -------- DETAIL -------- #

    stock = st.selectbox("📊 Select stock", df["Stock"])
    st.write(df[df["Stock"] == stock])

else:
    st.error("No opportunities found")
