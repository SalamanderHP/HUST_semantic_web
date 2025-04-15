import uvicorn
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocketState
import asyncio
from typing import List
from src.services.qa_service import QAService

# Assume create_sparql_query is defined elsewhere and imported
# from your_module import create_sparql_query

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Store active connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: str):
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.send_text(message)
            # Force flush the message
            await websocket.send_bytes(b"")

manager = ConnectionManager()
qa_service = QAService()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections for the question-answering process."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await qa_service.question(data, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket Error: {e}")
        if websocket in manager.active_connections:
            await manager.send_message(websocket, f"Error occurred: {str(e)}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
