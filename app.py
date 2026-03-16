import streamlit as st
import pandas as pd

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

try:
    df_raw = pd.read_excel("SuperFile.xlsx", header=None)
    st.success("SuperFile loaded successfully")
    st.write("First 10 rows of the file:")
    st.dataframe(df_raw.head(10))
except Exception as e:
    st.error(f"Error loading SuperFile: {e}")
