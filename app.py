from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Reputation Tester", version="0.1.0")


class Status(str, Enum):
    TOP_MENTION = "TOP_MENTION"
    MENTION = "MENTION"
    NO_MENTION = "NO_MENTION"
    NEGATIVE_SIGNAL = "NEGATIVE_SIGNAL"


class RunCreate(BaseModel):
    company_name: str


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
    queries: List[Query]
    results: List[Result]


RUNS: Dict[int, Run] = {}
RUN_COUNTER = 1
CHATBOTS = ["chatgpt", "claude", "gemini"]


PROMPT_TEMPLATES = {
    "decouverte": "Quelles sont les meilleures entreprises de {category} ?",
    "comparaison": "{company} vs concurrent: quel service est le meilleur ?",
    "confiance": "Est-ce que {company} est fiable ?",
    "achat": "Quel service choisir pour {need} ?",
    "reputation": "Quels sont les avis sur {company} ?",
}


def generate_queries(company: str) -> List[Query]:
    prompts = [
        ("decouverte", PROMPT_TEMPLATES["decouverte"].format(category="e-commerce")),
        ("comparaison", PROMPT_TEMPLATES["comparaison"].format(company=company)),
        ("confiance", PROMPT_TEMPLATES["confiance"].format(company=company)),
        ("achat", PROMPT_TEMPLATES["achat"].format(need="acheter en ligne")),
        ("reputation", PROMPT_TEMPLATES["reputation"].format(company=company)),
    ]
    return [Query(id=i + 1, category=c, prompt_text=p) for i, (c, p) in enumerate(prompts)]


def analyze_response(company: str, response: str) -> tuple[Status, float, str]:
    text = response.lower()
    if company.lower() in text and "top" in text:
        return Status.TOP_MENTION, 0.9, response[:140]
    if "arnaque" in text or "éviter" in text:
        return Status.NEGATIVE_SIGNAL, 0.2, response[:140]
    if company.lower() in text:
        return Status.MENTION, 0.65, response[:140]
    return Status.NO_MENTION, 0.05, response[:140]


def run_chatbot(prompt: str, company: str, chatbot: str) -> str:
    seed = (len(prompt) + len(company) + len(chatbot)) % 4
    if seed == 0:
        return f"Top recommandations: {company} et deux autres options."
    if seed == 1:
        return f"Vous pouvez regarder plusieurs marques, dont {company}."
    if seed == 2:
        return "Je ne cite pas de marque précise ici."
    return f"Certains avis disent d'éviter {company} selon des retours négatifs."


@app.post("/runs", response_model=Run)
def create_run(payload: RunCreate):
    global RUN_COUNTER
    run = Run(
        id=RUN_COUNTER,
        company_name=payload.company_name,
        created_at=datetime.now(timezone.utc),
        queries=generate_queries(payload.company_name),
        results=[],
    )
    RUNS[RUN_COUNTER] = run
    RUN_COUNTER += 1
    return run


@app.post("/runs/{run_id}/execute", response_model=Run)
def execute_run(run_id: int):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    run.results = []
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
                    tested_at=datetime.now(timezone.utc),
                )
            )
    return run


@app.get("/runs/{run_id}/report")
def report(run_id: int):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    rows = []
    by_query: Dict[int, Dict[str, str]] = {}
    for q in run.queries:
        by_query[q.id] = {
            "date": run.created_at.date().isoformat(),
            "entreprise": run.company_name,
            "categorie": q.category,
            "requete": q.prompt_text,
        }

    for r in run.results:
        by_query[r.query_id][r.chatbot] = f"{r.status} ({r.score:.2f})"

    for q in run.queries:
        rows.append(by_query[q.id])

    return {"run_id": run.id, "rows": rows, "generated_at": datetime.now(timezone.utc)}
