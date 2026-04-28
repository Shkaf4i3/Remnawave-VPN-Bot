from fastapi import FastAPI
from uvicorn import run

from .routes import webhook_router
from .utils import lifespan


app = FastAPI(docs_url="/", redoc_url=None, lifespan=lifespan)
app.include_router(router=webhook_router, prefix="/api/v1")


if __name__ == "__main__":
    run(app="main:app", host="0.0.0.0", port=8000)
