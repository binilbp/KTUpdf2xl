from db.app.db.schema.user_file import UserFileOutput
from .base import BaseRepository
from db.app.db.models.user import User, UserFile
from db.app.db.schema.user import UserInCreate

class UserRepository(BaseRepository):
    def create_user(self, user_data: UserInCreate):
        newUser = User(**user_data.model_dump(exclude_none=True))

        self.session.add(instance=newUser)
        self.session.commit()
        self.session.refresh(instance=newUser)

        return newUser
    def user_exist_by_email(self, email : str) -> bool:
        user = self.session.query(User).filter_by(email=email).first()
        return bool(user)
    def get_user_by_email(self, email : str) -> User:
        user = self.session.query(User).filter_by(email=email).first()
        return user
    def get_user_by_id(self, user_id : int):
        user = self.session.query(User).filter_by(id=user_id).first()
        return user
    
    #adding file info to tables , need validation file_data: UserFileCreate) -> UserFile:
    def create_user_file(self, user_id: int, file_data):
        new_file = UserFile(
            user_id = user_id,
            filename = file_data.filename,
            download_path = file_data.download_path,
            json_charts = file_data.json_charts
        )
        self.session.add(new_file)
        self.session.commit()
        self.session.refresh(new_file)

        return UserFileOutput(
        id=new_file.id,
        filename=new_file.filename,
        download_path=new_file.download_path,
        json_charts=new_file.json_charts,
        created_at=new_file.created_at.isoformat()  # convert to string , no need for conversion but the responce is not validating correctly
    )