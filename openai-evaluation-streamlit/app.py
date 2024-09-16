import os
import pandas as pd
import openai
import streamlit as st
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key

# Initialize AWS S3 client
def init_s3_client(access_key, secret_key):
    return boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)

# Function to send a question and file URL to ChatGPT
def get_chatgpt_response(question, file_url=None):
    # Construct the message for the new Chat API
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    # Add question to the messages
    user_message = question
    if file_url:
        user_message += f"\n[Please refer to the attached file: {file_url}]"
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' or 'gpt-4' if available
            messages=messages
        )
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except Exception as e:
        st.error(f"Error calling ChatGPT API: {e}")
        return None

# Compare ChatGPT's response with the expected answer
def compare_and_update_status(row, chatgpt_response):
    final_answer = str(row['Final answer']).strip().lower()
    chatgpt_response = chatgpt_response.strip().lower()

    if chatgpt_response == final_answer:
        return 'Correct'
    else:
        return 'Incorrect'

# Load the dataset
def load_dataset(csv_path):
    try:
        df = pd.read_csv(csv_path)
        # Ensure the 'result_status' column is of type object (string)
        if 'result_status' not in df.columns:
            df['result_status'] = 'N/A'  # Initialize with 'N/A' if the column does not exist
        else:
            df['result_status'] = df['result_status'].astype('object')  # Set to 'object' dtype
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

# Streamlit app to interactively work with the dataset
def run_streamlit_app(df, s3_client, bucket_name):
    st.title("GAIA Dataset QA with ChatGPT")

    # Initialize session state for pagination
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    # Pagination controls at the very top
    col1, col2 = st.columns([1, 1])
    if col1.button("Previous"):
        if st.session_state.current_page > 0:
            st.session_state.current_page -= 1

    if col2.button("Next"):
        if st.session_state.current_page < (len(df) // 7):
            st.session_state.current_page += 1

    # Set pagination parameters
    page_size = 7  # Number of questions to display per page
    total_pages = (len(df) + page_size - 1) // page_size
    current_page = st.session_state.current_page

    # Display the current page of questions
    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    current_df = df.iloc[start_idx:end_idx]

    # Display the questions in a compact table
    st.write(f"Page {current_page + 1} of {total_pages}")
    st.dataframe(current_df[['Question']], height=200)

    # Use a selectbox to choose a question index from the current page
    selected_row_index = st.selectbox(
        "Select Question Index",
        options=current_df.index,
        format_func=lambda x: f"{x}: {current_df.loc[x, 'Question'][:50]}..."
    )

    # Display question details if a row is selected
    selected_row = df.loc[selected_row_index]
    st.write("**Question:**", selected_row['Question'])
    st.write("**Final Answer:**", selected_row['Final answer'])
    
    # Get the file URL (S3 path) if file_path is available
    file_url = selected_row['file_path'] if selected_row['file_path'] else None
    if file_url:
        st.write(f"**File Path (URL):** {file_url}")
    
    # Button to send the question to ChatGPT without instructions
    if st.button("Send to ChatGPT"):
        # Call ChatGPT API
        chatgpt_response = get_chatgpt_response(selected_row['Question'], file_url)
        if chatgpt_response:
            # Display ChatGPT's response
            st.write("**ChatGPT's Response:**", chatgpt_response)

            # Compare response with the final answer
            status = compare_and_update_status(selected_row, chatgpt_response)
            if status == 'Correct':
                df.at[selected_row_index, 'result_status'] = 'Correct'  # Update the DataFrame immediately
            else:
                # If incorrect, show an option to edit instructions and resend
                st.write("**Initial response was incorrect. You can edit the instructions and try again.**")
                editable_steps = st.text_area("Edit Steps (Optional)", selected_row.get('Annotator_Metadata_Steps', ''))
                
                if st.button("Send to ChatGPT with Instructions"):
                    # Send the question with edited instructions to ChatGPT
                    updated_prompt = selected_row['Question'] + "\nInstructions: " + editable_steps
                    chatgpt_response_with_instructions = get_chatgpt_response(updated_prompt, file_url)

                    if chatgpt_response_with_instructions:
                        st.write("**ChatGPT's Response with Instructions:**", chatgpt_response_with_instructions)
                        status_with_instructions = compare_and_update_status(selected_row, chatgpt_response_with_instructions)
                        df.at[selected_row_index, 'result_status'] = 'Correct with Instructions' if status_with_instructions == 'Correct' else 'Incorrect'

    # Display current status
    st.write(f"**Result Status:** {df.loc[df.index == selected_row_index, 'result_status'].values[0]}")

    # Save changes to CSV
    if st.button("Save Changes"):
        df.to_csv('updated_gaia_dataset.csv', index=False)
        st.success("Changes saved to updated_gaia_dataset.csv")

if __name__ == "__main__":
    # Set your OpenAI and AWS credentials from environment variables
    openai_api_key = os.getenv('OPENAI_API_KEY')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    csv_path = os.getenv('CSV_PATH')

    # Initialize APIs
    init_openai(openai_api_key)
    s3_client = init_s3_client(aws_access_key, aws_secret_key)

    # Load the dataset
    df = load_dataset(csv_path)
    
    if df is not None:
        run_streamlit_app(df, s3_client, bucket_name)
