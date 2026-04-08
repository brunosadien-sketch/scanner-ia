import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Scanner IA V6", layout="wide")

st.title("🚀 Scanner IA V6 - Pro Trading Tool")

API_KEY = st.secrets["FINNHUB_API_KEY"]
TG_TOKEN = st.secrets["TELEGRAM_TOKEN"]
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# 📡 Liste large (simule 100+ actions)
stocks = [
    "AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN","GOOGL",
    "PLTR","SOFI","UPST","RKLB","AFRM","IONQ","LCID","RIVN",
    "SNAP","ROKU","SHOP","COIN","SQ","NET","CRWD","ZS","OKTA"
]

def get_data(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    return requests.get(url).json()

def analyze_stock(symbol):
    try:
        d = get_data(symbol)

        c = d.get("c", 0)
        pc = d.get("pc", 0)
        h = d.get("h", 0)
        l = d.get("l", 0)

        if c == 0 or pc == 0:
            return None

        momentum = (c - pc) / pc
        volatility = (h - l) / c if c != 0 else 0

        score = (momentum * 100 * 0.7) + (volatility * 100 * 0.3)

        # 🤖 IA gratuite
        if score > 6:
            signal = "🔥 Forte opportunité"
        elif score > 3:
            signal = "📈 Potentiel intéressant"
        else:
            signal = "⚠️ Faible signal"

        return {
            "Stock": symbol,
            "Prix": round(c, 2),
            "Momentum %": round(momentum * 100, 2),
            "Volatility %": round(volatility * 100, 2),
            "Score": round(score, 2),
            "Signal": signal
        }

    except:
        return None

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# -------- SCAN -------- #

results = []

with st.spinner("🔍 Scan du marché..."):
    for stock in stocks:
        res = analyze_stock(stock)
        if res:
            results.append(res)
        time.sleep(0.2)

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

if not df.empty:

    df = df.sort_values(by="Score", ascending=False)

    df_filtered = df[df["Momentum %"] > 0]

    st.subheader("🏆 Opportunités détectées")
    st.dataframe(df_filtered, use_container_width=True)

    top = df_filtered.head(5)

    st.subheader("🔥 Top 5")
    st.write(top)

    # 🔔 Alertes Telegram
    strong = df_filtered[df_filtered["Score"] > 6]

    if not strong.empty:
        st.success("🚨 Signal fort détecté !")

        message = "🚨 Opportunités détectées:\n\n"
        for _, row in strong.iterrows():
            message += f"{row['Stock']} | Score: {row['Score']}\n"

        if st.button("📲 Envoyer alerte Telegram"):
            send_telegram(message)
            st.success("Message envoyé !")

    stock_selected = st.selectbox("📊 Analyse détaillée", df_filtered["Stock"])
    st.write(df[df["Stock"] == stock_selected])

else:
    st.error("❌ Aucun résultat")
