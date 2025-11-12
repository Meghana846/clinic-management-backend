from sqlalchemy.orm import sessionmaker
from models import Clinic, engine

Session = sessionmaker(bind=engine)

session = Session()

# Inserting data 
# clinic = Clinic(clinic_name = "KIMS Hospitals", address="Gachibowli")
# clinic_3 = Clinic(clinic_name = "AIG Hospitals", address="Gachibowli")
# clinic_4 = Clinic(clinic_name = "Yashodha Hospitals", address="BHEL")
# clinic_5 = Clinic(clinic_name = "Medunited", address="Sun City")

# session.add(clinic)
# session.add_all([clinic_3, clinic_4, clinic_5])

#Reading Data
# clinics = session.query(Clinic).all()

# for clinic in clinics:
#     print(f"Clinic id:{clinic.clinic_id}, clinic name:{clinic.clinic_name}, clinic address:{clinic.address} ")


# clinics_by_id = session.query(Clinic).filter_by(clinic_id=1)
# clinics_by_address = session.query(Clinic).filter_by(address="Gachibowli").all()
# clinics_by_address = session.query(Clinic).filter_by(address="Gachibowli").one()
# clinics_by_address = session.query(Clinic).filter_by(address="Gachibowli").one_or_none()

# print(clinics_by_id)
# print(clinics_by_address)

clinics_by_id = session.query(Clinic).filter_by(clinic_id=1).one_or_none()

print(clinics_by_id)

clinics_by_id.clinic_name = "Meghana Hospitals"
print(clinics_by_id.clinic_name)

#Delete rows
clinics_by_id = session.query(Clinic).filter_by(clinic_id=1).one_or_none()
session.delete(clinics_by_id)


session.commit()
