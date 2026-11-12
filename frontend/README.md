# ⚖️ Indian Law Search & RAG Assistant

## 1. What is this project?
This is a web application that helps ordinary Indian citizens understand the law in plain language. Users can ask questions in natural language (or by voice) in English, Hindi, or Malayalam. The application retrieves the exact legal sections from the **Bharatiya Nyaya Sanhita (BNS)** and the **Constitution of India**, and generates a simplified answer.

It uses a **Retrieval-Augmented Generation (RAG)** pipeline. This means the AI is strictly forced to answer *only* using the verified legal database. It will not hallucinate laws. It also features an IPC-to-BNS mapping system for legacy queries and native voice input/output.

## 2. Tech Stack
*   **Frontend:** Next.js (React), Tailwind CSS
*   **Backend:** FastAPI (Python)
*   **Database:** PostgreSQL with `pgvector` extension
*   **AI/LLM:** Google Gemini (`gemini-embedding-001` for embeddings, `flash-lite` for generation)
*   **Voice:** Web Speech API (Browser native)

## 3. File Structure & Purpose

### Backend (`/backend`)
*   `app/main.py`: The entry point for the FastAPI server. Configures CORS and routes.
*   `app/database.py`: Connects to PostgreSQL and manages database sessions.
*   `app/models.py`: Defines the database tables (`Section` table with a 3072-dimension vector column).
*   `app/routers/search.py`: **The Brain of the App.** Handles direct lookups (IPC to BNS mapping), vector search, and talks to the Gemini API.
*   `scripts/fetch_data.py`: Seeds the Constitution articles into the database.
*   `scripts/ingest_bulk_data.py`: Downloads all 358 BNS sections from HuggingFace, generates embeddings, and saves them to the database.
*   `requirements.txt`: Python dependencies.

### Frontend (`/frontend`)
*   `app/page.tsx`: **The Main UI.** Contains the search bar, language dropdown, voice input/output logic, and answer display.
*   `app/layout.tsx`: The global layout and HTML wrapper.
*   `app/globals.css`: Tailwind CSS imports.

## 4. How to Run the Project Locally

**Prerequisites:** 
*   PostgreSQL running with a database named `indianlaw` and the `vector` extension enabled (`CREATE EXTENSION vector;`).
*   Node.js and Python installed.
*   A Google Gemini API Key.

### Step 1: Environment Setup
Create a file named `.env` inside the `backend` folder and add your secrets:

GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/indianlaw

### Step 2: Start the Backend
Open a terminal and run:

cd backend
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

*(The backend will run on http://localhost:8000)*

### Step 3: Start the Frontend
Open a **second** terminal and run:

cd frontend
npm install
npm run dev

*(The frontend will run on http://localhost:3000)*

## 5. Data Sources
*   **BNS 2023:** Sourced from the Hugging Face dataset `GSMS-B/indian-legal-sections-bns-bnss-bsa-2023`.
*   **Constitution of India:** Manual data entry covering Fundamental Rights (Articles 12-32).

## 6. Key Features
*   **Hybrid Search:** Combines exact section-number lookups with semantic vector search.
*   **IPC-to-BNS Mapping:** Automatically translates old IPC queries (e.g., "IPC 302") to the new BNS equivalent (BNS 103).
*   **Voice Accessibility:** Native microphone input and text-to-speech output.
*   **Multilingual:** Supports English, Hindi, and Malayalam.
*   **Caching:** In-memory caching for repeated queries to reduce API latency and save quota.