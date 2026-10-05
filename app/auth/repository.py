from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.model import User


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = select(User).where(User.email == email)

    return db.scalar(statement)


def create_user(
    db: Session,
    username: str,
    email: str,
    password_hash: str,
) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    return db.get(User, user_id)


def get_user_by_reset_token_hash(
    db: Session,
    reset_token_hash: str,
) -> User | None:
    statement = (
        select(User)
        .where(User.reset_token_hash == reset_token_hash)
    )

    return db.scalar(statement)