# Start med en Python-bilde
FROM python:3.9-slim

# Sett arbeidskatalogen
WORKDIR /app

# Kopier kravfilene
COPY api/requirements.txt requirements.txt

# Installer kravene
RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten av applikasjonen
COPY api/ .

# Eksponer porten Flask vil lytte på
ENV PORT=5000

# Sett opp kommandoen for å kjøre Flask-appen
CMD ["gunicorn", "-b", ":$PORT", "app:app"]
