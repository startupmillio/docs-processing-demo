import json
from base64 import b64decode
from typing import Optional

from fastapi import Request, HTTPException
from itsdangerous import TimestampSigner
from jose import jwt, JWTError
from aiocache import SimpleMemoryCache
import httpx

from api.exceptions import ForbiddenException, UnauthorizedException
from config import settings as st


JWKS_URL = f"https://{st.AUTH0_DOMAIN}/.well-known/jwks.json"
jwks_cache = SimpleMemoryCache()


async def fetch_jwks():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {e}")


async def get_jwks():
    cached = await jwks_cache.get("jwks")
    if cached:
        return cached

    jwks = await fetch_jwks()

    await jwks_cache.set("jwks", jwks, ttl=600)
    return jwks


async def get_signing_key(token: str):
    unverified_header = jwt.get_unverified_header(token)
    if "kid" not in unverified_header:
        raise HTTPException(status_code=401, detail="Token header missing 'kid'")

    jwks = await get_jwks()

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }

    raise HTTPException(status_code=401, detail="Unable to find matching JWK")


async def get_token_payload(token) -> Optional[dict]:
    try:
        signing_key = await get_signing_key(token)

        payload = jwt.decode(
            token,
            key=signing_key,
            algorithms=["RS256"],
            audience=st.API_URL,
            issuer=f"https://{st.AUTH0_DOMAIN}/",
        )

        return payload

    except JWTError as e:
        raise ForbiddenException(message="Invalid Token")


async def get_current_user(request: Request):
    token = request.session.get("access_token")
    if not token:
        raise UnauthorizedException

    return await get_token_payload(token)


async def get_payload_ws(session_cookie):
    if session_cookie is None:
        raise UnauthorizedException

    serializer = TimestampSigner(st.AUTH_SECRET, salt="itsdangerous.Signer")
    encoded_cookies = serializer.unsign(session_cookie, max_age=1209600)
    cookies = json.loads(b64decode(encoded_cookies))
    token = cookies.get("access_token")
    if not token:
        raise UnauthorizedException

    return await get_token_payload(token)
