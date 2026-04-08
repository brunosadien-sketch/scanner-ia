import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Scanner IA PRO", layout="wide")

st.title("🚀 Scanner IA PRO - Opportunités Marché")

API_KEY = st.secrets["FINNHUB_API_KEY"]

# Liste élargie (tu peux en ajouter)
stocks = [
    "PLTR","SOFI","UPST","RKLB","AFRM",
    "IONQ","LCID","RIVN","HOOD","U"
]

def get_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    r = requests.get(url)
    return r.json()

def analyze_stock(symbol):
    try:
        data = get_data(symbol)

        current = data.get("c", 0)
        prev_close = data.get("pc", 0)
        high = data.get("h", 0)
        low = data.get("l", 0)

        if current == 0 or prev_close == 0:
            return None

        momentum = (current - prev_close) / prev_close
        volatility = (high - low) / current if current != 0 else 0

        score = (momentum * 100) - (volatility * 10)

        return {
            "Stock": symbol,
            "Prix": round(current, 2),
            "Momentum": round(momentum, 3),
            "Volatility": round(volatility, 3),
            "Score": round(score, 2)
        }

    except:
        st.warning(f"Erreur sur {symbol}")
        return None


results = []

with st.spinner("Analyse du marché en cours..."):
    for stock in stocks:
        res = analyze_stock(stock)
        if res:
            results.append(res)
        time.sleep(0.5)

df = pd.DataFrame(results)

if not df.empty:
    df = df.sort_values(by="Score", ascending=False)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🏆 Top opportunités")
        st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("🔥 Top 3")
        st.write(df.head(3))

    stock_selected = st.selectbox("📊 Détail", df["Stock"])

    st.subheader(f"📈 Données : {stock_selected}")
    st.write(df[df["Stock"] == stock_selected])

else:
    st.error("❌ Impossible de récupérer les données")
