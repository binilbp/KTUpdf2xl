from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Union
from db.app.core.security.authHandler import AuthHandler
from db.app.service.userService import UserService
from db.app.core.database import get_db
from db.app.db.schema.user import UserOutput

AUTH_PREFIX = 'Bearer '

def get_current_user(
    session: Session = Depends(get_db),
    authorization: Annotated[Union[str, None], Header()] = None
) -> UserOutput:

    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Authentication Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if not authorization:
        raise auth_exception

    if not authorization.startswith(AUTH_PREFIX):
        raise auth_exception

    token = authorization[len(AUTH_PREFIX):].strip()

    payload = AuthHandler.decode_jwt(token)

    if not payload or not payload.get("user_id"):
        raise auth_exception

    user = UserService(session=session).get_user_by_id(payload["user_id"])

    if not user:
        print("User not found in DB.")
        raise auth_exception

    return UserOutput(
        id=user.id,
        user_name=user.user_name,
        institution=user.institution,
        designation=user.designation,
        email=user.email
    )
