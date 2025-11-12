from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    full_name: str | None = None
    
class UserCreate(UserBase):
    password: str
    
class UserResponse(UserBase):
    user_id: int
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class UserLogin(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class ClinicBase(BaseModel):
    clinic_name: str
    address: str
    mobile: str
    status : str = 'active'
    
class ClinicCreate(ClinicBase):
    pass

class ClinicUpdate(BaseModel):
    clinic_name: str | None = None
    address: str | None = None
    mobile: str | None = None
    status: str | None = None
    
class ClinicResponse(ClinicBase):
    clinic_id: int
    mobile: str | None = None
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True
        
class DoctorBase(BaseModel):
    doctor_name : str
    mobile : str
    email : str
    address : str
    specialization : str
    status : str = 'active'
    # clinic_id : int
    
class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    doctor_name: str | None = None
    mobile: str | None = None
    email: str | None = None
    address: str | None = None
    specialization: str | None = None
    # Corrected line
    status: str | None = None
    # clinic_id: int | None = None 

class DoctorResponse(DoctorBase):
    doctor_id: int
    clinic_id: int
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    patient_name : str
    mobile : str
    age : int
    gender : str
    status : str = 'active'
    doctor_id: int  
    doctor_name: str

    
class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    patient_name: str | None = None
    mobile: str | None = None
    age: int | None = None
    gender: str | None = None
    status: str | None = None
    doctor_id: int  | None = None 
    doctor_name: str | None = None 


class PatientResponse(PatientBase):
    patient_id: int
    clinic_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True

class PatientConsultationBase(BaseModel):
    is_primary : bool
    consultation_date : datetime
    status: str = 'active'

    
class PatientConsultationCreate(PatientConsultationBase):
    pass

class PatientConsultationUpdate(BaseModel):
    patient_name: str | None = None
    mobile: str | None = None
    age: int | None = None
    gender: str | None = None
    status: str | None = None

class PatientConsultationResponse(PatientConsultationBase):
    patient_id: int
    consultation_id: int
    clinic_id: int
    doctor_id: int
    created_at: datetime
    updated_at: datetime | None
    
    class Config:
        from_attributes = True