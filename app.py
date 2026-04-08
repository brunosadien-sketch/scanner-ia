import streamlit as st
import requests
import pandas as pd
import time
import numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="AI Trading System V9", layout="wide")

st.title("🚀 AI Trading System V9")

API_KEY = st.secrets["FINNHUB_API_KEY"]
TG_TOKEN = st.secrets["TELEGRAM_TOKEN"]
CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

stocks = ["AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN","PLTR","SOFI","UPST"]

# -------- TELEGRAM -------- #
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# -------- DATA -------- #
def get_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
    return requests.get(url).json()

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

        score = momentum*100*0.7 + volatility*100*0.3

        signal = "HOLD"

        if momentum > 0.02 and score > 5:
            signal = "BUY"
        elif momentum < -0.01:
            signal = "SELL"

        return {
            "Stock": symbol,
            "Price": c,
            "Momentum": momentum,
            "Volatility": volatility,
            "Score": score,
            "Signal": signal
        }

    except:
        return None

# -------- ML MODEL -------- #
def train_model():
    X = np.random.rand(100,3)
    y = (X[:,0] + X[:,1] > 1).astype(int)

    model = RandomForestClassifier()
    model.fit(X,y)
    return model

model = train_model()

# -------- SCAN -------- #
results = []

for s in stocks:
    r = analyze(s)
    if r:
        results.append(r)
    time.sleep(0.2)

df = pd.DataFrame(results)

# -------- DISPLAY -------- #
if not df.empty:

    df = df.sort_values(by="Score", ascending=False)

    st.subheader("📊 Signaux")
    st.dataframe(df)

    # -------- ALERTES AUTO -------- #
    buys = df[df["Signal"] == "BUY"]

    if not buys.empty:
        msg = "🚨 BUY SIGNALS 🚨\n"
        for _, row in buys.iterrows():
            msg += f"{row['Stock']} Score:{round(row['Score'],2)}\n"

        send_telegram(msg)
        st.success("Alerte envoyée automatiquement")

    # -------- BACKTEST SIMPLE -------- #
    st.subheader("📊 Backtest")

    returns = []

    for i in range(len(df)):
        if df.iloc[i]["Signal"] == "BUY":
            returns.append(df.iloc[i]["Momentum"] * 100)

    if returns:
        st.metric("Performance moyenne (%)", round(np.mean(returns),2))

    # -------- ML PREDICTION -------- #
    st.subheader("🤖 ML Prediction")

    sample = np.array([[0.5,0.3,0.2]])
    pred = model.predict(sample)[0]

    st.write("Prediction marché :", "📈 Hausse" if pred == 1 else "📉 Baisse")

else:
    st.error("No data")
