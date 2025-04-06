from fastapi import Request, Depends, APIRouter
from starlette.responses import RedirectResponse

from auth.auth0 import get_current_user
from auth_config import auth0
from config import settings as st


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/login")
async def login(request: Request):
    return await auth0.authorize_redirect(
        request, f"{st.API_URL}/auth/callback", audience=st.API_URL
    )


@auth_router.get("/callback")
async def callback(request: Request):
    token = await auth0.authorize_access_token(request)
    request.session["access_token"] = token["access_token"]
    return RedirectResponse(url="/")


@auth_router.get("/profile")
def profile(user: dict = Depends(get_current_user)):
    return {"user": user}


@auth_router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url=f"https://{st.AUTH0_DOMAIN}/v2/logout?"
        f"returnTo={st.API_URL}/auth/login&"
        f"client_id={st.AUTH0_CLIENT_ID}"
    )
