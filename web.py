#!/usr/bin/env python3
"""Batman-themed web UI for the Russian → German Translator."""

from flask import Flask, request, jsonify, render_template_string
from translator.core import translate_text
from translator.dictionary import DICTIONARY, GENDER_ARTICLE

app = Flask(__name__)

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BAT-TRANSLATOR | RU → DE</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');

  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bat-yellow: #f5c518;
    --bat-dark: #0a0a0a;
    --bat-gray: #1a1a2e;
    --bat-mid: #16213e;
    --bat-blue: #0f3460;
    --bat-glow: #f5c51855;
    --bat-text: #e0e0e0;
    --neon-yellow: #ffe600;
  }

  body {
    background: var(--bat-dark);
    color: var(--bat-text);
    font-family: 'Rajdhani', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* ── Animated background ── */
  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background:
      radial-gradient(ellipse at 20% 50%, #1a1a2e44 0%, transparent 50%),
      radial-gradient(ellipse at 80% 20%, #0f346033 0%, transparent 50%),
      radial-gradient(ellipse at 50% 80%, #f5c51808 0%, transparent 40%);
    z-index: -1;
    animation: bgPulse 8s ease-in-out infinite alternate;
  }

  @keyframes bgPulse {
    0% { opacity: 0.6; }
    100% { opacity: 1; }
  }

  /* ── Batman SVG Logo ── */
  .bat-logo {
    display: flex;
    justify-content: center;
    margin: 30px auto 0;
    filter: drop-shadow(0 0 25px var(--bat-yellow)) drop-shadow(0 0 50px #f5c51844);
    animation: batFloat 3s ease-in-out infinite;
  }

  .bat-logo svg {
    width: 140px;
    height: auto;
    fill: var(--bat-yellow);
  }

  @keyframes batFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
  }

  /* ── Header ── */
  .header {
    text-align: center;
    padding: 10px 20px 20px;
  }

  .header h1 {
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: clamp(1.6rem, 5vw, 2.8rem);
    background: linear-gradient(135deg, var(--bat-yellow), #fff176, var(--neon-yellow));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    letter-spacing: 3px;
    text-transform: uppercase;
    animation: titleGlow 2s ease-in-out infinite alternate;
  }

  @keyframes titleGlow {
    0% { filter: brightness(1); }
    100% { filter: brightness(1.3); }
  }

  .header .subtitle {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    color: #888;
    margin-top: 4px;
    letter-spacing: 5px;
    text-transform: uppercase;
  }

  /* ── Main container ── */
  .container {
    max-width: 700px;
    margin: 0 auto;
    padding: 0 20px 40px;
  }

  /* ── Input area ── */
  .input-section {
    position: relative;
    margin-bottom: 24px;
  }

  .input-wrapper {
    position: relative;
    border: 2px solid #333;
    border-radius: 16px;
    background: linear-gradient(145deg, #111, #1a1a2e);
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
  }

  .input-wrapper:focus-within {
    border-color: var(--bat-yellow);
    box-shadow: 0 0 20px var(--bat-glow), 0 0 40px #f5c51822;
  }

  .input-wrapper textarea {
    width: 100%;
    padding: 20px;
    padding-right: 70px;
    background: transparent;
    border: none;
    color: #fff;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    resize: none;
    outline: none;
    min-height: 80px;
  }

  .input-wrapper textarea::placeholder {
    color: #555;
    font-weight: 400;
  }

  .send-btn {
    position: absolute;
    right: 12px;
    bottom: 12px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    border: 2px solid var(--bat-yellow);
    background: linear-gradient(135deg, #1a1a2e, #0f3460);
    color: var(--bat-yellow);
    font-size: 1.4rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
  }

  .send-btn:hover {
    background: var(--bat-yellow);
    color: #000;
    box-shadow: 0 0 20px var(--bat-glow);
    transform: scale(1.1);
  }

  .send-btn:active { transform: scale(0.95); }

  /* ── Gender legend ── */
  .gender-legend {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .legend-chip {
    padding: 6px 16px;
    border-radius: 20px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    border: 1px solid;
  }

  .legend-chip.m { background: #1b5e2011; border-color: #4caf50; color: #4caf50; }
  .legend-chip.f { background: #e91e6311; border-color: #e91e63; color: #e91e63; }
  .legend-chip.n { background: #2196f311; border-color: #2196f3; color: #2196f3; }

  /* ── Results ── */
  .results {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .result-card {
    background: linear-gradient(145deg, #111118, #1a1a2e);
    border: 1px solid #2a2a3e;
    border-radius: 14px;
    padding: 16px 20px;
    transition: all 0.3s;
    animation: cardIn 0.4s ease-out backwards;
  }

  .result-card:hover {
    border-color: #444;
    transform: translateX(4px);
    box-shadow: -4px 0 15px #f5c51811;
  }

  @keyframes cardIn {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .result-card .source {
    font-size: 0.85rem;
    color: #777;
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 2px;
  }

  .result-card .translation {
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
  }

  .result-card .meta {
    font-size: 0.9rem;
    margin-top: 4px;
    color: #999;
  }

  .result-card .article {
    font-weight: 900;
    font-size: 1.5rem;
    margin-right: 6px;
  }

  .result-card.maskulin .article { color: #4caf50; }
  .result-card.feminin .article  { color: #e91e63; }
  .result-card.neutrum .article  { color: #2196f3; }

  .result-card .gender-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 10px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-left: 8px;
    vertical-align: middle;
  }

  .result-card.maskulin .gender-badge { background: #1b5e2033; color: #4caf50; border: 1px solid #4caf5055; }
  .result-card.feminin .gender-badge  { background: #e91e6322; color: #e91e63; border: 1px solid #e91e6355; }
  .result-card.neutrum .gender-badge  { background: #2196f322; color: #2196f3; border: 1px solid #2196f355; }

  .result-card.non-noun .translation { color: var(--bat-yellow); }
  .result-card.non-noun .pos-tag {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 10px;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 1px;
    background: #f5c51815;
    color: var(--bat-yellow);
    border: 1px solid #f5c51833;
    margin-left: 8px;
    vertical-align: middle;
  }

  .result-card.unknown {
    border-color: #ff5722;
    border-style: dashed;
  }

  .result-card.unknown .translation { color: #ff8a65; }

  .plural-info {
    color: #666;
    font-size: 0.85rem;
    font-style: italic;
  }

  /* ── Empty state ── */
  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #444;
  }

  .empty-state .icon { font-size: 3rem; margin-bottom: 10px; }
  .empty-state p { font-size: 1rem; letter-spacing: 2px; }

  /* ── Quick chips ── */
  .quick-section {
    margin-bottom: 20px;
  }

  .quick-section .label {
    font-size: 0.75rem;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 8px;
  }

  .quick-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .quick-chip {
    padding: 8px 16px;
    border-radius: 20px;
    background: #1a1a2e;
    border: 1px solid #333;
    color: #aaa;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .quick-chip:hover {
    border-color: var(--bat-yellow);
    color: var(--bat-yellow);
    background: #f5c51811;
  }

  .quick-chip:active { transform: scale(0.95); }

  /* ── Loading spinner ── */
  .loading { display: none; text-align: center; padding: 20px; }
  .loading.active { display: block; }
  .loading .spinner {
    width: 40px; height: 40px;
    border: 3px solid #333;
    border-top-color: var(--bat-yellow);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
</head>
<body>

<!-- Batman SVG Logo -->
<div class="bat-logo">
  <svg viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
    <path d="M256 48C141.1 48 48 141.1 48 256s93.1 208 208 208 208-93.1 208-208S370.9 48 256 48zm0 384c-97 0-176-79-176-176S159 80 256 80s176 79 176 176-79 176-176 176z" opacity="0.15"/>
    <path d="M256 100c-12 0-24 38-30 58-8 26-40 42-70 52-14 4-30 14-38 28 0 0 16-8 38-6 20 2 36 14 42 30 4 10 2 28-10 52-8 16-14 32-14 32s22-18 40-34c14-12 24-18 32-18s18 6 32 18c18 16 40 34 40 34s-6-16-14-32c-12-24-14-42-10-52 6-16 22-28 42-30 22-2 38 6 38 6-8-14-24-24-38-28-30-10-62-26-70-52-6-20-18-58-30-58z"/>
  </svg>
</div>

<div class="header">
  <h1>Bat-Translator</h1>
  <div class="subtitle">Russian → German</div>
</div>

<div class="container">
  <!-- Gender legend -->
  <div class="gender-legend">
    <span class="legend-chip m">der — maskulin</span>
    <span class="legend-chip f">die — feminin</span>
    <span class="legend-chip n">das — neutrum</span>
  </div>

  <!-- Input -->
  <div class="input-section">
    <div class="input-wrapper">
      <textarea id="inputText" placeholder="Введите русское слово..." rows="2"
                onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();doTranslate();}"></textarea>
      <button class="send-btn" onclick="doTranslate()" title="Translate">&#9654;</button>
    </div>
  </div>

  <!-- Quick try chips -->
  <div class="quick-section">
    <div class="label">Try these</div>
    <div class="quick-chips">
      <span class="quick-chip" onclick="quickTranslate('кошка')">кошка</span>
      <span class="quick-chip" onclick="quickTranslate('дом')">дом</span>
      <span class="quick-chip" onclick="quickTranslate('мать')">мать</span>
      <span class="quick-chip" onclick="quickTranslate('солнце')">солнце</span>
      <span class="quick-chip" onclick="quickTranslate('любовь')">любовь</span>
      <span class="quick-chip" onclick="quickTranslate('я читать книга')">я читать книга</span>
      <span class="quick-chip" onclick="quickTranslate('до свидания')">до свидания</span>
      <span class="quick-chip" onclick="quickTranslate('хлеб молоко сыр')">хлеб молоко сыр</span>
    </div>
  </div>

  <!-- Loading -->
  <div class="loading" id="loading"><div class="spinner"></div></div>

  <!-- Results -->
  <div class="results" id="results">
    <div class="empty-state">
      <div class="icon">&#x1F987;</div>
      <p>The Dark Knight awaits your words...</p>
    </div>
  </div>
</div>

<script>
function quickTranslate(text) {
  document.getElementById('inputText').value = text;
  doTranslate();
}

async function doTranslate() {
  const input = document.getElementById('inputText').value.trim();
  if (!input) return;

  const results = document.getElementById('results');
  const loading = document.getElementById('loading');

  loading.classList.add('active');
  results.innerHTML = '';

  try {
    const resp = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: input })
    });
    const data = await resp.json();

    loading.classList.remove('active');

    if (data.results.length === 0) {
      results.innerHTML = '<div class="empty-state"><p>Nothing to translate</p></div>';
      return;
    }

    let html = '';
    data.results.forEach((item, i) => {
      const style = `animation-delay: ${i * 0.08}s`;

      if (item.pos === 'noun' && item.gender) {
        const article = item.article || '';
        const cls = item.gender;
        const plural = item.plural ? `<span class="plural-info">Pl. ${item.plural}</span>` : '';
        html += `
          <div class="result-card ${cls}" style="${style}">
            <div class="source">${item.source}</div>
            <div class="translation">
              <span class="article">${article}</span>${item.translation}
              <span class="gender-badge">${item.gender}</span>
            </div>
            <div class="meta">${plural}</div>
          </div>`;
      } else if (item.unknown) {
        html += `
          <div class="result-card unknown" style="${style}">
            <div class="source">${item.source}</div>
            <div class="translation">Not in dictionary</div>
          </div>`;
      } else {
        html += `
          <div class="result-card non-noun" style="${style}">
            <div class="source">${item.source}</div>
            <div class="translation">
              ${item.translation}
              <span class="pos-tag">${item.pos}</span>
            </div>
          </div>`;
      }
    });

    results.innerHTML = html;
  } catch (err) {
    loading.classList.remove('active');
    results.innerHTML = '<div class="empty-state"><p>Translation failed. Try again.</p></div>';
  }
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    raw_results = translate_text(text)

    enriched = []
    for item in raw_results:
        source_lower = item["source"].lower().strip()
        entry = DICTIONARY.get(source_lower)

        if entry is None:
            enriched.append({
                "source": item["source"],
                "translation": item["result"],
                "pos": None,
                "gender": None,
                "article": None,
                "plural": None,
                "unknown": True,
            })
        elif entry["pos"] == "noun":
            enriched.append({
                "source": item["source"],
                "translation": entry["translation"],
                "pos": "noun",
                "gender": entry["gender"],
                "article": GENDER_ARTICLE[entry["gender"]],
                "plural": entry.get("plural"),
                "unknown": False,
            })
        else:
            enriched.append({
                "source": item["source"],
                "translation": entry["translation"],
                "pos": entry["pos"],
                "gender": None,
                "article": None,
                "plural": None,
                "unknown": False,
            })

    return jsonify({"results": enriched})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=False)
