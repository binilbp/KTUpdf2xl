from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.app.db.schema.user_file import UserFileCreate, UserFileOutput
from db.app.core.database import get_db
from db.app.service.userService import UserService
from db.app.db.schema.user import UserOutput
from db.app.util.protectRoute import get_current_user

router = APIRouter(prefix="/userfiles", tags=["user files"])

@router.post("/test", response_model=UserFileOutput) #dont use this in prod
def test_userfile_endpoint(
    file_data: UserFileCreate,
    db: Session = Depends(get_db),
    user: UserOutput = Depends(get_current_user)  # get logged-in user from token
):
    """
    Creates a UserFile entry for the logged-in user.
    """
    service = UserService(session=db)
    return service.add_user_file(user_id=user.id, file_data=file_data)

@router.get("/user/files", response_model=list[UserFileOutput])
def get_user_files(
    db: Session = Depends(get_db),
    user: UserOutput = Depends(get_current_user)
):
    service = UserService(session=db)
    return service.get_user_files_by_user_id(user_id=user.id)
