from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="RetailPulse", layout="wide")
st.title("RetailPulse Intelligence")
lake = Path(st.sidebar.text_input("Gold data path", "data/lake/gold/daily_sales"))
files = list(lake.glob("**/*.parquet")) if lake.exists() else []
if not files:
    st.info("No Gold data found. Run the generator and batch ETL first.")
else:
    frame = pd.read_parquet(lake)
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"${frame['revenue'].sum():,.2f}")
    c2.metric("Orders", f"{frame['order_count'].sum():,.0f}")
    c3.metric("Average order value", f"${frame['average_order_value'].mean():,.2f}")
    st.line_chart(frame.set_index("order_date")["revenue"])
    st.dataframe(frame, use_container_width=True)
