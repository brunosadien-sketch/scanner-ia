import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Scanner IA", layout="wide")

st.title("🚀 Scanner IA - Opportunités Small & Mid Caps")

# ⚠️ Moins d'actions = plus stable
stocks = ["PLTR","SOFI","UPST","RKLB","AFRM"]

def analyze_stock(ticker):
    try:
        data = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False,
            threads=False
        )

        if data.empty or len(data) < 20:
            return None

        data["Return"] = data["Close"].pct_change()

        momentum = data["Return"].mean()
        volatility = data["Return"].std()

        score = momentum / volatility if volatility != 0 else 0

        return {
            "Stock": ticker,
            "Score": round(score, 3),
            "Momentum": round(momentum, 4),
            "Volatility": round(volatility, 4)
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
        time.sleep(1)  # 🔥 évite blocage API

df = pd.DataFrame(results)

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🏆 Top opportunités")
    st.dataframe(df, use_container_width=True)

    stock_selected = st.selectbox("📊 Choisir une action", df["Stock"])

    try:
        data = yf.download(stock_selected, period="3mo", progress=False, threads=False)
        st.line_chart(data["Close"])
    except:
        st.warning("Erreur graphique")

else:
    st.error("❌ Impossible de récupérer les données (limite API)")
