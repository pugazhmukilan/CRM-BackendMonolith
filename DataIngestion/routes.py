from fastapi import APIRouter, HTTPException,status
from fastapi.params import Depends
from starlette.requests import Request
from starlette.responses import RedirectResponse
from datetime import datetime
from auth.verify_token import verify_token
from db import customers_col
from .models import Customer, CustomerIngestionResponse
import os
import pymongo
import pika, json
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

print(f"Using RabbitMQ URL: {RABBITMQ_URL}")  # Debug print
router = APIRouter(prefix="/data", tags=["Data"])

@router.get("/health")
async def datahealth():
    return {"status":"SUCCESS"}




def publish_message(channel, queue_name, message):
    try:
        # Convert datetime → str
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        body = json.dumps(message, default=default_serializer).encode()
        channel.basic_publish(
            exchange="",
            routing_key="customer_queue",
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to publish message: {e}"
        )

@router.post("/addrecord", response_model=CustomerIngestionResponse, status_code=status.HTTP_201_CREATED)
async def add_customer(customer: Customer,claim:dict=Depends(verify_token)):
    try:
        print(claim)
        customer_dict = customer.model_dump()

        channel = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)).channel()
        channel.queue_declare(queue="customer_queue", durable=True)
        # 👉 Instead of DB write, push to RabbitMQ
        print(customer_dict)
        publish_message(channel=channel, queue_name="customer_queue", message=customer_dict)

        return CustomerIngestionResponse(
            status="success",
            message="Customer data pushed to queue for ingestion.",
            customer_id=customer_dict.get("email")  # temporary identifier
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {e}"
        )
    """async def add_customer(customer: Customer):
    try:
        customer_dict = customer.dict()
        publish_message(customer_dict)

        return CustomerIngestionResponse(
            status="success",
            message="Customer record has been queued for ingestion."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {e}"
        )
    """