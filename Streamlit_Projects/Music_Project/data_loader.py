# Data loader code will go here
import pandas as pd
import streamlit as st

@st.cache_data
def load_data(all):
    return pd.read_csv(all+".csv")