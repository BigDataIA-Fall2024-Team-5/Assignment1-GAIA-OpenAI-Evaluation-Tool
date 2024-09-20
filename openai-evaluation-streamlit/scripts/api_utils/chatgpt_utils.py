#chatgpt_utils
import openai
import streamlit as st

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key

# Function to send a question and preprocessed file data to ChatGPT
def get_chatgpt_response(question, instructions=None, preprocessed_data=None):
    # Construct the message for the Chat API
    messages = [
        {
            "role": "system", 
            "content": (
                "You are a helpful assistant. Provide clear and concise responses to questions. "
                "Your answers should be direct and focus on the specific piece of information requested in the question. "
                "Avoid additional context unless necessary for clarity. "
                "For example:\n"
                "Q: What is 2 + 2? A: 4.\n"
                "Q: Name the capital of France. A: Paris.\n"
                "Q: What is the chemical symbol for water? A: H2O.\n"
                "Respond with only the essential information needed to answer the question."
            )
        }
    ]
    
    # Add question and instructions to the messages
    user_message = question
    if instructions:
        user_message += f"\nInstructions: {instructions}\nPlease provide only the key information in the answer."
    
    # Add preprocessed data if available
    if preprocessed_data:
        user_message += f"\nHere is the reference file details:\n{preprocessed_data}"

    user_message += "\nProvide the answer as concisely as possible."
    messages.append({"role": "user", "content": user_message})

    # Debug print for question being sent
    print(f"Debug: Sending question to ChatGPT: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Use 'gpt-3.5-turbo' or 'gpt-4' or 'gpt-4-turbo' or 'gpt-4o-mini'
            messages=messages,
            temperature=0.3,  # Lower temperature to encourage more direct answers
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

    # Construct a generalized comparison prompt for OpenAI
    comparison_prompt = (
        f"The original answer is: {original_answer}\n\n"
        f"The question was: {question}\n\n"
        f"The AI's response was: {ai_engine_answer}\n\n"
        "Does the AI's response contain the key piece of information that matches the original answer? "
        "Focus on the specific information requested in the question. "
        "Respond strictly with one word: 'YES' if the key information matches, or 'NO' if it does not. "
        "Do not include any explanations or extra words, respond only with 'YES' or 'NO'."
    )

    # Debug print for comparison being sent
    print(f"Debug: Sending comparison prompt to ChatGPT:\n{comparison_prompt}")

    try:
        # Send the generalized comparison prompt to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": comparison_prompt}],
            temperature=0,  # Zero temperature for deterministic results
        )
        
        # Extract the response
        comparison_result = response['choices'][0]['message']['content'].strip().lower()

        # Debug print for the response from ChatGPT
        print(f"Debug : Received comparison response from ChatGPT: {comparison_result}")

        # Normalize the result to handle variations of 'yes' and 'no'
        if 'yes' in comparison_result:
            if instructions:
                return 'Correct with Instruction'
            else:
                return 'Correct without Instruction'
        elif 'no' in comparison_result:
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
