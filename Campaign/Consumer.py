# consumer_worker.py
import pika, json, os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
QUEUE_NAME = "email_queue"

def send_email(to_email, body):
    print(f"Sending email to {to_email} with body '{body}'")



def callback(ch, method, properties, body):
    try:
        emails = json.loads(body)
        print("Received:", emails)

        send_email(
            to_email=emails["email"],
           
            body=emails["message"]
        )

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
