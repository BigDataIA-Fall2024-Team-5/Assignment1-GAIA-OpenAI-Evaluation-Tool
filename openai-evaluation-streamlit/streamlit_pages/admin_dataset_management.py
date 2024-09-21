import streamlit as st
from scripts.main import process_dataset  # Import the function directly

# Callback to trigger dataset processing logic
def run_dataset_processing():
    try:
        result = process_dataset()

        # Store the result in session state for display
        st.session_state['dataset_processing_status'] = "Dataset Processing Complete"
        st.session_state['dataset_processing_output'] = result

    except Exception as e:
        st.session_state['dataset_processing_status'] = f"An unexpected error occurred: {e}"

def admin_dataset_management_page():
    # Ensure session state variables are initialized
    if 'dataset_processing_status' not in st.session_state:
        st.session_state['dataset_processing_status'] = ''
    if 'dataset_processing_output' not in st.session_state:
        st.session_state['dataset_processing_output'] = ''

    st.title("Dataset Management")

    st.write("""
    This page allows you to manage the GAIA dataset. You can trigger the entire dataset processing pipeline,
    which includes cloning the repository, loading the dataset, uploading files to S3, and inserting records
    into Azure SQL.
    """)

    # Provide a button to trigger the main process
    st.button("Process Dataset", on_click=run_dataset_processing)

    # Check and display dataset processing status and output
    if st.session_state['dataset_processing_status']:
        st.write(st.session_state['dataset_processing_status'])
        st.text(st.session_state['dataset_processing_output'])

    # Back button to return to the Admin page
    st.button("Back to Admin", on_click=lambda: st.session_state.update(page='admin'))
