import os 
import sys # Used for sys.exit()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from api.core.config import settings

from api import models
from api.database.session import  init_db
from api.routers import auth, category, transaction, admin, budget, seed_data, subscription, investment, dashboard, transaction, user, account, investment_price

from fastapi.middleware.cors import CORSMiddleware
CORS_ORIGINS = settings.origins
 
from api.utils.logger import create_info_logger
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
print(CORS_ORIGINS)

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

server_logger.info("Loading Budget Router")
app.include_router(budget.router)
server_logger.info("Budget Router Loaded")
print("--------------------------------")

server_logger.info("Loading Seeding Router")
app.include_router(seed_data.router)
server_logger.info("Seeding Router Loaded")
print("--------------------------------")

server_logger.info("Loading Subscription Router")
app.include_router(subscription.router)
server_logger.info("Subscription Router Loaded")
print("--------------------------------")

server_logger.info("Loading Investment Router")
app.include_router(investment.router)
server_logger.info("Investment Router Loaded")
print("--------------------------------")

server_logger.info("Loading Investment Price Router")
app.include_router(investment_price.router)
server_logger.info("Investment Price Router Loaded")
print("--------------------------------")

server_logger.info("Loading Dashboard Router")
app.include_router(dashboard.router)
server_logger.info("Dashboard Router Loaded")
print("--------------------------------")

server_logger.info("Loading User Router")
app.include_router(user.router)
server_logger.info("User Router Loaded")
print("--------------------------------")

server_logger.info("Loading Account Router")
app.include_router(account.router)
server_logger.info("Account Router Loaded")
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


