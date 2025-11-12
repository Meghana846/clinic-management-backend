from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy.exc import IntegrityError

# Import our files
from database import get_db, engine
from datetime import datetime, timedelta
from models import Base, User, Clinic, Doctor, Patient, PatientConsultation
from schemas import UserResponse, UserBase, UserCreate, UserLogin, ClinicCreate, ClinicResponse, ClinicUpdate, DoctorCreate, DoctorResponse, DoctorUpdate, PatientCreate, PatientResponse, PatientUpdate,PatientConsultationCreate, PatientConsultationUpdate, PatientConsultationResponse
from auth import hash_password, create_access_token, get_current_user, require_admin, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="Hospital Management", version="1.0.0")

@app.post("/clinics/", response_model=ClinicResponse, status_code=status.HTTP_201_CREATED, tags=["Clinics"])
def create_clinic(clinic: ClinicCreate, db: Session = Depends(get_db)):
    """
    Create a new clinic
    """
    try:
     # Step 1: Convert Pydantic model → SQLAlchemy model
        db_clinic = Clinic(**clinic.model_dump())
        
        # clinic.model_dump() returns:
    # {
    #     "clinic_name": "Apollo",
    #     "address": "Hyderabad",
    #     "mobile": "9876543210",
    #     "status": "active"
    # }

    # # ** unpacks it:
    # Clinic(
    #     clinic_name="Apollo",
    #     address="Hyderabad",
    #     mobile="9876543210",
    #     status="active"
    # )
        
        # Step 2: Add to database
        db.add(db_clinic)
        
        # Step 3: Save changes
        db.commit()
        
        # Step 4: Refresh to get generated values (id, created_at)
        db.refresh(db_clinic)
        
        # Step 5: Return (FastAPI auto-converts to JSON)
        return db_clinic
    
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig).lower()
        if "mobile" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists. Please use a different number."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/clinics/", response_model=List[ClinicResponse], tags=["Clinics"])
def get_clinics(
    skip: int = 0,
    limit: int = 10,
    mobile: str | None = None,
    db: Session = Depends(get_db)):
    """
    GET all clinics with pagination and filtering
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 10)
    - **mobile**: Filter by mobile (optional)
    """
    
    query = db.query(Clinic)  # SELECT * FROM clinics
    
    if mobile:
        query = query.filter(Clinic.mobile.contains(mobile))
        
    # Apply pagination
    clinics = query.offset(skip).limit(limit).all()
    
    return clinics

@app.get("/clinics/{clinic_id}", response_model=ClinicResponse, tags=["Clinics"])
def get_clinic(clinic_id : int,db: Session = Depends(get_db)):
    """
    GET a specific clinic by ID
    """
    
    # Query database
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()  # SELECT * FROM clinics
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    return clinic

@app.put("/clinics/{clinic_id}", response_model=ClinicResponse, tags=["Clinics"])
def update_clinic(
    clinic_id : int, 
    clinic_update: ClinicUpdate,
    db: Session = Depends(get_db)):
    """ 
    Update a clinic (partial update supported)
    
    You can update any combination of fields:
    - Only mobile
    - Only name and address
    - All fields
    - etc.
    """
     # Step 1: Find the clinic
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    
    # Step 2: Check if exists
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
        
    try:
            
        # Step 3: Get only fields user wants to update
        update_data = clinic_update.model_dump(exclude_unset=True)
        
        # Step 4: Update each field dynamically
        for key, value in update_data.items():
            setattr(clinic, key, value)
        
        # Dynamic Update with setattr()
        """
        Step 4: Dynamic Update with setattr()
        pythonfor key, value in update_data.items():
        setattr(clinic, key, value)
        What's setattr()?
        It's like doing clinic.mobile = "9999999999" but dynamically!
        Manual way (tedious):
        pythonif "mobile" in update_data:
        clinic.mobile = update_data["mobile"]
        if "status" in update_data:
        clinic.status = update_data["status"]
        if "clinic_name" in update_data:
        clinic.clinic_name = update_data["clinic_name"]
        # ... repeat for every field! 😩
        Dynamic way (smart):
        pythonfor key, value in update_data.items():
        setattr(clinic, key, value)
        # Works for ANY fields! 🎉
        How setattr() works:
        python# These are equivalent:
        clinic.mobile = "9999999999"
        setattr(clinic, "mobile", "9999999999")

        # Usage:
        field_name = "mobile"
        setattr(clinic, field_name, "9999999999")

        """
        
        # Step 5: Save changes
        db.commit()
        
        # Step 6: Refresh and return
        db.refresh(clinic)
        return clinic
    
    except IntegrityError as e:
        db.rollback()
        error_message = str(e.orig).lower()
        if "mobile" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists. Please use a different number."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.delete("/clinics/{clinic_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Clinics"])
def delete_clinic(
    clinic_id : int, 
    db: Session = Depends(get_db)):
    """ 
    Delete a clinic by ID
    
    Returns 204 No Content on success
    Returns 404 if clinic not found
    """
     # Step 1: Find the clinic
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    
    # Step 2: Check if exists
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
        
    doctor_count = db.query(Doctor).filter(Doctor.clinic_id == clinic_id).count()
    if doctor_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete clinic. It has {doctor_count} doctor(s). Delete them first."

        )
        
    patient_count = db.query(Patient).filter(Patient.clinic_id == clinic_id).count()
    if patient_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete clinic. It has {patient_count} patient(s). Delete them first."
        )

    try:   
        db.delete(clinic)
        db.commit()
        return

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete clinic due to existing related records"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/doctors/{clinic_id}", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED, tags=["Doctors"])
def create_doctor( clinic_id : int, doctor: DoctorCreate, db: Session = Depends(get_db)):
    """
    Create a new doctor
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    try:
        # Step 1: Convert Pydantic model → SQLAlchemy model
        db_doctor = Doctor(**doctor.model_dump())
        db_doctor.clinic_id = clinic_id
        
        # Step 2: Add to database
        db.add(db_doctor)
        
        # Step 3: Save changes
        db.commit()
        
        # Step 4: Refresh to get generated values (id, created_at)
        db.refresh(db_doctor)
        
        # Step 5: Return (FastAPI auto-converts to JSON)
        return db_doctor

    except IntegrityError as e:
        db.rollback()  # Rollback the failed transaction

                # Check what constraint was violated

        error_message = str(e.orig) # Get original database error
        
        
        if "mobile" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists. Please use a different number."
            )
        elif "email" in error_message.lower():
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="Email already exists. Please use a different email."
            )
        elif "foreign key" in error_message.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid clinic reference"
                )
        else:
                # Generic integrity error
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Database constraint violation: {error_message}"
                )
                
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    



@app.get("/clinics/{clinic_id}/doctors", response_model=List[DoctorResponse], tags=["Doctors"])
def get_doctors_by_clinic( clinic_id : int, db: Session = Depends(get_db)):
    """
Get all doctors for a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    doctors = db.query(Doctor).filter(Doctor.clinic_id == clinic_id).all()

    if not doctors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No doctors found for clinic with id {clinic_id}"
            )

    return doctors


@app.get("/clinics/{clinic_id}/doctors/{doctor_id}/", response_model=DoctorResponse, tags=["Doctors"])
def get_doctor_by_id( clinic_id : int, doctor_id : int,db: Session = Depends(get_db)):
    """
    Get a specific doctor from a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
        
    doctor = db.query(Doctor).filter(
        Doctor.clinic_id == clinic_id, 
        Doctor.doctor_id == doctor_id).first()

    if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No doctors found for clinic with id {clinic_id}"
            )

    return doctor


@app.put("/clinics/{clinic_id}/doctors/{doctor_id}/", response_model=DoctorResponse, tags=["Doctors"])
def update_doctor( 
    clinic_id : int, 
    doctor_id : int,        
    doctor_update: DoctorUpdate,
    db: Session = Depends(get_db)):
    """
        Update a  specific doctor from a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic id {clinic_id} does not exist"
        )
        
    doctor = db.query(Doctor).filter(
        Doctor.clinic_id == clinic_id, 
        Doctor.doctor_id == doctor_id).first()

    if doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No doctors found for clinic with id {clinic_id}"
            )
            
    try:
        update_data = doctor_update.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(doctor, key, value)
            
        # Step 5: Save changes
        db.commit()
        
        # Step 6: Refresh and return
        db.refresh(doctor)
        return doctor
    
    except IntegrityError as e:
        db.rollback()
        
        error_message = str(e.orig).lower()
        
        if "mobile" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists. Please use a different number."
            )
        elif "email" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists. Please use a different email."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.delete("/clinics/{clinic_id}/doctors/{doctor_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Doctors"])
def delete_doctor(clinic_id: int, doctor_id: int, db: Session = Depends(get_db)):
    """
    Delete a doctor with foreign key protection
    """
    # Verify clinic exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first()
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic id {clinic_id} does not exist"
        )
    
    # Find doctor
    doctor = db.query(Doctor).filter(
        Doctor.clinic_id == clinic_id, 
        Doctor.doctor_id == doctor_id
    ).first()
    
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found"
        )
    
    # Check if doctor has patients
    patient_count = db.query(Patient).filter(Patient.doctor_id == doctor_id).count()
    if patient_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete doctor. They have {patient_count} patient(s). Reassign or delete them first."
        )
    
    # Check if doctor has consultations
    consultation_count = db.query(PatientConsultation).filter(
        PatientConsultation.doctor_id == doctor_id
    ).count()
    if consultation_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete doctor. They have {consultation_count} consultation(s) in history."
        )
    
    try:
        db.delete(doctor)
        db.commit()
        return
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete doctor due to existing related records"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/patients/{clinic_id}", response_model=PatientResponse, status_code=status.HTTP_201_CREATED, tags=["Patients"])
def create_patient( clinic_id : int, patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    #check if  doctor belongs to this clinic
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == patient.doctor_id,
        Doctor.clinic_id == clinic_id, 
    ).first()
    
    if doctor is None:
        raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {patient.doctor_id} not found in this clinic"
        )
        
    try:
        db_patient = Patient(**patient.model_dump())
        db_patient.clinic_id = clinic_id
        
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        return db_patient
    except IntegrityError as e:
        db.rollback()
        
        error_message = str(e.orig).lower()
        
        if "mobile" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number already exists. Please use a different number."
            )
        elif "foreign key" in error_message or "doctor_id" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid doctor reference"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/clinics/{clinic_id}/patients", response_model=List[PatientResponse], tags=["Patients"])
def get_patients_by_clinic( clinic_id : int, db: Session = Depends(get_db)):
    """
    Get all patients for a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    patients = db.query(Patient).filter(Patient.clinic_id == clinic_id).all()

    if not patients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Patients found for clinic with id {clinic_id}"
            )

    return patients


@app.get("/clinics/{clinic_id}/patients/{patient_id}/", response_model=PatientResponse, tags=["Patients"])
def get_patients_by_clinic( clinic_id : int, patient_id: int, db: Session = Depends(get_db)):
    """
    Get a specific patient from a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
    
    patient = db.query(Patient).filter(
        Patient.clinic_id == clinic_id,
        Patient.patient_id == patient_id).first() 

    if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Patients found for clinic with id {clinic_id}"
            )

    return patient


@app.put("/clinics/{clinic_id}/patients/{patient_id}/", response_model=PatientResponse, tags=["Patients"])
def update_patient( 
    clinic_id : int, 
    patient_id : int,        
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)):
    """
        Update a  specific patient from a clinic
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    
    # Check if found
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic id {clinic_id} does not exist"
        )
        
    patient = db.query(Patient).filter(
        Patient.clinic_id == clinic_id, 
        Patient.patient_id == patient_id).first()

    if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No Patients found for clinic with id {clinic_id}"
            )
            
    update_data = patient_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(patient, key, value)
        
    # Step 5: Save changes
    db.commit()
    
    # Step 6: Refresh and return
    db.refresh(patient)
    return patient


@app.delete("/clinics/{clinic_id}/patients/{patient_id}/", status_code=status.HTTP_204_NO_CONTENT, tags=["Patients"])
def delete_patient(
    clinic_id : int, 
    patient_id : int, 
    db: Session = Depends(get_db)):
    """ 
    Delete a Patient by ID

    Returns 204 No Content on success
    Returns 404 if doctor not found
    """
    
     # Query database to check if given clinic_id exists
    patient = db.query(Patient).filter(Patient.clinic_id == clinic_id).first() 
    
    # Check if found
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic id {clinic_id} does not exist"
        )
        
     # Step 1: Find the clinic
    patient = db.query(Patient).filter(
        Patient.clinic_id == clinic_id, 
        Patient.patient_id == patient_id).first()
    
    # Step 2: Check if exists
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {patient} not found"
        )
        
    print(f"Deleting patient {patient_id} from clinic {clinic_id}")
    db.delete(patient)
    db.commit()
    print("Delete successful")

    return


@app.post("/patients_consultation/clinics/{clinic_id}/doctors/{doctor_id}/patients/{patient_id}", 
          response_model=PatientConsultationResponse, 
          status_code=status.HTTP_201_CREATED, 
          tags=["Patients Consultations"])
def create_doctor_patient_consultation( 
    clinic_id : int, 
    doctor_id: int, 
    patient_id: int, 
    consultation: PatientConsultationCreate, 
    db: Session = Depends(get_db)
    ):
    """
    Create a new patient consulation with clinic and doctor
    """
    
    # Query database to check if given clinic_id exists
    clinic = db.query(Clinic).filter(Clinic.clinic_id == clinic_id).first() 
    if clinic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Clinic with id {clinic_id} not found"
        )
        
    # Check if SPECIFIC doctor exists AND belongs to this clinic
    doctor = db.query(Doctor).filter(
        Doctor.doctor_id == doctor_id,
        Doctor.clinic_id == clinic_id).first() 
    # Check if found
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with id {doctor_id} not found"
        )
    
    # Check if SPECIFIC patient exists AND belongs to this clinic
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.clinic_id == clinic_id).first() 
    # Check if found
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {patient_id} not found"
        )
        
    # Check if doctor is active
    if doctor.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doctor is not active. Current status: {doctor.status}"
        )
    
    # Check if patient is active
    if patient.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient is not active. Current status: {patient.status}"
        )
    
    try: 
        # Create consultation
        db_consultation = PatientConsultation(**consultation.model_dump())
        db_consultation.clinic_id = clinic_id
        db_consultation.patient_id = patient_id
        db_consultation.doctor_id = doctor_id
        
        db.add(db_consultation)
        db.commit()
        db.refresh(db_consultation)
        return db_consultation
    
    except IntegrityError as e:
        db.rollback()
        
        error_message = str(e.orig).lower()
        
        if "foreign key" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reference to clinic, doctor, or patient"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user: User registration data (username, email, password, full_name)
        db: Database session
        
    Returns:
        Created user information (without password)
    """
    
    print(f"📝 Attempting to register user: {user.username}")  # Debug log
    
    existing_user = db.query(User).filter(User.username == user.username).first()
    
    # Step 1: Check if username already exists
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
        
    # Step 2: Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        print(f"🔐 Hashing password for {user.username}")  # Debug log
        
        # Step 3: Hash the password
        hashed_pwd = hash_password(user.password)
        
        print(f"✅ Password hashed successfully")  # Debug log
        print(f"📦 Creating user object")  # Debug log
        
        user_data = user.model_dump(exclude={'password'})  # Exclude plain password!
        
        print(f"User data: {user_data}")  # Debug log

        db_user = User(**user_data, hashed_password=hashed_pwd)
        
        print(f"💾 Adding user to database")  # Debug log
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ User {user.username} registered successfully!")  # Debug log
        
        return db_user
    
    except IntegrityError as e:
        db.rollback()
        print(f"❌ IntegrityError: {str(e)}")  # Debug log
        error_message = str(e.orig).lower()
        
        if "username" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        elif "email" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e.orig)}"
            )
            
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")  # Debug log
        import traceback
        traceback.print_exc()  # Print full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    
    