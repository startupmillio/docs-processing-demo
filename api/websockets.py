from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect

from auth.auth0 import get_payload_ws
from services.vosk import live_transcription_generator


ws_router = APIRouter(prefix="/ws")


@ws_router.websocket("/live/{meeting_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    meeting_id: str,
):
    await websocket.accept()

    userinfo = await get_payload_ws(websocket.cookies.get("session"))

    try:
        await live_transcription_generator(
            websocket, user_id=userinfo["sub"], meeting_id=meeting_id
        )
    except WebSocketDisconnect:
        await websocket.close()
