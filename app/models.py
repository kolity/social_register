
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Date, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)


class Household(Base):
    __tablename__ = "households"

    household_id = Column(Integer, primary_key=True, index=True)
    household_national_id = Column(String(50), unique=True, index=True)
    registration_date = Column(Date, nullable=False)
    address = Column(Text, nullable=False)
    primary_phone = Column(String(20))
    secondary_phone = Column(String(20))
    dwelling_type = Column(String(50))
    ownership_status = Column(String(50))
    monthly_rent = Column(Numeric(10, 2))
    number_of_rooms = Column(Integer)
    has_electricity = Column(Boolean)
    has_water = Column(Boolean)
    has_sanitation = Column(Boolean)
    total_monthly_income = Column(Numeric(10, 2))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default='active')
    
    # Relationships
    members = relationship("HouseholdMember", back_populates="household")
    registered_by = Column(Integer, ForeignKey('users.user_id'))

class HouseholdMember(Base):
    __tablename__ = "household_members"

    member_id = Column(Integer, primary_key=True, index=True)
    household_id = Column(Integer, ForeignKey('households.household_id'))
    national_id = Column(String(50), unique=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    phone_number = Column(String(20))
    relationship_to_head = Column(String(50))
    marital_status = Column(String(20))
    education_level = Column(String(50))
    employment_status = Column(String(50))
    monthly_income = Column(Numeric(10, 2))
    is_household_head = Column(Boolean, default=False)
    disability_status = Column(String(50))
    
    # Relationship
    household = relationship("Household", back_populates="members")