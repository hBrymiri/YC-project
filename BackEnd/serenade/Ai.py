import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    return OpenAI(api_key=api_key)

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        client = get_client()
        resp = client.responses.create(
            model="gpt-4.1-mini",
            input=req.message,
        )
        return {"reply": resp.output_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")
print("LOADED Ai.py")
