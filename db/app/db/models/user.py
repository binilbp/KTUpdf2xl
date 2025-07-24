from app.core.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    email = Column(String(70), unique=True)
    institution = Column(String(50))
    designation = Column(String(50))
    password = Column(String(250))
