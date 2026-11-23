"""Módulo de Ingestão e Validação do Dataset BBC News.

Disciplina de Probabilidade e Estatística (IFCE).
"""

from __future__ import annotations

import csv
from pathlib import Path
import shutil
import sys

import kagglehub

# Configuração de caminhos base
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
TARGET_CSV_PATH = RAW_DATA_DIR / "bbc-text.csv"
DATASET_IDENTIFIER = "moazeldsokyx/bbc-news"
EXPECTED_COLUMNS = {"category", "text"}
EXPECTED_MIN_ROWS = 2000


def download_dataset() -> Path:
    """Realiza o download da versão mais recente do dataset no Kaggle."""
    print(f"[1/4] Baixando/verificando dataset '{DATASET_IDENTIFIER}' via KaggleHub...")
    download_dir = kagglehub.dataset_download(DATASET_IDENTIFIER)
    source_csv = Path(download_dir) / "bbc-text.csv"

    if not source_csv.exists():
        raise FileNotFoundError(
            f"O arquivo 'bbc-text.csv' não foi encontrado no diretório: {download_dir}"
        )

    print(f"      Arquivo de origem encontrado em: {source_csv}")
    return source_csv


def sync_local_data(source_csv: Path, target_csv: Path) -> None:
    """Copia o dataset para a pasta padronizada do projeto (data/raw/)."""
    print(f"[2/4] Sincronizando arquivo para '{target_csv}'...")
    target_csv.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_csv, target_csv)
    print("      Cópia local concluída com sucesso.")


def validate_dataset(csv_path: Path) -> dict[str, int]:
    """Valida a integridade do arquivo CSV e retorna contagens por categoria."""
    print(f"[3/4] Validando integridade de '{csv_path.name}'...")
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        raise ValueError(f"O arquivo {csv_path} está vazio ou não existe.")

    counts: dict[str, int] = {}
    total_rows = 0

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        header = set(reader.fieldnames or [])

        if not EXPECTED_COLUMNS.issubset(header):
            raise ValueError(
                f"Estrutura inválida! Esperava colunas {EXPECTED_COLUMNS}, mas obteve {header}"
            )

        for row in reader:
            category = row["category"].strip()
            text = row["text"].strip()

            if not category or not text:
                continue

            counts[category] = counts.get(category, 0) + 1
            total_rows += 1

    if total_rows < EXPECTED_MIN_ROWS:
        raise ValueError(
            f"O dataset contém apenas {total_rows} registros válidos (mínimo esperado: {EXPECTED_MIN_ROWS})."
        )

    print(f"[4/4] Validação concluída! Total de artigos válidos: {total_rows}")
    for cat, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        print(f"      - {cat:<15}: {count:>4} artigos")

    return counts


def main() -> None:
    """Ponto de entrada do script de ingestão."""
    try:
        source_csv = download_dataset()
        sync_local_data(source_csv, TARGET_CSV_PATH)
        validate_dataset(TARGET_CSV_PATH)
        print("\n✔ Ingestão e validação finalizadas com sucesso!")
    except Exception as exc:
        print(f"\ Erro durante a ingestão: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
