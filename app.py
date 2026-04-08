import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime
import os

st.set_page_config(page_title="AI TRADING SYSTEM V8", layout="wide")

st.title("🚀 AI Trading System V8 (Pro)")

API_KEY = st.secrets["FINNHUB_API_KEY"]

# -------- STOCK UNIVERSE (scalable) -------- #

stocks = [
    "AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN","GOOGL",
    "PLTR","SOFI","UPST","RKLB","AFRM","IONQ","LCID","RIVN",
    "SNAP","ROKU","SHOP","COIN","SQ","NET","CRWD","ZS","OKTA",
    "TTD","DDOG","MDB","AI","SNOW","DOCU","ZM","PINS"
]

# -------- DATA -------- #

def get_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    return requests.get(url).json()

# -------- NEWS SENTIMENT -------- #

def sentiment_score(symbol):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&token={API_KEY}"
        news = requests.get(url).json()

        score = 0
        for article in news[:5]:
            h = article.get("headline","").lower()
            if "beat" in h or "growth" in h:
                score += 1
            if "miss" in h or "risk" in h:
                score -= 1

        return score
    except:
        return 0

# -------- ANALYSIS -------- #

def analyze(symbol):
    try:
        d = get_quote(symbol)

        c = d.get("c",0)
        pc = d.get("pc",0)
        h = d.get("h",0)
        l = d.get("l",0)

        if c == 0 or pc == 0:
            return None

        momentum = (c-pc)/pc
        volatility = (h-l)/c

        sentiment = sentiment_score(symbol)

        score = (
            momentum*100*0.5 +
            volatility*100*0.3 +
            sentiment*2
        )

        return {
            "Stock": symbol,
            "Price": round(c,2),
            "Momentum": round(momentum*100,2),
            "Volatility": round(volatility*100,2),
            "Sentiment": sentiment,
            "Score": round(score,2)
        }

    except:
        return None

# -------- SCAN -------- #

results = []

with st.spinner("Scanning market..."):
    for s in stocks:
        r = analyze(s)
        if r:
            results.append(r)
        time.sleep(0.2)

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

if not df.empty:

    df = df.sort_values(by="Score", ascending=False)
    df = df[df["Momentum"] > 0]

    st.subheader("🏆 Opportunities")
    st.dataframe(df, use_container_width=True)

    top = df.head(5)

    # -------- PORTFOLIO -------- #

    st.subheader("💰 Portfolio")

    portfolio = top.copy()
    portfolio["Allocation %"] = 100/len(portfolio)

    st.write(portfolio)

    # -------- PERFORMANCE TRACKING -------- #

    file = "portfolio.csv"

    if os.path.exists(file):
        history = pd.read_csv(file)
    else:
        history = pd.DataFrame()

    snapshot = portfolio.copy()
    snapshot["Date"] = datetime.now()

    history = pd.concat([history, snapshot])
    history.to_csv(file, index=False)

    st.subheader("📊 Portfolio History")
    st.line_chart(history.groupby("Date")["Score"].mean())

    # -------- BACKTEST SIMPLE -------- #

    st.subheader("📈 Backtest (approximation)")

    avg_score = df["Score"].mean()
    st.metric("Market Strength", avg_score)

    # -------- DETAILS -------- #

    stock = st.selectbox("Select stock", df["Stock"])
    st.write(df[df["Stock"] == stock])

else:
    st.error("No data")
