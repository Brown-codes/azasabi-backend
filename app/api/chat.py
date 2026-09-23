# app/api/chat.py
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.business import Business
from app.models.sale import Sale
from app.models.message import Message 
from app.services.ai import process_chat_message

router = APIRouter(prefix="/chat", tags=["AI Chat"])

class ChatRequest(BaseModel):
    business_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    extracted_data: dict | None = None

@router.post("/", response_model=ChatResponse)
def chat_with_azasabi(
    chat_in: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_start = time.time()
    
    business = db.query(Business).filter(
        Business.id == chat_in.business_id,
        Business.owner_id == current_user.id
    ).first()
    
    if not business:
        raise HTTPException(status_code=403, detail="Not authorized for this business.")
        
    db_start = time.time()
    # 1. Fetch the last 10 messages for context
    db_messages = db.query(Message).filter(
        Message.business_id == business.id
    ).order_by(Message.created_at.asc()).limit(10).all()
    
    history = [{"role": m.role, "content": m.content} for m in db_messages]
    
    # 2. Save the new user message to the database immediately
    user_msg = Message(business_id=business.id, role="user", content=chat_in.message)
    db.add(user_msg)
    db.commit() # Save it so it gets a timestamp
    print(f"⏱️ Initial DB Setup Took: {time.time() - db_start:.2f} seconds")
    
    ai_start = time.time()
    try:
        response = process_chat_message(chat_in.message, history)
    except Exception as e:
        # If the error contains "503" or "UNAVAILABLE", handle it gracefully
        if "503" in str(e) or "UNAVAILABLE" in str(e):
            return ChatResponse(
                reply="My servers are a bit overwhelmed right now! Give me just a few seconds and try sending that again.", 
                extracted_data=None
            )
        # For any other unexpected error, return a generic safe message
        print(f"AI Error: {e}")
        return ChatResponse(
            reply="I ran into a small glitch. Could you try again?", 
            extracted_data=None
        )
    print(f"⏱️ Gemini AI Took: {time.time() - ai_start:.2f} seconds")
    
    # --- CRITICAL FIX: Define defaults before checking the AI response ---
    reply_text = "I am not sure how to respond to that."
    extracted = None
    # --------------------------------------------------------------------
    
    # 4. Handle Tool Calls (Sales Logging)
    if response.function_calls:
        tool_call = response.function_calls[0]
        if tool_call.name == "record_sale":
            args = tool_call.args
            
            new_sale = Sale(
                business_id=business.id,
                item_name=args["item_name"],
                quantity=int(args.get("quantity", 1)),
                total_amount=float(args["total_amount"])
            )
            db.add(new_sale)
            
            reply_text = f"Got it! I've recorded the sale of {new_sale.quantity} {new_sale.item_name} for ₦{new_sale.total_amount:,.2f}."
            extracted = args
            
    # 5. Handle Normal Conversation
    elif response.text:
        reply_text = response.text
        
    # 6. Save the AI's reply to the database so it remembers this interaction later
    ai_msg = Message(business_id=business.id, role="model", content=reply_text)
    db.add(ai_msg)
    db.commit()
    
    print(f"⏱️ Total Endpoint Time: {time.time() - total_start:.2f} seconds")
    
    return ChatResponse(reply=reply_text, extracted_data=extracted)