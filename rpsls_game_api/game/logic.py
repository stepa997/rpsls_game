from datetime import datetime, timedelta
from sqlalchemy import func, and_
from ai.commentator import generate_comment
from db.get_db import get_redis_from_env
from db.models import Move, GameResult, User
from game.level_choice import get_random_choice, get_medium_choice, get_hard_choice


def play_game_by_id(
    session,
    player_id: int,
    session_id: str,
    difficulty: str = "easy",
    challenge_mode: bool = False,
):
    player_move = session.get(Move, player_id)
    if not player_move:
        return {"error": "Invalid choice ID!"}

    # Get computer move
    if difficulty == "hard":
        computer_move_obj = get_hard_choice(session, session_id)
    elif difficulty == "medium":
        computer_move_obj = get_medium_choice(session, session_id)
    else:
        computer_move_obj = get_random_choice(session)

    computer_move_id = (
        computer_move_obj["id"]
        if isinstance(computer_move_obj, dict)
        else computer_move_obj.id
    )

    beats_ids = [b.loser_id for b in player_move.wins_against]

    # Determine result
    if computer_move_id == player_move.id:
        result = "draw"
    elif computer_move_id in beats_ids:
        result = "win"
    else:
        result = "lose"

    # Insert result in DB
    game_result = GameResult(
        played_at=datetime.utcnow(),
        player_move_id=player_move.id,
        computer_move_id=computer_move_id,
        result=result,
        session_id=session_id,
    )
    session.add(game_result)
    session.commit()

    ai_comment = generate_comment(
        player_move, session.get(Move, computer_move_id), result
    )

    # --- CHALLENGE MODE LOGIC ---
    if challenge_mode:
        level_list = ["easy", "medium", "hard"]
        redis_db = get_redis_from_env()
        challenge = redis_db.hgetall(session_id)
        if not challenge:
            redis_db.hset(
                session_id, mapping={"level": "easy", "round": 1, "wins": 0, "games": 0}
            )
            challenge = redis_db.hgetall(session_id)

        round_wins = int(challenge["wins"])
        round_games = int(challenge["games"])

        # Update only if in challenge mode
        if difficulty in level_list:
            round_games += 1
            if result == "win":
                round_wins += 1

            redis_db.hset(
                session_id, mapping={"wins": round_wins, "games": round_games}
            )

            # End of round (10 games)
            if round_games >= 10:
                if round_wins >= 5:
                    next_round = int(challenge["round"]) + 1
                    if next_round > 3:
                        redis_db.delete(session_id)  # Completed all rounds
                    else:

                        redis_db.hset(
                            session_id,
                            mapping={
                                "level": level_list[next_round - 1],
                                "round": next_round,
                                "wins": 0,
                                "games": 0,
                            },
                        )
                else:
                    # Fail - restart challenge
                    redis_db.hset(
                        session_id,
                        mapping={
                            "level": level_list[0],
                            "round": 1,
                            "wins": 0,
                            "games": 0,
                        },
                    )

    return {
        "result": result,
        "player": player_move.id,
        "computer": computer_move_id,
        "comment": ai_comment,
    }


def get_challenge_status(session_id: str):
    redis_db = get_redis_from_env()
    return redis_db.hgetall(session_id)


def start_challenge_mode(session_id: str):
    redis_db = get_redis_from_env()
    redis_db.hset(
        session_id,
        mapping={
            "level": "easy",
            "round": 0,
            "wins": 0,
            "games": 0,
        },
    )
    return "Start challenge mode"


def get_last_n_games(session, session_id: str, last_n_numbers=10):
    games = (
        session.query(GameResult)
        .filter(GameResult.session_id == session_id)
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


def get_top_results_today(session, last_n_numbers=10):
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    results = (
        session.query(GameResult.session_id, func.count(GameResult.id).label("wins"))
        .filter(
            and_(
                GameResult.result == "win",
                GameResult.played_at >= today,
                GameResult.played_at < tomorrow,
            )
        )
        .group_by(GameResult.session_id)
        .order_by(func.count(GameResult.id).desc())
        .limit(last_n_numbers)
        .all()
    )

    names = [name for (name,) in session.query(User.name).all()]

    return [
        {
            "session_id": (
                f"Guest {r.session_id[:8]}"
                if r.session_id not in names
                else r.session_id
            ),
            "wins": r.wins,
        }
        for r in results
    ]


def remove_results(session, session_id: str):
    session.query(GameResult).filter(GameResult.session_id == session_id).delete(
        synchronize_session=False
    )
    session.commit()
