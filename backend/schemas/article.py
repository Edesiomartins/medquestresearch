from typing import Optional

from pydantic import BaseModel


class ArticleSections(BaseModel):
    abstract: Optional[str] = None
    introduction: Optional[str] = None
    methods: Optional[str] = None
    results: Optional[str] = None
    discussion: Optional[str] = None
    conclusion: Optional[str] = None


class ArticleSectionResponse(BaseModel):
    section: str
    content: str
    warnings: list[str] = []

