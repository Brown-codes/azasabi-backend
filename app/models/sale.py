# app/models/sale.py
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Link this sale to a specific business
    business_id = Column(String, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    
    # The flexible data the AI will extract
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    total_amount = Column(Float, nullable=False) # The total price paid
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))