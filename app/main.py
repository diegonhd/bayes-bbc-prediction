"""Servidor Web FastAPI para Classificação de Artigos da BBC News.

Disciplina de Probabilidade e Estatística (IFCE).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import joblib
import numpy as np

from app.schemas import (
    ArticlePreview,
    PredictionResponse,
    ProbabilityItem,
    TextPredictionRequest,
    UrlPredictionRequest,
)
from app.scraper import extract_bbc_article

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "bbc_multinomial_pipeline.joblib"
STATIC_DIR = PROJECT_ROOT / "app" / "static"

# Variável global para armazenar o pipeline na RAM
pipeline = None


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Gerencia a carga única do modelo na inicialização do servidor."""
    global pipeline
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Artefato do modelo não encontrado em: {MODEL_PATH}. "
            "Execute o notebook src/train.ipynb para gerar o modelo antes de iniciar o servidor!"
        )
    print(f"Carregando modelo treinado de: {MODEL_PATH}")
    pipeline = joblib.load(MODEL_PATH)
    print(f"Modelo pronto. Classes reconhecidas: {list(pipeline.classes_)}")
    yield
    print("Desligando servidor...")


app = FastAPI(
    title="BBC News Classifier API",
    description="API de Classificação de Notícias com Multinomial Naive Bayes e Raspagem de URL.",
    version="1.0.0",
    lifespan=lifespan,
)

# Habilita CORS para permitir chamadas assíncronas do Front-End
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CATEGORY_LABELS = {
    "tech": "Tecnologia",
    "business": "Negócios",
    "politics": "Política",
    "sport": "Esportes",
    "entertainment": "Entretenimento",
}


def run_inference(text: str, preview: ArticlePreview | None = None) -> PredictionResponse:
    """Executa a predição probabilística sobre o texto e estrutura a resposta."""
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="O modelo ainda não foi carregado na memória.",
        )

    # 1. Predição e probabilidades
    predicted_class = str(pipeline.predict([text])[0])
    probabilities = pipeline.predict_proba([text])[0]
    classes = pipeline.classes_

    # 2. Ordena da maior para a menor probabilidade
    sorted_indices = np.argsort(probabilities)[::-1]
    prob_items = [
        ProbabilityItem(
            category=str(classes[idx]),
            category_label=CATEGORY_LABELS.get(str(classes[idx]), str(classes[idx]).capitalize()),
            probability=float(round(probabilities[idx], 4)),
            percentage=float(round(probabilities[idx] * 100, 2)),
        )
        for idx in sorted_indices
    ]

    top_prob = prob_items[0]
    top_confidence = top_prob.percentage
    confidence_level = "Alta" if top_confidence >= 80.0 else ("Média" if top_confidence >= 55.0 else "Baixa")
    confidence_formatted = f"{top_prob.percentage:.1f}%".replace(".", ",")

    # Objeto compacto exatamente como exigido no card SAÍDA DO MODELO (app/assets/Área de análise.png)
    json_output = {
        "categoria": predicted_class,
        "confianca": top_prob.probability,
    }

    return PredictionResponse(
        status="success",
        predicted_category=predicted_class,
        category_label=CATEGORY_LABELS.get(predicted_class, predicted_class.capitalize()),
        confidence=top_confidence,
        confidence_formatted=confidence_formatted,
        confidence_level=confidence_level,
        probabilities=prob_items,
        preview=preview,
        json_output=json_output,
    )


@app.get("/health")
@app.get("/api/health")
def health_check():
    """Rota de verificação de integridade do serviço."""
    return {
        "status": "healthy",
        "model_loaded": pipeline is not None,
        "classes": list(pipeline.classes_) if pipeline else [],
    }


@app.post("/api/predict", response_model=PredictionResponse)
def predict_from_text(payload: TextPredictionRequest):
    """Classifica um texto colado diretamente pelo usuário."""
    try:
        return run_inference(payload.text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno no classificador: {exc}",
        ) from exc


@app.post("/api/scrape-and-predict", response_model=PredictionResponse)
def predict_from_url(payload: UrlPredictionRequest):
    """Raspa uma notícia da BBC News, monta o preview e executa a predição."""
    try:
        scraped_data = extract_bbc_article(payload.url)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except ConnectionError as conn_err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(conn_err),
        ) from conn_err
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha inesperada ao raspar artigo: {exc}",
        ) from exc

    preview = ArticlePreview(
        title=str(scraped_data["title"]),
        image_url=scraped_data["image_url"],
        summary=str(scraped_data["summary"]),
        canonical_url=str(scraped_data["canonical_url"]),
        word_count=int(scraped_data["word_count"]),
    )

    full_text = str(scraped_data["full_text"])
    return run_inference(full_text, preview=preview)


# Se a pasta static existir, serve os arquivos estáticos (HTML/CSS/JS do Front-End)
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
