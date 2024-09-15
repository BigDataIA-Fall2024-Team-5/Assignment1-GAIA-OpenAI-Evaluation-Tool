import os
import boto3

# Initialize the S3 client (using the AWS CLI credentials configured earlier)
s3_client = boto3.client('s3')

def upload_folder_to_s3(folder_path, bucket_name, s3_folder_path=''):
    """
    Uploads the contents of a local folder to an S3 bucket.

    :param folder_path: Path to the local folder to upload
    :param bucket_name: S3 bucket name
    :param s3_folder_path: S3 path where the folder will be uploaded
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            # Create the full local path
            local_file_path = os.path.join(root, file_name)
            # Create the full S3 path
            relative_path = os.path.relpath(local_file_path, folder_path)
            s3_file_path = os.path.join(s3_folder_path, relative_path).replace("\\", "/")  # Use forward slashes for S3 paths
            
            try:
                # Upload the file to S3
                s3_client.upload_file(local_file_path, bucket_name, s3_file_path)
                print(f"Uploaded {local_file_path} to s3://{bucket_name}/{s3_file_path}")
            except Exception as e:
                print(f"Error uploading {local_file_path}: {e}")

# Define your folder path and bucket name
folder_path = r'C:\Users\Linata04\Desktop\Big Data Semester 3\Assignment1_github\Assignment1-GAIA-OpenAI-Evaluation-Tool\openai-evaluation-streamlit\Testing\dump'
bucket_name = 's3gaiabucket'

# Define the S3 path where the folder contents will be uploaded
s3_folder_path = 'Testing/dump'

# Call the function to upload the folder to S3
upload_folder_to_s3(folder_path, bucket_name, s3_folder_path)
