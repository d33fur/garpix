from pydantic import BaseModel

class StandartBase(BaseModel):
    standart_name: str

    class Config:
        from_attributes = True
