import os
import streamlit as st
from dotenv import load_dotenv
from scripts.s3_upload import init_s3_client
from scripts.azure_sql_utils import fetch_dataframe_from_sql
from scripts.chatgpt_utils import init_openai

# Load environment variables
load_dotenv()

def main():
    # Initialize session state to control navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'  # Set the initial page to 'landing'

    # Display the current page based on session state
    if st.session_state.page == 'landing':
        run_landing_page()
    elif st.session_state.page == 'main':
        run_main_page()
    elif st.session_state.page == 'explore_questions':
        run_explore_questions()
    elif st.session_state.page == 'view_summary':
        run_view_summary()

# Callback functions to change pages
def set_page_to_main():
    st.session_state.page = 'main'

def set_page_to_explore_questions():
    st.session_state.page = 'explore_questions'

def set_page_to_view_summary():
    st.session_state.page = 'view_summary'

def run_landing_page():
    st.title("OPEN AI EVALUATION APP")
    st.write("Welcome to the Open AI Evaluation App!")

    # "Try It" button to navigate to the Main Page
    st.button("Try It", on_click=set_page_to_main)  # Using callback to change the page

def run_main_page():
    st.title("Main Page")
    st.write("Choose an option:")

    # "Explore Questions" button to navigate to the Explore Questions Page
    st.button("Explore Questions", on_click=set_page_to_explore_questions)  # Using callback to change the page

    # "View Summary" button to navigate to the Summary Page
    st.button("View Summary", on_click=set_page_to_view_summary)  # Using callback to change the page

def run_explore_questions():
    # Initialize APIs and data for the Explore Questions page
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
        st.error(f"Missing environment variables: {', '.join(missing_vars)}. Please ensure these are set.")
        return  # Exit the function if any environment variable is missing

    # Initialize OpenAI and S3 client
    init_openai(openai_api_key)
    s3_client = init_s3_client(aws_access_key, aws_secret_key)

    df = fetch_dataframe_from_sql()  # Fetch the dataset from Azure SQL
    if df is not None:
        # Corrected import for the explore_questions module
        from streamlit_pages.explore_questions import run_streamlit_app
        run_streamlit_app(df, s3_client, bucket_name)
    else:
        st.error("Failed to load dataset from Azure SQL.")

def run_view_summary():
    # Load the dataset for the Summary Page
    df = fetch_dataframe_from_sql()
    if df is not None:
        # Corrected import for the view_summary module
        from streamlit_pages.view_summary import run_summary_page
        run_summary_page(df)
    else:
        st.error("Failed to load dataset from Azure SQL.")

if __name__ == "__main__":
    main()
