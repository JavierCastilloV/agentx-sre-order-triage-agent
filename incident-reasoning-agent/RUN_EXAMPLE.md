# Example execution

Start service:

docker compose up --build

Submit sample incident:

curl -X POST http://localhost:8000/incident \
-H "Content-Type: application/json" \
-d @data/sample_incident_checkout_timeout.json

Example output:

{
  "possible_causes": [
    "timeout misconfiguration",
    "network latency spike"
  ]
}
