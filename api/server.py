from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from . import models
from .database import create_database_if_not_exists, create_tables_if_not_exists
from api.routers import auth, category, transaction

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_if_not_exists()
    create_tables_if_not_exists()
    yield  

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(transaction.router)



@app.get("/api")
def home():
    return {"message": "FastAPI is running"}

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("   .server:app", host="0.0.0.0", port=8000, reload=True)
