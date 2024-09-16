# main.py
import os
from clone_repo import clone_repository
from load_dataset import load_gaia_dataset
from s3_upload import init_s3_client, upload_files_to_s3_and_update_paths

if __name__ == "__main__":
    repo_url = "https://huggingface.co/datasets/gaia-benchmark/GAIA"
    clone_dir = "./custom_cache/gaia_repo_test"
    aws_access_key = 'AKIARSU7KMPC6DA5Y3KY'
    aws_secret_key = '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'
    bucket_name = 's3-openai-evaluation-app-storage'

    try:
        # Step 1: Clone the repository
        print("Cloning the repository...")
        clone_repository(repo_url, clone_dir)

        # Step 2: Load the dataset
        print("Loading the dataset...")
        df = load_gaia_dataset()
        if df is not None:
            print("Data loaded successfully")
            print(df.head())  # Display the first few rows of the dataset
            
            # Step 3: Initialize S3 client
            print("Initializing S3 client...")
            s3_client = init_s3_client(aws_access_key, aws_secret_key)
            
            # Step 4: Upload files to S3 and update paths
            print("Uploading files to S3...")
            df = upload_files_to_s3_and_update_paths(df, s3_client, bucket_name, clone_dir)
            
            # Step 5: Save the updated DataFrame to a new CSV file
            output_dir = 'dump'
            os.makedirs(output_dir, exist_ok=True)
            output_csv_file = os.path.join(output_dir, 'gaia_level1_test_updated.csv')
            df.to_csv(output_csv_file, index=False)
            print(f"\nData with updated file paths successfully saved to {output_csv_file}")
        else:
            print("Data loading failed.")
    except Exception as e:
        print(f"Error: {e}")
