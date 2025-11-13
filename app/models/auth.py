from pydantic import BaseModel


class authModel(BaseModel):
    api_key: str
    client_secret: str
