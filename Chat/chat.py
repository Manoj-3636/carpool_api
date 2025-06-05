from typing import Annotated

from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect, status

from Chat.classes import GlobalConnectionManager
from rides.models import RideDB
from users.models import UserDatabase
from dependencies import get_current_user
from db import db

rides_collection = db["rides"]

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

gcm = GlobalConnectionManager()


@router.websocket("/{ride_id}")
async def websocket_handler(websocket: WebSocket, ride_id: str,
                            current_user: Annotated[UserDatabase, Depends(get_current_user)]):
    ride_details = await rides_collection.find_one({"_id": ride_id})
    ride_details = RideDB(**ride_details)
    if not ride_details:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if not current_user.id in ride_details.users:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    connection_manager = gcm.get_connection_manager(ride_id)
    # TODO Check if user has permission to connect to this ride
    await connection_manager.connect(current_user.id, websocket)
    print(len(connection_manager.active_connections))
    # Send old messages

    for message in (await connection_manager.get_messages()):
        await websocket.send_json(message)



    try:
        while True:
            data = await websocket.receive_json()
            await connection_manager.broadcast(current_user.id, data["message"], "user_message")

    except WebSocketDisconnect:
        connection_manager.disconnect(current_user.id)
