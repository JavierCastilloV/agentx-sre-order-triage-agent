# QUICKGUIDE

This guide explains how to run and validate the Incident Reasoning Agent locally.

The application runs entirely using Docker and includes mock technical signals to demonstrate the end to end reasoning flow.

No external services are required.

---

# 1 Clone repository

git clone <repository_url>

cd incident-reasoner

---

# 2 Configure environment variables

Copy environment template:

cp .env.example .env

The project runs using mock reasoning by default.

No API keys are required.

---

# 3 Build and start the application

docker compose up --build

The API will be available at:

http://localhost:8000

---

# 4 Validate service status

Run:

curl http://localhost:8000/

Expected response:

{
 "message": "Incident Reasoning Agent is running",
 "prompt_loaded": "yes"
}

---

# 5 Open interactive API documentation

Open:

http://localhost:8000/docs

Swagger UI allows testing endpoints interactively.

---

# 6 Submit sample incident

Example request:

curl -X POST http://localhost:8000/incident \
-H "Content-Type: application/json" \
-d @data/sample_incident_checkout_timeout.json

---

# 7 Validate reasoning output

Response includes:

incident summary
possible root causes
confidence score per hypothesis
recommended technical actions

---

# 8 Validate ticket creation

A simulated ticket will be created:

output/ticket_<incident_id>.json

Example:

cat output/ticket_001.json

---

# 9 Available sample incidents

data/sample_incident_checkout_timeout.json
data/sample_incident_missing_payload_field.json
data/sample_incident_config_mismatch.json

---

# End to end flow demonstrated

incident submitted
technical signals retrieved
reasoning hypotheses generated
structured explanation created
mock ticket stored

---

# Stop service

CTRL + C

or

docker compose down
