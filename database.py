from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os # <--- ADD THIS

# Define the folder and file path
DATA_DIR = "/app/data"
DB_FILE = "database.db"
db_path = os.path.join(DATA_DIR, DB_FILE)
db_url = f"sqlite:///{db_path}"

# --- THIS IS THE NEW, IMPORTANT PART ---
# Ensure the directory exists *before* creating the engine
os.makedirs(DATA_DIR, exist_ok=True)
# ----------------------------------------

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit = False, autoflush=False , bind=engine)

Base = declarative_base() # This is what your models will inherit from 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()