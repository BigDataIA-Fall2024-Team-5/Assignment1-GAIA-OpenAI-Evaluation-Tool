#delete_cache
import shutil
import os

def delete_cache_folder(cache_dir):
    """Delete the cache directory if it exists."""
    if os.path.exists(cache_dir):
        try:
            # Change permissions of files to allow deletion
            for root, dirs, files in os.walk(cache_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.chmod(file_path, 0o777)  # Change permissions to read/write/execute

            shutil.rmtree(cache_dir)
            print(f"Successfully deleted the cache directory: {cache_dir}")
        except Exception as e:
            print(f"Error deleting the cache directory: {e}")
    else:
        print(f"Cache directory does not exist: {cache_dir}")
