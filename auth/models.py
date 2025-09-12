from pydantic import BaseModel,Field

class TokenRequest(BaseModel):
    token:str = Field(..., min_length=1, description="JWT token to verify")