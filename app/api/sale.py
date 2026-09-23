# app/api/sale.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.business import Business
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleResponse
from app.services.pdf import generate_sales_pdf

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

@router.get("/export/{business_id}")
def export_sales_pdf(
    business_id: str,
    start_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DD"),
    end_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    business = db.query(Business).filter(
        Business.id == business_id, Business.owner_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Not authorized for this business.")
        
    # Base query
    query = db.query(Sale).filter(Sale.business_id == business.id)
    period_label = "All Time"
    
    # Apply date filters
    if start_date:
        query = query.filter(Sale.created_at >= start_date)
        period_label = f"From {start_date.strftime('%Y-%m-%d')}"
    if end_date:
        query = query.filter(Sale.created_at <= end_date)
        if start_date:
            period_label += f" to {end_date.strftime('%Y-%m-%d')}"
        else:
            period_label = f"Up to {end_date.strftime('%Y-%m-%d')}"
            
    sales = query.order_by(Sale.created_at.desc()).all()
    
    if not sales:
        raise HTTPException(status_code=404, detail="No sales found for this period.")
        
    # Generate the file
    pdf_bytes = generate_sales_pdf(business, sales, period_label)
    
    filename = f"{business.name.replace(' ', '_')}_Sales.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)