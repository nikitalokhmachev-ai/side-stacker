import multiprocessing
import uvicorn
from fastapi import FastAPI
from .api import routes
from .database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI()
app.include_router(routes.router)

# Entry point
if __name__ == "__main__":
    cpu_count = multiprocessing.cpu_count()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, workers=cpu_count)
