import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# Create sample data
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=['A', 'B', 'C'])

# Matplotlib chart
st.write('### Matplotlib Chart')
fig, ax = plt.subplots()
ax.hist(chart_data['A'], bins=20)
st.pyplot(fig)

# Native Streamlit line chart
st.write('### Streamlit Line Chart')
st.line_chart(chart_data)

# Native Streamlit area chart
st.write('### Streamlit Area Chart')
st.area_chart(chart_data)

# Native Streamlit bar chart
st.write('### Streamlit Bar Chart')
st.bar_chart(chart_data)

# Plotly chart (more interactive)
st.write('### Plotly Chart')
chart_data['C_size'] = chart_data['C'].abs()  # Ensure size is positive
fig = px.scatter(chart_data, x='A', y='B', color='C', size='C_size')
st.plotly_chart(fig)
