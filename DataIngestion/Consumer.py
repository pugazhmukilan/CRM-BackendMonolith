# consumer_worker.py
import pika, json, os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = "customer_queue"
MONGO_URL = os.getenv("MONGO_URL")
db = MongoClient(MONGO_URL)["mini_crm"]
customers_col = db["customers"]

def callback(ch, method, properties, body):
    try:
        customer = json.loads(body)
        print("Received:", customer)

        # Upsert logic
        result = customers_col.replace_one(
            {"email": customer["email"]},
            customer,
            upsert=True
        )

        if result.upserted_id:
            print(f"Inserted new customer with ID: {result.upserted_id}")
        else:
            print(f"Updated existing customer with email: {customer['email']}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Error processing message:", e)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()
