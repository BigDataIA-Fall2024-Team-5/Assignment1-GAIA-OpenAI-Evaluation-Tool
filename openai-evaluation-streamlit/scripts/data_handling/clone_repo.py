#clone_repo
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
