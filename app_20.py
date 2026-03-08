import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

# --- Page Setup ---
st.set_page_config(page_title="HNI Order Radar", layout="wide")

# UI Header
st.markdown("<h1 style='text-align: center; color: #00FFA3;'>🚀 High-Value Order Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Filtering: 0 Debt | 0 Pledge | Orders > 10Cr</p>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("Filter Criteria")
min_order = st.sidebar.slider("Minimum Order (Cr)", 5, 1000, 50)
refresh_rate = st.sidebar.selectbox("Auto Refresh", [1, 5, 10, 30], index=1)

# --- Core Logic Functions ---

def get_financials(symbol):
    """Fetch Debt and Pledge status using yfinance"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        debt = info.get('totalDebt', 0)
        pledge = info.get('pledgedProperty', 0) # Simplified check
        mcap = info.get('marketCap', 0) / 10**7 # Cr mein convert
        return debt, pledge, mcap
    except:
        return 999, 999, 0

def fetch_data():
    """NSE/BSE Mock Data (Last 3 Days)"""
    # Note: In production, use 'BeautifulSoup' to scrape: 
    # https://www.nseindia.com/companies-listing/corporate-filings-announcements
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    
    raw_data = [
        {"S.No": 1, "Symbol": "RAILTEL", "Name": "RailTel Corp", "Date": today, "Order_Cr": 26.73, "Time": "12 Months", "Link": "https://www.nseindia.com"},
        {"Symbol": "ASHOKA", "Name": "Ashoka Buildcon", "Date": yesterday, "Order_Cr": 520.0, "Time": "24 Months", "Link": "https://www.bseindia.com"},
        {"Symbol": "KEC", "Name": "KEC International", "Date": yesterday, "Order_Cr": 1100.0, "Time": "18 Months", "Link": "https://www.nseindia.com"}
    ]
    
    final_list = []
    for item in raw_data:
        debt, pledge, mcap = get_financials(item['Symbol'])
        
        # User Condition: 0 Debt and 0 Pledge
        if debt == 0 and pledge == 0 and item['Order_Cr'] >= min_order:
            item["Market Cap (Cr)"] = round(mcap, 2)
            item["Debt"] = "Zero"
            item["Pledge"] = "0%"
            final_list.append(item)
            
    return pd.DataFrame(final_list)

# --- UI Execution ---

data_df = fetch_data()

if not data_df.empty:
    # Adding Serial Number properly
    data_df.insert(0, 'S.No', range(1, len(data_df) + 1))
    
    st.subheader(f"Latest Announcements (Last 3 Days)")
    st.dataframe(
        data_df[['S.No', 'Name', 'Date', 'Order_Cr', 'Time', 'Market Cap (Cr)', 'Debt', 'Link']],
        column_config={
            "Link": st.column_config.LinkColumn("PDF Link"),
            "Order_Cr": st.column_config.NumberColumn("Order Size (Cr)", format="₹%.2f"),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.warning("⚠️ No companies found matching 0 Debt & 0 Pledge with the current Order Size filter.")

# --- Auto Refresh ---
st.empty()
time.sleep(refresh_rate * 60)
st.rerun()
