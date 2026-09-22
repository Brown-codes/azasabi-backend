# app/schemas/business.py
from pydantic import BaseModel
from datetime import datetime

# Input: All the Flutter app needs to send is the name of the shop
class BusinessCreate(BaseModel):
    name: str

# Output: What we send back after saving it to the database
class BusinessResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True  # Tells Pydantic to read the SQLAlchemy database model