from pydantic import BaseModel
from typing import List, Optional,Any,Literal

class CampaignModel(BaseModel):
    pipeline:List[dict[str,Any]]

class EmailContentModel(BaseModel):
    users:List[str]
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


class SavedCampaignModel(BaseModel):
    status:Literal["failed","saved"]
    name:str
    campaign_id:Optional[str]

class CampaignModel(BaseModel):
    name: str
    pipeline: List[Any]
    created_at: Optional[str] = None
    customers: List[Any]
    status:Literal["Completed","NotCompleted"]



class ContentMailModel(BaseModel):

    message: str
    email: str
    

class StartCampaignRequest(BaseModel):
    campaign_id: str