# Data Handling Utilities

This folder contains scripts responsible for managing data operations in the OpenAI Evaluation App. These operations include cloning repositories, preprocessing files, and managing cache.

## Files

- **clone_repo.py**: 
  - Clones the GAIA dataset repository from Hugging Face and stores it locally for further processing.
  
- **delete_cache.py**: 
  - Deletes cache directories to clean up space after processing.

- **file_processor.py**: 
  - Preprocesses various file formats (e.g., `.txt`, `.csv`, `.jpg`, `.mp3`) associated with the questions. Preprocessed data is included when sending the questions to ChatGPT for evaluation.
  
- **load_dataset.py**: 
  - Loads the GAIA dataset from Hugging Face into a Pandas DataFrame for further processing and evaluation. This script also flattens and cleans up nested metadata for easier analysis.

These scripts handle all aspects of data management, ensuring that data and files are processed efficiently and correctly for evaluation by ChatGPT.
