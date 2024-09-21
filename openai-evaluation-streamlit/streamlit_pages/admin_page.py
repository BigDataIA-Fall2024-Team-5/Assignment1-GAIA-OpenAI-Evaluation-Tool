import streamlit as st
from streamlit_pages.admin_dataset_management import admin_dataset_management_page
from streamlit_pages.admin_user_management import admin_user_management_page

# Admin Dashboard Page
def admin_page():
    # Ensure session state variables are initialized
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'login_success' not in st.session_state:
        st.session_state['login_success'] = False

    st.title("Admin Dashboard")
    st.write(f"Welcome {st.session_state['username']} to the Admin Dashboard!")

    # Admin action buttons
    st.button("Manage Dataset", on_click=lambda: st.session_state.update(page='admin_dataset_management'))
    st.button("Manage Users", on_click=lambda: st.session_state.update(page='admin_user_management'))
    st.button("Logout", on_click=lambda: st.session_state.update(page='login'))
