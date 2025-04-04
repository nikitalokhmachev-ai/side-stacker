import multiprocessing
import uvicorn
from fastapi import FastAPI
from app.api import routes
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import websocket_endpoint
from fastapi.websockets import WebSocket
from uuid import UUID

# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.websocket("/ws/games/{game_id}")
async def websocket_proxy(websocket: WebSocket, game_id: UUID):
    await websocket_endpoint(websocket, game_id)


# Entry point
if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
