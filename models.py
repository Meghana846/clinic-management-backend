from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean,  func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Clinic(Base):
    __tablename__ = "clinics"
    
    clinic_id = Column(Integer, primary_key=True, autoincrement=True)
    clinic_name = Column(String(100), nullable=False)
    address = Column(String(255))
    mobile = Column(String(15), nullable=False, index=True, unique=True)
    status = Column(String(20), default='active', index=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 🔗 RELATIONSHIP - Allows easy access to clinic
    doctors = relationship("Doctor", back_populates="clinic")
    patients = relationship("Patient", back_populates="clinic")
    consultations = relationship("PatientConsultation",back_populates="clinic")


    def __repr__(self):
        return f"<Clinic(id={self.clinic_id}, name={self.clinic_name})>"


class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_name =  Column(String(255), nullable=False, index=True )
    mobile = Column(String(15), nullable=False, index=True, unique=True)
    email = Column(String(100), unique=True, index=True)
    address = Column(String(255))
    specialization = Column(String(255))
    status = Column(String(20), default='active', index=True)

    # 🔑 FOREIGN KEY - Links to Clinic
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 🔗 RELATIONSHIP - Allows easy access to clinic
    clinic = relationship("Clinic", back_populates="doctors")
    patients = relationship("Patient", back_populates="doctor" )
    consultations = relationship("PatientConsultation",back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.doctor_id}, name={self.doctor_name})>"


class Patient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_name = Column(String(255), nullable=False, index=True )
    mobile = Column(String(15), nullable=False, index=True, unique=True)
    age = Column(Integer)
    gender = Column(String(100))
    status = Column(String(20), default='active', index=True)

    # 🔑 FOREIGN KEY - Links to Clinic
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable=False)
    doctor_name =  Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 🔗 RELATIONSHIP - Allows easy access to clinic
    clinic = relationship("Clinic", back_populates="patients")
    doctor = relationship("Doctor", back_populates="patients")
    consultations = relationship("PatientConsultation",back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.patient_id}, name={self.patient_name})>"

class PatientConsultation(Base):
    __tablename__ = "patients_consultations"
    
    consultation_id = Column(Integer, primary_key=True, autoincrement=True)
    is_primary =  Column(Boolean,default=False)
    consultation_date  =  Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='active')


    # 🔑 FOREIGN KEY - Links to Clinic
    clinic_id = Column(Integer, ForeignKey('clinics.clinic_id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.doctor_id'), nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # 🔗 RELATIONSHIP'S
    patient = relationship("Patient",back_populates="consultations")
    clinic = relationship("Clinic", back_populates="consultations")
    doctor = relationship("Doctor", back_populates="consultations")

    def __repr__(self):
        return (f"<PatientConsultation(id={self.consultation_id},"
        f"patient_id={self.patient_id}, doctor_id={self.doctor_id}, "
        f"is_primary={self.is_primary}, status={self.status})>")
        
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # Never store plain password!
    full_name = Column(String(100))
    role = Column(String(20), default='user')  # 'user' or 'admin'
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username={self.username}, role={self.role})>"
