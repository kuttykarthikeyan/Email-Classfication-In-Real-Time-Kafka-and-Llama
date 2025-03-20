import aiohttp
import json
from app.mongodb import collection


OLLAMA_URL = "http://localhost:11434/api/generate"

async def classify_email(email_data):
    email_id = email_data.get("email_id")

    prompt = f"""
You are an expert email classifier. Your task is to analyze the following email and classify it into one of these categories:

1. **Spam** – Irrelevant or unsolicited messages, often promotional or deceptive.
2. **Phishing** – Emails attempting to steal sensitive information (e.g., login credentials, financial details).
3. **Social** – Legitimate personal or social communication (e.g., friend invitations, event updates, casual messages).

### **Email Details:**
- **Subject:** "{email_data.get('subject', '')}"
- **Body:** "{email_data.get('body', '')}"
- **Full HTML Body:** "{email_data.get('full_body_html', '')}"
- **Sender Email:** "{email_data.get('sender_email', '')}"
- **Sender Name:** "{email_data.get('sender_name', '')}"
- **Attachment Count:** {email_data.get('attachment_count', 0)}
- **Timestamp:** "{email_data.get('timestamp', '')}"

### **Analyze the Following:**
1. **Subject Analysis:**  
   - If the subject includes words like "offer", "win", "free", or "urgent," classify it as **spam**.  
   - If the subject references personal events (e.g., invitations, casual meetings), classify it as **social**.  

2. **Body and HTML Content Analysis:**  
   - If the language references financial gain, promotional content, or urgency, classify it as **spam**.  
   - If the language is conversational or related to personal communication (e.g., "see you soon", "let's meet up"), classify it as **social**.  

3. **Sender Information Consistency:**  
   - If the sender is a known entity (friend, family, or colleague), classify it as **social**.  
   - If the sender's address resembles marketing or generic patterns, classify it as **spam**.  

4. **Spam and Phishing Indicators:**  
   - If the email urges immediate action or asks for sensitive information, classify it as **phishing**.  
   - If the email is conversational or about personal plans, classify it as **social**.  

---

### **Respond in the following JSON format:**
{{
  "classification": "spam/phishing/social"
}}
"""


    print("\n📨 **Prompt Sent to LLaMA:**")
    print(prompt)

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

            if "spam" in result_text.lower():
                classification = "spam"
            elif "phishing" in result_text.lower():
                classification = "phishing"
            elif "social" in result_text.lower():
                classification = "social"
            else:
                classification = "unknown"

            if classification != "unknown":
                await collection.update_one(
                    {"_id": email_id},
                    {"$set": {"status": classification}}
                )
                print(f"✅ Email {email_id} classified as: {classification}")
