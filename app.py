import streamlit as st
import requests
from datetime import date, datetime
import json

st.set_page_config(page_title="Investment Tracker", layout="wide")
st.title("📈 Investment Portfolio Tracker")

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []

# Alternative price API (Yahoo Finance alternative)
def get_stock_price(symbol):
    """Get stock price using Alpha Vantage API (free tier)"""
    try:
        # Map symbols
        symbol_map = {'NDQ': 'NDQ.AX', 'IVV': 'IVV.AX', 'CBA': 'CBA.AX'}
        yahoo_symbol = symbol_map.get(symbol, symbol)
        
        # Use Yahoo Finance API directly (simpler than yfinance)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart']:
            return data['chart']['result'][0]['meta']['regularMarketPrice']
        return 0
    except:
        return 0

# Fallback prices (manual updates)
fallback_prices = {
    'NDQ': 32.50,  # You can update these manually
    'IVV': 65.80,
    'CBA': 115.25
}

def get_price(symbol):
    price = get_stock_price(symbol)
    return price if price > 0 else fallback_prices.get(symbol, 0)

# Sidebar for transactions
with st.sidebar:
    st.header("Add Transaction")
    
    symbol = st.selectbox("Stock", ["NDQ", "IVV", "CBA"])
    units = st.number_input("Units", min_value=1, value=10)
    price = st.number_input("Price per Share ($)", min_value=0.01, value=50.0)
    trans_date = st.date_input("Date", value=date.today())
    
    total = units * price
    st.write(f"**Total: ${total:.2f}**")
    
    if st.button("Add Transaction"):
        transaction = {
            'id': len(st.session_state.transactions) + 1,
            'date': trans_date.isoformat(),
            'symbol': symbol,
            'units': units,
            'price': price,
            'total': total
        }
        st.session_state.transactions.append(transaction)
        st.success("✅ Transaction added!")
        st.rerun()
    
    if st.button("Clear All Data"):
        st.session_state.transactions = []
        st.success("🗑️ Data cleared!")
        st.rerun()
    
    # Manual price updates
    st.header("Manual Price Updates")
    for sym in ["NDQ", "IVV", "CBA"]:
        new_price = st.number_input(f"{sym} Price", value=fallback_prices[sym], key=f"price_{sym}")
        fallback_prices[sym] = new_price

# Current Prices
st.header("💵 Current Prices")
col1, col2, col3 = st.columns(3)

ndq_price = get_price('NDQ')
ivv_price = get_price('IVV')
cba_price = get_price('CBA')

with col1:
    st.metric("NDQ", f"${ndq_price:.2f}")
with col2:
    st.metric("IVV", f"${ivv_price:.2f}")
with col3:
    st.metric("CBA", f"${cba_price:.2f}")

# Portfolio Calculation
if st.session_state.transactions:
    st.header("📊 Portfolio Summary")
    
    holdings = {}
    for transaction in st.session_state.transactions:
        symbol = transaction['symbol']
        if symbol not in holdings:
            holdings[symbol] = {'units': 0, 'invested': 0}
        holdings[symbol]['units'] += transaction['units']
        holdings[symbol]['invested'] += transaction['total']
    
    total_value = 0
    total_invested = 0
    
    for symbol, data in holdings.items():
        if data['units'] > 0:
            current_price = get_price(symbol)
            current_value = data['units'] * current_price
            total_value += current_value
            total_invested += data['invested']
    
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
    for symbol, data in holdings.items():
        if data['units'] > 0:
            current_price = get_price(symbol)
            current_value = data['units'] * current_price
            profit = current_value - data['invested']
            avg_price = data['invested'] / data['units']
            
            with st.expander(f"{symbol} - {data['units']} units", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Average Price:** ${avg_price:.2f}")
                    st.write(f"**Current Price:** ${current_price:.2f}")
                with col2:
                    st.write(f"**Current Value:** ${current_value:,.2f}")
                    st.write(f"**Profit/Loss:** ${profit:,.2f}")

# Transaction History
if st.session_state.transactions:
    st.header("📋 Transaction History")
    for transaction in reversed(st.session_state.transactions):
        st.write(f"**{transaction['date']}** - {transaction['symbol']} - {transaction['units']} units @ ${transaction['price']:.2f}")
else:
    st.info("💡 No transactions yet. Add your first transaction using the sidebar!")

st.success("🚀 App deployed successfully! Using manual price updates with API fallback.")
