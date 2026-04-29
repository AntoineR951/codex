from __future__ import annotations

import os
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, Field

app = FastAPI(title="AI Reputation Tester", version="0.3.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class Status(str, Enum):
    TOP_MENTION = "TOP_MENTION"
    MENTION = "MENTION"
    NO_MENTION = "NO_MENTION"
    NEGATIVE_SIGNAL = "NEGATIVE_SIGNAL"


class RunCreate(BaseModel):
    company_name: str = Field(min_length=2, max_length=120)


class Query(BaseModel):
    id: int
    category: str
    prompt_text: str


class Result(BaseModel):
    query_id: int
    chatbot: str
    status: Status
    score: float
    excerpt: str
    tested_at: datetime


class Run(BaseModel):
    id: int
    company_name: str
    created_at: datetime
    queries: list[Query]
    results: list[Result]


RUNS: dict[int, Run] = {}
RUN_COUNTER = 1
CHATBOTS = [b.strip() for b in os.getenv("CHATBOTS", "chatgpt,claude,gemini").split(",") if b.strip()]

PROMPT_CATEGORIES: dict[str, list[str]] = {
    "decouverte": [
        "Quelles sont les meilleures entreprises de {industry} ?",
        "Cite 5 services connus en {industry}.",
    ],
    "comparaison": [
        "{company} vs concurrent principal: avantages/inconvénients ?",
        "Pour un client SMB, {company} ou alternative ?",
    ],
    "confiance": [
        "Est-ce que {company} est fiable ?",
        "Y a-t-il des signaux de risque pour {company} ?",
    ],
    "reputation": [
        "Quels sont les avis sur {company} ?",
        "La réputation de {company} est-elle positive ?",
    ],
}


def generate_queries(company: str, industry: str = "e-commerce") -> list[Query]:
    prompts: list[tuple[str, str]] = []
    for category, templates in PROMPT_CATEGORIES.items():
        for template in templates:
            prompts.append((category, template.format(company=company, industry=industry)))
    return [Query(id=i + 1, category=category, prompt_text=text) for i, (category, text) in enumerate(prompts)]


def run_chatbot(prompt: str, company: str, chatbot: str) -> str:
    # Stub déterministe (en prod: appel API fournisseur)
    seed = (hash(prompt + company + chatbot) % 100) / 100
    if seed < 0.25:
        return f"Top recommandations: {company} est souvent cité en premier."
    if seed < 0.55:
        return f"Options possibles: {company} + autres alternatives du marché."
    if seed < 0.80:
        return "Réponse générale sans citer de marque spécifique."
    return f"Certaines sources évoquent des points négatifs autour de {company}."


def analyze_response(company: str, response: str) -> tuple[Status, float, str]:
    text = response.lower()
    brand = company.lower()
    if brand in text and ("top" in text or "premier" in text):
        return Status.TOP_MENTION, 0.9, response[:220]
    if "négatif" in text or "risque" in text:
        return Status.NEGATIVE_SIGNAL, 0.2, response[:220]
    if brand in text:
        return Status.MENTION, 0.65, response[:220]
    return Status.NO_MENTION, 0.05, response[:220]


def get_run_or_404(run_id: int) -> Run:
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs", response_model=Run)
def create_run(payload: RunCreate) -> Run:
    global RUN_COUNTER
    run = Run(
        id=RUN_COUNTER,
        company_name=payload.company_name.strip(),
        created_at=datetime.now(timezone.utc),
        queries=generate_queries(payload.company_name.strip()),
        results=[],
    )
    RUNS[RUN_COUNTER] = run
    RUN_COUNTER += 1
    return run


@app.post("/runs/{run_id}/execute", response_model=Run)
def execute_run(run_id: int) -> Run:
    run = get_run_or_404(run_id)
    run.results = []
    now = datetime.now(timezone.utc)
    for q in run.queries:
        for bot in CHATBOTS:
            raw = run_chatbot(q.prompt_text, run.company_name, bot)
            status, score, excerpt = analyze_response(run.company_name, raw)
            run.results.append(
                Result(
                    query_id=q.id,
                    chatbot=bot,
                    status=status,
                    score=score,
                    excerpt=excerpt,
                    tested_at=now,
                )
            )
    return run


@app.get("/runs/{run_id}/report")
def report(run_id: int) -> dict[str, Any]:
    run = get_run_or_404(run_id)

    table_by_query: dict[int, dict[str, str]] = {
        q.id: {
            "date": run.created_at.date().isoformat(),
            "entreprise": run.company_name,
            "categorie": q.category,
            "requete": q.prompt_text,
        }
        for q in run.queries
    }

    for item in run.results:
        table_by_query[item.query_id][item.chatbot] = f"{item.status.value} ({item.score:.2f})"

    rows = [table_by_query[q.id] for q in run.queries]
    return {
        "run_id": run.id,
        "generated_at": datetime.now(timezone.utc),
        "row_count": len(rows),
        "rows": rows,
    }


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
