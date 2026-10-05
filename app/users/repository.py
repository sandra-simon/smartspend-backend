from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.model import User


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = select(User).where(
        User.user_id == user_id
    )

    return db.scalar(statement)

def update_user(
    db: Session,
    user: User,
    username: str | None = None,
    theme: str | None = None,
) -> User:
    if username is not None:
        user.username = username

    if theme is not None:
        user.theme = theme

    db.commit()
    db.refresh(user)

    return user