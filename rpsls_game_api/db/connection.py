from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager


_engine = None
_SessionLocal = None


def get_connection(user: str, password: str, host: str, port: str, database: str):
    global _engine, _SessionLocal
    if _engine is None:
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        _engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    @contextmanager
    def get_session():
        session: Session = _SessionLocal()
        try:
            yield session
        finally:
            session.close()

    return get_session
