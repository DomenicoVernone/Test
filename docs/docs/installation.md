Installazione

Requisiti di sistema



La piattaforma ClinicalTwin è distribuita come sistema containerizzato basato su Docker Compose, che consente l’esecuzione coordinata dei microservizi necessari alla pipeline neuroimaging.



Prima dell’installazione è necessario verificare la presenza dei seguenti prerequisiti:



Docker ≥ 24.x

Docker Compose ≥ 2.x

Git

almeno 16 GB di RAM consigliati (per esecuzione FreeSurfer)

sistema operativo Linux, macOS oppure Windows con Docker Desktop attivo



Per workflow completi con segmentazione FreeSurfer è raccomandata la disponibilità di CPU multi-core e spazio disco ≥ 20 GB 📦



Clonazione del repository



Il primo passo consiste nel clonare il repository del progetto:



git clone https://github.com/DomenicoVernone/Test.git

cd Test



Questo comando scarica l’intera struttura del sistema ClinicalTwin sul computer locale.



Configurazione delle variabili d’ambiente



Prima dell’avvio dei servizi è necessario configurare le variabili di ambiente utilizzate dai container.



Copiare il file di esempio:



cp .env.example .env



e modificarne i parametri principali, in particolare:



directory condivisa per i volumi MRI

configurazione GPU (se disponibile)

parametri di rete tra i servizi



Questa fase consente al sistema di adattarsi all’ambiente locale di esecuzione ⚙️



Build dei container Docker



ClinicalTwin utilizza immagini Docker personalizzate per i moduli di preprocessing neuroimaging.



Per costruire i container eseguire:



docker compose up --build



Il comando esegue automaticamente:



build delle immagini Docker personalizzate;

inizializzazione dei servizi backend;

avvio della pipeline orchestrata;

configurazione della rete interna tra container.



Durante la prima esecuzione il processo può richiedere diversi minuti a causa della compilazione delle immagini FreeSurfer, FSL e PyRadiomics.



Avvio della piattaforma



Una volta completata la build, il sistema avvia automaticamente i seguenti servizi:



API Gateway (autenticazione utenti)

Orchestrator (gestione task MRI)

Nextflow Worker (pipeline neuroimaging)

Model Service (inferenza diagnostica)

LLM Assistant (supporto interpretativo)

Frontend web clinico



L’interfaccia utente è accessibile tramite browser all’indirizzo:



http://localhost:3000



Da qui è possibile autenticarsi, caricare immagini MRI e monitorare l’avanzamento delle analisi 🧠



Verifica del corretto funzionamento



Per verificare che il sistema sia operativo:



accedere al frontend;

registrare un nuovo utente;

caricare un file MRI in formato .nii o .nii.gz;

monitorare lo stato del task di preprocessing;

visualizzare la predizione diagnostica generata dal modello.



Se tutti i servizi risultano attivi, ClinicalTwin è pronto per l’utilizzo sperimentale e la validazione della pipeline neuroimaging.

