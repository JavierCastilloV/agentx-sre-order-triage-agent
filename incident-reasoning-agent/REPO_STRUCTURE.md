# Repository Structure

incident-reasoner/

README.md
AGENTS_USE.md
SCALING.md
QUICKGUIDE.md
LICENSE
docker-compose.yml
.env.example

app/
 main.py
 agent.py
 tools.py

data/
 sample_incident_checkout_timeout.json
 sample_incident_missing_payload_field.json
 sample_incident_config_mismatch.json

data/
 sample_logs_checkout.json
 sample_logs_payload.json
 sample_logs_config.json

output/
 ticket_example.json

diagrams/
 incident_e2e_flow.puml

presentation/
 Incident_Reasoning_Agent_Deck.pptx
