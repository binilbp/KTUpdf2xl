from pydantic import BaseModel

class SchemeCreate(BaseModel):
    name : str

class SchemeOutput(BaseModel):
    id : int
    name : str