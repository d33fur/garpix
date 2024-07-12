from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine
from .pdf_to_json import ExtractTextInfoFromPDF
from dotenv import load_dotenv
import os

load_dotenv()

CURRENT_PDF_JSON = None
CURRENT_STANDARD_JSON = None
CURRENT_ERRORS_JSON = None

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/list", response_model=list[str])
def read_standards(db: Session = Depends(get_db)):
    standards = db.query(models.Standart).all()
    return [standard.standart_name for standard in standards]

@app.post("/check")
async def check_file(standart: str = Header(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    print(f"Received standard header: {standart}")
    standard = db.query(models.Standart).filter(models.Standart.standart_name == standart).first()
    if not standard:
        raise HTTPException(status_code=400, detail="Standard not found")
    
    print(f"Found standard: {standard.standart_name}")
    
    CURRENT_STANDARD_JSON = standard.standart_json

    file_location = f"docs/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    parser = ExtractTextInfoFromPDF(file_location)
    CURRENT_PDF_JSON = parser.get_json_data()
    
    return CURRENT_PDF_JSON