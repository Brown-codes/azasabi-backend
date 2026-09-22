from fastapi import FastAPI
from app.api import auth
from app.core.config import settings
from app.api import auth, business, sale

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered sales assistant for local businesses."
)


# INCLUDE THE ROUTER
app.include_router(auth.router)
app.include_router(business.router)
app.include_router(sale.router)

@app.get("/")
def health_check():
    return {
        "status": "online", 
        "project": settings.PROJECT_NAME,
        "message": "Sabi API is running successfully."
    }