from app import db
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, validates

# declarative base class
Base = declarative_base()

class Employee(db.Model):
    __tablename__ = 'Employee_Database'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    emp_id = Column(String(50))

    def __str__(self):
        return f"Employee: {self.name} (ID: {self.emp_id})"
