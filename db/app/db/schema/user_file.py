import datetime
from pydantic import BaseModel
from typing import Optional, Any

class UserFileCreate(BaseModel):
    filename: str
    download_path : str
    json_charts : Optional[Any] = None #Ensures list or dict

class UserFileOutput(BaseModel):
    id : int
    filename : str
    download_path : str
    json_charts : Optional[Any] #might change Optional for Union or the other way
    created_at : str