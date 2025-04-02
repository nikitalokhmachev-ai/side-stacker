import multiprocessing
import uvicorn
from fastapi import FastAPI
from app.api import routes
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

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

# Entry point
if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, workers=1)
