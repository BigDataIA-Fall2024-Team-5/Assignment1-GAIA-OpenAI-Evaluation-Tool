#explore_questions.py
import os
import streamlit as st
import pandas as pd
from scripts.api_utils.azure_sql_utils import update_user_result, fetch_dataframe_from_sql, fetch_user_results
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
    # Do not clear the session state related to user info
    st.session_state.show_instructions = False
    st.session_state.current_page = 0
    st.session_state.last_selected_row_index = None
    st.session_state.chatgpt_response = None  # Reset ChatGPT response

    # Navigate back to the main page without clearing username/session data
    st.session_state.page = 'main'

# Callback function for handling 'Send to ChatGPT'
def handle_send_to_chatgpt(selected_row, selected_row_index, preprocessed_data):
    user_id = st.session_state.get('user_id', 'default_user')  # Get user ID from session

    # Get the current status from the user_results table
    current_status = st.session_state.user_results.loc[selected_row_index, 'user_result_status']

    # Get the response status from the user_results table
    chatgpt_response = st.session_state.user_results.loc[selected_row_index, 'chatgpt_response']

    # Determine if instructions should be used based on the current status
    use_instructions = current_status.startswith("Incorrect")
    
    # Call ChatGPT API, passing the preprocessed file data instead of a URL
    chatgpt_response = get_chatgpt_response(
        selected_row['Question'], 
        instructions=st.session_state.instructions if use_instructions else None, 
        preprocessed_data=preprocessed_data  # Send the preprocessed file data
    )

    if chatgpt_response:
        # Compare response with the final answer
        status = compare_and_update_status(selected_row, chatgpt_response, st.session_state.instructions if use_instructions else None)
        
        # Update the status in session state immediately
        st.session_state.user_results.at[selected_row_index, 'user_result_status'] = status
    
        # Update the status in the Azure SQL Database (backend)
        update_user_result(user_id=user_id, task_id=selected_row['task_id'], status=status, chatgpt_response=chatgpt_response)

        # Store ChatGPT response in session state
        st.session_state.chatgpt_response = chatgpt_response

        # Ensure the UI reflects the updated status immediately
        st.session_state.final_status_updated = True

        # Show instructions if the response is incorrect
        if status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
            st.session_state.show_instructions = True
        else:
            st.session_state.show_instructions = False  # Hide instructions if Correct

def run_streamlit_app(df=None, s3_client=None, bucket_name=None):
    


    # Add a "Back" button to return to the main page using a callback
    st.button("Back", on_click=go_back_to_main, key="back_button")

    #st.title("GAIA Dataset QA with ChatGPT")
    st.markdown("<h1 style='text-align: center;'>GAIA Dataset QA with ChatGPT</h1>", unsafe_allow_html=True)

    user_id = st.session_state.get('user_id', 'default_user')  # Fetch user_id from session state

    # Explicitly check database connection and load data if not provided
    if df is None:
        st.info("Attempting to connect to the database...")
        df = fetch_dataframe_from_sql()
        if df is not None:
            st.success("GaiaDataset loaded successfully.")
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
    if 'chatgpt_response' not in st.session_state:
        st.session_state.chatgpt_response = None  # Store the ChatGPT response
    if 'final_status_updated' not in st.session_state:
        st.session_state.final_status_updated = False  # Track if the final status was updated

    # Fetch user-specific results
    user_results = fetch_user_results(user_id)

    # If user_results is empty, create a default DataFrame with 'user_result_status' set to 'N/A'
    if user_results is None or user_results.empty:
        user_results = pd.DataFrame({
            'task_id': st.session_state.df['task_id'],
            'user_result_status': ['N/A'] * len(st.session_state.df),
            'chatgpt_response' : ['N/A'] * len(st.session_state.df)
        })

    # Merge user_results with GaiaDataset
    user_results = user_results.rename(columns={'result_status': 'user_result_status'})
    user_results = user_results.rename(columns={'gpt_response': 'chatgpt_response'})
  
    if 'task_id' in user_results.columns and 'user_result_status' in user_results.columns and 'chatgpt_response' in user_results.columns:
        merged_df = st.session_state.df.merge(
            user_results[['task_id', 'user_result_status', 'chatgpt_response']],
            on='task_id',
            how='left'
        )
    else:
        st.error("Necessary columns for merging ('task_id', 'user_result_status', or 'chatgpt_response') are missing.")
        return
    
    # Check if 'chatgpt_response' exists in user_results; if not, create it
    if 'chatgpt_response' not in user_results.columns:
        user_results['chatgpt_response'] = None  # Initialize with None or a default value

    # After merging user_results with GaiaDataset, fill missing 'user_result_status' with 'N/A'
    merged_df['user_result_status'] = merged_df['user_result_status'].fillna('N/A')
    merged_df['chatgpt_response'] = merged_df['chatgpt_response'].fillna('N/A')

    st.session_state.user_results = merged_df  # Store merged DataFrame in session state
    
    # Add a Refresh button
    if st.button("Refresh", key="refresh_button"):
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
    st.session_state.user_results.reset_index(drop=True, inplace=True)
    
    # Pagination controls at the very top
    col1, col2 = st.columns([9, 1])  # Adjust the width ratio to push "Next" to the right
    if col1.button("Previous", key="previous_button"):
        if st.session_state.current_page > 0:
            st.session_state.current_page -= 1

    if col2.button("Next", key="next_button"):  # Next button is now on the right
        if st.session_state.current_page < (len(st.session_state.df) // 7):
            st.session_state.current_page += 1


    # Set pagination parameters
    page_size = 7  # Number of questions to display per page
    total_pages = (len(st.session_state.df) + page_size - 1) // page_size
    current_page = st.session_state.current_page

    # Display the current page of questions
    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    current_df = st.session_state.user_results.iloc[start_idx:end_idx]

    # Check if 'Question' column is missing
    if 'Question' not in current_df.columns:
        st.error("'Question' column is missing from the dataset!")
        return
  
    # Display the questions in a compact table
    # st.write(f"Page {current_page + 1} of {total_pages}")
    # st.dataframe(current_df[['Question']], height=200)

    # Function to apply dark and bold border to the dataframe
    def style_dataframe_with_borders(df):
        return df.style.set_table_styles(
            [{
                'selector': 'table',
                'props': [('border', '3px solid black'), ('width', '100%')]  # Set a bold, dark border and full width
            }, {
                'selector': 'th',
                'props': [('border', '2px solid black'), ('font-weight', 'bold')]  # Bold border and font for headers
            }, {
                'selector': 'td',
                'props': [('border', '2px solid black'), ('width', '100%')]  # Ensure the cell takes full width
            }]
        )

    # Assuming `current_df` is the dataframe you're displaying
    # Filter the dataframe to show only the 'Question' column
    question_df = current_df[['Question']]

    # Give a name to the index column
    question_df.index.name = 'ID'

    # Apply styling to the 'Question' dataframe
    styled_df = style_dataframe_with_borders(question_df)

    # Display the styled dataframe in Streamlit, using container width to expand the table
    st.dataframe(styled_df, use_container_width=True)

    # Use a selectbox to choose a question index from the current page
    selected_row_index = st.selectbox(
        "Select Question Index",
        options=current_df.index.tolist(),  # Use the index from current_df
        format_func=lambda x: f"{x}: {current_df.loc[x, 'Question'][:50]}...",  # Adjust format_func
        key=f"selectbox_{current_page}"
    )



    # Display question details if a row is selected
    selected_row = current_df.loc[selected_row_index]
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
                    st.error(f"Failed to download the file {file_name} from S3.")
            else:
                st.error(f"Invalid bucket name: {bucket_name}. Please check the environment variables.")
    else:
        st.info("No file associated with this question.")

    # Get the current status from user-specific results
    current_status = selected_row['user_result_status']
    chatgpt_response = selected_row['chatgpt_response']

    # Update session state for instructions when selecting a new question
    if 'last_selected_row_index' not in st.session_state or st.session_state.last_selected_row_index != selected_row_index:
        # Conditions to show the Edit Instructions box:
        # Show instructions if the result is 'Correct with Instructions', 'Incorrect with Instructions', or 'Incorrect without Instructions'
        if current_status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
            st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')  # Pre-fill from dataset if available
            st.session_state.show_instructions = True  # Show the instructions box
        else:
            #st.session_state.instructions = ""  # Clear instructions
            st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')
            st.session_state.show_instructions = False  # Hide instructions by default

        st.session_state.last_selected_row_index = selected_row_index
        st.session_state.chatgpt_response = None  # Reset ChatGPT response

    # Display ChatGPT response if available
    if st.session_state.chatgpt_response:
        st.write(f"**ChatGPT's Response:** {st.session_state.chatgpt_response}")

    # Only display the button if the status is not "Correct with Instruction"
    if not st.session_state.show_instructions and current_status != "Correct with Instruction":
        # Show 'Send to ChatGPT' if the status is not 'Correct with Instruction'
        if st.button("Send to ChatGPT", on_click=handle_send_to_chatgpt, args=(selected_row, selected_row_index, preprocessed_data), key=f"send_chatgpt_{selected_row_index}"):
            # ChatGPT response will be processed in handle_send_to_chatgpt
            pass

    # If the response was incorrect, prompt for instructions
    if st.session_state.show_instructions:
        st.write("**The response was incorrect. Please provide instructions.**")

        # Pre-fill instructions from the dataset or previous inputs
        st.session_state.instructions = st.text_area(
            "Edit Instructions (Optional)",
            value=st.session_state.instructions,
            key=f"instructions_{selected_row_index}"  # Unique key for each question
        )

        # Button to send instructions to ChatGPT
        if st.button("Send Instructions to ChatGPT", key=f'send_button_{selected_row_index}'):
            # Use the updated instructions to query ChatGPT
            chatgpt_response = get_chatgpt_response(
                selected_row['Question'], 
                instructions=st.session_state.instructions, 
                preprocessed_data=preprocessed_data
            )

            if chatgpt_response:
                st.write(f"**ChatGPT's Response with Instructions:** {chatgpt_response}")

                # Compare and update status based on ChatGPT's response
                status = compare_and_update_status(selected_row, chatgpt_response, st.session_state.instructions)
                st.session_state.user_results.at[selected_row_index, 'user_result_status'] = status
                current_status = status  # Update current_status

                # Update the user-specific status in the Azure SQL Database
                update_user_result(user_id=user_id, task_id=selected_row['task_id'], status=status, chatgpt_response=chatgpt_response)

                 # Update show_instructions flag based on new status
                if status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
                    st.session_state.show_instructions = True
                else:
                    st.session_state.show_instructions = False

                # Store the new ChatGPT response
                st.session_state.chatgpt_response = chatgpt_response

    # Function to apply background color based on the Final Result Status
    def style_status_based_on_final_result(status):
        # Strip any leading/trailing spaces and make the check case-insensitive
        if status.strip().lower().startswith("correct"):
            # Green background for Correct statuses
            return 'background-color: #38761d; padding: 10px; border-radius: 5px;'
        else:
            # Red background for non-Correct statuses
            return 'background-color: #d62929; padding: 10px; border-radius: 5px;'

    # Get the background color based on the Final Result Status
    background_style = style_status_based_on_final_result(current_status)

   # Apply the same background color style to both "Final Result Status" and "Latest ChatGPT Response"
    st.markdown(f'<div style="{background_style}"><strong>Final Result Status:</strong> {current_status}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="{background_style}"><strong>Latest ChatGPT Response:</strong> {chatgpt_response}</div>', unsafe_allow_html=True)

    # Cleanup: Delete cache folder after processing if a file was downloaded
    # if downloaded_file_path:
    #     delete_cache_folder(temp_file_dir)  # Cleanup the temp directory after the process is done