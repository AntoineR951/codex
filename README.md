# AI Reputation Tester API

MVP exécutable pour tester la réputation IA d'une entreprise avec 3 endpoints.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Endpoints

- `POST /runs` avec `{"company_name": "ACME"}`
- `POST /runs/{id}/execute`
- `GET /runs/{id}/report`

## Exemple rapide

```bash
curl -s -X POST http://127.0.0.1:8000/runs -H 'content-type: application/json' -d '{"company_name":"ACME"}'
curl -s -X POST http://127.0.0.1:8000/runs/1/execute
curl -s http://127.0.0.1:8000/runs/1/report
```

Le rapport retourne un tableau avec:
- une requête par ligne,
- un chatbot par colonne,
- la date,
- le statut + score dans chaque cellule.
