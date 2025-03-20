from fastapi import FastAPI, Request
from .mongodb import collection
from .kafka_producer import producer
import uuid
import json
from datetime import datetime

app = FastAPI()

@app.post("/email-received")
async def receive_email(request: Request):
    data = await request.json()
    print("\n📥 **Incoming Email Request:**")
    print(json.dumps(data, indent=4))

    # ✅ Create unique email_id
    email_id = str(uuid.uuid4())
    subject = data.get("subject")
    body = data.get("body")
    full_body_html = data.get("full_body_html", "")
    sender_email = data.get("sender_email")
    sender_name = data.get("sender_name")
    attachment_count = int(data.get("attachment_count", 0))
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())

    # ✅ Store email in MongoDB
    email_data = {
        "_id": email_id,
        "subject": subject,
        "body": body,
        "full_body_html": full_body_html,
        "sender_email": sender_email,
        "sender_name": sender_name,
        "attachment_count": attachment_count,
        "timestamp": timestamp,
        "status": "pending"
    }

    await collection.insert_one(email_data)
    print(f"✅ Stored in MongoDB - ID: {email_id}")

    # ✅ Send email data to Kafka
    kafka_payload = {
        "email_id": email_id,
        "subject": subject,
        "body": body,
        "full_body_html": full_body_html,
        "sender_email": sender_email,
        "sender_name": sender_name,
        "attachment_count": attachment_count,
        "timestamp": timestamp
    }
    producer.send("email-topic", kafka_payload)
    print(f"📡 Sent to Kafka - Topic: email-topic")

    return {"message": "Email received", "email_id": email_id}

@app.get("/")
def root():
    return {"status": "API is running"}
