from pydantic import BaseModel,EmailStr
from typing import List, Optional,Any,Literal

class CampaignModel(BaseModel):
    pipeline:List[dict[str,Any]]

class EmailContentModel(BaseModel):
    users:List[EmailStr]
    content :List[str]


## RETURN MODEL

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc
class ResultModel(BaseModel):
    success: bool = True
    count: int
    users: List[dict[str, Any]]
    
class CompletionResponseModel(BaseModel):
    status :Literal["success", "error"]
    successCount: int