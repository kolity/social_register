from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..utils.auth import get_current_user
from datetime import date
from decimal import Decimal

router = APIRouter(prefix="/households", tags=["households"])

@router.post("/", response_model=schemas.HouseholdInDB)
def create_household(
    household: schemas.HouseholdCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "case_worker"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to register households"
        )

    # Check if household national ID already exists
    existing_household = db.query(models.Household).filter(
        models.Household.household_national_id == household.household_national_id
    ).first()
    if existing_household:
        raise HTTPException(
            status_code=400,
            detail="Household with this national ID already exists"
        )

    # Create new household
    db_household = models.Household(
        **household.dict(exclude={'members'}),
        registration_date=date.today(),
        registered_by=current_user.user_id
    )
    db.add(db_household)
    db.flush()  # Get the household_id without committing

    # Add household members
    total_income = Decimal(0)
    for member in household.members:
        db_member = models.HouseholdMember(
            **member.dict(),
            household_id=db_household.household_id
        )
        if member.monthly_income:
            total_income += member.monthly_income
        db.add(db_member)

    # Update total household income
    db_household.total_monthly_income = total_income

    db.commit()
    db.refresh(db_household)
    return db_household

@router.get("/{household_id}", response_model=schemas.HouseholdInDB)
def get_household(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    household = db.query(models.Household).filter(
        models.Household.household_id == household_id
    ).first()
    
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    return household

@router.get("/", response_model=List[schemas.HouseholdInDB])
def list_households(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    households = db.query(models.Household).offset(skip).limit(limit).all()
    return households

@router.put("/{household_id}", response_model=schemas.HouseholdInDB)
def update_household(
    household_id: int,
    household_update: schemas.HouseholdUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "case_worker"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update households"
        )

    db_household = db.query(models.Household).filter(
        models.Household.household_id == household_id
    ).first()
    
    if not db_household:
        raise HTTPException(status_code=404, detail="Household not found")

    # Update household fields
    for key, value in household_update.dict(exclude_unset=True).items():
        setattr(db_household, key, value)

    db.commit()
    db.refresh(db_household)
    return db_household

@router.put("/{household_id}/members/{member_id}", response_model=schemas.HouseholdMemberInDB)
def update_household_member(
    household_id: int,
    member_id: int,
    member_update: schemas.HouseholdMemberUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role not in ["admin", "case_worker"]:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update household members"
        )

    db_member = db.query(models.HouseholdMember).filter(
        models.HouseholdMember.member_id == member_id,
        models.HouseholdMember.household_id == household_id
    ).first()
    
    if not db_member:
        raise HTTPException(status_code=404, detail="Household member not found")

    # Update member fields
    for key, value in member_update.dict(exclude_unset=True).items():
        setattr(db_member, key, value)

    # Recalculate total household income
    household_members = db.query(models.HouseholdMember).filter(
        models.HouseholdMember.household_id == household_id
    ).all()
    
    total_income = sum(
        (member.monthly_income or Decimal(0))
        for member in household_members
    )
    
    db_member.household.total_monthly_income = total_income

    db.commit()
    db.refresh(db_member)
    return db_member


@router.get("/search/", response_model=List[schemas.HouseholdInDB])
def search_households(
    national_id: Optional[str] = None,
    phone: Optional[str] = None,
    member_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Household)

    if national_id:
        query = query.filter(models.Household.household_national_id.ilike(f"%{national_id}%"))
    
    if phone:
        query = query.filter(
            (models.Household.primary_phone.ilike(f"%{phone}%")) |
            (models.Household.secondary_phone.ilike(f"%{phone}%"))
        )
    
    if member_name:
        query = query.join(models.HouseholdMember).filter(
            (models.HouseholdMember.first_name.ilike(f"%{member_name}%")) |
            (models.HouseholdMember.last_name.ilike(f"%{member_name}%"))
        )

    return query.all()