# Start med en Node.js-bilde
FROM node:18-alpine

# Sett arbeidskatalogen til /app
WORKDIR /bot

# Kopier package.json og package-lock.json
COPY package*.json ./

# Installer avhengigheter
RUN npm install --production

# Kopier resten av applikasjonsfilene
COPY . .

EXPOSE 8080

# Start botten
CMD ["node", "index.js"]
