import json
from fastapi import APIRouter, Depends,HTTPException,status
import pika

from auth.verify_token import verify_token
from .models import CampaignModel, ResultModel, serialize_doc,EmailContentModel,CompletionResponseModel
from db import customers_col
import os
router = APIRouter(prefix="/campaign", tags=["Campaign"])
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
from bson import ObjectId



@router.get("/")
async def campaign_home():
    return {"message": "Welcome to the Campaign Service"}

@router.get("/fetchusers",response_model=ResultModel)
async def fetch_users(statergy:CampaignModel,claim:dict=Depends(verify_token)):
    result = customers_col.aggregate(statergy.pipeline)
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


@router.put("/startcampaign", response_model=CompletionResponseModel, status_code=status.HTTP_202_ACCEPTED)
async def start_campaign(mails: EmailContentModel,claim:dict=Depends(verify_token)):
    """
    Publishes email campaign messages to RabbitMQ instead of sending directly.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue="email_queue", durable=True)

        success = 0
        for email, message in zip(mails.users, mails.content):
            payload = {"email": email, "message": message}
            publish_message(channel=channel, queue_name="email_queue", message=payload)
            print(f"Queued email to {email}")
            success += 1

        connection.close()

        return CompletionResponseModel(
            status="success",
            successCount=success
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )

