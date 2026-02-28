from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

#SQLALCHEMY_DATABASE_URL= f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
SQLALCHEMY_DATABASE_URL = "postgresql://postgres.amzfsjihsdxpcfhuiztp:parvinder%%40123@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require"
engine= create_engine(SQLALCHEMY_DATABASE_URL)

sessionlocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=declarative_base()

def get_db():
    db=sessionlocal()
    try:
        yield db 
    finally:
        db.close()


