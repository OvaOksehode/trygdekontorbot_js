# Bruk en base image med Python
FROM python:3.11-slim

# Sett arbeidskatalogen i containeren
WORKDIR /app

# Kopier requirements.txt inn i containeren
COPY requirements.txt .

# Installer nødvendige Python-pakker
RUN pip install --no-cache-dir -r requirements.txt

# Kopier Flask API-koden inn i containeren
COPY . .

# Eksponer port 5000 for Flask-appen
EXPOSE 5000

# Kommandoen for å kjøre Flask-appen
CMD ["python", "app.py"]
