# Classificador Multinomial Naive Bayes de Notícias da BBC

Projeto acadêmico desenvolvido para a disciplina de **Probabilidade e Estatística** do Instituto Federal de Educação, Ciência e Tecnologia do Ceará (IFCE).

A aplicação implementa um classificador probabilístico supervisionado baseado no algoritmo **Multinomial Naive Bayes** para predição da categoria temática de artigos jornalísticos do portal BBC News em cinco categorias reais: **Tecnologia (tech)**, **Negócios (business)**, **Política (politics)**, **Esportes (sport)** e **Entretenimento (entertainment)**.

A solução engloba desde a modelagem matemática e análise exploratória de dados até a disponibilização de uma API assíncrona com raspagem de matérias em tempo real, interface web interativa de alta fidelidade visual e empacotamento completo em container Docker.

---

## 1. Fundamentação Teórica e Modelagem

O classificador utiliza o Teorema de Bayes para calcular a probabilidade a posteriori de um documento pertencer a cada classe temática:

$$P(C_k \mid D) \propto P(C_k) \prod_{i=1}^{V} P(w_i \mid C_k)^{x_i}$$

Onde:
- $C_k$ representa uma das 5 categorias temáticas.
- $P(C_k)$ é a probabilidade a priori da classe (proporção balanceada no corpus de treino).
- $w_i$ representa cada termo no vocabulário $V$.
- $x_i$ é a frequência do termo $w_i$ no documento $D$.
- $P(w_i \mid C_k)$ é calculada com **Suavização de Laplace (Laplace Smoothing)** para mitigar o problema de probabilidade zero para termos não observados no treino:

$$P(w_i \mid C_k) = \frac{N_{k,i} + \alpha}{N_k + \alpha \cdot |V|}$$

com $\alpha = 1.0$.

### Desempenho do Modelo
- **Acurácia Global:** ~98.4% no conjunto de teste estratificado (80/20).
- **Pipeline:** `CountVectorizer` com união léxica de stopwords (NLTK + Scikit-Learn + termos editoriais) e estimador `MultinomialNB`.
- **Serialização:** Pipeline completo exportado de forma imutável em `models/bbc_multinomial_pipeline.joblib`.

---

## 2. Arquitetura da Solução

```text
bayes-bbc-prediction/
├── app/                           # Backend FastAPI e Frontend da aplicacao
│   ├── assets/                    # Wireframes originais de referencia visual
│   ├── static/                    # Interface Web
│   │   ├── css/style.css          # Estilizacao editorial responsiva
│   │   ├── js/app.js              # Logica assincrona, barras e consumo da API
│   │   └── index.html             # Estrutura semantica dos 3 blocos visuais
│   ├── schemas.py                 # Contratos de dados Pydantic V2
│   ├── scraper.py                 # Raspagem de metadados Open Graph e texto
│   └── main.py                    # Servidor ASGI FastAPI e montagem estatica
├── data/
│   ├── base.py                    # Script de ingestao e persistencia do dataset
│   └── raw/bbc-text.csv           # Corpus de 2.225 artigos rotulados
├── models/
│   └── bbc_multinomial_pipeline.joblib # Modelo treinado pronto para producao
├── reports/
│   ├── figures/                   # Graficos de distribuicao, matriz e wordclouds
│   └── metricas_avaliacao.txt     # Relatorio consolidado de metricas
├── src/                           # Cadernos Jupyter metodologicos
│   ├── eda.ipynb                  # 02 Analise Exploratoria de Dados
│   ├── preprocessor.ipynb         # 03 Pre-processamento e Vetorizacao
│   ├── train.ipynb                # 04 Treinamento e Pipeline Scikit-Learn
│   ├── evaluate.ipynb             # 05 Avaliacao e Matriz de Confusao
│   └── predict.ipynb              # 06 Inferencia Interativa CLI
├── tests/
│   ├── __init__.py
│   └── test_api.py                # Testes automatizados de integracao (pytest)
├── .dockerignore                  # Regras de exclusao de contexto Docker
├── .gitignore                     # Controle estrito de arquivos versionados
├── Dockerfile                     # Multi-stage build (seguranca e leveza)
├── docker-compose.yml             # Orquestracao de execucao local
├── README.md                      # Documentacao principal
└── requirements.txt               # Dependencias do projeto
```

---

## 3. Instalação e Execução Local

### Pré-requisitos
- Python 3.12 instalado
- Git

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/<seu-usuario>/bayes-bbc-prediction.git
   cd bayes-bbc-prediction
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Inicie o servidor de desenvolvimento:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

5. **Acesse no navegador:**
   - Interface Web: `http://localhost:8000`
   - Documentação Swagger da API: `http://localhost:8000/docs`
   - Healthcheck: `http://localhost:8000/health`

---

## 4. Execução com Docker e Docker Compose

A aplicação é totalmente conteinerizada através de um `Dockerfile` com **multi-stage build** baseado em `python:3.12-slim`:
- Estágio de construção isolado com virtualenv em `/opt/venv`.
- Imagem de execução final sem ferramentas de compilação.
- Execução sob usuário restrito sem privilégios administrativos (`appuser`).
- Healthcheck interno configurado.

### Comandos de Execução

```bash
# Construir a imagem e subir o container em segundo plano
docker compose up -d --build

# Inspecionar status e saude do container
docker compose ps

# Visualizar logs em tempo real
docker compose logs -f

# Parar o servico
docker compose down
```

A aplicação responde imediatamente na porta `8000`.

---

## 5. Testes Automatizados

A suite de testes de integração utiliza `pytest` e o `TestClient` do FastAPI para validar:
- O carregamento correto do pipeline Naive Bayes na memória.
- A inferência direta sobre textos com validação da distribuição a posteriori e saída JSON.
- Rejeição de textos vazios ou excessivamente curtos (HTTP 422).
- Rejeição e validação de domínio para URLs fora da BBC (HTTP 400).
- Rejeição e orientação pedagógica para links em português (HTTP 400).

Para rodar os testes:

```bash
pytest tests/ -v
```

Resultado esperado:
```text
tests/test_api.py::test_health_endpoint PASSED                           [ 20%]
tests/test_api.py::test_predict_endpoint_valid_business PASSED           [ 40%]
tests/test_api.py::test_predict_endpoint_short_text_error PASSED         [ 60%]
tests/test_api.py::test_scrape_endpoint_invalid_domain PASSED            [ 80%]
tests/test_api.py::test_scrape_endpoint_portuguese_rejection PASSED      [100%]

======================== 5 passed in 3.61s ========================
```

---

## 6. Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Verifica a integridade da API e a presença do modelo na RAM. |
| `POST` | `/api/predict` | Recebe um texto (`{"text": "..."}`) e retorna a predição probabilística. |
| `POST` | `/api/scrape-and-predict` | Recebe uma URL da BBC News (`{"url": "..."}`), extrai a prévia e classifica o conteúdo. |
| `GET` | `/docs` | Documentação interativa OpenAPI / Swagger UI. |

---

## 7. Tecnologias Empregadas

- **Linguagem:** Python 3.12
- **Modelagem Estatística e NLP:** Scikit-Learn, NumPy, Pandas, NLTK, Matplotlib, Seaborn, WordCloud
- **Back-End e Servidor Web:** FastAPI, Pydantic V2, Uvicorn, Starlette
- **Raspagem de Dados Web:** Requests, BeautifulSoup4, Trafilatura
- **Testes e Qualidade:** Pytest, HTTPX
- **Front-End:** HTML5 semântico, CSS3 moderno com tipografia editorial, Vanilla JavaScript
- **DevOps e Deploy:** Docker (Multi-stage), Docker Compose
