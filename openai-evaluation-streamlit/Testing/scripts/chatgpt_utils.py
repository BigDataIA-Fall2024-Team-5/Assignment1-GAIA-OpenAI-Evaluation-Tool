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
                "You are a helpful assistant. Provide clear and concise responses to questions. "
                "Your answers should be direct and no longer than 5 lines. Include only minimal context if necessary. "
                "For example:\n"
                "Q: What is 2 + 2? A: The answer is 4.\n"
                "Q: Name the capital of France. A: The capital of France is Paris.\n"
                "Keep each response under 5 lines, focusing on the main point."
            )
        }
    ]
    
    # Add question and instructions to the messages
    user_message = question
    if instructions:
        user_message += f"\nInstructions: {instructions}"
    if file_url:
        user_message += f"\n[Please refer to the attached file: {file_url}]"
    
    user_message += "\nPlease provide a response no longer than 5 lines."
    messages.append({"role": "user", "content": user_message})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' or 'gpt-4'
            messages=messages,
            temperature=0.2,  # Lower temperature to encourage more direct answers
        )
        # Extract and process the answer
        answer = response['choices'][0]['message']['content'].strip()
        
        # Ensure the answer does not exceed 5 lines
        lines = answer.split('\n')
        if len(lines) > 5:
            answer = '\n'.join(lines[:5])  # Limit to the first 5 lines
        
        return answer
    except Exception as e:
        st.error(f"Error calling ChatGPT API: {e}")
        return None

# Compare ChatGPT's response with the expected answer using OpenAI API
def compare_and_update_status(row, chatgpt_response, instructions):
    original_answer = str(row['FinalAnswer']).strip()
    ai_engine_answer = chatgpt_response.strip()
    question = row['Question'].strip()

    # Construct the comparison message for OpenAI
    comparison_prompt = (
        f"ORIGINAL ANSWER IS: {original_answer}\n\n"
        f"QUESTION: {question}\n\n"
        "AI ENGINE ANSWER:\n"
        f"{ai_engine_answer}\n\n"
        "Compare the original answer with the AI Engine Answer for the above question "
        "and strictly give me a one-word reply: 'YES' if it matches, or 'NO' if it does not. "
        "No other words other than the ones inside quotes (' ') without the quotes."
    )

    try:
        # Send the comparison prompt to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' or 'gpt-4'
            messages=[{"role": "user", "content": comparison_prompt}],
            temperature=0,  # Zero temperature for deterministic results
        )
        
        # Extract the response
        comparison_result = response['choices'][0]['message']['content'].strip().lower()

        # Normalize the result to handle variations of 'yes' and 'no'
        if comparison_result in ['yes', "'yes'", '"yes"', 'yes.', 'yes!', 'yes ', 'yes']:
            if instructions:
                return 'Correct with Instruction'
            else:
                return 'Correct without Instruction'
        elif comparison_result in ['no', "'no'", '"no"', 'no.', 'no!', 'no ', 'no']:
            if instructions:
                return 'Incorrect with Instruction'
            else:
                return 'Incorrect without Instruction'
        else:
            # If the response is unexpected, mark it as 'Error'
            st.error(f"Unexpected response from OpenAI: {comparison_result}")
            return 'Error'

    except Exception as e:
        st.error(f"Error calling OpenAI API for comparison: {e}")
        return 'Error'

