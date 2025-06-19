from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import models, auth
from .database import engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

@app.get("/api")
def home():
    return {"message": "FastAPI is running"}

# Serve static files
app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("   .server:app", host="0.0.0.0", port=8000, reload=True)
