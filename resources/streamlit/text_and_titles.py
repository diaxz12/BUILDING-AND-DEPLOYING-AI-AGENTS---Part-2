import streamlit as st

# Add a title
st.title('My First Streamlit App')

# Add header
st.header('This is a header')

# Add subheader
st.subheader('This is a subheader')

# Add normal text
st.text('This is regular text')

# Add markdown
st.markdown('### This is markdown with *emphasis*')

# Display a Python object's information
st.write('Display data or variables:', {'data': 'values'})