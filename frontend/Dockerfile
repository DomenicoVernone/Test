# Dockerfile per il frontend basato su Node.js e Vite
FROM node:20-alpine

# Imposta la cartella di lavoro
WORKDIR /app

# Copia i file di configurazione e installa le dipendenze
COPY package*.json ./

# Installazione delle dipendenze Node.js
RUN npm install

# Copia tutto il codice del frontend
COPY . .

# Esponiamo esplicitamente la porta (Best Practice per la leggibilità)
EXPOSE 5173

# Comando di avvio per Vite, ascoltando sulla porta 5173
CMD ["npm", "run", "dev", "--", "--host"] 