import streamlit as st
from backend.authenticate import authenticate_user
from database import email_exist
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="Login", page_icon="images/YouTube-Icon-Full-Color-Logo.wine.svg", layout="centered")

cookies_secret = st.secrets["cookies_secret"]
cookies = EncryptedCookieManager(password=cookies_secret, prefix="yt_dashboard_")  

if not cookies.ready():
    st.stop() 

if cookies.get("user_session"):
    st.session_state["email"] = cookies.get("user_session")
    st.switch_page("pages/dashboard.py")  

st.title("Log In")
st.image("images/bmc.png", width=150)
st.markdown("[☕ Buy Me a Coffee to support my work!](https://buymeacoffee.com/dataprincess)", unsafe_allow_html=True)

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Take me to my dashboard!", key="login"):
    if not email or not password:  
        st.error("Please enter both email and password.")
    else:
        try:
            valid = authenticate_user(email, password)
            
            if valid:
                st.session_state["email"] = email

                cookies["user_session"] = email  
                cookies.save()

                with st.spinner("Redirecting to dashboard..."):
                    st.switch_page("pages/dashboard.py")
            else:
                st.error("❌ Invalid email or password.")

        except ValueError as e:
            if not email_exist(email):
                st.error("⚠️ Email not found. [Sign up](signup) to create an account.")
            else:
                st.error(f"⚠️ {e}") 
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}") 

st.write("Don't have an account? [Sign up](signup)")
