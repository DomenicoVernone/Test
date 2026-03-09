# File: frontend/Dockerfile
# Usiamo una versione leggera di Node.js
FROM node:20-alpine

# Impostiamo la cartella di lavoro
WORKDIR /app

# Copiamo prima package.json per sfruttare la cache dei layer Docker
COPY package*.json ./

# Installiamo le dipendenze
RUN npm install

# [FIX SINTASSI] Copiamo il resto del codice sorgente
COPY . .

# Esponiamo la porta di default di Vite
EXPOSE 5173

# Avviamo il server di sviluppo esposto sulla rete Docker
CMD ["npm", "run", "dev", "--", "--host"]