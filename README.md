```markdown
# Email Spam Classifier  
Classifies emails into Spam, Phishing, or Legitimate using Kafka, LLaMA3.1 8B, and MongoDB.  

## Project Overview  
This project builds a real-time email classification pipeline using:  
- Zapier – Captures incoming emails  
- Kafka – Streams email data  
- LLaMA3.1 8B (via Ollama) – Classifies emails  
- MongoDB – Stores classification results  

## Flow and Usability  
1. Zapier captures emails and sends them to the backend via a webhook.  
2. The backend sends the email data to a Kafka topic.  
3. A Kafka consumer reads the data and sends it to the LLaMA3.1 model via Ollama.  
4. The model classifies the email as Spam, Phishing, or Legitimate.  
5. The result is stored in MongoDB and displayed on the console.  

## Setup Instructions  
### Clone the Repository  
```bash
git clone https://github.com/your-username/email-spam-classifier.git  
cd email-spam-classifier
```

### Create Virtual Environment  
```bash
python3 -m venv venv  
source venv/bin/activate
```

### Install Dependencies  
```bash
pip install -r requirements.txt
```

### Set Environment Variables  
Create a `.env` file:  
```plaintext
KAFKA_BROKER=localhost:9092  
KAFKA_TOPIC=email_spam  
OLLAMA_URL=http://localhost:11434  
MONGO_URI=mongodb://localhost:27017/email_classifier  
```

### Install Ollama  
- Install Ollama:  
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

- Pull the LLaMA model (Example: LLaMA3.1 8B):  
```bash
ollama pull llama3.1:8b
```

- Start Ollama service:  
```bash
ollama serve
```

### Create Kafka Topic  
Create a Kafka topic named `email_spam`:  
```bash
bin/kafka-topics.sh --create --topic email_spam --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### Start Kafka  
Start Zookeeper and Kafka server:  
```bash
bin/zookeeper-server-start.sh config/zookeeper.properties  
bin/kafka-server-start.sh config/server.properties
```

### Run Pipeline  
Start the HTTP server:  
```bash
python main.py
```

Start Kafka consumer:  
```bash
python consumer_main.py
```

## Zapier Integration  
1. Create a Zap:  
   - Trigger: New Email  
   - Action: Webhook (POST)  

2. Send to Local Server:  
   - URL: `http://localhost:5000/process-email`  
   - JSON Payload:  
```json
{
  "subject": "{{subject}}", 
  "body": "{{body}}"
}
```

## How It Works  
1. Email → Zapier → Kafka  
2. Kafka → LLaMA3.1 (via Ollama) → Classification  
3. Store result in MongoDB  
4. Output result on terminal  

## Tech Stack  
- Python – Backend  
- Kafka – Message streaming  
- LLaMA3.1 8B – Language model for classification  
- MongoDB – Database  
- Zapier – Webhook automation  
- Ollama – Model serving  

## Author  
Karthikeyan S – Data Scientist  

For any queries, contact me at **karthikeyan25062005@gmail.com**  

Happy Coding!
```
