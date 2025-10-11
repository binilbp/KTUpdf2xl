from db.app.db.repository.userRepo import UserRepository
from db.app.db.schema.user import UserOutput, UserInCreate, UserInLogin, UserWithToken
from db.app.core.security.hashHelper import HashHelper
from db.app.core.security.authHandler import AuthHandler
from sqlalchemy.orm import Session
from fastapi import HTTPException

from db.app.db.schema.user_file import UserFileCreate, UserFileOutput

class UserService:
    def __init__(self, session : Session):
        self.__userRepository = UserRepository(session=session)
        
    def signup(self, user_details : UserInCreate) -> UserOutput:
        if self.__userRepository.user_exist_by_email(email=user_details.email):
            raise HTTPException(status_code=400, detail="Please Login")
        
        hashed_password = HashHelper.get_password_hash(plain_password=user_details.password)
        user_details.password = hashed_password  
        return self.__userRepository.create_user(user_data=user_details)          

    def login(self, login_details : UserInLogin) -> UserWithToken:
        if not self.__userRepository.user_exist_by_email(email=login_details.email):
            raise HTTPException(status_code=400, detail="Please Create an Account")
        
        user = self.__userRepository.get_user_by_email(email=login_details.email)
        if HashHelper.verify_password(plain_plassword=login_details.password, hashed_password=user.password):
            token = AuthHandler.sign_jwt(user_id=user.id)
            if token:
                return UserWithToken(token=token)
            raise HTTPException(status_code=500, detail="Unable to process request")
        raise HTTPException(status_code=400, detail="Please Check your credentials")
    
    def get_user_by_id(self, user_id : int):
        user = self.__userRepository.get_user_by_id(user_id = user_id)
        if user:
            return user
        raise HTTPException(status_code=400, detail="User is not available")

    def add_user_file(self, user_id: int, file_data: UserFileCreate) -> UserFileOutput:
        user = self.__userRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        #create file record
        created_file = self.__userRepository.create_user_file(user_id, file_data=file_data)
        return created_file
    
    def get_user_files_by_user_id(self, user_id: int):
        #fetch all records for a user
        user = self.__userRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User Not Found")
        
        user_files = self.__userRepository.get_user_files_by_user_id(user_id)
        return user_files
