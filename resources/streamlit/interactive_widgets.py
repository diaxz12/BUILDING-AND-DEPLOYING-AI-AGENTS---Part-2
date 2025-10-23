import streamlit as st

# Text input
user_input = st.text_input("Enter some text")
st.write('You entered:', user_input)

# Number input
number = st.number_input("Enter a number", min_value=0, max_value=100, value=50)
st.write('Selected number:', number)

# Slider
slider_value = st.slider("Select a range", 0, 100, 25)
st.write('Slider value:', slider_value)

# Checkbox
if st.checkbox("Show additional options"):
    st.write("You selected to show additional options!")

# Selectbox
option = st.selectbox("Choose an option", ["Option 1", "Option 2", "Option 3"])
st.write('You selected:', option)

# Radio buttons
radio_option = st.radio("Select one", ["Choice A", "Choice B", "Choice C"])
st.write('You selected:', radio_option)

# Multiselect
multi_options = st.multiselect("Select multiple", ["Item 1", "Item 2", "Item 3", "Item 4"])
st.write('You selected:', multi_options)

# Button
if st.button("Click me"):
    st.write("Button clicked!")
