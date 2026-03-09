from pydantic import BaseModel,EmailStr,AnyUrl,Field,field_validator,model_validator,computed_field
from typing import List,Dict,Optional,Annotated

class Patient(BaseModel):
    name : Annotated[str,Field(max_length=50,title='Name of the patient',description='Give the name of the patient in less 50 chars', examples=['Nitish','Amit'])]

    email:EmailStr
    linkedin_url:AnyUrl
    age : int
    weight:Annotated[float,Field(gt=0,strict=True)]
    height:int
    married:bool = False
    allergies:Optional[List[str]] = None
    contact_details:Dict[str,str]

    @field_validator('email')
    @classmethod
    def email_validator(cls,value):
        valid_domains = ['hdfc.com','icici.com']
        domain_name = value.split('@')[-1]

        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        
        return value
    
    @field_validator('name',mode='after')
    @classmethod
    def transform_name(cls,value):
        return value.upper()
    
    @field_validator('age',mode='after')
    @classmethod
    def validate_age(cls,value):
        if 0 < value < 100:
            return value
        else:
            raise ValueError('Age should be in between 0 and 100')
        
    @model_validator(mode='after')
    def validate_emergency_contact(cls,model):
        if model.age > 60 and 'emergency' not in model.contact_details:
            raise ValueError('Patients older than 60 must have an emergency contact')
        return model
    
    @computed_field
    @property
    def calculate_bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    

    
    

def insert_patient_data(patient:Patient):
    print(patient.age)
    print(patient.name)
    print(patient.calculate_bmi)

patient_info = {'name':'nitish','email':'harhsit@hdfc.com','linkedin_url':'http://linkedin.com/1322','age':70,'weight':75.2,'married':True,'allergies':['pollen','dust'], 'contact_details':{'email':'abc@gmail.com','phone':'2324232'}}

Patient1 = Patient(**patient_info)

insert_patient_data(Patient1)