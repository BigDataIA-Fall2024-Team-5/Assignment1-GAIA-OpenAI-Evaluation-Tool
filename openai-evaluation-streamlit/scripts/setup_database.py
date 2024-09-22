import os
import bcrypt  # To hash the passwords
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from api_utils.azure_sql_utils import get_sqlalchemy_connection_string

# Load environment variables from .env file
load_dotenv()

# SQL queries to drop and create tables
drop_user_results_table = "IF OBJECT_ID('user_results', 'U') IS NOT NULL DROP TABLE user_results;"
drop_users_table = "IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;"

create_users_table = """
CREATE TABLE users (
    user_id NVARCHAR(50) PRIMARY KEY,
    username NVARCHAR(100) UNIQUE,
    password NVARCHAR(255),
    role NVARCHAR(20) NOT NULL
);
"""

create_user_results_table = """
CREATE TABLE user_results (
    result_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id NVARCHAR(50),
    task_id NVARCHAR(50),
    user_result_status NVARCHAR(50),
    chatgpt_response NVARCHAR(MAX),  -- Column to store ChatGPT response
    created_date DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

# Default user and admin credentials
default_users = [
    {"username": "admin", "password": "admin", "role": "admin"},
    {"username": "user", "password": "user", "role": "user"}
]

def setup_database():
    connection_string = get_sqlalchemy_connection_string()
    engine = create_engine(connection_string)

    with engine.connect() as connection:
        # Start a transaction to drop tables
        transaction = connection.begin()
        try:
            # Drop existing tables in the correct order
            print("Dropping existing tables if they exist...")
            connection.execute(text(drop_user_results_table))  # Drop dependent table first
            connection.execute(text(drop_users_table))  # Then drop the referenced table

            # Commit the transaction after dropping tables
            transaction.commit()
            print("Tables dropped successfully.")
        except Exception as e:
            # Rollback the transaction in case of error
            transaction.rollback()
            print(f"An error occurred while dropping tables: {e}")
            return  # Exit if there's an error

        # Start a new transaction to create tables and insert users
        transaction = connection.begin()
        try:
            # Create new tables
            print("Creating users table...")
            connection.execute(text(create_users_table))

            print("Creating user_results table...")
            connection.execute(text(create_user_results_table))

            # Insert default users
            print("Inserting default users...")
            for user in default_users:
                # Hash the password
                hashed_password = bcrypt.hashpw(user["password"].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # SQL query to insert a new user
                insert_user_query = text(f"""
                INSERT INTO users (user_id, username, password, role)
                VALUES (NEWID(), :username, :password, :role)
                """)
                
                # Execute the query with user data
                connection.execute(insert_user_query, {
                    "username": user["username"],
                    "password": hashed_password,
                    "role": user["role"]
                })

            # Commit the transaction after creating tables and inserting users
            transaction.commit()
            print("Database setup completed successfully, and default users have been added.")

        except Exception as e:
            # Rollback the transaction in case of error
            transaction.rollback()
            print(f"An error occurred while creating tables or inserting users: {e}")

if __name__ == "__main__":
    setup_database()
