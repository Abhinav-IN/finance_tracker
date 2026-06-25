from fastapi import FastAPI
from contextlib import asynccontextmanager
from api.core.config import settings

from api import models
from api.database.session import init_db
from api.routers import auth, category, transaction, budget, subscription, investment, dashboard, transaction, user, investment_price

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
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def home():
    return {"message": "FastAPI is running"}

server_logger.info("Loading Auth Router")
app.include_router(auth.router)
server_logger.info("Auth Router Loaded")

server_logger.info("Loading Category Router")
app.include_router(category.router)
server_logger.info("Category Router Loaded")

server_logger.info("Loading Transaction Router")
app.include_router(transaction.router)
server_logger.info("Transaction Router Loaded")

server_logger.info("Loading Budget Router")
app.include_router(budget.router)
server_logger.info("Budget Router Loaded")

server_logger.info("Loading Subscription Router")
app.include_router(subscription.router)
server_logger.info("Subscription Router Loaded")

server_logger.info("Loading Investment Router")
app.include_router(investment.router)
server_logger.info("Investment Router Loaded")

server_logger.info("Loading Investment Price Router")
app.include_router(investment_price.router)
server_logger.info("Investment Price Router Loaded")

server_logger.info("Loading Dashboard Router")
app.include_router(dashboard.router)
server_logger.info("Dashboard Router Loaded")

server_logger.info("Loading User Router")
app.include_router(user.router)
server_logger.info("User Router Loaded")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(".server:app", host="0.0.0.0", port=8000, reload=True)