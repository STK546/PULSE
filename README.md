# Voice of Associates (VOA) Console
> People Analytics & Engagement Action Console built for Tech Mahindra.

An interactive Streamlit-based web console for HR Business Partners (HRBPs) and People Analytics teams to ingest, normalize, filter, and analyze employee connect sessions, priority risks, and action items.

---

## Key Features

* **Overview Dashboard**: Get a high-level view of key engagement metrics (Active Connects, High Severity, Avg Risk, Sentiment) alongside dynamic Plotly charts (Volume Timeline, CARES Lever Mix, Severity Mix, Sentiment, and Service Line breakdowns).
* **Priority & Risk Analysis**: Computes a dynamic composite **Risk Score (0–100)** for every connect session based on status, age of unresolved tickets, severity, and sentiment to identify hotspots.
* **Coverage & Themes**: Merges connect logs with secondary thematic observations to plot frequency distributions of action themes with interactive sliders.
* **Action Center**: Tracks owner workload distributions and lists actionable high-risk sessions in a progress-bar-equipped data grid.
* **Insight Library**: Explore a searchable directory of CARES framework levers, descriptions, and standard action playbooks.
* **Data Explorer & Session Inspector**: A comprehensive grid with live search autocompletions and a side-by-side detail card viewer that renders specific query details, action plans, and ownership assignments.

---

## Tech Mahindra Red Design System

The app utilizes a custom design theme (`theme.py`) aligned with the **Tech Mahindra 60-30-10 color guidelines**:
* **60% Warm Neutrals** (`#F6F2EA`): Clarity grey backgrounds to minimize eye strain.
* **30% Blueprint & Anchor Tones** (`#0A0838` / `#4A453D`): Headings, navigation tiles, and sidebar cards.
* **10% Mahindra Red** (`#E31837`): Accent lines, alerts, and priority action buttons.

---

## Architecture & Implementation

### 1. Data Loader & Ingestion ([data_loader.py](file:///c:/Users/profe/Downloads/HR%20P/data_loader.py))
* **Fuzzy Matching**: Matches varying column names (e.g. `BHR Name` vs. `Name BHR`) dynamically.
* **Sequential Artificial Key Mapping**: Assigns sequential primary keys (`1, 2, 3...`) to the connect sessions to maintain database uniqueness.
* **Fallback Resolution**: Builds a double-lookup index using `(BHR Employee ID/Name, Date)` and the original Excel form `ID` to map secondary themes in `"Data_Insight"` back to the correct parent sessions without data duplication.
* **Synthetic Demo Fallback**: Automatically spins up a high-fidelity synthetic demo dataset if the spreadsheet workbooks are missing.

### 2. Streamlit Console ([app.py](file:///c:/Users/profe/Downloads/HR%20P/app.py))
* **State Management**: Persists loaded data across navigation pages in the browser session.
* **Cache Busting**: Employs cache-invalidation functions (`get_dataset_v5()`, `enrich_sessions_v3()`, `load_logo_svg_v3()`) to bypass stale browser states when new columns/data schemas are loaded.
* **Favicon Injector**: base64-encodes the Tech Mahindra logo and forces it into the HTML head using asynchronous Javascript to override React rendering.

---

## Prerequisites & Installation

1. Install Python (v3.8+ recommended) and the required packages:
   ```bash
   pip install streamlit pandas plotly openpyxl
   ```

2. Clone or download this project folder into your local environment:
   ```
   c:\Users\profe\Downloads\HR P\
   ```

---

## Running the Application

1. Open a terminal (PowerShell or Command Prompt) and navigate to the project directory:
   ```powershell
   cd "C:\Users\profe\Downloads\HR P"
   ```

2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

3. Open your browser and navigate to the local URL (usually `http://localhost:8501`).

---

## Source Workbook Structure

The system reads from two spreadsheet sheets in your uploaded workbook (or defaults to `HR_Dashboard_Final.xlsx`):
1. **`Data_Summary`** (Main Connect Logs): Contains BHR details, date of connect, employee bands, service lines, sentiment, status, queries, and action owners.
2. **`Data_Insight`** (Observational Themes): Maps back to the connects using dates and names to outline specific coverage items, severity, and action plans.
