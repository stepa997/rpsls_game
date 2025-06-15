import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Test db
TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="function")
def session():
    engine = create_engine(TEST_DATABASE_URL, echo=False, future=True)
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()

    # Init db
    from db.models import Move, Beats

    move_names = ["rock", "paper", "scissors", "lizard", "spock"]
    moves = {name: Move(name=name) for name in move_names}
    db.add_all(moves.values())
    db.commit()

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
    db.add_all(beats_entries)
    db.commit()

    yield db
    db.close()
