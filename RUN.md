# RUN.md

**Primary review method: local.**

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
cp .env.example .env             # then fill in your real SARVAM_API_KEY
alembic upgrade head
```

This creates `backend/kivi.db` with all tables (`users`, `dictations`, `memories`,
`memory_provenance`, `memory_events`, `hey_kivi_turns`, `shortcuts`).

Generate the corpus (deterministic, seeded, no API calls, produces ~500+ records):

```bash
cd corpus
python generate_corpus.py
cd ..
```

Ingest it into the database (this does call the Sarvam API, once per record — expect
several minutes for the full corpus):

```bash
python scripts/import_corpus.py corpus/data/dictations.json
```

## 5. Start every required process

Terminal 1 — backend:

```bash
cd backend
source .venv/bin/activate        # Windows: .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:

```bash
cd frontend
npm run dev
```

## 6. Interface to open

`http://localhost:5173`

## 7. Primary interactions to try

In the **Hey Kivi** tab:
- "What does PRJ-FLC stand for?"
- "Find my most recent Slack update about Project Falcon and polish it for a client email."
- "How should my Slack updates be formatted right now?"
- "What did I work on last week?"
- "What is the status of Project Nimbus?" (should abstain — never mentioned)

In the **Shortcuts** tab: teach a shortcut (e.g. trigger `my sign-off`, expansion
`Warm regards,\nYour Name`), then in the **Record** tab, dictate something containing
that phrase and confirm it expands before being saved. Then ask Hey Kivi "what does my
sign-off shortcut do?" to confirm recall.

The **Dictation Feed** tab replays ingested records chronologically with an app filter.
The **Memory Viewer** tab shows everything currently in memory, grouped by type.

## 8. Exact command to run the candidate evaluation

```bash
cd backend
python eval/run_eval.py                                          # core 10-question set
python eval/run_eval.py corpus/data/held_out_questions.json held_out_report   # 9-question held-out set
python eval/run_eval.py corpus/data/qa_suites.json qa_report                  # 35-question stress suite
python eval/run_eval.py corpus/data/naive_user_queries.json naive_report      # 15-question naive-user set
python -m pytest tests/ -v                                       # 24 fast unit tests, no LLM calls
```

Each `run_eval.py` invocation writes `eval/results/<name>.json` and `<name>.md`.

## 9. Procedure for importing another corpus

The corpus import format is documented by `corpus/data/dictations.json` itself:

```json
{
  "user_name": "string",
  "company": "string (optional)",
  "records": [
    {
      "record_id": "unique string",
      "app": "Slack | Google Docs | Outlook | Notes",
      "raw_asr": "raw speech-to-text string",
      "llm_formatted": "cleaned-up string",
      "timestamp": "ISO 8601 datetime",
      "extra_metadata": {}
    }
  ]
}
```

To import a different corpus in this format (including the reviewers' internal
500-dictation corpus, once translated into this shape):

```bash
python scripts/import_corpus.py path/to/your_corpus.json
```

Add a second argument to limit the number of records processed for a quick test, e.g.
`python scripts/import_corpus.py path/to/corpus.json 10`.

The importer is idempotent — records with a `record_id` already in the database are
skipped, so it's safe to re-run against a partially-ingested corpus.

## 10. Where evaluation results and memory state can be inspected

- Eval reports: `backend/eval/results/*.json` and `*.md`
- Memory state via API: `GET http://localhost:8000/debug/memories?user_name=<name>`
- Raw ingested dictations: `GET http://localhost:8000/debug/dictations?user_name=<name>`
- Substring search across all memory (bypasses retrieval scoring, useful for checking
  whether something was ever extracted at all):
  `GET http://localhost:8000/debug/memory-search?user_name=<name>&contains=<term>`
- Full audit trail (every create/retrieve/update/reject/decay decision with a reason)
  lives in the `memory_events` table — inspectable via any SQLite client pointed at
  `backend/kivi.db`, or by querying it directly:
  `sqlite3 backend/kivi.db "SELECT * FROM memory_events ORDER BY created_at DESC LIMIT 20;"`
- Frontend Memory Viewer tab shows the same data as the `/debug/memories` endpoint, in
  the running UI.

## 11. Exact procedure for resetting the system

```bash
cd backend
rm kivi.db                       # Windows: Remove-Item kivi.db
alembic upgrade head
python scripts/import_corpus.py corpus/data/dictations.json
```

This drops all data and rebuilds the schema and corpus from scratch.

## Notes

- `SARVAM_API_KEY` is the only required credential; see `backend/.env.example`.
- No credentials are committed anywhere in this repository.
- Ingesting the full corpus takes several minutes since it makes one Sarvam API call
  per dictation record for extraction; the eval scripts also make API calls per
  question and will similarly take a few minutes each for the larger sets.