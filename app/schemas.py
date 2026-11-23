"""Esquemas de dados Pydantic para a API de Classificação BBC News."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TextPredictionRequest(BaseModel):
    """Payload para classificação direta de texto."""
    text: str = Field(
        ...,
        min_length=15,
        description="Texto do artigo em língua inglesa para classificação.",
        examples=["The company reported surging profits due to global smartphone sales."],
    )


class UrlPredictionRequest(BaseModel):
    """Payload para classificação a partir de link da BBC."""
    url: str = Field(
        ...,
        description="URL completa de um artigo publicado no portal da BBC News.",
        examples=["https://www.bbc.com/news/technology-12345678"],
    )


class ProbabilityItem(BaseModel):
    """Item individual da distribuição a posteriori."""
    category: str
    category_label: str
    probability: float
    percentage: float


class ArticlePreview(BaseModel):
    """Metadados visuais extraídos para o preview da notícia (Área de análise)."""
    title: str
    image_url: str | None = None
    summary: str
    canonical_url: str
    domain: str = "bbc.com"
    word_count: int


class PredictionResponse(BaseModel):
    """Resposta consolidada de predição adaptada ao layout visual de assets."""
    status: str = "success"
    predicted_category: str
    category_label: str
    confidence: float
    confidence_formatted: str
    confidence_level: str
    probabilities: list[ProbabilityItem]
    preview: ArticlePreview | None = None
    json_output: dict
