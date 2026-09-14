# RUN.md

**Primary review method: local.**

A hosted version is also live at [FILL IN VERCEL URL] for convenience, but local is the
declared primary review method since it doesn't depend on my hosting credits/uptime.

## 1. Required runtimes and versions

- Python 3.11+
- Node.js 18+
- A Sarvam AI API key (free tier available at dashboard.sarvam.ai)

## 2. Required environment variables

Backend (`backend/.env`, copy from `backend/.env.example`):
SARVAM_API_KEY=your_sarvam_api_key_here
SARVAM_BASE_URL=https://api.sarvam.ai/v1
SARVAM_CHAT_MODEL=sarvam-105b
DATABASE_URL=sqlite:///./kivi.db
CORS_ORIGIN=http://localhost:5173


Frontend (`frontend/.env`):
VITE_API_URL=http://localhost:8000



## 3. Install dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cd ../frontend
npm install
```

## 4. Create, migrate, and seed the database

```bash
cd backend
cp .env.example .env             # fill in your real SARVAM_API_KEY
alembic upgrade head
```

Generate the corpus (deterministic, seeded, no API calls):

```bash
cd corpus
python generate_corpus.py
cd ..
```

**Corpus import now requires an authenticated account** (auth was added after the
original ingestion endpoint). Sign up through the running app first (see step 5-6
below), then import the corpus as that account:

```bash
# after signing up in the browser and copying your access token from browser
# devtools (Application > Session Storage > kivi_token), or via:
curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" \
  -d "{\"name\": \"Review User\", \"email\": \"review@example.com\", \"password\": \"reviewpass123\"}"
# copy the access_token from the response, then:
python scripts/import_corpus.py corpus/data/dictations.json --token YOUR_ACCESS_TOKEN
```

*(Note: `scripts/import_corpus.py` was originally written before auth existed and calls
the ingestion logic directly against the database rather than through the HTTP API, so
it does not actually require a token in its current form — it takes a `user_name` and
creates/finds that user directly via `get_or_create_user`. If you want the corpus
attached to a specific login-capable account, either (a) sign up with email
`review@example.com` and name `Review User`, matching exactly what the script's
`corpus/data/dictations.json`'s `user_name` field contains, since `get_or_create_user`
matches on name, or (b) set a password on that user afterward directly in the database.
This is a known rough edge from adding auth after the original ingestion script was
built — documented here rather than hidden.)*

## 5. Start every required process

Terminal 1 — backend:
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:
```bash
cd frontend
npm run dev
```

## 6. Interface to open

`http://localhost:5173` — sign up with any email/password, or log in with
`review@example.com` / `reviewpass123` if you used that account for corpus import above.

## 7. Primary interactions to try

In **Hey Kivi**:
- "What does PRJ-FLC stand for?"
- "Find my most recent Slack update about Project Falcon and polish it for a client email."
- "How should my Slack updates be formatted right now?"
- "What did I work on last week?"
- "What is the status of Project Nimbus?" (should abstain — never mentioned)

In **Shortcuts**: teach one (trigger `my sign-off`, expansion `Warm regards,\nYour Name`),
then in **Record**, dictate something containing that phrase and confirm expansion. Ask
Hey Kivi "what does my sign-off shortcut do?" to confirm recall.

**Dictation Feed** replays ingested records chronologically with an app filter.
**Memory Viewer** shows everything currently in memory, grouped by type.

**To verify multi-user isolation:** sign up a second account and confirm it sees none of
the first account's shortcuts, dictations, or memories.

## 8. Exact command to run the candidate evaluation

```bash
cd backend
python eval/run_eval.py
python eval/run_eval.py corpus/data/held_out_questions.json held_out_report
python eval/run_eval.py corpus/data/qa_suites.json qa_report
python eval/run_eval.py corpus/data/naive_user_queries.json naive_report
python -m pytest tests/ -v
```

Each `run_eval.py` call writes `eval/results/<name>.json` and `<name>.md`. Note: these
eval scripts call the orchestrator/ingestion logic directly against the database (not
through the authenticated HTTP API), so they are unaffected by the auth layer added
after they were built.

## 9. Procedure for importing another corpus

Format (see `corpus/data/dictations.json` for a full example):

```json
{
  "user_name": "string",
  "company": "string (optional)",
  "records": [
    {
      "record_id": "unique string", "app": "Slack | Google Docs | Outlook | Notes",
      "raw_asr": "string", "llm_formatted": "string",
      "timestamp": "ISO 8601 datetime", "extra_metadata": {}
    }
  ]
}
```

```bash
python scripts/import_corpus.py path/to/your_corpus.json
```
Add a second argument to limit records for a quick test:
`python scripts/import_corpus.py path/to/corpus.json 10`. The importer is idempotent —
records with a `record_id` already in the database are skipped.

## 10. Where evaluation results and memory state can be inspected

- Eval reports: `backend/eval/results/*.json` and `*.md`
- Memory state via API (requires a Bearer token from login):
  `GET http://localhost:8000/debug/memories` with `Authorization: Bearer <token>`
- Raw dictations: `GET http://localhost:8000/debug/dictations`
- Substring search bypassing retrieval scoring:
  `GET http://localhost:8000/debug/memory-search?contains=<term>`
- Full audit trail: `memory_events` table, inspectable via any SQLite client on
  `backend/kivi.db`, or: `sqlite3 backend/kivi.db "SELECT * FROM memory_events ORDER BY created_at DESC LIMIT 20;"`
- Frontend Memory Viewer tab shows the same data as `/debug/memories`, live in the UI.

## 11. Exact procedure for resetting the system

```bash
cd backend
rm kivi.db                       # Windows: Remove-Item kivi.db
alembic upgrade head
python scripts/import_corpus.py corpus/data/dictations.json
```

## Hosted deployment (supplementary, not the primary review method)

- **App:** [FILL IN VERCEL URL]
- **API:** [FILL IN RENDER URL]
- Backend: Render.com (Python web service + managed Postgres)
- Frontend: Vercel (static Vite build)
- Same environment variables as local, with `DATABASE_URL` pointing at the hosted
  Postgres instance and `CORS_ORIGIN` set to the Vercel URL
- Sign up directly through the hosted app; there is no seeded demo account

## Notes

- `SARVAM_API_KEY` and `JWT_SECRET_KEY` are the only required secrets; see
  `backend/.env.example`. No credentials are committed anywhere in this repository.
- Ingesting the full corpus takes several minutes (one Sarvam API call per record for
  extraction). The larger eval sets similarly take a few minutes each.