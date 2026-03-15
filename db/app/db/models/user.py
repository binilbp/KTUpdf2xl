from db.app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_name = Column(String(50))
    email = Column(String(70), unique=True)
    institution = Column(String(50))
    designation = Column(String(50))
    password = Column(String(250))

    #admin/user role 
    role = Column(String(20), default="user")

    #this makes links between tables somehow
    files = relationship("UserFile", back_populates="user", cascade="all, delete")

class UserFile(Base):
    __tablename__ = "user_files"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    download_path = Column(String(255), nullable=False)
    json_charts = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    #idk wht this does but seems important
    user = relationship("User", back_populates="files")

#patterns table foriegn key to schemes for scalability
class RegexPattern(Base):
    __tablename__ = "regex_patterns"
    id = Column(Integer, primary_key=True)
    scheme_id = Column(
        Integer,
        ForeignKey("schemes.id",ondelete="CASCADE"),
        nullable=False
    )
    name = Column(String(100), nullable=False)
    pattern = Column(Text, nullable=False)
    scheme = relationship("Scheme", back_populates="regex_patterns")

    __table_args__ = (
        UniqueConstraint("scheme_id","name"),
    )

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    regex_patterns = relationship(
        "RegexPattern",
        back_populates="scheme",
        cascade="all, delete"
    )