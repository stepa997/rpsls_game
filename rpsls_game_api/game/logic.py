import os
from dotenv import load_dotenv
from datetime import datetime
import random
import requests
from db.models import Move, GameResult

# Load env file
load_dotenv()

# Get random url from .env
RANDOM_URL = os.getenv("RANDOM_URL")


def get_choices(session):
    return [
        {"id": m.id, "name": m.name}
        for m in session.query(Move).order_by(Move.id).all()
    ]


def get_random_choice(session):
    # your existing function returning list of dicts like {"id":1,"name":"rock"}
    choices = get_choices(session)
    try:
        response = requests.get(RANDOM_URL, timeout=2)
        response.raise_for_status()
        data = response.json()
        rand_num = data.get("random_number")
        if isinstance(rand_num, int) and 1 <= rand_num <= 100:
            # Map the random number (1-100) to the choices list
            # If choices length != 100, scale accordingly
            idx = (
                (rand_num - 1) * len(choices) // 100
            )  # integer index from 0 to len(choices)-1
            return choices[idx]
    except (requests.RequestException, ValueError, KeyError):
        pass  # fallback on any failure

    # fallback: choose randomly
    return random.choice(choices)


def play_game_by_id(session, player_id: int):
    player_move = session.get(Move, player_id)
    if not player_move:
        return {"error": "Invalid choice ID!"}

    # Choose random computer
    computer_move = get_random_choice(session)

    # ID which player beats
    beats_ids = [b.loser_id for b in player_move.wins_against]

    # Result
    if computer_move["id"] == player_move.id:
        result = "draw"
    elif computer_move["id"] in beats_ids:
        result = "win"
    else:
        result = "lose"

    # Insert result in DB
    game_result = GameResult(
        played_at=datetime.utcnow(),
        player_move_id=player_move.id,
        computer_move_id=computer_move["id"],
        result=result,
    )
    session.add(game_result)
    session.commit()

    return {"result": result, "player": player_move.id, "computer": computer_move["id"]}


def get_last_n_games(session, last_n_numbers=10):
    games = (
        session.query(GameResult)
        .order_by(GameResult.played_at.desc())
        .limit(last_n_numbers)
        .all()
    )

    return [
        {
            "id": game.id,
            "played_at": game.played_at,
            "player_move": game.player_move.name,
            "computer_move": game.computer_move.name,
            "winner": game.result,
        }
        for game in games
    ]


def remove_results(session):
    session.query(GameResult).delete()
    session.commit()
