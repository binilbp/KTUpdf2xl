#validation checks

from pydantic import EmailStr, BaseModel
from typing import Union


class UserInCreate(BaseModel):
    user_name: str
    institution: str
    designation: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: int
    user_name: str
    institution: str
    designation: str
    email: EmailStr


class UserInUpdate(BaseModel):
    id: int
    user_name: Union[str, None] = None
    institution: Union[str, None] = None
    designation: Union[str, None] = None
    email: Union[EmailStr, None] = None
    password: Union[str, None] = None

class UserInLogin(BaseModel):
    email: EmailStr
    password: str

class UserWithToken(BaseModel):
    token: str