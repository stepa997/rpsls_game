from fastapi import APIRouter, Depends
from sqlalchemy import func
from typing import List
from db.get_db import get_db_from_env
from db.models import User, GameResult, Move
from auth.auth import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

get_session = get_db_from_env()


@router.get("/users", response_model=List[dict], dependencies=[Depends(get_admin_user)])
def list_users():
    with get_session() as session:
        users = session.query(User).all()
        return [
            {"id": u.id, "username": u.name, "email": u.email, "is_admin": u.is_admin}
            for u in users
        ]


@router.get("/stats", dependencies=[Depends(get_admin_user)])
def get_game_stats():
    with get_session() as session:
        total_users = session.query(User).count()
        total_games = session.query(GameResult).count()
        total_wins = (
            session.query(GameResult).filter(GameResult.result == "win").count()
        )
        total_losses = (
            session.query(GameResult).filter(GameResult.result == "loss").count()
        )
        total_draws = (
            session.query(GameResult).filter(GameResult.result == "draw").count()
        )

        return {
            "total_users": total_users,
            "total_games": total_games,
            "wins": total_wins,
            "losses": total_losses,
            "draws": total_draws,
        }


@router.get("/stats/summary", dependencies=[Depends(get_admin_user)])
def summary_stats():
    with get_session() as session:
        total_users = session.query(User).count()
        active_players = session.query(GameResult.session_id).distinct().count()
        total_games = session.query(GameResult).count()

        return {
            "total_users": total_users,
            "active_players": active_players,
            "total_games": total_games,
        }


@router.get("/stats/outcomes", dependencies=[Depends(get_admin_user)])
def outcome_stats():
    with get_session() as session:
        counts = (
            session.query(GameResult.result, func.count().label("count"))
            .group_by(GameResult.result)
            .all()
        )
        return {outcome: count for outcome, count in counts}


@router.get("/stats/per-day", dependencies=[Depends(get_admin_user)])
def games_per_day():
    with get_session() as session:
        results = (
            session.query(func.date(GameResult.played_at), func.count())
            .group_by(func.date(GameResult.played_at))
            .order_by(func.date(GameResult.played_at))
            .all()
        )
        return [{"date": str(date), "games": count} for date, count in results]


@router.get("/stats/popular-moves", dependencies=[Depends(get_admin_user)])
def most_common_moves():
    with get_session() as session:
        results = (
            session.query(Move.name, func.count().label("count"))
            .select_from(GameResult)
            .join(Move, Move.id == GameResult.player_move_id)
            .group_by(Move.name)
            .order_by(func.count().desc())
            .all()
        )
        return [{"move": name, "count": count} for name, count in results]
