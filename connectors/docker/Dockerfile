FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

ENV PLATFORM_API_URL=http://localhost:8000/api/v1
ENV HEARTBEAT_INTERVAL=30
ENV SSL_VERIFY=true

CMD ["python", "agent.py"]
