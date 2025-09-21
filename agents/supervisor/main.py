import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import logging
from fastapi import FastAPI, HTTPException, logger
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from .graph.graph import SupervisorGraph
import logging
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supervisor_graph = SupervisorGraph()


class MessageRequest(BaseModel):
    message: str

@app.post("/agent/chat")
async def handle_message(request: MessageRequest):
    try:
     response = await supervisor_graph.run(request.message)
     logging.info(f"Response: {response}")
     return {"response": response}
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)