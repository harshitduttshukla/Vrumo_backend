from fastapi import FastAPI,Path,HTTPException,Query,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional,List
import json
import database_models 
from database import SessionLocal, engine
from sqlalchemy.orm import Session



app = FastAPI()

#create tables
database_models.Base.metadata.create_all(bind=engine)

#Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='ID of the patient',examples=['P001'])]
    name:Annotated[str,Field(...,description='Name of the patient')]
    city:Annotated[str,Field(...,description='City where the patient is living')]
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the patient')]
    gender:Annotated[Literal['male','female','others'],Field(...,description='Gender of the patient')]
    height:Annotated[float,Field(...,gt=0,description='Height of the patient in mtrs')]
    weight:Annotated[float,Field(...,gt=0,description='weight of the patient in kg')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

class PatientResponse(Patient):
    id:str
    @computed_field
    @property
    def bmi (self) -> float:
        return round(self.weight/(self.height **2),2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    class Config:
        from_attributes = True




@app.get("/")
def hello():
    return {'message':'Hello world'}




@app.get('/patients',response_model=List[PatientResponse])
def get_all_patients(db:Session = Depends(get_db)): 
    db_patients = db.query(database_models.Patient).all()

    return db_patients

    


@app.get('/patient/{patient_id}',response_model=PatientResponse)
def view_patient(
    patient_id:str = Path(..., description='ID of the patient in the DB',examples=['P001']),
    db:Session = Depends(get_db)
    ):
    

    db_patient = db.query(database_models.Patient).filter(database_models.Patient.id==patient_id).first()

    if not db_patient:
        raise HTTPException(status_code=404,detail="Patient not found")

    return db_patient


   




@app.post('/create')
def create_patient(patient:Patient,db:Session = Depends(get_db)):
    #check if patient already exists in DB
    existing_patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient.id
    ).first()

    if existing_patient:
        raise HTTPException(
            status_code=400,
            detail="Patient already exists"
        )

    #create database object
    new_patient = database_models.Patient(
        id=patient.id,
        name=patient.name,
        city=patient.city,
        age=patient.age,
        gender=patient.gender,
        height=patient.height,
        weight=patient.weight
    )

    # add to database
    db.add(new_patient)

    #save changes
    db.commit()

    #refresh to get latest data
    db.refresh(new_patient)

    return {
        "message":"Patient created successfully",
        "patient":new_patient
    }

   

    
@app.put('/patients/{patient_id}',response_model=PatientResponse)
def update_patient(
    patient_id:str,
    patient_update:PatientUpdate,
    db:Session = Depends(get_db)
    ):
    
    patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404,detail=f"Patient not found{patient_id}")
    
    update_data = patient_update.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(patient,key,value)

    db.commit()
    db.refresh(patient)


    return patient




@app.delete('/delete/{patient_id}')
def delete_patient(
    patient_id:str,
    db:Session = Depends(get_db)
    ):

    patient = db.query(database_models.Patient).filter(
        database_models.Patient.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404,detail="patient not found")
    
    db.delete(patient)
    db.commit()

    return {
        "message":"Patient deleted successfully"
    }





@app.get('/patients/sort',response_model=List[PatientResponse])
def sort_patients(
    sort_by:str = Query(...,description='Sort on the basic of height,weight or bmi '),
    order:str=Query('asc',description='sort in asc or desc order'),
    db:Session = Depends(get_db)
    ):

    valid_fields = ['height','weight','age']

    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f'Invalid field select from {valid_fields}'
        )
    
    if order not in ['asc','desc']:
        raise HTTPException(
            status_code=400,
            detail='Invalid order select between asc and desc'
            )
    
    column = getattr(database_models.Patient,sort_by)
    if order == "desc":
        column = column.desc()

    patients = db.query(database_models.Patient).order_by(column).all()

    return patients
