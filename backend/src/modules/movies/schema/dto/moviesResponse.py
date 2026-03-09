from typing import Any

from pydantic import BaseModel, Field


class MovieResponse(BaseModel):
    title: str
    omdb_data: dict[str, Any] = Field(default_factory=dict)


class MovieErrorResponse(BaseModel):
    status: str = "error"
    message: str


class MoviesEmptyResponse(BaseModel):
    status: str = "empty"
    message: str
    items: list[MovieResponse] = Field(default_factory=list)
