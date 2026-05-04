<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – API Reference</title>

<style>
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 40px;
    background-color: #f9f9f9;
    color: #333;
}

h1, h2, h3 {
    color: #2c3e50;
}

h1 {
    border-bottom: 2px solid #ccc;
    padding-bottom: 10px;
}

pre {
    background-color: #eee;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

.section {
    margin-bottom: 40px;
}

.box {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

ul {
    margin-left: 20px;
}

/* ===== TABLE STYLE UNIFICATO ===== */

table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 15px;
    font-size: 14px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 6px;
    overflow: hidden;
}

th {
    background-color: #2c3e50;
    color: white;
    text-align: left;
    padding: 12px;
    font-weight: 600;
}

td {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    vertical-align: top;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

tr:hover {
    background-color: #eef2f5;
}
</style>

</head>

<body>

<div class="box">

<h1>REST API – MLOps System</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
The MLOps system exposes a set of REST APIs that enable communication
between microservices and interaction with the clinical frontend.
</p>

<p>
APIs represent the integration layer of the entire platform and
define the contract between:
</p>

<ul>
<li>user and system (frontend → backend)</li>
<li>internal microservices</li>
<li>pipeline and inference engine</li>
</ul>

<p>
Endpoints are mainly implemented using FastAPI (Python)
and Plumber (R), and use JSON as the standard format for requests and responses.
</p>

</div>

<div class="section">
<h2>2. API Architecture</h2>

<p>
The APIs follow a distributed model where each microservice exposes
specific endpoints for its functional domain.
</p>

<pre>
Frontend
   ↓
API Gateway (authentication)
   ↓
Orchestrator (pipeline tasks)
   ↓
Nextflow Worker (pipeline)
   ↓
Inference Engine (KNN + UMAP)
   ↓
LLM Service (explainability)
</pre>

<p>
The API Gateway represents the main entry point and manages
authentication through JWT tokens.
</p>

</div>

<div class="section">
<h2>3. Authentication and Security</h2>

<p>
The system uses JSON Web Token (JWT)-based authentication
to protect endpoints.
</p>

<p>
Authentication flow:
</p>

<pre>
1. User logs in
2. Server generates JWT
3. Token included in subsequent requests
4. Services validate the token
</pre>

<p>
Required header:
</p>

<pre>
Authorization: Bearer &lt;token&gt;
</pre>

</div>

<div class="section">
<h2>4. api_gateway API</h2>

<h3>4.1 User Registration</h3>

<pre>
POST /signup
</pre>

<p>Request:</p>

<pre>
{
  "username": "user",
  "password": "password"
}
</pre>

<p>Response:</p>

<pre>
{
  "message": "User created successfully"
}
</pre>

<h3>4.2 Login</h3>

<pre>
POST /login
</pre>

<p>Response:</p>

<pre>
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
</pre>

<h3>4.3 User Information</h3>

<pre>
GET /me
</pre>

<p>Response:</p>

<pre>
{
  "username": "user"
}
</pre>

</div>

<div class="section">
<h2>5. orchestrator API</h2>

<h3>5.1 Start MRI Analysis</h3>

<pre>
POST /analyze
</pre>

<p>Request:</p>

<pre>
{
  "filename": "subject01.nii.gz"
}
</pre>

<p>Response:</p>

<pre>
{
  "task_id": "12345",
  "status": "pending"
}
</pre>

<h3>5.2 Task Status</h3>

<pre>
GET /task/{task_id}
</pre>

<p>Response:</p>

<pre>
{
  "task_id": "12345",
  "status": "running",
  "created_at": "timestamp"
}
</pre>

<h3>5.3 Task List</h3>

<pre>
GET /tasks
</pre>

<p>
Returns all analyses associated with the authenticated user.
</p>

</div>

<div class="section">
<h2>6. inference_engine API</h2>

<h3>6.1 KNN Classification</h3>

<pre>
POST /knn
</pre>

<p>Response:</p>

<pre>
{
  "prediction": "bvFTD",
  "confidence": 0.81
}
</pre>

<h3>6.2 UMAP Projection</h3>

<pre>
POST /umap
</pre>

<p>Response:</p>

<pre>
{
  "x": 1.23,
  "y": -0.45,
  "z": 2.11
}
</pre>

</div>

<div class="section">
<h2>7. model_service API</h2>

<h3>7.1 Model Loading</h3>

<pre>
POST /load-model
</pre>

<p>
Downloads the model from the MLflow Model Registry and makes it available
to the inference_engine.
</p>

<h3>7.2 Prediction (optional)</h3>

<pre>
POST /predict
</pre>

<p>
Optional endpoint for direct inference (not used in the main workflow).
</p>

</div>

<div class="section">
<h2>8. llm_service API</h2>

<h3>8.1 AI Chat</h3>

<pre>
POST /chat
</pre>

<p>Request:</p>

<pre>
{
  "message": "Explain this patient's diagnosis"
}
</pre>

<p>Response:</p>

<pre>
{
  "response": "The patient is located near..."
}
</pre>

<p>
This endpoint uses radiomic features and UMAP coordinates
to generate contextual clinical explanations.
</p>

</div>

<div class="section">
<h2>9. Data Contract Between Services</h2>

<p>
APIs define a clear data contract between system components.
</p>

<p>
Core element:
</p>

<pre>
radiomics_features.csv
</pre>

<p>
This file represents the standard input for the inference_engine
and ensures consistency between pipeline and inference.
</p>

<p>
Inference output:
</p>

<pre>
{
  "prediction": "...",
  "confidence": 0.XX,
  "umap_coordinates": [x, y, z]
}
</pre>

</div>

<div class="section">
<h2>10. Swagger and Testing</h2>

<p>
Each FastAPI microservice exposes interactive documentation
via Swagger UI:
</p>

<pre>
http://localhost:8000/docs
http://localhost:8001/docs
http://localhost:8002/docs
</pre>

<p>
Swagger allows:
</p>

<ul>
<li>endpoint testing</li>
<li>JSON validation</li>
<li>quick debugging</li>
</ul>

</div>

<div class="section">
<h2>11. Error Handling</h2>

<p>
APIs follow standard HTTP conventions:
</p>

<ul>
<li>200 → success</li>
<li>401 → unauthorized</li>
<li>404 → resource not found</li>
<li>500 → internal error</li>
</ul>

<p>
Errors are propagated across services to ensure
workflow consistency.
</p>

</div>

<div class="section">
<h2>12. Conclusions</h2>

<p>
APIs represent the communication backbone of the MLOps system,
ensuring interoperability between microservices and integration
with the frontend.
</p>

<p>
Clear definition of data contracts and endpoints enables
modular system evolution and facilitates the development
of new features.
</p>

</div>

</div>

</body>
</html>
