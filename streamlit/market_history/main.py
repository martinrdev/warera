from urllib.parse import urljoin
import streamlit as st
import pandas as pd
import requests

DATA_API_URL = st.secrets["data_api_url"]
DATA_API_KEY = st.secrets["data_api_key"]

st.title("Warera Market History")

url = urljoin(DATA_API_URL, "query")

headers = {
    'Authorization': DATA_API_KEY,
}

query = "SELECT * FROM marketHistory"
query_params = []

body = {
    "query": query,
    "params": query_params
}

result = requests.post(url, headers=headers, json=body)

# Example result.results structure:
# [
#     {
#       "product": "steak",
#       "timestamp": 1748668047363,
#       "price": 1.7574818840579707
#     },
#     {
#       "product": "livestock",
#       "timestamp": 1748668047363,
#       "price": 0.7920368421052633
#     }
# ]


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
df.set_index('timestamp', inplace=True)

st.write("This is the market history data fetched from the API.")

st.dataframe(df)

# Pivot the DataFrame so each product is a column, indexed by timestamp
df_pivot = df.pivot(columns='product', values='price')
st.line_chart(df_pivot, use_container_width=True)
