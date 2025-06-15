import random
from db.models import Move, GameResult


def test_stress_many_game_results(session):
    moves = session.query(Move).all()

    for _ in range(1000):
        p = random.choice(moves)
        c = random.choice(moves)
        res = "draw" if p.id == c.id else "win"

        game_result = GameResult(
            player_move=p,
            computer_move=c,
            result=res,
        )
        session.add(game_result)

    session.commit()

    count = session.query(GameResult).count()
    assert count >= 1000
