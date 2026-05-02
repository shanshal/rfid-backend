from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.alerts import router as alerts_router
from src.api.routes.devices import router as devices_router
from src.api.routes.diagnostics import router as diagnostics_router
from src.api.routes.health import router as health_router
from src.api.routes.instruments import router as instruments_router
from src.api.routes.movements import router as movements_router
from src.api.routes.procedures import router as procedures_router
from src.api.routes.readers import router as readers_router
from src.api.routes.rooms import router as rooms_router
from src.api.routes.scans import router as scans_router
from src.mqtt.lifespan import mqtt_lifespan


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mqtt_lifespan():
        yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "API is running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

PREFIX = "/api/v1"

app.include_router(health_router, prefix=PREFIX)
app.include_router(instruments_router, prefix=PREFIX)
app.include_router(rooms_router, prefix=PREFIX)
app.include_router(procedures_router, prefix=PREFIX)
app.include_router(movements_router, prefix=PREFIX)
app.include_router(devices_router, prefix=PREFIX)
app.include_router(diagnostics_router, prefix=PREFIX)
app.include_router(scans_router, prefix=PREFIX)
app.include_router(alerts_router, prefix=PREFIX)
app.include_router(readers_router, prefix=PREFIX)
