# Dockerfile for Flask API
FROM python:3.9-slim

WORKDIR /app

COPY api/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ .

ENV PORT=5000

CMD ["python", "app.py"]
