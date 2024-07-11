import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse, FileResponse
from . import models, schemas
from .database import SessionLocal, engine
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/list", response_model=list[str])
def read_standarts(db: Session = Depends(get_db)):
    standarts = db.query(models.Standart).all()
    return [standart.standart_name for standart in standarts]

@app.post("/check")
async def check_file(standart: str = Header(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    standart = db.query(models.Standart).filter(models.Standart.standart_name == standart).first()
    if not standart:
        raise HTTPException(status_code=404, detail="Standart not found")

    file_location = f"temp/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    return FileResponse(path=file_location, media_type=file.content_type, filename=file.filename)
