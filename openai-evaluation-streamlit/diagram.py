from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.aws.storage import S3
from diagrams.azure.database import SQLDatabases

# Define custom logos with your file paths
chatgpt_logo = "/Users/godalla/Desktop/chatgpt.png"
streamlit_logo = "/Users/godalla/Desktop/streamlit-logo-secondary-colormark-darktext.png"
huggingface_logo = "/Users/godalla/Desktop/png-transparent-hugging-face-full-logo-tech-companies.png"
azuresql_logo = "/Users/godalla/Desktop/avid709mg.webp"
vs_code = "/Users/godalla/Desktop/png-clipart-visual-studio-code-logo-thumbnail-tech-companies-thumbnail.png"
with Diagram("OpenAI Evaluation App Flow", show=True):

    # Define Users
    user = User("User")
    admin = User("Admin")

    # Streamlit Application Cluster
    with Cluster("Streamlit Application"):
        streamlit = Custom("Streamlit App", streamlit_logo)
        
        # Login for user and admin
        user_login = streamlit << Edge(label="Log In", color="green") >> user
        admin_login = streamlit << Edge(label="Log In", color="green") >> admin

        # User Dashboard with Explore, Summary, and Logout Options
        with Cluster("User Dashboard"):
            explore_questions = Custom("Explore Questions", streamlit_logo)
            view_summary = Custom("View Summary", streamlit_logo)
            logout = Custom("Log Out", streamlit_logo)

            user >> Edge(label="Explore") >> explore_questions
            user >> Edge(label="View Summary") >> view_summary
            user >> Edge(label="Logout") >> logout

    # Admin Operations for GAIA Dataset and Repo Management
    with Cluster("Admin Operations"):
        huggingface = Custom("Hugging Face", huggingface_logo)
        repo_clone = Custom("VS code", vs_code)
        s3_bucket = S3("Amazon S3")

        admin << Edge(label="Load GAIA Dataset", color="darkred") >> huggingface 
        huggingface >> Edge(label="Clone Files", color="orange") >> repo_clone
        repo_clone << Edge(label="Upload to S3/Preprocess", color="orange") >> s3_bucket

    # GAIA Dataset and ChatGPT Interaction for User Operations
    with Cluster("User Operations"):
        gaia_dataset = Custom("GAIA Dataset", huggingface_logo)
        openai_api = Custom("OpenAI API", chatgpt_logo)
        
        # User interaction flow
        explore_questions >> Edge(label="", color="darkred") >> gaia_dataset
        gaia_dataset >> Edge(label="Choose Question", color="purple") >> openai_api
        
    # Database Operations
    with Cluster("Database"):
        mysql_db = Custom("Azure MySQL Database", azuresql_logo)
        setup_db = streamlit >> Edge(label="", color="blue") >> mysql_db
        
        # Data validation and summary
        openai_api >> Edge(label="Validate Answer", color="blue") >> mysql_db
        view_summary << Edge(label="", color="green") >> mysql_db

    # Final step: View results
    user >> Edge(label="View Results", color="green") >> streamlit
    