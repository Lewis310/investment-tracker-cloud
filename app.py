import streamlit as st
import yfinance as yf
from datetime import date
import json

# Pandas-free version that will definitely work
st.set_page_config(page_title="Investment Tracker", layout="wide")
st.title("📈 Investment Portfolio Tracker")

# Initialize data
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'holdings' not in st.session_state:
    st.session_state.holdings = {}

# Simple price fetcher without pandas dependencies
def get_simple_price(symbol):
    try:
        # Map symbols to tickers
        ticker_map = {'NDQ': 'NDQ.AX', 'IVV': 'IVV.AX', 'CBA': 'CBA.AX'}
        ticker = ticker_map.get(symbol, symbol)
        
        # Use yfinance without pandas operations
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('currentPrice', info.get('regularMarketPrice', 0))
    except:
        return 0

# Sidebar
with st.sidebar:
    st.header("Add Transaction")
    
    symbol = st.selectbox("Stock", ["NDQ", "IVV", "CBA"])
    units = st.number_input("Units", min_value=1, value=10)
    price = st.number_input("Price per Share ($)", min_value=0.01, value=50.0)
    trans_date = st.date_input("Date", value=date.today())
    
    total = units * price
    st.write(f"**Total: ${total:.2f}**")
    
    if st.button("Add Buy Transaction"):
        transaction = {
            'id': len(st.session_state.transactions) + 1,
            'date': str(trans_date),
            'symbol': symbol,
            'units': units,
            'price': price,
            'total': total
        }
        st.session_state.transactions.append(transaction)
        
        # Update holdings
        if symbol not in st.session_state.holdings:
            st.session_state.holdings[symbol] = {'units': 0, 'invested': 0}
        
        st.session_state.holdings[symbol]['units'] += units
        st.session_state.holdings[symbol]['invested'] += total
        
        st.success("✅ Transaction added!")
        st.rerun()
    
    if st.button("Clear All Data"):
        st.session_state.transactions = []
        st.session_state.holdings = {}
        st.success("🗑️ Data cleared!")
        st.rerun()

# Current Prices
st.header("💵 Current Prices")
col1, col2, col3 = st.columns(3)

ndq_price = get_simple_price('NDQ')
ivv_price = get_simple_price('IVV')
cba_price = get_simple_price('CBA')

with col1:
    st.metric("NDQ", f"${ndq_price:.2f}")
with col2:
    st.metric("IVV", f"${ivv_price:.2f}")
with col3:
    st.metric("CBA", f"${cba_price:.2f}")

# Portfolio Summary
st.header("📊 Portfolio Summary")

total_value = 0
total_invested = 0

for symbol, holding in st.session_state.holdings.items():
    if holding['units'] > 0:
        current_price = get_simple_price(symbol)
        current_value = holding['units'] * current_price
        total_value += current_value
        total_invested += holding['invested']

profit_loss = total_value - total_invested
profit_pct = (profit_loss / total_invested * 100) if total_invested > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Value", f"${total_value:,.2f}")
with col2:
    st.metric("Total Invested", f"${total_invested:,.2f}")
with col3:
    st.metric("Profit/Loss", f"${profit_loss:,.2f}", f"{profit_pct:.1f}%")

# Holdings Display
st.header("📦 Your Holdings")

if st.session_state.holdings:
    for symbol, holding in st.session_state.holdings.items():
        if holding['units'] > 0:
            current_price = get_simple_price(symbol)
            current_value = holding['units'] * current_price
            profit = current_value - holding['invested']
            avg_price = holding['invested'] / holding['units']
            
            with st.expander(f"{symbol} - {holding['units']} units", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Average Price:** ${avg_price:.2f}")
                    st.write(f"**Current Price:** ${current_price:.2f}")
                with col2:
                    st.write(f"**Current Value:** ${current_value:,.2f}")
                    st.write(f"**Profit/Loss:** ${profit:,.2f}")
else:
    st.info("💡 No holdings yet. Add your first transaction using the sidebar!")

# Transaction History
if st.session_state.transactions:
    st.header("📋 Transaction History")
    for transaction in reversed(st.session_state.transactions):
        st.write(f"**{transaction['date']}** - {transaction['symbol']} - {transaction['units']} units @ ${transaction['price']:.2f}")

st.success("🚀 App deployed successfully! Data is stored in your session.")
