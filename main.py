from fastapi import FastAPI

app = FastAPI()

# Include other routes here
# using app.include_router()

@app.get("/")
async def base_handler(): #throughout code path operators will be suffixed by _handler
    return "Eventually you can hope to get some documentation from this endpoint"



