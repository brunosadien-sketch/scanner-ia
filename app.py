import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests

st.set_page_config(page_title="AI Trading System V15", layout="wide")

st.title("🚀 AI Trading System V15 - Small & Mid Caps + Alerts")

# -------- TELEGRAM -------- #

def send_telegram(msg):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": msg})

    except:
        st.warning("⚠️ Telegram non configuré")

# -------- STOCK LIST (SMALL / MID CAPS) -------- #

stocks = [
    # US
    "SOFI","PLTR","UPST","AFRM","OPEN","RUN","IONQ","RKLB","FUBO","LCID","HOOD","RIVN","PATH","U",
    
    # Europe
    "ALNOV.PA","ATE.PA","SOI.PA","DBK.DE","VOW3.DE","ADYEN.AS","ASML.AS"
]

# -------- STRATEGY -------- #

def strategy_ma(data, short, long):
    data = data.copy()

    data["MA_S"] = data["Close"].rolling(short).mean()
    data["MA_L"] = data["Close"].rolling(long).mean()

    data["Signal"] = 0.0
    data.loc[data["MA_S"] > data["MA_L"], "Signal"] = 1.0
    data.loc[data["MA_S"] < data["MA_L"], "Signal"] = -1.0

    data["Signal"] = data["Signal"].fillna(0).astype(float)

    return data

# -------- BACKTEST -------- #

def backtest(data):
    capital = 1000.0
    position = 0.0

    for i in range(len(data)):
        try:
            signal = float(data["Signal"].iloc[i])
            price = float(data["Close"].iloc[i])
        except:
            continue

        if np.isnan(signal) or np.isnan(price):
            continue

        if signal == 1.0 and position == 0.0:
            position = capital / price
            capital = 0.0

        elif signal == -1.0 and position > 0.0:
            capital = position * price
            position = 0.0

    final_value = capital if capital > 0 else position * float(data["Close"].iloc[-1])
    return final_value

# -------- MAIN -------- #

results = []

for stock in stocks:

    try:
        data = yf.download(stock, period="1y", progress=False)

        if data.empty or len(data) < 100:
            continue

        data = data.dropna()

        best_perf = 0
        best_params = (0, 0)

        for short in [5, 10, 20]:
            for long in [30, 50, 100]:

                if short >= long:
                    continue

                temp = strategy_ma(data, short, long)
                perf = backtest(temp)

                if perf > best_perf:
                    best_perf = perf
                    best_params = (short, long)

        results.append({
            "Stock": stock,
            "Strategy": f"MA{best_params[0]}/{best_params[1]}",
            "Performance": round(best_perf, 2)
        })

    except:
        continue

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

if not df.empty:

    df = df.sort_values(by="Performance", ascending=False)

    st.subheader("🏆 Top Opportunités")
    st.dataframe(df, use_container_width=True)

    # -------- ALERTES -------- #

    strong = df[df["Performance"] > 1200]  # seuil

    if not strong.empty:

        msg = "🚨 OPPORTUNITÉS DÉTECTÉES 🚨\n\n"

        for _, row in strong.iterrows():
            msg += f"{row['Stock']} | {row['Strategy']} | Perf: {row['Performance']}\n"

        send_telegram(msg)

        st.success("📲 Alerte Telegram envoyée")

    else:
        st.info("Aucune opportunité forte")

else:
    st.error("❌ Aucune donnée récupérée")
