# load_data.py
import os
import pandas as pd
from datasets import load_dataset

# Load the GAIA dataset using Hugging Face with authentication
def load_gaia_dataset():
    # Set the environment variable for Hugging Face token
    os.environ["HF_TOKEN"] = "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"
    #Or we can login using huggingface-cli login
    
    # Specify the configuration to load
    #Available: ['2023_all', '2023_level1', '2023_level2', '2023_level3']
    config_name = '2023_level1'
    
    # Authenticate and load the dataset with the chosen configuration
    ds = load_dataset('gaia-benchmark/GAIA', config_name, trust_remote_code=True)
    
    # Select the split to load, 'test' or 'validation'
    split_name = 'validation'  # Change this to 'test' if you want to load the test split

    # Check the structure of the selected split
    print(f"Selected split '{split_name}' structure:", ds[split_name])

    # Attempt to convert to DataFrame
    try:
        # Convert to DataFrame
        df = pd.DataFrame(ds[split_name])
        # Flatten the 'Annotator Metadata' column
        df = preprocess_nested_data(df)
        print("Dataset successfully converted to DataFrame.")
    except Exception as e:
        print(f"Error converting dataset to DataFrame: {e}")
        return None

    return df

def preprocess_nested_data(df):
    # Flatten the 'Annotator Metadata' column
    if 'Annotator Metadata' in df.columns:
        # Normalize the 'Annotator Metadata' column into separate columns
        metadata_df = pd.json_normalize(df['Annotator Metadata'])
        # Rename columns to include a prefix for clarity
        metadata_df.columns = [f"Annotator_Metadata_{col}" for col in metadata_df.columns]
        # Concatenate with the original DataFrame, dropping the original 'Annotator Metadata' column
        df = pd.concat([df.drop(columns=['Annotator Metadata']), metadata_df], axis=1)
    
    return df

# Test loading the dataset and export to CSV
if __name__ == "__main__":
    try:
        df = load_gaia_dataset()
        if df is not None:
            print("Data loaded successfully")
            print(df.head())  # Display the first few rows of the dataset
            
            # Save the DataFrame to a CSV file
            output_csv_file = 'dump/gaia_level1_test.csv'  # Specify the output file name
            df.to_csv(output_csv_file, index=False)
            print(f"Data successfully saved to {output_csv_file}")
    except Exception as e:
        print(f"Error loading data: {e}")
