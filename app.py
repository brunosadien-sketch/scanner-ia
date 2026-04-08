import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Scanner IA PRO V4", layout="wide")

st.title("🚀 Scanner IA V4 - Détection d'opportunités")

API_KEY = st.secrets["FINNHUB_API_KEY"]

# Liste élargie (tu peux encore l’agrandir)
stocks = [
    "PLTR","SOFI","UPST","RKLB","AFRM","IONQ","LCID","RIVN","HOOD","U",
    "SNAP","ROKU","SHOP","COIN","SQ","TTD","NET","CRWD","ZS","OKTA"
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

        # 📈 Momentum
        momentum = (current - prev_close) / prev_close

        # ⚡ Volatilité
        volatility = (high - low) / current if current != 0 else 0

        # 🎯 Filtre qualité
        if current < 1:
            return None

        # 🔥 Score amélioré
        score = (
            (momentum * 100 * 0.6) +
            (volatility * 100 * 0.4)
        )

        return {
            "Stock": symbol,
            "Prix": round(current, 2),
            "Momentum %": round(momentum * 100, 2),
            "Volatility %": round(volatility * 100, 2),
            "Score": round(score, 2)
        }

    except:
        return None


results = []

with st.spinner("🔍 Scan du marché en cours..."):
    for stock in stocks:
        res = analyze_stock(stock)
        if res:
            results.append(res)
        time.sleep(0.3)

df = pd.DataFrame(results)

if not df.empty:

    # 🔥 Tri intelligent
    df = df.sort_values(by="Score", ascending=False)

    # 📊 Filtre opportunités
    df_filtered = df[df["Momentum %"] > 0]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🏆 Opportunités détectées")
        st.dataframe(df_filtered, use_container_width=True)

    with col2:
        st.subheader("🔥 Top 5")
        st.write(df_filtered.head(5))

    # 📈 Détail
    stock_selected = st.selectbox("📊 Analyse d'une action", df_filtered["Stock"])

    st.subheader(f"📌 Détails : {stock_selected}")
    st.write(df[df["Stock"] == stock_selected])

else:
    st.error("❌ Aucun résultat (API ou limite atteinte)")
