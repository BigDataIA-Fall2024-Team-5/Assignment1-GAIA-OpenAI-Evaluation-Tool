import os
import pymssql
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_azure_sql_connection():
    """
    Establishes a connection to the Azure SQL Database using pymssql.
    
    Returns:
        conn: The pymssql connection object.
    """
    try:
        # Establish the connection using pymssql
        conn = pymssql.connect(
            server=os.getenv('AZURE_SQL_SERVER'),
            user=os.getenv('AZURE_SQL_USER'),
            password=os.getenv('AZURE_SQL_PASSWORD'),
            database=os.getenv('AZURE_SQL_DATABASE'),
            port=1433
        )
        return conn
    except pymssql.Error as e:
        print(f"Error connecting to Azure SQL Database: {e}")
        return None

def insert_dataframe_to_sql(df, table_name):
    """
    Inserts a DataFrame into the specified table in Azure SQL Database using pymssql.
    If the table already exists, it drops the table and creates it again.
    
    Args:
        df (pd.DataFrame): The DataFrame to be inserted.
        table_name (str): The name of the table in Azure SQL Database.
    """
    try:
        # Get a connection to Azure SQL
        conn = get_azure_sql_connection()
        if conn is None:
            print("Failed to connect to Azure SQL Database.")
            return
        cursor = conn.cursor()

        # Drop the table if it exists
        drop_table_query = f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};"
        cursor.execute(drop_table_query)
        conn.commit()

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
        cursor.execute(create_table_query)
        conn.commit()

        # Insert the DataFrame into the Azure SQL table
        for index, row in df.iterrows():
            insert_query = f"""
            INSERT INTO {table_name} (
                task_id, Question, Level, FinalAnswer, file_name, file_path, 
                Annotator_Metadata_Steps, Annotator_Metadata_Number_of_steps, 
                Annotator_Metadata_How_long_did_this_take, Annotator_Metadata_Tools, 
                Annotator_Metadata_Number_of_tools, result_status, created_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            try:
                cursor.execute(insert_query, 
                               (row['task_id'], row['Question'], row['Level'], row['Final answer'], 
                                row['file_name'], row['file_path'], 
                                row['Annotator_Metadata_Steps'], row['Annotator_Metadata_Number of steps'], 
                                row['Annotator_Metadata_How long did this take?'], row['Annotator_Metadata_Tools'], 
                                row['Annotator_Metadata_Number of tools'], row.get('result_status', 'N/A'),
                                row['created_date'])
                              )
            except pymssql.Error as e:
                print(f"Error inserting row with task_id {row['task_id']}: {e}")
                continue  # Skip this row and move to the next one
        
        conn.commit()
        print(f"Data successfully inserted into {table_name} in Azure SQL Database.")
        
    except Exception as e:
        print(f"Error inserting data into Azure SQL Database: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()
