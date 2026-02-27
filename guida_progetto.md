# **📘 Manuale Operativo Personale: Setup e Gestione Progetto**

Questo documento è il tuo riferimento personale. Definisce le best practices, l'architettura delle cartelle, il workflow di Git/GitHub e la configurazione dell'ambiente di sviluppo per la creazione del sistema di Supporto alla Decisione Clinica (FTD).

*Nota: Questo è il tuo manuale privato. Il file README.md sarà invece un file più breve destinato a chi (come il professore) dovrà capire come far partire il progetto.*

## **1\. Architettura delle Cartelle (Il Monorepo)**

Utilizzeremo un approccio **Monorepo**: un unico repository GitHub che contiene tutti i microservizi. Questo garantisce che il codice del frontend, del backend (FastAPI) e del modello ML siano sempre allineati.

La struttura **DEVE** essere esattamente questa:

PROGETTO\_TESI/  
├── .git/                 (Cartella nascosta, il "cervello" di Git)  
├── .gitignore            (Regole globali per ignorare file)  
├── README.md             (Brevi istruzioni pubbliche per chi visita il repo)  
├── guida\_progetto.md     (\<-- QUESTO FILE: il tuo manuale personale)  
├── docker-compose.yml    (Orchestrazione dei container)  
│  
├── frontend/             (React \+ Vite)  
│   ├── .gitignore        (Regole specifiche per Node/React)  
│   ├── package.json  
│   ├── src/  
│   └── Dockerfile  
│  
├── fastapi/              (FastAPI \+ Python)  
│   ├── .gitignore        (Regole specifiche per Python)  
│   ├── main.py  
│   ├── requirements.txt  
│   └── Dockerfile  
│  
└── microservizio\_r/      (R \+ Plumber)  
    ├── .gitignore        (Regole specifiche per R)  
    ├── plumber.R  
    └── Dockerfile

## **2\. Ordine di Setup e Installazione (Cruciale\!)**

Segui questo ordine esatto per evitare conflitti, specialmente i temuti "submodules" di Git.

### **Step 1: Creazione della "Scatola" Principale**

1. Crea una cartella vuota chiamata PROGETTO\_TESI (fuori da OneDrive/Google Drive).  
2. Aprila con VS Code.  
3. Apri il terminale integrato di VS Code e inizializza Git:  
   git init

### **Step 2: Setup del Frontend (React)**

1. Dal terminale principale, lancia: npx create-vite frontend \--template react  
2. **ATTENZIONE:** Vite a volte crea una sua cartella .git nascosta dentro frontend/. Devi cancellarla assolutamente, altrimenti impazzirai. Il progetto deve avere UN SOLO .git nella cartella principale PROGETTO\_TESI/.

### **Step 3: Setup Backend e ML**

1. Crea manualmente la cartella fastapi/ e aggiungi i file Python.  
2. Crea manualmente la cartella microservizio\_r/ e aggiungi i file R.

## **3\. I File .gitignore (La tua cassaforte)**

Questi file dicono a Git cosa **NON** tracciare. Creali nei percorsi indicati.

**A. Nella radice del progetto (PROGETTO\_TESI/.gitignore):**

\# Sistemi Operativi  
.DS\_Store  
Thumbs.db

\# Dati Clinici e Modelli (MAI CARICARE DATI REALI SU GIT)  
\*.nii  
\*.nii.gz  
\*.dcm  
\*.rds  
dati\_sensibili/

**B. Nella cartella Frontend (PROGETTO\_TESI/frontend/.gitignore):**

node\_modules/  
dist/  
.env

**C. Nella cartella FastAPI (PROGETTO\_TESI/fastapi/.gitignore):**

\_\_pycache\_\_/  
\*.pyc  
.venv/  
venv/  
.env

**D. Nella cartella R (PROGETTO\_TESI/microservizio\_r/.gitignore):**

.Rhistory  
.RData  
.Ruserdata

## **4\. GitHub e Workflow Giornaliero**

### **A. Primo collegamento a GitHub**

1. Vai su GitHub e crea un nuovo repository vuoto (senza README, senza .gitignore).  
2. Nel terminale di VS Code (nella cartella PROGETTO\_TESI), lancia:  
   git add .  
   git commit \-m "feat: setup iniziale architettura a microservizi"  
   git branch \-M main  
   git remote add origin \[https://github.com/TUO\_NOME/TUO\_REPO.git\](https://github.com/TUO\_NOME/TUO\_REPO.git)  
   git push \-u origin main

### **B. Il Workflow Quotidiano (La routine del programmatore)**

Ogni volta che inizi a lavorare:

1. git pull (Scarica eventuali modifiche, utile se lavori da due PC).  
2. Scrivi il tuo codice. Testalo.  
3. git status (Guarda cosa hai modificato in rosso).  
4. git add . (Prepara tutte le modifiche).  
5. git commit \-m "tipo: descrizione" (Salva una "fotografia" locale).  
6. git push (Invia la fotografia su GitHub).

### **C. Regole di Nomenclatura dei Commit (Conventional Commits)**

Usa sempre questi prefissi per i tuoi messaggi di commit:

* feat: (Nuova funzionalità. Es: *feat: aggiunto bottone caricamento MRI*)  
* fix: (Risoluzione di un bug. Es: *fix: corretto errore CORS in FastAPI*)  
* docs: (Modifiche alla documentazione/README)  
* refactor: (Pulizia del codice senza aggiungere funzionalità)

### **D. I Branch (Sperimentazione sicura)**

Se devi provare una cosa nuova e hai paura di rompere il progetto funzionante:

1. Crea un ramo: git checkout \-b feature/nuovo-test  
2. Lavora e fai i commit qui.  
3. Se funziona, torna al principale (git checkout main) e uniscilo (git merge feature/nuovo-test).

## **5\. L'Ambiente VS Code (I Superpoteri)**

Per sviluppare comodamente con questa architettura, VS Code deve essere configurato bene.

### **Estensioni Obbligatorie da Installare:**

1. **Docker (di Microsoft):** Ti permette di vedere i container accesi, spegnerli e leggere i log cliccando su un'interfaccia grafica a sinistra, senza usare il terminale.  
2. **GitLens:** Un superpotere per Git. Ti fa vedere in ogni riga di codice chi l'ha modificata, quando, e in quale commit. Ti mostra un albero visuale fantastico dei tuoi branch.  
3. **Python (di Microsoft):** Essenziale per FastAPI, ti darà l'autocompletamento del codice.  
4. **ESLint & Prettier:** Per formattare automaticamente il codice React ogni volta che salvi (Ctrl+S / Cmd+S).

### **Gestione dei Terminali in VS Code:**

Non impazzire con decine di finestre nere aperte.

* Usa la funzione **"Split Terminal"** (l'icona con due pannelli affiancati in alto a destra nel pannello del terminale).  
* Puoi tenere aperto a sinistra il terminale per React (npm run dev), al centro quello per Docker (docker compose up) e a destra la console per i comandi Git.  
* Rinomina i terminali (tasto destro sul nome del terminale \-\> *Rename*) in "Frontend", "Docker" e "Git" per non confonderti mai.

* Nota: Test del workflow di Git completato con successo. 