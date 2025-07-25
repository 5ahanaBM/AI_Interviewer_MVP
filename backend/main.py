import tempfile
import os
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.parser import extract_text_from_pdf, extract_structured_info, categorize_skills
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from rag.vectorstore import QuestionVectorStore
from rag.question_gen import QuestionSelector, generate_conversational_question
from rag.chat_session import ChatSession

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize on startup
vector_store = QuestionVectorStore(data_path="data/questions.json")
vector_store.build_index()

selector = QuestionSelector(vector_store)

# Temporary in-memory session store
active_sessions: dict = {}

# Dummy data for vector store test
sample_questions = [
    "What is a neural network?",
    "Explain how FAISS works.",
    "How does a transformer architecture operate?",
    "What is dropout in deep learning?",
]

# Define request schema
class QueryRequest(BaseModel):
    question: str

# Build FAISS index once on app startup
embedding_model = OpenAIEmbeddings()
doc_vectors = FAISS.from_texts(sample_questions, embedding_model)

@app.get("/")
def root():
    return {"status": "API running", "faiss_index_size": doc_vectors.index.ntotal}

@app.post("/query")
def query_faiss(req: QueryRequest):
    """
    Accepts a question string and returns top 2 similar questions from FAISS index.
    """
    results = doc_vectors.similarity_search(req.question, k=2)
    return {"input": req.question, "matches": [r.page_content for r in results]}

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts a resume PDF, extracts text, and optionally returns structured info.
    """
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    raw_text = extract_text_from_pdf(tmp_path)
    structured_data = extract_structured_info(raw_text)

    if structured_data and "skills" in structured_data:
        structured_data["categorized_skills"] = categorize_skills(structured_data["skills"])

    return {
        "raw_text": raw_text[:500],  # preview only
        "structured_info": structured_data
    }

@app.get("/search_questions")
def search_questions(query: str):
    """
    Given a skill/topic, return top matching technical questions.
    """
    results = vector_store.search(query)
    return {"query": query, "matches": results}

@app.post("/generate_questions")
def generate_questions(payload: dict):
    """
    Accepts a list of skills and returns a shortlist of contextual questions.
    Expected format: { "skills": ["Python", "LangChain", "AWS"] }
    """
    skills = payload.get("skills", [])
    if not skills:
        return {"error": "No skills provided."}
    
    questions = selector.select_relevant_questions(skills)
    return {"questions": questions}

@app.post("/chat_question")
def chat_question(payload: dict):
    """
    Converts a technical question into conversational form or follow-up question.

    Expected:
    {
        "question": "What is a neural network?",
        "previous_answer": "It's a layered architecture used in ML."
    }
    """
    q = payload.get("question", "")
    prev = payload.get("previous_answer", "")

    if not q:
        return {"error": "Missing base question"}

    conversational = generate_conversational_question(q, prev)
    return {"chat_question": conversational}

@app.post("/start_session")
def start_session(payload: dict):
    """
    Initializes a new session. Provide: { "session_id": "abc123", "skills": [...] }
    """
    session_id = payload.get("session_id")
    skills = payload.get("skills", [])
    if not session_id or not skills:
        return {"error": "session_id and skills are required"}

    session = ChatSession(skills=skills, vector_store=vector_store)
    active_sessions[session_id] = session
    first_prompt = session.get_next_prompt()
    return {"prompt": first_prompt}

@app.post("/next_question")
def next_question(payload: dict):
    """
    Continues session with user response. Provide: { "session_id": "abc123", "user_input": "..." }
    """
    session_id = payload.get("session_id")
    user_input = payload.get("user_input", "")

    session = active_sessions.get(session_id)
    if not session:
        return {"error": "Invalid session ID"}

    if session.is_finished():
        return {"message": "Interview complete.", "summary": session.chat_history}

    next_prompt = session.get_next_prompt(user_input)
    return {"prompt": next_prompt}