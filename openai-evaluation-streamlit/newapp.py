#newapp.py
import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from scripts.api_utils.amazon_s3_utils import init_s3_client
from scripts.api_utils.azure_sql_utils import fetch_dataframe_from_sql, fetch_user_results
from scripts.api_utils.chatgpt_utils import init_openai
from streamlit_pages.login_page import login_page
from streamlit_pages.register_page import register_page
from streamlit_pages.admin_page import admin_page
from streamlit_pages.admin_dataset_management import admin_dataset_management_page
from streamlit_pages.admin_user_management import admin_user_management_page

# Load environment variables
load_dotenv()

def main():
    # Set default values for session state using setdefault()
    st.session_state.setdefault('page', 'landing')
    st.session_state.setdefault('login_success', False)
    st.session_state.setdefault('username', '')
    st.session_state.setdefault('user_id', None)  # Ensure 'user_id' is initialized properly
    st.session_state.setdefault('role', '')

    # Ensure user is logged in before accessing certain pages
    if st.session_state.page in ['main', 'explore_questions', 'admin', 'view_summary'] and not st.session_state['login_success']:
        st.error("Please login to access this page.")
        st.session_state.page = 'login'  # Redirect to login page
        return

    # Display the page based on session state
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

def go_back_to_main():
    # Optionally reset any page-specific states here if needed
    st.session_state.show_instructions = False
    st.session_state.current_page = 0
    st.session_state.last_selected_row_index = None

    # Navigate back to the main page
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
    # Clear the session state except for 'page' to properly manage logout behavior
    for key in list(st.session_state.keys()):
        if key != 'page':  # Do not clear 'page' to avoid resetting navigation
            del st.session_state[key]
    st.session_state.page = 'login'  # Redirect back to login

# Landing Page
def run_landing_page():
    st.title("OPEN AI EVALUATION APP")
    st.write("Would you like to assess AI's Answering Prowess?")
    st.button("Try It", on_click=go_to_login)

# Main Page
def run_main_page():
    # Ensure session keys like 'username' and 'login_success' exist
    if st.session_state.get('login_success', False):
        st.title("Main Page")
        
        # Display username if available, else display default welcome message
        if st.session_state.get('username'):  # Check if username is present in session state
            st.write(f"Welcome {st.session_state['username']}!")  # Display username
        else:
            st.write("Welcome!")  # Fallback message in case username is missing

        # Admin section (if the user is an admin)
        if st.session_state.get('role') == 'admin':
            st.button("Admin Page", on_click=go_to_admin)

        st.button("Explore Questions", on_click=go_to_explore_questions)
        st.button("View Summary", on_click=go_to_view_summary)
        st.button("Log Out", on_click=logout)
    else:
        st.error("Please login to access this page.")
        st.session_state.page = 'login'

# Explore Questions Page
def run_explore_questions():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')

    # Error handling for missing environment variables
    if not openai_api_key:
        st.error("Missing OPENAI_API_KEY.")
        return
    if not aws_access_key:
        st.error("Missing AWS_ACCESS_KEY.")
        return
    if not aws_secret_key:
        st.error("Missing AWS_SECRET_KEY.")
        return
    if not bucket_name:
        st.error("Missing S3_BUCKET_NAME.")
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
    # Ensure 'user_id' is available in session state
    if not st.session_state.get('user_id'):
        st.error("User ID not found. Please log in again.")
        st.session_state.page = 'login'  # Redirect to login page
        return

    # Fetch the main dataset (GaiaDataset)
    df = fetch_dataframe_from_sql()
    
    # Fetch user-specific results (returns None if no results are found)
    user_results_df = fetch_user_results(st.session_state['user_id'])

    # Ensure the main dataset was fetched successfully
    if df is None:
        st.error("Failed to load the main dataset from Azure SQL.")
        return
    
    # If user_results_df is None (no results found for the user), create an empty DataFrame
    if user_results_df is None or user_results_df.empty:
        st.write("No user results found. Please complete some questions.")
        user_results_df = pd.DataFrame(columns=['task_id', 'user_result_status', 'chatgpt_response'])  # Empty DataFrame

    # Drop 'user_result_status' from df (main dataset) to avoid duplication during the merge
    if 'user_result_status' in df.columns:
        df = df.drop(columns=['user_result_status'])

    # Merge the two dataframes on 'task_id'
    merged_df = df.merge(user_results_df[['task_id', 'user_result_status']], on='task_id', how='left')

    # Fill missing 'user_result_status' with 'N/A'
    merged_df['user_result_status'] = merged_df['user_result_status'].fillna('N/A')

    from streamlit_pages.view_summary import run_summary_page

    # Call the summary page with the merged dataframe
    run_summary_page(merged_df, user_results_df)


if __name__ == "__main__":
    main()
