#register_page.py
import streamlit as st
from scripts.api_utils.azure_sql_utils import fetch_user_from_sql, insert_user_to_sql

def register_page():
    st.title("Create a New Account")

    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        else:
            # Check if username already exists
            user = fetch_user_from_sql(username)
            if user:
                st.error("Username already exists!")
            else:
                insert_user_to_sql(username, password, role="user")  # Default role is user
                st.success(f"Account created successfully for {username}!")
                st.session_state.page = 'login'  # Redirect to login page
