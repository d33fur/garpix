from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from . import models, schemas
from .database import SessionLocal, engine
from .pdf_to_json import ExtractTextInfoFromPDF
from dotenv import load_dotenv
import os
import json
from .rules import JSONValidator

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
    standard = db.query(models.Standart).filter(models.Standart.standart_name == standart).first()
    if not standard:
        raise HTTPException(status_code=400, detail="Standard not found")
    
    
    CURRENT_STANDARD_JSON = standard.standart_json

    file_location = f"docs/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)

    with open(file_location, "wb") as buffer:
        buffer.write(await file.read())

    parser = ExtractTextInfoFromPDF(file_location)
    CURRENT_PDF_JSON = parser.get_json_data()
    with open("template/errors_desc.json", "r") as f:
        CURRENT_ERRORS_JSON = json.load(f)

    validator = JSONValidator(CURRENT_PDF_JSON, CURRENT_STANDARD_JSON, CURRENT_ERRORS_JSON)
    answer = {"errors": validator.all_errors_markdown}

    return JSONResponse(content=answer)

@app.post("/add")
async def add_standard(config: schemas.StandardConfig, db: Session = Depends(get_db)):
    existing_standard = db.query(models.Standart).filter(models.Standart.standart_name == config.standard_name).first()
    if existing_standard:
        existing_standard.standart_json = config.standard_json
        db.commit()
    else:
        new_standard = models.Standart(
            standart_name=config.standard_name,
            standart_json=config.standard_json
        )
        db.add(new_standard)
        db.commit()
    return {"message": "Standard added or updated successfully"}

@app.post("/delete")
async def delete_standard(config: schemas.StandardName, db: Session = Depends(get_db)):
    standard = db.query(models.Standart).filter(models.Standart.standart_name == config.standard_name).first()
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    db.delete(standard)
    db.commit()
    return {"message": "Standard deleted successfully"}

@app.get("/get_all", response_model=list[schemas.StandardConfig])
def get_all_standards(db: Session = Depends(get_db)):
    standards = db.query(models.Standart).all()
    return [schemas.StandardConfig(standard_name=standard.standart_name, standard_json=standard.standart_json) for standard in standards]
