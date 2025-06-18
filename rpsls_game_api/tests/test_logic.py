import pytest
from game.level_choice import get_choices
from game.logic import (
    get_random_choice,
    play_game_by_id,
)
from db.models import Move
from tests.generate_uuid import generate_session_id


def test_get_choices_structure(session):
    choices = get_choices(session)
    assert len(choices) == 5
    for choice in choices:
        assert "id" in choice and isinstance(choice["id"], int)
        assert "name" in choice and isinstance(choice["name"], str)
        assert choice["id"] in [m.id for m in session.query(Move).all()]
        assert choice["name"] in [m.name for m in session.query(Move).all()]


def test_get_random_choice_validity(session):
    choice = get_random_choice(session)
    assert isinstance(choice, dict)
    assert choice["id"] in [m.id for m in session.query(Move).all()]
    assert choice["name"] in [m.name for m in session.query(Move).all()]


@pytest.mark.parametrize("player_id", [1, 2, 3, 4, 5])
def test_play_game_valid_ids(session, player_id):
    session_id = generate_session_id()
    result = play_game_by_id(session, player_id, session_id=session_id)
    assert "result" in result
    assert result["result"] in {"win", "lose", "draw"}
    assert result["player"] == player_id
    assert isinstance(result["computer"], int)


@pytest.mark.parametrize("invalid_id", [-1, 0, 6, 99])
def test_play_game_invalid_ids(session, invalid_id):
    session_id = generate_session_id()
    result = play_game_by_id(session, invalid_id, session_id=session_id)
    assert "error" in result
    assert result["error"] == "Invalid choice ID!"
