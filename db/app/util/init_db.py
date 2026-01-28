from db.app.core.database import Base, engine
from db.app.db.models import user

def create_tables():
    Base.metadata.create_all(bind=engine)
    