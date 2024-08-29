# Bruk en Node.js base image
FROM node:20-alpine

# Sett arbeidskatalogen i containeren
WORKDIR /bot

# Kopier package.json og package-lock.json inn i containeren
COPY package*.json ./

# Installer nødvendige npm-pakker
RUN npm install

# Kopier all bot-kode inn i containeren
COPY . .

# Start Discord-boten
CMD ["node", "index.js"]
