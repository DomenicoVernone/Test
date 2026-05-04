<!DOCTYPE html>

<html lang="it">

<head>

<meta charset="UTF-8">
<title>MLOps – Test Plan</title>

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

<h1>Test Plan – MLOps System Validation</h1>

<div class="section">
<h2>1. Introduction</h2>

<p>
This document describes the testing strategy adopted to ensure
the correctness, robustness, and reliability of the MLOps platform.
</p>

<p>
Unlike monolithic systems, a microservices architecture requires
multi-level validation: individual components, service communication,
and overall system behavior.
</p>

<p>
Testing is therefore designed to cover the entire analysis lifecycle,
from MRI input to diagnostic output and interpretation.
</p>

</div>

<div class="section">
<h2>2. Testing Objectives</h2>

<p>
The main goal is to ensure that each system component operates correctly
both in isolation and in integration with other services.
</p>

<ul>
<li>verify correct behavior of microservices</li>
<li>validate the end-to-end workflow</li>
<li>identify errors and edge cases</li>
<li>ensure system stability under load</li>
<li>guarantee data consistency between pipeline and inference</li>
</ul>

</div>

<div class="section">
<h2>3. Testing Levels</h2>

<p>
Testing is organized into multiple levels to detect errors
across different stages of the system.
</p>

<table>

<tr>
<th>Level</th>
<th>Description</th>
</tr>

<tr>
<td>Unit Test</td>
<td>Verification of individual functions or modules in isolation</td>
</tr>

<tr>
<td>Integration Test</td>
<td>Validation of communication between microservices</td>
</tr>

<tr>
<td>System Test</td>
<td>Verification of the complete system in a controlled environment</td>
</tr>

<tr>
<td>End-to-End Test</td>
<td>Full simulation of real user workflow</td>
</tr>

</table>

<p>
This layered approach allows quick identification of error sources
and reduces debugging time.
</p>

</div>

<div class="section">
<h2>4. Functional Tests</h2>

<p>
Functional tests verify that each component produces the expected output
given valid input.
</p>

<table>

<tr>
<th>Test</th>
<th>Description</th>
<th>Expected Result</th>
</tr>

<tr>
<td>User Login</td>
<td>Authentication via API Gateway</td>
<td>Valid JWT token</td>
</tr>

<tr>
<td>MRI Upload</td>
<td>Upload MRI file to the system</td>
<td>File correctly stored</td>
</tr>

<tr>
<td>Pipeline Start</td>
<td>Creation of orchestrator task</td>
<td>Task in pending/running state</td>
</tr>

<tr>
<td>Inference</td>
<td>Execution of KNN classification</td>
<td>Diagnostic class returned</td>
</tr>

<tr>
<td>LLM</td>
<td>Generation of clinical explanation</td>
<td>Coherent textual output</td>
</tr>

</table>

<p>
These tests ensure that the core system functionalities operate correctly
and meet the expected specifications.
</p>

</div>

<div class="section">
<h2>5. End-to-End Tests</h2>

<p>
End-to-end tests represent the most critical level, as they validate
the system as a whole.
</p>

<pre>
Login
   ↓
Upload MRI
   ↓
Nextflow Pipeline
   ↓
Feature Extraction
   ↓
Inference
   ↓
UMAP
   ↓
Explainability
</pre>

<p>
These tests verify:
</p>

<ul>
<li>correct execution sequence</li>
<li>data consistency across services</li>
<li>absence of intermediate errors</li>
</ul>

<p>
This level is essential to detect integration issues not visible
in unit tests.
</p>

</div>

<div class="section">
<h2>6. Performance Tests</h2>

<p>
Performance tests evaluate the system’s ability to handle
computational workloads.
</p>

<table>

<tr>
<th>Test</th>
<th>Description</th>
<th>Objective</th>
</tr>

<tr>
<td>Pipeline Time</td>
<td>Total MRI processing duration</td>
<td>Acceptable execution time</td>
</tr>

<tr>
<td>Parallelization</td>
<td>Concurrent execution of multiple analyses</td>
<td>No significant performance degradation</td>
</tr>

<tr>
<td>GPU Test</td>
<td>FastSurfer CUDA usage</td>
<td>Reduced execution time</td>
</tr>

</table>

<p>
These tests are essential for evaluating system scalability
in real-world scenarios.
</p>

</div>

<div class="section">
<h2>7. Resilience Tests</h2>

<p>
Resilience tests evaluate the system’s ability to handle
errors and abnormal conditions.
</p>

<table>

<tr>
<th>Scenario</th>
<th>Expected Behavior</th>
</tr>

<tr>
<td>Pipeline Error</td>
<td>Immediate interruption (fail-fast)</td>
</tr>

<tr>
<td>Service Unavailable</td>
<td>Error correctly propagated</td>
</tr>

<tr>
<td>Invalid Input</td>
<td>Controlled error handling</td>
</tr>

</table>

<p>
This ensures that the system does not produce inconsistent outputs.
</p>

</div>

<div class="section">
<h2>8. Security Tests</h2>

<p>
Security tests verify endpoint protection and credential management.
</p>

<ul>
<li>JWT token validation</li>
<li>authenticated endpoint access</li>
<li>sensitive data protection</li>
</ul>

</div>

<div class="section">
<h2>9. API Tests</h2>

<p>
APIs are tested using Swagger UI and manual HTTP requests.
</p>

<pre>
http://localhost:8000/docs
</pre>

<p>
Verification includes:
</p>

<ul>
<li>correct JSON responses</li>
<li>appropriate HTTP status codes</li>
<li>input/output validation</li>
</ul>

</div>

<div class="section">
<h2>10. Test Automation</h2>

<p>
To ensure continuous validation, automated testing tools can be integrated:
</p>

<ul>
<li>pytest for backend testing</li>
<li>automated API tests</li>
<li>CI/CD pipelines</li>
</ul>

<p>
Automation enables early detection of regressions.
</p>

</div>

<div class="section">
<h2>11. Validation Metrics</h2>

<p>
Metrics allow objective evaluation of system performance.
</p>

<table>

<tr>
<th>Metric</th>
<th>Description</th>
</tr>

<tr>
<td>Accuracy</td>
<td>Diagnostic model accuracy</td>
</tr>

<tr>
<td>Latency</td>
<td>System response time</td>
</tr>

<tr>
<td>Error rate</td>
<td>Execution error percentage</td>
</tr>

</table>

</div>

<div class="section">
<h2>12. Conclusions</h2>

<p>
The adopted test plan ensures complete and systematic validation
of the MLOps platform.
</p>

<p>
The multi-level approach enables rapid issue identification
and ensures long-term system reliability and stability.
</p>

</div>

</div>

</body>

</html>
