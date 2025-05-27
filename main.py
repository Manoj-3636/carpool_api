from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from users import login
from users.exceptions import InvalidToken

app = FastAPI()

# Include other routes here
# using app.include_router()
origins = [
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(InvalidToken)
async def InvalidToken_exception_handler(request:Request,exc:InvalidToken):
    return JSONResponse(
        status_code=401,
        content={
            "detail":exc.detail,
            "received id": exc.id_token
        },
    )

app.include_router(login.router)

@app.get("/")
async def base_handler():
    return "Eventually you can hope to get some documentation from this endpoint"



