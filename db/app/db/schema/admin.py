from pydantic import BaseModel, EmailStr


class adminLogin(BaseModel):
    email: EmailStr
    password: str
