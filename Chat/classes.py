from typing import Dict

from fastapi import WebSocket

# Validation of who sent the message has to be done on the backend itself or else
# a html request can be crafted to fool the server
class ConnectionManager:
    def __init__(self):
        # Key is userid
        self.active_connections:Dict[str,WebSocket] = {}

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
        await self.broadcast(0,user_id,"connect")
        print(user_id)

    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            await self.broadcast(0,user_id,"disconnect")
        # Don't call close() here - connection is already closed

    async def broadcast(self,sender_user_id:int,message:str,type_of):
        dead_connections = []
        print(self.active_connections)
        for user_id in self.active_connections:
            # if sender_user_id == user_id:
            #     continue

            try:
                await self.active_connections[user_id].send_json({
                    "sender":sender_user_id,
                    "type":type_of,
                    "message":message,
                })
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
            self._rooms[ride_id] = ConnectionManager()

        return self._rooms[ride_id]




