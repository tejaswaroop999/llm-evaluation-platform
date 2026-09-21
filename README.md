# LLM Evaluation Platform

A portfolio-grade platform for evaluating LLMs and AI agents across quality, latency, cost, reliability, and failure modes.

## MVP

- Create/load evaluation datasets
- Run prompts against one model
- Exact-match evaluator
- Record latency and pass/fail results
- View evaluation results through an API
- Add a Next.js dashboard after the backend MVP works

## Stack

- Backend: Python + FastAPI
- Frontend: Next.js + TypeScript
- Database: SQLite first, PostgreSQL later
- Models: Claude / OpenAI adapters
- Infra: Docker + GitHub Actions

## Start backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs

## Milestone 1 verification

From `backend/`, install the dependencies and run the test suite:

```bash
pip install -r requirements.txt
python -m pytest
```

Milestone 1 includes the `/health` endpoint and initial Pydantic schemas for
evaluation cases, datasets, prompt versions, runs, and results. Milestone 2
adds in-memory dataset CRUD at `/datasets`; persistence, provider adapters,
and evaluation execution are intentionally deferred to later milestones.

## Milestone 3: deterministic evaluation

An evaluator compares an expected output with an actual model output and
returns a structured `EvaluationOutcome` containing `passed`, `score`, and
`reason`. `ExactMatchEvaluator` uses strict, case-sensitive equality:
whitespace and case are not normalized, and two empty strings are a match.

Deterministic evaluation comes before LLM-as-a-judge because it is repeatable
for the same inputs. That makes it useful for regression tests, CI/CD checks,
and reliable comparison of prompt versions or models. LLM-as-a-judge can be
added later for subjective quality dimensions where deterministic rules are
not sufficient, with its non-determinism tracked explicitly.

Run the evaluator tests from `backend/` with:

```bash
python -m pytest tests/test_evaluators.py
```
