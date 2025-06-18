import os
from dotenv import load_dotenv
import random
import requests
from sqlalchemy import desc
from collections import defaultdict, Counter
from db.models import GameResult, Move, Beats


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


# Return medium choice
def get_medium_choice(session, session_id: str):
    # Get the last 5 moves played by the player in this session
    recent_games = (
        session.query(GameResult)
        .filter(GameResult.session_id == session_id)
        .order_by(desc(GameResult.played_at))
        .limit(5)
        .all()
    )

    if not recent_games:
        # Fallback to random if there's no history
        return get_random_choice(session)

    # Extract player's move IDs
    player_move_ids = [game.player_move_id for game in recent_games]

    # Count the most frequent player move
    most_common_id, _ = Counter(player_move_ids).most_common(1)[0]

    # Find all moves that beat the most common player move
    counter_moves = (
        session.query(Move)
        .join(Beats, Beats.winner_id == Move.id)
        .filter(Beats.loser_id == most_common_id)
        .all()
    )

    if not counter_moves:
        # Fallback to random if no counters found (edge case)
        return get_random_choice(session)

    return random.choice(counter_moves)


def get_hard_choice(session, session_id: str):
    # Fetch the last 20 moves by the player in this session
    recent_games = (
        session.query(GameResult)
        .filter(GameResult.session_id == session_id)
        .order_by(desc(GameResult.played_at))
        .limit(20)
        .all()
    )

    # We need at least 3 moves to do pattern prediction
    if len(recent_games) < 3:
        return get_medium_choice(session, session_id)

    # Reverse to chronological order
    recent_moves = list(reversed([g.player_move_id for g in recent_games]))

    # Build pattern map: (move1, move2) -> [move3, move3, ...]
    pattern_map = defaultdict(list)
    for i in range(len(recent_moves) - 2):
        key = (recent_moves[i], recent_moves[i + 1])
        next_move = recent_moves[i + 2]
        pattern_map[key].append(next_move)

    # Use last 2 moves as key
    last_two = tuple(recent_moves[-2:])
    possible_next_moves = pattern_map.get(last_two)

    if not possible_next_moves:
        # Fallback to medium AI if no pattern found
        return get_medium_choice(session, session_id)

    # Predict the most likely next move
    predicted_move_id, _ = Counter(possible_next_moves).most_common(1)[0]

    # Find all moves that beat the predicted move
    counter_moves = (
        session.query(Move)
        .join(Beats, Beats.winner_id == Move.id)
        .filter(Beats.loser_id == predicted_move_id)
        .all()
    )

    if not counter_moves:
        return get_medium_choice(session, session_id)

    return random.choice(counter_moves)
