# Start med en Node.js-bilde
FROM node:16-alpine

# Sett arbeidskatalogen til /app
WORKDIR /bot

# Kopier package.json og package-lock.json
COPY bot/package*.json ./

# Installer avhengigheter
RUN npm install --production

# Kopier resten av applikasjonsfilene
COPY bot/ .

# Sett miljøvariabler for PORT
ENV PORT=8080

# Start botten
CMD ["node", "index.js"]
