import os
import subprocess

# Clone the Git repository containing the dataset files
def clone_repository(repo_url, clone_dir):
    if not os.path.exists(clone_dir):
        # Clone the repository using git
        try:
            # Install git-lfs if not already installed
            subprocess.run(["git", "lfs", "install"], check=True)
            
            # Clone the repository
            subprocess.run(["git", "clone", repo_url, clone_dir], check=True)
            print(f"Repository successfully cloned into {clone_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
    else:
        print(f"Repository already cloned in {clone_dir}")

# Find a file by name in the repository
def find_file_in_repo(file_name, repo_dir):
    # Construct the expected file path
    search_path = os.path.join(repo_dir, "2023", "validation", file_name)
    if os.path.exists(search_path):
        print(f"File {file_name} found at {search_path}")
        return search_path
    else:
        print(f"File {file_name} not found in {search_path}")
        return None

# Test the functions
if __name__ == "__main__":
    # Define a custom cache directory
    custom_cache_dir = './custom_cache'
    
    # Define the repository URL and directory to clone into
    repo_url = "https://huggingface.co/datasets/gaia-benchmark/GAIA"
    clone_dir = os.path.join(custom_cache_dir, "gaia_repo_test")  # Custom directory within cache
    
    # Ensure the custom cache directory exists
    os.makedirs(custom_cache_dir, exist_ok=True)

    # Define a test file name
    test_file_name = "cffe0e32-c9a6-4c52-9877-78ceb4aaa9fb.docx"  # Replace with a known file name you want to test

    # Test cloning the repository
    print("Testing repository cloning...")
    clone_repository(repo_url, clone_dir)

    # Test finding a file in the repository
    print("\nTesting file search in repository...")
    found_file_path = find_file_in_repo(test_file_name, clone_dir)

    if found_file_path:
        print(f"File search successful: {found_file_path}")
    else:
        print("File search failed.")
