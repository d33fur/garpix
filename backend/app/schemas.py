from pydantic import BaseModel
from typing import Dict, Any

class StandardConfig(BaseModel):
    standard_name: str
    standard_json: Dict[str, Any]

    class Config:
        orm_mode = True

class StandardName(BaseModel):
    standard_name: str
