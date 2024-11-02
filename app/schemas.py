from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    user_id: int
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None



class HouseholdMemberBase(BaseModel):
    national_id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone_number: Optional[str] = None
    relationship_to_head: str
    marital_status: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    is_household_head: bool = False
    disability_status: Optional[str] = None

class HouseholdMemberCreate(HouseholdMemberBase):
    pass

class HouseholdMemberUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    marital_status: Optional[str] = None
    education_level: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    disability_status: Optional[str] = None

class HouseholdBase(BaseModel):
    household_national_id: str
    address: str
    primary_phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    dwelling_type: Optional[str] = None
    ownership_status: Optional[str] = None
    monthly_rent: Optional[Decimal] = None
    number_of_rooms: Optional[int] = None
    has_electricity: Optional[bool] = None
    has_water: Optional[bool] = None
    has_sanitation: Optional[bool] = None

class HouseholdCreate(HouseholdBase):
    members: List[HouseholdMemberCreate]

class HouseholdUpdate(BaseModel):
    address: Optional[str] = None
    primary_phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    dwelling_type: Optional[str] = None
    ownership_status: Optional[str] = None
    monthly_rent: Optional[Decimal] = None
    number_of_rooms: Optional[int] = None
    has_electricity: Optional[bool] = None
    has_water: Optional[bool] = None
    has_sanitation: Optional[bool] = None
    status: Optional[str] = None

class HouseholdMemberInDB(HouseholdMemberBase):
    member_id: int
    household_id: int

    class Config:
        from_attributes = True

class HouseholdInDB(HouseholdBase):
    household_id: int
    registration_date: date
    total_monthly_income: Optional[Decimal]
    status: str
    updated_at: datetime
    members: List[HouseholdMemberInDB]

    class Config:
        from_attributes = True