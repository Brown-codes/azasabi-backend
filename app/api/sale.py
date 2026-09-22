# app/api/sale.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.business import Business
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleResponse

router = APIRouter(prefix="/sales", tags=["Sales"])

@router.post("/", response_model=SaleResponse)
def record_sale(
    sale_in: SaleCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. AUTHORIZATION: Does this user actually own this business?
    business = db.query(Business).filter(
        Business.id == sale_in.business_id, 
        Business.owner_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have permission to log sales for this business."
        )
        
    # 2. Build the database record
    new_sale = Sale(
        business_id=sale_in.business_id,
        item_name=sale_in.item_name,
        quantity=sale_in.quantity,
        total_amount=sale_in.total_amount
    )
    
    # 3. Save to PostgreSQL
    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    
    return new_sale