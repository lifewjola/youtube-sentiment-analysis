import streamlit as st
from backend.authenticate import authenticate_user
from database import email_exist

st.set_page_config(page_title="Login", page_icon="images/ytlogo.svg", layout="centered")

 

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
