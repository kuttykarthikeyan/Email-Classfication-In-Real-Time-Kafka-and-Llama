from kafka import KafkaConsumer
from motor.motor_asyncio import AsyncIOMotorClient
import json
import aiohttp
import asyncio

# Kafka Config
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "email-topic"

# MongoDB Config
MONGO_URI = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URI)
db = client["emailDB"]
collection = db["emails"]

# LLaMA 3.1 (Ollama) Config
OLLAMA_URL = "http://localhost:11434/api/generate"

# Function to classify email using LLaMA 3.1
async def classify_email(email_data):
    email_id = email_data.get("email_id")

    prompt = f"""
You are an expert email classifier. Your task is to analyze the following email and classify it into one of these categories:

1. **Spam** – Irrelevant or unsolicited messages, often promotional or deceptive.
2. **Phishing** – Emails attempting to steal sensitive information (e.g., login credentials, financial details).
3. **Social** – Legitimate personal or social communication (e.g., friend invitations, updates).

### **Email Details:**
- **Subject:** "{email_data.get('subject', '')}"
- **Body:** "{email_data.get('body', '')}"
- **Full HTML Body:** "{email_data.get('full_body_html', '')}"
- **Sender Email:** "{email_data.get('sender_email', '')}"
- **Sender Name:** "{email_data.get('sender_name', '')}"
- **Attachment Count:** {email_data.get('attachment_count', 0)}
- **Timestamp:** "{email_data.get('timestamp', '')}"

### **Respond in the following JSON format:**
{{
  "classification": "spam/phishing/social"
}}
"""

    print("\n📨 **Prompt Sent to LLaMA:**")
    print(prompt)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json={
                "model": "llama3.1:8b",
                "prompt": prompt,
                "stream": False
            }) as response:
                result = await response.json()
                print("\n🛬 **Response from LLaMA:**")
                print(json.dumps(result, indent=4))

                result_text = result.get("response", "").strip()

                # ✅ Handle JSON parsing or fallback to raw text classification
                try:
                    classification_result = json.loads(result_text)
                    classification = classification_result.get("classification", "unknown")
                except json.JSONDecodeError:
                    if "spam" in result_text.lower():
                        classification = "spam"
                    elif "phishing" in result_text.lower():
                        classification = "phishing"
                    elif "social" in result_text.lower():
                        classification = "social"
                    else:
                        classification = "unknown"

                # ✅ Update MongoDB with classification result only
                if classification != "unknown":
                    await collection.update_one(
                        {"_id": email_id},
                        {"$set": {"status": classification}}
                    )
                    print(f"✅ Email {email_id} classified as: {classification}")
                else:
                    print(f"⚠️ Classification failed for email {email_id}")

    except Exception as e:
        print(f"❌ Error processing email {email_id}: {e}")

# Kafka Consumer
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

if __name__ == "__main__":
    asyncio.run(consume())
