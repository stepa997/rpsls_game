import pytest
from datetime import datetime, timedelta
from db.models import GameResult
from game.logic import get_top_results_today


@pytest.fixture
def populate_game_results(session):
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)

    player_move_id = 1
    computer_move_id = 2

    # Session 1 - 3 wins today
    for _ in range(3):
        session.add(
            GameResult(
                session_id="session1",
                result="win",
                played_at=now,
                player_move_id=player_move_id,
                computer_move_id=computer_move_id,
            )
        )
    # Session 2 - 5 wins today
    for _ in range(5):
        session.add(
            GameResult(
                session_id="session2",
                result="win",
                played_at=now,
                player_move_id=player_move_id,
                computer_move_id=computer_move_id,
            )
        )
    # Session 3 - 1 win today
    session.add(
        GameResult(
            session_id="session3",
            result="win",
            played_at=now,
            player_move_id=player_move_id,
            computer_move_id=computer_move_id,
        )
    )
    # Session 4 - 4 wins yesterday (should be excluded)
    for _ in range(4):
        session.add(
            GameResult(
                session_id="session4",
                result="win",
                played_at=yesterday,
                player_move_id=player_move_id,
                computer_move_id=computer_move_id,
            )
        )
    # Session 5 - 2 loses today (result != "win", should be excluded)
    for _ in range(2):
        session.add(
            GameResult(
                session_id="session5",
                result="lose",
                played_at=now,
                player_move_id=player_move_id,
                computer_move_id=computer_move_id,
            )
        )
    session.commit()
    yield
    # Cleanup not strictly necessary since db is recreated per test


def test_get_top_results_today_returns_correct_order(session, populate_game_results):
    results = get_top_results_today(session, last_n_numbers=10)

    expected = [
        {"session_id": "Guest session2", "wins": 5},
        {"session_id": "Guest session1", "wins": 3},
        {"session_id": "Guest session3", "wins": 1},
    ]

    assert results == expected


def test_get_top_results_today_limits_results(session, populate_game_results):
    results = get_top_results_today(session, last_n_numbers=2)
    assert len(results) == 2
    assert results[0]["wins"] >= results[1]["wins"]


def test_get_top_results_today_no_wins(session):
    results = get_top_results_today(session, last_n_numbers=10)
    assert results == []
