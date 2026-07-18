import streamlit as st

st.title("Research AI System")

query = st.text_input("Enter research topic")

if st.button("Search"):
    st.write(f"Searching for: {query}")