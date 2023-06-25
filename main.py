from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app import events
from app.settings import Settings
from app.views import router

app = FastAPI()
app.include_router(router)


@app.on_event('startup')
async def startup_events() -> None:
    """События на старте приложения."""
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.state.conf = Settings()
    events.connect_redis(app)
    await events.read_csv(app)


@app.on_event('shutdown')
async def shutdown_events() -> None:
    """События при закрытии приложения."""
    await app.state.cache.close()
