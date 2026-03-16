import streamlit as st
from superfile_loader import load_superfile

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

df = load_superfile()

if df is None:
    st.error("SuperFile not loaded")
else:
    st.success("SuperFile loaded successfully")
    st.write("Columns found in SuperFile:")
    st.write(list(df.columns))
