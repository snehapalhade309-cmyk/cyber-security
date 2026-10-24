
from flask import Flask, request, jsonify, render_template_string, Response
import pandas as pd
import io
import csv

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB upload limit

COLUMNS = ["date", "incident_type", "severity", "source", "status"]

SAMPLE_DATA = [
    ["2026-01-04", "Phishing", "High", "Email", "Open"],
    ["2026-01-08", "Malware", "Critical", "Endpoint", "Investigating"],
    ["2026-01-12", "Brute Force", "Medium", "Authentication", "Closed"],
    ["2026-01-19", "Phishing", "Medium", "Email", "Closed"],
    ["2026-02-02", "Ransomware", "Critical", "Endpoint", "Open"],
    ["2026-02-07", "Data Breach", "High", "Cloud", "Investigating"],
    ["2026-02-15", "Phishing", "High", "Email", "Closed"],
    ["2026-02-22", "DDoS", "Medium", "Network", "Closed"],
    ["2026-03-03", "Malware", "High", "Endpoint", "Open"],
    ["2026-03-11", "Brute Force", "Low", "Authentication", "Closed"],
    ["2026-03-17", "Data Breach", "Critical", "Cloud", "Investigating"],
    ["2026-03-26", "Phishing", "High", "Email", "Open"],
    ["2026-04-05", "DDoS", "High", "Network", "Closed"],
    ["2026-04-13", "Ransomware", "Critical", "Endpoint", "Open"],
    ["2026-04-20", "Malware", "Medium", "Endpoint", "Closed"],
    ["2026-05-01", "Phishing", "High", "Email", "Investigating"],
    ["2026-05-09", "Brute Force", "Medium", "Authentication", "Open"],
    ["2026-05-18", "Data Breach", "High", "Cloud", "Closed"],
    ["2026-06-02", "Malware", "High", "Endpoint", "Open"],
    ["2026-06-14", "DDoS", "Medium", "Network", "Closed"],
    ["2026-06-21", "Phishing", "Critical", "Email", "Investigating"],
    ["2026-07-06", "Ransomware", "High", "Endpoint", "Open"],
    ["2026-07-19", "Brute Force", "Low", "Authentication", "Closed"],
    ["2026-08-04", "Data Breach", "High", "Cloud", "Open"],
    ["2026-08-16", "Phishing", "Medium", "Email", "Closed"],
    ["2026-09-01", "Malware", "Critical", "Endpoint", "Investigating"],
    ["2026-09-12", "DDoS", "High", "Network", "Open"],
    ["2026-09-25", "Phishing", "High", "Email", "Closed"],
    ["2026-10-03", "Data Breach", "Medium", "Cloud", "Open"],
    ["2026-10-12", "Ransomware", "Critical", "Endpoint", "Investigating"],
]

SEVERITIES = ["Critical", "High", "Medium", "Low"]
STATUSES = ["Open", "Investigating", "Closed"]

df = pd.DataFrame(SAMPLE_DATA, columns=COLUMNS)
df["date"] = pd.to_datetime(df["date"])


# ==================================================
# FRONTEND: HTML + CSS + JAVASCRIPT
# ==================================================

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CyberScope | Security Intelligence Dashboard</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>
:root {
    --bg: #f4f7fc;
    --card: #ffffff;
    --navy: #10172a;
    --muted: #8490a5;
    --blue: #4f6bff;
    --border: #e8edf5;
    --green: #10b981;
    --red: #ef4444;
    --shadow: 0 8px 30px rgba(20, 35, 70, 0.045);
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background: var(--bg);
    color: #202b42;
    font-family: Inter, "Segoe UI", Arial, sans-serif;
}

.sidebar {
    width: 248px;
    position: fixed;
    inset: 0 auto 0 0;
    background: var(--navy);
    color: white;
    padding: 28px 18px;
    z-index: 10;
    overflow-y: auto;
}

.brand {
    font-size: 23px;
    font-weight: 800;
    letter-spacing: -.6px;
    padding: 0 8px;
    margin-bottom: 38px;
}

.brand span {
    color: #7c91ff;
}

.brand-icon {
    color: #8da0ff;
    margin-right: 8px;
}

.nav-label {
    font-size: 10px;
    letter-spacing: 2px;
    color: #7d8ba6;
    padding: 0 10px;
    margin: 25px 0 12px;
}

.nav-link {
    display: block;
    padding: 13px 12px;
    border-radius: 9px;
    margin: 5px 0;
    text-decoration: none;
    color: #b8c2d5;
    font-size: 13px;
    transition: .2s;
}

.nav-link:hover,
.nav-link.active {
    color: white;
    background: #273452;
}

.nav-link.active {
    border-left: 3px solid #8293ff;
}

.sidebar-bottom {
    margin-top: 45px;
    padding: 15px;
    background: #1b2741;
    border-radius: 12px;
    font-size: 12px;
    line-height: 1.8;
    color: #b8c2d5;
}

.sidebar-bottom strong {
    color: #a7b6ff;
}

.main {
    margin-left: 248px;
    padding: 30px;
    max-width: 1800px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 18px;
    margin-bottom: 24px;
}

h1 {
    font-size: 27px;
    margin: 0 0 8px;
    letter-spacing: -.6px;
}

.subtitle {
    color: var(--muted);
    font-size: 13px;
    margin: 0;
    line-height: 1.6;
}

.top-right {
    display: flex;
    align-items: center;
    gap: 12px;
}

.live-badge {
    padding: 10px 14px;
    border: 1px solid #c9f0df;
    background: #e9fbf2;
    color: #087c55;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
}

.dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    margin-right: 6px;
}

.date-label {
    color: #78859b;
    font-size: 12px;
}

.hero {
    padding: 25px 28px;
    border-radius: 16px;
    background: linear-gradient(115deg, #263f9d, #4f6bff 68%, #8293ff);
    color: white;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: "⌁";
    position: absolute;
    right: 35px;
    top: -35px;
    font-size: 170px;
    color: rgba(255,255,255,.09);
    transform: rotate(-15deg);
}

.hero h2 {
    font-size: 21px;
    margin: 0 0 9px;
    position: relative;
    z-index: 1;
}

.hero p {
    margin: 0;
    max-width: 650px;
    color: #e1e7ff;
    font-size: 13px;
    line-height: 1.8;
    position: relative;
    z-index: 1;
}

.section-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin: 27px 0 15px;
    flex-wrap: wrap;
}

.section-heading h2 {
    font-size: 17px;
    margin: 0;
}

.section-heading p {
    margin: 5px 0 0;
    color: var(--muted);
    font-size: 12px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 17px;
}

.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    box-shadow: var(--shadow);
    min-width: 0;
}

.stat-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.stat-title {
    color: var(--muted);
    font-size: 12px;
}

.stat-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    font-size: 17px;
    background: #eef1ff;
}

.stat-value {
    font-size: 30px;
    font-weight: 800;
    margin-top: 15px;
    letter-spacing: -1px;
    color: #1c2941;
}

.stat-note {
    font-size: 11px;
    color: var(--muted);
    margin-top: 8px;
}

.red { color: #e34d59; }
.blue { color: #4f6bff; }
.green { color: #079669; }
.orange { color: #e88a25; }

.panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 22px;
    box-shadow: var(--shadow);
    min-width: 0;
}

.charts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
}

.chart-panel {
    min-width: 0;
}

.chart-panel.full {
    grid-column: 1 / -1;
}

.panel-heading {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 20px;
}

.panel-heading h3 {
    font-size: 14px;
    margin: 0 0 6px;
}

.panel-heading p {
    margin: 0;
    color: var(--muted);
    font-size: 11px;
}

.chart-wrap {
    height: 280px;
    position: relative;
}

.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 18px;
}

input, select, button {
    border: 1px solid #dfe5ef;
    border-radius: 8px;
    padding: 11px 13px;
    font-size: 12px;
    font-family: inherit;
}

input, select {
    background: white;
    color: #26344d;
}

input[type="search"] {
    flex: 1;
    min-width: 190px;
}

button {
    cursor: pointer;
    border: none;
    background: var(--blue);
    color: white;
    font-weight: 600;
    transition: .2s;
}

button:hover {
    filter: brightness(.92);
    transform: translateY(-1px);
}

button.secondary {
    background: #edf0ff;
    color: #3c55ce;
}

button.dark {
    background: #202d45;
    color: white;
}

button:disabled {
    opacity: .55;
    cursor: not-allowed;
    transform: none;
}

.table-meta {
    color: var(--muted);
    font-size: 12px;
}

.table-wrap {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 680px;
}

th {
    text-align: left;
    background: #f7f9fd;
    color: #7b879b;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: .7px;
    padding: 14px 12px;
}

td {
    padding: 15px 12px;
    font-size: 12px;
    border-bottom: 1px solid #edf0f6;
    color: #34415a;
}

tbody tr:hover {
    background: #fafbff;
}

.pill {
    display: inline-block;
    border-radius: 6px;
    padding: 5px 9px;
    font-size: 10px;
    font-weight: 700;
    white-space: nowrap;
}

.sev-critical { background: #ffe5e7; color: #c92c3a; }
.sev-high { background: #fff0df; color: #b96b18; }
.sev-medium { background: #fff7d8; color: #8b7208; }
.sev-low { background: #ddf8eb; color: #087b54; }

.status-open { background: #ffe5e7; color: #c92c3a; }
.status-investigating { background: #e6edff; color: #3957cb; }
.status-closed { background: #ddf8eb; color: #087b54; }

.upload-box {
    border: 1.5px dashed #cbd5e5;
    border-radius: 12px;
    background: #fafbff;
    padding: 22px;
}

.upload-box p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
}

#message {
    margin-top: 14px;
    font-size: 12px;
    line-height: 1.6;
    overflow-wrap: anywhere;
}

.success { color: #07835c; }
.error { color: #d33748; }

.footer {
    text-align: center;
    color: #9aa5b6;
    font-size: 11px;
    padding: 30px 0 10px;
}

@media (max-width: 1100px) {
    .sidebar { width: 205px; }
    .main { margin-left: 205px; padding: 22px; }
    .stats { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 760px) {
    .sidebar {
        position: relative;
        width: 100%;
        height: auto;
        padding: 15px;
    }

    .brand { margin-bottom: 12px; }
    .nav-label, .sidebar-bottom { display: none; }

    .sidebar nav {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }

    .nav-link { padding: 10px; margin: 0; }

    .main {
        margin-left: 0;
        padding: 15px;
    }

    .charts { grid-template-columns: 1fr; }
    .chart-panel.full { grid-column: auto; }
    .hero { padding: 22px; }
    .hero::after { right: -10px; }
}

@media (max-width: 430px) {
    .stats { grid-template-columns: 1fr; }
    .top-right { width: 100%; justify-content: space-between; }
    .chart-wrap { height: 240px; }
}
</style>
</head>

<body>

<aside class="sidebar">
    <div class="brand"><span class="brand-icon">⬡</span>Cyber<span>Scope</span></div>

    <div class="nav-label">MAIN MENU</div>
    <nav>
        <a class="nav-link active" href="#overview">▦ &nbsp; Dashboard</a>
        <a class="nav-link" href="#analytics">◷ &nbsp; Threat Analytics</a>
        <a class="nav-link" href="#records">☷ &nbsp; Incident Records</a>
        <a class="nav-link" href="#upload">⇧ &nbsp; Upload Dataset</a>
    </nav>

    <div class="nav-label">PROJECT</div>
    <a class="nav-link" href="#about">ⓘ &nbsp; About Project</a>

    <div class="sidebar-bottom">
        <strong>PROJECT STATUS</strong><br>
        ● Dashboard running locally<br>
        Python + Flask + Pandas
    </div>
</aside>

<main class="main">

    <header class="topbar">
        <div>
            <h1>Security Intelligence</h1>
            <p class="subtitle">Cybersecurity Incident Data Analysis &amp; Visualization</p>
        </div>

        <div class="top-right">
            <span class="live-badge"><span class="dot"></span>DEMO ENVIRONMENT</span>
            <span class="date-label" id="today"></span>
        </div>
    </header>

    <section class="hero" id="about">
        <h2>Welcome to CyberScope</h2>
        <p>
            Analyze cyber threats, monitor incident severity, identify attack
            patterns, and explore incident records in one interactive dashboard.
            This project demonstrates data analysis and visualization using Python.
            The default records are illustrative sample data, not verified real incidents.
        </p>
    </section>

    <section id="overview">
        <div class="section-heading">
            <div>
                <h2>Dashboard Overview</h2>
                <p>Summary of the currently selected incident records</p>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-top">
                    <span class="stat-title">Total Incidents</span>
                    <span class="stat-icon blue">▤</span>
                </div>
                <div class="stat-value blue" id="total">—</div>
                <div class="stat-note">Matching incident records</div>
            </div>

            <div class="stat-card">
                <div class="stat-top">
                    <span class="stat-title">High / Critical</span>
                    <span class="stat-icon red">⚠</span>
                </div>
                <div class="stat-value red" id="high">—</div>
                <div class="stat-note">Higher-severity incidents</div>
            </div>

            <div class="stat-card">
                <div class="stat-top">
                    <span class="stat-title">Unresolved</span>
                    <span class="stat-icon orange">◷</span>
                </div>
                <div class="stat-value orange" id="open">—</div>
                <div class="stat-note">Open or under investigation</div>
            </div>

            <div class="stat-card">
                <div class="stat-top">
                    <span class="stat-title">Threat Categories</span>
                    <span class="stat-icon green">⌘</span>
                </div>
                <div class="stat-value green" id="types">—</div>
                <div class="stat-note">Distinct attack categories</div>
            </div>
        </div>
    </section>

    <section id="analytics">
        <div class="section-heading">
            <div>
                <h2>Threat Analytics</h2>
                <p>Visual patterns in the selected dataset</p>
            </div>
        </div>

        <div class="charts">
            <div class="panel chart-panel full">
                <div class="panel-heading">
                    <div>
                        <h3>Monthly Incident Trend</h3>
                        <p>Incident volume by month</p>
                    </div>
                </div>
                <div class="chart-wrap"><canvas id="trendChart"></canvas></div>
            </div>

            <div class="panel chart-panel">
                <div class="panel-heading">
                    <div>
                        <h3>Severity Distribution</h3>
                        <p>Breakdown by severity level</p>
                    </div>
                </div>
                <div class="chart-wrap"><canvas id="severityChart"></canvas></div>
            </div>

            <div class="panel chart-panel">
                <div class="panel-heading">
                    <div>
                        <h3>Threat Categories</h3>
                        <p>Comparison of attack types</p>
                    </div>
                </div>
                <div class="chart-wrap"><canvas id="typeChart"></canvas></div>
            </div>

            <div class="panel chart-panel full">
                <div class="panel-heading">
                    <div>
                        <h3>Incident Status</h3>
                        <p>Current workflow status of incidents</p>
                    </div>
                </div>
                <div class="chart-wrap"><canvas id="statusChart"></canvas></div>
            </div>
        </div>
    </section>

    <section id="records">
        <div class="section-heading">
            <div>
                <h2>Incident Records</h2>
                <p>Search and filter the dataset</p>
            </div>
            <span class="table-meta" id="recordCount">Loading records...</span>
        </div>

        <div class="controls">
            <input type="search" id="search" placeholder="Search type, source, or status...">

            <select id="severity">
                <option value="All">All Severities</option>
                <option value="Critical">Critical</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
            </select>

            <select id="status">
                <option value="All">All Statuses</option>
                <option value="Open">Open</option>
                <option value="Investigating">Investigating</option>
                <option value="Closed">Closed</option>
            </select>

            <button onclick="loadDashboard()">Apply Filters</button>
            <button class="secondary" onclick="resetFilters()">Reset</button>
            <button class="dark" onclick="downloadCSV()">Export CSV ↓</button>
        </div>

        <div class="panel">
            <div class="table-wrap">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Incident Type</th>
                            <th>Severity</th>
                            <th>Source</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody id="incidentTable">
                        <tr><td colspan="5">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section id="upload">
        <div class="section-heading">
            <div>
                <h2>Upload Dataset</h2>
                <p>Analyze your own cybersecurity incident CSV file</p>
            </div>
        </div>

        <div class="panel">
            <div class="upload-box">
                <h3>Import CSV Dataset</h3>
                <p>
                    Your CSV must contain these column names:
                    <strong>date, incident_type, severity, source, status</strong>.<br>
                    Accepted severity values: Critical, High, Medium, Low.<br>
                    Accepted statuses: Open, Investigating, Closed.
                </p>

                <input type="file" id="csvFile" accept=".csv">
                <button onclick="uploadCSV()">Upload and Analyze</button>
                <button class="secondary" onclick="resetDataset()">Restore Sample Data</button>

                <div id="message" role="status"></div>
            </div>
        </div>
    </section>

    <footer class="footer">
        CyberScope · Cybersecurity Analytics · College Mini Project
    </footer>
</main>

<script>
let charts = {};
let currentRows = [];
let requestNumber = 0;

document.getElementById("today").textContent =
    new Date().toLocaleDateString(undefined, {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });

function showMessage(text, isError = false) {
    const el = document.getElementById("message");
    el.textContent = text;
    el.className = isError ? "error" : "success";
}

async function loadDashboard() {
    const thisRequest = ++requestNumber;

    const params = new URLSearchParams({
        search: document.getElementById("search").value,
        severity: document.getElementById("severity").value,
        status: document.getElementById("status").value
    });

    try {
        const response = await fetch("/api/dashboard?" + params.toString());
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Dashboard request failed.");
        }

        // Ignore older search responses that arrive late.
        if (thisRequest !== requestNumber) return;

        document.getElementById("total").textContent = data.total;
        document.getElementById("high").textContent = data.high;
        document.getElementById("open").textContent = data.open;
        document.getElementById("types").textContent =
            Object.keys(data.types).length;

        document.getElementById("recordCount").textContent =
            data.total + " matching records";

        currentRows = data.rows;
        displayTable(data.rows);

        renderChart("trendChart", "line", data.months, "#4f6bff");
        renderChart("severityChart", "doughnut", data.severities);
        renderChart("typeChart", "bar", data.types, "#10b981");
        renderChart("statusChart", "bar", data.statuses, "#8b5cf6");

    } catch (error) {
        showMessage("Could not load the dashboard: " + error.message, true);
        console.error(error);
    }
}

function renderChart(canvasId, type, values, color) {
    const canvas = document.getElementById(canvasId);

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    const labels = Object.keys(values);
    const numbers = Object.values(values);

    const palette = [
        "#ef4444", "#f59e0b", "#4f6bff",
        "#10b981", "#8b5cf6", "#06b6d4",
        "#f97316", "#ec4899"
    ];

    const dataset = {
        label: "Incidents",
        data: numbers,
        backgroundColor: type === "doughnut" ? palette : color,
        borderColor: type === "line" ? color : "transparent",
        borderWidth: type === "line" ? 3 : 1,
        borderRadius: type === "bar" ? 6 : 0,
        tension: 0.35,
        fill: false,
        pointRadius: type === "line" ? 4 : 0
    };

    charts[canvasId] = new Chart(canvas.getContext("2d"), {
        type: type,
        data: {
            labels: labels,
            datasets: [dataset]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: type === "doughnut",
                    position: "bottom"
                }
            },
            scales: type === "doughnut" ? {} : {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                }
            }
        }
    });
}

function displayTable(rows) {
    const table = document.getElementById("incidentTable");
    table.replaceChildren();

    if (!rows.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 5;
        td.textContent = "No matching incidents found.";
        tr.appendChild(td);
        table.appendChild(tr);
        return;
    }

    rows.forEach(row => {
        const tr = document.createElement("tr");

        const date = document.createElement("td");
        date.textContent = row.date;
        tr.appendChild(date);

        const type = document.createElement("td");
        type.textContent = row.incident_type;
        tr.appendChild(type);

        const severity = document.createElement("td");
        const severityBadge = document.createElement("span");
        severityBadge.className =
            "pill sev-" + row.severity.toLowerCase();
        severityBadge.textContent = row.severity;
        severity.appendChild(severityBadge);
        tr.appendChild(severity);

        const source = document.createElement("td");
        source.textContent = row.source;
        tr.appendChild(source);

        const status = document.createElement("td");
        const statusBadge = document.createElement("span");
        statusBadge.className =
            "pill status-" + row.status.toLowerCase();
        statusBadge.textContent = row.status;
        status.appendChild(statusBadge);
        tr.appendChild(status);

        table.appendChild(tr);
    });
}

async function uploadCSV() {
    const input = document.getElementById("csvFile");

    if (!input.files.length) {
        showMessage("Please select a CSV file first.", true);
        return;
    }

    const file = input.files[0];

    if (!file.name.toLowerCase().endsWith(".csv")) {
        showMessage("Please select a file with the .csv extension.", true);
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        showMessage("Uploading and validating the dataset...");

        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Upload failed.");
        }

        showMessage(result.message);
        await loadDashboard();

    } catch (error) {
        showMessage(error.message || "Upload failed.", true);
    }
}

async function resetDataset() {
    try {
        const response = await fetch("/api/reset", {method: "POST"});
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not reset dataset.");
        }

        document.getElementById("csvFile").value = "";
        showMessage(result.message);
        resetFilters();
        await loadDashboard();

    } catch (error) {
        showMessage(error.message, true);
    }
}

function resetFilters() {
    document.getElementById("search").value = "";
    document.getElementById("severity").value = "All";
    document.getElementById("status").value = "All";
    loadDashboard();
}

function downloadCSV() {
    if (!currentRows.length) {
        showMessage("There are no records to export.", true);
        return;
    }

    const columns = [
        "date", "incident_type", "severity", "source", "status"
    ];

    const csv = [
        columns.join(","),
        ...currentRows.map(row =>
            columns.map(column => {
                const value = String(row[column] ?? "");
                return '"' + value.replace(/"/g, '""') + '"';
            }).join(",")
        )
    ].join("\r\n");

    const blob = new Blob(["\uFEFF" + csv], {
        type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "cybersecurity_incidents.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(() => URL.revokeObjectURL(url), 1000);
}

let searchTimer;

document.getElementById("search").addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadDashboard, 250);
});

document.getElementById("severity").addEventListener("change", loadDashboard);
document.getElementById("status").addEventListener("change", loadDashboard);

loadDashboard();
</script>
</body>
</html>
"""


# ==================================================
# DATA PROCESSING
# ==================================================

def get_filtered_data():
    global df

    data = df.copy()

    search = request.args.get("search", "").strip()
    severity = request.args.get("severity", "All")
    status = request.args.get("status", "All")

    if search:
        mask = data.astype(str).apply(
            lambda col: col.str.contains(
                search, case=False, regex=False, na=False
            )
        ).any(axis=1)
        data = data[mask]

    if severity != "All":
        data = data[
            data["severity"].str.casefold() == severity.casefold()
        ]

    if status != "All":
        data = data[
            data["status"].str.casefold() == status.casefold()
        ]

    return data


def serialize_rows(data):
    rows = []

    for _, row in data.sort_values("date", ascending=False).iterrows():
        rows.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "incident_type": str(row["incident_type"]),
            "severity": str(row["severity"]),
            "source": str(row["source"]),
            "status": str(row["status"])
        })

    return rows


# ==================================================
# DASHBOARD API
# ==================================================

@app.route("/api/dashboard")
def dashboard_api():
    data = get_filtered_data()

    # Sort monthly labels by actual date, not alphabetically.
    monthly_data = data.assign(
        month=data["date"].dt.to_period("M")
    ).groupby("month").size().sort_index()

    months = {
        period.strftime("%b %Y"): int(count)
        for period, count in monthly_data.items()
    }

    severities = {
        str(key): int(value)
        for key, value in data["severity"].value_counts().items()
    }

    types = {
        str(key): int(value)
        for key, value in data["incident_type"].value_counts().items()
    }

    statuses = {
        str(key): int(value)
        for key, value in data["status"].value_counts().items()
    }

    return jsonify({
        "total": int(len(data)),
        "high": int(
            data["severity"].isin(["High", "Critical"]).sum()
        ),
        "open": int(
            data["status"].isin(["Open", "Investigating"]).sum()
        ),
        "types": types,
        "severities": severities,
        "statuses": statuses,
        "months": months,
        "rows": serialize_rows(data.head(100))
    })


# ==================================================
# CSV UPLOAD API
# ==================================================

@app.route("/api/upload", methods=["POST"])
def upload_api():
    global df

    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({"error": "Please select a CSV file."}), 400

    if not file.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are accepted."}), 400

    try:
        uploaded_df = pd.read_csv(file)

        uploaded_df.columns = [
            str(column).strip().lower()
            for column in uploaded_df.columns
        ]

        if not set(COLUMNS).issubset(uploaded_df.columns):
            return jsonify({
                "error": (
                    "CSV must contain these columns: "
                    "date, incident_type, severity, source, status."
                )
            }), 400

        uploaded_df = uploaded_df[COLUMNS].copy()

        if uploaded_df.empty:
            return jsonify({"error": "The CSV contains no records."}), 400

        uploaded_df["date"] = pd.to_datetime(
            uploaded_df["date"], errors="coerce"
        )

        if uploaded_df["date"].isna().any():
            return jsonify({
                "error": "One or more dates are invalid. Use YYYY-MM-DD format."
            }), 400

        text_columns = ["incident_type", "severity", "source", "status"]

        for column in text_columns:
            uploaded_df[column] = (
                uploaded_df[column].astype("string").str.strip()
            )

        if uploaded_df[text_columns].isna().any().any():
            return jsonify({
                "error": "Incident fields cannot contain empty values."
            }), 400

        if (uploaded_df[text_columns] == "").any().any():
            return jsonify({
                "error": "Incident fields cannot contain blank values."
            }), 400

        uploaded_df["severity"] = (
            uploaded_df["severity"].str.capitalize()
        )
        uploaded_df["status"] = (
            uploaded_df["status"].str.capitalize()
        )

        if not uploaded_df["severity"].isin(SEVERITIES).all():
            return jsonify({
                "error": "Severity must be Critical, High, Medium, or Low."
            }), 400

        if not uploaded_df["status"].isin(STATUSES).all():
            return jsonify({
                "error": "Status must be Open, Investigating, or Closed."
            }), 400

        uploaded_df["date"] = uploaded_df["date"].dt.normalize()

        # Replace the in-memory dataset for this demonstration.
        df = uploaded_df.reset_index(drop=True)

        return jsonify({
            "message": f"Successfully loaded {len(df)} incident records."
        })

    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
        return jsonify({
            "error": f"Could not read the CSV: {error}"
        }), 400

    except Exception:
        app.logger.exception("Unexpected CSV upload error")
        return jsonify({
            "error": "An unexpected error occurred while processing the CSV."
        }), 500


# ==================================================
# RESTORE SAMPLE DATA
# ==================================================

@app.route("/api/reset", methods=["POST"])
def reset_api():
    global df

    df = pd.DataFrame(SAMPLE_DATA, columns=COLUMNS)
    df["date"] = pd.to_datetime(df["date"])

    return jsonify({
        "message": "Sample cybersecurity data has been restored."
    })


# ==================================================
# MAIN WEBSITE
# ==================================================

@app.route("/")
def home():
    return render_template_string(HTML)


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":
    print("=" * 55)
    print("CYBERSCOPE CYBERSECURITY ANALYTICS")
    print("Open: http://127.0.0.1:5000")
    print("Press CTRL+C to stop the server.")
    print("=" * 55)

    # Local college-project demo only.
    app.run(debug=True)

