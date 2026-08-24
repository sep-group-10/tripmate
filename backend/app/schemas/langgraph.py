from pydantic import BaseModel


class GeminiResponse(BaseModel):
    status: str
    message: str