from pymongo import AsyncMongoClient

uri = "mongodb+srv://f20240236:*s13634151e*@locosync.r0qmmi1.mongodb.net/?retryWrites=true&w=majority&appName=locosync"
client = AsyncMongoClient(uri)
db = client["carpool"]

# This provides a shared db across all files