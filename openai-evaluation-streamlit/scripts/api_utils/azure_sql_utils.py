import os
import pandas as pd
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Integer, DateTime
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

def get_sqlalchemy_connection_string():
    """
    Constructs an SQLAlchemy connection string for Azure SQL Database.
    """
    server = os.getenv('AZURE_SQL_SERVER')
    user = os.getenv('AZURE_SQL_USER')
    password = os.getenv('AZURE_SQL_PASSWORD')
    database = os.getenv('AZURE_SQL_DATABASE')

    return f"mssql+pymssql://{user}:{password}@{server}/{database}"

# Function to insert a DataFrame into the SQL table (e.g., for initial data setup)
def insert_dataframe_to_sql(df, table_name):
    """
    Inserts DataFrame into Azure SQL Database (replaces existing table).
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        # Drop table if it exists
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                drop_table_query = text(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};")
                connection.execute(drop_table_query)
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                print(f"Error dropping table: {e}")
                return

        # Create the table and insert the data
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
                    user_result_status NVARCHAR(50) DEFAULT 'N/A',
                    created_date DATETIME
                );
            """)
            connection.execute(create_table_query)

        # Insert DataFrame into SQL table
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
            'user_result_status': NVARCHAR(length=50),
            'created_date': DateTime
        })

        print(f"Data successfully inserted into {table_name}.")
    
    except Exception as e:
        print(f"Error inserting data into Azure SQL: {e}")

# Function to fetch the dataset (default, e.g., main table like GaiaDataset)
def fetch_dataframe_from_sql(table_name='GaiaDataset'):
    """
    Fetches data from Azure SQL as a DataFrame.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        return df
    
    except Exception as e:
        print(f"Error fetching data from Azure SQL: {e}")
        return None

def fetch_user_results(user_id):
    """
    Fetches the user-specific results from the Azure SQL Database.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        query = text("""
            SELECT 
                user_id, 
                task_id, 
                user_result_status,
                chatgpt_response 
            FROM user_results 
            WHERE user_id = :user_id
        """)
        with engine.connect() as connection:
            result = connection.execute(query, {"user_id": user_id}).fetchall()

        if result:
            df = pd.DataFrame(result, columns=['user_id', 'task_id', 'user_result_status', 'chatgpt_response'])
            return df
        else:
            return None  # No results found for the user

    except Exception as e:
        print(f"Error fetching user results: {e}")
        return None

def update_user_result(user_id, task_id, status, chatgpt_response, table_name='user_results'):
    """
    Updates user-specific result and ChatGPT response in the user_results table.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                update_query = text(f"""
                    MERGE INTO {table_name} AS target
                    USING (SELECT :user_id AS user_id, :task_id AS task_id, :status AS status, :chatgpt_response AS chatgpt_response) AS source
                    ON target.user_id = source.user_id AND target.task_id = source.task_id
                    WHEN MATCHED THEN
                        UPDATE SET user_result_status = source.status, chatgpt_response = source.chatgpt_response
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, task_id, user_result_status, chatgpt_response) 
                        VALUES (source.user_id, source.task_id, source.status, source.chatgpt_response);
                """)
                connection.execute(update_query, {
                    'user_id': user_id, 
                    'task_id': task_id, 
                    'status': status, 
                    'chatgpt_response': chatgpt_response
                })
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                print(f"Transaction error: {e}")

    except Exception as e:
        print(f"Error updating user result: {e}")

# Function to fetch user information based on username
def fetch_user_from_sql(username):
    """
    Fetch user information based on username.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        query = text("SELECT user_id, username, password, role FROM users WHERE username = :username")
        with engine.connect() as connection:
            result = connection.execute(query, {"username": username}).fetchone()

        if result:
            return dict(result._mapping)
        return None
    
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

# Function to insert a new user with a hashed password
def insert_user_to_sql(username, password, role):
    """
    Inserts a new user with a hashed password into the users table.
    """
    try:
        # Hash the user's password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        insert_user_query = text("""
            INSERT INTO users (user_id, username, password, role)
            VALUES (NEWID(), :username, :password, :role)
        """)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(insert_user_query, {
                    'username': username, 
                    'password': hashed_password, 
                    'role': role
                })
                transaction.commit()
                print(f"User '{username}' added successfully.")
            except SQLAlchemyError as e:
                transaction.rollback()
                print(f"Error inserting user: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

# Function to fetch all users from the database
def fetch_all_users():
    """
    Fetch all users from the database.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("SELECT user_id, username, role FROM users")
        with engine.connect() as connection:
            result = connection.execute(query).fetchall()

        return [row._asdict() for row in result]
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return None

# Function to remove a user from the database
def remove_user(username):
    """
    Remove a user from the database.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("DELETE FROM users WHERE username = :username")
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                result = connection.execute(query, {"username": username})
                transaction.commit()
                return result.rowcount > 0
            except SQLAlchemyError as e:
                transaction.rollback()
                print(f"Error removing user: {e}")
                return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to promote a user to admin role
def promote_to_admin(username):
    """
    Promote a user to admin role.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("UPDATE users SET role = 'admin' WHERE username = :username")
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                result = connection.execute(query, {"username": username})
                transaction.commit()
                return result.rowcount > 0
            except SQLAlchemyError as e:
                transaction.rollback()
                print(f"Error promoting user: {e}")
                return False
    except Exception as e:
        print(f"Error: {e}")
