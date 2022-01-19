from fastapi import HTTPException, Cookie
from fastapi.security import HTTPBearer
from typing import Optional, Dict
from app.routers.login import decodeJWT


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, access_token: Optional[str] = Cookie(None)):
        if access_token is None:
            raise HTTPException(
                status_code=403, detail="Invalid token or expired token."
            )

        scheme, access_token = access_token.split()
        if access_token:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(access_token):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return access_token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
