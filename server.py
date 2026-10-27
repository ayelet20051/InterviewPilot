
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from agent import InterviewAgent


app = FastAPI(title="InterviewPilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = InterviewAgent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/api/start", response_model=ChatResponse)
def start_interview():
    response = agent.start()
    return ChatResponse(response=response)


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = agent.answer(request.message)
    return ChatResponse(response=response)


@app.get("/api/health")
def health():
    return {"status": "ok"}
