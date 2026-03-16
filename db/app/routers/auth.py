from fastapi import APIRouter, Depends, HTTPException, Response
from db.app.core.database import get_db
from sqlalchemy.orm import Session
from db.app.core.security.authHandler import AuthHandler
from db.app.core.security.hashHelper import HashHelper
from db.app.db.models.user import User
from db.app.db.schema.admin import adminLogin
from db.app.service.userService import UserService
from db.app.db.schema.user import UserInCreate, UserInLogin, UserWithToken, UserOutput
authrouter = APIRouter()

@authrouter.post("/login", status_code=200, response_model=UserWithToken)
def login(loginDetails: UserInLogin, session:Session = Depends(get_db)):
    try:
        return UserService(session=session).login(login_details=loginDetails) 
    except Exception as error:
        print(error)
        raise error

@authrouter.post("/signup", status_code=200, response_model=UserOutput)
def signup(signUpDetails: UserInCreate, session:Session = Depends(get_db)):
    try:
        return UserService(session=session).signup(user_details=signUpDetails)
    except Exception as error:
        print(error)
        raise error

@authrouter.post("/admin/login")
def admin_login(data: adminLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if not HashHelper.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access Required")
    
    token = AuthHandler.sign_jwt(user.id)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return {"status": "Admin logged in"}

    

