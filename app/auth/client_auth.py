import secrets
from typing import List, Optional

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class ClientCredentialsMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        api_key: str,
        client_secret: str,
        exclude_paths: Optional[List[str]] = None,
    ):
        super().__init__(app)
        self.api_key = api_key
        self.client_secret = client_secret
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in self.exclude_paths:
            return await call_next(request)

        # Para conexiones WebSocket de Genesys
        if (
            path == "/v1/voicebot/voicebot"
            and request.headers.get("user-agent") == "GenesysCloud-AudioHook-Client"
        ):
            # Verificar headers específicos de Genesys
            if not request.headers.get(
                "audiohook-organization-id"
            ) or not request.headers.get("audiohook-session-id"):
                raise HTTPException(
                    status_code=401, detail="Invalid Genesys WebSocket connection"
                )
            return await call_next(request)

        # Para el resto de endpoints API
        header_api_key = request.headers.get("x-api-key")
        if not header_api_key or not secrets.compare_digest(
            header_api_key, self.api_key
        ):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return await call_next(request)
