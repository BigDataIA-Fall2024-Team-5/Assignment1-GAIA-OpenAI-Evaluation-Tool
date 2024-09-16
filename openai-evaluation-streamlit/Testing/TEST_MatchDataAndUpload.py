# test_s3_upload.py
import os
import pandas as pd
import boto3

# Initialize AWS S3 client
def init_s3_client(access_key, secret_key):
    return boto3.client('s3',
                        aws_access_key_id=access_key,
                        aws_secret_access_key=secret_key)

# Upload files to S3 and update paths in the DataFrame
def upload_files_to_s3_and_update_paths(dataset, s3_client, bucket_name, repo_dir):
    for index, row in dataset.iterrows():
        if 'file_name' in row and row['file_name']:
            # Find the file in the repository
            local_file_path = os.path.join(repo_dir, "2023", "validation", row['file_name'])
            if os.path.exists(local_file_path):
                # Upload to S3
                try:
                    s3_client.upload_file(local_file_path, bucket_name, row['file_name'])
                    # Update file path to S3 URL
                    dataset.at[index, 'file_path'] = f"https://{bucket_name}.s3.amazonaws.com/{row['file_name']}"
                    print(f"Uploaded {row['file_name']} to S3.")
                except Exception as e:
                    print(f"Error uploading {row['file_name']} to S3: {e}")
            else:
                print(f"File {row['file_name']} not found in {local_file_path}")
    return dataset

# Test the functions
if __name__ == "__main__":
    aws_access_key = 'AKIARSU7KMPCQQEZE6HR'
    aws_secret_key = '2/9qN3UiySCfIrOAKG8brGj85+VrMEPQ2d9wwT3D'
    bucket_name = 's3-openai-evaluation-app-storage'
    repo_dir = './custom_cache/gaia_repo_test'  # Replace with your repo directory
    
    # Sample DataFrame with file names
    data = {
        'file_name': ['cffe0e32-c9a6-4c52-9877-78ceb4aaa9fb.docx', '8f80e01c-1296-4371-9486-bb3d68651a60.png'],
        'file_path': [''] * 2  # This will be updated with S3 URLs
    }
    df = pd.DataFrame(data)
    
    try:
        # Step 1: Initialize S3 client
        print("Initializing S3 client...")
        s3_client = init_s3_client(aws_access_key, aws_secret_key)
        
        # Step 2: Upload files to S3 and update paths
        print("Uploading files to S3...")
        df_updated = upload_files_to_s3_and_update_paths(df, s3_client, bucket_name, repo_dir)
        
        # Step 3: Display the updated DataFrame
        print("\nUpdated DataFrame with S3 URLs:")
        print(df_updated)
        
        # Save the updated DataFrame to a new CSV file for verification
        output_csv_file = 'test_s3_upload_results.csv'
        df_updated.to_csv(output_csv_file, index=False)
        print(f"\nData with updated file paths successfully saved to {output_csv_file}")
        
    except Exception as e:
        print(f"Error: {e}")
