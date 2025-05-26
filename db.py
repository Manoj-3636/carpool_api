from pymongo import AsyncMongoClient

client = AsyncMongoClient("mongodb://localhost:27017/")
db = client["carpool"]

# This provides a shared db across all files