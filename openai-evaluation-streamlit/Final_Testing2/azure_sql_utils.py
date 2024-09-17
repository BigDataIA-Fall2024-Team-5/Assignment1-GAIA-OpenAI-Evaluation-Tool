import os
import pyodbc
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_azure_sql_connection():
    """
    Establishes a connection to the Azure SQL Database.
    
    Returns:
        conn: The pyodbc connection object.
    """
    # Construct the connection string
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.environ.get('AZURE_SQL_SERVER')};"
        f"DATABASE={os.environ.get('AZURE_SQL_DATABASE')};"
        f"UID={os.environ.get('AZURE_SQL_USER')};"
        f"PWD={os.environ.get('AZURE_SQL_PASSWORD')}"
    )
    
    # Establish the connection
    conn = pyodbc.connect(connection_string)
    return conn

def insert_dataframe_to_sql(df, table_name):
    """
    Inserts a DataFrame into the specified table in Azure SQL Database.
    If the table already exists, it drops the table and creates it again.
    
    Args:
        df (pd.DataFrame): The DataFrame to be inserted.
        table_name (str): The name of the table in Azure SQL Database.
    """
    try:
        # Get a connection to Azure SQL
        conn = get_azure_sql_connection()
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
            file_path NVARCHAR(500),
            Annotator_Metadata_Steps NVARCHAR(MAX),
            Annotator_Metadata_Number_of_steps INT,
            Annotator_Metadata_How_long_did_this_take NVARCHAR(50),
            Annotator_Metadata_Tools NVARCHAR(MAX),
            Annotator_Metadata_Number_of_tools INT,
            result_status NVARCHAR(50) DEFAULT 'N/A'
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
                Annotator_Metadata_Number_of_tools, result_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, 
                           row['task_id'], row['Question'], row['Level'], row['Final answer'], 
                           row['file_name'], row['file_path'], 
                           row['Annotator_Metadata_Steps'], row['Annotator_Metadata_Number of steps'], 
                           row['Annotator_Metadata_How long did this take?'], row['Annotator_Metadata_Tools'], 
                           row['Annotator_Metadata_Number of tools'], row.get('result_status', 'N/A')
                          )
        
        conn.commit()
        conn.close()
        print(f"Data successfully inserted into {table_name} in Azure SQL Database.")
    except Exception as e:
        print(f"Error inserting data into Azure SQL Database: {e}")
