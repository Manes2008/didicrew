from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.core.ws_manager import ws_manager

router = APIRouter(tags=["WebSocket Realtime"])

@router.websocket("/ws/tasks/{task_id}")
async def websocket_task_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket Endpoint ket noi real-time theo task_id.
    Client (Next.js / React / Rust) lang nghe tien do, logs va ket qua cua task_id tai day.
    """
    await ws_manager.connect(websocket, task_id)
    try:
        # Gui message xac nhan ket noi thanh cong
        await websocket.send_json({
            "event": "connected",
            "task_id": task_id,
            "message": f"Da ket noi WebSocket thanh cong toi task: {task_id}"
        })
        while True:
            # Lang nghe message tu client (neu co ping/pong hoac lenh huy)
            data = await websocket.receive_text()
            # Xu ly message tiep nhan tu client neu can thiet
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, task_id)
    except Exception:
        ws_manager.disconnect(websocket, task_id)
