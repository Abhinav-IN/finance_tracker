from fastapi import FastAPI
from server.routes import user  # Import routes
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Register the user routes
app.include_router(user.router, prefix="/users", tags=["Users"])

# @app.get("/")
# def home():
#     return {"message": "FastAPI is running"}


app.mount("/", StaticFiles(directory="static-node", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
