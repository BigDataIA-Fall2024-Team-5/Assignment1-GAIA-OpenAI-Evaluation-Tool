#azure_sql_utils
import os
import pandas as pd
import bcrypt
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
            # Use an explicit transaction block for dropping the table
            transaction = connection.begin()
            try:
                drop_table_query = text(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};")
                connection.execute(drop_table_query)
                transaction.commit()
                print(f"Table '{table_name}' dropped successfully.")
            except Exception as drop_error:
                transaction.rollback()
                print(f"Error dropping table '{table_name}': {drop_error}")
                return  # Exit if unable to drop the table

        # Create the table
        with engine.connect() as connection:
            create_table_query = text(f"""
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
            """)
            connection.execute(create_table_query)
            print(f"Table '{table_name}' created successfully.")

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



def fetch_user_from_sql(username):
    """
    Fetches a user from the Azure SQL Database based on the username.
    
    Args:
        username (str): The username to fetch from the database.
    
    Returns:
        dict: The user record as a dictionary, or None if the user does not exist.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        query = text(f"SELECT * FROM users WHERE username = :username")
        with engine.connect() as connection:
            result = connection.execute(query, {"username": username}).fetchone()
        
        if result:
            return dict(result)  # Return the user data as a dictionary
        else:
            return None

    except Exception as e:
        print(f"Error fetching user from Azure SQL Database: {e}")
        return None

def insert_user_to_sql(username, password, role):
    """
    Inserts a new user into the Azure SQL Database with hashed password.
    
    Args:
        username (str): The username to insert.
        password (str): The plain-text password (it will be hashed before inserting).
        role (str): The role of the user ('admin' or 'user').
    """
    try:
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        insert_user_query = text(f"""
            INSERT INTO users (user_id, username, password, role)
            VALUES (NEWID(), :username, :password, :role)
        """)
        
        with engine.connect() as connection:
            connection.execute(insert_user_query, {"username": username, "password": hashed_password, "role": role})
        
        print(f"User '{username}' added successfully.")

    except Exception as e:
        print(f"Error inserting user into Azure SQL Database: {e}")
