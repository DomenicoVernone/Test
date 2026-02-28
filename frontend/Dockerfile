# Usiamo una versione leggera di Node.js (la 20 Alpine)
FROM node:20-alpine

# Impostiamo la cartella di lavoro dentro il container
WORKDIR /app

# Copiamo PRIMA solo i file delle dipendenze (package.json)
# Questo trucco sfrutta la cache di Docker e velocizza i caricamenti futuri
COPY package*.json ./

# Installiamo i pacchetti (lucide-react, tailwind, vite, ecc.)
RUN npm install

# Ora copiamo tutto il resto del codice sorgente
COPY . .

# Esponiamo la porta 5173 (quella di default di Vite)
EXPOSE 5173

# Avviamo il server di sviluppo forzando l'esposizione sulla rete di Docker
CMD ["npm", "run", "dev", "--", "--host"]