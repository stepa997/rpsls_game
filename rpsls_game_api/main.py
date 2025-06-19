from uuid import uuid4
from fastapi import FastAPI, HTTPException, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from db.get_db import get_db_from_env
from game.level_choice import get_choices
from game.logic import (
    get_random_choice,
    play_game_by_id,
    get_challenge_status,
    start_challenge_mode,
    get_last_n_games,
    get_top_results_today,
    remove_results,
)
from routes import users, admin
from schemas.models import (
    PlayRequest,
    GameResultsResponse,
    GameHistoryRequest,
    LeaderboardRequest,
)


app = FastAPI()
app.include_router(users.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3030"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key="secret123")


get_session = get_db_from_env()


@app.get("/")
def root():
    return {"message": "Welcome to Rock, Paper, Scissors, Lizard, Spock game!"}


@app.get("/start")
def start(request: Request):
    session_id = request.cookies.get("session_id")

    if not session_id:
        session_id = str(uuid4())
        response = JSONResponse({"message": "New session created"})
        response.set_cookie("session_id", session_id, httponly=True)
        return response

    return {"message": "Session already exists"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/choices")
def choices():
    with get_session() as session:
        return get_choices(session)


@app.get("/choice")
def random_choice():
    with get_session() as session:
        return get_random_choice(session)


@app.post("/play")
def play_round(payload: PlayRequest, request: Request):
    name = request.session.get("user", {}).get("name")
    if name:
        session_id = name
    else:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session")

    with get_session() as session:
        result = play_game_by_id(
            session,
            payload.player,
            session_id=session_id,
            difficulty=payload.level,
            challenge_mode=payload.challenge_mode,
        )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/challenge/status")
def play_round(request: Request):
    name = request.session.get("user", {}).get("name")
    if name:
        session_id = name
    else:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session")

    return get_challenge_status(session_id)


@app.post("/challenge/start")
def play_round(request: Request):
    name = request.session.get("user", {}).get("name")
    if name:
        session_id = name
    else:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session")

    return start_challenge_mode(session_id)


@app.post("/games/history", response_model=GameResultsResponse)
def top_10_games(payload: GameHistoryRequest, request: Request):
    name = request.session.get("user", {}).get("name")
    if name:
        session_id = name
    else:
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session")

    last_n_games = payload.number_of_last

    # One more check:
    if last_n_games > 100:
        raise HTTPException(status_code=400, detail="Maximum is 100 games.")

    with get_session() as session:
        results = get_last_n_games(
            session,
            session_id=session_id,
            last_n_numbers=last_n_games,
        )
        return {"count": len(results), "data": results}


@app.post("/leaderboard/today")
def top_players_today(payload: LeaderboardRequest):
    last_n_numbers = payload.last_n_numbers
    with get_session() as session:
        return get_top_results_today(session, last_n_numbers=last_n_numbers)


@app.delete("/results/truncate")
def delete_item(request: Request):
    name = request.session.get("user", {}).get("name")
    if name:
        session_id = name
    else:
        session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="Missing session")

    with get_session() as session:
        remove_results(session=session, session_id=session_id)
        return {"detail": "Game results removed"}
