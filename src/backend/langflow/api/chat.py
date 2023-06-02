from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    status,
)
from logging import StreamHandler
import asyncio
import logging

from langflow.api.chat_manager import ChatManager
from langflow.utils.logger import logger
import sys
import asyncio

router = APIRouter()
chat_manager = ChatManager()

from fastapi import BackgroundTasks

# This will be our list of connected clients
connected_clients = []

class WebsocketWriter:
    def __init__(self, connected_clients, original_stream, filepath=None):
        self.connected_clients = connected_clients
        self.original_stream = original_stream
        self.filepath = filepath

    def write(self, message: str):
        self.original_stream.write(message)
        if self.filepath:
            with open(self.filepath, 'a') as f:
                f.write(message)
        try:
            if message.strip() != "":  # exclude simple newlines
                for client in self.connected_clients:
                    client["tasks"].append(asyncio.create_task(client["websocket"].send_json({'type':'log','message':message})))
        except Exception as e:
            pass

    def flush(self):
        self.original_stream.flush()

    async def drain(self):
        for client in self.connected_clients:
            await asyncio.gather(*client["tasks"], return_exceptions=True)
            client["tasks"] = []

original_stdout = sys.stdout
original_stderr = sys.stderr
sys.stdout = WebsocketWriter(connected_clients, original_stdout, 'stdout.log')
sys.stderr = WebsocketWriter(connected_clients, original_stderr, 'stderr.log')

class SafeWebSocket:
    def __init__(self, websocket):
        self.websocket = websocket
        self.log_tasks = []
        self.closed = False
        
    async def send(self, message):
        await asyncio.gather(*self.log_tasks, return_exceptions=True)
        if not self.closed:
            await self.websocket.send(message)

    async def send_json(self, data):
        if not self.closed:
            if isinstance(data, dict) and data.get('type') == 'log':
                task = asyncio.create_task(self.websocket.send_json(data))
                self.log_tasks.append(task)
            else:
                await self.websocket.send_json(data)

    async def close(self, code=None, reason=None):
        if not self.closed:
            self.closed = True
            await asyncio.gather(*self.log_tasks, return_exceptions=True)
            await self.websocket.close(code, reason)
            
    def __getattr__(self, attr):
        # This will forward any method calls not explicitly defined on SafeWebSocket
        # to the underlying WebSocket instance.
        return getattr(self.websocket, attr)

@router.websocket("/chat/{client_id}")
async def websocket_endpoint(client_id: str, websocket: WebSocket):
    """Websocket endpoint for chat."""
    # add websocket to connected clients
    client_info = {"websocket": websocket, "tasks": []}
    connected_clients.append(client_info)
    
    ws = SafeWebSocket(websocket)

    try:
        await chat_manager.handle_websocket(client_id, ws)
    except WebSocketException as exc:
        logger.error(exc)
        await ws.send_json({"error": str(exc)})
        await ws.close(code=status.WS_1011_INTERNAL_ERROR, reason=str(exc))

    except WebSocketDisconnect as exc:
        logger.error(exc)
        await ws.close(code=status.WS_1000_NORMAL_CLOSURE, reason=str(exc))
    finally:
        # Wait for all log messages to be sent
        await sys.stdout.drain()
        await sys.stderr.drain()
        # remove websocket from connected clients
        connected_clients.remove(client_info)
