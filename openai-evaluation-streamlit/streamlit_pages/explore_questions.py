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

# Callback function for handling 'Send to ChatGPT'
def handle_send_to_chatgpt(selected_row, selected_row_index, preprocessed_data):
    current_status = st.session_state.df.loc[selected_row_index, 'result_status']
    use_instructions = False
    if current_status.startswith("Incorrect"):
        use_instructions = bool(st.session_state.instructions)
    
    chatgpt_response = get_chatgpt_response(
        selected_row['Question'],
        instructions=st.session_state.instructions if use_instructions else None,
        preprocessed_data=preprocessed_data
    )
    
    if chatgpt_response:
        if use_instructions:
            st.session_state.chatgpt_responses_with_instructions[selected_row_index] = chatgpt_response
        else:
            st.session_state.chatgpt_responses[selected_row_index] = chatgpt_response
        
        status = compare_and_update_status(selected_row, chatgpt_response, st.session_state.instructions if use_instructions else None)
        st.session_state.df.at[selected_row_index, 'result_status'] = status
        update_result_status(selected_row['task_id'], status)
        
        if status.startswith("Incorrect"):
            st.session_state.show_instructions = True
        
        if use_instructions:
            st.session_state.stored_instructions[selected_row_index] = st.session_state.instructions

def run_streamlit_app(df=None, s3_client=None, bucket_name=None):
    st.title("GAIA Dataset QA with ChatGPT")
    st.button("Back", on_click=go_back_to_main)

    if df is None:
        st.info("Attempting to connect to the database...")
        df = fetch_dataframe_from_sql()
        if df is not None:
            st.success("Database connection established successfully.")
        else:
            st.error("Failed to connect to the database. Please check your connection settings.")
            return

    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'df' not in st.session_state:
        st.session_state.df = df
    if 'instructions' not in st.session_state:
        st.session_state.instructions = ""
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = False
    if 'chatgpt_responses' not in st.session_state:
        st.session_state.chatgpt_responses = {}
    if 'chatgpt_responses_with_instructions' not in st.session_state:
        st.session_state.chatgpt_responses_with_instructions = {}
    if 'stored_instructions' not in st.session_state:
        st.session_state.stored_instructions = {}

    if st.button("Refresh"):
        df = fetch_dataframe_from_sql()
        if df is not None:
            df.reset_index(drop=True, inplace=True)
            st.session_state.df = df
            st.session_state.current_page = 0
            st.success("Data refreshed successfully!")
        else:
            st.error("Failed to refresh data from the database.")

    st.session_state.df.reset_index(drop=True, inplace=True)

    col1, col2 = st.columns([1, 1])
    if col1.button("Previous"):
        if st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    if col2.button("Next"):
        if st.session_state.current_page < (len(st.session_state.df) // 7):
            st.session_state.current_page += 1

    page_size = 7
    total_pages = (len(st.session_state.df) + page_size - 1) // page_size
    current_page = st.session_state.current_page

    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    current_df = st.session_state.df.iloc[start_idx:end_idx]

    st.write(f"Page {current_page + 1} of {total_pages}")
    st.dataframe(current_df[['Question']], height=200)

    selected_row_index = st.selectbox(
        "Select Question Index",
        options=range(start_idx, end_idx),
        format_func=lambda x: f"{x}: {current_df.iloc[x - start_idx]['Question'][:50]}..."
    )

    selected_row = st.session_state.df.iloc[selected_row_index]
    st.write("**Question:**", selected_row['Question'])
    st.write("**Expected Final Answer:**", selected_row['FinalAnswer'])

    file_name = selected_row.get('file_name', None)
    file_url = selected_row.get('file_path', None)
    downloaded_file_path = None
    preprocessed_data = None

    if file_name:
        st.write(f"**File Name:** {file_name}")
        if file_url:
            st.write(f"**File Path (URL):** {file_url}")

        file_extension = os.path.splitext(file_name)[1].lower()
        unsupported_types = ['.jpg', '.png', '.zip', '.mp3']

        if file_extension in unsupported_types:
            st.error(f"File type '{file_extension}' is currently not supported")
        else:
            if bucket_name:
                downloaded_file_path = download_file_from_s3(file_name, bucket_name, temp_file_dir, s3_client)

                if downloaded_file_path:
                    st.write(f"File downloaded successfully to: {downloaded_file_path}")
                    preprocessed_data = preprocess_file(downloaded_file_path)
                    if isinstance(preprocessed_data, str) and "not supported" in preprocessed_data:
                        st.error(preprocessed_data)
                    else:
                        pass
                else:
                    st.error(f"Failed to download the file {file_name} from S3.")
            else:
                st.error(f"Invalid bucket name: {bucket_name}. Please check the environment variables.")
    else:
        st.info("No file associated with this question.")

    current_status = st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]

    if 'last_selected_row_index' not in st.session_state or st.session_state.last_selected_row_index != selected_row_index:
        if current_status.startswith('Correct'):
            st.session_state.instructions = ""
        else:
            st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')
        
        if selected_row_index in st.session_state.stored_instructions:
            st.session_state.instructions = st.session_state.stored_instructions[selected_row_index]
        
        st.session_state.last_selected_row_index = selected_row_index
        st.session_state.show_instructions = False

    if not st.session_state.show_instructions and not current_status.startswith("Incorrect"):
        st.button("Send to ChatGPT", on_click=handle_send_to_chatgpt, args=(selected_row, selected_row_index, preprocessed_data))

    if selected_row_index in st.session_state.chatgpt_responses:
        st.write(f"**ChatGPT's Response:** {st.session_state.chatgpt_responses[selected_row_index]}")

    if selected_row_index in st.session_state.chatgpt_responses_with_instructions:
        st.write(f"**ChatGPT's Response with Instructions:** {st.session_state.chatgpt_responses_with_instructions[selected_row_index]}")

    if st.session_state.show_instructions or current_status.startswith("Incorrect"):
        st.write("**The response was incorrect. Please provide instructions.**")
        if not st.session_state.show_instructions:
            st.button("Send to ChatGPT", disabled=True)

        st.session_state.instructions = st.text_area(
            "Edit Instructions (Optional)",
            value=st.session_state.instructions,
            key=f"instructions_{selected_row_index}"
        )

        if st.button("Send Instructions to ChatGPT", key=f'send_button_{selected_row_index}'):
            st.session_state.stored_instructions[selected_row_index] = st.session_state.instructions
            chatgpt_response = get_chatgpt_response(
                selected_row['Question'],
                instructions=st.session_state.instructions,
                preprocessed_data=preprocessed_data
            )

            if chatgpt_response:
                st.write(f"**ChatGPT's Response with Instructions:** {chatgpt_response}")
                st.session_state.chatgpt_responses_with_instructions[selected_row_index] = chatgpt_response
                status = compare_and_update_status(selected_row, chatgpt_response, st.session_state.instructions)
                st.session_state.df.at[selected_row_index, 'result_status'] = status
                current_status = status
                update_result_status(selected_row['task_id'], status)

    st.write(f"**Final Result Status:** {st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]}")

    # Uncomment the following lines if you want to clean up the temp directory after processing
    # if downloaded_file_path:
    #     delete_cache_folder(temp_file_dir)