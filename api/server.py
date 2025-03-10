from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes.user import user as userRoute  # Import the user routes
from api.routes.auth import auth  as authRoute # Import the user routes
from . import models
from .database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/api")
def home():
    return {"message": "FastAPI is running"}

# Include user routes
app.include_router(userRoute.router, prefix="/users", tags=["Users"])
app.include_router(authRoute.router, prefix="/auth", tags=["Auth"])

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("   .server:app", host="0.0.0.0", port=8000, reload=True)
