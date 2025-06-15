from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Move(Base):
    __tablename__ = "move"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Move(id={self.id}, name='{self.name}')>"


class Beats(Base):
    __tablename__ = "beats"

    winner_id = Column(Integer, ForeignKey("move.id"), primary_key=True)
    loser_id = Column(Integer, ForeignKey("move.id"), primary_key=True)

    winner = relationship("Move", foreign_keys=[winner_id], backref="wins_against")
    loser = relationship("Move", foreign_keys=[loser_id], backref="loses_to")

    def __repr__(self):
        return f"<Beats({self.winner.name} beats {self.loser.name})>"


class GameResult(Base):
    __tablename__ = "game_result"

    id = Column(Integer, primary_key=True)
    played_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    player_move_id = Column(Integer, ForeignKey("move.id"), nullable=False)
    computer_move_id = Column(Integer, ForeignKey("move.id"), nullable=False)
    result = Column(String, nullable=False)
    session_id = Column(String, nullable=False, index=True)

    player_move = relationship("Move", foreign_keys=[player_move_id])
    computer_move = relationship("Move", foreign_keys=[computer_move_id])

    def __repr__(self):
        return (
            f"<GameResult(id={self.id}, played_at={self.played_at}, "
            f"player_move={self.player_move.name}, computer_move={self.computer_move.name})>"
        )
