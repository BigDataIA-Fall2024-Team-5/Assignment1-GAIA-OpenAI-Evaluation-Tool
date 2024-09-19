#amazon_s3_utils
import os
import boto3

# Initialize AWS S3 client
def init_s3_client(access_key, secret_key):
    """Initialize AWS S3 client."""
    return boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)

# Find a file by name in the repository
def find_file_in_repo(file_name, repo_dir):
    """Find a file by name in the local repository."""
    # Construct the expected file path
    search_path = os.path.join(repo_dir, "2023", "validation", file_name)
    if os.path.exists(search_path):
        print(f"File {file_name} found at {search_path}")
        return search_path
    else:
        print(f"File {file_name} not found in {search_path}")
        return None

# Upload files to S3 and update paths in the DataFrame
def upload_files_to_s3_and_update_paths(dataset, s3_client, bucket_name, repo_dir):
    """Upload files to S3 and update paths in the DataFrame."""
    # Counters
    total_files = 0
    files_uploaded = 0
    file_paths_updated = 0
    uploaded_file_types = set()  # Set to keep track of uploaded file types

    for index, row in dataset.iterrows():
        if 'file_name' in row and row['file_name']:
            total_files += 1  # Increment total file name counter

            # Find the file in the repository
            local_file_path = find_file_in_repo(row['file_name'], repo_dir)
            if local_file_path:
                # Upload to S3 (will overwrite if the file already exists)
                try:
                    s3_client.upload_file(local_file_path, bucket_name, row['file_name'])
                    # Update file path to S3 URL
                    dataset.at[index, 'file_path'] = f"https://{bucket_name}.s3.amazonaws.com/{row['file_name']}"
                    print(f"Uploaded {row['file_name']} to S3 (overwritten if already existed).")
                    files_uploaded += 1  # Increment files uploaded counter
                    file_paths_updated += 1  # Increment file paths updated counter

                    # Add the file type to the set
                    file_extension = os.path.splitext(row['file_name'])[1].lower()
                    uploaded_file_types.add(file_extension)  # Track unique file types
                except Exception as e:
                    print(f"Error uploading {row['file_name']} to S3: {e}")
            else:
                print(f"File {row['file_name']} not found in repository.")
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total rows with file names: {total_files}")
    print(f"Total files uploaded to S3: {files_uploaded}")
    print(f"Total file paths updated in DataFrame: {file_paths_updated}")
    print(f"Uploaded file types: {', '.join(uploaded_file_types)}") 
    
    return dataset

# Download file from S3
def download_file_from_s3(file_name, bucket_name, download_dir, s3_client):
    """Download a file from S3 to the specified directory."""
    if not file_name or not bucket_name:
        print(f"Error: file_name or bucket_name is None. file_name: {file_name}, bucket_name: {bucket_name}")
        return None
    
    os.makedirs(download_dir, exist_ok=True)  # Create download directory if not exists
    file_path = os.path.join(download_dir, file_name)  # Define the local file path

    try:
        # Attempt to download the file from S3
        s3_client.download_file(bucket_name, file_name, file_path)
        print(f"Downloaded {file_name} from S3 to {file_path}")
        return file_path  # Return the path of the downloaded file
    except Exception as e:
        print(f"Error downloading {file_name} from S3: {e}")
        return None


