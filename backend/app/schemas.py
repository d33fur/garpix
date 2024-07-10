from pydantic import BaseModel

class StandartBase(BaseModel):
    standart_name: str

    class Config:
        orm_mode = True
