from urllib.parse import urljoin
import streamlit as st
import pandas as pd
import requests

DATA_API_URL = st.secrets["data_api_url"]
DATA_API_KEY = st.secrets["data_api_key"]

st.title("Warera Market")

query_url = urljoin(DATA_API_URL, "query")

headers = {
    'Authorization': DATA_API_KEY,
}

@st.fragment()
def render_market_history():
    st.header("Market Prices")

    body = {
        "query": "SELECT * FROM marketHistory",
        "params": [],
    }
    result = requests.post(query_url, headers=headers, json=body)

    if not result.ok:
        st.error(f"Error fetching data: {result.status_code} - {result.text}")
        print("Error:", result.text)
        st.stop()

    data = result.json()
    df = pd.DataFrame(data['results'])

    if df.empty:
        st.warning("No data available to display.")
        st.stop()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp')
    
    latest_timestamp = df['timestamp'].max()
    st.write(f"Latest data timestamp: {latest_timestamp}")

    latest_df = df[df['timestamp'] == latest_timestamp]
    latest_df = latest_df.drop(columns=['timestamp'])
    column_config = {
        "product": st.column_config.TextColumn("Product"),
        "price": st.column_config.NumberColumn("Market price", format="%.3f BTC"),
    }
    st.dataframe(latest_df, hide_index=True, use_container_width=True, column_config=column_config)

    # Pivot the DataFrame so each product is a column, indexed by timestamp
    df_pivot = df.pivot(index='timestamp', columns='product', values='price')
    st.line_chart(df_pivot, use_container_width=True)


@st.fragment()
def render_profit_history():
    st.header("Work Unit Profit")

    body = {
            "query": "SELECT * FROM profitHistory",
            "params": [],
        }
    result = requests.post(query_url, headers=headers, json=body)

    if not result.ok:
        st.error(f"Error fetching data: {result.status_code} - {result.text}")
        print("Error:", result.text)
        st.stop()

    data = result.json()
    df = pd.DataFrame(data['results'])

    if df.empty:
        st.warning("No profit history data available to display.")
        st.stop()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp')
    
    latest_timestamp = df['timestamp'].max()
    st.write(f"Latest data timestamp: {latest_timestamp}")

    latest_df = df[df['timestamp'] == latest_timestamp]
    latest_df = latest_df.drop(columns=['timestamp'])
    latest_df.sort_values(by='workUnitProfit', inplace=True, ascending=False)
    column_config = {
        "product": st.column_config.TextColumn("Product"),
        "workUnitProfit": st.column_config.NumberColumn("Work Unit Profit", format="%.3f BTC"),
    }
    st.dataframe(latest_df, hide_index=True, use_container_width=True, column_config=column_config)
    
    # Pivot the DataFrame so each product is a column, indexed by timestamp
    df_pivot = df.pivot(index='timestamp', columns='product', values='workUnitProfit')
    st.line_chart(df_pivot, use_container_width=True)


render_market_history()
st.divider()
render_profit_history()
