import streamlit as st
import pandas as pd
import numpy as np

# Create sample data
df = pd.DataFrame({
    'Name': ['John', 'Mary', 'Bob', 'Jane'],
    'Age': [25, 30, 22, 28],
    'City': ['New York', 'Boston', 'Chicago', 'Seattle']
})

# Display the dataframe
st.write('### Sample Data:')
st.dataframe(df)

# Display static table
st.table(df)

# Display statistics
st.write('### Data Statistics:')
st.write(df.describe())