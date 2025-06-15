import pytest
from db.models import GameResult, Move
from datetime import datetime, timedelta
from tests.generate_uuid import generate_session_id


def test_create_game_result(session):
    # Get moves from DB
    player_move = session.query(Move).filter_by(name="rock").first()
    computer_move = session.query(Move).filter_by(name="scissors").first()

    session_id = generate_session_id()

    # Start Game
    game_result = GameResult(
        played_at=datetime.utcnow(),
        player_move_id=player_move.id,
        computer_move_id=computer_move.id,
        result="win",
        session_id=session_id,
    )
    session.add(game_result)
    session.commit()

    # Check is that save
    saved_result = session.query(GameResult).filter_by(id=game_result.id).first()
    assert saved_result is not None
    assert saved_result.result == "win"
    assert saved_result.player_move.name == "rock"
    assert saved_result.computer_move.name == "scissors"
    assert saved_result.session_id == session_id


def test_game_results_ordering(session):
    # Add more games
    now = datetime.utcnow()
    session_id = generate_session_id()

    results = [
        GameResult(
            played_at=now - timedelta(days=2),
            player_move_id=1,
            computer_move_id=2,
            result="win",
            session_id=session_id,
        ),
        GameResult(
            played_at=now - timedelta(days=1),
            player_move_id=2,
            computer_move_id=3,
            result="lose",
            session_id=session_id,
        ),
        GameResult(
            played_at=now,
            player_move_id=3,
            computer_move_id=1,
            result="draw",
            session_id=session_id,
        ),
    ]
    session.add_all(results)
    session.commit()

    # Get the last results
    last_results = (
        session.query(GameResult)
        .filter_by(session_id=session_id)
        .order_by(GameResult.played_at.desc())
        .all()
    )

    assert len(last_results) == 3
    assert (
        last_results[0].played_at
        > last_results[1].played_at
        > last_results[2].played_at
    )


@pytest.mark.parametrize("result_value", ["win", "lose", "draw"])
def test_game_result_valid_result_field(session, result_value):
    session_id = generate_session_id()

    # Create with different valid results
    game_result = GameResult(
        played_at=datetime.utcnow(),
        player_move_id=1,
        computer_move_id=2,
        result=result_value,
        session_id=session_id,
    )
    session.add(game_result)
    session.commit()

    saved = session.query(GameResult).filter_by(id=game_result.id).first()
    assert saved.result == result_value
    assert saved.session_id == session_id
