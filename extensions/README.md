# SuperDocs HR Composer & Document Assembly

*Built by Ashfaq ur Rahman for the SuperDocs Engineering Task.*

![HR Composer UI Screenshot](./path-to-your-screenshot.png) 
*(Note: Replace this image path with an actual screenshot of your web UI)*

## Overview
This repository contains two decoupled, deterministic microservices built on a shared SDK:
1. **HR Composer (Word Add-in):** A React/FastAPI application for HR teams to generate, approve, and export jurisdiction-specific offer letters (California, UK, Standard).
2. **Document Assembly (Microservice):** A backend engine for Legal/Finance teams to programmatically compose multi-section contracts from a deterministic clause library.

Both services enforce a strict **Human-in-the-Loop** state machine, halting at `REVIEW_REQUIRED` and strictly blocking physical exports until explicit human approval is granted.

## Prerequisites
* Python 3.9+
* Node.js v18+

## Quick Start (Local Setup)

**1. Install Python Dependencies**
Navigate to the `hr-composer` directory, create a virtual environment, and install the required native libraries:
```bash
cd extensions/Ashfaq-codez/hr-composer
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn pydantic python-docx fpdf2 httpx
2. Install Frontend Dependencies

Bash
cd frontend
npm install
Running the Application
You will need two terminal windows to run the full Word Add-in stack.

Terminal 1: Start the FastAPI Backend

Bash
cd extensions/Ashfaq-codez/hr-composer
source .venv/bin/activate
PYTHONPATH=.:../superdocs-client uvicorn backend.main:app --reload --port 8000
Terminal 2: Start the React Frontend

Bash
cd extensions/Ashfaq-codez/hr-composer/frontend
npm run dev
Open http://localhost:3000 in your browser to access the Composer UI.

Running the Automated CLI Demo
If you prefer to see the pipeline (Upload -> Compose -> Halt for Review -> Approve -> Export Real DOCX/PDF) without the UI, run the E2E script:

Bash
cd extensions/Ashfaq-codez/hr-composer
source .venv/bin/activate
python scripts/demo.py
Running the Test Suite (61 Passing Tests)
The system is heavily tested for strict state-machine compliance and artifact integrity. Run the following commands from their respective directories:

Phase 1 & 5: SDK & Physical File Generation

Bash
cd extensions/Ashfaq-codez/superdocs-client
python3 -m unittest discover tests
Phase 2: Document Assembly Logic

Bash
cd use-cases/Ashfaq-codez/doc-assembly
PYTHONPATH=.:../../../extensions/Ashfaq-codez/superdocs-client python3 -m unittest discover tests
Phase 3: HR Composer Backend

Bash
cd extensions/Ashfaq-codez/hr-composer
PYTHONPATH=.:../superdocs-client python3 -m unittest discover tests
Phase 4: HR Composer Frontend

Bash
cd extensions/Ashfaq-codez/hr-composer/frontend
npm run test
Core Architectural Decisions
Deterministic Legal Templating: LLMs are intentionally omitted from the legal clause assembly. Jurisdiction mappings and clauses are injected using deterministic string.Template logic to prevent hallucinated terms.

Pluggable SDK Architecture: The domain layer relies on SuperDocsClientInterface. During tests, it uses MockSuperDocsClient (in-memory, ultrafast). At runtime, it uses LocalSuperDocsClient (generates physical OpenXML and PDF binaries using python-docx and fpdf2).

Safe Local Artifacts: Physical artifacts are stored securely in a temporary runtime/ directory and served via a path-sanitized GET endpoint to prevent directory traversal attacks.


***

**Final Action Checklist:**
1. Save this file as `README.md`.
2. Take a screenshot of your beautiful new web UI (showing the form or the generated download buttons) and save it in the same folder.
3. Update the `![HR Composer UI Screenshot](./path-to-your-screenshot.png)` line to match your image file's exact name.
4. Stage, commit, and push this README to your repository.