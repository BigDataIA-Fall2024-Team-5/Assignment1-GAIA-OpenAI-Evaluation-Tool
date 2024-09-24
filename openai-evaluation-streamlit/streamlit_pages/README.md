# Streamlit Pages

This folder contains the individual pages that make up the user interface of the OpenAI Evaluation App, built using **Streamlit**. Each page corresponds to a different functionality within the app.

## Files

- **explore_questions.py**: 
  - This page allows users to explore the questions in the GAIA dataset. Users can select a question, view the associated file (if available), and send the question to ChatGPT for evaluation. The results are then displayed on this page.
  
- **view_summary.py**: 
  - This page provides a summary of the evaluation results, visualized using **Matplotlib**. Users can view a bar chart showing the distribution of correct and incorrect answers, along with detailed counts of the evaluation results.

- **admin_page.py**:
  - The admin dashboard that allows authorized users to manage datasets and users in the system. It includes navigation to sub-pages for dataset and user management.

- **admin_dataset_management.py**:
  - This page allows the admin to trigger the processing of the GAIA dataset, including uploading files to AWS S3 and storing records in Azure SQL. It provides a button to initiate the process and displays the status of the operation.

- **admin_user_management.py**:
  - This page allows the admin to manage users, including deleting users or promoting them to admin roles. A table of users is displayed with options for actions on each user.

- **login_page.py**:
  - The login page for users to authenticate. It checks user credentials against the database, stores session data upon success, and redirects users based on their roles (admin or regular user).

- **register_page.py**:
  - The registration page for new users to create accounts. It verifies the uniqueness of the username and ensures passwords match before storing the new user in the database.

Each page is designed to give users a smooth interface to interact with the dataset and evaluate the questions using ChatGPT.
