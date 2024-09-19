# chatgpt_utils.py
import openai
import streamlit as st

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key

# Function to send a question and file URL to ChatGPT
def get_chatgpt_response(question, instructions=None, file_url=None):
    # Construct the message for the Chat API
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a helpful assistant. Respond only with the final answer to questions. "
                "For example: \n"
                "Q: What is 2 + 2? A: 4\n"
                "Q: Name the capital of France. A: Paris\n"
                "Provide only the final answer without explanations."
            )
        }
    ]
    
    # Add question and instructions to the messages
    user_message = question
    if instructions:
        user_message += f"\nInstructions: {instructions}"
    if file_url:
        user_message += f"\n[Please refer to the attached file: {file_url}]"
    
    user_message += "\nPlease provide only the final answer. Do not include any explanation."
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' or 'gpt-4' if available
            messages=messages,
            temperature=0.2,  # Lower temperature to encourage more direct answers
        )
        # Extract and return the answer as a single line
        answer = response['choices'][0]['message']['content'].strip().split('\n')[0]  # Get the first line of the response
        return answer
    except Exception as e:
        st.error(f"Error calling ChatGPT API: {e}")
        return None

# Compare ChatGPT's response with the expected answer
def compare_and_update_status(row, chatgpt_response, instructions):
    final_answer = str(row['FinalAnswer']).strip().lower()
    chatgpt_response = chatgpt_response.strip().lower()

    if chatgpt_response == final_answer:
        if instructions:
            return 'Correct with Instruction'
        else:
            return 'Correct without Instruction'
    else:
        if instructions:
            return 'Incorrect with Instruction'
        else:
            return 'Incorrect without Instruction'
