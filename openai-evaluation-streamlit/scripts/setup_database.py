import os
import bcrypt  # To hash the passwords
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Modify the connection string to use pymssql
connection_string = f"mssql+pymssql://{os.getenv('AZURE_SQL_USER')}:{os.getenv('AZURE_SQL_PASSWORD')}@{os.getenv('AZURE_SQL_SERVER')}/{os.getenv('AZURE_SQL_DATABASE')}"

# Initialize SQLAlchemy engine with pymssql
engine = create_engine(connection_string)

# SQL queries to drop and create tables
drop_users_table = "IF OBJECT_ID('users', 'U') IS NOT NULL DROP TABLE users;"
drop_user_results_table = "IF OBJECT_ID('user_results', 'U') IS NOT NULL DROP TABLE user_results;"

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
    question NVARCHAR(MAX),
    result_status NVARCHAR(50),
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
    with engine.connect() as connection:
        # Drop the tables if they exist
        print("Dropping existing tables if they exist...")
        connection.execute(text(drop_users_table))
        connection.execute(text(drop_user_results_table))
        
        # Create the tables
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

        print("Database setup completed successfully, and default users have been added.")

if __name__ == "__main__":
    setup_database()
