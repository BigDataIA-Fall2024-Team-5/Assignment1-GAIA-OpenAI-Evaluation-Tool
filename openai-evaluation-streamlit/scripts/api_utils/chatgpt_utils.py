import openai
import streamlit as st

# Initialize OpenAI API
def init_openai(api_key):
    openai.api_key = api_key

# Function to send a question and preprocessed file data to ChatGPT
def get_chatgpt_response(question, instructions=None, preprocessed_data=None):
    # Construct the system message for the Chat API
    system_message = {
        "role": "system",
        "content": (
            "You are an AI assistant specialized in providing concise, accurate answers. "
            "Focus on the key information requested without adding unnecessary context. "
            "Use any provided instructions or reference data to inform your answer. "
            "For example:\n"
            "Q: What is 2 + 2? A: 4.\n"
            "Q: Name the capital of France. A: Paris.\n"
            "Q: What is the chemical symbol for water? A: H2O.\n"
            "Respond with only the essential information needed to answer the question."
        )
    }
    
    # Construct the user message with clear structure and instructions
    user_message = f"""
Question: {question}

Instructions: {instructions if instructions else 'No specific instructions provided.'}

Reference Data: {preprocessed_data if preprocessed_data else 'No reference data available.'}

Please provide a concise answer that directly addresses the question. Your response should:
1. Be no longer than 3 sentences or 50 words, whichever is shorter.
2. Include only essential information relevant to the question.
3. Use precise language and avoid unnecessary elaboration.
4. If using reference data, integrate it seamlessly without mentioning the source.

Answer:
"""

    # Debug print for question being sent
    print(f"Debug: Sending question to ChatGPT: {user_message}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Keep the specified model version
            messages=[system_message, {"role": "user", "content": user_message}],
            temperature=0.2,  # Lower temperature for more focused responses
            max_tokens=100,  # Limit token count to encourage brevity
            top_p=0.9,  # Slightly reduce randomness in token selection
            frequency_penalty=0.5,  # Discourage repetition
            presence_penalty=0.5  # Encourage new concepts when appropriate
        )
        
        # Extract and process the answer
        answer = response['choices'][0]['message']['content'].strip()
        
        # Ensure the answer does not exceed specified constraints
        sentences = answer.split('.')
        words = answer.split()
        
        if len(sentences) > 3:
            answer = '. '.join(sentences[:3]) + '.'
        if len(words) > 50:
            answer = ' '.join(words[:50]) + '...'
        
        return answer.strip()
    except Exception as e:
        st.error(f"Error calling ChatGPT API: {e}")
        return None

# Compare ChatGPT's response with the expected answer using OpenAI API
def compare_and_update_status(row, chatgpt_response, instructions):
    original_answer = str(row['FinalAnswer']).strip()
    ai_engine_answer = chatgpt_response.strip()
    question = row['Question'].strip()

    # Construct a comparison prompt for OpenAI
    comparison_prompt = f"""
Question: {question}

Original Answer: {original_answer}

AI Response: {ai_engine_answer}

Instructions:
1. Analyze if the AI's response contains the key information present in the original answer.
2. Focus on factual accuracy and relevance to the question.
3. Ignore minor differences in phrasing or additional context.
4. Respond with 'YES' if the core information matches, 'NO' if it doesn't.

Does the AI's response match the key information in the original answer? Respond with only 'YES' or 'NO'.
"""

    # Debug print for comparison being sent
    print(f"Debug: Sending comparison prompt to ChatGPT:\n{comparison_prompt}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": comparison_prompt}],
            temperature=0  # Zero temperature for deterministic results
        )
        
        comparison_result = response['choices'][0]['message']['content'].strip().lower()

        # Normalize and interpret the result
        if 'yes' in comparison_result:
            return 'Correct with Instruction' if instructions else 'Correct without Instruction'
        elif 'no' in comparison_result:
            return 'Incorrect with Instruction' if instructions else 'Incorrect without Instruction'
        else:
            st.error(f"Unexpected response from OpenAI: {comparison_result}")
            return 'Error'

    except Exception as e:
        st.error(f"Error calling OpenAI API for comparison: {e}")
        return 'Error'