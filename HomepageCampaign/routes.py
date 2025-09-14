from http.client import HTTPException
from bson import ObjectId
from fastapi import APIRouter, Depends
from db  import campaigns_col
from Campaign.models import ResultModel, serialize_doc
from HomepageCampaign.models import CampaignListResponseModel
from auth.verify_token import verify_token


router = APIRouter(prefix="/homepagecampaign", tags=["HomepageCampaign"])


@router.get("/getcampaigns",response_model =CampaignListResponseModel) 
async def get_campaigns():
    result = campaigns_col.find({}).sort("created_at",1)
    campaigns = list(result)
    
    serialize_docs = [serialize_doc(d) for d in campaigns]
   
    return CampaignListResponseModel(
        success=True,
        count=len(serialize_docs),
        campaigns=serialize_docs
    )


@router.post("/deletecampaign/{campaign_id}")
async def set_campaign(campaign_id: str):
    try:
        result = campaigns_col.delete_one({"_id": ObjectId(campaign_id)})
        if result.deleted_count == 1:
            return  {"status": "success", "detail": "Campaign deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Campaign not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting campaign: {e}")


## reatea  route for chaing the camping status to completed 
@router.post("/updatecampaign/{campaign_id}")
async def complete_campaign(campaign_id: str):
    try:
        result = campaigns_col.update_one(
            {"_id": ObjectId(campaign_id)},
            {"$set": {"status": "Completed"}}
        )
        if result.modified_count == 1:
            return {"status": "success", "detail": "Campaign marked as completed"}
        else:
            raise HTTPException(status_code=404, detail="Campaign not found or already completed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating campaign: {e}")