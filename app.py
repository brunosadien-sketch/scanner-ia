import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Trading System V14 STABLE", layout="wide")

st.title("🚀 AI Trading System V14 - STABLE VERSION")

stocks = ["AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN"]

# -------- STRATEGY -------- #

def strategy_ma(data, short, long):
    data = data.copy()

    data["MA_S"] = data["Close"].rolling(short).mean()
    data["MA_L"] = data["Close"].rolling(long).mean()

    data["Signal"] = 0.0

    data.loc[data["MA_S"] > data["MA_L"], "Signal"] = 1.0
    data.loc[data["MA_S"] < data["MA_L"], "Signal"] = -1.0

    # 🔥 nettoyage complet
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
            "Best Strategy": f"MA{best_params[0]}/MA{best_params[1]}",
            "Performance": round(best_perf, 2)
        })

    except:
        continue

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

if not df.empty:

    st.subheader("🏆 Best Strategies")
    st.dataframe(df, use_container_width=True)

    best_global = df.sort_values(by="Performance", ascending=False).iloc[0]

    st.subheader("🔥 Best Global Strategy")
    st.write(best_global)

    # -------- LIVE SIGNAL -------- #

    st.subheader("📊 Live Signal")

    best_stock = best_global["Stock"]

    data = yf.download(best_stock, period="3mo", progress=False)

    if not data.empty:

        data = data.dropna()

        short, long = map(int, best_global["Best Strategy"].replace("MA","").split("/"))

        data = strategy_ma(data, short, long)

        last_signal = float(data["Signal"].iloc[-1])

        signal = "📈 BUY" if last_signal == 1.0 else "📉 SELL"

        st.metric("Signal actuel", signal)

else:
    st.error("❌ Aucune donnée disponible")
