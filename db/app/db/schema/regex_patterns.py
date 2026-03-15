from pydantic import BaseModel
from typing import List

class RegexPatternCreate(BaseModel):
    scheme_id: int
    name: str
    pattern: str


class RegexPatternOutput(BaseModel):
    id: int
    scheme_id: int
    name: str
    pattern: str

class SchemeWithRegex(BaseModel):
    id: int
    name: str
    regex_patterns: List[RegexPatternOutput]