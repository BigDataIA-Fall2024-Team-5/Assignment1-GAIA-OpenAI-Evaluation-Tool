# streamlit_pages/login_page.py
import streamlit as st
from scripts.api_utils.azure_sql_utils import fetch_user_from_sql
import bcrypt

def login_page():
    st.title("Login to Your Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = fetch_user_from_sql(username)
        
        if user:
            stored_password = user['password'].encode('utf-8')  # Stored hashed password from DB
            if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                st.session_state['user_id'] = user['user_id']
                st.session_state['username'] = user['username']
                st.session_state['role'] = user['role']
                st.success(f"Welcome, {username}!")
                st.session_state.page = 'main'  # Redirect to main page after login
            else:
                st.error("Incorrect password")
        else:
            st.error("Username not found")

    if st.button("Create New Account"):
        st.session_state.page = 'register'  # Redirect to the registration page
