from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import run_calendar_agent

app = FastAPI(title="AI Calendar Agent")

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Pass the query to our agent logic
        response_text = run_calendar_agent(request.query)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)