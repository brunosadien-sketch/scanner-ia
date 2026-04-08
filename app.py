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
        data = yf.download(ticker, period="6mo", progress=False, threads=False)

        if data is None or data.empty or len(data) < 50:
            return None

        data["Return"] = data["Close"].pct_change()

        momentum = data["Return"].mean()
        volatility = data["Return"].std()

        ma20 = data["Close"].rolling(20).mean().iloc[-1]
        ma50 = data["Close"].rolling(50).mean().iloc[-1]

        trend = 1 if ma20 > ma50 else -1

        avg_volume = data["Volume"].mean()
        recent_volume = data["Volume"].iloc[-1]

        if avg_volume == 0:
            volume_spike = 0
        else:
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

    except Exception as e:
        st.warning(f"Erreur sur {ticker}")
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

    try:
        data = yf.download(stock_selected, period="6mo", progress=False, threads=False)

        if not data.empty:
            st.subheader(f"📈 Graphique : {stock_selected}")
            st.line_chart(data["Close"])
        else:
            st.warning("Pas de données pour ce stock")

    except:
        st.warning("Erreur affichage graphique")

else:
    st.error("❌ Aucune donnée récupérée (API lente ou bloquée)")
