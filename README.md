# Fridge2Fork 🍳

An AI-powered recipe recommendation system that turns whatever ingredients you have — typed, spoken, or eventually photographed — into a grounded, honest recipe suggestion. Built as a deep-dive into RAG (Retrieval-Augmented Generation) systems, with a specific focus on **knowing when the system doesn't know**, rather than just optimizing for accuracy.

## The Core Idea

Most RAG demos are graded on "did it answer correctly?" This project is built around a harder, more valuable question: **how do you catch and honestly communicate when a system's answer is a weak match, before it misleads the user?**

The cooking domain is the testbed. The actual engineering focus is retrieval, grounding, and failure detection.

## Architecture

Input (text / voice)
↓
Constraint Parser (extracts time, dietary, exclusions, spice, budget)
↓
Query Router (simple search vs. filtered search)
↓
Hybrid Retrieval (BM25 keyword search + dense vector embeddings)
↓
Exclusion Filter (safety-critical: allergies, dietary restrictions)
↓
Coverage Guardrail (measures how well results actually match the query)
↓
LLM Generation (grounded strictly in retrieved recipes)
↓
Output (displayed + optionally emailed, with nutrition suggestions)


## Key Features

- **Hybrid retrieval**: combines BM25 (exact keyword matching) with dense embeddings (semantic similarity) over a 2M+ recipe dataset, since vector search alone missed exact-term matches like specific excluded ingredients
- **Constraint parsing**: extracts time limits, dietary restrictions, allergies/exclusions, spice level, and budget signals from natural language
- **Safety-critical exclusion filtering**: uses a category-expansion map (e.g., "shellfish" → shrimp, crab, oyster, lobster) so allergy-related requests are caught even when the user doesn't name every specific ingredient
- **Coverage guardrail**: measures what fraction of the user's actual ingredients appear in the retrieved recipes, and explicitly warns the user when the match is weak — instead of confidently returning a poor result
- **Grounded LLM generation**: the model is instructed to only use retrieved recipes and to honestly reflect guardrail warnings in its response
- **Voice input**: Whisper (OpenAI, open-source, runs locally) transcribes spoken ingredient lists
- **Email delivery**: sends the final recommendation via Gmail SMTP
- **Nutrition suggestions**: rule-based (not LLM-generated, deliberately) estimation using the USDA FoodData Central API, suggesting simple additions to round out a meal's nutrition

## The Eval Story

Rather than just testing the system by hand, I built a 25-query adversarial evaluation set spanning six categories: easy/baseline, constraint-heavy, rare-ingredient, ambiguous phrasing, logically conflicting requests, and allergy-critical exact-match cases.

**What the eval found:**
- 4 real bugs, 3 of them safety-relevant — the exclusion filter wasn't catching category terms like "shellfish-free" or "nut-free," meaning allergy-relevant recipes (containing peanut butter, shrimp, tree nuts) were slipping through
- 1 UX bug — overly aggressive filtering occasionally returned zero results with no explanation

**What I fixed:**
- Built a category-expansion map so exclusions catch related ingredients, not just literal keyword matches
- Increased the candidate pool size so filtering has enough room to find safe matches
- Added an explicit fallback message when no recipes satisfy all constraints, instead of silently returning nothing

**An interesting finding during generation testing**: the LLM generation layer caught a logical contradiction ("vegan recipe with chicken") that the retrieval and guardrail layers had missed — a reminder that grounding instructions can serve as a second line of defense beyond structured filters, and that different layers of a system can have complementary strengths.

Full eval results and manual labeling are in `data/eval_results.csv` and `data/eval_generation_results.csv`.

## Model & Provider Choices

- **Embeddings**: `all-MiniLM-L6-v2` (sentence-transformers) — local, free, fast
- **Generation**: Groq API running `openai/gpt-oss-120b` — chosen after hitting a widespread Gemini free-tier access restriction affecting new Google Cloud projects in mid-2026. Groq offers a genuinely free, reliable tier with no billing setup required.
- **Speech-to-text**: OpenAI's Whisper (`base` model), run entirely locally — free, no API dependency

The architecture is provider-agnostic: swapping the generation model requires changing only the API call in `generate_response.py`, not any retrieval, parsing, or guardrail logic. This separation was a deliberate design choice.

## Tech Stack

- **Retrieval**: sentence-transformers, rank_bm25, scikit-learn (cosine similarity)
- **Generation**: Groq API (Llama-family / GPT-OSS)
- **Speech**: OpenAI Whisper (local)
- **Data**: pandas, RecipeNLG dataset (2.2M recipes, 2000-row dev sample)
- **Nutrition**: USDA FoodData Central API
- **Email**: Gmail SMTP
- **Environment**: Python, python-dotenv for secrets management

## Known Limitations

- **Contradiction detection**: the retrieval layer doesn't structurally detect logically conflicting requests (e.g., "vegan with chicken") — currently caught inconsistently by the generation layer's grounding instructions, not by a dedicated check
- **Time constraints are parsed but not enforced**: `max_time_minutes` is extracted but not yet used as a hard filter on results
- **Ingredient extraction is regex/keyword-based**, not a trained NER model — multi-word ingredients (e.g., "coconut milk") are occasionally split incorrectly
- **Whisper transcription accuracy varies** on low-quality audio — tested on a single low-volume recording, where the `small` model did not consistently outperform `base`
- **Dataset skews toward Western/American home cooking** — queries involving cuisines outside this distribution (e.g., ingredients like saffron, miso, or coconut milk) reliably trigger low-coverage warnings, which is the guardrail working as intended, not a bug

## What I'd Do With More Time / At Scale

- Add a dedicated contradiction-detection step before retrieval, rather than relying on generation-layer grounding alone
- Enforce time constraints as a hard filter, not just a parsed field
- Fine-tune a lightweight classifier for constraint extraction instead of regex, to handle more phrasing variation
- Add hybrid search reranking with a cross-encoder for further precision improvement
- Scale from the 2000-row dev sample to the full 2.2M-row dataset with a production vector index (e.g., FAISS with approximate search)
- Add cost/latency tracking and query routing (skip generation entirely for simple constraint-only queries)

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


Run the full pipeline:
```bash
python src/query_router.py
```

Run the eval suite:
```bash
python src/run_eval.py
python src/run_eval_with_generation.py
```
