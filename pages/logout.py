import streamlit as st

def log_out():
    st.session_state.pop("email", None)
    with st.spinner("Redirecting to login page..."):
        st.switch_page("pages/login.py")

log_out()