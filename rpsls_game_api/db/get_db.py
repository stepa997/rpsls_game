import os
from dotenv import load_dotenv
from db.connection import get_connection


def get_db_from_env():
    # Load env file
    load_dotenv()

    # Get connection credentials
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    get_session = get_connection(db_user, db_password, db_host, db_port, db_name)

    return get_session
