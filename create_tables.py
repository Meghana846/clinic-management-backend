from database import engine, Base
from models import Clinic
from sqlalchemy import inspect

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully!")


inspector = inspect(engine)
print("Tables in database:", inspector.get_table_names())
print("Columns in clinics:", [col['name'] for col in inspector.get_columns('clinics')])