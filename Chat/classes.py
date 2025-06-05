from typing import Dict
import asyncio
from fastapi import WebSocket
from db import db

message_collection = db["messages"]

# Validation of who sent the message has to be done on the backend itself or else
# a html request can be crafted to fool the server
class ConnectionManager:
    def __init__(self,ride_id):
        # Key is userid
        self.active_connections:Dict[str,WebSocket] = {}
        self.ride_id = ride_id

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        # Close existing connection if user already connected
        # FIXME Handle multiple connections from the same user gracefully
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].close(code=1000, reason="New connection established")
            except:
                pass  # Connection might already be dead

        # Set new connection
        self.active_connections[user_id] = websocket
        await self.broadcast_server(user_id,"connect")
        print(user_id)

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            await self.broadcast_server(user_id,"disconnect")
        # Don't call close() here - connection is already closed

    async def broadcast(self,sender_user_id:int,message:str,type_of):
        dead_connections = []
        print(self.active_connections)
        message_res = {
            "sender": sender_user_id,
            "type": type_of,
            "message": message,
        }
        for user_id in self.active_connections:
            # if sender_user_id == user_id:
            #     continue

            try:

                await self.active_connections[user_id].send_json(message_res)
            except Exception as e:
                dead_connections.append(user_id)

        asyncio.create_task(self.store_message(message_res))
        for dead_user_id in dead_connections:
            await self.disconnect(dead_user_id)



    async def store_message(self,message_res:Dict[str,str]):
        # Id will be made automatically no need to care much about that
        message_res["ride_id"] = self.ride_id
        await message_collection.insert_one(message_res)


    async def get_messages(self):
        cursor = message_collection.find(filter={"ride_id":self.ride_id},projection={"_id":0})
        return [message async for message in cursor]

    async def broadcast_server(self, message:str,type_of:str):
        dead_connections = []
        print(self.active_connections)
        for user_id in self.active_connections:
            if message == user_id:
                continue

            try:
                message_res = {
                    "sender": 0,
                    "type": type_of,
                    "message": message,
                }
                await self.active_connections[user_id].send_json(message_res)
            except Exception as e:
                dead_connections.append(user_id)

        for dead_user_id in dead_connections:
            await self.disconnect(dead_user_id)


class GlobalConnectionManager:
    def __init__(self):
        # Key is the ride_id and the corresponding value is the connection manager for that key
        self._rooms:Dict[str,ConnectionManager] = {}

    def get_connection_manager(self,ride_id):
        if ride_id not in self._rooms:
            print("Not found creating new")
            self._rooms[ride_id] = ConnectionManager(ride_id)

        return self._rooms[ride_id]




