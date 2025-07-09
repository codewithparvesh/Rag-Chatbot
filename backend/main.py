from fastapi import FastAPI, UploadFile, File
import os
from db import save_to_faiss, search_faiss
from model import generate_answer
from fastapi.middleware.cors import CORSMiddleware
import os
import pandas as pd
from datetime import datetime
from pydantic import BaseModel

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensures folder exists at runtime

app = FastAPI()

# Enable CORS to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    feedback: str  # like, dislike, neutral


UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")  # Root endpoint to check if the backend is running
async def root():
    return {"message": "Backend is running!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    save_to_faiss(file_path)
    return {"message": f"File '{file.filename}' uploaded and processed."}

@app.get("/ask/")
async def ask_question(query: str):
    try:
        context = search_faiss(query)
        answer = generate_answer(query, context)
        return {"question": query, "answer": answer, "context": context}
    except Exception as e:
        return {"error": str(e)}

@app.post("/feedback/")
async def submit_feedback(feedback: FeedbackRequest):
    if feedback.feedback not in ["like", "dislike", "neutral"]:
        return {"error": "Feedback must be 'like', 'dislike', or 'neutral'"}

    # Create DataFrame from feedback
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "question": feedback.question,
        "answer": feedback.answer,
        "feedback": feedback.feedback
    }

    df_new = pd.DataFrame([feedback_data])
    FEEDBACK_FILE = "feedback.xlsx"
    # Append or create Excel file
    if os.path.exists(FEEDBACK_FILE):
        df_existing = pd.read_excel(FEEDBACK_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(FEEDBACK_FILE, index=False)
    else:
        df_new.to_excel(FEEDBACK_FILE, index=False)

    return {"message": "Feedback saved to Excel", "data": feedback_data}