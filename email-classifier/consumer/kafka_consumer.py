from kafka import KafkaConsumer
import json
from .classifier import classify_email

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "email-topic"

async def consume():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True
    )

    print("✅ Listening for new emails...")

    for message in consumer:
        email_data = message.value
        print(f"\n📥 **New email received:** {email_data.get('subject', '')}")
        await classify_email(email_data)
