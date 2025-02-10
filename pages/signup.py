from backend.create_user import create_user
import streamlit as st
import re
from backend.database import email_exist

st.set_page_config(page_title="Signup", page_icon="images/YouTube-Icon-Full-Color-Logo.wine.svg", layout="centered")


st.title("Sign Up")
with st.form("signup"):
    st.write("Sign up to access your YouTube Dashboard.")
    youtube_username = st.text_input("YouTube Username", placeholder="@username")
    nickname = st.text_input("Nick Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    password_confirm = st.text_input("Confirm Password", type="password")
    st.image("images/bmc.png", width=150)
    st.markdown("[☕ Buy Me a Coffee to support my work!](https://buymeacoffee.com/dataprincess)", unsafe_allow_html=True)

    submitted = st.form_submit_button("Create my account!")



    if submitted:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Invalid email address.")
        elif email_exist(email):
            st.error("Email already exists. Please [Log in](login)")
        elif password != password_confirm:
            st.error("Passwords do not match.")
        else:
            try:
                success = create_user(nickname, email, password, youtube_username)
                st.success("Sign up successful.")
                with st.spinner("Redirecting to login page..."):
                    st.switch_page("pages/login.py")
            except ValueError as e:
                st.error(f"⚠️ {e}") 
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}") 

    st.write("Already have an account? [Log in](login)")
