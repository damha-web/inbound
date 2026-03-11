"""
Automation V2 - FastAPI Backend
Marketing Proposal Dashboard API Server
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve paths relative to this file's directory
_BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(_BACKEND_DIR)
load_dotenv(_BACKEND_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import submissions, proposals, email
from models.schemas import LoginRequest, TokenResponse
from services.auth_service import authenticate_admin, create_access_token
from fastapi import HTTPException

app = FastAPI(
    title="DAMHA Automation V2",
    description="마케팅 제안서 자동화 대시보드 API",
    version="2.0.0",
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(submissions.router)
app.include_router(proposals.router)
app.include_router(email.router)


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    if not authenticate_admin(req.username, req.password):
        raise HTTPException(status_code=401, detail="잘못된 사용자명 또는 비밀번호")
    token = create_access_token(data={"sub": req.username})
    return TokenResponse(access_token=token)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
