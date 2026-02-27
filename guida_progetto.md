📘 Manuale Operativo Personale: Setup e Gestione Progetto

Questo documento è il tuo riferimento personale. Definisce le best practices, l'architettura delle cartelle, il workflow di Git/GitHub e la configurazione dell'ambiente di sviluppo per la creazione del sistema di Supporto alla Decisione Clinica (FTD).

Nota: Questo è il tuo manuale privato. Il file README.md sarà invece un file più breve destinato a chi (come il professore) dovrà capire come far partire il progetto.

1. Architettura delle Cartelle (Il Monorepo)

Utilizzeremo un approccio Monorepo: un unico repository GitHub che contiene tutti i microservizi. Questo garantisce che il codice del frontend, del backend (FastAPI) e del modello ML siano sempre allineati.

La struttura DEVE essere esattamente questa:

PROGETTO_TESI/
├── .git/                 (Cartella nascosta, il "cervello" di Git)
├── .gitignore            (Regole globali per ignorare file)
├── README.md             (Brevi istruzioni pubbliche per chi visita il repo)
├── guida_progetto.md     (<-- QUESTO FILE: il tuo manuale personale)
├── docker-compose.yml    (Orchestrazione dei container)
│
├── frontend/             (React + Vite)
│   ├── .gitignore        (Regole specifiche per Node/React)
│   ├── package.json
│   ├── src/
│   └── Dockerfile
│
├── fastapi/              (FastAPI + Python)
│   ├── .gitignore        (Regole specifiche per Python)
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── microservizio_r/      (R + Plumber)
    ├── .gitignore        (Regole specifiche per R)
    ├── plumber.R
    └── Dockerfile


2. Ordine di Setup e Installazione (Cruciale!)

Segui questo ordine esatto per evitare conflitti, specialmente i temuti "submodules" di Git.

Step 1: Creazione della "Scatola" Principale

Crea una cartella vuota chiamata PROGETTO_TESI (fuori da OneDrive/Google Drive).

Aprila con VS Code.

Apri il terminale integrato di VS Code e inizializza Git:

git init


Step 2: Setup del Frontend (React)

Dal terminale principale, lancia: npx create-vite frontend --template react

ATTENZIONE: Vite a volte crea una sua cartella .git nascosta dentro frontend/. Devi cancellarla assolutamente, altrimenti impazzirai. Il progetto deve avere UN SOLO .git nella cartella principale PROGETTO_TESI/.

Step 3: Setup Backend e ML

Crea manualmente la cartella fastapi/ e aggiungi i file Python.

Crea manualmente la cartella microservizio_r/ e aggiungi i file R.

3. I File .gitignore (La tua cassaforte)

Questi file dicono a Git cosa NON tracciare. Creali nei percorsi indicati.

A. Nella radice del progetto (PROGETTO_TESI/.gitignore):

# Sistemi Operativi
.DS_Store
Thumbs.db

# Dati Clinici e Modelli (MAI CARICARE DATI REALI SU GIT)
*.nii
*.nii.gz
*.dcm
*.rds
dati_sensibili/


B. Nella cartella Frontend (PROGETTO_TESI/frontend/.gitignore):

node_modules/
dist/
.env


C. Nella cartella FastAPI (PROGETTO_TESI/fastapi/.gitignore):

__pycache__/
*.pyc
.venv/
venv/
.env


D. Nella cartella R (PROGETTO_TESI/microservizio_r/.gitignore):

.Rhistory
.RData
.Ruserdata


4. GitHub e Workflow Giornaliero

A. Primo collegamento a GitHub

Vai su GitHub e crea un nuovo repository vuoto (senza README, senza .gitignore).

Nel terminale di VS Code (nella cartella PROGETTO_TESI), lancia:

git add .
git commit -m "feat: setup iniziale architettura a microservizi"
git branch -M main
git remote add origin [https://github.com/TUO_NOME/TUO_REPO.git](https://github.com/TUO_NOME/TUO_REPO.git)
git push -u origin main


B. Il Workflow Quotidiano (La routine del programmatore)

Ogni volta che inizi a lavorare:

git pull (Scarica eventuali modifiche, utile se lavori da due PC).

Scrivi il tuo codice. Testalo.

git status (Guarda cosa hai modificato in rosso). Oppure usa la scheda Source Control di VS Code.

git add . (Prepara tutte le modifiche, cliccando il + nell'interfaccia visiva).

git commit -m "tipo: descrizione" (Salva la "fotografia" locale, scrivendo il messaggio e premendo Commit).

git push (Invia la fotografia su GitHub, premendo Sync Changes).

C. Regole di Nomenclatura dei Commit (Conventional Commits)

Usa sempre questi prefissi per i tuoi messaggi di commit:

feat: (Nuova funzionalità. Es: feat: aggiunto bottone caricamento MRI)

fix: (Risoluzione di un bug. Es: fix: corretto errore CORS in FastAPI)

docs: (Modifiche alla documentazione/README)

refactor: (Pulizia del codice senza aggiungere funzionalità)

D. I Branch (Sperimentazione sicura)

Se devi provare una cosa nuova e hai paura di rompere il progetto funzionante:

Metodo Visivo (Senza Terminale, consigliato):

Crea il ramo: Clicca sul nome del ramo attuale (main) in basso a sinistra nella barra di stato blu di VS Code. Seleziona Create new branch..., digita il nome (es. feature/nuovo-test) e premi Invio.

Lavora e salva: Fai le tue modifiche e usa l'icona Source Control (il rametto a sinistra) per fare i tuoi commit.

Unisci (Merge): * Clicca in basso a sinistra sul nome del tuo ramo attuale e riseleziona main (stai tornando all'universo principale).

Apri la Command Palette premendo Ctrl+Shift+P (su Windows/Linux) o Cmd+Shift+P (su Mac).

Scrivi Git: Merge Branch... e premi Invio.

Seleziona dalla lista il ramo che hai appena finito (es. feature/nuovo-test). Fatto!

Elimina il ramo: Apri la Command Palette (Ctrl+Shift+P), scrivi Git: Delete Branch..., seleziona il ramo appena unito ed eliminalo per mantenere pulito il progetto.

Metodo da Terminale (Alternativa):

Crea un ramo: git checkout -b feature/nuovo-test

Lavora e fai i commit qui.

Torna al principale e unisci: git checkout main poi git merge feature/nuovo-test.

Elimina il ramo: git branch -d feature/nuovo-test

5. L'Ambiente VS Code (I Superpoteri)

Per sviluppare comodamente con questa architettura, VS Code deve essere configurato bene.

Estensioni Obbligatorie da Installare:

Docker (di Microsoft): Ti permette di vedere i container accesi, spegnerli e leggere i log cliccando su un'interfaccia grafica a sinistra, senza usare il terminale.

GitLens: Un superpotere per Git. Ti fa vedere in ogni riga di codice chi l'ha modificata, quando, e in quale commit. Ti mostra un albero visuale fantastico dei tuoi branch.

Python (di Microsoft): Essenziale per FastAPI, ti darà l'autocompletamento del codice.

ESLint & Prettier: Per formattare automaticamente il codice React ogni volta che salvi (Ctrl+S / Cmd+S).

Gestione dei Terminali in VS Code:

Non impazzire con decine di finestre nere aperte.

Usa la funzione "Split Terminal" (l'icona con due pannelli affiancati in alto a destra nel pannello del terminale).

Puoi tenere aperto a sinistra il terminale per React (npm run dev), al centro quello per Docker (docker compose up) e a destra la console per i comandi Git.

Rinomina i terminali (tasto destro sul nome del terminale -> Rename) in "Frontend", "Docker" e "Git" per non confonderti mai.

FRONTEND
🎨 Progettazione UX/UI: Digital Twin ClinicoQuesto documento definisce la struttura visiva e l'esperienza utente del frontend React.1. Analisi del Workflow dell'Utente (Il "Viaggio" del Medico)Il sistema ha una natura fortemente temporale. L'interfaccia non può mostrare tutto subito, ma deve evolversi in 3 fasi (Stati):Fase 1: Input (Stato Iniziale)L'utente seleziona l'esperimento di riferimento.L'utente fa l'upload della risonanza (NIfTI).Fase 2: Validazione & Attesa (Stato Asincrono)Il visualizzatore si attiva sulla scheda "Vista 3D (NiiVue)": il medico controlla visivamente che la slice caricata sia corretta.L'utente preme "Avvia Analisi".Cruciale: Il visualizzatore entra in stato di "Loading" (spinner, messaggi di stato "Estrazione features in corso...") inibendo ulteriori click.Fase 3: Risultati & Interpretazione (Stato Finale)Il sistema fa lo switch automatico sulla scheda "Grafico UMAP (Plotly)".Il medico può passare liberamente tra l'immagine NIfTI e il Grafico cliccando sulle linguette.Si attiva la chat LLM per interpretare i risultati.2. Proposta di Layout: "Command Center Compatto" (Scelta Ufficiale)Questo layout divide lo schermo in due colonne. La colonna di sinistra massimizza lo spazio utilizzando uno Switch (Tabs) per scambiare la vista tra l'immagine anatomica e i risultati matematici, evitando lo scrolling verticale.+---------------------------------------------------------+
| [Logo Tesi]    Esperimento: [ Dropdown Menu ▼ ]         | <- HEADER
+-----------------------------------+---------------------+
|                                   |                     |
|  +-----------------------------+  |  +---------------+  |
|  | [ Area di Drag & Drop     ] |  |  |               |  |
|  | [ Upload File .nii        ] |  |  |               |  |
|  +-----------------------------+  |  |   Assistente  |  |
|                                   |  |      LLM      |  |
|  +-----------------------------+  |  |    (Chat)     |  |
|  | [ 🧠 Vista 3D ] [ 📊 UMAP ] |  |  |               |  | <- SWITCH TABS
|  +-----------------------------+  |  |               |  |
|  |                             |  |  |               |  |
|  |                             |  |  |               |  |
|  |   Area di Visualizzazione   |  |  |               |  |
|  |   (Mostra NiiVue o Plotly   |  |  +---------------+  |
|  |    in base al tab attivo)   |  |  | [ Scrivi... ] |  |
|  |                             |  |  +---------------+  |
|  +-----------------------------+  |                     |
|                                   |                     |
+-----------------------------------+---------------------+
            COLONNA DATI (65%)         COLONNA IA (35%)
I Vantaggi di questa scelta:Zero Scrolling: L'interfaccia sta tutta in una schermata (Single Page Application pura).Focus Cognitivo: L'utente guarda solo il dato che gli serve in quel momento (l'anatomia o la matematica), senza distrazioni, ma sa che l'altro è a un click di distanza.Transizione Fluida: Il passaggio da "Vista 3D" a "UMAP" alla fine del caricamento dà una chiara sensazione di completamento dell'analisi.3. Gestione del Tempo Asincrono (UX Cruciale)Poiché l'elaborazione richiederà tempo, l'utente non deve mai pensare che il sistema si sia bloccato.Soluzione UX: Al click su "Avvia Analisi", l'Area di Visualizzazione diventerà un pannello di stato animato.Esempio di messaggi che si aggiornano:⏳ Caricamento immagine nel database...🧠 Segmentazione e Coregistrazione in corso (può richiedere alcuni minuti)...📊 Calcolo proiezioni UMAP e finalizzazione...