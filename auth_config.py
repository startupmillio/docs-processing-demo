from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from config import settings

auth_config = {
    "AUTH0_CLIENT_ID": settings.AUTH0_CLIENT_ID,
    "AUTH0_CLIENT_SECRET": settings.AUTH0_CLIENT_SECRET,
    "AUTH0_DOMAIN": settings.AUTH0_DOMAIN,
    "AUTH0_CALLBACK_URL": f"{settings.API_URL}/auth/callback",
}

config = Config(environ=auth_config)
oauth = OAuth(config)

auth0 = oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
        "audience": settings.API_URL,
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)
