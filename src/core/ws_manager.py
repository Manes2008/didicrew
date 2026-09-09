import asyncio
import json
from typing import Dict, Set, Any
from fastapi import WebSocket

class WebSocketConnectionManager:
    """
    Quan ly cac ket noi WebSocket de cap nhat trang thai, tien do va streaming logs realtime.
    Ho tro giao tiep an toan da luong (Thread-safe) tu Background Worker toi client.
    """
    def __init__(self):
        # Map: task_id -> Set cac WebSocket dang lang nghe
        self.active_task_connections: Dict[str, Set[WebSocket]] = {}
        # Danh sach toan bo ket noi chung
        self.global_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, task_id: str | None = None):
        await websocket.accept()
        if task_id:
            if task_id not in self.active_task_connections:
                self.active_task_connections[task_id] = set()
            self.active_task_connections[task_id].add(websocket)
        else:
            self.global_connections.add(websocket)

    def disconnect(self, websocket: WebSocket, task_id: str | None = None):
        if task_id and task_id in self.active_task_connections:
            self.active_task_connections[task_id].discard(websocket)
            if not self.active_task_connections[task_id]:
                del self.active_task_connections[task_id]
        else:
            self.global_connections.discard(websocket)

    async def send_to_task(self, task_id: str, message: Dict[str, Any]):
        """Gui du lieu JSON bat dong bo toi tat ca cac client dang theo doi task_id."""
        if task_id in self.active_task_connections:
            dead_sockets = []
            for ws in self.active_task_connections[task_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.disconnect(ws, task_id)

    async def broadcast(self, message: Dict[str, Any]):
        """Phat tin hieu JSON toi toan bo cac client dang ket noi."""
        dead_sockets = []
        for ws in self.global_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead_sockets.append(ws)
        for ws in dead_sockets:
            self.disconnect(ws)

    def send_to_task_threadsafe(self, task_id: str, message: Dict[str, Any], loop: asyncio.AbstractEventLoop):
        """
        Goi tu worker thread de day message ve Event Loop cua FastAPI.
        """
        asyncio.run_coroutine_threadsafe(self.send_to_task(task_id, message), loop)

# Khoi tao instance singleton toan cuc
ws_manager = WebSocketConnectionManager()
