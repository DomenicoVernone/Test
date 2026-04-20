<style>

.warn {

&#x20; border-left: 6px solid #f44336;

&#x20; background: #fdecea;

&#x20; padding: 14px;

&#x20; margin: 18px 0;

&#x20; border-radius: 6px;

}

</style>



<h1>Troubleshooting</h1>



<div class="warn">

Questa sezione raccoglie i problemi più comuni durante l’utilizzo della piattaforma ClinicalTwin.

</div>



<h2>Docker non avviato</h2>



Errore:



<pre>Cannot connect to the Docker daemon</pre>



Soluzione:



<pre>

docker info

</pre>



Se fallisce:



<ul>

<li>avvia Docker Desktop</li>

<li>riavvia Docker</li>

</ul>



<h2>FreeSurfer license missing</h2>



Scaricare:



https://surfer.nmr.mgh.harvard.edu/registration.html



Inserire:



<pre>nextflow\_worker/license.txt</pre>



Ricostruire:



<pre>docker compose up --build</pre>



<h2>Pipeline Nextflow bloccata</h2>



Verificare build immagini:



<pre>

docker build -t clinical-freesurfer ...

docker build -t clinical-fsl ...

docker build -t clinical-pyradiomics ...

</pre>



<h2>Errore database orchestrator</h2>



Errore:



<pre>no such table: tasks</pre>



Soluzione:



<pre>

docker compose exec orchestrator bash

python -c "from models.domain import Base; from core.database import engine; Base.metadata.create\_all(bind=engine)"

</pre>



<h2>Reset ambiente completo</h2>



<pre>

docker compose down -v

docker compose build --no-cache

docker compose up -d

</pre>

