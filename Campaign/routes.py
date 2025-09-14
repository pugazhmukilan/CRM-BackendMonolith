import json
from fastapi import APIRouter, Depends,HTTPException,status
import pika
from typing import List
from .utils import generatecontentformail
from auth.verify_token import verify_token
from .models import CampaignModel, ResultModel, StartCampaignRequest, serialize_doc,EmailContentModel,CompletionResponseModel,SavedCampaignModel
from db import customers_col,campaigns_col
import os
router = APIRouter(prefix="/campaign", tags=["Campaign"])
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
from bson import ObjectId



@router.get("/")
async def campaign_home():
    return {"message": "Welcome to the Campaign Service"}

@router.post("/fetchusers",response_model=ResultModel)
async def fetch_users(statergy:List[dict],claim:dict=Depends(verify_token)):
    result = customers_col.aggregate(statergy)
    users = list(result)
    serialize_docs = [serialize_doc(d) for d in users]
    return ResultModel(
        success=True,
        count=len(serialize_docs),
        users=serialize_docs
    )

    



def publish_message(channel, queue_name, message):
    """Helper function to publish messages to RabbitMQ."""
    try:
        body = json.dumps(message).encode()
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish message: {e}"
        )


# @router.post("/startcampaign", response_model=CompletionResponseModel, status_code=status.HTTP_202_ACCEPTED)
# def start_campaign(request: StartCampaignRequest,claim:dict=Depends(verify_token)):
#     """
#     Publishes email campaign messages to RabbitMQ instead of sending directly.
#     """
#     try:
#         mailids = campaigns_col.find_one({"_id": ObjectId(request.campaign_id)},{"customers": 1})
#         print(mailids)
#         # mails = await generatecontentformail(mailids)
#         # print("generatedmailids content")
#         connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
#         channel = connection.channel()
#         channel.queue_declare(queue="email_queue", durable=True)

#         success = 0
#         print("starting the queueing operation")
#         # for email, message in zip(mails.users, mails.content):
#         #     payload = {"email": email, "message": message}
#         #     publish_message(channel=channel, queue_name="email_queue", message=payload)
#         #     print(f"Queued email to {email}")
#         #     success += 1
#         try:

#             for mailid in mailids["customers"]:
#                 cust_info = customers_col.find_one({"_id": ObjectId(mailid["_id"])}, {"_id": 0})
#                 if not cust_info:
#                     print(f"Customer with ID {mailid} not found.")
#                     continue

#                 email_body = "here is your discount coupon code: WELCOME10\n\n"
#                 payload = {
#                     "email": cust_info["email"],
#                     "message": email_body
#                 }
#                 publish_message(channel=channel, queue_name="email_queue", message=payload)
#                 print(f"Queued email to {cust_info['email']}")
#                 success += 1

#             connection.close()
#         except Exception as e:
#             print(f"Error during queuing: {e}")

#         return CompletionResponseModel(
#             status="success",
#             successCount=success
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Unexpected error: {e}"
#         )

@router.post("/startcampaign", response_model=CompletionResponseModel, status_code=status.HTTP_202_ACCEPTED)
def start_campaign(request: StartCampaignRequest,claim:dict=Depends(verify_token)):
    """
    Publishes email campaign messages to RabbitMQ instead of sending directly.
    """
    try:
        campaign_data = campaigns_col.find_one({"_id": ObjectId(request.campaign_id)})
        
        # If pipeline was stored as string, parse it back (for future use if needed)
        if 'pipeline' in campaign_data and isinstance(campaign_data['pipeline'], str):
            campaign_data['pipeline'] = json.loads(campaign_data['pipeline'])
        
        mailids = {"customers": campaign_data.get("customers", [])}
        print(mailids)
        
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue="email_queue", durable=True)

        success = 0
        print("starting the queueing operation")
        
        try:
            for mailid in mailids["customers"]:
                cust_info = customers_col.find_one({"_id": ObjectId(mailid["_id"])}, {"_id": 0})
                if not cust_info:
                    print(f"Customer with ID {mailid} not found.")
                    continue

                email_body = "here is your discount coupon code: WELCOME10\n\n"
                payload = {
                    "email": cust_info["email"],
                    "message": email_body
                }
                publish_message(channel=channel, queue_name="email_queue", message=payload)
                print(f"Queued email to {cust_info['email']}")
                success += 1

            connection.close()
        except Exception as e:
            print(f"Error during queuing: {e}")

        return CompletionResponseModel(
            status="success",
            successCount=success
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )




# @router.post("/savecampaign",status_code=status.HTTP_201_CREATED,response_model=SavedCampaignModel)
# async def save_campaign(campaign: CampaignModel,claim:dict=Depends(verify_token)):
#     """Saves a campaign to the database."""
#     try:
#         campaign_dict = campaign.model_dump()
#         result = campaigns_col.insert_one(campaign_dict)
#         if result.inserted_id:
#             return SavedCampaignModel(
#                 status="saved",
#                 name=campaign.name,  # You can modify this to accept a name from the request
#                 campaign_id=str(result.inserted_id)
#             )
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 detail="Failed to save campaign"
#             )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Unexpected error: {e}"
#         )

@router.post("/savecampaign",status_code=status.HTTP_201_CREATED,response_model=SavedCampaignModel)
async def save_campaign(campaign: CampaignModel,claim:dict=Depends(verify_token)):
    """Saves a campaign to the database."""
    try:
        campaign_dict = campaign.model_dump()
        
        # Convert pipeline to string to avoid MongoDB $ key restriction
        if 'pipeline' in campaign_dict and campaign_dict['pipeline']:
            campaign_dict['pipeline'] = json.dumps(campaign_dict['pipeline'])
        
        result = campaigns_col.insert_one(campaign_dict)
        
        if result.inserted_id:
            return SavedCampaignModel(
                status="saved",
                name=campaign.name,
                campaign_id=str(result.inserted_id)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save campaign"
            )
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {type(e).__name__}: {str(e)}"
        )