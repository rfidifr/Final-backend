from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

#SQLALCHEMY_DATABASE_URL= f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
SQLALCHEMY_DATABASE_URL = "postgresql://rfid_db_l4s2_user:98QOQOEGkcPYR16f5FXESUaJTp4stvo0@dpg-d6hapq3h46gs73e3k7lg-a/rfid_db_l4s2"
engine= create_engine(SQLALCHEMY_DATABASE_URL)

sessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=declarative_base()

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()


