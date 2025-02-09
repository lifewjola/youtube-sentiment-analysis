import streamlit as st
from backend.authenticate import authenticate_user

st.set_page_config(page_title="Login", page_icon="images/YouTube-Icon-Full-Color-Logo.wine.svg", layout="centered")


if "email" in st.session_state:
    st.switch_page("pages/dashboard.py")  
else:
    st.title("Log In")

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
                st.error(f"⚠️ {e}") 
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}") 

    st.write("Don't have an account? [Sign up](signup)")
