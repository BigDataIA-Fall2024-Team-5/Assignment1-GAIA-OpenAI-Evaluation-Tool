# Scripts

This folder contains the core scripts that power the OpenAI Evaluation App. The scripts are organized into two main subfolders and also contain the main orchestration script.

## Files

- **main.py**: 
  - This is the main orchestration script responsible for the initial setup and execution of the app's key functions. It loads the GAIA dataset, uploads files to AWS S3, stores the data in Azure SQL, and prepares the data for ChatGPT evaluation.
  
- **setup_database.py**:
  - This script is responsible for setting up the database schema and seeding default users. It drops the existing `users` and `user_results` tables if they exist, then recreates them with the appropriate schema. It also inserts default admin and user credentials and hashes their passwords before storing them. The database tables are used to track user credentials, roles, and results of ChatGPT evaluations.

## Subfolders

1. **api_utils**: Handles API interactions for AWS S3, Azure SQL, and OpenAI ChatGPT.
2. **data_handling**: Responsible for managing data-related tasks such as cloning repositories, processing files, and deleting cache.

Refer to the respective subfolder `README.md` files for more details on the functionality of each set of scripts.

---

### Notes for `setup_database.py`:

- **Table Creation**: The script creates two tables:
  1. `users`: Tracks user credentials, with hashed passwords and roles (admin or user).
  2. `user_results`: Stores ChatGPT evaluation results for each user.
  
- **Default Users**: The script seeds the database with one admin and one regular user:
  - **Admin**: `username: admin`, `password: admin`
  - **User**: `username: user`, `password: user`

- **Environment Variables**: The database connection uses environment variables for credentials. Ensure that your `.env` file contains the necessary Azure SQL details (`AZURE_SQL_SERVER`, `AZURE_SQL_USER`, `AZURE_SQL_PASSWORD`, and `AZURE_SQL_DATABASE`).

---

