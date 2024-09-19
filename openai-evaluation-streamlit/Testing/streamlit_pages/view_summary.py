# pages/view_summary.py
import streamlit as st
import matplotlib.pyplot as plt

def go_back_to_main():
    st.session_state.page = 'main'

def run_summary_page(df):
    st.title("Summary of Results")

    # Add a "Back" button to return to the main page using a callback
    st.button("Back", on_click=go_back_to_main)
    
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
