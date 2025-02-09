import streamlit as st

def log_out():
    st.session_state.pop("email", None)
    st.stop()