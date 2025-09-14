from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from db import users_col

import os
from dotenv import load_dotenv
load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
       
        userinfo = jwt.decode(token,algorithms=ALGORITHM,key=JWT_SECRET)  # your decode logic
       
        useremail = userinfo["sub"]
       
        result = users_col.find_one({"email": useremail})
       
        
        if result is None:
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or user not found"
            )

        
      
        return {"email": useremail, "claims": userinfo}
        
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )