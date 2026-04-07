import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Scanner IA Small Caps", layout="wide")

st.title("🚀 Scanner IA - Opportunités Small & Mid Caps")

stocks = [
    "PLTR","SOFI","UPST","RKLB","FUBO","AFRM","OPEN",
    "RUN","IONQ","LCID","HOOD","RIVN","U","PATH"
]

@st.cache_data
def analyze_stock(ticker):
    try:
        data = yf.download(ticker, period="6mo", progress=False)

        if len(data) < 50:
            return None

        data["Return"] = data["Close"].pct_change()

        momentum = data["Return"].mean()
        volatility = data["Return"].std()

        ma20 = data["Close"].rolling(20).mean().iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]

        trend = 1 if ma20 > ma50 else -1

        avg_volume = data["Volume"].mean()
        recent_volume = data["Volume"].iloc[-1]
        volume_spike = recent_volume / avg_volume

        score = (
            (momentum * 100) * 0.4 +
            (trend * 0.2) +
            (volume_spike * 0.2) -
            (volatility * 0.2)
        )

        return {
            "Stock": ticker,
            "Score": score,
            "Momentum": momentum,
            "Volatility": volatility,
            "Trend": trend,
            "Volume Spike": volume_spike
        }

    except:
        return None


results = []

with st.spinner("Analyse en cours..."):
    for stock in stocks:
        res = analyze_stock(stock)
        if res:
            results.append(res)

df = pd.DataFrame(results)

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🏆 Top opportunités")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("🎯 Top 3")
        st.write(df.head(3))

    stock_selected = st.selectbox("📊 Analyse détaillée", df["Stock"])

    data = yf.download(stock_selected, period="6mo", progress=False)

    st.subheader(f"📈 Graphique : {stock_selected}")
    st.line_chart(data["Close"])

else:
    st.error("Erreur lors de l'analyse.")
