import streamlit as st
from scripts.api_utils.azure_sql_utils import insert_user_to_sql, fetch_user_from_sql

# Callback function to go back to login page
def go_to_login():
    # Reset registration success and input values when going back
    st.session_state['registration_success'] = False
    st.session_state['username'] = ''
    st.session_state['password'] = ''
    st.session_state['confirm_password'] = ''
    st.session_state.page = 'login'

# Function to handle the registration logic
def handle_register():
    username = st.session_state['username']
    password = st.session_state['password']
    confirm_password = st.session_state['confirm_password']
    
    # Check if any of the fields are empty
    if not username or not password or not confirm_password:
        st.error("All fields are required.")
    else:
        # Check if the username already exists in the database
        existing_user = fetch_user_from_sql(username)
        if existing_user:
            st.error("Username already exists. Please choose a different username.")
        elif password == confirm_password:
            # Insert the user into the database
            insert_user_to_sql(username, password, 'user')  # Default role is 'user'
            st.success("Account created successfully! Please log in with your new credentials.")
            st.session_state['registration_success'] = True
        else:
            st.error("Passwords do not match. Please try again.")

def register_page():
    st.title("Register a New Account")

    # Ensure that session state variables are initialized
    if 'registration_success' not in st.session_state:
        st.session_state['registration_success'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'password' not in st.session_state:
        st.session_state['password'] = ''
    if 'confirm_password' not in st.session_state:
        st.session_state['confirm_password'] = ''

    # Show the registration form if the registration hasn't been successful yet
    if not st.session_state['registration_success']:
        # Display input fields without the form
        st.session_state['username'] = st.text_input("Username", value=st.session_state['username'])
        st.session_state['password'] = st.text_input("Password", type="password", value=st.session_state['password'])
        st.session_state['confirm_password'] = st.text_input("Confirm Password", type="password", value=st.session_state['confirm_password'])

        # Use a regular button with on_click to handle registration
        st.button("Register", on_click=handle_register)

    # Always display the Back to Login button, and reset registration success when clicked
    st.button("Back to Login", on_click=go_to_login, key="manual_login_button")
