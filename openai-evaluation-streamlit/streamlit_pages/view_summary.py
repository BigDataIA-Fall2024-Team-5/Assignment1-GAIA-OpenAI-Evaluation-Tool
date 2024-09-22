import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

def go_back_to_main():
    st.session_state.page = 'main'

def run_summary_page(df, user_results_df):
    st.title("Summary of Results")

    # Add a "Back" button to return to the main page
    st.button("Back to Main", on_click=go_back_to_main)

    # Ensure 'task_id' is of string type in both DataFrames
    df['task_id'] = df['task_id'].astype(str)
    user_results_df['task_id'] = user_results_df['task_id'].astype(str)

    # Check if 'user_result_status' exists in the main dataset before merging and drop it to avoid conflict
    if 'user_result_status' in df.columns:
        df = df.drop(columns=['user_result_status'])

    # Perform the merge with 'task_id' to combine user results
    merged_df = df.merge(
        user_results_df[['task_id', 'user_result_status']], 
        on='task_id', 
        how='left'
    )

    # If user_result_status is missing after the merge, fill it with 'N/A'
    if 'user_result_status' not in merged_df.columns:
        st.warning("'user_result_status' column missing after merge. Filling with 'N/A'.")
        merged_df['user_result_status'] = 'N/A'
    else:
        # Fill missing user_result_status values with 'N/A'
        merged_df['user_result_status'] = merged_df['user_result_status'].fillna('N/A')

    # Filter answered questions (exclude 'N/A' status)
    answered_df = merged_df[merged_df['user_result_status'] != 'N/A']
    unanswered_count = len(merged_df) - len(answered_df)

    # Create a bar chart for 'user_result_status'
    if not answered_df.empty:
        status_counts = answered_df['user_result_status'].value_counts()

        st.write("### Result Status Distribution (Answered Questions Only)")

        # Plot the bar chart
        fig, ax = plt.subplots()
        status_counts.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_xlabel('Result Status')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Answered Questions by Result Status')
        st.pyplot(fig)

        # Display the detailed counts for each result status
        st.write("### Detailed Result Status Counts")
        st.write(status_counts)
    else:
        st.write("No answered questions to display.")

    # Display total number of questions and answered questions
    st.write(f"**Total Questions in the Dataset:** {len(merged_df)}")
    st.write(f"**Total Answered Questions:** {len(answered_df)}")
    st.write(f"**Total Unanswered Questions:** {unanswered_count}")

    # Explanation of result statuses
    st.write("### Explanation of Result Statuses:")
    st.write("""
    - **Correct without Instruction**: The answer was correct on the first attempt, without needing any instructions.
    - **Correct with Instruction**: The answer was correct after providing additional instructions.
    - **Incorrect without Instruction**: The answer was incorrect on the first attempt, without using instructions.
    - **Incorrect with Instruction**: The answer remained incorrect even after providing additional instructions.
    """)