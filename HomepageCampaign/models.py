import bson
from pydantic import BaseModel, Field

class Campaign(BaseModel):
    id: bson.ObjectId = Field(default_factory=bson.ObjectId, alias="_id")

    class Config:
        arbitrary_types_allowed = True  # ✅ Allow arbitrary types like bson.ObjectId

## createa  response model for retriving all the capagins  form the database it should be easy for me to pasrse
class CampaignResponseModel(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    pipeline: list[dict]
    created_at: str | None = None
    customers: list
    status: str

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            bson.ObjectId: str
        }

class CampaignListResponseModel(BaseModel):
    success: bool = True
    count: int
    campaigns: list[CampaignResponseModel]