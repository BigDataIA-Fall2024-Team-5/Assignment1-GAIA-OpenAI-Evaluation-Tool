import streamlit as st
from scripts.api_utils.azure_sql_utils import fetch_user_from_sql
import bcrypt

# Callback function to go back to the register page
def go_to_register():
    st.session_state['login_success'] = False
    st.session_state['username'] = ''
    st.session_state['password'] = ''
    st.session_state.page = 'register'

# Callback function to handle login
def on_login_click():
    username = st.session_state['username']
    password = st.session_state['password']
    
    user = fetch_user_from_sql(username)
    if user:
        stored_password = user['password'].encode('utf-8')  # Stored hashed password from DB
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            st.session_state['user_id'] = user['user_id']
            st.session_state['username'] = user['username']
            st.session_state['role'] = user['role']
            st.success(f"Welcome, {username}!")

            # Redirect based on role
            if user['role'] == 'admin':
                st.session_state.page = 'admin'  # Redirect to admin page
            else:
                st.session_state.page = 'main'  # Redirect to main page for regular users

        else:
            st.error("Incorrect password")
    else:
        st.error("Username not found")

def login_page():
    st.title("Login to Your Account")

    # Ensure session state variables are initialized
    if 'login_success' not in st.session_state:
        st.session_state['login_success'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'password' not in st.session_state:
        st.session_state['password'] = ''

    # Show the login form if login hasn't been successful yet
    if not st.session_state['login_success']:
        st.text_input("Username", key='username', value=st.session_state['username'])
        st.text_input("Password", key='password', type="password", value=st.session_state['password'])

        # Login button with explicit on_click callback
        st.button("Login", on_click=on_login_click)

    # Create New Account button
    st.button("Create New Account", on_click=go_to_register, key="register_button")
