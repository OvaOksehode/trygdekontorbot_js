# Dockerfile for Flask API
FROM python:3.9-slim

WORKDIR /api

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/data"]

EXPOSE 5000

CMD ["python", "app.py"]
