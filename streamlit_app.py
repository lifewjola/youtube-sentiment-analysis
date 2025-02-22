import streamlit as st
import pathlib

def main():
    st.set_page_config(
        page_title="YouTube Sentiment Analysis", 
        page_icon="images/ytlogosvg",  
        layout="wide"
    )

    st.image("images/ytfulllogo.png", width=200)

    def load_css(file):
        with open(file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    css_path = pathlib.Path("styles.css")
    load_css(css_path)

    st.markdown(
        "<h1 style='text-align: center; font-size: 2.5rem;'>Understand Your YT Audience Better!</h1>",
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Start Exploring", key="d-button"):
            st.switch_page("pages/dashboard.py")
    with col2:
        if st.button("Log In", key="l-button"):
            st.switch_page("pages/login.py")
    with col3:
        if st.button("Sign Up", key="s-button"):
            st.switch_page("pages/signup.py")

    st.markdown(
        "<h3 style='text-align: center;'><a href='https://buymeacoffee.com/dataprincess' target='_blank'>☕ Buy Me a Coffee to support my work!</a></h3>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()