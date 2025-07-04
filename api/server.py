import os 
import sys # Used for sys.exit()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .config import settings

from . import models
from .database import  init_db
from api.routers import auth, category, transaction


from fastapi.middleware.cors import CORSMiddleware
CORS_ORIGINS = settings.origins
 
from .logger import create_info_logger
server_logger = create_info_logger("Server Logger")

@asynccontextmanager
async def lifespan(app: FastAPI):
    server_logger.info("Server is starting...")
    init_db()
    yield  


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # List of allowed origins
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"],    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],    # Allow all headers (including Authorization header for JWTs)
)

@app.get("/api")
def home():
    return {"message": "FastAPI is running"}
print("--------------------------------")

server_logger.info("Loading Auth Router")
app.include_router(auth.router)
server_logger.info("Auth Router Loaded")
print("--------------------------------")

server_logger.info("Loading Category Router")
app.include_router(category.router)
server_logger.info("Category Router Loaded")
print("--------------------------------")

server_logger.info("Loading Transaction Router")
app.include_router(transaction.router)
server_logger.info("Transaction Router Loaded")
print("--------------------------------")

# Serve static files

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist")

# Add a check for the dist folder's presence
if not os.path.isdir(DIST_DIR):
    print(f"ERROR: The 'dist' folder was not found at '{DIST_DIR}'.")
    print("Please ensure you have built the frontend project (e.g., by running 'npm run build:frontend').")
    sys.exit(1) # Exit with an error code

# Serve static files only if the dist directory exists
app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="dist")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(".server:app", host="0.0.0.0", port=8000, reload=True)
