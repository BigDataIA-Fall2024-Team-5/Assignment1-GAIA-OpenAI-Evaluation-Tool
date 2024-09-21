# Scripts

This folder contains the core scripts that power the OpenAI Evaluation App. The scripts are organized into two main subfolders and also contain the main orchestration script.

## Files

- **main.py**: 
  - This is the main orchestration script responsible for the initial setup and execution of the app's key functions. It loads the GAIA dataset, uploads files to AWS S3, stores the data in Azure SQL, and prepares the data for ChatGPT evaluation.

## Subfolders

1. **api_utils**: Handles API interactions for AWS S3, Azure SQL, and OpenAI ChatGPT.
2. **data_handling**: Responsible for managing data-related tasks such as cloning repositories, processing files, and deleting cache.

Refer to the respective subfolder `README.md` files for more details on the functionality of each set of scripts.
