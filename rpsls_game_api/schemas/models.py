from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, constr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GuestUser(BaseModel):
    name: Optional[str] = "Guest"


class UserOut(BaseModel):
    id: int
    name: Optional[str]
    email: Optional[EmailStr]

    class Config:
        orm_mode = True


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


class LeaderboardRequest(BaseModel):
    last_n_numbers: int = Field(10, ge=1, le=100)
