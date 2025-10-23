import streamlit as st

# Create columns
col1, col2 = st.columns(2)

with col1:
    st.header("Column 1")
    st.write("This is the first column")
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=200)

with col2:
    st.header("Column 2")
    st.write("This is the second column")
    if st.button("Click me!"):
        st.write("Thanks for clicking!")

# Create expandable sections
with st.expander("Click to expand"):
    st.write("This content is hidden until expanded")
    st.bar_chart({"data": [1, 5, 2, 6, 2, 1]})

# Create tabs
tab1, tab2 = st.tabs(["First Tab", "Second Tab"])

with tab1:
    st.header("Tab 1 Content")
    st.write("You are viewing the first tab")

with tab2:
    st.header("Tab 2 Content")
    st.write("You are viewing the second tab")
