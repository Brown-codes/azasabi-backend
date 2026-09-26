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
    new_business = Business(
        name=business_in.name,
        owner_id=current_user.id
    )
    
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    
    return new_business

# --- NEW ROUTE ADDED BELOW ---

@router.get("/", response_model=BusinessResponse)
def get_my_business(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches the business profile belonging to the currently logged-in user.
    """
    business = db.query(Business).filter(Business.owner_id == current_user.id).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="No business found for this user.")
        
    return business