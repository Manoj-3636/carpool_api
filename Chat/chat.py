from typing import Annotated

from fastapi import APIRouter,WebSocket,Depends,WebSocketDisconnect

from Chat.classes import GlobalConnectionManager
from users.models import UserDatabase
from dependencies import get_current_user
router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

gcm = GlobalConnectionManager()

@router.websocket("/{ride_id}")
async def websocket_handler(websocket:WebSocket,ride_id:str,current_user:Annotated[UserDatabase,Depends(get_current_user)]):
    connection_manager = gcm.get_connection_manager(ride_id)
    # TODO Check if user has permission to connect to this ride
    await connection_manager.connect(current_user.id,websocket)
    print(len(connection_manager.active_connections))

    try:
        while True:
            message = await websocket.receive_json()
            await connection_manager.broadcast(current_user.id,message)
            print(message)

    except WebSocketDisconnect:
        connection_manager.disconnect(current_user.id)
