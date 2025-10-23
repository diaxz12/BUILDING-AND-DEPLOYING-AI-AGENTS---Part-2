import streamlit as st
import pandas as pd
import time

# Caching data loading
@st.cache_data
def load_large_dataset():
    time.sleep(5)  # Simulate long loading time
    return pd.DataFrame({
        'A': range(1000),
        'B': range(1000, 2000)
    })

data = load_large_dataset()
st.write('Loaded data:', data.head())