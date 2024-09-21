#explore_questions
import os
import streamlit as st
from scripts.api_utils.azure_sql_utils import update_result_status, fetch_dataframe_from_sql
from scripts.api_utils.chatgpt_utils import get_chatgpt_response, compare_and_update_status
from scripts.api_utils.amazon_s3_utils import download_file_from_s3
from scripts.data_handling.file_processor import preprocess_file
from scripts.data_handling.delete_cache import delete_cache_folder

# Define cache directory and temporary file directory
cache_dir = '.cache'
temp_file_dir = os.path.join(cache_dir, 'temp_file')

# Ensure that cache and temp directories exist
os.makedirs(temp_file_dir, exist_ok=True)

def go_back_to_main():
    st.session_state.page = 'main'

def run_streamlit_app(df=None, s3_client=None, bucket_name=None):
    st.title("GAIA Dataset QA with ChatGPT")

    # Add a "Back" button to return to the main page using a callback
    st.button("Back", on_click=go_back_to_main)
    
    # Explicitly check database connection and load data if not provided
    if df is None:
        st.info("Attempting to connect to the database...")
        df = fetch_dataframe_from_sql()
        if df is not None:
            st.success("Database connection established successfully.")
        else:
            st.error("Failed to connect to the database. Please check your connection settings.")
            return  # Exit the function if the connection fails

    # Initialize session state for pagination and instructions
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'df' not in st.session_state:
        st.session_state.df = df
    if 'instructions' not in st.session_state:
        st.session_state.instructions = ""  # Initialize instructions state
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = False  # Flag to control text area display

    # Add a Refresh button
    if st.button("Refresh"):
        # Reload the dataset from Azure SQL Database and reset session state
        df = fetch_dataframe_from_sql()  # Fetch from database
        if df is not None:
            df.reset_index(drop=True, inplace=True)  # Reset the index
            st.session_state.df = df
            st.session_state.current_page = 0
            st.success("Data refreshed successfully!")
        else:
            st.error("Failed to refresh data from the database.")

    # Reset the DataFrame index to avoid KeyError issues
    st.session_state.df.reset_index(drop=True, inplace=True)

    # Pagination controls at the very top
    col1, col2 = st.columns([1, 1])
    if col1.button("Previous"):
        if st.session_state.current_page > 0:
            st.session_state.current_page -= 1

    if col2.button("Next"):
        if st.session_state.current_page < (len(st.session_state.df) // 7):
            st.session_state.current_page += 1

    # Set pagination parameters
    page_size = 7  # Number of questions to display per page
    total_pages = (len(st.session_state.df) + page_size - 1) // page_size
    current_page = st.session_state.current_page

    # Display the current page of questions
    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    current_df = st.session_state.df.iloc[start_idx:end_idx]

    # Display the questions in a compact table
    st.write(f"Page {current_page + 1} of {total_pages}")
    st.dataframe(current_df[['Question']], height=200)

    # Use a selectbox to choose a question index from the current page
    selected_row_index = st.selectbox(
        "Select Question Index",
        options=range(start_idx, end_idx),  # Use positional range
        format_func=lambda x: f"{x}: {current_df.iloc[x - start_idx]['Question'][:50]}..."  # Adjust format_func
    )

    # Display question details if a row is selected
    selected_row = st.session_state.df.iloc[selected_row_index]  # Use iloc to get the row by position
    st.write("**Question:**", selected_row['Question'])
    st.write("**Expected Final Answer:**", selected_row['FinalAnswer'])

    # Get the file name and file path (S3 URL) if available
    file_name = selected_row.get('file_name', None)
    file_url = selected_row.get('file_path', None)
    downloaded_file_path = None
    preprocessed_data = None

    if file_name:
        st.write(f"**File Name:** {file_name}")
        if file_url:
            st.write(f"**File Path (URL):** {file_url}")
        
        if bucket_name:
            downloaded_file_path = download_file_from_s3(file_name, bucket_name, temp_file_dir, s3_client)
            
            if downloaded_file_path:
                st.write(f"File downloaded successfully to: {downloaded_file_path}")

                # Preprocess the file (pass the downloaded file to the preprocessing function)
                preprocessed_data = preprocess_file(downloaded_file_path)
                print(f"Debug : Preprocessed Data: {preprocessed_data}")
            else:
                st.error(f"Failed to download the file {file_name} from S3.")
        else:
            st.error(f"Invalid bucket name: {bucket_name}. Please check the environment variables.")
    else:
        st.info("No file associated with this question.")

    # Get the current status
    current_status = st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]

    # Update session state for instructions when selecting a new question
    if 'last_selected_row_index' not in st.session_state or st.session_state.last_selected_row_index != selected_row_index:
        # Update the session state instructions with the current row's metadata
        st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')
        st.session_state.last_selected_row_index = selected_row_index
        st.session_state.show_instructions = False  # Reset the flag

    # Show the text area if instructed or if the status is 'Incorrect without Instruction' or 'Incorrect with Instruction'
    if st.session_state.show_instructions or current_status in ['Incorrect without Instruction', 'Incorrect with Instruction']:
        st.write("**The response was incorrect. You can provide instructions and try again.**")
        st.session_state.instructions = st.text_area(
            "Edit Instructions (Optional)",
            value=st.session_state.instructions,  # Load the previous instructions if available
        )

    if st.button("Send to ChatGPT"):
        # Determine if instructions should be used
        use_instructions = current_status.startswith('Incorrect') and st.session_state.instructions

        # Call ChatGPT API, passing the preprocessed file data instead of a URL
        chatgpt_response = get_chatgpt_response(
            selected_row['Question'], 
            instructions=st.session_state.instructions if use_instructions else None, 
            preprocessed_data=preprocessed_data  # Send the preprocessed file data
        )
        
        if chatgpt_response:
            # Display ChatGPT's response with appropriate labeling
            if use_instructions:
                st.write("**ChatGPT's Response with Instructions:**", chatgpt_response)
            else:
                st.write("**ChatGPT's Response:**", chatgpt_response)

            # Compare response with the final answer
            status = compare_and_update_status(selected_row, chatgpt_response, st.session_state.instructions if use_instructions else None)
            st.session_state.df.at[selected_row_index, 'result_status'] = status  # Update the DataFrame immediately
            st.write(f"**Updated Result Status:** {status}")

            # Update the status in the Azure SQL Database
            update_result_status(selected_row['task_id'], status)

            # Set flag to show instructions if the response is incorrect
            if status in ['Incorrect without Instruction', 'Incorrect with Instruction']:
                st.session_state.show_instructions = True

    # Display current status
    st.write(f"**Result Status:** {st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]}")

    # Cleanup: Delete cache folder after processing if a file was downloaded
    # if downloaded_file_path:
    #     delete_cache_folder(temp_file_dir)  # Cleanup the temp directory after the process is done