# IA Reputation Tester

Application MVP pour évaluer comment des chatbots mentionnent une entreprise (ou un site) à partir d'un simple nom.

## Objectif

Entrée utilisateur:
- `nom_entreprise` (ex: `Stripe`, `Doctolib`, `BackMarket`)

Sortie:
- un rapport structuré (tableau + possibilité d'exports) montrant, par requête et par chatbot:
  - mention positive / neutre / négative
  - présence/absence de mention
  - positionnement de la marque (en tête de réponse, mention secondaire, etc.)
  - extrait de réponse
  - date du test

---

## MVP proposé

### 1) Génération de requêtes de test

Le système génère automatiquement des prompts à tester, classés par intentions.

Exemples de catégories:
- **Découverte**: "Quelles sont les meilleures entreprises de [catégorie]?"
- **Comparaison**: "[Entreprise A] vs [Entreprise B]"
- **Confiance**: "Est-ce que [Entreprise] est fiable ?"
- **Achat**: "Quel service choisir pour [besoin]?"
- **Réputation**: "Avis sur [Entreprise]"

Chaque catégorie peut avoir 5 à 20 variantes pour robustesse.

### 2) Exécution des tests

Pour chaque chatbot connecté (ex: ChatGPT, Claude, Gemini), l'app:
1. envoie les prompts
2. collecte les réponses
3. applique une grille d'analyse simple

Exemples de statuts cellule:
- `TOP_MENTION` (entreprise citée parmi les premières recommandations)
- `MENTION` (entreprise citée sans priorité)
- `NO_MENTION` (aucune mention)
- `NEGATIVE_SIGNAL` (risque réputation)

### 3) Rapport tabulaire (version initiale)

Structure recommandée:
- une ligne = un prompt
- colonnes fixes: date, entreprise, catégorie
- une colonne par chatbot
- cellule chatbot = statut + score + extrait court

Exemple:

| Date | Entreprise | Catégorie | Requête | ChatGPT | Claude | Gemini |
|---|---|---|---|---|---|---|
| 2026-04-29 | ACME | Comparaison | "ACME vs CompetitorX" | TOP_MENTION (0.82) | MENTION (0.63) | NO_MENTION (0.05) |

---

## Architecture simple (prête à coder)

- **Frontend**: Next.js (form + tableau)
- **Backend API**: FastAPI ou Node/Express
- **DB**: Postgres
- **Queue (optionnel)**: Redis + worker pour exécuter des tests longs

Modules backend:
1. `prompt_generator` (templates + variantes)
2. `runner` (connecteurs chatbot)
3. `analyzer` (règles + scoring)
4. `reporting` (agrégations + exports CSV)

---

## Modèle de données minimal

### `test_runs`
- `id`
- `company_name`
- `created_at`

### `queries`
- `id`
- `run_id`
- `category`
- `prompt_text`

### `results`
- `id`
- `query_id`
- `chatbot`
- `status` (`TOP_MENTION|MENTION|NO_MENTION|NEGATIVE_SIGNAL`)
- `score` (0-1)
- `excerpt`
- `raw_response`
- `tested_at`

---

## Roadmap produit

1. **Semaine 1**: MVP tableau (1 entreprise, 10 prompts, 2 chatbots)
2. **Semaine 2**: scoring amélioré + filtres + export CSV
3. **Semaine 3**: graphiques d'évolution temporelle
4. **Semaine 4**: alertes automatiques (baisse de visibilité, signaux négatifs)

---

## Prochaine étape recommandée

Implémenter un POC technique en 3 endpoints:
- `POST /runs` (crée un test pour une entreprise)
- `POST /runs/{id}/execute` (lance l'exécution)
- `GET /runs/{id}/report` (retourne le tableau consolidé)

