# Assignment1-GAIA-OpenAI-Evaluation-Tool

# OpenAI Evaluation Streamlit App

This repository contains a Streamlit-based application designed to evaluate datasets of questions using the OpenAI API. The app processes structured and unstructured data, integrates with AWS S3 for file storage, and uses Azure SQL for data management.

## Features

- **OpenAI API Integration:** Evaluates questions using OpenAI's ChatGPT model.
- **AWS S3 Integration:** Uploads and retrieves files from AWS S3 for persistent storage.
- **Azure SQL Integration:** Stores and manages processed data in an Azure SQL database.
- **Streamlit Web Interface:** Provides a user-friendly interface to upload data, explore results, and visualize evaluations.

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Project Structure
📦 openai-evaluation-streamlit
 ┣ 📂 .cache               # Temporary files for caching
 ┣ 📜 README.md            # Main README file
 ┣ 📂 scripts              # Core application logic
 ┃ ┣ 📂 api_utils          # API interaction scripts (AWS, Azure, OpenAI)
 ┃ ┣ 📂 data_handling      # Data loading, preprocessing, and cleanup
 ┃ ┣ 📜 main.py            # Main script to execute the application
 ┣ 📂 streamlit_pages      # Pages for the Streamlit web interface
 ┣ 📜 app.py               # Main entry point for the Streamlit app
 ┣ 📜 .env                 # Environment variable configuration
 ┣ 📜 .gitignore           # File to exclude unnecessary files from Git
 ┣ 📜 poetry.lock          # Poetry lock file for dependencies
 ┣ 📜 pyproject.toml       # Poetry project configuration
 ┣ 📜 LICENSE              # License for the project

## Installation

To get the project running on your local machine, follow these steps:

### Prerequisites

Make sure you have the following installed:
- Python 3.x
- Poetry (for dependency management)
- AWS account (for S3 storage)
- Azure SQL database (for data management)
- OpenAI API key (for accessing OpenAI models)

### Steps

1. Clone the repository:

   git clone https://github.com/your-username/openai-evaluation-streamlit.git  
   cd openai-evaluation-streamlit

2. Install dependencies using Poetry:

   poetry install

3. Set up environment variables:

   Create a `.env` file in the root of the project and add your credentials for AWS, Azure, and OpenAI:
  
      HF_TOKEN='your-hugging-face-token'
      OPENAI_API_KEY='your-openai-api-key'
      AWS_ACCESS_KEY='your-aws-access-key'
      AWS_SECRET_KEY='your-aws-secret-key'
      S3_BUCKET_NAME='your-s3-bucket-name'
      GAIA_REPO_URL='https://huggingface.co/datasets/gaia-benchmark/GAIA'
      CSV_PATH='path-to-your-csv'
      AZURE_SQL_SERVER='your-azure-sql-server'
      AZURE_SQL_DATABASE='your-azure-sql-database'
      AZURE_SQL_TABLE='your-azure-sql-table'
      AZURE_SQL_USER='your-azure-sql-username'
      AZURE_SQL_PASSWORD='your-azure-sql-password'


4. Set up Azure SQL and AWS S3:

   - Azure SQL: Ensure you have an Azure SQL database set up. Use the connection string in your `.env` file.
   - AWS S3: Set up an S3 bucket for file storage. The AWS credentials should be added to the `.env` file.

5. Run the application:

   streamlit run app.py

6. Explore the web interface:

   Once the app is running, navigate to the URL displayed in the terminal (usually `http://localhost:8501`) to interact with the web interface, upload files, and view the results.

## Usage

Once the application is set up and the environment variables are configured, follow these steps to use the app:

1. Run the Streamlit app:

   streamlit run app.py

2. Explore the web interface:

   Once the app is running, navigate to the URL displayed in the terminal (usually `http://localhost:8501`) to interact with the web interface. The app provides the following features:

   - **Preloaded Questions from GAIA Dataset:** The app already contains a list of questions from the GAIA dataset.
   - **Final Answer Comparison:** Each question in the dataset has a "final answer." The ChatGPT model generates an answer for each question, and the app compares this generated answer with the final answer provided in the dataset.
   - **Evaluation Process:** ChatGPT evaluates how well its answer matches the final answer from the dataset. This comparison helps determine whether the model provided the correct or incorrect response.
   - **File Download and Preprocessing:** If a question is associated with a file (e.g., image, audio), the file is automatically downloaded and preprocessed before being sent to the ChatGPT model for evaluation.
   - **Result Visualization:** After the evaluation, the results are displayed using **Matplotlib** charts for easy analysis and interpretation.

3. Data Processing:

   The app processes the preloaded questions from the GAIA dataset and sends them to OpenAI’s ChatGPT for evaluation. The model generates an answer, and the app compares this answer with the final answer in the dataset to determine its accuracy. Any associated files (e.g., images, audio) are downloaded, preprocessed, and included in the evaluation request if necessary.

   - Results of the comparison (whether ChatGPT's answer matches the final answer) are stored in Azure SQL for further analysis.
   - The results are visualized using **Matplotlib**, providing a clear view of the evaluation process and performance.
   - The app provides a comprehensive summary of how accurately ChatGPT responds to each question compared to the dataset's final answers.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.


