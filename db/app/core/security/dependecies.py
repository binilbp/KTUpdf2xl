from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from db.app.core.database import get_db
from db.app.core.security.authHandler import AuthHandler
from db.app.db.models.user import User

# use this where ever admin verification is needed "protected" for admin
def verify_admin(
        access_token: str = Cookie(None),
        db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not Authenticated")

    payload = AuthHandler.decode_jwt(access_token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin Access required")
    
    return user