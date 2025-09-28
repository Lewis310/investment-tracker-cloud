import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date

# Simple working version
st.set_page_config(page_title="Investment Tracker", layout="wide")
st.title("📈 Investment Portfolio Tracker")

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Ticker mappings
ticker_map = {'NDQ': 'NDQ.AX', 'IVV': 'IVV.AX', 'CBA': 'CBA.AX'}

def get_current_price(symbol):
    try:
        ticker = ticker_map.get(symbol, symbol)
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1d')
        return hist['Close'].iloc[-1] if not hist.empty else 0
    except:
        return 0

# Sidebar for adding transactions
with st.sidebar:
    st.header("Add Transaction")
    
    symbol = st.selectbox("Stock", ["NDQ", "IVV", "CBA"])
    units = st.number_input("Units", min_value=1, value=10)
    price = st.number_input("Price per Share ($)", min_value=0.01, value=50.0)
    trans_date = st.date_input("Date", value=date.today())
    
    total = units * price
    st.write(f"Total: ${total:.2f}")
    
    if st.button("Add Buy Transaction"):
        transaction = {
            'date': trans_date.isoformat(),
            'symbol': symbol,
            'units': units,
            'price': price,
            'total': total
        }
        st.session_state.transactions.append(transaction)
        st.success("Transaction added!")

# Display current prices
st.header("Current Prices")
col1, col2, col3 = st.columns(3)
with col1:
    ndq_price = get_current_price('NDQ')
    st.metric("NDQ", f"${ndq_price:.2f}")
with col2:
    ivv_price = get_current_price('IVV')
    st.metric("IVV", f"${ivv_price:.2f}")
with col3:
    cba_price = get_current_price('CBA')
    st.metric("CBA", f"${cba_price:.2f}")

# Calculate portfolio
if st.session_state.transactions:
    st.header("Your Portfolio")
    
    # Group by symbol
    portfolio = {}
    for trans in st.session_state.transactions:
        symbol = trans['symbol']
        if symbol not in portfolio:
            portfolio[symbol] = {'units': 0, 'invested': 0}
        portfolio[symbol]['units'] += trans['units']
        portfolio[symbol]['invested'] += trans['total']
    
    # Display holdings
    for symbol, data in portfolio.items():
        current_price = get_current_price(symbol)
        current_value = data['units'] * current_price
        profit = current_value - data['invested']
        
        st.subheader(symbol)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"Units: {data['units']}")
            st.write(f"Avg Price: ${data['invested']/data['units']:.2f}")
        with col2:
            st.write(f"Current Price: ${current_price:.2f}")
            st.write(f"Current Value: ${current_value:.2f}")
        with col3:
            st.write(f"Profit/Loss: ${profit:.2f}")
        st.divider()
else:
    st.info("Add your first transaction using the sidebar!")

# Transaction history
if st.session_state.transactions:
    st.header("Transaction History")
    for trans in reversed(st.session_state.transactions):
        st.write(f"{trans['date'][:10]} - {trans['symbol']} - {trans['units']} units @ ${trans['price']:.2f}")

st.success("App is running successfully!")
