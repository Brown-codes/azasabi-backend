# app/schemas/sale.py
from pydantic import BaseModel
from datetime import datetime

class SaleCreate(BaseModel):
    business_id: str
    item_name: str
    quantity: int = 1
    total_amount: float

class SaleResponse(BaseModel):
    id: str
    business_id: str
    item_name: str
    quantity: int
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True