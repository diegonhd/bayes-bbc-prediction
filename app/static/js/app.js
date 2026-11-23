/**
 * Lógica do Front-End para Classificação de Notícias BBC News.
 * Integração com /api/scrape-and-predict e renderização dos cards (app/assets/).
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elementos do formulário
  const form = document.getElementById("scrape-form");
  const urlInput = document.getElementById("url-input");
  const btnSubmit = document.getElementById("btn-submit");
  const exampleChips = document.querySelectorAll(".example-chip");

  // Elementos da Prévia da Notícia (Coluna 01)
  const previewBadge = document.getElementById("preview-badge");
  const previewCategoryTag = document.getElementById("preview-category-tag");
  const previewTitle = document.getElementById("preview-title");
  const previewSummary = document.getElementById("preview-summary");
  const previewImageContainer = document.getElementById("preview-image-container");
  const previewImage = document.getElementById("preview-image");
  const previewDomain = document.getElementById("preview-domain");
  const previewLink = document.getElementById("preview-link");

  // Elementos do Resultado do Modelo (Coluna 02)
  const resultBadge = document.getElementById("result-badge");
  const resultCategory = document.getElementById("result-category");
  const resultConfidence = document.getElementById("result-confidence");
  const probabilitiesContainer = document.getElementById("probabilities-container");
  const jsonCodeBlock = document.getElementById("json-code-block");

  // Mapeamento de categorias em inglês para português editorial
  const CATEGORY_MAP = {
    tech: "Tecnologia",
    business: "Negócios",
    politics: "Política",
    sport: "Esportes",
    entertainment: "Entretenimento"
  };

  // Dicionário de demonstração para os chips rápidos de exemplo (notícias reais e ativas da BBC)
  const DEMO_PREVIEWS = {
    tech: {
      tag: "Tecnologia",
      title: "San Francisco is enjoying an AI boom, but worries about a crash are growing",
      summary: "AI employees in the industry's epicentre - San Francisco - worry that the sector is overheated.",
      domain: "bbc.com/news",
      url: "https://www.bbc.com/news/articles/cqe9k09j9jv4o",
      image_url: "https://ichef.bbci.co.uk/news/1024/branded_news/06d6/live/b3d40440-e712-11f1-a094-5fdc692f3e33.jpg",
      predicted_category: "tech",
      category_label: "Tecnologia",
      confidence: 100.0,
      confidence_formatted: "100,0%",
      probabilities: [
        { name: "Tecnologia", pct: 100.0 },
        { name: "Negócios", pct: 0.0 },
        { name: "Política", pct: 0.0 },
        { name: "Entretenimento", pct: 0.0 },
        { name: "Esportes", pct: 0.0 }
      ],
      json_output: { categoria: "tech", confianca: 1.0 }
    },
    business: {
      tag: "Negócios",
      title: "COP31 climate talks fail to reach deal amid fossil fuel and money rows",
      summary: "The prime minister of Australia, which co-hosted COP31, attributed the failure to \"difficult geopolitical times\".",
      domain: "bbc.com/news",
      url: "https://www.bbc.com/news/articles/cqwy06zrd26lo",
      image_url: "https://ichef.bbci.co.uk/news/1024/branded_news/a5fe/live/bf5d6f10-e71f-11f1-99a1-253766e7ad8b.jpg",
      predicted_category: "business",
      category_label: "Negócios",
      confidence: 100.0,
      confidence_formatted: "100,0%",
      probabilities: [
        { name: "Negócios", pct: 100.0 },
        { name: "Tecnologia", pct: 0.0 },
        { name: "Política", pct: 0.0 },
        { name: "Entretenimento", pct: 0.0 },
        { name: "Esportes", pct: 0.0 }
      ],
      json_output: { categoria: "business", confianca: 1.0 }
    },
    politics: {
      tag: "Política",
      title: "My approach to EU is pragmatic, says Andy Burnham",
      summary: "The prime minister also said his predecessors who have urged him not to reopen the Brexit debate are 'stuck in the past'.",
      domain: "bbc.com/news",
      url: "https://www.bbc.com/news/articles/c6vg2v9xkr40o",
      image_url: "https://ichef.bbci.co.uk/news/1024/branded_news/2176/live/24f4bbf0-e773-11f1-99b6-a35a62fa4264.jpg",
      predicted_category: "politics",
      category_label: "Política",
      confidence: 100.0,
      confidence_formatted: "100,0%",
      probabilities: [
        { name: "Política", pct: 100.0 },
        { name: "Negócios", pct: 0.0 },
        { name: "Tecnologia", pct: 0.0 },
        { name: "Entretenimento", pct: 0.0 },
        { name: "Esportes", pct: 0.0 }
      ],
      json_output: { categoria: "politics", confianca: 1.0 }
    },
    sport: {
      tag: "Esportes",
      title: "How does Mauricio Pochettino halt Man Utd's desperate slide",
      summary: "How does Mauricio Pochettino halt Manchester United's desperate slide towards the foot of the Premier League",
      domain: "bbc.com/sport",
      url: "https://www.bbc.com/sport/football/articles/ck9d7qxxl7w8o",
      image_url: "https://ichef.bbci.co.uk/ace/branded_sport/1200/cpsprodpb/ca84/live/d15e3100-e75a-11f1-b407-33329b1ec67a.jpg",
      predicted_category: "sport",
      category_label: "Esportes",
      confidence: 100.0,
      confidence_formatted: "100,0%",
      probabilities: [
        { name: "Esportes", pct: 100.0 },
        { name: "Entretenimento", pct: 0.0 },
        { name: "Negócios", pct: 0.0 },
        { name: "Política", pct: 0.0 },
        { name: "Tecnologia", pct: 0.0 }
      ],
      json_output: { categoria: "sport", confianca: 1.0 }
    },
    entertainment: {
      tag: "Entretenimento",
      title: "Don Toliver postpones London O2 arena show after Manchester evacuation",
      summary: "Don Toliver's show on Sunday was evacuated after an 'unknown substance' was released into the crowd.",
      domain: "bbc.com/news",
      url: "https://www.bbc.com/news/articles/ck3rgp4gv9pxo",
      image_url: "https://ichef.bbci.co.uk/news/1024/branded_news/cfc1/live/cdea3a90-e747-11f1-88dc-f746e0cde621.jpg",
      predicted_category: "entertainment",
      category_label: "Entretenimento",
      confidence: 100.0,
      confidence_formatted: "100,0%",
      probabilities: [
        { name: "Entretenimento", pct: 100.0 },
        { name: "Negócios", pct: 0.0 },
        { name: "Esportes", pct: 0.0 },
        { name: "Tecnologia", pct: 0.0 },
        { name: "Política", pct: 0.0 }
      ],
      json_output: { categoria: "entertainment", confianca: 1.0 }
    }
  };

  /**
   * Renderiza os dados no Grid de Análise.
   */
  function renderAnalysisData(data, isLive = true) {
    // 1. Atualiza Badges
    if (isLive) {
      previewBadge.textContent = "PRÉVIA REAL";
      previewBadge.className = "status-badge badge-real";
      resultBadge.textContent = "RESULTADO REAL";
      resultBadge.className = "status-badge badge-real";
    } else {
      previewBadge.textContent = "EXEMPLO";
      previewBadge.className = "status-badge badge-neutral";
      resultBadge.textContent = "DEMONSTRAÇÃO";
      resultBadge.className = "status-badge badge-demo";
    }

    // 2. Coluna 01: Prévia da Notícia (suporta payload de API e DEMO_PREVIEWS)
    const previewData = data.preview || data;
    if (previewData && previewData.title) {
      previewTitle.textContent = previewData.title;
      previewSummary.textContent = previewData.summary;
      previewDomain.textContent = previewData.domain || "bbc.com";
      previewLink.href = previewData.canonical_url || previewData.url || "#";

      if (previewData.image_url) {
        previewImage.src = previewData.image_url;
        previewImageContainer.classList.remove("hidden");
      } else {
        previewImageContainer.classList.add("hidden");
      }
    }

    const catLabel = data.category_label || CATEGORY_MAP[data.predicted_category] || data.predicted_category;
    previewCategoryTag.textContent = catLabel;

    // 3. Coluna 02: Resultado do Modelo
    resultCategory.textContent = catLabel;
    resultConfidence.textContent = data.confidence_formatted || `${data.confidence.toFixed(1)}%`.replace(".", ",");

    // 4. Renderiza Barras de Probabilidade
    probabilitiesContainer.innerHTML = "";
    const probList = data.probabilities || [];

    probList.forEach((item, index) => {
      const isTop = index === 0;
      const itemName = item.category_label || item.name || CATEGORY_MAP[item.category] || item.category;
      const itemPct = typeof item.percentage === "number" ? item.percentage : item.pct;
      const pctFormatted = `${itemPct.toFixed(1)}%`.replace(".", ",");

      const row = document.createElement("div");
      row.className = "prob-row";
      row.innerHTML = `
        <div class="prob-labels">
          <span class="prob-name">${itemName}</span>
          <span class="prob-pct">${pctFormatted}</span>
        </div>
        <div class="prob-bar-track">
          <div class="prob-bar-fill ${isTop ? 'top-fill' : 'secondary-fill'}" style="width: ${itemPct}%;"></div>
        </div>
      `;
      probabilitiesContainer.appendChild(row);
    });

    // 5. Card Saída do Modelo JSON
    const jsonOutput = data.json_output || {
      categoria: data.predicted_category,
      confianca: Number((data.confidence / 100).toFixed(4))
    };
    jsonCodeBlock.querySelector("code").textContent = JSON.stringify(jsonOutput, null, 2);
  }

  /**
   * Dispara a requisição assíncrona para a API.
   */
  async function analyzeUrl(url) {
    btnSubmit.disabled = true;
    btnSubmit.querySelector(".btn-text").textContent = "Analisando...";

    try {
      const response = await fetch("/api/scrape-and-predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "Falha na requisição." }));
        throw new Error(errorData.detail || `Erro HTTP ${response.status}`);
      }

      const data = await response.json();
      renderAnalysisData(data, true);
    } catch (err) {
      alert(`Não foi possível analisar a notícia:\n${err.message}`);
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.querySelector(".btn-text").textContent = "Analisar notícia";
    }
  }

  // Evento de submissão do formulário
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (url) {
      analyzeUrl(url);
    }
  });

  // Evento dos chips de exemplo rápido
  exampleChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const demoKey = chip.getAttribute("data-demo");
      const demoUrl = chip.getAttribute("data-url");
      urlInput.value = demoUrl;

      if (DEMO_PREVIEWS[demoKey]) {
        renderAnalysisData(DEMO_PREVIEWS[demoKey], false);
      }
    });
  });
});
