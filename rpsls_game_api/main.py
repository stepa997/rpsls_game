import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from db.connection import get_connection
from game.logic import (
    get_choices,
    get_random_choice,
    play_game_by_id,
    get_last_n_games,
    remove_results,
)
from schemas.models import PlayRequest, GameResultsResponse, GameHistoryRequest


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load env file
load_dotenv()

# Get connection credentials
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

get_session = get_connection(db_user, db_password, db_host, db_port, db_name)


@app.get("/")
def root():
    return {"message": "Welcome to Rock, Paper, Scissors, Lizard, Spock game!"}


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
def play_round(payload: PlayRequest):
    with get_session() as session:
        result = play_game_by_id(session, payload.player)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/games/history", response_model=GameResultsResponse)
def top_10_games(payload: GameHistoryRequest):
    last_n_games = payload.number_of_last

    # One more check:
    if last_n_games > 100:
        raise HTTPException(status_code=400, detail="Maximum is 100 games.")

    with get_session() as session:
        results = get_last_n_games(
            session,
            last_n_numbers=last_n_games,
        )
        return {"count": len(results), "data": results}


@app.delete("/results/truncate")
def delete_item():
    with get_session() as session:
        remove_results(session)
        return {"detail": "Game results removed"}
