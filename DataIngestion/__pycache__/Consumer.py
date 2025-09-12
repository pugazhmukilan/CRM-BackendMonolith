import os
import pika
import json
from pymongo import MongoClient

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["mydb"]
customers_col = db["customers"]

def callback(ch, method, properties, body):
    customer_dict = json.loads(body.decode())
    print(" [x] Received", customer_dict)

    # 👉 Your MongoDB write logic here
    user = customers_col.find_one({"email": customer_dict['email']})
    if user is None:
        result = customers_col.insert_one(customer_dict)
        print(f"Inserted new customer with id {result.inserted_id}")
    else:
        id = user.get("_id")
        result = customers_col.replace_one({"email": customer_dict['email']}, customer_dict)
        if result.matched_count > 0:
            print(f"Replaced existing customer with id {id}")
        else:
            print("Failed to replace customer data")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    print("started")
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue="customer_queue", durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="customer_queue", on_message_callback=callback)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
