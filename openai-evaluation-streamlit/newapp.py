import os
import streamlit as st
from dotenv import load_dotenv
from scripts.api_utils.amazon_s3_utils import init_s3_client
from scripts.api_utils.azure_sql_utils import fetch_dataframe_from_sql
from scripts.api_utils.chatgpt_utils import init_openai
from streamlit_pages.login_page import login_page
from streamlit_pages.register_page import register_page
from streamlit_pages.admin_page import admin_page
from streamlit_pages.admin_dataset_management import admin_dataset_management_page
from streamlit_pages.admin_user_management import admin_user_management_page

# Load environment variables
load_dotenv()

def main():
    # Initialize session state to control navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'  # Set the initial page to 'landing'

    # Display the current page based on session state
    if st.session_state.page == 'landing':
        run_landing_page()
    elif st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'main':
        run_main_page()
    elif st.session_state.page == 'admin':
        admin_page()
    elif st.session_state.page == 'admin_dataset_management':
        admin_dataset_management_page()
    elif st.session_state.page == 'admin_user_management':
        admin_user_management_page()
    elif st.session_state.page == 'explore_questions':
        run_explore_questions()
    elif st.session_state.page == 'view_summary':
        run_view_summary()

# Callback functions for navigation
def go_to_login():
    st.session_state.page = 'login'

def go_to_main():
    st.session_state.page = 'main'

def go_to_admin():
    st.session_state.page = 'admin'

def go_to_explore_questions():
    st.session_state.page = 'explore_questions'

def go_to_view_summary():
    st.session_state.page = 'view_summary'

def go_to_register():
    st.session_state.page = 'register'

def go_to_admin_dataset_management():
    st.session_state.page = 'admin_dataset_management'

def go_to_admin_user_management():
    st.session_state.page = 'admin_user_management'

def logout():
    # Reset session state variables related to login
    st.session_state['username'] = ''
    st.session_state['password'] = ''
    st.session_state['role'] = ''
    st.session_state['login_success'] = False
    st.session_state.page = 'login'  # Navigate back to login page

# Landing Page
def run_landing_page():
    st.title("OPEN AI EVALUATION APP")
    st.write("Welcome to the Open AI Evaluation App!")
    st.button("Try It", on_click=go_to_login)

# Main Page
def run_main_page():
    st.title("Main Page")
    st.write(f"Welcome {st.session_state['username']}!")

    # Admin section (if the user is an admin)
    if st.session_state.get('role') == 'admin':
        st.button("Admin Page", on_click=go_to_admin)
    
    st.button("Explore Questions", on_click=go_to_explore_questions)
    st.button("View Summary", on_click=go_to_view_summary)
    st.button("Log Out", on_click=logout)

# Explore Questions Page
def run_explore_questions():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')

    # Error handling for missing environment variables
    missing_vars = []
    if not openai_api_key:
        missing_vars.append("OPENAI_API_KEY")
    if not aws_access_key:
        missing_vars.append("AWS_ACCESS_KEY")
    if not aws_secret_key:
        missing_vars.append("AWS_SECRET_KEY")
    if not bucket_name:
        missing_vars.append("S3_BUCKET_NAME")

    if missing_vars:
        st.error(f"Missing environment variables: {', '.join(missing_vars)}.")
        return

    init_openai(openai_api_key)
    s3_client = init_s3_client(aws_access_key, aws_secret_key)

    df = fetch_dataframe_from_sql()
    if df is not None:
        from streamlit_pages.explore_questions import run_streamlit_app
        run_streamlit_app(df, s3_client, bucket_name)
    else:
        st.error("Failed to load dataset from Azure SQL.")

# View Summary Page
def run_view_summary():
    df = fetch_dataframe_from_sql()
    if df is not None:
        from streamlit_pages.view_summary import run_summary_page
        run_summary_page(df)
    else:
        st.error("Failed to load dataset from Azure SQL.")

if __name__ == "__main__":
    main()
