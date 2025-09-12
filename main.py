from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from auth.routes import router as auth_router
from DataIngestion.routes import router as data_router
from Campaign.routes import router as campaign_router
from dotenv import load_dotenv  
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv() 
app = FastAPI(title="Mini CRM Auth Service")

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SESSION_SECRET_KEY")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Flutter app's URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(data_router)
app.include_router(campaign_router)

@app.get("/health")
async def root():
    return {"message": "Welcome to the Mini CRM Auth Service"}