from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Unified Imports
from services.llm_service import call_llm, check_fraud, analyze_quant
from services.session_store import create_session, get_history, add_message, SEBI_DISCLAIMER
from services.quant_data import get_market_data

#databse
from services.database import save_fraud_check, init_db

from datetime import datetime


app = FastAPI(title="ArthDrishti Backend")

@app.on_event("startup")
async def startup_event():
    print("Initializing Database...")
    init_db()

origins = ["http://localhost:3000", "http://localhost:5173" , "https://arthdrishti-frontend.vercel.app",]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 1. PYDANTIC MODELS (Data Contracts)
# ==========================================

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None 
    mode: str = "profiler"  # Toggles between "profiler" and "money_mgmt"

class VoiceChatRequest(ChatRequest):
    language_code: str = "hi-IN" # Defaults to Hindi

class FraudCheckRequest(BaseModel):
    loan_amount: float
    interest_rate: float
    processing_fee: float
    lender_name: str
    source: str
    description: str
    session_id: Optional[str] = None

class QuantRequest(BaseModel):
    stock_name: str
    session_id: Optional[str] = None


# ==========================================
# 2. API ENDPOINTS (The Doors)
# ==========================================

@app.get("/")
async def root():
    return {"status": "ok", "message": "ArthDrishti Backend is running"}

@app.get("/health")
async def health_check():
    """Professional health check endpoint for monitoring."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "ArthDrishti Backend is healthy and running"
    }

# ------------------------------------------
# Door 1: Text Chat (Profiler & Budgeting)
# ------------------------------------------
@app.post("/chat")
async def chat(req: ChatRequest, x_session_id: Optional[str] = Header(None)):
    current_session = req.session_id or x_session_id or create_session()
    
    add_message(current_session, "user", req.message, req.mode)
    chat_history = get_history(current_session)
    
    ai_reply = await call_llm(chat_history)
    add_message(current_session, "assistant", ai_reply, req.mode)
    
    return {
        "session_id": current_session,
        "response": ai_reply
    }

# ------------------------------------------
# Door 2: Voice Chat (Flags TTS for Frontend)
# ------------------------------------------
@app.post("/voice-chat")
async def voice_chat(req: VoiceChatRequest, x_session_id: Optional[str] = Header(None)):
    current_session = req.session_id or x_session_id or create_session()
    
    add_message(current_session, "user", req.message, req.mode)
    chat_history = get_history(current_session)
    
    ai_reply = await call_llm(chat_history)
    add_message(current_session, "assistant", ai_reply, req.mode)
    
    return {
        "session_id": current_session,
        "response": ai_reply,
        "voice": True,
        "language_code": req.language_code
    }

# ------------------------------------------
# Door 3: Fraud Detection Calculator
# ------------------------------------------
@app.post("/fraud-check")
async def fraud_check_endpoint(req: FraudCheckRequest):
    # Convert the Pydantic model into a Python dictionary and send to LLM
    analysis_result = await check_fraud(req.model_dump())
    
    # 9.7: Save the check to the database for persistence/logging
    s_id = req.session_id or "anonymous"
    
    # Safely extract the score and verdict even if the AI failed to format it properly
    score = analysis_result.get("fraud_score", 0.0)
    verdict = analysis_result.get("verdict", "UNKNOWN")
    
    save_fraud_check(s_id, req.model_dump(), float(score), verdict)
    
    return analysis_result

# ------------------------------------------
# Door 4: Quant Market Analysis
# ------------------------------------------
@app.post("/quant-analysis")
async def quant_analysis_endpoint(req: QuantRequest):
    data = get_market_data(req.stock_name)
    
    if not data:
        return {
            "status": "error",
            "response": "Currently, ArthDrishti only supports historical analysis for 'Nifty 50' and 'Sensex'. Please ask about those.",
            "session_id": req.session_id
        }
        
    ai_analysis = await analyze_quant(req.stock_name, data)
    final_response = f"{ai_analysis}\n\n{SEBI_DISCLAIMER}"
    
    return {
        "status": "success",
        "response": final_response,
        "session_id": req.session_id
    }