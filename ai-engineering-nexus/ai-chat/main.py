import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.responses import StreamingResponse
import json
from models import get_model_stream
import logging
logger = logging.getLogger("uvicorn") # Hooks into FastAPI's default logger

app = FastAPI()

running_tasks = {}

# This is just a simple UI to test your websocket
html = """
<!DOCTYPE html>
<html>
    <body>
        <h1>WebSocket Echo</h1>
        <input type="text" id="messageText" autocomplete="off"/>
        <button onclick="sendMessage()">Send</button>
        <ul id='messages'></ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws1");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                const msg = JSON.parse(event.data);
                if (msg.type === "start") {
                    // Create the new list item once
                    currentMessageElement = document.createElement('li');
                    messages.appendChild(currentMessageElement);
                } else if(msg.type === "thinking"){
                    // Append text to the SAME list item
                    currentMessageElement = document.createElement('li');
                    messages.appendChild(currentMessageElement);    
                    currentMessageElement.textContent += msg.data;
                } else if(msg.type === "clear"){
                    messages.replaceChildren();
                } else {
                    // Append text to the SAME list item
                    currentMessageElement.textContent += msg.data;
                } 
            };
            function sendMessage() {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# YOUR TASK: Implement the @app.websocket("/ws") route here
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     # Instead of print()
#     logger.info("New connection established")
#     try:
#         while True:
#             question = await websocket.receive_text()
#             try:
#                 question_dict = json.loads(question)
#                 model = question_dict['model']
#                 question = question_dict['question']
#             except json.JSONDecodeError:
#                 model = "gemini-2.5-flash"
#                 question = question
#             try:
#                 await websocket.send_json({"type": "start"})
#                 async for token in get_model_stream(model, question):
#                     await websocket.send_json({"type": "content", "data": token})
#             except Exception as e:
#                 await websocket.send_json({"type": "error", "data": "AI is sleepy. Try again!"})
#     except WebSocketDisconnect:
#         logger.error(f"Client Disconnected!")

@app.post("/ask/stream")
async def ask_stream(payload: dict):
    # 1. Extract data
    question = payload.get("question")
    model = payload.get("model", "gemini-2.5-flash")

    # 2. Define the SSE wrapper
    async def sse_wrapper():
        # Reuse your model logic
        async for token in get_model_stream(model, question):
            # SSE requirement: 'data: <payload>\n\n'
            # We send JSON to match our WebSocket format
            message = json.dumps({"type": "content", "data": token})
            yield f"data: {message}\n\n"
        
        # Signal completion
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    # 3. Return the stream
    return StreamingResponse(sse_wrapper(), media_type="text/event-stream")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

# Create a single shared instance
manager = ConnectionManager()

async def process_ai_response(websocket, question):
    try:
        question_dict = json.loads(question)
        model = question_dict['model']
        question = question_dict['question']
    except json.JSONDecodeError:
        model = "gemini-2.5-flash"
        question = question
    try:
        await websocket.send_json({"type": "start"})
        async for token in get_model_stream(model, question):
            await websocket.send_json({"type": "content", "data": token})
    except Exception as e:
        await websocket.send_json({"type": "error", "data": "AI is sleepy. Try again!"})

@app.websocket("/ws1")
async def ask(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            question = await websocket.receive_text()
            if websocket in running_tasks:
                running_tasks[websocket].cancel()
                try:
                    await running_tasks[websocket]
                except asyncio.CancelledError:
                    pass # We expected this!
                await websocket.send_json({"type": "clear"})
                logger.info("Previous task cancelled for new user input")
            new_task = asyncio.create_task(
                process_ai_response(websocket, question)
            )
            running_tasks[websocket] = new_task
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if websocket in running_tasks:
            running_tasks[websocket].cancel()
    finally:
        manager.disconnect(websocket)
        if websocket in running_tasks:
            running_tasks[websocket].cancel()