from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse
from datetime import datetime
from db import users_col
from .oauth import oauth
from .jwt_handler import create_access_token, decode_token
import os
from .models import TokenRequest
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file

router = APIRouter(prefix="/auth", tags=["Auth"])
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:58179")

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    print(f"Using redirect URI: {redirect_uri}")  # Debug print
    return await oauth.google.authorize_redirect(request, redirect_uri)
@router.get("/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print(token)
        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Google login failed")

        # Save user if not exists
        existing = users_col.find_one({"email": user_info["email"]})
        if not existing:
            users_col.insert_one({
                "email": user_info["email"],
                "name": user_info.get("name", ""),
                "created_at": datetime.utcnow()
            })

        # Issue JWT for our app
        jwt_token = create_access_token({"sub": user_info["email"]})

        # Redirect back to frontend with token
        return RedirectResponse(f"{FRONTEND_URL}/?token={jwt_token}")
    
    except Exception as e:
        print(f"OAuth callback error: {e}")
        # Redirect to frontend with error
        return RedirectResponse(f"{FRONTEND_URL}/?error=auth_failed")



@router.get("/verify")
async def verifytoken(req:TokenRequest):
    try:
        userinfo = decode_token(req.token)
        print(userinfo)
        useremail = userinfo["sub"]
        result = users_col.find_one({"email": useremail})
        if result is None:
            return HTTPException(status_code=401, detail="Token is INvalid")
        
        return HTTPException(status_code=200, detail="Token is valid and user exists",headers={"UserEmail": useremail})   
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")