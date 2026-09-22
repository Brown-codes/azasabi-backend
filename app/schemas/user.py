# app/schemas/user.py
from pydantic import BaseModel
from datetime import datetime

# Schema for incoming data (Registration)
class UserCreate(BaseModel):
    email: str
    password: str

# Schema for outgoing data
# Notice we DO NOT include the password here!
class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # This tells Pydantic to read SQLAlchemy models