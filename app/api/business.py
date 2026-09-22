# app/api/business.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessResponse

router = APIRouter(prefix="/businesses", tags=["Businesses"])

@router.post("/", response_model=BusinessResponse)
def create_business(
    business_in: BusinessCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🛡️ The Bouncer at work!
):
    """
    Creates a new business profile. 
    The user must be logged in (provide a valid JWT).
    """
    # 1. Build the database record
    # Notice we don't ask the Flutter app for the owner_id. 
    # We securely extract it from the token via the Bouncer.
    new_business = Business(
        name=business_in.name,
        owner_id=current_user.id
    )
    
    # 2. Save to PostgreSQL
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    
    return new_business