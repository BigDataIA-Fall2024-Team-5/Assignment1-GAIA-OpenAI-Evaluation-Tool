# Assignment1-GAIA-OpenAI-Evaluation-Tool

## OpenAI Evaluation App - Quick Overview

Welcome to the **OpenAI Evaluation App**! This application leverages OpenAI's ChatGPT model to evaluate a dataset of questions. The app is designed to streamline the evaluation process by handling datasets with associated files, uploading them to cloud storage, and storing results in a database. It includes a user-friendly web interface built using **Streamlit**, providing clear visual insights through **Matplotlib**.

## Key Features

- **GAIA Dataset Integration**: The app loads questions from the GAIA benchmark dataset, allowing users to evaluate how well ChatGPT's answers match the "final answer" provided in the dataset.
- **File Retrieval**: For questions with associated files (e.g., images, audio), the app downloads and uploads these files to AWS S3 for secure storage.
- **ChatGPT Evaluation**: The core functionality revolves around using ChatGPT to generate answers for each question. The generated responses are then compared to the final answers in the dataset to determine their accuracy.
- **AWS S3 and Azure SQL Integration**: Files are securely stored in AWS S3, and processed data (including file paths and evaluation results) is pushed to an Azure SQL database.
- **Visualization with Matplotlib**: The app provides a visual representation of the evaluation results, helping users easily interpret ChatGPT's performance.

## Why This App?

This app makes it easy to:
- **Automate the evaluation** of large datasets using OpenAI's language models.
- **Handle multimedia files** (e.g., images, audio) in conjunction with textual data.
- **Visualize results** and store them for future analysis with the help of cloud storage (AWS S3) and database systems (Azure SQL).
- **Enhance efficiency** in handling complex datasets by automating data preprocessing and storage.

For detailed instructions on how to set up and run the application, please refer to the **Main README.md** file.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
