# tests/test_auth_logic.py
from db.models import User
from auth.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)
from jose import jwt

# --- Password hashing ---


def test_password_hashing_and_verification():
    plain_password = "secure123"
    hashed = get_password_hash(plain_password)
    assert hashed != plain_password
    assert verify_password(plain_password, hashed)
    assert not verify_password("wrongpass", hashed)


# --- Create user ---


def test_create_user(session):
    hashed_pw = get_password_hash("testpass")
    user = User(name="John", email="john@example.com", hashed_password=hashed_pw)
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.email == "john@example.com"


# --- Get user by email ---


def test_get_user_by_email(session):
    hashed_pw = get_password_hash("1234")
    user = User(name="Alice", email="alice@example.com", hashed_password=hashed_pw)
    session.add(user)
    session.commit()

    result = session.query(User).filter(User.email == "alice@example.com").first()
    assert result is not None
    assert result.name == "Alice"


# --- Authenticate user manually ---


def test_authenticate_user_success(session):
    pw = "mypassword"
    user = User(
        name="Bob", email="bob@example.com", hashed_password=get_password_hash(pw)
    )
    session.add(user)
    session.commit()

    found_user = session.query(User).filter(User.email == "bob@example.com").first()
    assert found_user is not None
    assert verify_password(pw, found_user.hashed_password)


def test_authenticate_user_failure_wrong_password(session):
    user = User(
        name="Eve",
        email="eve@example.com",
        hashed_password=get_password_hash("rightpass"),
    )
    session.add(user)
    session.commit()

    found_user = session.query(User).filter(User.email == "eve@example.com").first()
    assert found_user is not None
    assert not verify_password("wrongpass", found_user.hashed_password)


# --- JWT token generation and decoding ---


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "123"}
    token = create_access_token(payload)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "123"
