from fastapi import FastAPI
from uvicorn import run

from .routes import webhook_router
from .utils import lifespan


app = FastAPI(docs_url="/", redoc_url=None, lifespan=lifespan)
app.router.prefix = "/api/v1"
app.include_router(router=webhook_router)


if __name__ == "__main__":
    # Delete reload paramert during production
    run(app="main:app", reload=True)
