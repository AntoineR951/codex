# AI Reputation Tester API

API MVP exécutable pour tester la réputation IA d'une entreprise.

## Priorité recommandée (très important)

### 1) Commencer par le **dashboard**
Oui, je te conseille de commencer par le dashboard.

Pourquoi:
- c'est la **valeur produit principale** (le rapport que l'utilisateur paie pour voir),
- ça valide vite le cœur métier (requêtes, exécution, résultats, scoring),
- ça permet d'itérer sur la data avant de polir l'acquisition marketing.

La page de vente peut rester simple au début (headline + CTA) pendant que le dashboard devient solide.

### 2) Copier les maquettes dans le projet ?
Oui, bonne idée.

Je recommande:
- créer un dossier `design/` (ou `docs/design/`) avec:
  - captures PNG/JPG,
  - tokens de style (couleurs, typo, spacing),
  - notes d'interaction (filtres, colonnes, tri, états vides/loading),
- ne pas mélanger les assets design avec `static/` tant qu'ils ne sont pas intégrés dans l'UI finale.

---

## Fonctionnalités
- Génération automatique de requêtes par intention.
- Exécution multi-chatbots (configurable via `CHATBOTS`).
- Analyse et classification (`TOP_MENTION`, `MENTION`, `NO_MENTION`, `NEGATIVE_SIGNAL`).
- Rapport tabulaire par requête avec une colonne par chatbot.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Configuration
```bash
export CHATBOTS="chatgpt,claude,gemini"
```

## Endpoints
- `GET /health`
- `POST /runs` body: `{"company_name":"ACME"}`
- `POST /runs/{id}/execute`
- `GET /runs/{id}/report`

## Tests
```bash
pytest -q
```
