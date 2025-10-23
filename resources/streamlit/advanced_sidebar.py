import streamlit as st

# Add sidebar elements
st.sidebar.title("Control Panel")
selected_option = st.sidebar.selectbox(
    "Choose analysis type",
    ["Overview", "Detailed Analysis", "Predictions"]
)

# Main content based on sidebar selection
if selected_option == "Overview":
    st.title("Overview Dashboard")
    st.write("This is the overview section")
elif selected_option == "Detailed Analysis":
    st.title("Detailed Analysis")
    st.write("Here you can explore more details")
elif selected_option == "Predictions":
    st.title("Predictions")
    st.write("This section contains predictive models")