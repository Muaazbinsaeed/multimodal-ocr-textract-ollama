from typing import Optional
from pydantic import BaseModel


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ExtractTextResponse(BaseModel):
    text: str
    model: str
    usage: Optional[TokenUsage] = None


class ErrorResponse(BaseModel):
    error: str
    message: str
    code: int