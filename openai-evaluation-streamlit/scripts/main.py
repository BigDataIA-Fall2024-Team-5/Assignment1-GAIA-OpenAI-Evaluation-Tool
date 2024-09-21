import os
import sys
from dotenv import load_dotenv

# Add the 'scripts' folder to the Python path if it's not already there
sys.path.append(os.path.dirname(__file__))

from data_handling.clone_repo import clone_repository
from data_handling.load_dataset import load_gaia_dataset
from api_utils.amazon_s3_utils import init_s3_client, upload_files_to_s3_and_update_paths
from huggingface_hub import login
from api_utils.azure_sql_utils import insert_dataframe_to_sql
from datetime import datetime  # Import datetime for created_date
from data_handling.delete_cache import delete_cache_folder  # Import the function to delete cache

# Load environment variables from .env file
load_dotenv()

def process_dataset():
    try:
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
            return "Error: Hugging Face token not found in environment variables."

        # Programmatically login to Hugging Face without adding to Git credentials
        login(token=hf_token, add_to_git_credential=False)

        # Step 1: Clone the repository
        clone_dir = os.path.join(cache_dir, "gaia_repo")
        clone_repository(repo_url, clone_dir)

        # Step 2: Load the dataset
        df = load_gaia_dataset(cache_dir)
        if df is not None:
            # Add the 'created_date' column with the current timestamp
            df['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Step 3: Initialize S3 client
            s3_client = init_s3_client(aws_access_key, aws_secret_key)

            # Step 4: Upload files to S3 and update paths
            df = upload_files_to_s3_and_update_paths(df, s3_client, bucket_name, clone_dir)

            # Step 5: Insert the updated DataFrame into Azure SQL Database before saving to CSV
            table_name = "GaiaDataset"
            insert_dataframe_to_sql(df, table_name)

            # Step 6: Save the updated DataFrame to a new CSV file
            output_dir = os.path.join(cache_dir, 'data_to_azuresql')
            os.makedirs(output_dir, exist_ok=True)
            output_csv_file = os.path.join(output_dir, 'gaia_data_view.csv')
            df.to_csv(output_csv_file, index=False)

            # Optional: Step 7: Delete the cache directory
            # delete_cache_folder(cache_dir)

            # Return a summary of the processing steps instead of the CSV file location
            return f"""
            Dataset processing complete:
            - Repository cloned to: {clone_dir}
            - Dataset successfully loaded
            - Files uploaded to S3 bucket: {bucket_name}
            - Data inserted into Azure SQL table: {table_name}
            """
        else:
            return "Data loading failed."
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(process_dataset())
