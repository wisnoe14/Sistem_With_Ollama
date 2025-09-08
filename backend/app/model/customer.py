from sqlalchemy import Column, Integer, String
from app.database.database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)

# Untuk membuat tabel di database (opsional, jalankan sekali saja)
# Base.metadata.create_all(bind=engine)