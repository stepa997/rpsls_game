# init_db.py

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from db.models import Base, Move, Beats

# Load env file
load_dotenv()

# Get DB connection string
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(DATABASE_URL, echo=True)

# Create tables if they don't exist
Base.metadata.create_all(engine)

with Session(engine) as session:
    # Check if data already exists
    move_count = session.scalar(select(func.count()).select_from(Move))
    if move_count and move_count > 0:
        print("Database already initialized. Skipping.")
    else:
        print("Initializing database...")
        move_names = ["rock", "paper", "scissors", "lizard", "spock"]
        moves = {name: Move(name=name) for name in move_names}
        session.add_all(moves.values())
        session.commit()

        beats_pairs = [
            ("rock", "scissors"),
            ("rock", "lizard"),
            ("paper", "rock"),
            ("paper", "spock"),
            ("scissors", "paper"),
            ("scissors", "lizard"),
            ("lizard", "spock"),
            ("lizard", "paper"),
            ("spock", "scissors"),
            ("spock", "rock"),
        ]
        beats_entries = [
            Beats(winner_id=moves[w].id, loser_id=moves[l].id) for w, l in beats_pairs
        ]
        session.add_all(beats_entries)
        session.commit()
        print("Database initialized.")
