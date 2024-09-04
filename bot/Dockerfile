# Start med en Node.js-bilde
FROM node:16-alpine

# Sett arbeidskatalogen til /app
WORKDIR /app

# Kopier package.json og package-lock.json
COPY package*.json ./

# Installer avhengigheter
RUN npm install --production

# Kopier resten av applikasjonsfilene
COPY . .

# Miljøvariabler for å overstyre PORT
ENV PORT 8080

# Start botten
CMD ["node", "index.js"]
