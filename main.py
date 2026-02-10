from fastapi import FastAPI,Path,HTTPException,Query
import json 
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional

class Patient(BaseModel):
    id : Annotated[str, Field(...,description='Id of the Patient',examples=['P001','P002'])]
    name : Annotated[str,Field(...,description='Name of the patient')]
    city : Annotated[str,Field(...,description='City where the patient live')]
    age : Annotated[int, Field(...,gt=0,lt=120,description='age of the patient')]
    gender : Annotated[Literal['male','female','others'],Field(...,description='Specify the gender of the patient')]
    height : Annotated[float,Field(...,gt=0,description='Height of the Patients in mtrs')]
    weight : Annotated[float,Field(...,gt=0,description='weight of the Patients in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if(self.bmi<18.5):
            return 'underweight'
        elif(self.bmi<25):
            return 'Normal'
        elif(self.bmi<30):
            return 'Overwieght'
        else:
            return 'Obese'


class PatientUpdate(BaseModel):
    name : Annotated[Optional[str],Field(default=None)]
    city : Annotated[Optional[str],Field(default=None)]
    age : Annotated[Optional[int],Field(default=None,gt=0)]
    gender : Annotated[Optional[Literal['male','Female','others']],Field(default=None)]
    height : Annotated[Optional[float],Field(default=None,gt=0)]
    weight : Annotated[Optional[float],Field(default=None,gt=0)]

        
app = FastAPI()

def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json','w') as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {'message' : 'Patients Record Managing API'}

@app.get("/about")
def about():
    return {"About Us" : "A best way to manage patients record"}

@app.get("/view")
def view():
    data = load_data()

    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id : str = Path(...,description = 'ID of patients in the DB',example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail = 'Patient Not Found')

@app.get("/sort")
def sort_patients(sort_by : str = Query(...,description = 'sort on the basis of height , weight and BMI'), order : str = Query('asc',description='Sort in Ascending and Descending Order')):
    valid_fields = ['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Enter Valid Field from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail='select valid order from [asc,desc]')
    
    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by,0),reverse = sort_order)

    return sorted_data

@app.post('/create')
def create_patient(patient : Patient):
    data = load_data()

    if patient.id in data:
        raise HTTPException(status_code=400,detail='This Patient alraedy exist')
    
    data[patient.id] = patient.model_dump(exclude=['id']) 

    save_data(data)

    return JSONResponse(status_code=201,content={'message':'Patient Created Successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id : str, patient_update : PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient Not Found')
    
    existing_patient_info = data[patient_id]

    updated_patient_info = patient_update.model_dump(exclude_unset = True)

    for key,value in updated_patient_info.items():

        existing_patient_info[key] = value

    existing_patient_info['id'] = patient_id

    patient_pydantic_obj = Patient(**existing_patient_info)

    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'Updated Successfully'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id : str):
    
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail='Patient Not Found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200,content={'message':'Patient Deleted Successfully'})