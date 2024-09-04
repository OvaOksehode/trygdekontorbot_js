# Start med en Python-bilde
FROM python:3.9-slim

# Sett arbeidskatalogen
WORKDIR /app

COPY requirements.txt requirements.txt  # Sjekk at denne refererer til riktig sti
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Eksponer porten Flask vil lytte på
ENV PORT=5000

# Sett opp kommandoen for å kjøre Flask-appen
CMD ["gunicorn", "-b", ":$PORT", "app:app"]
