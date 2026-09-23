# app/services/ai.py
from google import genai
from google.genai import types
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# 1. Define a standard Python function. 
# The AI reads the docstring and type hints to understand how to use it!
def record_sale(item_name: str, quantity: int, total_amount: float):
    """
    Records a sale of an item.
    
    Args:
        item_name: The name of the item or service sold.
        quantity: The number of items sold. Default to 1.
        total_amount: The total final price paid by the customer.
    """
    pass # We just need the signature, FastAPI handles the actual execution.

def process_chat_message(user_message: str, history: list[dict] = None):
    if history is None:
        history = []
        
    system_instruction = (
        "You are AzaSabi, a friendly AI assistant for a local business vendor in Nigeria. "
        "You help vendors track their daily sales. "
        "If the user tells you about a sale, use the record_sale tool to extract the data. "
        "CRITICAL RULES FOR SALES: "
        "1. Never guess, calculate, or assume the total amount. "
        "2. If a user changes a quantity, DO NOT automatically calculate the new price. "
        "3. If any detail (item, quantity, or total amount) is missing or ambiguous, DO NOT use the tool. Instead, reply in text and ask the user to clarify the missing detail. "
        "If they just say hello, reply naturally and warmly in text. Keep it brief."
    )
    
    # 1. Format the database history for Gemini
    contents = []
    for msg in history:
        contents.append(
            types.Content(role=msg["role"], parts=[types.Part.from_text(text=msg["content"])])
        )
        
    # 2. Add the brand new message from the user
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    )
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=contents, # <-- Pass the entire conversation thread here
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[record_sale],
            temperature=0.3,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
        ),
    )
    
    return response