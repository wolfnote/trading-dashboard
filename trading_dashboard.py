import streamlit as st
import pandas as pd
import mysql.connector

# ----- Streamlit UI Setup -----
st.set_page_config(page_title="Trading Dashboard", layout="wide")
st.title("📈 Trading Tracker Dashboard")

# ----- Database Connection Function -----
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=st.secrets["host"],
        user=st.secrets["user"],
        password=st.secrets["password"],
        database=st.secrets["database"],
        ssl_ca="cacert.pem"  # Use only ssl_ca with PlanetScale
    )

# ----- Connect -----
conn = get_connection()

# ----- Load Trades Data -----
df = pd.read_sql("SELECT * FROM trades ORDER BY trade_date", conn)

# ----- Main Table -----
st.subheader("🧾 All Trades")
st.dataframe(df, use_container_width=True)

# ----- Charts -----
col1, col2 = st.columns(2)

# 📊 Profit by Strategy
with col1:
    st.subheader("💼 Profit by Strategy")
    strategy_profit = df.groupby("strategy")["net_gain_loss"].sum().sort_values(ascending=False)
    st.bar_chart(strategy_profit)

# 📆 Monthly Profit
with col2:
    st.subheader("📅 Monthly Profit")
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df['month'] = df['trade_date'].dt.to_period('M')
    monthly_profit = df.groupby('month')['net_gain_loss'].sum()
    st.bar_chart(monthly_profit)

# ----- KPIs -----
total_profit = df['net_gain_loss'].sum()
win_rate = df['win_flag'].mean() * 100 if len(df) > 0 else 0
num_trades = len(df)

st.markdown("---")
st.subheader("📊 Key Stats")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Profit", f"${total_profit:,.2f}")
kpi2.metric("Win Rate", f"{win_rate:.1f}%")
kpi3.metric("Total Trades", f"{num_trades}")