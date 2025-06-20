from typing import cast
from urllib.parse import urljoin
import streamlit as st
import pandas as pd
import requests
import pytz
from utils import PRODUCT_LABELS

# setup app configuration
DATA_API_URL = st.secrets["data_api_url"]
DATA_API_KEY = st.secrets["data_api_key"]

query_url = urljoin(DATA_API_URL, "query")

headers = {
    'Authorization': DATA_API_KEY,
}

query_filter_mapping = {
    "24 horas": "timestamp >= strftime('%s', 'now', '-24 hours') * 1000",
    "3 días": "timestamp >= strftime('%s', 'now', '-3 days') * 1000 AND strftime('%M', timestamp / 1000, 'unixepoch') = '00'",
    "7 días": "timestamp >= strftime('%s', 'now', '-7 days') * 1000 AND strftime('%M', timestamp / 1000, 'unixepoch') = '00'",
}

# setup page configuration
st.set_page_config(
    page_title="Warera - Análisis de mercado",
    page_icon=":bar_chart:",
)

@st.fragment()
def render_market_history(query_filter: str):
    body = {
        "query": "SELECT * FROM marketHistory WHERE " + query_filter,
        "params": [],
    }
    result = requests.post(query_url, headers=headers, json=body)

    if not result.ok:
        st.error(f"Error al traer los datos: {result.status_code} - {result.text}")
        print("Error:", result.text)
        st.stop()

    data = result.json()
    df = pd.DataFrame(data['results'])

    if df.empty:
        st.warning("No hay datos para mostrar.")
        st.stop()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp')
    
    latest_timestamp = cast(pd.Timestamp, df['timestamp'].max())
    st.write(f"Ultima actualización: {latest_timestamp.astimezone(pytz.timezone('America/Montevideo')).strftime('%Y-%m-%d %H:%M')} (UY)")

    df['product'] = df['product'].map(PRODUCT_LABELS).fillna(df['product'])

    # Pivot the DataFrame so each product is a column, indexed by timestamp
    df_pivot = df.pivot(index='timestamp', columns='product', values='price')

    latest_df = df[df['timestamp'] == latest_timestamp]
    latest_df = latest_df.drop(columns=['timestamp'])
    latest_df['product_order'] = latest_df['product'].map(lambda x: list(PRODUCT_LABELS.values()).index(x) if x in PRODUCT_LABELS.values() else float('inf'))
    latest_df.sort_values(by='product_order', inplace=True)
    latest_df.drop(columns=['product_order'], inplace=True)
    latest_df['history'] = latest_df['product'].apply(
        lambda prod: df_pivot[prod].to_list()
    )
    column_config = {
        "product": st.column_config.TextColumn("Producto"),
        "price": st.column_config.NumberColumn("Precio en el mercado", format="%.3f BTC"),
        "history": st.column_config.LineChartColumn("Historial de precio"),
    }
    st.dataframe(latest_df, hide_index=True, use_container_width=True, column_config=column_config)

    st.line_chart(df_pivot, use_container_width=True, x_label="Tiempo", y_label="Precio (BTC)")


@st.fragment()
def render_profit_history(query_filter: str):
    body = {
            "query": "SELECT * FROM profitHistory WHERE " + query_filter,
            "params": [],
        }
    result = requests.post(query_url, headers=headers, json=body)

    if not result.ok:
        st.error(f"Error al traer los datos: {result.status_code} - {result.text}")
        print("Error:", result.text)
        st.stop()

    data = result.json()
    df = pd.DataFrame(data['results'])

    if df.empty:
        st.warning("No hay datos para mostrar.")
        st.stop()

    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp')
    
    latest_timestamp = cast(pd.Timestamp, df['timestamp'].max())
    st.write(f"Ultima actualización: {latest_timestamp.astimezone(pytz.timezone('America/Montevideo')).strftime('%Y-%m-%d %H:%M')} (UY)")

    df['product'] = df['product'].map(PRODUCT_LABELS).fillna(df['product'])

    # Pivot the DataFrame so each product is a column, indexed by timestamp
    df_pivot = df.pivot(index='timestamp', columns='product', values='workUnitProfit')

    latest_df = df[df['timestamp'] == latest_timestamp]
    latest_df = latest_df.drop(columns=['timestamp'])
    latest_df.sort_values(by='workUnitProfit', inplace=True, ascending=False)
    latest_df.insert(0, 'rank', range(1, len(latest_df) + 1))
    latest_df['history'] = latest_df['product'].apply(
        lambda prod: df_pivot[prod].to_list()
    )
    column_config = {
        "rank": st.column_config.NumberColumn("Posición"),
        "product": st.column_config.TextColumn("Producto"),
        "workUnitProfit": st.column_config.NumberColumn("Rendimiento del trabajo", format="%.3f BTC"),
        "history": st.column_config.LineChartColumn("Historial de rendimiento"),
    }
    st.dataframe(latest_df, hide_index=True, use_container_width=True, column_config=column_config)
    
    st.line_chart(df_pivot, use_container_width=True, x_label="Tiempo", y_label="Rendimiento del trabajo (BTC)")


# render page
st.title("Warera - Análisis de mercado")

time_selection = st.selectbox(
        "Selecciona el intervalo de tiempo",
        options=["24 horas", "3 días", "7 días"],
    )
query_filter = query_filter_mapping[time_selection]

st.header("Precios de mercado")
with st.spinner("Cargando precios..."):
    render_market_history(query_filter)

st.divider()

st.header("Rendimiento de unidades de trabajo")
with st.spinner("Cargando rendimiento..."):
    render_profit_history(query_filter)
