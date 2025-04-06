import uvicorn

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from config import settings as st

from api import transcribe_router, root_router, ws_router, auth_router, upload_router


app = FastAPI(
    title=st.PROJECT_NAME,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=st.AUTH_SECRET)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(transcribe_router)
app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(ws_router)
app.include_router(root_router)


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=8000, log_level="info", reload=False, log_config=None
    )
