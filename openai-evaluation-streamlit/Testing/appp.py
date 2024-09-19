import os
import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
from dotenv import load_dotenv
from scripts.s3_upload import init_s3_client
from scripts.azure_sql_utils import get_azure_sql_connection, update_result_status, fetch_dataframe_from_sql
from scripts.chatgpt_utils import init_openai, get_chatgpt_response, compare_and_update_status  # Import ChatGPT utilities

# Load environment variables
load_dotenv()

# Streamlit app to interactively work with the dataset
def run_streamlit_app(df, s3_client, bucket_name):
    st.title("GAIA Dataset QA with ChatGPT")

    # Add a Refresh button
    if st.button("Refresh"):
        # Reload the dataset from Azure SQL Database and reset session state
        df = fetch_dataframe_from_sql()  # Fetch from database
        if df is not None:
            df.reset_index(drop=True, inplace=True)  # Reset the index
            st.session_state.df = df
            st.session_state.current_page = 0
            st.success("Data refreshed successfully!")

    # Initialize session state for pagination
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'df' not in st.session_state:
        st.session_state.df = df

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
    st.write("**Final Answer:**", selected_row['FinalAnswer'])

    # Get the file URL (S3 path) if file_path is available
    file_url = selected_row['file_path'] if selected_row['file_path'] else None
    if file_url:
        st.write(f"**File Path (URL):** {file_url}")

    # Get the current status
    current_status = st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]

    # Text area for instructions
    instructions = None
    if current_status in ['Incorrect without Instruction', 'Incorrect with Instruction']:
        # Show instruction text box if status is "Incorrect without Instruction" or "Incorrect with Instruction"
        st.write("**The response was incorrect. You can provide instructions and try again.**")
        instructions = st.text_area("Edit Instructions (Optional)", selected_row.get('Annotator_Metadata_Steps', ''))

    if st.button("Send to ChatGPT"):
        # Determine if instructions should be used
        use_instructions = current_status.startswith('Incorrect') and instructions is not None
        
        # Call ChatGPT API
        chatgpt_response = get_chatgpt_response(
            selected_row['Question'], 
            instructions=instructions if use_instructions else None, 
            file_url=file_url
        )
        
        if chatgpt_response:
            # Display ChatGPT's response with appropriate labeling
            if use_instructions:
                st.write("**ChatGPT's Response with Instructions:**", chatgpt_response)
            else:
                st.write("**ChatGPT's Response:**", chatgpt_response)

            # Compare response with the final answer
            status = compare_and_update_status(selected_row, chatgpt_response, instructions if use_instructions else None)
            st.session_state.df.at[selected_row_index, 'result_status'] = status  # Update the DataFrame immediately
            st.write(f"**Updated Result Status:** {status}")

            # Update the status in the Azure SQL Database
            update_result_status(selected_row['task_id'], status)
    
    # Display current status
    st.write(f"**Result Status:** {st.session_state.df.loc[st.session_state.df.index == selected_row_index, 'result_status'].values[0]}")

def run_summary_page(df):
    st.title("Summary of Results")

    # Create a bar chart for the 'result_status' column
    status_counts = df['result_status'].value_counts()
    st.write("### Result Status Distribution")
    fig, ax = plt.subplots()
    status_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel('Result Status')
    ax.set_ylabel('Count')
    st.pyplot(fig)

    # Display the raw counts
    st.write("### Detailed Result Status Counts")
    st.write(status_counts)

if __name__ == "__main__":
    # Get the environment variables directly
    openai_api_key = os.getenv('OPENAI_API_KEY')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('BUCKET_NAME')

    # Initialize APIs
    init_openai(openai_api_key)
    s3_client = init_s3_client(aws_access_key, aws_secret_key)

    # Load the dataset from Azure SQL Database
    df = fetch_dataframe_from_sql()  # Fetch the dataset from Azure SQL
    if df is not None:
        # Sidebar navigation
        page = st.sidebar.selectbox("Choose a page:", ["QA Page", "Summary Page"])

        if page == "QA Page":
            run_streamlit_app(df, s3_client, bucket_name)
        elif page == "Summary Page":
            run_summary_page(df)
