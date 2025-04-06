import uuid
from pathlib import Path

from fastapi import APIRouter
from fastapi.params import Depends
from starlette import status
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

from auth.auth0 import get_current_user

root_router = APIRouter()


@root_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_index(meeting_id: str = None, user=Depends(get_current_user)):
    if not meeting_id:
        new_id = str(uuid.uuid4())
        return RedirectResponse(url=f"/?meeting_id={new_id}")

    html_path = Path("static/real-time-speach.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(
        content="<h1>real-time-speach.html not found</h1>", status_code=404
    )


@root_router.get("/healthcheck", tags=["healthcheck"])
async def healthcheck():
    return JSONResponse({"status": "ok"}, status.HTTP_200_OK)


@root_router.get("/upload-file", response_class=HTMLResponse, include_in_schema=False)
async def upload_file_page(user=Depends(get_current_user)):
    html_path = Path("static/file-upload.html")
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>file-upload.html not found</h1>", status_code=404)
