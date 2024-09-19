#main.py
import os
from dotenv import load_dotenv
from clone_repo import clone_repository
from load_dataset import load_gaia_dataset
from s3_upload import init_s3_client, upload_files_to_s3_and_update_paths
from huggingface_hub import login
from azure_sql_utils import insert_dataframe_to_sql 
from datetime import datetime  # Import datetime for created_date

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Set the environment variable for Hugging Face cache directory
    cache_dir = './.cache'
    
    os.environ["HF_HOME"] = cache_dir
    os.environ["HF_DATASETS_CACHE"] = cache_dir

    # Ensure that the cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    # Get the environment variables
    hf_token = os.getenv('HF_TOKEN')
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    repo_url = os.getenv('GAIA_REPO_URL')

    # Ensure tokens are available
    if not hf_token:
        print("Error: Hugging Face token not found in environment variables. Please set the HF_TOKEN environment variable.")
        exit(1)

    # Programmatically login to Hugging Face without adding to Git credentials
    login(token=hf_token, add_to_git_credential=False)

    try:
        # Step 1: Clone the repository
        clone_dir = os.path.join(cache_dir, "gaia_repo") 
        print("Cloning the repository...")
        clone_repository(repo_url, clone_dir)

        # Step 2: Load the dataset
        print("Loading the dataset...")
        df = load_gaia_dataset(cache_dir)
        if df is not None:
            print("Data loaded successfully")
            print(df.head())  # Display the first few rows of the dataset
            
            # Add the 'created_date' column with the current timestamp
            df['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Step 3: Initialize S3 client
            print("Initializing S3 client...")
            s3_client = init_s3_client(aws_access_key, aws_secret_key)
            
            # Step 4: Upload files to S3 and update paths
            print("Uploading files to S3...")
            df = upload_files_to_s3_and_update_paths(df, s3_client, bucket_name, clone_dir)
            
            # Step 5: Insert the updated DataFrame into Azure SQL Database before saving to CSV
            print("Inserting data into Azure SQL Database...")
            table_name = "GaiaDataset"  # Define your table name in Azure SQL Database
            insert_dataframe_to_sql(df, table_name)  # Insert the DataFrame into Azure SQL

            # Step 6: Save the updated DataFrame to a new CSV file
            output_dir = os.path.join(cache_dir, 'data_to_azuresql')  # Set the output directory under cache
            os.makedirs(output_dir, exist_ok=True)
            output_csv_file = os.path.join(output_dir, 'gaia_data_view.csv')
            df.to_csv(output_csv_file, index=False)
            print(f"\nData with updated file paths successfully saved to {output_csv_file}")

        else:
            print("Data loading failed.")
    except Exception as e:
        print(f"Error: {e}")
