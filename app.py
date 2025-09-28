import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, date
import json

# Updated version with purchase price per share and integer units
def main():
    st.set_page_config(page_title="Investment Tracker", layout="wide")
    st.title("📈 Investment Portfolio Tracker")
    
    # Initialize session state for transactions
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
    
    # Sidebar for transactions
    with st.sidebar:
        st.header("Add Transaction")
        with st.form("transaction_form"):
            trans_type = st.selectbox("Type", ["BUY", "SELL"])
            symbol = st.selectbox("Symbol", ["NDQ", "IVV", "CBA"])
            units = st.number_input("Units", min_value=1, value=10, step=1)  # Changed to integer
            purchase_price = st.number_input("Purchase price per share ($)", min_value=0.01, value=50.0, step=0.01)  # Changed to purchase price per share
            trans_date = st.date_input("Date", value=date.today())
            
            # Calculate total amount automatically
            total_amount = units * purchase_price
            st.write(f"**Total amount: ${total_amount:,.2f}**")
            
            if st.form_submit_button("Add Transaction"):
                transaction = {
                    'id': len(st.session_state.transactions) + 1,
                    'type': trans_type,
                    'symbol': symbol,
                    'units': units,
                    'purchase_price': purchase_price,  # Store purchase price per share
                    'total_amount': total_amount,  # Store calculated total
                    'date': trans_date.isoformat()
                }
                st.session_state.transactions.append(transaction)
                st.success("✅ Transaction added!")
        
        if st.button("Clear All Data"):
            st.session_state.transactions = []
            st.success("🗑️ Data cleared!")
    
    # Portfolio calculations
    holdings = {}
    for transaction in st.session_state.transactions:
        symbol = transaction['symbol']
        if symbol not in holdings:
            holdings[symbol] = {
                'units': 0, 
                'total_invested': 0,
                'average_purchase_price': 0,
                'purchase_history': []
            }
        
        if transaction['type'] == 'BUY':
            # Add to units and total invested
            holdings[symbol]['units'] += transaction['units']
            holdings[symbol]['total_invested'] += transaction['total_amount']
            holdings[symbol]['purchase_history'].append({
                'units': transaction['units'],
                'price': transaction['purchase_price'],
                'total': transaction['total_amount']
            })
            # Recalculate average purchase price
            if holdings[symbol]['units'] > 0:
                holdings[symbol]['average_purchase_price'] = holdings[symbol]['total_invested'] / holdings[symbol]['units']
                
        elif transaction['type'] == 'SELL':
            holdings[symbol]['units'] -= transaction['units']
            # For sells, we need to calculate the cost of the sold units
            # Using FIFO (First In First Out) method
            remaining_units = transaction['units']
            sold_amount = 0
            
            for purchase in holdings[symbol]['purchase_history']:
                if remaining_units <= 0:
                    break
                    
                if purchase['units'] > 0:
                    units_to_sell = min(remaining_units, purchase['units'])
                    sold_amount += units_to_sell * purchase['price']
                    purchase['units'] -= units_to_sell
                    remaining_units -= units_to_sell
            
            holdings[symbol]['total_invested'] -= sold_amount
            
            # Recalculate average purchase price
            if holdings[symbol]['units'] > 0:
                holdings[symbol]['average_purchase_price'] = holdings[symbol]['total_invested'] / holdings[symbol]['units']
            else:
                holdings[symbol]['average_purchase_price'] = 0
    
    # Add current prices and values
    total_value = 0
    total_invested = 0
    for symbol, data in holdings.items():
        if data['units'] > 0:  # Only process holdings with positive units
            current_price = get_current_price(symbol)
            data['current_price'] = current_price
            data['current_value'] = data['units'] * current_price
            data['profit_loss'] = data['current_value'] - data['total_invested']
            data['profit_loss_pct'] = (data['profit_loss'] / data['total_invested'] * 100) if data['total_invested'] > 0 else 0
            total_value += data['current_value']
            total_invested += data['total_invested']
    
    # Display portfolio summary
    st.subheader("📊 Portfolio Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    with col2:
        st.metric("Total Invested", f"${total_invested:,.2f}")
    with col3:
        profit_loss = total_value - total_invested
        st.metric("Total Profit/Loss", f"${profit_loss:,.2f}")
    with col4:
        profit_pct = (profit_loss / total_invested * 100) if total_invested > 0 else 0
        st.metric("Return Percentage", f"{profit_pct:.1f}%")
    
    # Display current prices
    st.subheader("💵 Current Prices")
    prices_col1, prices_col2, prices_col3 = st.columns(3)
    with prices_col1:
        ndq_price = get_current_price('NDQ')
        st.metric("NDQ", f"${ndq_price:.2f}")
    with prices_col2:
        ivv_price = get_current_price('IVV')
        st.metric("IVV", f"${ivv_price:.2f}")
    with prices_col3:
        cba_price = get_current_price('CBA')
        st.metric("CBA", f"${cba_price:.2f}")
    
    # Display holdings in a nice table format
    if holdings:
        st.subheader("📦 Your Holdings")
        
        # Create holdings data for table
        holdings_data = []
        for symbol, data in holdings.items():
            if data['units'] > 0:  # Only show positive holdings
                holdings_data.append({
                    'Symbol': symbol,
                    'Units': f"{data['units']:,}",
                    'Avg Purchase Price': f"${data['average_purchase_price']:.2f}",
                    'Current Price': f"${data['current_price']:.2f}",
                    'Total Value': f"${data['current_value']:,.2f}",
                    'Profit/Loss': f"${data['profit_loss']:,.2f}",
                    'Return %': f"{data['profit_loss_pct']:.1f}%"
                })
        
        if holdings_data:
            # Display as a nice table
            for holding in holdings_data:
                with st.container():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.write(f"**{holding['Symbol']}**")
                        st.write(f"Units: {holding['Units']}")
                    with col2:
                        st.write(f"Avg Price: {holding['Avg Purchase Price']}")
                        st.write(f"Current: {holding['Current Price']}")
                    with col3:
                        st.write(f"Value: {holding['Total Value']}")
                    with col4:
                        color = "green" if float(holding['Profit/Loss'].replace('$','').replace(',','')) >= 0 else "red"
                        st.write(f"P/L: <span style='color: {color}'>{holding['Profit/Loss']}</span>", unsafe_allow_html=True)
                        st.write(f"Return: {holding['Return %']}")
                    st.divider()
    else:
        st.info("💡 No holdings yet. Add your first transaction using the sidebar!")
    
    # Simple growth chart using Streamlit's native charts
    if st.session_state.transactions:
        st.subheader("📈 Portfolio Growth")
        
        # Create a simple timeline
        timeline_data = []
        running_units = {symbol: 0 for symbol in ticker_map.keys()}
        running_invested = 0
        
        # Sort transactions by date
        sorted_transactions = sorted(st.session_state.transactions, key=lambda x: x['date'])
        
        for transaction in sorted_transactions:
            symbol = transaction['symbol']
            if transaction['type'] == 'BUY':
                running_units[symbol] += transaction['units']
                running_invested += transaction['total_amount']
            elif transaction['type'] == 'SELL':
                running_units[symbol] -= transaction['units']
                running_invested -= (transaction['units'] * transaction['purchase_price'])
            
            # Calculate current value at this point
            current_value = sum(running_units[sym] * get_current_price(sym) for sym in running_units)
            
            timeline_data.append({
                'date': transaction['date'][:10],
                'invested': running_invested,
                'value': current_value
            })
        
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            st.line_chart(timeline_df.set_index('date')[['invested', 'value']])
    
    # Transaction history
    if st.session_state.transactions:
        st.subheader("📋 Transaction History")
        trans_data = []
        for trans in st.session_state.transactions:
            trans_data.append({
                'Date': trans['date'][:10],
                'Type': trans['type'],
                'Symbol': trans['symbol'],
                'Units': f"{trans['units']:,}",
                'Price/Share': f"${trans['purchase_price']:.2f}",
                'Total Amount': f"${trans['total_amount']:,.2f}"
            })
        
        trans_df = pd.DataFrame(trans_data)
        st.table(trans_df)
    
    st.success("🚀 Your investment tracker is ready! Data is saved in your browser session.")

if __name__ == "__main__":
    main()