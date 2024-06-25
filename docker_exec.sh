#/bin/bash

docker run -t session-tracker python3 -m pytest /app/ 
echo
echo "Please find the Fair Billable Session Reports for log file $1: "
docker run -v "$1":/app/logs.txt -t session-tracker python3 /app/generate_billable_sessions.py /app/logs.txt

