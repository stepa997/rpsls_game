from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class PlayRequest(BaseModel):
    player: int


# Pydantic model
class GameResultOut(BaseModel):
    id: int
    played_at: datetime
    player_move: str
    computer_move: str
    winner: str

    class Config:
        orm_mode = True


class GameResultsResponse(BaseModel):
    count: int
    data: List[GameResultOut]


class GameHistoryRequest(BaseModel):
    number_of_last: int = Field(
        ..., ge=1, le=100, description="Number of the last games (1-100)"
    )
