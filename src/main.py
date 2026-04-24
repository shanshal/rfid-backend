from fastapi import FastAPI
from src.api.routes.health import router as health_router

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "API is running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

app.include_router(health_router)

