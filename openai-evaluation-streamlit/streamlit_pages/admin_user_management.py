import streamlit as st
from scripts.api_utils.azure_sql_utils import fetch_all_users, remove_user, promote_to_admin

# Function to delete a user with session state tracking
def handle_delete_user(username):
    try:
        remove_user(username)
        st.session_state['user_action_success'] = f"User '{username}' deleted successfully."
    except Exception as e:
        st.session_state['user_action_success'] = f"Failed to delete user '{username}': {e}"

# Function to promote a user to admin with session state tracking
def handle_promote_user(username):
    try:
        promote_to_admin(username)
        st.session_state['user_action_success'] = f"User '{username}' promoted to admin."
    except Exception as e:
        st.session_state['user_action_success'] = f"Failed to promote user '{username}': {e}"

def admin_user_management_page():
    st.title("User Management")

    # Check if there's a success message stored in session state and display it
    if 'user_action_success' in st.session_state and st.session_state['user_action_success']:
        st.success(st.session_state['user_action_success'])
        st.session_state['user_action_success'] = ''  # Clear after displaying the message

    # Fetch all users from the database
    users = fetch_all_users()

    if users:
        st.write("Below is the list of users in the system:")

        # Display users in a table
        for user in users:
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            col1.write(user["user_id"])
            col2.write(user["username"])
            col3.write(user["role"])

            # Only allow promoting if the user is not already an admin
            if user["role"] != "admin":
                col4.button(f"Promote to Admin", key=f"promote_{user['user_id']}", on_click=lambda u=user["username"]: handle_promote_user(u))
            
            # Button to delete the user
            col4.button(f"Delete User", key=f"delete_{user['user_id']}", on_click=lambda u=user["username"]: handle_delete_user(u))
    else:
        st.write("No users found.")

    # Back button to return to the Admin page
    st.button("Back to Admin", on_click=lambda: st.session_state.update(page='admin'))
