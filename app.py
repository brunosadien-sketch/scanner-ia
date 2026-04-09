import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="AI Trading System V14", layout="wide")

st.title("🚀 AI Trading System V14 - Auto Optimization")

stocks = ["AAPL","MSFT","NVDA","TSLA","AMD","META","AMZN"]

# -------- STRATEGIES -------- #

def strategy_ma(data, short, long):
    data["MA_S"] = data["Close"].rolling(short).mean()
    data["MA_L"] = data["Close"].rolling(long).mean()

    data["Signal"] = 0
    data.loc[data["MA_S"] > data["MA_L"], "Signal"] = 1
    data.loc[data["MA_S"] < data["MA_L"], "Signal"] = -1

    return data

def backtest(data):
    capital = 1000
    position = 0

    for i in range(50, len(data)):

        if data["Signal"].iloc[i] == 1 and position == 0:
            position = capital / data["Close"].iloc[i]
            capital = 0

        elif data["Signal"].iloc[i] == -1 and position > 0:
            capital = position * data["Close"].iloc[i]
            position = 0

    final = capital if capital > 0 else position * data["Close"].iloc[-1]
    return final

# -------- AUTO OPTIMIZATION -------- #

results = []

for stock in stocks:

    data = yf.download(stock, period="1y", progress=False)

    best_perf = 0
    best_params = None

    for short in [5,10,20]:
        for long in [30,50,100]:

            if short >= long:
                continue

            temp = data.copy()
            temp = strategy_ma(temp, short, long)

            perf = backtest(temp)

            if perf > best_perf:
                best_perf = perf
                best_params = (short, long)

    results.append({
        "Stock": stock,
        "Best Strategy": f"MA{best_params[0]}/MA{best_params[1]}",
        "Performance": round(best_perf,2)
    })

df = pd.DataFrame(results)

# -------- DISPLAY -------- #

st.subheader("🏆 Best Strategies")

st.dataframe(df)

best_global = df.sort_values(by="Performance", ascending=False).iloc[0]

st.subheader("🔥 Best Global Strategy")
st.write(best_global)

# -------- LIVE SIGNAL -------- #

st.subheader("📊 Live Signal")

best_stock = best_global["Stock"]

data = yf.download(best_stock, period="3mo", progress=False)

short, long = map(int, best_global["Best Strategy"].replace("MA","").split("/"))

data = strategy_ma(data, short, long)

last_signal = data["Signal"].iloc[-1]

signal = "BUY" if last_signal == 1 else "SELL"

st.metric("Signal actuel", signal)
