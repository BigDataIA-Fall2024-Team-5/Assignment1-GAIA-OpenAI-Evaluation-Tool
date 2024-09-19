#azure_sql_utils.py
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Integer, DateTime


# Load environment variables from .env file
load_dotenv()

def get_sqlalchemy_connection_string():
    """
    Constructs an SQLAlchemy connection string for connecting to Azure SQL Database.
    
    Returns:
        str: SQLAlchemy connection string.
    """
    server = os.getenv('AZURE_SQL_SERVER')
    user = os.getenv('AZURE_SQL_USER')
    password = os.getenv('AZURE_SQL_PASSWORD')
    database = os.getenv('AZURE_SQL_DATABASE')

    connection_string = f"mssql+pymssql://{user}:{password}@{server}/{database}"
    return connection_string

def insert_dataframe_to_sql(df, table_name):
    """
    Inserts a DataFrame into the specified table in Azure SQL Database using SQLAlchemy.
    If the table already exists, it drops the table and creates it again.
    
    Args:
        df (pd.DataFrame): The DataFrame to be inserted.
        table_name (str): The name of the table in Azure SQL Database.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        # Drop the table if it exists
        with engine.connect() as connection:
            drop_table_query = f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};"
            connection.execute(drop_table_query)

            # Create the table
            create_table_query = f"""
            CREATE TABLE {table_name} (
                task_id NVARCHAR(50) PRIMARY KEY, 
                Question NVARCHAR(MAX),
                Level INT,
                FinalAnswer NVARCHAR(MAX),
                file_name NVARCHAR(255),
                file_path NVARCHAR(MAX),
                Annotator_Metadata_Steps NVARCHAR(MAX),
                Annotator_Metadata_Number_of_steps NVARCHAR(MAX),
                Annotator_Metadata_How_long_did_this_take NVARCHAR(100),
                Annotator_Metadata_Tools NVARCHAR(MAX),
                Annotator_Metadata_Number_of_tools INT,
                result_status NVARCHAR(50) DEFAULT 'N/A',
                created_date DATETIME
            );
            """
            connection.execute(create_table_query)

        # Insert the DataFrame into the Azure SQL table
        df.to_sql(table_name, engine, if_exists='append', index=False, dtype={
            'task_id': NVARCHAR(length=50),
            'Question': NVARCHAR(length='max'),
            'Level': Integer,
            'FinalAnswer': NVARCHAR(length='max'),
            'file_name': NVARCHAR(length=255),
            'file_path': NVARCHAR(length='max'),
            'Annotator_Metadata_Steps': NVARCHAR(length='max'),
            'Annotator_Metadata_Number_of_steps': NVARCHAR(length='max'),
            'Annotator_Metadata_How_long_did_this_take': NVARCHAR(length=100),
            'Annotator_Metadata_Tools': NVARCHAR(length='max'),
            'Annotator_Metadata_Number_of_tools': Integer,
            'result_status': NVARCHAR(length=50),
            'created_date': DateTime
        })
        
        print(f"Data successfully inserted into {table_name} in Azure SQL Database.")
        
    except Exception as e:
        print(f"Error inserting data into Azure SQL Database: {e}")

def fetch_dataframe_from_sql(table_name='GaiaDataset'):
    """
    Fetches the Gaia dataset from the Azure SQL Database and returns it as a pandas DataFrame.
    
    Args:
        table_name (str): The name of the table to fetch the data from.
    
    Returns:
        pd.DataFrame: The dataset as a DataFrame, or None if fetching fails.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        # Fetch data using pandas read_sql
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        return df

    except Exception as e:
        print(f"Error fetching data from Azure SQL Database: {e}")
        return None


def update_result_status(task_id, status, table_name='GaiaDataset'):
    """
    Updates the result_status for a specific task in the Azure SQL Database using SQLAlchemy.
    
    Args:
        task_id (str): The task_id of the row to update.
        status (str): The new status to set.
        table_name (str): The name of the table to update the data in.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        with engine.connect() as connection:
            # Start a transaction
            transaction = connection.begin()
            try:
                # Use the text() function to wrap the SQL query string
                update_query = text(f"UPDATE {table_name} SET result_status = :status WHERE task_id = :task_id")
                connection.execute(update_query, {'status': status, 'task_id': task_id})
                
                # Commit the transaction
                transaction.commit()
                print(f"Updated result_status for task_id {task_id} to {status}.")
            except Exception as e:
                transaction.rollback()
                print(f"Transaction rolled back due to an error: {e}")
        
    except Exception as e:
        print(f"Error updating result_status in Azure SQL Database: {e}")



