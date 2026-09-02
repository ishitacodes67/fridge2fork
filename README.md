# Fridge2Fork 🍳

An AI-powered recipe recommendation system that turns whatever ingredients you have — typed, spoken, or photographed — into a grounded, honest, complete recipe (not just a name). Built as a deep-dive into RAG (Retrieval-Augmented Generation) systems, with a specific focus on **knowing when the system doesn't know**, rather than just optimizing for accuracy.

## The Core Idea

Most RAG demos are graded on "did it answer correctly?" This project is built around a harder, more valuable question: **how do you catch and honestly communicate when a system's answer is a weak match, before it misleads the user?**

The cooking domain is the testbed. The engineering focus is retrieval, grounding, and failure detection.

## Architecture
Input (text / voice / photo)
↓
Constraint Parser (time, dietary, exclusions, spice, budget)
↓
Query Router (simple search vs. filtered search)
↓
Hybrid Retrieval (BM25 keyword search + dense vector embeddings)
↓
Exclusion & Budget Filters (safety-critical + cost-aware)
↓
Coverage Guardrail (measures how well results actually match)
↓
LLM Generation (grounded strictly in retrieved recipes + real directions)
↓
Output (web UI receipt card + optional email, with nutrition suggestions)

## Key Features

- **Three input modalities**: type ingredients, speak them (Whisper, local), or photograph them (Groq vision model) — all funnel into one shared pipeline
- **Hybrid retrieval**: BM25 (exact keyword matching) + dense embeddings (semantic similarity) over a 2M+ recipe dataset — vector search alone missed exact-term matches like specific excluded ingredients
- **Constraint parsing**: time limits, dietary restrictions, allergies/exclusions, spice level, and real budget amounts (e.g. "under ₹300") extracted from natural language
- **Safety-critical exclusion filtering**: a category-expansion map (e.g. "shellfish" → shrimp, crab, oyster, lobster) catches allergy-relevant recipes even when the user doesn't name every specific ingredient
- **Real budget filtering**: a deterministic ingredient-cost lookup table (not LLM-guessed) estimates recipe cost and filters out anything over the user's stated budget
- **Coverage guardrail**: measures what fraction of the user's actual ingredients appear in the retrieved recipes, and explicitly warns when the match is weak — instead of confidently returning a poor result
- **Grounded, warm generation**: the LLM is instructed to use only retrieved recipes' real ingredients and directions, to state any weak-match caveat in its first sentence (not buried at the end), and to write like a friendly recipe card rather than a technical report
- **Nutrition suggestions**: rule-based (not LLM-generated, deliberately) estimation using the USDA FoodData Central API
- **Email delivery**: sends the full recipe via Gmail SMTP
- **Web frontend**: a receipt/pantry-themed single-page UI (FastAPI backend) supporting all three input types, with a stamped confidence badge reflecting the guardrail state as structured data, not guessed from prose

## The Eval Story

Built a 25-query adversarial evaluation set spanning six categories: easy/baseline, constraint-heavy, rare-ingredient, ambiguous phrasing, logically conflicting requests, and allergy-critical exact-match cases.

**Bugs found and fixed, in order of discovery:**

1. **3 safety-relevant exclusion bugs** — the filter wasn't catching category terms like "shellfish-free" or "nut-free," letting allergy-relevant recipes (containing peanut butter, shrimp, tree nuts) slip through. Fixed with a category-expansion map.
2. **A zero-results UX bug** — overly aggressive filtering sometimes returned nothing with no explanation. Fixed with a larger candidate pool and an explicit fallback message.
3. **Missing recipe substance** — generation only ever received ingredient lists, never the dataset's actual `directions` field, so "recommendations" were really just ingredient summaries with no way to actually cook the dish. Found by using my own product critically, not by an automated test. Fixed by passing full directions into the grounding context.
4. **Stiff, report-style generation tone** — early prompts produced bolded headers and markdown dividers instead of a readable recipe. Fixed by giving the model an exact template to fill in, rather than abstract formatting instructions.

**An interesting finding during generation testing**: the LLM generation layer independently caught a logical contradiction ("vegan recipe with chicken") that the retrieval and guardrail layers had missed — different layers of the system had complementary strengths, not just redundant ones.

Full eval results and manual labeling are in `data/eval_results.csv` and `data/eval_generation_results.csv`.

## Model & Provider Choices

- **Embeddings**: `all-MiniLM-L6-v2` (sentence-transformers) — local, free, fast
- **Text generation**: Groq API running `openai/gpt-oss-120b` — chosen after a widespread Gemini free-tier access restriction affected new Google Cloud projects in mid-2026; Groq offers a genuinely free, reliable tier with no billing setup required
- **Vision (photo ingredient recognition)**: Groq's `qwen/qwen3.6-27b`, also free-tier
- **Speech-to-text**: OpenAI's Whisper (`base` model), run entirely locally

The architecture is provider-agnostic: swapping the generation model requires changing only the API call in `generate_response.py`, not any retrieval, parsing, or guardrail logic.

## Tech Stack

- **Retrieval**: sentence-transformers, rank_bm25, scikit-learn (cosine similarity)
- **Generation**: Groq API (GPT-OSS / Qwen vision)
- **Speech**: OpenAI Whisper (local)
- **Data**: pandas, RecipeNLG dataset (2.2M recipes, 2000-row dev sample)
- **Nutrition**: USDA FoodData Central API
- **Budget**: static ingredient-cost lookup table (deterministic, not LLM-based — see Design Decisions)
- **Backend**: FastAPI, uvicorn
- **Frontend**: vanilla HTML/CSS/JS, no framework
- **Email**: Gmail SMTP
- **Environment**: Python, python-dotenv for secrets

## Design Decisions Worth Noting

- **Nutrition and budget are rule-based, not LLM-generated.** Both need auditable, correctable numbers — an LLM asked to recall prices or nutrition facts from memory would produce plausible-sounding but ungrounded, unsourced answers. Deterministic lookups are the more accurate *and* more honest engineering choice here, consistent with the project's overall anti-hallucination philosophy.
- **The guardrail's match confidence is exposed as structured API data** (`warned: true/false`), not inferred by parsing the LLM's natural-language output — this makes the frontend's confidence stamp reliable rather than a fragile text-matching heuristic.

## Known Limitations

- **Cuisine coverage gap**: the dataset skews heavily toward American home-cooking. For common combinations popular in other cuisines (e.g., eggs+onion+tomato → Indian-style bhurji or shakshuka), the system surfaces a technically-matching but practically inferior recommendation, since no better option exists in the corpus. This is a data-sourcing limitation, not a retrieval or generation bug.
- **Contradiction detection**: the retrieval layer doesn't structurally detect logically conflicting requests (e.g., "vegan with chicken") — currently caught inconsistently by the generation layer's grounding instructions, not by a dedicated check.
- **Time constraints are parsed but not enforced** as a hard filter on results.
- **Ingredient extraction is regex/keyword-based**, not a trained NER model — multi-word ingredients (e.g., "coconut milk") are occasionally split incorrectly.
- **Whisper transcription accuracy varies** on low-quality audio.
- **Budget estimates use a static price table**, not live grocery pricing — a reasonable approximation, not a production-grade cost source.

## What I'd Do With More Time / At Scale

- Source or supplement multi-cuisine recipes to close the dataset coverage gap
- Add a dedicated contradiction-detection step before retrieval
- Enforce time constraints as a hard filter, not just a parsed field
- Fine-tune a lightweight classifier for constraint extraction to handle more phrasing variation
- Add cross-encoder reranking on top of hybrid search for further precision
- Scale from the 2000-row dev sample to the full 2.2M-row dataset with a production vector index (e.g. FAISS)
- Add cost/latency tracking and query routing (skip generation for simple constraint-only queries)

## Running It

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Set up a `.env` file with:
GROQ_API_KEY=your_key
GMAIL_ADDRESS=your_email
GMAIL_APP_PASSWORD=your_app_password
USDA_API_KEY=your_key

Run the backend:
```bash
uvicorn src.api:app --reload
```

Open `frontend/index.html` in your browser.

Run the eval suite:
```bash
python src/run_eval.py
python src/run_eval_with_generation.py
```
