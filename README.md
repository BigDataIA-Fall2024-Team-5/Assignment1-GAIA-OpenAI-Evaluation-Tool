# Assignment1-GAIA-OpenAI-Evaluation-Tool

- **Application Link: https://team5-assignment1.streamlit.app**
- **Code Lab Link: https://codelabs-preview.appspot.com/?file_id=1a1lWq_iTi-cp2h0ZCZ2yJs9ST9suEgrhw78o4ldVr0M#0**
- **Presentation Video Link: https://drive.google.com/file/d/1HdkIqzupZM6o4eZYRvcK_zLyv5mOZoi2/view?usp=drive_link**

## OpenAI Evaluation App - Quick Overview

Welcome to the **OpenAI Evaluation App**! This application leverages OpenAI's ChatGPT model to evaluate a dataset of questions. The app is designed to streamline the evaluation process by handling datasets with associated files, uploading them to cloud storage, and storing results in a database. It includes a user-friendly web interface built using **Streamlit**, providing clear visual insights through **Matplotlib**.

## Key Features

- **GAIA Dataset Integration**: The app loads questions from the GAIA benchmark dataset, allowing users to evaluate how well ChatGPT's answers match the "final answer" provided in the dataset.
- **File Retrieval**: The application preprocesses various file formats (such as text, CSV, Excel, JSON-LD, Word, PDF, and PowerPoint) and uploads these files to AWS S3 for secure storage. Unsupported files, including audio, image and zip formats, are flagged accordingly.
- **ChatGPT Evaluation**: The core functionality revolves around using ChatGPT to generate answers for each question. The generated responses are then compared to the final answers in the dataset to determine their accuracy.
- **AWS S3 and Azure SQL Integration**: Files are securely stored in AWS S3, and processed data (including file paths and evaluation results) is pushed to an Azure SQL database.
- **User and Admin Management**: The app includes a role-based access control system. Admins can manage users, promote them to admin roles, or delete them. The system also includes a registration page for new users.
- **Database Setup**: A setup script (`setup_database.py`) initializes Azure SQL tables and inserts default users.
- **Visualization with Matplotlib**: The app provides a visual representation of the evaluation results, helping users easily interpret ChatGPT's performance.

## Why This App?

This app makes it easy to:
- **Automate the evaluation** of large datasets using OpenAI's language models.
- **Handle multimedia files** including text, CSV, Word, PDF, and more, with automated file preprocessing.
- **Manage users and roles** with admin-level control for promoting or deleting users.
- **Setup Azure SQL tables** with the provided `setup_database.py` script.
- **Visualize results** and store them for future analysis with the help of cloud storage (AWS S3) and database systems (Azure SQL).
- **Enhance efficiency** in handling complex datasets by automating data preprocessing and storage.

For detailed instructions on how to set up and run the application, please refer to the **Main README.md** file.

## Attestation

WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR
ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK

**Contribution**
- **Dharun Karthick Ramaraj** 33.33%
- **Nikhil Godalla** 33.33%
- **Linata Deshmukh** 33.33%


## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
