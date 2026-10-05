from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token


bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
) -> int:
    return decode_access_token(
        credentials.credentials
    )


def get_optional_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(HTTPBearer(auto_error=False)),
    ],
) -> int | None:

    if credentials is None:
        return None

    return decode_access_token(
        credentials.credentials
    )