"""Módulo de extração de artigos e metadados da BBC News."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
import trafilatura


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def validate_bbc_url(url: str) -> None:
    """Valida se a URL pertence aos domínios suportados da BBC News em inglês."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if not any(d in domain for d in ["bbc.com", "bbc.co.uk"]):
        raise ValueError(
            "URL inválida: A notícia precisa pertencer ao domínio da BBC (bbc.com ou bbc.co.uk)."
        )

    if "/portuguese" in path:
        raise ValueError(
            "Idioma incompatível: O classificador opera sobre o vocabulário em inglês. "
            "Por favor, selecione uma matéria da BBC News Internacional."
        )


def extract_bbc_article(url: str) -> dict[str, str | int | None]:
    """Baixa o artigo da BBC, extrai metadados Open Graph e o corpo do texto via trafilatura."""
    validate_bbc_url(url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=8)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ConnectionError(f"Falha ao conectar aos servidores da BBC: {exc}") from exc

    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Extração de Metadados Open Graph para o Preview
    og_title = soup.find("meta", property="og:title")
    og_image = soup.find("meta", property="og:image")
    og_desc = soup.find("meta", property="og:description")

    title_str = (
        og_title["content"].strip()
        if og_title and og_title.get("content")
        else (soup.title.string.strip() if soup.title else "BBC News Article")
    )
    # Remove sufixos como "- BBC News" para manter o título puro
    title_str = re.sub(r"\s*-\s*BBC News.*$", "", title_str, flags=re.IGNORECASE)

    image_str = og_image["content"].strip() if og_image and og_image.get("content") else None
    desc_str = og_desc["content"].strip() if og_desc and og_desc.get("content") else None

    # 2. Extração do corpo textual limpo com trafilatura
    body_text = trafilatura.extract(
        html_content,
        include_comments=False,
        include_tables=False,
        no_fallback=False,
    )

    if not body_text or len(body_text.split()) < 20:
        # Fallback de emergência em tags de parágrafo
        paragraphs = [p.get_text().strip() for p in soup.find_all("p")]
        body_text = " ".join([p for p in paragraphs if len(p.split()) > 5])

    if not body_text or len(body_text.split()) < 15:
        raise ValueError("Não foi possível extrair o texto textual da matéria informada.")

    summary_str = desc_str or (body_text[:220] + "...")

    return {
        "title": title_str,
        "image_url": image_str,
        "summary": summary_str,
        "full_text": body_text,
        "word_count": len(body_text.split()),
        "canonical_url": url,
    }
