from __future__ import annotations

import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

st.set_page_config(page_title="FinBank Risk Lakehouse", layout="wide")


def get_engine():
    user = os.getenv("POSTGRES_USER", "finbank")
    password = os.getenv("POSTGRES_PASSWORD", "finbank")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "finbank")
    return create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}")


@st.cache_data(ttl=300)
def read_sql(query: str) -> pd.DataFrame:
    return pd.read_sql(query, get_engine())


st.title("FinBank Risk Lakehouse")
st.caption("Banking data engineering portfolio project")

exposure = read_sql("select * from analytics_marts.mart_customer_exposure")
transactions = read_sql("select * from analytics_marts.mart_daily_transactions")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Customers", f"{exposure['customer_id'].nunique():,}")
col2.metric("Total Exposure", f"{exposure['total_outstanding_balance'].sum():,.2f}")
col3.metric("High/Default Risk", f"{exposure[exposure['portfolio_status'].isin(['HIGH_RISK', 'DEFAULT_RISK'])]['customer_id'].nunique():,}")
col4.metric("Suspicious Tx", f"{transactions['suspicious_count'].sum():,.0f}")

st.subheader("Exposure by segment")
seg = exposure.groupby("segment", as_index=False)["total_outstanding_balance"].sum()
st.plotly_chart(px.bar(seg, x="segment", y="total_outstanding_balance"), use_container_width=True)

st.subheader("Portfolio status distribution")
status = exposure.groupby("portfolio_status", as_index=False)["customer_id"].count()
st.plotly_chart(px.pie(status, names="portfolio_status", values="customer_id"), use_container_width=True)

st.subheader("Daily transaction volume")
daily = transactions.groupby("transaction_date", as_index=False)["total_amount"].sum()
st.plotly_chart(px.line(daily, x="transaction_date", y="total_amount"), use_container_width=True)
