# AI Interviewer

An AI-powered interview assistant that analyzes resumes, generates contextual technical questions, and conducts conversational mock interviews with feedback.

---

## Project Structure

* **Frontend**: React.js (chat UI)
* **Backend**: FastAPI (Python)
* **LLM Provider**: OpenAI (GPT-3.5-turbo)
* **Vector Store**: FAISS (in-memory)
* **Skill Extraction**: LLM-based parsing from raw resume text

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ai-interviewer.git
cd ai-interviewer
```

### 2. Backend Setup (FastAPI)

#### a. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### b. Install Dependencies

```bash
pip install -r requirements.txt
```

#### c. Set OpenAI API Key

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_key_here
```

#### d. Run the Backend

```bash
uvicorn main:app --reload
```

By default, the backend runs on `http://localhost:8000`.

### 3. Frontend Setup (React)

#### a. Navigate to `frontend/`

```bash
cd frontend
```

#### b. Install Dependencies

```bash
npm install
```

#### c. Start React App

```bash
npm run dev  # or npm start depending on tooling
```

Frontend should now be available on `http://localhost:5173`.

---

## Core Features

### Resume Upload

* Supports PDF and text files
* Extracts skills using OpenAI's LLM (chat API) for structured info

### Question Generation

* Vector similarity search on technical questions using FAISS
* Conversational phrasing via OpenAI chat completion API
* Follow-up questions dynamically generated based on user's last answer

### Interview Flow

* Starts with a greeting, waits for candidate readiness
* Asks a base question followed by a follow-up
* Concludes with a score summary and LLM-generated feedback

### Summary & Feedback

* Total questions and follow-ups shown
* Skills inferred from session tagged
* Personalized feedback and scoring using an LLM based on entire chat history

---

## Design Decisions

* **LLM-Driven Parsing**: Skill and experience extraction is performed via structured prompts to an OpenAI chat model, which returns JSON. This allows for flexible and accurate parsing without relying on regex or classical NLP pipelines.
* **Modular Prompting**: Prompt creation is abstracted so question generation and feedback remain adaptable.
* **Minimal External Dependencies**: No heavy resume parsing libraries used beyond PDF text extraction (PyMuPDF).
* **FAISS**: Fast and lightweight vector retrieval without requiring external DBs.
* **Session-based State**: Each chat session is handled in-memory; suitable for demo-scale interviews.
* **Frontend Simplicity**: ChatBox uses native React state for simplicity; no Redux or heavy state mgmt.
* **UI Enhancements**: Enlarged and centered chat window for better laptop experience, multiline input box for comfortable answering, auto-scroll to latest message, and clean layout using native styling.

---

## Trade-offs

* LLM-based parsing offers richer context understanding but may occasionally hallucinate or misformat JSON.
* There's a dependency on external API availability and cost.
* No persistent DB or user login to maintain candidate history.
* Question variety and tagging are handcrafted; could be extended with real-world job datasets.
* Stateless vector store — not optimized for large-scale use cases.

---

## Future Improvements

* Role-specific interview paths
* Admin view with candidate analytics
* Configurable interview length/difficulty
* Audio/video integration for realism
* Better feedback rubric using rubric chaining
